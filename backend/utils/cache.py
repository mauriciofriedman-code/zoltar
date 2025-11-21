"""
Sistema de caché para respuestas del chatbot.
Usa LRU cache en memoria para respuestas frecuentes.
"""
from functools import lru_cache
from typing import Dict, Optional
import hashlib
import json
import time

# Cache en memoria con TTL
_cache_store: Dict[str, tuple] = {}  # {hash: (response, timestamp)}
CACHE_TTL = 3600  # 1 hora en segundos
MAX_CACHE_SIZE = 100


def _generate_cache_key(text: str, mode: str, rag: bool = False, history: str = "") -> str:
    """Genera una clave única para el caché basada en los parámetros de entrada."""
    cache_data = {
        "text": text.strip().lower(),
        "mode": mode,
        "rag": rag,
        "history": history.strip().lower() if history else ""
    }
    cache_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_str.encode()).hexdigest()


def get_cached_response(text: str, mode: str, rag: bool = False, history: str = "") -> Optional[Dict]:
    """
    Obtiene una respuesta del caché si existe y no ha expirado.
    
    Returns:
        Dict con la respuesta o None si no está en caché/expirado
    """
    cache_key = _generate_cache_key(text, mode, rag, history)
    
    if cache_key in _cache_store:
        response, timestamp = _cache_store[cache_key]
        
        # Verificar si el caché ha expirado
        if time.time() - timestamp < CACHE_TTL:
            return response
        else:
            # Eliminar entrada expirada
            del _cache_store[cache_key]
    
    return None


def set_cached_response(text: str, mode: str, response: Dict, rag: bool = False, history: str = ""):
    """
    Almacena una respuesta en el caché.
    
    Args:
        text: Texto de la pregunta
        mode: Modo del chatbot
        response: Respuesta a cachear
        rag: Si es modo RAG
        history: Historial opcional
    """
    # Limpiar caché si está lleno
    if len(_cache_store) >= MAX_CACHE_SIZE:
        # Eliminar la entrada más antigua
        oldest_key = min(_cache_store.keys(), key=lambda k: _cache_store[k][1])
        del _cache_store[oldest_key]
    
    cache_key = _generate_cache_key(text, mode, rag, history)
    _cache_store[cache_key] = (response, time.time())


def clear_cache():
    """Limpia todo el caché."""
    _cache_store.clear()


def get_cache_stats() -> Dict:
    """Retorna estadísticas del caché."""
    current_time = time.time()
    valid_entries = sum(1 for _, (_, ts) in _cache_store.items() if current_time - ts < CACHE_TTL)
    expired_entries = len(_cache_store) - valid_entries
    
    return {
        "total_entries": len(_cache_store),
        "valid_entries": valid_entries,
        "expired_entries": expired_entries,
        "max_size": MAX_CACHE_SIZE,
        "ttl_seconds": CACHE_TTL
    }

