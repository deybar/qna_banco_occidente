"""
llm_chains.py — Motor de IA del Sistema Q&A Banco de Occidente
═══════════════════════════════════════════════════════════════════════════════
Proveedor LLM: Google AI Studio (Gemini)
Modelos compatibles con free tier (abril 2026):
  - gemini-2.5-flash      (recomendado, balance ideal)
  - gemini-2.5-flash-lite (mayor cuota gratuita)
  - gemini-3-flash        (más nuevo)
"""

import os
import re
import math
from collections import Counter
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# ════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Modelo principal y modelos de fallback automático
# Si el principal falla, intenta con los siguientes en orden
PRIMARY_MODEL  = os.getenv("GEMINI_MODEL", "Gemma-3-1B")
FALLBACK_MODELS = [
    "Gemini 3.1 Flash Lite"
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-flash",
    "gemini-flash-latest",
]

CORPUS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "corpus_master.md"
)

RELEVANCE_THRESHOLD = 0.08

STOPWORDS_ES = {
    "de","la","el","en","y","a","los","del","se","las","un","por","con","una",
    "su","para","es","al","lo","como","mas","pero","sus","le","ya","o","este",
    "si","porque","esta","entre","cuando","muy","sin","sobre","también","me",
    "hasta","hay","donde","quien","desde","todo","nos","durante","todos","uno",
    "les","ni","contra","otros","ese","eso","ante","ellos","e","esto","antes",
    "algunos","unos","yo","otro","otras","otra","tanto","esa","estos","mucho",
    "cual","poco","ella","estar","estas","algunas","algo","nosotros","mis",
    "que","fue","son","han","ser","tiene","ha","están","está","puede","no",
    "así","bien","vez","cada","aquí","mismo","tan","más","él","tú","te","ti",
}

_SYNONYMS = {
    "tarjeta":    ["tarjetas", "crédito", "débito", "visa", "mastercard", "plástico"],
    "tarjetas":   ["tarjeta", "crédito", "débito", "visa", "mastercard"],
    "cuenta":     ["cuentas", "ahorro", "ahorros", "corriente", "depósito"],
    "cuentas":    ["cuenta", "ahorro", "corriente", "depósito"],
    "crédito":    ["créditos", "préstamo", "préstamos", "financiamiento", "financiación"],
    "propósito":  ["misión", "visión", "objetivo", "filosofía", "corporativo", "quienes"],
    "proposito":  ["misión", "visión", "objetivo", "filosofía", "corporativo"],
    "banco":      ["bancario", "entidad", "institución", "financiero", "occidente"],
    "productos":  ["producto", "servicio", "servicios", "oferta", "portafolio", "soluciones"],
    "producto":   ["productos", "servicio", "servicios", "oferta", "portafolio"],
    "requisitos": ["requisito", "condiciones", "documentos", "solicitar", "cómo"],
    "beneficios": ["beneficio", "ventajas", "características", "ventaja"],
    "inversión":  ["inversiones", "invertir", "rentabilidad", "portafolio", "fondos"],
    "digital":    ["online", "virtual", "internet", "app", "aplicación", "banca"],
    "empresa":    ["empresas", "corporativo", "pyme", "empresarial", "negocios"],
    "hipotecario":["vivienda", "hipoteca", "inmueble", "casa", "apartamento"],
    "seguro":     ["seguros", "protección", "cobertura", "póliza"],
    "tasa":       ["tasas", "interés", "porcentaje", "costo", "cobro"],
    "sucursal":   ["sucursales", "oficina", "agencia", "punto", "atención"],
}


# ════════════════════════════════════════════════════════════════
# 2. CHUNKING POR SECCIONES
# ════════════════════════════════════════════════════════════════
def _split_into_sections(corpus: str) -> list:
    chunks = []
    documents = re.split(r"={40,}", corpus)
    for doc in documents:
        doc = doc.strip()
        if len(doc) < 100:
            continue
        sections = re.split(r"\n(?=#{1,3} )", doc)
        for section in sections:
            section = section.strip()
            if len(section) < 150:
                continue
            if re.match(r"^(URL:|Fuente documental:|---|Fuente:)", section):
                continue
            chunks.append(section)
    return chunks


