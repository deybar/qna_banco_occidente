"""
05_corpus_master.py v2 — Constructor del Corpus Maestro Estructurado
Filosofía:
  1. CATEGORIZAR documentos por tema (tarjetas, créditos, empresas, etc.)
  2. ORDENAR siguiendo una jerarquía lógica de banco (institucional → productos → canales)
  3. GENERAR Tabla de Contenidos (TOC) navegable al inicio
  4. DETECTAR documentos casi-duplicados entre páginas similares
  5. FILTRAR documentos de baja calidad (vacíos, solo metadata)
  6. REPORTAR estadísticas detalladas del corpus final
"""

import os
import re
import hashlib
from collections import defaultdict, Counter

INPUT_DIR   = "data/markdown_docs"
OUTPUT_FILE = "data/corpus_master.md"

# Filtros de calidad
MIN_DOC_CHARS    = 300        # menor a esto se descarta
MIN_DOC_HEADINGS = 1          # debe tener al menos 1 H2/H3
SIMILARITY_THRESHOLD = 0.85   # >85% similar → duplicado

# ─────────────────────────────────────────────────────────────────
# CATEGORIZACIÓN TEMÁTICA
# ─────────────────────────────────────────────────────────────────
# Ordenadas según jerarquía corporativa: institucional → productos → soporte
CATEGORIES = [
    {
        "id":    "01_institucional",
        "title": "Información Institucional",
        "url_patterns": [
            r"nosotros", r"quienes", r"acerca", r"empresa", r"historia",
            r"mision", r"vision", r"sostenibilidad", r"gobierno"
        ],
        "content_keywords": [
            "propósito", "misión", "visión", "historia", "sostenibilidad",
            "valores corporativos", "gobierno corporativo", "grupo aval"
        ],
    },
    {
        "id":    "02_cuentas_ahorro",
        "title": "Cuentas y Productos de Ahorro",
        "url_patterns": [
            r"cuenta", r"ahorro", r"corriente", r"nomina", r"infantil"
        ],
        "content_keywords": [
            "cuenta de ahorros", "cuenta corriente", "cuenta nómina",
            "cuenta infantil", "depósito"
        ],
    },
    {
        "id":    "03_tarjetas",
        "title": "Tarjetas de Crédito y Débito",
        "url_patterns": [
            r"tarjeta", r"credit-card", r"debito", r"visa", r"mastercard"
        ],
        "content_keywords": [
            "tarjeta de crédito", "tarjeta débito", "visa", "mastercard",
            "cupo", "avances", "puntos", "millas"
        ],
    },
    {
        "id":    "04_creditos_personales",
        "title": "Créditos para Personas",
        "url_patterns": [
            r"credito", r"prestamo", r"libre.?inversion", r"vehiculo",
            r"hipotecario", r"vivienda", r"moto", r"educativo"
        ],
        "content_keywords": [
            "crédito de libre inversión", "crédito hipotecario",
            "crédito de vehículo", "crédito de vivienda", "préstamo personal",
            "cuota fija", "cuota mensual"
        ],
    },
    {
        "id":    "05_inversion",
        "title": "Productos de Inversión",
        "url_patterns": [
            r"cdt", r"inversion", r"fondo", r"fiducia", r"valor"
        ],
        "content_keywords": [
            "cdt", "certificado de depósito", "fondos de inversión",
            "fiducia", "rentabilidad", "plazo fijo"
        ],
    },
    {
        "id":    "06_empresarial",
        "title": "Banca Empresarial y Corporativa",
        "url_patterns": [
            r"empresa", r"corporativ", r"pyme", r"comercial", r"leasing",
            r"comercio.?exterior", r"capital.?trabajo"
        ],
        "content_keywords": [
            "banca empresarial", "leasing", "cartera ordinaria",
            "comercio exterior", "carta de crédito", "factoring",
            "capital de trabajo", "banca de inversión"
        ],
    },
    {
        "id":    "07_seguros",
        "title": "Seguros y Protección",
        "url_patterns": [
            r"seguro", r"proteccion", r"asistencia"
        ],
        "content_keywords": [
            "seguro de vida", "seguro de desempleo", "cuota protegida",
            "póliza", "cobertura", "asistencia"
        ],
    },
    {
        "id":    "08_canales_digitales",
        "title": "Canales Digitales y Servicios en Línea",
        "url_patterns": [
            r"portal", r"app", r"digital", r"online", r"banca.?linea",
            r"banca.?virtual", r"transaccional"
        ],
        "content_keywords": [
            "portal transaccional", "banca en línea", "aplicación móvil",
            "app móvil", "banca digital", "biometría"
        ],
    },
    {
        "id":    "09_atencion",
        "title": "Atención al Cliente y Sucursales",
        "url_patterns": [
            r"atencion", r"contacto", r"sucursal", r"oficina", r"ayuda",
            r"pqr", r"linea"
        ],
        "content_keywords": [
            "línea de atención", "sucursales", "horario de atención",
            "puntos de atención", "PQR", "petición"
        ],
    },
    {
        "id":    "10_legal",
        "title": "Información Legal y Regulatoria",
        "url_patterns": [
            r"transparencia", r"politica", r"terminos", r"privacidad",
            r"defensor", r"regulacion"
        ],
        "content_keywords": [
            "superintendencia financiera", "fogafin", "política de privacidad",
            "términos y condiciones", "defensor del consumidor",
            "habeas data"
        ],
    },
    {
        "id":    "99_otros",
        "title": "Información Complementaria",
        "url_patterns": [],   # catch-all
        "content_keywords": [],
    },
]


