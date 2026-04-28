"""
03_cleaner.py v2 — Limpieza inteligente del corpus bancario
Filosofía: conservar TODO el contenido informativo, eliminar SOLO artefactos de UI.

Problemas del cleaner anterior:
  - Eliminaba nombres de productos bancarios reales (tarjeta de crédito, seguro de vida...)
  - MIN_LINE_LENGTH=40 descartaba datos clave (tasas, plazos, montos)
  - Ratio de unicidad de palabras descartaba listas válidas de características
"""

import os
import re
import hashlib

INPUT_DIR  = "data/raw_docs"
OUTPUT_DIR = "data/clean_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# ARTEFACTOS DE UI — Lo que SÍ es ruido (no información bancaria)
# Solo patrones que NUNCA aportan contenido semántico útil
# ─────────────────────────────────────────────────────────────────
UI_NOISE = [
    # Navegación pura
    r"^inicio\s*[>›/]\s*",
    r"^home\s*[>›/]\s*",
    r"^menú principal$",
    r"^ir al contenido$",
    r"^saltar al contenido$",

    # Botones de acción sin contexto
    r"^(ver más|ver menos|leer más|leer menos)$",
    r"^(clic aquí|haz clic|click aquí)$",
    r"^(solicita(r)? (ahora|ya|hoy))$",
    r"^(descarga(r)? (la )?(app|aplicación))$",
    r"^(inicia(r)? sesión|cerrar sesión|login|logout)$",
    r"^(acepto|no acepto|aceptar|cancelar|confirmar|enviar)$",

    # Cookies y privacidad
    r"(política de cookies|usamos cookies|aceptar cookies)",
    r"(este sitio web utiliza cookies)",

    # Redes sociales
    r"^(síguenos|follow us|compartir|share)$",
    r"^(facebook|twitter|instagram|linkedin|youtube|tiktok)$",

    # Copyright y legal genérico (no específico del banco)
    r"^(todos los derechos reservados|all rights reserved)$",
    r"^©\s*\d{4}",

    # Breadcrumbs / rutas de navegación
    r"^[a-záéíóú\s]+\s*[>›/]\s*[a-záéíóú\s]+\s*[>›/]",

    # Paginación
    r"^(página|page)\s+\d+\s+(de|of)\s+\d+$",
    r"^(anterior|siguiente|next|previous)\s*$",

    # Mensajes de carga / UI
    r"^(cargando|loading|espere|please wait)\.{0,3}$",
]

# Compilamos una sola vez para eficiencia
_UI_REGEX = re.compile(
    "|".join(UI_NOISE),
    flags=re.IGNORECASE
)

# ─────────────────────────────────────────────────────────────────
# LÍNEAS DE ALTO VALOR — NUNCA eliminar aunque sean cortas
# Si una línea contiene estos patrones, se conserva siempre
# ─────────────────────────────────────────────────────────────────
HIGH_VALUE_PATTERNS = re.compile(
    r"""
    # Datos financieros concretos
    \$[\d.,]+ |                         # Montos en pesos
    \d+[\.,]\d+\s*%\s*(m\.?v\.?|e\.?a\.?|anual|mensual)? |  # Tasas
    (tasa|cuota|plazo|monto|mínimo|máximo|desde|hasta)\s+\w |
    \d+\s*(meses|años|días|cuotas) |    # Plazos

    # Información de contacto
    \d{3,4}[\s\-]\d{3,4}[\s\-]?\d{0,4} |  # Teléfonos
    (línea|lnea)\s+(de\s+)?(atención|gratuita) |
    \d{2}\s+\d{4}\s+\d{3,4} |          # Números de atención

    # Requisitos (siempre valiosos)
    (requisi|document|certific|soport|acredit) |
    (mayor de edad|cédula|pasaporte|rut\b|nit\b) |

    # Nombres de productos bancarios específicos
    (cuenta\s+(de\s+)?(ahorro|corriente|nómina) |
    cdt\b|certificado de depósito|
    tarjeta\s+(de\s+)?(crédito|débito|prepago)|
    crédito\s+(hipotecario|libre inversión|vehicular|de vehículo)|
    leasing|fiducia|cartera|portafolio) |

    # Canales
    (portal transaccional|banca (en\s+)?línea|app\s+móvil|cajero) |

    # Entidades regulatorias (contexto valioso)
    (superfinanciera|fogafín|grupo aval|banco de occidente)
    """,
    re.IGNORECASE | re.VERBOSE
)


