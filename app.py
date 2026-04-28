"""
app.py — Sistema Q&A Banco de Occidente · Asistente Virtual Corporativo
═══════════════════════════════════════════════════════════════════════
Identidad visual corporativa: paleta azul Banco de Occidente
Maestría en IA y Ciencia de Datos · Universidad Autónoma de Occidente
"""

import time
import streamlit as st
from llm_chains import ask_question, make_summary, make_faq, get_status

# ════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Banco de Occidente · Asistente IA",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════
# DISEÑO CORPORATIVO — IDENTIDAD VISUAL BANCO DE OCCIDENTE
# Paleta azul oficial monocromática
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    /* ─── PALETA AZUL BANCO DE OCCIDENTE ─── */
    --bdo-blue:        #003DA5;   /* Azul corporativo principal */
    --bdo-blue-dark:   #002A75;   /* Azul oscuro - hover/énfasis */
    --bdo-blue-deep:   #001E55;   /* Azul muy oscuro - footer/sombras */
    --bdo-blue-light:  #4D7BC4;   /* Azul claro - acentos */
    --bdo-blue-pale:   #E6EDF7;   /* Azul muy claro - fondos sutiles */
    --bdo-blue-50:     #F0F5FB;   /* Azul casi blanco - cards */

    /* ─── NEUTROS ─── */
    --neutral-900:    #0F172A;
    --neutral-800:    #1E293B;
    --neutral-700:    #334155;
    --neutral-600:    #475569;
    --neutral-500:    #64748B;
    --neutral-400:    #94A3B8;
    --neutral-300:    #CBD5E1;
    --neutral-200:    #E2E8F0;
    --neutral-100:    #F1F5F9;
    --neutral-50:     #F8FAFC;

    /* ─── ESTADOS ─── */
    --success:        #059669;
    --success-light:  #D1FAE5;
    --warning:        #D97706;

    /* ─── SOMBRAS Y RADIOS ─── */
    --shadow-sm:  0 1px 2px rgba(0, 61, 165, 0.05);
    --shadow-md:  0 4px 6px rgba(0, 61, 165, 0.07);
    --shadow-lg:  0 10px 15px rgba(0, 61, 165, 0.10);
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
}

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--neutral-900);
}

.stApp {
    background: linear-gradient(180deg, #FAFBFC 0%, #F0F5FB 100%);
}

.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem;
    max-width: 1280px;
}

/* ─── HEADER CORPORATIVO ─────────────────────────────────────── */
.bdo-header {
    background: linear-gradient(135deg, #003DA5 0%, #002A75 50%, #001E55 100%);
    margin: -1rem -1rem 2rem -1rem;
    padding: 28px 40px;
    box-shadow: 0 4px 20px rgba(0, 61, 165, 0.25);
    position: relative;
    overflow: hidden;
}
.bdo-header::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 400px; height: 100%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
}
.bdo-header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    z-index: 1;
}
.bdo-brand {
    display: flex;
    align-items: center;
    gap: 18px;
}
.bdo-logo {
    background: white;
    color: #003DA5;
    width: 52px;
    height: 52px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.4rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    letter-spacing: -1px;
}
.bdo-title h1 {
    color: white;
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.3px;
}
.bdo-title p {
    color: rgba(255,255,255,0.85);
    font-size: 0.875rem;
    margin: 2px 0 0 0;
    font-weight: 400;
}
.bdo-header-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
}
.bdo-badge {
    background: rgba(255,255,255,0.15);
    color: white;
    border: 1px solid rgba(255,255,255,0.25);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.bdo-timestamp {
    color: rgba(255,255,255,0.75);
    font-size: 0.75rem;
}

/* ─── SECCIONES INTRO ────────────────────────────────────────── */
.section-intro {
    background: white;
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--neutral-200);
    border-top: 3px solid var(--bdo-blue);
    margin-bottom: 24px;
}
.section-intro h2 {
    color: var(--bdo-blue-deep);
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0 0 6px 0;
}
.section-intro p {
    color: var(--neutral-700);
    font-size: 0.95rem;
    margin: 0;
    line-height: 1.6;
}