# ─────────────────────────────────────────────────────────────────
# CLASIFICACIÓN POR DOCUMENTO
# ─────────────────────────────────────────────────────────────────

def categorize(filename: str, content: str) -> str:
    """
    Asigna un documento a la categoría que mejor lo describe.
    Estrategia: scoring combinado URL + contenido.
    """
    fname_lower   = filename.lower()
    content_lower = content.lower()
    scores        = {}

    for cat in CATEGORIES:
        if cat["id"] == "99_otros":
            continue

        score = 0

        # Coincidencias en nombre de archivo (URL)
        for pattern in cat["url_patterns"]:
            if re.search(pattern, fname_lower):
                score += 10        # peso alto: la URL es la señal más fuerte

        # Coincidencias en contenido (primeros 2000 chars son los más relevantes)
        head = content_lower[:2000]
        for keyword in cat["content_keywords"]:
            count = head.count(keyword.lower())
            score += count * 3

        scores[cat["id"]] = score

    # Si ninguna categoría alcanza umbral mínimo → "otros"
    best_cat = max(scores, key=scores.get) if scores else "99_otros"
    if scores.get(best_cat, 0) < 5:
        return "99_otros"
    return best_cat


# ─────────────────────────────────────────────────────────────────
# FILTROS DE CALIDAD
# ─────────────────────────────────────────────────────────────────

def is_quality_doc(content: str) -> tuple[bool, str]:
    """Retorna (es_calidad, razón_si_no)."""
    body = re.sub(r"^---.*?---", "", content, flags=re.DOTALL).strip()

    if len(body) < MIN_DOC_CHARS:
        return False, f"muy corto ({len(body)} chars)"

    headings = len(re.findall(r"^##+ ", body, re.MULTILINE))
    if headings < MIN_DOC_HEADINGS:
        # Aún válido si tiene mucho texto sustantivo
        if len(body) < 800:
            return False, f"sin estructura ({headings} headings, {len(body)} chars)"

    # Detectar documentos que son casi solo metadata
    if body.count("**Fuente:**") > 0 and len(body) < 500:
        return False, "casi solo metadata"

    return True, ""


# ─────────────────────────────────────────────────────────────────
# DETECCIÓN DE DUPLICADOS POR SHINGLING
# ─────────────────────────────────────────────────────────────────

def make_shingles(text: str, k: int = 5) -> set:
    """Genera shingles (k-gramas de palabras) para comparación de similitud."""
    text  = re.sub(r"\s+", " ", text.lower())
    words = re.findall(r"\b\w+\b", text)
    if len(words) < k:
        return set()
    return {tuple(words[i:i+k]) for i in range(len(words) - k + 1)}


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Similitud de Jaccard entre dos conjuntos de shingles."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union        = len(set_a | set_b)
    return intersection / union if union else 0.0


