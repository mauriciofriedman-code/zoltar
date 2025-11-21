from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

# RAG y prompts
from backend.rag_pipeline import chatbot_simple
from backend.prompt_baseline import BASELINE_SYSTEM_PROMPT

# Utilidades
from backend.utils import (
    get_cached_response,
    set_cached_response,
    sanitize_text,
    validate_input,
    logger,
    log_metric
)

# Si no existe ENGINEERED, cae a BASELINE
try:
    from backend.prompt_baseline import ENGINEERED_SYSTEM_PROMPT
except Exception:
    ENGINEERED_SYSTEM_PROMPT = BASELINE_SYSTEM_PROMPT

router = APIRouter(tags=["generate"])
limiter = Limiter(key_func=get_remote_address)

# ==== Esquemas ====
class GenerateIn(BaseModel):
    text: str = Field(..., min_length=1, description="Consulta del usuario")
    mode: str = Field(
        default="engineered",
        description='Modo del chatbot: "baseline" o "engineered"',
    )

class GenerateOut(BaseModel):
    text: str

# ==== Endpoint ====
@router.post("/generate", response_model=GenerateOut)
@limiter.limit("20/minute")  # Rate limiting: 20 requests por minuto
def generate_endpoint(request: Request, inp: GenerateIn):
    """
    Chatbot simple (baseline / engineered) sin RAG.
    - Aquí el modelo puede alucinar, porque no está grounded en documentos.
    
    **Rate Limit**: 20 requests por minuto por IP
    """
    import time
    start_time = time.time()
    
    # Sanitizar y validar entrada
    q = sanitize_text(inp.text or "", max_length=2000)
    
    is_valid, error_msg = validate_input(q, min_length=3, max_length=2000)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Validar modo
    mode = inp.mode.lower()
    if mode not in ["baseline", "engineered"]:
        mode = "engineered"  # Default seguro

    # Verificar caché
    cached_response = get_cached_response(q, mode, rag=False)
    if cached_response:
        logger.info(f"Cache hit for generate endpoint: {q[:50]}...")
        log_metric("cache_hit", 1, endpoint="generate")
        return GenerateOut(text=cached_response.get("text", ""))

    try:
        # Elegir prompt
        system_prompt = (
            BASELINE_SYSTEM_PROMPT if mode == "baseline"
            else ENGINEERED_SYSTEM_PROMPT
        )

        # ✅ Enviar mensaje como lista de mensajes
        conversation = [{"role": "user", "content": q}]
        answer_dict = chatbot_simple(conversation, system_prompt)
        response_text = answer_dict.get("text", "⚠️ Respuesta vacía")
        
        # Validar que la respuesta no esté vacía
        if not response_text or len(response_text.strip()) == 0:
            response_text = "Lo siento, no pude generar una respuesta. Por favor, intenta reformular tu pregunta."
        
        # Almacenar en caché
        response_dict = {"text": response_text}
        set_cached_response(q, mode, response_dict, rag=False)
        
        # Log métricas
        duration = (time.time() - start_time) * 1000
        log_metric("generate_duration_ms", duration, mode=mode)
        log_metric("cache_miss", 1, endpoint="generate")
        
        return GenerateOut(text=response_text)
    except HTTPException:
        raise
    except Exception as e:
        from backend.utils import log_error
        log_error(e, context={"endpoint": "generate", "question": q[:100]})
        raise HTTPException(status_code=500, detail=f"Error en generación simple: {str(e)}")













