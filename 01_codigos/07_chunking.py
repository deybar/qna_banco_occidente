import os
import sys
import re
import json
import math
import time
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CORPUS_FILE, CHROMA_DIR, CHROMA_COLLECTION, ensure_dirs

from dotenv import load_dotenv
load_dotenv()

ensure_dirs()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Embeddings locales — sin cuotas de API, soporte nativo para español
# El modelo se descarga ~550MB la primera vez y queda en caché
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
BATCH_SIZE      = 64    # los modelos locales soportan batches grandes
CHUNK_SIZE      = 700
CHUNK_OVERLAP   = 120


def _load_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    print("  Cargando modelo de embeddings...")
    print(f"  Modelo: {EMBEDDING_MODEL}")
    print("  (Primera vez descarga ~550MB, luego usa caché local)\n")
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True, "batch_size": BATCH_SIZE},
    )


def parse_corpus_sections(corpus_text: str) -> list:
    sections     = []
    current_cat  = "general"
    current_text = []

    for line in corpus_text.split("\n"):
        cat_match = re.search(r"CATEGORÍA:\s*(\w+)", line, re.IGNORECASE)
        if cat_match:
            if current_text:
                sections.append({
                    "categoria": current_cat,
                    "texto":     "\n".join(current_text).strip(),
                })
                current_text = []
            current_cat = cat_match.group(1).lower()
        else:
            current_text.append(line)

    if current_text:
        sections.append({
            "categoria": current_cat,
            "texto":     "\n".join(current_text).strip(),
        })

    return [s for s in sections if len(s["texto"]) > 100]


def detect_source_type(text: str) -> str:
    text_lower = text.lower()
    if any(k in text_lower for k in ["transcripción", "subtítulo", "youtu", "video"]):
        return "youtube"
    if any(k in text_lower for k in ["página", "anexo", ".pdf"]):
        return "pdf"
    return "html"


def extract_section_title(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            return re.sub(r"^#+\s*", "", line).strip()[:100]
    return text[:60].strip()


def enrich_chunks(raw_chunks: list, categoria: str, chunk_id_start: int) -> list:
    docs = []
    for i, chunk in enumerate(raw_chunks):
        text = chunk.page_content.strip()
        if len(text) < 80:
            continue

        metadata = {
            "categoria":   categoria,
            "seccion":     extract_section_title(text),
            "tipo_fuente": detect_source_type(text),
            "chunk_id":    chunk_id_start + i,
            "char_count":  len(text),
            "fecha":       datetime.now().strftime("%Y-%m-%d"),
        }

        prefijo = f"[Banco de Occidente · {categoria.upper()}]\n\n"
        docs.append(Document(page_content=prefijo + text, metadata=metadata))

    return docs


def build_vector_store(documents: list, embeddings_model) -> None:
    import chromadb

    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)
        print("  Vector store anterior eliminado.\n")

    os.makedirs(CHROMA_DIR, exist_ok=True)

    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection    = chroma_client.create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    total_batches = math.ceil(len(documents) / BATCH_SIZE)
    failed        = 0

    for i in range(0, len(documents), BATCH_SIZE):
        batch     = documents[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        texts     = [doc.page_content for doc in batch]
        metadatas = [doc.metadata     for doc in batch]
        ids       = [f"chunk_{i + j}" for j in range(len(batch))]

        print(f"  Batch {batch_num:>3}/{total_batches} ({len(batch)} chunks)...",
              end=" ", flush=True)

        try:
            embeds = embeddings_model.embed_documents(texts)

            if len(embeds) != len(texts):
                raise ValueError(
                    f"Mismatch embeddings: esperados {len(texts)}, recibidos {len(embeds)}"
                )

            collection.add(
                embeddings=embeds,
                documents=texts,
                metadatas=metadatas,
                ids=ids,
            )
            print("✓")

        except Exception as e:
            print(f"✗ {str(e)[:80]}")
            failed += 1

    total = collection.count()
    print(f"\n  Chunks indexados en ChromaDB: {total}")
    if failed:
        print(f"  ⚠️  Batches fallidos: {failed} — re-ejecuta el paso para completar.")


def save_stats(documents: list) -> dict:
    cat_counts    = {}
    source_counts = {}
    for doc in documents:
        cat = doc.metadata["categoria"]
        src = doc.metadata["tipo_fuente"]
        cat_counts[cat]    = cat_counts.get(cat, 0) + 1
        source_counts[src] = source_counts.get(src, 0) + 1

    total_chars = sum(doc.metadata["char_count"] for doc in documents)
    avg_chars   = total_chars // max(len(documents), 1)

    stats = {
        "total_chunks":            len(documents),
        "avg_chars_per_chunk":     avg_chars,
        "total_chars":             total_chars,
        "embedding_model":         EMBEDDING_MODEL,
        "embedding_type":          "local_sentence_transformers",
        "chunk_size":              CHUNK_SIZE,
        "chunk_overlap":           CHUNK_OVERLAP,
        "fecha_creacion":          datetime.now().isoformat(),
        "distribucion_categorias": cat_counts,
        "distribucion_fuentes":    source_counts,
    }

    stats_file = os.path.join(CHROMA_DIR, "stats.json")
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    return stats


def run():
    print("\n=== CHUNKING + EMBEDDINGS — Banco de Occidente ===")
    print(f"  Chunk size:  {CHUNK_SIZE} chars  |  Overlap: {CHUNK_OVERLAP} chars")
    print(f"  Batch size:  {BATCH_SIZE} chunks\n")

    if not os.path.exists(CORPUS_FILE):
        print(f"❌ Corpus no encontrado: {CORPUS_FILE}")
        print("   Ejecuta primero: python main.py --step corpus")
        return

    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        corpus_text = f.read()

    print(f"  Corpus cargado: {len(corpus_text):,} caracteres\n")

    sections = parse_corpus_sections(corpus_text)
    print(f"  Secciones detectadas: {len(sections)}\n")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " "],
        length_function=len,
    )

    all_documents = []
    chunk_counter = 0

    for section in sections:
        raw_chunks = splitter.create_documents([section["texto"]])
        enriched   = enrich_chunks(raw_chunks, section["categoria"], chunk_counter)
        all_documents.extend(enriched)
        chunk_counter += len(enriched)

    cat_summary = {}
    for doc in all_documents:
        cat = doc.metadata["categoria"]
        cat_summary[cat] = cat_summary.get(cat, 0) + 1

    print(f"  Total chunks generados: {len(all_documents)}\n")
    print("  Distribución por categoría:")
    for cat, n in sorted(cat_summary.items(), key=lambda x: -x[1]):
        bar = "█" * min(n // 10, 60)
        print(f"    {cat:<20} {n:>4}  {bar}")

    embeddings_model = _load_embeddings()

    t0 = time.time()
    print(f"\n  Construyendo ChromaDB en: {CHROMA_DIR}\n")
    build_vector_store(all_documents, embeddings_model)

    stats   = save_stats(all_documents)
    elapsed = time.time() - t0

    print(f"\n{'='*55}")
    print(f"  Chunks indexados:    {stats['total_chunks']}")
    print(f"  Avg chars/chunk:     {stats['avg_chars_per_chunk']}")
    print(f"  Tiempo total:        {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"  Modelo:              {EMBEDDING_MODEL}")
    print(f"  Fuentes incluidas:")
    for src, n in stats["distribucion_fuentes"].items():
        print(f"    {src:<12} {n} chunks")
    print(f"  Vector store:        {CHROMA_DIR}")
    print(f"{'='*55}")
    print("\nSiguiente paso: python main.py --app\n")


if __name__ == "__main__":
    run()
