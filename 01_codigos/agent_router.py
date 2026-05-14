import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import TOOLS

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, ToolMessage
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
MEMORY_WINDOW  = 6

FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3-flash",
    "gemini-flash-latest",
]

_SYSTEM_PROMPT = """# IDENTIDAD

Eres el Asistente Virtual Conversacional del Banco de Occidente, entidad
financiera colombiana fundada en 1965, parte del Grupo Aval. Tu misión es
asistir a los clientes manteniendo conversaciones coherentes, recordando lo
que ya se habló y eligiendo la mejor herramienta para cada consulta.

# HERRAMIENTAS DISPONIBLES

## 1. consultar_corpus_documental
Úsala para preguntas ABIERTAS que requieren explicación, contexto o información
narrativa sobre productos, servicios, procesos o información corporativa.

Ejemplos:
- ¿Qué tarjetas de crédito tiene el banco?
- ¿Cuáles son los requisitos del crédito hipotecario?
- ¿Cómo funciona el CDT?
- ¿Qué beneficios tiene la cuenta de ahorros?

## 2. consultar_datos_estructurados
Úsala para datos PUNTUALES Y FIJOS: teléfonos, horarios, NIT, sucursales,
redes sociales, normativa, tutoriales cortos.

Tipos válidos: telefono, horario, corporativo, sucursales (+ ciudad),
redes_sociales, canales_digitales, normativo, preguntas_directas.

Ejemplos:
- ¿Cuál es el teléfono de atención? → tipo='telefono'
- ¿En qué horario atienden? → tipo='horario'
- ¿Cuál es el NIT? → tipo='corporativo'
- ¿Hay sucursales en Cali? → tipo='sucursales', ciudad='Cali'

# PROTOCOLO DE DECISIÓN

PASO 1 — VERIFICAR DOMINIO:
   ¿La consulta es sobre el Banco de Occidente?
   - NO → Responde sin herramientas:
     "No cuento con información sobre ese tema. Mi conocimiento se limita
     a productos, servicios e información oficial del Banco de Occidente."

PASO 2 — RESOLVER REFERENCIAS CON EL HISTORIAL:
   Si la pregunta usa pronombres ("ese", "esa", "el primero", "ese crédito",
   "esa tarjeta") resuélvelos con el historial ANTES de llamar a la herramienta.
   Nunca pases pronombres sin resolver. Siempre usa el nombre específico.

   Ejemplos:
   - "¿Y ese crédito qué requisitos tiene?" (contexto: hipotecario)
     → llama con consulta="requisitos crédito hipotecario"
   - "¿Cuánto cuesta la primera que mencionaste?" (contexto: Occiflex)
     → llama con consulta="cuota manejo tarjeta Occiflex"

PASO 3 — ELEGIR HERRAMIENTA:
   - Dato puntual fijo → consultar_datos_estructurados
   - Explicación narrativa o características → consultar_corpus_documental

PASO 4 — RESPONDER:
   Redacta una respuesta natural y cálida usando la salida de la herramienta.

# REGLAS

1. Responde siempre en español formal y cálido, primera persona del banco.
2. PROHIBIDO inventar datos no presentes en la respuesta de la herramienta.
3. PROHIBIDO mencionar "tool", "herramienta", "corpus" o detalles técnicos.
4. Si el cliente saluda o se despide, responde con cortesía sin herramientas.
"""


