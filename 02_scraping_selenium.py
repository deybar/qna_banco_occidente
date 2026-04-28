"""
02_scraping_selenium.py v2 — Scraping HTML + PDFs
═══════════════════════════════════════════════════════════════════════════════
Mejoras vs v1:
  1. SCRAPING HTML con Selenium (igual que antes)
  2. DESCARGA Y EXTRACCIÓN DE TEXTO DE PDFs con pypdf
  3. INTEGRACIÓN DE REDES SOCIALES como documento informativo

REQUISITOS PREVIOS:
    pip install selenium webdriver-manager pypdf

ARCHIVOS DE ENTRADA:
    data/urls.txt          → URLs HTML para scraping
    data/pdf_urls.txt      → URLs de PDFs para descarga
    data/social_links.txt  → Enlaces de redes sociales

ARCHIVOS DE SALIDA:
    data/raw_docs/         → .txt con contenido extraído (HTML + PDFs)
    data/pdf_docs/         → .pdf descargados (respaldo)
"""

import os
import time
import re
import requests
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════
INPUT_HTML    = "data/urls.txt"
INPUT_PDFS    = "data/pdf_urls.txt"
INPUT_SOCIAL  = "data/social_links.txt"

OUTPUT_DIR    = "data/raw_docs"
PDF_DIR       = "data/pdf_docs"

DELAY_HTML    = 2.0
DELAY_PDF     = 0.8

HEADERS_PDF = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════
# UTILIDADES
# ════════════════════════════════════════════════════════════════

def safe_filename(url: str, prefix: str = "") -> str:
    """Convierte una URL en un nombre de archivo válido."""
    name = re.sub(r'[^a-zA-Z0-9]', '_', url)[:140]
    return f"{prefix}{name}"


# ════════════════════════════════════════════════════════════════
# PARTE 1: SCRAPING HTML CON SELENIUM
# ════════════════════════════════════════════════════════════════

def build_driver():
    """Crea un driver de Chrome en modo headless."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def extract_html_content(driver) -> str:
    """Extrae texto estructurado de la página actual del driver."""
    content = []
    title = driver.title
    if title:
        content.append(f"# {title.strip()}\n")

    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
    except Exception:
        pass

    noise_selectors = [
        "nav", "footer", "header", "aside",
        "[class*='cookie']", "[class*='popup']",
        "[class*='modal']", "[class*='banner']",
    ]
    for selector in noise_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                driver.execute_script("arguments[0].remove()", el)
        except Exception:
            pass

    tags = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, p, li, td")
    for tag in tags:
        try:
            text = tag.text.strip()
            name = tag.tag_name

            if not text or len(text) < 25:
                continue
            if len(text.split()) < 4 and name in ["li", "p"]:
                continue

            if name == "h1":
                content.append(f"\n# {text}\n")
            elif name == "h2":
                content.append(f"\n## {text}\n")
            elif name == "h3":
                content.append(f"\n### {text}\n")
            elif name == "h4":
                content.append(f"\n#### {text}\n")
            elif name == "li":
                content.append(f"- {text}")
            elif name == "td":
                content.append(f"| {text}")
            else:
                content.append(text)
        except Exception:
            continue

    return "\n".join(content)


def save_doc(url: str, text: str, prefix: str = ""):
    """Guarda un documento extraído."""
    filename = safe_filename(url, prefix) + ".txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n\n")
        f.write(text)


def scrape_html_pages():
    """Scraping de todas las páginas HTML del banco."""
    if not os.path.exists(INPUT_HTML):
        print(f"⚠️ No existe {INPUT_HTML}. Ejecuta primero 01_crawling.py")
        return 0

    with open(INPUT_HTML, "r", encoding="utf-8") as f:
        urls = [ln.strip() for ln in f if ln.strip()]

    if not urls:
        print("⚠️ No hay URLs HTML para procesar")
        return 0

    print(f"\n📄 SCRAPING HTML — {len(urls)} URLs a procesar\n")
    driver  = build_driver()
    success = 0

    try:
        for i, url in enumerate(urls):
            print(f"   [{i+1:>3}/{len(urls)}] {url[:75]}")
            try:
                driver.get(url)
                time.sleep(DELAY_HTML)

                text = extract_html_content(driver)
                if len(text) < 200:
                    print(f"            ⚠️  Contenido muy corto ({len(text)} chars), ignorado")
                    continue

                save_doc(url, text)
                success += 1
                print(f"            ✅ Guardado ({len(text):,} chars)")

            except Exception as e:
                print(f"            ❌ Error: {str(e)[:80]}")
    finally:
        driver.quit()

    return success


# ════════════════════════════════════════════════════════════════
# PARTE 2: DESCARGA Y EXTRACCIÓN DE PDFs
# ════════════════════════════════════════════════════════════════

def extract_pdf_text(pdf_bytes: bytes, url: str) -> str:
    """Extrae texto de un PDF en memoria usando pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("            ⚠️  pypdf no instalado. Ejecuta: pip install pypdf")
        return ""

    try:
        reader   = PdfReader(BytesIO(pdf_bytes))
        num_pgs  = len(reader.pages)

        filename = url.split("/")[-1].replace(".pdf", "").replace("%20", " ")
        filename = re.sub(r"[_-]+", " ", filename).strip()

        content = [f"# {filename}\n"]
        content.append(f"**Documento PDF · {num_pgs} páginas**\n")

        for i, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text() or ""
                text = text.strip()
                if not text:
                    continue
                if num_pgs > 1:
                    content.append(f"\n## Página {i}\n")
                content.append(text)
            except Exception as e:
                print(f"            ⚠️  Error en página {i}: {str(e)[:50]}")
                continue

        return "\n".join(content)
    except Exception as e:
        print(f"            ❌ No se pudo extraer texto: {str(e)[:80]}")
        return ""


