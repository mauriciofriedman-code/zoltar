"""
Utilidades de seguridad: sanitización de entrada y protección XSS.
"""
import bleach
from html import escape
import re

# Configuración de bleach para permitir solo texto plano
ALLOWED_TAGS = []  # No permitir HTML
ALLOWED_ATTRIBUTES = {}
ALLOWED_STYLES = []

# Patrones para detectar intentos de inyección
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
    r"(--|#|/\*|\*/)",
    r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
]

SCRIPT_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",  # Event handlers como onclick=
]


def sanitize_text(text: str, max_length: int = 2000) -> str:
    """
    Sanitiza texto de entrada eliminando HTML, scripts y caracteres peligrosos.
    
    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima permitida
        
    Returns:
        Texto sanitizado
    """
    if not text:
        return ""
    
    # Truncar si es muy largo
    if len(text) > max_length:
        text = text[:max_length]
    
    # Eliminar caracteres de control excepto \n y \r
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Escapar HTML
    text = escape(text)
    
    # Eliminar scripts y patrones peligrosos
    for pattern in SCRIPT_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Detectar intentos de SQL injection (solo para logging, no bloqueamos)
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            # Log pero no bloqueamos (puede ser texto legítimo)
            pass
    
    return text.strip()


def sanitize_html_response(html_content: str) -> str:
    """
    Sanitiza contenido HTML de respuestas del LLM para prevenir XSS.
    
    Args:
        html_content: Contenido HTML a sanitizar
        
    Returns:
        HTML sanitizado
    """
    if not html_content:
        return ""
    
    # Usar bleach para sanitizar HTML
    # Permitir solo párrafos, saltos de línea y texto básico
    ALLOWED_TAGS_SAFE = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
    
    sanitized = bleach.clean(
        html_content,
        tags=ALLOWED_TAGS_SAFE,
        attributes={},
        styles=[],
        strip=True
    )
    
    return sanitized


def validate_input(text: str, min_length: int = 3, max_length: int = 2000) -> tuple[bool, str]:
    """
    Valida entrada de texto.
    
    Returns:
        (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "El texto no puede estar vacío"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"El texto debe tener al menos {min_length} caracteres"
    
    if len(text) > max_length:
        return False, f"El texto no puede exceder {max_length} caracteres"
    
    # Verificar que no sea solo espacios
    if not text.replace(' ', '').replace('\n', '').replace('\t', ''):
        return False, "El texto no puede contener solo espacios"
    
    return True, ""

