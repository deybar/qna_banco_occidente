"""
00_reset.py — Limpieza Completa del Pipeline
═══════════════════════════════════════════════════════════════════════════════
Borra TODOS los datos generados por el pipeline para empezar desde cero.
Útil cuando quieres re-ejecutar todo el flujo sin que queden residuos
de ejecuciones anteriores.

Uso:
    python 00_reset.py
    python 00_reset.py --auto    # No pide confirmación

ARCHIVOS Y CARPETAS QUE SE BORRAN:
  - data/urls.txt
  - data/pdf_urls.txt
  - data/social_links.txt
  - data/raw_docs/
  - data/clean_docs/
  - data/markdown_docs/
  - data/pdf_docs/
  - data/corpus_master.md
  - __pycache__/

NO SE TOCAN:
  - El código fuente (.py)
  - El archivo .env
  - El archivo .gitignore
  - La carpeta venv/
"""

import os
import shutil
import sys

# ════════════════════════════════════════════════════════════════
# CONFIGURACIÓN — RUTAS A LIMPIAR
# ════════════════════════════════════════════════════════════════

FILES_TO_DELETE = [
    "data/urls.txt",
    "data/pdf_urls.txt",
    "data/social_links.txt",
    "data/corpus_master.md",
    "data/chunks.json",
]

DIRS_TO_CLEAN = [
    "data/raw_docs",
    "data/clean_docs",
    "data/markdown_docs",
    "data/pdf_docs",
    "__pycache__",
]


# ════════════════════════════════════════════════════════════════
# FUNCIONES
# ════════════════════════════════════════════════════════════════

def delete_file(path: str) -> bool:
    """Borra un archivo si existe. Retorna True si lo borró."""
    if os.path.exists(path):
        try:
            os.remove(path)
            return True
        except Exception as e:
            print(f"  ⚠️ Error al borrar {path}: {e}")
            return False
    return False


def clean_directory(path: str) -> tuple:
    """
    Borra el contenido de un directorio (no el directorio en sí).
    Retorna (existió, archivos_borrados).
    """
    if not os.path.exists(path):
        return False, 0

    files_count = 0
    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isfile(full_path):
                os.remove(full_path)
                files_count += 1
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
                files_count += 1
        return True, files_count
    except Exception as e:
        print(f"  ⚠️ Error al limpiar {path}: {e}")
        return True, files_count


def get_size_mb(path: str) -> float:
    """Calcula tamaño total en MB de un archivo o carpeta."""
    if not os.path.exists(path):
        return 0.0
    if os.path.isfile(path):
        return os.path.getsize(path) / (1024 * 1024)
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass
    return total / (1024 * 1024)


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

def run(auto: bool = False):
    print("=" * 70)
    print("🧹 LIMPIEZA DEL PIPELINE — Sistema Q&A Banco de Occidente")
    print("=" * 70)

    # ── ESCANEO INICIAL ──
    print("\n📊 Resumen del estado actual:\n")
    total_size = 0.0
    found_anything = False

    for f in FILES_TO_DELETE:
        if os.path.exists(f):
            size = get_size_mb(f)
            total_size += size
            print(f"  📄 {f:<35} {size:>8.2f} MB")
            found_anything = True

    for d in DIRS_TO_CLEAN:
        if os.path.exists(d):
            size = get_size_mb(d)
            count = sum(1 for _ in os.walk(d) for _ in _) if os.path.isdir(d) else 0
            num_files = sum(len(files) for _, _, files in os.walk(d))
            total_size += size
            print(f"  📁 {d:<35} {size:>8.2f} MB  ({num_files} archivos)")
            found_anything = True

    if not found_anything:
        print("  ✨ No hay nada que limpiar — el proyecto ya está limpio.\n")
        return

    print(f"\n  💾 Total a liberar: {total_size:.2f} MB\n")

    # ── CONFIRMACIÓN ──
    if not auto:
        respuesta = input("⚠️  ¿Confirmas borrar TODOS estos archivos? (escribe 'SI' para confirmar): ")
        if respuesta.strip().upper() != "SI":
            print("\n❌ Operación cancelada por el usuario.\n")
            return

    # ── EJECUCIÓN ──
    print("\n" + "─" * 70)
    print("🗑️  Iniciando limpieza...\n")

    deleted_files   = 0
    cleaned_dirs    = 0

    # Borrar archivos individuales
    for f in FILES_TO_DELETE:
        if delete_file(f):
            print(f"  ✅ Borrado: {f}")
            deleted_files += 1

    # Limpiar directorios
    for d in DIRS_TO_CLEAN:
        existed, count = clean_directory(d)
        if existed and count > 0:
            print(f"  ✅ Limpiado: {d}/ ({count} elementos)")
            cleaned_dirs += 1
        elif existed:
            print(f"  ✓  Vacío:    {d}/")

    # ── RESUMEN ──
    print("\n" + "=" * 70)
    print("✅ LIMPIEZA COMPLETADA")
    print("=" * 70)
    print(f"📄 Archivos borrados:       {deleted_files}")
    print(f"📁 Directorios limpiados:   {cleaned_dirs}")
    print(f"💾 Espacio liberado:        {total_size:.2f} MB")
    print("=" * 70)
    print("\n💡 Siguiente paso: ejecuta el pipeline desde el inicio:\n")
    print("   python 01_crawling.py")
    print("   python 02_scraping_selenium.py")
    print("   python 03_cleaner.py")
    print("   python 04_markdown_builder.py")
    print("   python 05_corpus_master.py")
    print("   streamlit run app.py\n")


if __name__ == "__main__":
    auto_mode = "--auto" in sys.argv
    run(auto=auto_mode)