# ─────────────────────────────────────────────────────────────────
# GENERACIÓN DE TOC
# ─────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convierte un texto a anchor válido en markdown."""
    s = text.lower()
    s = re.sub(r"[áä]", "a", s)
    s = re.sub(r"[éë]", "e", s)
    s = re.sub(r"[íï]", "i", s)
    s = re.sub(r"[óö]", "o", s)
    s = re.sub(r"[úü]", "u", s)
    s = re.sub(r"ñ", "n", s)
    s = re.sub(r"[^a-z0-9\s\-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s


def build_toc(grouped_docs: dict) -> str:
    """Construye una tabla de contenidos navegable."""
    lines = [
        "## 📑 Tabla de Contenidos",
        "",
        "Este corpus está organizado por áreas temáticas del Banco de Occidente:",
        "",
    ]

    for cat in CATEGORIES:
        docs = grouped_docs.get(cat["id"], [])
        if not docs:
            continue

        anchor = slugify(cat["title"])
        lines.append(f"- **[{cat['title']}](#{anchor})** — {len(docs)} documento(s)")

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
# CONSTRUCCIÓN DEL CORPUS
# ─────────────────────────────────────────────────────────────────

def build_corpus():
    files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".md")])
    print(f"📂 Procesando {len(files)} markdowns para corpus maestro...\n")

    # ── FASE 1: Carga, filtrado de calidad y categorización ──
    print("🔍 Fase 1/3: Filtrado de calidad y categorización...")
    docs_by_cat   = defaultdict(list)
    rejected      = []
    all_shingles  = []      # para detección de duplicados

    for fname in files:
        path = os.path.join(INPUT_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Filtro de calidad
        ok, reason = is_quality_doc(content)
        if not ok:
            rejected.append((fname, reason))
            continue

        # Filtro de duplicado contra docs ya aceptados
        shingles = make_shingles(content, k=5)
        is_duplicate = False
        for prev_fname, prev_shingles in all_shingles:
            if jaccard_similarity(shingles, prev_shingles) >= SIMILARITY_THRESHOLD:
                rejected.append((fname, f"duplicado de {prev_fname[:40]}"))
                is_duplicate = True
                break
        if is_duplicate:
            continue

        # Categorización
        category = categorize(fname, content)
        docs_by_cat[category].append({
            "filename": fname,
            "content":  content,
            "chars":    len(content),
        })
        all_shingles.append((fname, shingles))

    accepted_count = sum(len(d) for d in docs_by_cat.values())
    print(f"   ✅ Aceptados:   {accepted_count}")
    print(f"   ❌ Rechazados: {len(rejected)}")
    if rejected:
        for fname, reason in rejected[:5]:
            print(f"      · {fname[:50]} → {reason}")
        if len(rejected) > 5:
            print(f"      · ... y {len(rejected) - 5} más")

    # ── FASE 2: Construcción del corpus ordenado ──
    print("\n📝 Fase 2/3: Construyendo corpus jerárquico...")
    output = []

    # Header del corpus
    output.append("# CORPUS DOCUMENTAL MAESTRO — BANCO DE OCCIDENTE")
    output.append("")
    output.append("> Base de conocimiento estructurada para el sistema Q&A corporativo.  ")
    output.append("> Origen: Web scraping de www.bancodeoccidente.com.co  ")
    output.append(f"> Documentos integrados: **{accepted_count}**  ")
    output.append("")
    output.append("---")
    output.append("")

    # Tabla de contenidos
    output.append(build_toc(docs_by_cat))

    # Cuerpo organizado por categoría
    for cat in CATEGORIES:
        docs = docs_by_cat.get(cat["id"], [])
        if not docs:
            continue

        # Ordenar docs dentro de cada categoría por tamaño descendente
        # (los más completos primero, mejora retrieval)
        docs.sort(key=lambda d: d["chars"], reverse=True)

        # Encabezado de sección
        output.append("")
        output.append("=" * 100)
        output.append(f"# {cat['title']}")
        output.append("=" * 100)
        output.append("")
        output.append(f"*Esta sección contiene {len(docs)} documento(s) sobre "
                      f"{cat['title'].lower()}.*")
        output.append("")

        # Documentos de la categoría
        for i, doc in enumerate(docs, start=1):
            output.append("")
            output.append("-" * 80)
            output.append(f"### Documento {i} de {len(docs)} · {cat['title']}")
            output.append("-" * 80)
            output.append("")
            output.append(doc["content"].strip())
            output.append("")

    # ── FASE 3: Estadísticas finales ──
    print("📊 Fase 3/3: Calculando estadísticas...")
    final_text = "\n".join(output)
    stats = compute_stats(final_text, docs_by_cat)

    # Anexar resumen de stats al final del corpus
    output.append("")
    output.append("=" * 100)
    output.append("# Metadata del Corpus")
    output.append("=" * 100)
    output.append("")
    output.append(f"- **Total de caracteres:** {stats['chars']:,}")
    output.append(f"- **Total de palabras:**   {stats['words']:,}")
    output.append(f"- **Total de secciones (H2):** {stats['h2']:,}")
    output.append(f"- **Total de subsecciones (H3):** {stats['h3']:,}")
    output.append(f"- **Total de items de lista:** {stats['bullets']:,}")
    output.append("")
    output.append("**Distribución por categoría:**")
    for cat in CATEGORIES:
        count = len(docs_by_cat.get(cat["id"], []))
        if count > 0:
            output.append(f"- {cat['title']}: {count} documento(s)")
    output.append("")

    final_text = "\n".join(output)

    # Guardado
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_text)

    return stats, docs_by_cat, accepted_count, len(rejected)


