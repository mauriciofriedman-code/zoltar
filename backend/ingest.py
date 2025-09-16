# backend/ingest.py

import argparse
import shutil
from pathlib import Path
from typing import Optional
from pypdf import PdfReader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

from backend.config import DOCS_DIR, CHROMA_DIR, EMBEDDINGS_MODEL


def clear_chroma_dir():
    """Elimina todo el contenido de CHROMA_DIR (archivos y subcarpetas)."""
    if CHROMA_DIR.exists():
        for f in CHROMA_DIR.iterdir():
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f)


def extract_pdf_metadata(pdf_path: Path) -> dict:
    """
    Extrae metadatos útiles (title, author, etc.) del PDF si existen.
    """
    try:
        reader = PdfReader(str(pdf_path))
        info = reader.metadata or {}

        title = info.get("/Title") or pdf_path.stem
        authors = info.get("/Author") or "Autor desconocido"

        return {
            "title": title.strip(),
            "authors": authors.strip(),
        }
    except Exception as e:
        print(f"[!] Error extrayendo metadatos de {pdf_path.name}: {e}")
        return {
            "title": pdf_path.stem,
            "authors": "Autor desconocido"
        }


def main(rebuild: bool = False):
    if rebuild:
        print("🧹 Limpiando índice Chroma…")
        clear_chroma_dir()

    print(f"📂 Cargando PDFs desde {DOCS_DIR}…")
    loader = PyPDFDirectoryLoader(str(DOCS_DIR))
    docs = loader.load()
    print(f"📄 Total de documentos cargados: {len(docs)}")

    # Enriquecer metadata de cada documento
    for d in docs:
        raw_path = d.metadata.get("source", "")
        path = Path(raw_path)
        meta = extract_pdf_metadata(path)

        d.metadata["doc_id"] = path.name
        d.metadata["title"] = meta["title"]
        d.metadata["authors"] = meta["authors"]
        d.metadata["page"] = d.metadata.get("page", "N/A")
        d.metadata["source"] = path.name

    # Trocear documentos en chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
    )
    splits = text_splitter.split_documents(docs)
    print(f"✂️ Total de chunks: {len(splits)}")

    # Crear embeddings
    embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)

    # Crear base de datos vectorial
    Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    print(f"✅ Embeddings guardados en {CHROMA_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Recrear el índice desde cero"
    )
    args = parser.parse_args()
    main(rebuild=args.rebuild)






