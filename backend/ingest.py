# backend/ingest.py
import argparse
import shutil
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


def main(rebuild: bool = False):
    if rebuild:
        print("🧹 Limpiando índice Chroma…")
        clear_chroma_dir()

    print(f"📂 Cargando PDFs desde {DOCS_DIR}…")
    loader = PyPDFDirectoryLoader(str(DOCS_DIR))
    docs = loader.load()
    print(f"📄 Total de documentos cargados: {len(docs)}")

    # Trocear documentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=350,
        chunk_overlap=70
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