# ─────────────────────────────────────────────────────────────────
# FUNCIONES DE LIMPIEZA
# ─────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Normalización básica sin perder contenido."""
    text = text.replace("\xa0", " ")   # non-breaking space
    text = text.replace("\t", " ")
    text = re.sub(r" {2,}", " ", text) # múltiples espacios → uno
    return text.strip()


def is_ui_artifact(line: str) -> bool:
    """True si la línea es puramente un artefacto de interfaz sin valor informativo."""
    stripped = line.strip()

    # Línea vacía
    if not stripped:
        return True

    # Línea de solo símbolos/números sin letras
    if re.fullmatch(r"[\W\d\s]+", stripped):
        return True

    # Línea en la lista de artefactos de UI
    if _UI_REGEX.search(stripped):
        return True

    return False


def is_high_value(line: str) -> bool:
    """True si la línea contiene datos financieros o bancarios concretos."""
    return bool(HIGH_VALUE_PATTERNS.search(line))


def should_keep(line: str) -> bool:
    """
    Lógica de decisión principal.
    Orden de prioridad:
      1. Si es artefacto de UI → descartar
      2. Si tiene alto valor informativo → conservar siempre
      3. Si tiene al menos 20 chars y no es UI → conservar
      4. Si tiene menos de 20 chars → descartar (muy corto para aportar)
    """
    if is_ui_artifact(line):
        return False
    if is_high_value(line):
        return True
    # Umbral bajo: 20 chars (antes era 40, demasiado agresivo)
    return len(line.strip()) >= 20


def line_hash(text: str) -> str:
    return hashlib.md5(text.lower().strip().encode()).hexdigest()


def clean_document(raw: str) -> str:
    """
    Limpia un documento preservando toda información bancaria relevante.
    Solo elimina duplicados exactos y artefactos de UI.
    """
    lines   = raw.split("\n")
    cleaned = []
    seen    = set()          # Para deduplicación exacta
    seen_fuzzy = {}          # Para deduplicación de líneas muy similares

    for line in lines:
        line = normalize(line)

        if not should_keep(line):
            continue

        # Deduplicación exacta (mismo texto)
        h = line_hash(line)
        if h in seen:
            continue
        seen.add(h)

        cleaned.append(line)

    return "\n".join(cleaned)


def get_stats(raw: str, cleaned: str) -> dict:
    """Calcula estadísticas de la limpieza para reporte."""
    raw_lines     = [l for l in raw.split("\n") if l.strip()]
    cleaned_lines = [l for l in cleaned.split("\n") if l.strip()]
    return {
        "raw_lines":     len(raw_lines),
        "clean_lines":   len(cleaned_lines),
        "retention_pct": round(len(cleaned_lines) / max(len(raw_lines), 1) * 100, 1),
        "raw_chars":     len(raw),
        "clean_chars":   len(cleaned),
    }


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def run():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
    print(f"📂 Procesando {len(files)} documentos...\n")

    saved   = 0
    skipped = 0
    total_retention = []

    for file in files:
        path = os.path.join(INPUT_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

        cleaned = clean_document(raw)
        stats   = get_stats(raw, cleaned)
        total_retention.append(stats["retention_pct"])

        # Solo descartamos documentos casi vacíos (menos de 150 chars)
        if len(cleaned.strip()) < 150:
            skipped += 1
            print(f"  ⚠️  SKIP  {file[:60]} — muy corto tras limpieza")
            continue

        out = os.path.join(OUTPUT_DIR, file)
        with open(out, "w", encoding="utf-8") as f:
            f.write(cleaned)

        saved += 1
        print(
            f"  ✅ {file[:55]:<55} "
            f"{stats['clean_lines']:>4} líneas  "
            f"({stats['retention_pct']:>5.1f}% retenido)"
        )

    avg_retention = sum(total_retention) / max(len(total_retention), 1)
    print(f"\n{'─'*60}")
    print(f"✅ Guardados:            {saved}")
    print(f"⚠️  Descartados (vacíos): {skipped}")
    print(f"📊 Retención promedio:   {avg_retention:.1f}% del texto original")
    print(f"{'─'*60}")
    print("\n💡 Si la retención promedio es < 30%, el scraping capturó")
    print("   principalmente navegación — considera revisar el corpus.")
    print("   Si es > 60%, el contenido semántico fue bien preservado.")


if __name__ == "__main__":
    run()
