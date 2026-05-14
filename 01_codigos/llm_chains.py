import os
import sys
import re
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CHROMA_DIR, CHROMA_COLLECTION

load_dotenv()

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
PRIMARY_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3-flash",
    "gemini-flash-latest",
]

SIMILARITY_THRESHOLD = 0.28

BANKING_KEYWORDS = {
    "tarjeta","tarjetas","cuenta","cuentas","ahorro","ahorros",
    "crédito","credito","préstamo","prestamo","leasing","factoring",
    "banco","banca","financiero","financiera","occidente","bdo",
    "tasa","interés","interes","cuota","plazo","monto","saldo",
    "inversión","inversion","cdt","fondo","portafolio","rentabilidad",
    "seguro","póliza","poliza","cobertura","protección","proteccion",
    "sucursal","agencia","cajero","horario","atención","atencion",
    "transferencia","consignación","consignacion","pago","retiro",
    "app","aplicación","aplicacion","portal","transaccional","digital",
    "token","pse","qr","nequi","daviplata",
    "empresa","empresarial","pyme","corporativo","nómina","nomina",
    "hipotecario","hipoteca","vivienda","vehículo","vehiculo",
    "visa","mastercard","débito","debito",
    "fiducia","fiduciaria","valores","bolsa",
    "cliente","usuario","afiliado","beneficiario","titular",
    "documento","requisito","formulario","cédula","cedula","rut",
    "superfinanciera","fogafín","fogafin","habeas","consumidor",
    "abrir","solicitar","obtener","adquirir","contratar",
    "producto","productos","servicio","servicios","beneficio",
    "misión","mision","visión","vision","historia","fundación","fundacion",
    "sostenibilidad","responsabilidad","gobierno","junta",
}


# ════════════════════════════════════════════════════════════════
# VECTOR STORE
# ════════════════════════════════════════════════════════════════

def _load_vector_store():
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        raise FileNotFoundError(
            f"Vector store no encontrado en: {CHROMA_DIR}\n"
            "Ejecuta primero: python main.py --step chunks"
        )

    import chromadb
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

    vectorstore = Chroma(
        client=chroma_client,
        collection_name=CHROMA_COLLECTION,
        embedding_function=embeddings,
    )

    count = vectorstore._collection.count()
    print(f"[llm_chains] Vector store cargado: {count} chunks indexados")
    return vectorstore


try:
    _vectorstore      = _load_vector_store()
    VECTORSTORE_READY = True
    VECTORSTORE_ERROR = ""
except Exception as exc:
    _vectorstore      = None
    VECTORSTORE_READY = False
    VECTORSTORE_ERROR = str(exc)
    print(f"[llm_chains] ⚠️ Vector store: {exc}")


# ════════════════════════════════════════════════════════════════
# LLM
# ════════════════════════════════════════════════════════════════

def _build_llm(model, temperature=0.1, top_p=0.9):
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
        top_p=top_p,
        convert_system_message_to_human=True,
    )


def _init_llm():
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY no encontrada en .env. "
            "Obtén tu key en https://aistudio.google.com/apikey"
        )
    candidates = [PRIMARY_MODEL] + [m for m in FALLBACK_MODELS if m != PRIMARY_MODEL]
    last_err = None
    for model in candidates:
        try:
            print(f"[llm_chains] Probando: {model}")
            client = _build_llm(model)
            from langchain_core.messages import HumanMessage
            client.invoke([HumanMessage(content="ping")])
            print(f"[llm_chains] Activo: {model}")
            return client, model
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ("404", "not_found", "429", "quota", "resource_exhausted")):
                print(f"[llm_chains] {model} no disponible, probando siguiente...")
                last_err = e
            else:
                raise
    raise RuntimeError(f"Ningún modelo disponible. Último error: {last_err}")


try:
    _llm, ACTIVE_MODEL = _init_llm()
    LLM_READY = True
    LLM_ERROR = ""
except Exception as exc:
    _llm         = None
    ACTIVE_MODEL = "N/A"
    LLM_READY    = False
    LLM_ERROR    = str(exc)


# ════════════════════════════════════════════════════════════════
# RECUPERACIÓN SEMÁNTICA
# ════════════════════════════════════════════════════════════════

def _is_banking_query(query: str) -> bool:
    words = set(re.findall(r'\b\w+\b', query.lower()))
    return bool(words & BANKING_KEYWORDS)


def _get_context(query: str, top_k: int = 5, categoria: str = None):
    if not VECTORSTORE_READY or _vectorstore is None:
        return "", 0.0

    search_kwargs = {"k": top_k}
    if categoria and categoria in {
        "institucional", "cuentas", "tarjetas", "creditos",
        "inversion", "empresarial", "seguros", "digital", "atencion", "legal",
    }:
        search_kwargs["filter"] = {"categoria": categoria}

    try:
        results = _vectorstore.similarity_search_with_relevance_scores(
            query, **search_kwargs
        )
    except Exception as e:
        print(f"[llm_chains] Error en búsqueda: {e}")
        return "", 0.0

    if not results:
        return "", 0.0

    best_score = results[0][1]
    filtered   = [doc.page_content for doc, score in results if score >= SIMILARITY_THRESHOLD]

    if not filtered:
        return "", best_score

    return "\n\n---\n\n".join(filtered), best_score


