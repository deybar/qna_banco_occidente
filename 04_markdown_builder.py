"""
04_markdown_builder.py v2 — Constructor de Markdown estructural
Filosofía:
  1. PRESERVAR la jerarquía de encabezados ya generada por el scraper (#, ##, ###)
  2. DETECTAR encabezados implícitos con heurísticas múltiples
  3. AGRUPAR listas de bullets contiguos en bloques coherentes
  4. EXTRAER URL como metadata para trazabilidad
  5. DEDUPLICAR contenido repetido (footers, disclaimers, banners legales)
"""

import os
import re
import hashlib
from collections import Counter

INPUT_DIR  = "data/clean_docs"
OUTPUT_DIR = "data/markdown_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# PALABRAS CLAVE QUE INDICAN QUE UNA LÍNEA ES UN ENCABEZADO
# ─────────────────────────────────────────────────────────────────
HEADING_KEYWORDS = re.compile(
    r"""
    ^(
        # Productos
        (tarjeta|tarjetas|cuenta|cuentas|crédito|créditos|préstamo|seguro|seguros|
         leasing|cdt|fiducia|inversión|inversiones|portafolio|cartera|cobertura) |

        # Secciones temáticas
        (productos|servicios|beneficios|características|requisitos|condiciones|
         documentación|documentos|tasas|plazos|cuotas|montos|límites|cupos) |

        # Estructura corporativa
        (quiénes\s+somos|nuestra\s+empresa|nuestra\s+historia|misión|visión|
         valores|propósito|sostenibilidad|gobierno\s+corporativo) |

        # Canales y contacto
        (canales|atención|contacto|sucursales|oficinas|línea|líneas|
         banca\s+(en\s+)?línea|portal|app)
    )\b
    """,
    re.IGNORECASE | re.VERBOSE
)

# ─────────────────────────────────────────────────────────────────
# DEDUPLICACIÓN GLOBAL — frases que aparecen en >50% de documentos
# Se llenará en una primera pasada
# ─────────────────────────────────────────────────────────────────
_global_line_freq = Counter()
_TOTAL_DOCS_SEEN  = [0]   # contador en lista para mutabilidad


# ─────────────────────────────────────────────────────────────────
# EXTRACCIÓN DE METADATA
# ─────────────────────────────────────────────────────────────────

def extract_url(raw: str) -> str:
    """Extrae la URL del header del documento si existe."""
    match = re.search(r"^URL:\s*(\S+)", raw, re.MULTILINE)
    return match.group(1) if match else ""


def remove_url_header(raw: str) -> str:
    """Elimina la línea 'URL: ...' del cuerpo del texto."""
    return re.sub(r"^URL:\s*\S+\s*\n?", "", raw, count=1, flags=re.MULTILINE).strip()


# ─────────────────────────────────────────────────────────────────
# DETECCIÓN DE ENCABEZADOS IMPLÍCITOS
# ─────────────────────────────────────────────────────────────────

def is_explicit_heading(line: str) -> tuple[bool, int, str]:
    """Detecta encabezados markdown ya presentes (#, ##, ###).
       Retorna (es_heading, nivel, texto_sin_hashes)."""
    m = re.match(r"^(#{1,4})\s+(.+?)\s*#*\s*$", line.strip())
    if m:
        return True, len(m.group(1)), m.group(2).strip()
    return False, 0, ""


def looks_like_heading(line: str) -> bool:
    """
    Heurística para detectar encabezados implícitos.
    Una línea es probablemente un encabezado si cumple varias condiciones:
      - Es corta (<80 chars)
      - No termina en punto
      - Contiene palabras clave temáticas
      - Está en Title Case o MAYÚSCULAS
    """
    s = line.strip()

    if len(s) < 5 or len(s) > 80:
        return False

    if s.endswith(".") or s.endswith(","):
        return False

    # Termina en ":" → casi seguro es un encabezado
    if s.endswith(":"):
        return True

    # Contiene palabras clave temáticas + es corta
    if HEADING_KEYWORDS.search(s) and len(s.split()) <= 8:
        return True

    # Title Case (cada palabra empieza con mayúscula) y corta
    words = s.split()
    if len(words) <= 6 and len(words) >= 2:
        capitalized = sum(1 for w in words if w[0].isupper())
        if capitalized / len(words) >= 0.7:
            return True

    # Todo mayúsculas (probable encabezado)
    if s.isupper() and len(s) <= 60:
        return True

    return False


