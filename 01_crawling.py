import os
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque
import xml.etree.ElementTree as ET

# ========================
# CONFIGURACIÓN
# ========================

BASE_URL = "https://www.bancodeoccidente.com.co/"
DOMAIN = "bancodeoccidente.com.co"

OUTPUT_FILE = "data/urls.txt"
MAX_URLS = 400
DELAY = 1.5  # segundos entre requests (clave para no ser bloqueado)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

os.makedirs("data", exist_ok=True)

# ========================
# UTILIDADES
# ========================

def is_valid(url):
    parsed = urlparse(url)
    return (
        parsed.scheme in ["http", "https"]
        and DOMAIN in parsed.netloc
        and not any(ext in url for ext in [".pdf", ".jpg", ".png", ".zip"])
        and "#" not in url
        and "?" not in url  # evita duplicados con parámetros
    )

# ========================
# 1. INTENTO: SITEMAP (FAST PATH)
# ========================

def get_sitemap_urls():
    sitemap_url = urljoin(BASE_URL, "sitemap.xml")
    print(f"🔍 Buscando sitemap: {sitemap_url}")

    try:
        res = requests.get(sitemap_url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return []

        urls = []
        root = ET.fromstring(res.content)

        for url in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            if is_valid(url.text):
                urls.append(url.text)

        print(f"✅ {len(urls)} URLs encontradas en sitemap")
        return urls

    except Exception as e:
        print(f"⚠️ Error leyendo sitemap: {e}")
        return []

# ========================
# 2. CRAWLER BFS CONTROLADO
# ========================

def crawl():
    visited = set()
    queue = deque([BASE_URL])

    while queue and len(visited) < MAX_URLS:
        url = queue.popleft()

        if url in visited:
            continue

        print(f"🌐 Visitando: {url}")
        visited.add(url)

        try:
            res = requests.get(url, headers=HEADERS, timeout=10)

            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "lxml")

            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])

                if is_valid(full_url) and full_url not in visited:
                    queue.append(full_url)

            time.sleep(DELAY)

        except Exception as e:
            print(f"❌ Error: {e}")

    return list(visited)

# ========================
# MAIN
# ========================

if __name__ == "__main__":
    print("🚀 Iniciando crawling inteligente...")

    urls = get_sitemap_urls()

    # Si sitemap no funciona, usamos crawler
    if len(urls) == 0:
        print("⚠️ Sitemap no disponible, usando crawler BFS...")
        urls = crawl()

    # Guardar resultado
    urls = list(set(urls))[:MAX_URLS]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")

    print(f"\n✅ Total URLs recolectadas: {len(urls)}")
    print(f"📁 Guardadas en: {OUTPUT_FILE}")