def scrape_pdf_documents():
    """Descarga y extrae texto de PDFs."""
    if not os.path.exists(INPUT_PDFS):
        print(f"⚠️ No existe {INPUT_PDFS}, saltando PDFs")
        return 0

    with open(INPUT_PDFS, "r", encoding="utf-8") as f:
        urls = [ln.strip() for ln in f if ln.strip()]

    if not urls:
        print("ℹ️ No hay PDFs para procesar")
        return 0

    print(f"\n📑 PROCESAMIENTO PDFs — {len(urls)} PDFs a descargar\n")
    success = 0

    for i, url in enumerate(urls):
        print(f"   [{i+1:>3}/{len(urls)}] {url[:75]}")
        try:
            res = requests.get(url, headers=HEADERS_PDF, timeout=30, stream=True)
            if res.status_code != 200:
                print(f"            ⚠️  Status {res.status_code}, ignorado")
                continue

            pdf_bytes = res.content
            size_kb   = len(pdf_bytes) / 1024
            print(f"            📥 Descargado {size_kb:.0f} KB")

            pdf_name = safe_filename(url, prefix="pdf_") + ".pdf"
            pdf_path = os.path.join(PDF_DIR, pdf_name)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)

            text = extract_pdf_text(pdf_bytes, url)
            if len(text) < 100:
                print(f"            ⚠️  Texto extraído muy corto, ignorado")
                continue

            save_doc(url, text, prefix="pdf_")
            success += 1
            print(f"            ✅ Texto extraído ({len(text):,} chars)")

            time.sleep(DELAY_PDF)

        except Exception as e:
            print(f"            ❌ Error: {str(e)[:80]}")

    return success


# ════════════════════════════════════════════════════════════════
# PARTE 3: REDES SOCIALES COMO DOCUMENTO INFORMATIVO
# ════════════════════════════════════════════════════════════════

def integrate_social_media():
    """
    Genera un documento de texto con información sobre las redes sociales
    del banco para que sea parte del corpus.
    """
    if not os.path.exists(INPUT_SOCIAL):
        print("\nℹ️ No hay archivo de redes sociales, saltando")
        return False

    with open(INPUT_SOCIAL, "r", encoding="utf-8") as f:
        social_content = f.read()

    if "(No se detectaron" in social_content:
        print("\nℹ️ No se detectaron redes sociales en crawling")
        return False

    doc_path = os.path.join(OUTPUT_DIR, "redes_sociales_banco_de_occidente.txt")

    structured = []
    structured.append("URL: https://www.bancodeoccidente.com.co/redes-sociales\n")
    structured.append("# Redes Sociales y Canales Digitales del Banco de Occidente\n")
    structured.append(
        "El Banco de Occidente cuenta con presencia activa en las principales "
        "redes sociales y plataformas digitales, donde los clientes pueden "
        "interactuar, recibir atención y mantenerse informados sobre productos, "
        "promociones y novedades de la entidad.\n"
    )
    structured.append("\n## Plataformas oficiales del Banco de Occidente\n")

    current_network = None
    for line in social_content.split("\n"):
        line = line.strip()
        if line.startswith("## "):
            current_network = line[3:].strip()
            structured.append(f"\n### {current_network}")
            structured.append(
                f"El Banco de Occidente tiene presencia oficial en {current_network}, "
                f"donde los clientes pueden seguir las novedades del banco."
            )
        elif line.startswith("- "):
            url = line[2:].strip()
            if url and current_network:
                structured.append(f"- Enlace oficial en {current_network}: {url}")

    structured.append(
        "\n## Atención al cliente por canales digitales\n"
        "A través de estas redes sociales, el Banco de Occidente ofrece:\n"
        "- Atención al cliente en horario extendido\n"
        "- Información sobre nuevos productos y servicios\n"
        "- Promociones exclusivas para seguidores\n"
        "- Tips de educación financiera\n"
        "- Comunicación de eventos y novedades corporativas\n"
    )

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write("\n".join(structured))

    print(f"\n✅ Redes sociales integradas como documento: {doc_path}")
    return True


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 SCRAPING COMPLETO — Banco de Occidente v2")
    print("   HTML + PDFs + Redes Sociales")
    print("=" * 70)

    t_start = time.time()

    html_count   = scrape_html_pages()
    pdf_count    = scrape_pdf_documents()
    social_added = integrate_social_media()

    elapsed = time.time() - t_start

    print("\n" + "=" * 70)
    print("✅ SCRAPING COMPLETADO")
    print("=" * 70)
    print(f"   📄 Documentos HTML extraídos: {html_count}")
    print(f"   📑 PDFs procesados:           {pdf_count}")
    print(f"   🌐 Redes sociales:            {'integradas' if social_added else 'no aplicó'}")
    print(f"   ⏱  Tiempo total:              {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print("=" * 70)

    total_docs = html_count + pdf_count + (1 if social_added else 0)
    print(f"\n📊 Total documentos en {OUTPUT_DIR}: {total_docs}")
    print("\n💡 Siguiente paso:\n")
    print("   python 03_cleaner.py")
    print("   python 04_markdown_builder.py")
    print("   python 05_corpus_master.py")
    print("   streamlit run app.py\n")