/* ─── TABS ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-radius: var(--radius-lg);
    padding: 6px;
    gap: 4px;
    border: 1px solid var(--neutral-200);
    box-shadow: var(--shadow-sm);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--neutral-600);
    border-radius: var(--radius-md);
    padding: 12px 20px;
    font-weight: 600;
    font-size: 0.9rem;
}
.stTabs [aria-selected="true"] {
    background: var(--bdo-blue) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(0, 61, 165, 0.30);
}

/* ─── INPUTS ─────────────────────────────────────────────────── */
.stTextInput > div > div > input {
    background: white !important;
    border: 1.5px solid var(--neutral-200) !important;
    border-radius: var(--radius-md) !important;
    color: var(--neutral-900) !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--bdo-blue) !important;
    box-shadow: 0 0 0 3px rgba(0, 61, 165, 0.12) !important;
}

/* ─── BOTONES ────────────────────────────────────────────────── */
.stButton > button {
    background: var(--bdo-blue);
    color: white;
    font-weight: 600;
    font-size: 0.95rem;
    border: none;
    border-radius: var(--radius-md);
    padding: 12px 32px;
    box-shadow: 0 2px 4px rgba(0, 61, 165, 0.25);
    width: 100%;
}
.stButton > button:hover {
    background: var(--bdo-blue-dark);
    box-shadow: 0 4px 14px rgba(0, 61, 165, 0.35);
}

/* ═══════════════════════════════════════════════════════════════
   ANSWER CARD — CORRECCIÓN CRÍTICA DEL TEXTO BLANCO
   Forzamos color de texto en TODOS los elementos hijos
   ═══════════════════════════════════════════════════════════════ */
.answer-card {
    background: white;
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    margin-top: 16px;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--neutral-200);
    border-left: 4px solid var(--bdo-blue);
    line-height: 1.7;
}

/* Forzar color oscuro en TODO el contenido del card */
.answer-card,
.answer-card p,
.answer-card div,
.answer-card span,
.answer-card li,
.answer-card td,
.answer-card th {
    color: var(--neutral-800) !important;
    font-size: 0.97rem;
}

.answer-card strong,
.answer-card b {
    color: var(--bdo-blue-deep) !important;
    font-weight: 700;
}

.answer-card h1, .answer-card h2, .answer-card h3,
.answer-card h4, .answer-card h5, .answer-card h6 {
    color: var(--bdo-blue) !important;
    margin-top: 16px;
    margin-bottom: 8px;
    font-weight: 700;
}

.answer-card ul, .answer-card ol {
    padding-left: 24px;
    color: var(--neutral-800) !important;
}

.answer-card li {
    margin-bottom: 6px;
    color: var(--neutral-800) !important;
}

.answer-card a {
    color: var(--bdo-blue) !important;
    text-decoration: underline;
}

.answer-card code {
    background: var(--bdo-blue-pale);
    color: var(--bdo-blue-deep) !important;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
}

.answer-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--neutral-100);
    color: var(--neutral-500) !important;
    font-size: 0.8rem;
}

.answer-meta span {
    color: var(--neutral-500) !important;
}

.answer-meta strong {
    color: var(--bdo-blue-deep) !important;
}

/* También aplicar reglas a elementos generados por st.markdown dentro del card */
.answer-card [data-testid="stMarkdownContainer"] *,
.answer-card .stMarkdown * {
    color: var(--neutral-800) !important;
}

.answer-card [data-testid="stMarkdownContainer"] strong,
.answer-card .stMarkdown strong {
    color: var(--bdo-blue-deep) !important;
}

.answer-card [data-testid="stMarkdownContainer"] h1,
.answer-card [data-testid="stMarkdownContainer"] h2,
.answer-card [data-testid="stMarkdownContainer"] h3 {
    color: var(--bdo-blue) !important;
}