def is_bullet(line: str) -> bool:
    """True si la línea parece un item de lista."""
    s = line.strip()
    return bool(re.match(r"^[-•·*]\s+", s) or re.match(r"^\d+[.)]\s+", s))


def normalize_bullet(line: str) -> str:
    """Estandariza el formato de bullets a `- texto`."""
    s = line.strip()
    s = re.sub(r"^[•·*]\s+", "- ", s)
    s = re.sub(r"^\d+[.)]\s+", "- ", s)
    return s


# ─────────────────────────────────────────────────────────────────
# DEDUPLICACIÓN INTELIGENTE
# ─────────────────────────────────────────────────────────────────

def line_hash(text: str) -> str:
    return hashlib.md5(text.lower().strip().encode()).hexdigest()


def collect_global_frequencies(input_dir: str):
    """
    Primera pasada: cuenta cuántas veces aparece cada línea
    en TODOS los documentos. Las que aparezcan en >50% son boilerplate.
    """
    files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    _TOTAL_DOCS_SEEN[0] = len(files)

    for fname in files:
        seen_in_this_doc = set()
        with open(os.path.join(input_dir, fname), "r", encoding="utf-8") as f:
            for line in f.read().split("\n"):
                line = line.strip()
                if len(line) < 30:
                    continue
                h = line_hash(line)
                if h in seen_in_this_doc:
                    continue
                seen_in_this_doc.add(h)
                _global_line_freq[h] += 1


def is_global_boilerplate(line: str) -> bool:
    """True si la línea aparece en >50% de los documentos del corpus."""
    if _TOTAL_DOCS_SEEN[0] == 0:
        return False
    h = line_hash(line)
    threshold = max(3, int(_TOTAL_DOCS_SEEN[0] * 0.5))
    return _global_line_freq.get(h, 0) >= threshold


# ─────────────────────────────────────────────────────────────────
# CONSTRUCCIÓN DEL MARKDOWN
# ─────────────────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def infer_main_title(lines: list, fallback: str) -> str:
    """
    Encuentra el mejor título principal del documento.
    Prioriza encabezados H1 explícitos; si no hay, busca la primera línea
    significativa que no sea metadata.
    """
    # Buscar primer H1 explícito
    for line in lines:
        is_h, level, text = is_explicit_heading(line)
        if is_h and level == 1 and text:
            return text

    # Buscar primer H2
    for line in lines:
        is_h, level, text = is_explicit_heading(line)
        if is_h and level == 2 and text:
            return text

    # Fallback: primera línea sustantiva que parece título
    for line in lines:
        s = line.strip()
        if 15 <= len(s) <= 100 and not s.startswith("-") and not s.endswith("."):
            return s

    return fallback.replace("_", " ").replace(".txt", "").strip()


def build_markdown(raw: str, source_name: str) -> str:
    """
    Construye un markdown estructurado preservando jerarquía
    y agrupando contenido de forma semántica.
    """
    url     = extract_url(raw)
    body    = remove_url_header(raw)
    body    = normalize_text(body)
    lines   = [l for l in body.split("\n") if l.strip()]

    title   = infer_main_title(lines, source_name)

    # ── HEADER ─────────────────────────────
    md = []
    md.append(f"# {title}")
    md.append("")
    if url:
        md.append(f"**Fuente:** {url}")
    else:
        md.append(f"**Fuente:** {source_name}")
    md.append("")
    md.append("---")
    md.append("")

    # ── PROCESAMIENTO LÍNEA POR LÍNEA ──────
    seen_in_doc = set()
    in_bullet_list = False
    title_seen = False    # para evitar duplicar el título principal
    last_was_heading = False

    for line in lines:
        s = line.strip()

        # Saltar boilerplate global (footers que se repiten en todo el sitio)
        if is_global_boilerplate(s):
            continue

        # Deduplicación dentro del documento
        h = line_hash(s)
        if h in seen_in_doc:
            continue

        # ── CASO 1: Es un encabezado explícito (#, ##, ###) ──
        is_h, level, text = is_explicit_heading(s)
        if is_h:
            # Saltamos H1 si ya pusimos el título principal
            if level == 1 and not title_seen:
                title_seen = True
                seen_in_doc.add(h)
                continue
            if level == 1:
                level = 2  # degradamos H1 secundarios a H2

            if in_bullet_list:
                md.append("")
                in_bullet_list = False

            md.append("")
            md.append(f"{'#' * level} {text}")
            md.append("")
            seen_in_doc.add(h)
            last_was_heading = True
            continue

        # ── CASO 2: Es un bullet de lista ──
        if is_bullet(s):
            md.append(normalize_bullet(s))
            in_bullet_list = True
            seen_in_doc.add(h)
            last_was_heading = False
            continue

        # ── CASO 3: Encabezado implícito detectado ──
        if looks_like_heading(s) and not last_was_heading:
            if in_bullet_list:
                md.append("")
                in_bullet_list = False

            # Quitar ":" final si lo tiene
            heading_text = s.rstrip(":").strip()
            md.append("")
            md.append(f"## {heading_text}")
            md.append("")
            seen_in_doc.add(h)
            last_was_heading = True
            continue

        # ── CASO 4: Párrafo normal ──
        if in_bullet_list:
            md.append("")
            in_bullet_list = False

        # Filtrar líneas demasiado cortas SOLO si no son cifras importantes
        if len(s) < 25 and not re.search(r"\$|\d+\s*%|\d+\s*meses|\d+\s*años", s):
            continue

        md.append(s)
        md.append("")
        seen_in_doc.add(h)
        last_was_heading = False

    return "\n".join(md).strip() + "\n"


