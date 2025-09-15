# backend/retrieve.py
from pathlib import Path
from typing import Dict, Any
from backend.llm_loader import get_embeddings
from backend.config import CHROMA_DIR
from langchain_community.vectorstores import Chroma


def _has_chroma_index(dirpath: Path) -> bool:
    """
    Comprueba si el directorio de CHROMA_DIR contiene un índice válido.
    En la práctica, buscamos al menos un archivo .sqlite3 (p. ej. chroma.sqlite3).
    """
    if not dirpath.exists():
        return False
    # Busca un archivo sqlite3 dentro del directorio (nivel superior)
    for p in dirpath.iterdir():
        if p.is_file() and p.suffix == ".sqlite3":
            return True
    # Si no se encontró .sqlite3 arriba, revisa recursivamente por si la versión persiste en subcarpetas.
    for p in dirpath.rglob("*.sqlite3"):
        return True
    return False


def get_vectordb() -> Chroma:
    """
    Devuelve la instancia de Chroma persistente usando las embeddings actuales.
    Lanza excepción clara si el índice no existe (p. ej., primera vez sin PDFs).
    """
    chroma_dir = Path(CHROMA_DIR)
    if not _has_chroma_index(chroma_dir):
        raise RuntimeError(
            f"No se encontró un índice Chroma en {chroma_dir}. "
            "Sube tus PDFs a backend/data/docs y/o permite que ensure_index() "
            "construya el índice al iniciar."
        )

    embeddings = get_embeddings()
    return Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=embeddings
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

    Parámetros:
    - k: número de documentos a devolver.
    - use_mmr: si True, usa Maximal Marginal Relevance ("mmr") para diversidad.
    - fetch_k: candidatos iniciales (solo relevante para MMR).
    - lambda_mult: balance relevancia/diversidad en MMR (0..1).
    - score_threshold: umbral de similitud (0..1). Se aplica cuando use_mmr=False,
      usando el search_type 'similarity_score_threshold'.

    Nota:
    - En 'mmr' el 'score_threshold' NO se aplica. Si necesitas umbral + diversidad,
      puedes iniciar con MMR y filtrar manualmente resultados, pero aquí optamos
      por usar 'similarity_score_threshold' cuando use_mmr=False.
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
        # Aplica umbral de similitud
        search_type = "similarity_score_threshold"
        search_kwargs = {
            "k": k,
            "score_threshold": score_threshold,
        }

    return vectordb.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