def _load_corpus() -> list:
    if not os.path.exists(CORPUS_FILE):
        raise FileNotFoundError(
            f"No se encontró el corpus en: {CORPUS_FILE}\n"
            "Ejecuta primero: python 05_corpus_master.py"
        )
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        raw = f.read()
    chunks = _split_into_sections(raw)
    print(f"[llm_chains] Corpus cargado: {len(chunks)} secciones semánticas")
    return chunks


_chunks = _load_corpus()


# ════════════════════════════════════════════════════════════════
# 3. VECTORIZACIÓN TF-IDF
# ════════════════════════════════════════════════════════════════
_vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=20_000,
    sublinear_tf=True,
    stop_words=list(STOPWORDS_ES),
    min_df=1,
    max_df=0.85,
)
_matrix = _vectorizer.fit_transform(_chunks)


# ════════════════════════════════════════════════════════════════
# 4. BM25
# ════════════════════════════════════════════════════════════════
_AVG_CHUNK_LEN = max(1, sum(len(c.split()) for c in _chunks) // max(len(_chunks), 1))


def _bm25_score(query_terms: list, doc: str, k1: float = 1.5, b: float = 0.75) -> float:
    doc_words = [w for w in re.findall(r'\b\w+\b', doc.lower()) if w not in STOPWORDS_ES]
    doc_len   = max(len(doc_words), 1)
    freq      = Counter(doc_words)
    N         = len(_chunks)
    score     = 0.0
    for term in query_terms:
        f = freq.get(term, 0)
        if f == 0:
            continue
        idf     = math.log((N - 1 + 0.5) / (1 + 1) + 1)
        tf_norm = (f * (k1 + 1)) / (f + k1 * (1 - b + b * doc_len / _AVG_CHUNK_LEN))
        score  += idf * tf_norm
    return score


# ════════════════════════════════════════════════════════════════
# 5. EXPANSIÓN DE QUERY
# ════════════════════════════════════════════════════════════════
def _expand_query(query: str) -> str:
    words  = query.lower().split()
    extras = []
    for w in words:
        clean = re.sub(r'[^a-záéíóúñ]', '', w)
        if clean in _SYNONYMS:
            extras.extend(_SYNONYMS[clean])
    return (query + " " + " ".join(set(extras))).strip() if extras else query


# ════════════════════════════════════════════════════════════════
# 6. RECUPERADOR HÍBRIDO
# ════════════════════════════════════════════════════════════════
def _get_context(query: str, top_k: int = 5):
    expanded    = _expand_query(query)
    q_vec       = _vectorizer.transform([expanded])
    sims        = cosine_similarity(q_vec, _matrix).flatten()
    candidates  = sims.argsort()[-15:][::-1]
    best_tfidf  = float(sims[candidates[0]]) if len(candidates) > 0 else 0.0

    if best_tfidf < 0.03:
        return "", 0.0

    query_terms = [
        w for w in re.findall(r'\b\w+\b', expanded.lower())
        if w not in STOPWORDS_ES and len(w) > 2
    ]

    scored = []
    for idx in candidates:
        tfidf_s  = float(sims[idx])
        bm25_s   = _bm25_score(query_terms, _chunks[idx])
        combined = 0.7 * tfidf_s + 0.3 * min(bm25_s / 10.0, 1.0)
        scored.append((combined, idx))

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score = scored[0][0] if scored else 0.0

    selected = [
        _chunks[idx]
        for score, idx in scored[:top_k]
        if score >= RELEVANCE_THRESHOLD
    ]

    if not selected:
        return "", best_score

    return "\n\n---\n\n".join(selected), best_score


# ════════════════════════════════════════════════════════════════
# 7. INICIALIZACIÓN DEL LLM CON FALLBACK AUTOMÁTICO
# ════════════════════════════════════════════════════════════════

def _try_build_llm(model_name: str):
    """Intenta construir un cliente LLM para un modelo específico."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        convert_system_message_to_human=True,
    )


def _build_llm_with_fallback():
    """
    Intenta el modelo principal. Si falla por modelo no encontrado,
    prueba con la lista de fallbacks. Retorna (cliente, modelo_usado).
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY no definida en .env. "
            "Obtén tu key en https://aistudio.google.com/apikey"
        )

    # Lista priorizada: primero el del .env, luego los fallbacks (sin duplicar)
    candidates = [PRIMARY_MODEL] + [
        m for m in FALLBACK_MODELS if m != PRIMARY_MODEL
    ]

    last_error = None
    for model in candidates:
        try:
            print(f"[llm_chains] Intentando modelo: {model}")
            client = _try_build_llm(model)
            # Test rápido para verificar que el modelo realmente responde
            from langchain_core.messages import HumanMessage
            client.invoke([HumanMessage(content="ping")])
            print(f"[llm_chains] ✅ Modelo activo: {model}")
            return client, model
        except Exception as e:
            err_str = str(e).lower()
            # Si es 404 (modelo no existe), intentar siguiente
            # Si es 429 (cuota), también intentar otro modelo
            if "404" in err_str or "not_found" in err_str or "not found" in err_str:
                print(f"[llm_chains] ⚠️ Modelo {model} no disponible, probando siguiente...")
                last_error = e
                continue
            elif "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                print(f"[llm_chains] ⚠️ Modelo {model} sin cuota, probando siguiente...")
                last_error = e
                continue
            else:
                # Otro error: no tiene sentido seguir intentando
                raise

    # Si ningún modelo funcionó
    raise RuntimeError(
        f"Ningún modelo Gemini está disponible para tu API Key.\n"
        f"Modelos intentados: {candidates}\n"
        f"Último error: {last_error}\n"
        f"Verifica tu key en https://aistudio.google.com/apikey"
    )


