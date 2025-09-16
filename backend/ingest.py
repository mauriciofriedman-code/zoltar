# backend/ingest.py
import argparse
import shutil
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from PyPDF2 import PdfReader

from backend.config import DOCS_DIR, CHROMA_DIR, EMBEDDINGS_MODEL


def clear_chroma_dir():
    """Elimina todo el contenido de CHROMA_DIR (archivos y subcarpetas)."""
    if CHROMA_DIR.exists():
        for f in CHROMA_DIR.iterdir():
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f)


def extract_authors_from_filename(filename: str) -> str | None:
    """
    Si el archivo está en formato Autor1_Autor2_Titulo.pdf,
    extrae los autores antes del primer guion bajo.
    """
    stem = Path(filename).stem
    parts = stem.split("_")
    if len(parts) > 1:
        # todo antes del último bloque lo tomamos como autores
        return ", ".join(parts[:-1])
    return None


def extract_authors_from_pdf(path: str) -> str | None:
    """
    Intenta leer la primera página del PDF y detectar autores.
    Regresa un string o None si no encuentra.
    """
    try:
        reader = PdfReader(path)
        if len(reader.pages) == 0:
            return None
        first_page = reader.pages[0].extract_text()
        if not first_page:
            return None

        # Heurística simple: buscar línea con varios nombres capitalizados separados por comas
        for line in first_page.split("\n"):
            if line and line.count(",") >= 1 and any(ch.isupper() for ch in line):
                if len(line.split()) <= 15:  # no demasiado larga
                    return line.strip()
        return None
    except Exception:
        return None


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
        src = d.metadata.get("source", "desconocido")
        page = d.metadata.get("page", "N/A")

        title = Path(src).stem
        authors = extract_authors_from_filename(src)
        if not authors:
            authors = extract_authors_from_pdf(src)
        if not authors:
            authors = "Autor desconocido"

        d.metadata["doc_id"] = str(src)
        d.metadata["title"] = title
        d.metadata["authors"] = authors
        d.metadata["page"] = page
        d.metadata["source"] = str(src)

    # Trocear documentos (chunks más grandes)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,   # 🔥 más grande para contexto educativo
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(docs)
    print(f"✂️ Total de chunks: {len(splits)}")

    # Crear embeddings
    embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)

    # Crear base de datos vectorial en Chroma (se guarda automáticamente)
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