class Memory:
    """
    Historial de conversación con ventana deslizante y persistencia en disco.

    Uso:
        mem = Memory.load("data/memoria/sesion.json")
        mem.add("pregunta", "respuesta")
        mem.save("data/memoria/sesion.json")
    """

    def __init__(self, k: int = MEMORY_WINDOW):
        self.k     = k
        self._msgs = []

    # ── Operaciones de memoria ──────────────────────────────────

    def add(self, human: str, assistant: str):
        """Agrega un turno y aplica la ventana deslizante."""
        self._msgs.append(HumanMessage(content=human))
        self._msgs.append(AIMessage(content=assistant))
        self._msgs = self._msgs[-(self.k * 2):]

    def history(self) -> list:
        """Retorna los mensajes actuales (para pasarlos al LLM)."""
        return list(self._msgs)

    def turns(self) -> int:
        """Número de turnos almacenados actualmente."""
        return len(self._msgs) // 2

    def as_ui_messages(self) -> list:
        """
        Convierte el historial al formato de st.session_state.messages
        para reconstruir el chat en la interfaz al recargar la página.
        """
        ui = []
        for msg in self._msgs:
            if isinstance(msg, HumanMessage):
                ui.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                ui.append({
                    "role":       "assistant",
                    "content":    msg.content,
                    "tool_used":  None,
                    "tool_input": None,
                })
        return ui

    # ── Persistencia en disco ───────────────────────────────────

    def save(self, path: str) -> None:
        """
        Persiste el historial en un archivo JSON.
        Crea la carpeta si no existe.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version":  1,
            "window_k": self.k,
            "messages": [
                {
                    "type":    "human" if isinstance(m, HumanMessage) else "ai",
                    "content": m.content,
                }
                for m in self._msgs
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str, k: int = MEMORY_WINDOW) -> "Memory":
        """
        Carga el historial desde disco.
        Si el archivo no existe o está corrupto, retorna una memoria vacía.
        """
        mem = cls(k=k)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for msg in data.get("messages", []):
                t = msg.get("type", "")
                c = msg.get("content", "")
                if t == "human":
                    mem._msgs.append(HumanMessage(content=c))
                elif t == "ai":
                    mem._msgs.append(AIMessage(content=c))
            mem._msgs = mem._msgs[-(k * 2):]
            print(f"[memory] Cargados {mem.turns()} turnos desde {path}")
        except FileNotFoundError:
            print(f"[memory] No existe archivo en {path}. Memoria vacía.")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[memory] Error leyendo {path}: {e}. Memoria vacía.")
        return mem

    @staticmethod
    def delete(path: str) -> None:
        """Elimina el archivo de memoria del disco."""
        try:
            os.remove(path)
            print(f"[memory] Archivo eliminado: {path}")
        except FileNotFoundError:
            pass


# Alias backward-compatible por si hay imports previos de _Memory
_Memory = Memory


class _AgentSession:
    """Encapsula el LLM con tools y la memoria conversacional."""

    def __init__(self, llm, model_name: str, memory: Memory):
        self.llm   = llm
        self.model = model_name
        self.mem   = memory


def _build_llm():
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY no encontrada en .env. "
            "Obtén tu key en https://aistudio.google.com/apikey"
        )

    seen       = set()
    candidates = [GEMINI_MODEL] + [m for m in FALLBACK_MODELS if m != GEMINI_MODEL]
    candidates = [m for m in candidates if not (m in seen or seen.add(m))]

    last_err = None
    for model in candidates:
        try:
            print(f"[agent] Probando: {model}")
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=GEMINI_API_KEY,
                temperature=0.2,
                top_p=0.9,
                convert_system_message_to_human=False,
            )
            llm.invoke([HumanMessage(content="ping")])
            print(f"[agent] Activo: {model}")
            return llm, model
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ("404", "not_found", "429", "quota", "resource_exhausted")):
                print(f"[agent] {model} no disponible, probando siguiente...")
                last_err = e
            else:
                raise

    raise RuntimeError(f"Ningún modelo disponible. Último error: {last_err}")


def create_memory(path: str = None, k: int = MEMORY_WINDOW) -> Memory:
    """
    Crea una memoria.
    - Si se pasa `path`, carga el historial desde disco (persistencia).
    - Si no, crea una memoria vacía.
    """
    if path:
        return Memory.load(path, k=k)
    return Memory(k=k)


def build_agent_executor(memory: Memory):
    """Construye el LLM con tools y lo empaqueta en un _AgentSession."""
    llm, model = _build_llm()
    llm_with_tools = llm.bind_tools(TOOLS)
    return _AgentSession(llm_with_tools, model, memory), model


def chat(session: _AgentSession, user_input: str) -> dict:
    """Ejecuta un turno conversacional con tool calling nativo de Gemini."""

    messages = (
        [SystemMessage(content=_SYSTEM_PROMPT)]
        + session.mem.history()
        + [HumanMessage(content=user_input)]
    )

    tool_used = tool_input = tool_output = None

    try:
        response = session.llm.invoke(messages)

        if getattr(response, "tool_calls", None):
            tc         = response.tool_calls[0]
            tool_used  = tc.get("name")
            tool_input = tc.get("args", {})
            tc_id      = tc.get("id", f"call_{tool_used}")

            tool_fn = next((t for t in TOOLS if t.name == tool_used), None)
            if tool_fn:
                try:
                    tool_output = tool_fn.invoke(tool_input)
                except Exception as e:
                    tool_output = f"No pude obtener esa información: {str(e)[:100]}"
            else:
                tool_output = "Herramienta no encontrada."

            messages_2 = messages + [
                response,
                ToolMessage(content=str(tool_output), tool_call_id=tc_id),
            ]
            final  = session.llm.invoke(messages_2)
            answer = final.content or ""
        else:
            answer = response.content or ""

    except Exception as e:
        answer = f"⚠️ Error al procesar la consulta: {str(e)[:200]}"

    # Actualizar memoria (en RAM; el caller decide cuándo guardar a disco)
    session.mem.add(user_input, answer)

    return {
        "response":    answer,
        "tool_used":   tool_used,
        "tool_input":  tool_input,
        "tool_output": str(tool_output)[:400] if tool_output else None,
    }
