# backend/ingest.py
import argparse
import shutil
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from backend.config import DOCS_DIR, CHROMA_DIR
from backend.llm_loader import get_embeddings


# ================================
# Carga de PDFs
# ================================
def load_all_pdfs(docs_dir: Path):
    """Carga todos los PDFs desde docs_dir y añade metadatos."""
    docs = []
    for pdf_path in sorted(docs_dir.glob("**/*.pdf")):
        print(f"📄 Cargando {pdf_path.name}...")
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()

        # Metadatos personalizados según archivo
        if "s10639-023-12401-4" in pdf_path.name:
            title = ("Learning analytics dashboards are increasingly becoming about learning "
                     "and not just analytics – A systematic review")
            authors = "Lucas Paulsen, Euan Lindsay"
        elif "s41239-023-00426-1" in pdf_path.name:
            title = "Role of AI chatbots in education: systematic literature review"
            authors = "Lasha Labadze, Maya Grigolia, Lela Machaidze"
        else:
            title = pdf_path.stem
            authors = "Autores desconocidos"

        # Asignar metadatos a cada página
        for p in pages:
            p.metadata = p.metadata or {}
            p.metadata["title"] = title
            p.metadata["authors"] = authors
            p.metadata["doc_id"] = pdf_path.stem
        docs.extend(pages)

    return docs


# ================================
# Split de documentos
# ================================
def split_docs(docs, chunk_size=350, chunk_overlap=70):
    """Divide documentos en chunks con solapamiento."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(docs)


# ================================
# Manejo del índice
# ================================
def rebuild_chroma():
    """Elimina índice existente de Chroma."""
    if CHROMA_DIR.exists():
        print("🧹 Limpiando índice Chroma…")
        shutil.rmtree(CHROMA_DIR)


def has_index() -> bool:
    """Revisa si ya existe un índice persistente en CHROMA_DIR."""
    return CHROMA_DIR.exists() and any(CHROMA_DIR.glob("**/*"))


# ================================
# Construcción de índice
# ================================
def main(rebuild: bool = False):
    if rebuild:
        rebuild_chroma()

    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"❌ No existe {DOCS_DIR}. Coloca tus PDFs allí.")

    print(f"📂 Cargando PDFs desde {DOCS_DIR}…")
    raw_docs = load_all_pdfs(DOCS_DIR)
    if not raw_docs:
        raise RuntimeError("❌ No se encontraron PDFs en data/docs")

    print("✂️ Troceando documentos (350/70)…")
    chunks = split_docs(raw_docs)

    print(f"📊 Total de páginas: {len(raw_docs)}")
    print(f"📊 Total de chunks: {len(chunks)}")

    print("⚙️ Generando embeddings y persistiendo en Chroma…")
    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    vectordb.persist()
    print(f"✅ Listo. Índice guardado en {CHROMA_DIR}")


def ensure_index():
    """Usado en startup: si no existe índice, lo construye."""
    if has_index():
        print("✅ Índice Chroma existente. No se reconstruye.")
        return
    print("ℹ️ No hay índice Chroma. Creándolo por primera vez…")
    main(rebuild=False)


# ================================
# CLI
# ================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rebuild", action="store_true", help="Reconstruye el índice desde cero"
    )
    args = parser.parse_args()

    if args.rebuild:
        main(rebuild=True)
    else:
        ensure_index()