# ════════════════════════════════════════════════════════════════
# PROMPTS
# ════════════════════════════════════════════════════════════════

_BASE_RULES = """
REGLAS ABSOLUTAS (jamás violables):
1. Responde ÚNICAMENTE con información presente en el CONTEXTO.
2. PROHIBIDO inventar tasas, plazos, montos, requisitos, teléfonos o datos no presentes.
3. PROHIBIDO usar conocimiento externo al contexto.
4. PROHIBIDO responder sobre temas no bancarios bajo ninguna circunstancia.
5. PROHIBIDO mencionar "contexto", "documentos" o detalles del sistema.
6. Si el contexto es insuficiente → aplica la frase de rechazo indicada.
"""

_QA_PROMPT = """# IDENTIDAD Y MISIÓN
Eres el Asistente Virtual Oficial del Banco de Occidente, entidad financiera
colombiana fundada en 1965, parte del Grupo Aval. Respondes EXCLUSIVAMENTE sobre
productos, servicios e información corporativa de este banco.
""" + _BASE_RULES + """
# PROTOCOLO

PASO 1 — VERIFICAR DOMINIO:
   ¿La pregunta es del Banco de Occidente?
   - NO → Responde exactamente:
     "No cuento con información sobre ese tema. Mi conocimiento se limita
     a productos, servicios e información oficial del Banco de Occidente.
     ¿Hay algo del banco en lo que pueda ayudarte?"

PASO 2 — VERIFICAR EVIDENCIA EN EL CONTEXTO:
   ¿El contexto contiene la información para responder?
   - NO → Responde exactamente:
     "No cuento con información específica sobre ese tema. Te invito a
     contactar la línea de atención del banco o visitar una sucursal."

PASO 3 — RESPONDER con los datos del contexto.

# EJEMPLOS
Pregunta: "¿Quién ganó el mundial 2022?"
✅ Usar el rechazo del PASO 1. Nunca mencionar fútbol.

Pregunta: "¿Qué tarjetas de crédito tienen?"
✅ Listar tarjetas del contexto con sus características.
❌ Inventar tarjetas o tasas.

# FORMATO
- Español formal, primera persona del banco ("ofrecemos", "contamos con").
- 2-4 párrafos cortos. Viñetas solo si enumeras 3+ elementos.
- Negritas para nombres de productos. Sin emojis ni headers.

# AUTOVERIFICACIÓN
□ ¿La pregunta es del banco?      □ ¿Cada dato está en el contexto?
□ ¿No inventé nada?               □ ¿Usé solo información bancaria?

# CONTEXTO SEMÁNTICO RECUPERADO
{context}
"""

_SUMMARY_PROMPT = """# IDENTIDAD Y MISIÓN
Eres un Analista Senior de Productos del Banco de Occidente. Generas resúmenes
ejecutivos profesionales sobre productos o servicios del banco.
""" + _BASE_RULES + """
# PROTOCOLO

PASO 1 — VERIFICAR DOMINIO:
   ¿El tema pertenece al banco?
   - NO → "No puedo generar un resumen sobre ese tema. Mi función se limita
     a productos y servicios del Banco de Occidente."

PASO 2 — VERIFICAR PROFUNDIDAD:
   ¿El contexto tiene suficiente información?
   - NO → "No cuento con información suficiente para un resumen ejecutivo
     sobre ese tema. Consulta directamente con un asesor del banco."

PASO 3 — GENERAR EL RESUMEN con la estructura obligatoria.

# ESTRUCTURA OBLIGATORIA
Incluye SOLO las secciones con información real en el contexto:

**Descripción general** — Qué es el producto en 2-3 oraciones.
**Características principales** — Lista de atributos técnicos (min 3, max 7).
**Beneficios para el cliente** — Valor real para el cliente (min 3 ítems).
**Requisitos o condiciones** — Documentos o perfiles necesarios.
**Público objetivo** — Para quién está diseñado (1-2 oraciones).

PROHIBIDO rellenar secciones con texto genérico vacío.
PROHIBIDO usar lenguaje de marketing ("excelente", "increíble", "el mejor").

# AUTOVERIFICACIÓN
□ ¿Cada sección tiene datos reales?  □ ¿Omití las secciones sin información?

# CONTEXTO SEMÁNTICO RECUPERADO
{context}
"""