try:
    _llm, ACTIVE_MODEL = _build_llm_with_fallback()
    LLM_READY = True
    LLM_ERROR = ""
except Exception as exc:
    _llm         = None
    ACTIVE_MODEL = "N/A"
    LLM_READY    = False
    LLM_ERROR    = str(exc)


# ════════════════════════════════════════════════════════════════
# 8. PROMPT ENGINEERING — ANTI-ALUCINACIÓN ZERO-SHOT
# ════════════════════════════════════════════════════════════════
_SYSTEM_PROMPT = """Eres el Asistente Virtual Oficial del Banco de Occidente, \
entidad financiera colombiana fundada en 1965 con presencia nacional.

REGLAS CRÍTICAS DE COMPORTAMIENTO (ZERO-SHOT, INVIOLABLES):

1. FUENTE ÚNICA DE VERDAD
   Responde EXCLUSIVAMENTE con información presente en el CONTEXTO DOCUMENTAL.
   El contexto es tu única fuente válida. Tu conocimiento previo NO aplica.

2. PROHIBICIÓN DE INVENCIÓN
   NUNCA inventes ni infieras: tasas, plazos, montos, requisitos, productos, \
   nombres de funcionarios, direcciones, teléfonos o condiciones que no estén \
   literalmente en el contexto.

3. PROHIBICIÓN DE CONOCIMIENTO EXTERNO
   NO uses información sobre otros bancos, productos genéricos del sector, \
   ni datos generales que recuerdes de tu entrenamiento.

4. RESPUESTA HONESTA ANTE INSUFICIENCIA
   Si el contexto no contiene información suficiente, responde EXACTAMENTE:
   "No cuento con información específica sobre ese tema en la base documental \
   actual. Para mayor información, te invito a comunicarte con la línea de \
   atención al cliente del Banco de Occidente o visitar una sucursal."

5. TRANSPARENCIA SOBRE INFORMACIÓN PARCIAL
   Si el contexto tiene información parcial, preséntala con claridad y \
   reconoce los aspectos que no están cubiertos.

6. ESTILO DE COMUNICACIÓN
   Responde en español formal, cálido y orientado al servicio al cliente. \
   Usa primera persona del banco ("ofrecemos", "contamos con").

7. FORMATO DE RESPUESTA
   - Usa listas con viñetas al enumerar productos, beneficios o requisitos.
   - Usa **negritas** solo para nombres de productos o conceptos clave.
   - Mantén párrafos cortos (máximo 3-4 líneas).
   - No uses emojis.

8. OPACIDAD TÉCNICA
   NUNCA menciones palabras como "contexto", "documentos", "base documental" \
   o referencias a la arquitectura del sistema.

9. VERIFICACIÓN INTERNA ANTES DE RESPONDER
   Antes de emitir cada respuesta, valida que cada afirmación esté respaldada \
   por el contexto. Si no es así, aplica la Regla #4.

═══════════════════════════════════════
CONTEXTO DOCUMENTAL DISPONIBLE:
═══════════════════════════════════════

{context}

═══════════════════════════════════════
FIN DEL CONTEXTO
═══════════════════════════════════════
"""