/* ─── EXAMPLE CHIPS ──────────────────────────────────────────── */
.example-section {
    background: var(--bdo-blue-pale);
    border: 1px solid var(--bdo-blue-light);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    margin-bottom: 16px;
}
.example-section-title {
    color: var(--bdo-blue-deep);
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.example-chip {
    display: inline-block;
    background: white;
    border: 1px solid var(--bdo-blue-light);
    color: var(--bdo-blue-deep);
    font-size: 0.85rem;
    padding: 6px 12px;
    border-radius: 20px;
    margin: 3px 4px 3px 0;
}

/* ─── SIDEBAR ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid var(--neutral-200);
}
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 12px 20px 12px;
    border-bottom: 1px solid var(--neutral-100);
    margin-bottom: 20px;
}
.sidebar-logo-icon {
    background: var(--bdo-blue);
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.1rem;
    box-shadow: 0 2px 8px rgba(0, 61, 165, 0.30);
}
.sidebar-logo-text strong {
    color: var(--neutral-900);
    font-size: 1rem;
    font-weight: 700;
    display: block;
}
.sidebar-logo-text span {
    color: var(--neutral-500);
    font-size: 0.75rem;
}
.sidebar-section-title {
    color: var(--neutral-500);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 20px 12px 10px 12px;
}
.status-card {
    background: var(--bdo-blue-50);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    margin: 0 12px 16px 12px;
    border: 1px solid var(--bdo-blue-pale);
}
.status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.status-row:last-child { margin-bottom: 0; }
.status-label {
    color: var(--neutral-600);
    font-size: 0.78rem;
    font-weight: 500;
}
.status-value {
    color: var(--bdo-blue-deep);
    font-size: 0.78rem;
    font-weight: 600;
}
.status-dot-active {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 0 3px var(--success-light);
    margin-right: 6px;
    animation: pulse 2s infinite;
}
.status-dot-inactive {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--warning);
    margin-right: 6px;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 12px;
    color: var(--neutral-700);
    font-size: 0.82rem;
}
.pipeline-check {
    color: var(--bdo-blue);
    font-weight: 700;
    font-size: 0.9rem;
}

/* ─── FOOTER ─────────────────────────────────────────────────── */
.bdo-footer {
    text-align: center;
    padding: 32px 0 16px 0;
    margin-top: 48px;
    color: var(--neutral-500);
    font-size: 0.78rem;
    border-top: 1px solid var(--neutral-200);
}
.bdo-footer strong { color: var(--bdo-blue-deep); }

/* ─── HIDE STREAMLIT BRANDING ────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# ESTADO DE SESIÓN
# ════════════════════════════════════════════════════════════════
if "history" not in st.session_state:
    st.session_state.history = []


# ════════════════════════════════════════════════════════════════
# OBTENER ESTADO DEL MOTOR
# ════════════════════════════════════════════════════════════════
status = get_status()
status_safe = {
    "llm_ready":   status.get("llm_ready", False),
    "llm_error":   status.get("llm_error", "Estado desconocido"),
    "provider":    status.get("provider", "N/A"),
    "model":       status.get("model", "N/A"),
    "corpus_docs": status.get("corpus_docs", 0),
    "threshold":   status.get("threshold", 0.08),
}


# ════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="bdo-header">
    <div class="bdo-header-content">
        <div class="bdo-brand">
            <div class="bdo-logo">BdO</div>
            <div class="bdo-title">
                <h1>Asistente Virtual Inteligente</h1>
                <p>Banco de Occidente · Sistema de Consulta Documental</p>
            </div>
        </div>
        <div class="bdo-header-meta">
            <span class="bdo-badge">MÓDULO 1 · Q&A CORPORATIVO</span>
            <span class="bdo-timestamp">{time.strftime('%d/%m/%Y · %H:%M')}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">BdO</div>
        <div class="sidebar-logo-text">
            <strong>Panel de Control</strong>
            <span>Asistente IA Corporativo</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Estado del Sistema</div>',
                unsafe_allow_html=True)

    if status_safe["llm_ready"]:
        st.markdown(f"""
        <div class="status-card">
            <div class="status-row">
                <span class="status-label"><span class="status-dot-active"></span>Estado</span>
                <span class="status-value" style="color: var(--success);">Operativo</span>
            </div>
            <div class="status-row">
                <span class="status-label">Proveedor</span>
                <span class="status-value">{status_safe["provider"]}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Modelo</span>
                <span class="status-value">{status_safe["model"]}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Secciones</span>
                <span class="status-value">{status_safe["corpus_docs"]:,}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Umbral relev.</span>
                <span class="status-value">{status_safe["threshold"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-card" style="border-color: var(--warning);">
            <div class="status-row">
                <span class="status-label"><span class="status-dot-inactive"></span>Estado</span>
                <span class="status-value" style="color: var(--warning);">Inactivo</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.error(f"⚠️ {status_safe['llm_error']}")

    st.markdown('<div class="sidebar-section-title">Pipeline de Datos</div>',
                unsafe_allow_html=True)
    pipeline_steps = [
        "Crawling de URLs",
        "Web Scraping (Selenium)",
        "Limpieza Documental",
        "Construcción Markdown",
        "Corpus Maestro",
        "Motor TF-IDF + BM25",
        "Integración LLM",
    ]
    for step in pipeline_steps:
        st.markdown(
            f'<div class="pipeline-step">'
            f'<span class="pipeline-check">✓</span> {step}</div>',
            unsafe_allow_html=True
        )

    if st.session_state.history:
        st.markdown('<div class="sidebar-section-title">Consultas Recientes</div>',
                    unsafe_allow_html=True)
        for item in st.session_state.history[-3:][::-1]:
            q_truncated = item['q'][:55] + "..." if len(item['q']) > 55 else item['q']
            st.markdown(
                f'<div class="pipeline-step" style="font-size: 0.78rem;">'
                f'› {q_truncated}</div>',
                unsafe_allow_html=True
            )
        if st.button("Limpiar historial", key="clear_history", type="secondary"):
            st.session_state.history = []
            st.rerun()

    st.markdown("""
    <div style="margin-top: 32px; padding: 16px 12px; border-top: 1px solid var(--neutral-100);
                color: var(--neutral-400); font-size: 0.7rem; text-align: center;">
        UAO · Maestría IA & CD<br>
        Técnicas Avanzadas de IA · 2026
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "💬   Preguntas y Respuestas",
    "📋   Resumen Ejecutivo",
    "❓   Generador de FAQ",
])

# ────────────────────────────────────────────────────────────────
# TAB 1 — PREGUNTAS Y RESPUESTAS
# ────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div class="section-intro">
        <h2>Consulta tu Asistente Virtual</h2>
        <p>Realiza preguntas sobre productos, servicios, requisitos, canales o cualquier tema
        relacionado con el Banco de Occidente.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="example-section">
        <div class="example-section-title">💡 Ejemplos de consultas</div>
        <span class="example-chip">¿Qué tarjetas de crédito ofrece el banco?</span>
        <span class="example-chip">¿Cuáles son los requisitos para abrir una cuenta?</span>
        <span class="example-chip">¿Cómo solicito un crédito de vehículo?</span>
        <span class="example-chip">¿Qué es la Banca de Inversión?</span>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        question = st.text_input(
            "Pregunta",
            placeholder="Escribe tu pregunta aquí...",
            key="qa_input",
            label_visibility="collapsed",
        )
    with col_btn:
        btn_ask = st.button("🔍 Consultar", key="btn_qa", use_container_width=True)

    if btn_ask:
        if not question.strip():
            st.warning("⚠️ Por favor escribe una pregunta antes de consultar.")
        elif not status_safe["llm_ready"]:
            st.error(f"❌ Motor de IA no disponible: {status_safe['llm_error']}")
        else:
            with st.spinner("Consultando la base de conocimiento del Banco de Occidente..."):
                t0      = time.time()
                answer  = ask_question(question)
                elapsed = time.time() - t0
                st.session_state.history.append({"q": question, "a": answer})

            # Container con clase explícita y st.markdown nativo
            with st.container():
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(answer)
                st.markdown(f"""
                <div class="answer-meta">
                    <span>⏱ <strong>{elapsed:.2f}s</strong></span>
                    <span>🤖 <strong>{status_safe["model"]}</strong></span>
                    <span>📚 <strong>{status_safe["corpus_docs"]} secciones</strong></span>
                </div>
                </div>
                """, unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# TAB 2 — RESUMEN EJECUTIVO
# ────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="section-intro">
        <h2>Generador de Resumen Ejecutivo</h2>
        <p>Obtén un resumen estructurado y profesional sobre cualquier producto, servicio o área
        del Banco de Occidente.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="example-section">
        <div class="example-section-title">💡 Temas sugeridos</div>
        <span class="example-chip">Crédito Hipotecario</span>
        <span class="example-chip">Banca Empresarial</span>
        <span class="example-chip">Cuenta de Ahorros</span>
        <span class="example-chip">Tarjetas de Crédito</span>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        summary_topic = st.text_input(
            "Tema",
            placeholder="Ej: Crédito hipotecario, Banca empresarial...",
            key="summary_input",
            label_visibility="collapsed",
        )
    with col_btn:
        btn_summary = st.button("📋 Generar", key="btn_summary", use_container_width=True)

    if btn_summary:
        if not summary_topic.strip():
            st.warning("⚠️ Por favor ingresa un tema para resumir.")
        elif not status_safe["llm_ready"]:
            st.error(f"❌ Motor de IA no disponible: {status_safe['llm_error']}")
        else:
            with st.spinner(f"Construyendo resumen ejecutivo sobre '{summary_topic}'..."):
                t0      = time.time()
                resumen = make_summary(summary_topic)
                elapsed = time.time() - t0

            with st.container():
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(f"### 📋 {summary_topic}")
                st.markdown(resumen)
                st.markdown(f"""
                <div class="answer-meta">
                    <span>⏱ <strong>{elapsed:.2f}s</strong></span>
                    <span>🤖 <strong>{status_safe["model"]}</strong></span>
                    <span>📊 <strong>Resumen Ejecutivo</strong></span>
                </div>
                </div>
                """, unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# TAB 3 — FAQ
# ────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div class="section-intro">
        <h2>Generador Automático de FAQ</h2>
        <p>Crea automáticamente un conjunto de preguntas frecuentes con sus respuestas sobre
        cualquier tema del banco.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="example-section">
        <div class="example-section-title">💡 Temas sugeridos</div>
        <span class="example-chip">Tarjetas de Crédito</span>
        <span class="example-chip">Crédito de Vehículo</span>
        <span class="example-chip">Inversiones y CDT</span>
        <span class="example-chip">Cuentas de Ahorro</span>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        faq_topic = st.text_input(
            "Tema FAQ",
            placeholder="Ej: Tarjetas de crédito, Inversiones...",
            key="faq_input",
            label_visibility="collapsed",
        )
    with col_btn:
        btn_faq = st.button("❓ Crear FAQ", key="btn_faq", use_container_width=True)

    if btn_faq:
        if not faq_topic.strip():
            st.warning("⚠️ Por favor ingresa un tema para el FAQ.")
        elif not status_safe["llm_ready"]:
            st.error(f"❌ Motor de IA no disponible: {status_safe['llm_error']}")
        else:
            with st.spinner(f"Generando preguntas frecuentes sobre '{faq_topic}'..."):
                t0      = time.time()
                faq_out = make_faq(faq_topic)
                elapsed = time.time() - t0

            with st.container():
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(f"### ❓ Preguntas Frecuentes: {faq_topic}")
                st.markdown(faq_out)
                st.markdown(f"""
                <div class="answer-meta">
                    <span>⏱ <strong>{elapsed:.2f}s</strong></span>
                    <span>🤖 <strong>{status_safe["model"]}</strong></span>
                    <span>❓ <strong>FAQ generado</strong></span>
                </div>
                </div>
                """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="bdo-footer">
    <strong>Sistema Q&A · Banco de Occidente</strong><br>
    Maestría en Inteligencia Artificial y Ciencia de Datos · Universidad Autónoma de Occidente<br>
    Técnicas Avanzadas de IA — Módulo 1 · 2026
</div>
""", unsafe_allow_html=True)
