"""
Utilidades compartidas para la aplicación.
"""
from backend.utils.cache import (
    get_cached_response,
    set_cached_response,
    clear_cache,
    get_cache_stats
)
from backend.utils.logger import (
    logger,
    log_request,
    log_metric,
    log_error
)
from backend.utils.security import (
    sanitize_text,
    sanitize_html_response,
    validate_input
)

__all__ = [
    "get_cached_response",
    "set_cached_response",
    "clear_cache",
    "get_cache_stats",
    "logger",
    "log_request",
    "log_metric",
    "log_error",
    "sanitize_text",
    "sanitize_html_response",
    "validate_input",
]