_NO_INFO_RESPONSE = (
    "No cuento con información específica sobre ese tema en la base documental "
    "actual. Para mayor información, te invito a comunicarte con la línea de "
    "atención al cliente del Banco de Occidente o visitar una sucursal."
)


def _invoke_llm(context: str, user_msg: str) -> str:
    if not LLM_READY:
        return f"⚠️ Motor de IA no disponible: {LLM_ERROR}"
    from langchain_core.messages import SystemMessage, HumanMessage
    system_content = _SYSTEM_PROMPT.format(context=context)
    try:
        response = _llm.invoke([
            SystemMessage(content=system_content),
            HumanMessage(content=user_msg),
        ])
        return response.content.strip()
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
            return (
                "⚠️ Se ha alcanzado el límite de consultas por minuto del free tier de "
                "Gemini. Por favor espera unos segundos y vuelve a intentar."
            )
        return f"⚠️ Error al consultar el modelo: {str(e)[:200]}"


# ════════════════════════════════════════════════════════════════
# 9. FUNCIONES PÚBLICAS
# ════════════════════════════════════════════════════════════════
def ask_question(question: str) -> str:
    context, score = _get_context(question, top_k=5)
    if not context or score < RELEVANCE_THRESHOLD:
        return _NO_INFO_RESPONSE
    return _invoke_llm(context, question)


def make_summary(topic: str) -> str:
    context, score = _get_context(topic, top_k=7)
    if not context or score < RELEVANCE_THRESHOLD:
        return _NO_INFO_RESPONSE
    user_prompt = (
        f"Genera un **resumen ejecutivo estructurado** sobre: **{topic}**.\n\n"
        "El resumen debe organizarse en las siguientes secciones, "
        "incluyendo SOLO las que tengan respaldo en el contexto:\n\n"
        "**1. Descripción general**\n"
        "**2. Características principales**\n"
        "**3. Beneficios para el cliente**\n"
        "**4. Requisitos o condiciones** (si aplica)\n"
        "**5. Público objetivo** (si aplica)\n\n"
        "Si una sección no tiene información en el contexto, OMÍTELA por completo."
    )
    return _invoke_llm(context, user_prompt)


def make_faq(topic: str) -> str:
    context, score = _get_context(topic, top_k=7)
    if not context or score < RELEVANCE_THRESHOLD:
        return _NO_INFO_RESPONSE
    user_prompt = (
        f"Genera entre **3 y 5 preguntas frecuentes (FAQ)** con sus respuestas "
        f"sobre: **{topic}**.\n\n"
        "INSTRUCCIONES:\n"
        "- Las preguntas deben ser realistas, las que un cliente real haría.\n"
        "- Cada respuesta debe estar 100% basada en el contexto disponible.\n"
        "- Si solo hay información para 3 preguntas, genera 3 (no 5 con relleno).\n\n"
        "FORMATO OBLIGATORIO:\n\n"
        "**P1: [pregunta del cliente]**  \n"
        "R: [respuesta basada en el contexto]\n\n"
        "**P2: [pregunta]**  \n"
        "R: [respuesta]\n\n"
        "...y así sucesivamente."
    )
    return _invoke_llm(context, user_prompt)


# ════════════════════════════════════════════════════════════════
# 10. DIAGNÓSTICO PARA STREAMLIT
# ════════════════════════════════════════════════════════════════
def get_status() -> dict:
    return {
        "llm_ready":   LLM_READY,
        "llm_error":   LLM_ERROR,
        "provider":    "GEMINI",
        "model":       ACTIVE_MODEL,
        "corpus_docs": len(_chunks),
        "threshold":   RELEVANCE_THRESHOLD,
    }