def compute_stats(text: str, docs_by_cat: dict) -> dict:
    """Calcula métricas del corpus final."""
    return {
        "chars":    len(text),
        "words":    len(text.split()),
        "h2":       len(re.findall(r"^## [^#]", text, re.MULTILINE)),
        "h3":       len(re.findall(r"^### [^#]", text, re.MULTILINE)),
        "bullets":  len(re.findall(r"^- ", text, re.MULTILINE)),
        "categories_used": sum(1 for v in docs_by_cat.values() if v),
    }


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def run():
    print("🚀 Iniciando construcción del Corpus Maestro v2...\n")
    stats, grouped, accepted, rejected = build_corpus()

    print(f"\n{'='*70}")
    print("✅ CORPUS MAESTRO GENERADO")
    print(f"{'='*70}")
    print(f"📁 Archivo:        {OUTPUT_FILE}")
    print(f"📄 Documentos:     {accepted} integrados, {rejected} descartados")
    print(f"📊 Caracteres:     {stats['chars']:,}")
    print(f"📊 Palabras:       {stats['words']:,}")
    print(f"📊 Secciones H2:   {stats['h2']:,}")
    print(f"📊 Subsecciones H3:{stats['h3']:,}")
    print(f"📊 Items de lista: {stats['bullets']:,}")
    print(f"📊 Categorías:     {stats['categories_used']}/{len(CATEGORIES)} con contenido")
    print(f"{'='*70}\n")

    # Distribución por categoría
    print("📈 Distribución temática del corpus:")
    print()
    for cat in CATEGORIES:
        docs = grouped.get(cat["id"], [])
        if not docs:
            continue
        total_chars = sum(d["chars"] for d in docs)
        bar = "█" * min(40, total_chars // 500)
        print(f"  {cat['title'][:35]:<35} "
              f"{len(docs):>3} docs  "
              f"{total_chars:>6} chars  "
              f"{bar}")
    print()

    # Recomendaciones
    avg_chars = stats['chars'] / max(accepted, 1)
    print("💡 Indicadores de calidad:")
    if stats['chars'] < 20_000:
        print("   ⚠️  Corpus pequeño (<20K chars) — el LLM tendrá poco contexto.")
        print("       Considera aumentar MAX_URLS en 01_crawling.py")
    elif stats['chars'] > 200_000:
        print("   ⚠️  Corpus muy grande (>200K chars) — puede saturar el system prompt.")
        print("       Revisa si hay categorías sobrerepresentadas.")
    else:
        print(f"   ✅ Tamaño del corpus adecuado ({stats['chars']:,} chars).")

    if stats['h2'] < 10:
        print("   ⚠️  Pocas secciones (<10 H2) — corpus poco estructurado.")
    else:
        print(f"   ✅ Buena estructura: {stats['h2']} secciones H2 detectadas.")

    if stats['categories_used'] < 4:
        print("   ⚠️  Pocas categorías cubiertas — el banco tiene más áreas que las extraídas.")
    else:
        print(f"   ✅ Cobertura temática amplia: {stats['categories_used']} áreas del banco.")


if __name__ == "__main__":
    run()