# ─────────────────────────────────────────────────────────────────
# QA & ESTADÍSTICAS
# ─────────────────────────────────────────────────────────────────

def quality_score(md: str) -> dict:
    """Calcula métricas de calidad estructural del markdown."""
    h1_count     = len(re.findall(r"^# [^#]", md, re.MULTILINE))
    h2_count     = len(re.findall(r"^## [^#]", md, re.MULTILINE))
    h3_count     = len(re.findall(r"^### [^#]", md, re.MULTILINE))
    bullets      = len(re.findall(r"^- ", md, re.MULTILINE))
    paragraphs   = len([
        ln for ln in md.split("\n")
        if ln.strip() and not ln.startswith("#")
        and not ln.startswith("-")
        and not ln.startswith("**")
    ])
    chars = len(md)

    return {
        "h1": h1_count,
        "h2": h2_count,
        "h3": h3_count,
        "bullets":    bullets,
        "paragraphs": paragraphs,
        "chars":      chars,
        "structure_ratio": round(
            (h1_count + h2_count + h3_count) / max(paragraphs, 1) * 100, 1
        ),
    }


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def run():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]

    print(f"📂 Construyendo markdown estructurado de {len(files)} documentos...\n")

    # PASADA 1 — Detección de boilerplate global
    print("🔍 Pasada 1/2: Detectando contenido repetido entre documentos...")
    collect_global_frequencies(INPUT_DIR)
    boilerplate_count = sum(
        1 for v in _global_line_freq.values()
        if v >= max(3, int(_TOTAL_DOCS_SEEN[0] * 0.5))
    )
    print(f"   ⚠️  {boilerplate_count} líneas identificadas como boilerplate global\n")

    # PASADA 2 — Construcción del markdown
    print("📝 Pasada 2/2: Construyendo markdown por documento...")
    count = 0
    total_h, total_b, total_p = 0, 0, 0

    for fname in files:
        path = os.path.join(INPUT_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

        md_content = build_markdown(raw, fname)
        stats      = quality_score(md_content)

        out_path = os.path.join(OUTPUT_DIR, fname.replace(".txt", ".md"))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        total_h += stats["h2"] + stats["h3"]
        total_b += stats["bullets"]
        total_p += stats["paragraphs"]
        count   += 1

        print(
            f"  ✅ {fname[:50]:<50} "
            f"H:{stats['h2']+stats['h3']:>2}  "
            f"L:{stats['bullets']:>3}  "
            f"P:{stats['paragraphs']:>3}  "
            f"({stats['chars']:>5} chars)"
        )

    print(f"\n{'─'*70}")
    print(f"✅ Markdown corporativo generado: {count} documentos")
    print(f"📊 Total encabezados (H2+H3): {total_h}")
    print(f"📊 Total items de lista:      {total_b}")
    print(f"📊 Total párrafos:            {total_p}")
    print(f"{'─'*70}")
    print("\nLeyenda:  H = headings   L = bullets   P = párrafos")


if __name__ == "__main__":
    run()