_FAQ_PROMPT = """# IDENTIDAD Y MISIÓN
Eres un Especialista Senior de Servicio al Cliente del Banco de Occidente con
10+ años atendiendo consultas reales. Generas FAQs que reflejan las dudas
reales que los clientes expresan en sucursales y por teléfono.
""" + _BASE_RULES + """
# PROTOCOLO

PASO 1 — VERIFICAR DOMINIO:
   ¿El tema pertenece al banco?
   - NO → "No puedo generar FAQs sobre ese tema."

PASO 2 — VERIFICAR INFORMACIÓN:
   ¿El contexto permite 3+ preguntas sustantivas?
   - NO → "No cuento con información suficiente para FAQs sobre ese tema."

PASO 3 — GENERAR FAQ siguiendo el formato.

# CRITERIOS DE PREGUNTAS REALISTAS
✅ BUENAS — suenan a cliente real:
- "¿Cuánto me cuesta tener la tarjeta?"
- "¿Qué papeles necesito para abrir la cuenta?"

❌ MALAS — académicas:
- "¿Cuáles son las características y atributos del producto?"

# DIVERSIDAD TEMÁTICA
Cubre categorías distintas: costo · requisitos · proceso · beneficios · restricciones

# FORMATO ESTRICTO

**P1: [pregunta como la haría un cliente real]**

R: [respuesta directa de 2-3 oraciones basada en el contexto]

**P2: [pregunta distinta, otra categoría]**

R: [respuesta]

# REGLAS
- Entre 3 y 5 preguntas. Si solo hay info para 3, genera 3.
- PROHIBIDO respuestas vagas. Si el dato existe, úsalo.
- PROHIBIDO repetir información entre preguntas.

# CONTEXTO SEMÁNTICO RECUPERADO
{context}
"""

_REFUSAL_MESSAGE = (
    "No cuento con información sobre ese tema. Mi conocimiento se limita "
    "exclusivamente a los productos, servicios e información oficial del "
    "Banco de Occidente. Si tu consulta está relacionada con el banco, "
    "te invito a reformularla. De lo contrario, contáctanos en la línea "
    "de atención al cliente o visita una sucursal."
)


# ════════════════════════════════════════════════════════════════
# INVOCACIÓN AL LLM
# ════════════════════════════════════════════════════════════════

def _call(prompt_template: str, context: str, user_msg: str,
          temperature=None, top_p=None) -> str:
    if not LLM_READY:
        return f"⚠️ Motor no disponible: {LLM_ERROR}"

    from langchain_core.messages import SystemMessage, HumanMessage
    system = prompt_template.format(context=context)

    client = _build_llm(ACTIVE_MODEL, temperature or 0.1, top_p or 0.9) \
             if (temperature is not None or top_p is not None) else _llm

    try:
        resp = client.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
        return resp.content.strip()
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "quota" in msg or "resource_exhausted" in msg:
            return "⚠️ Límite de consultas alcanzado. Espera unos segundos e intenta de nuevo."
        return f"⚠️ Error: {str(e)[:200]}"


# ════════════════════════════════════════════════════════════════
# FUNCIONES PÚBLICAS
# ════════════════════════════════════════════════════════════════

def ask_question(question: str, temperature=None, top_p=None) -> str:
    context, score = _get_context(question, top_k=5)
    if not context:
        return _REFUSAL_MESSAGE
    return _call(_QA_PROMPT, context, question, temperature, top_p)

def make_summary(topic: str, temperature=None, top_p=None) -> str:
    context, score = _get_context(topic, top_k=8)
    if not context:
        return _REFUSAL_MESSAGE
    msg = (
        f"Genera un resumen ejecutivo sobre: **{topic}**.\n"
        "Incluye únicamente las secciones con información real."
    )
    return _call(_SUMMARY_PROMPT, context, msg, temperature, top_p)


def make_faq(topic: str, temperature=None, top_p=None) -> str:
    context, score = _get_context(topic, top_k=8)
    if not context:
        return _REFUSAL_MESSAGE
    msg = (
        f"Genera entre 3 y 5 preguntas frecuentes sobre: **{topic}**.\n"
        "Preguntas como las haría un cliente real al teléfono o en sucursal."
    )
    return _call(_FAQ_PROMPT, context, msg, temperature, top_p)


# ════════════════════════════════════════════════════════════════
# DIAGNÓSTICO
# ══════════════════════════════════════════

def get_status() -> dict:
    chunk_count = 0
    if VECTORSTORE_READY and _vectorstore:
        try:
            chunk_count = _vectorstore._collection.count()
        except Exception:
            pass

    return {
        "llm_ready":         LLM_READY,
        "llm_error":         LLM_ERROR,
        "vectorstore_ready": VECTORSTORE_READY,
        "vectorstore_error": VECTORSTORE_ERROR,
        "provider":          "GEMINI",
        "model":             ACTIVE_MODEL,
        "embedding_model":   EMBEDDING_MODEL,
        "corpus_docs":       chunk_count,
        "threshold":         SIMILARITY_THRESHOLD,
    }
