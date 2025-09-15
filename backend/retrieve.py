# backend/retrieve.py
from pathlib import Path
from typing import Dict, Any
from backend.llm_loader import get_embeddings
from backend.config import CHROMA_DIR
from langchain_community.vectorstores import Chroma


def _has_chroma_index(dirpath: Path) -> bool:
    """
    Comprueba si el directorio de CHROMA_DIR contiene un índice válido.

    En Chroma <0.4.x se buscaba chroma.sqlite3.
    En Chroma 0.4+ el índice se guarda en subcarpetas (ej: "index", "index_uuid").
    """
    if not dirpath.exists():
        return False

    # Compatibilidad con Chroma <0.4.x
    if any(p.is_file() and p.suffix == ".sqlite3" for p in dirpath.iterdir()):
        return True

    # Compatibilidad con Chroma 0.4+ (mira subcarpetas con metadata)
    if any(p.is_dir() and (p / "chroma.sqlite3").exists() for p in dirpath.iterdir()):
        return True
    if any(p.is_dir() and (p / "MANIFEST").exists() for p in dirpath.iterdir()):
        return True

    return False


def get_vectordb() -> Chroma:
    """
    Devuelve la instancia de Chroma persistente usando las embeddings actuales.
    Lanza excepción clara si el índice no existe.
    """
    chroma_dir = Path(CHROMA_DIR)
    if not _has_chroma_index(chroma_dir):
        raise RuntimeError(
            f"❌ No se encontró un índice Chroma en {chroma_dir}. "
            "Ejecuta `python -m backend.ingest --rebuild` primero."
        )

    embeddings = get_embeddings()
    return Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=embeddings,
    )


def get_retriever(
    k: int = 6,
    use_mmr: bool = True,
    fetch_k: int = 24,
    lambda_mult: float = 0.5,
    score_threshold: float = 0.55,
):
    """
    Construye un retriever de Chroma.

    - k: número de documentos a devolver
    - use_mmr: si True, usa Maximal Marginal Relevance ("mmr") para diversidad
    - fetch_k: candidatos iniciales (solo relevante para MMR)
    - lambda_mult: balance relevancia/diversidad en MMR
    - score_threshold: umbral de similitud (solo cuando use_mmr=False)
    """
    vectordb = get_vectordb()

    if use_mmr:
        search_type = "mmr"
        search_kwargs: Dict[str, Any] = {
            "k": k,
            "fetch_k": fetch_k,
            "lambda_mult": lambda_mult,
        }
    else:
        search_type = "similarity_score_threshold"
        search_kwargs: Dict[str, Any] = {
            "k": k,
            "score_threshold": score_threshold,
        }

    return vectordb.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

