"""
Sistema de logging estructurado usando loguru.
"""
import sys
from loguru import logger
from pathlib import Path

# Configurar logger
logger.remove()  # Remover handler por defecto

# Formato estructurado
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Logger para consola
logger.add(
    sys.stdout,
    format=log_format,
    level="INFO",
    colorize=True
)

# Logger para archivo (solo errores y warnings)
log_dir = Path(__file__).resolve().parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "app_{time:YYYY-MM-DD}.log",
    format=log_format,
    level="WARNING",
    rotation="1 day",
    retention="30 days",
    compression="zip"
)

# Logger para métricas
logger.add(
    log_dir / "metrics_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
    level="INFO",
    rotation="1 day",
    retention="7 days",
    filter=lambda record: "METRIC" in record["message"]
)

def log_request(endpoint: str, method: str, status_code: int, duration_ms: float, **kwargs):
    """Registra una petición HTTP."""
    logger.info(
        f"REQUEST | {method} {endpoint} | Status: {status_code} | Duration: {duration_ms:.2f}ms",
        extra={"endpoint": endpoint, "method": method, "status_code": status_code, "duration_ms": duration_ms, **kwargs}
    )

def log_metric(metric_name: str, value: float, **kwargs):
    """Registra una métrica."""
    logger.info(
        f"METRIC | {metric_name}={value}",
        extra={"metric_name": metric_name, "value": value, **kwargs}
    )

def log_error(error: Exception, context: dict = None):
    """Registra un error con contexto."""
    logger.error(
        f"ERROR | {type(error).__name__}: {str(error)}",
        exc_info=True,
        extra={"context": context or {}}
    )

