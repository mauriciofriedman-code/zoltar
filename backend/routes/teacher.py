# backend/routes/teacher.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

# Import correcto desde backend
from backend.rag_pipeline import chatbot_teacher

# Utilidades
from backend.utils import (
    get_cached_response,
    set_cached_response,
    sanitize_text,
    validate_input,
    logger,
    log_metric
)

router = APIRouter(tags=["teacher"])
limiter = Limiter(key_func=get_remote_address)


# ==== Esquemas ====
class TeacherIn(BaseModel):
    text: str = Field(..., min_length=1, description="Consulta del usuario")
    history: Optional[str] = Field(
        default=None,
        description="Historial breve opcional para dar continuidad al docente"
    )


class TeacherOut(BaseModel):
    text: str
    sources: List[str] = []   # 🔥 nuevo campo para referencias


# ==== Endpoint ====
@router.post("/teacher", response_model=TeacherOut)
@limiter.limit("15/minute")  # Rate limiting: 15 requests por minuto (RAG es más costoso)
def teacher_endpoint(request: Request, inp: TeacherIn):
    """
    Oráculo Docente (RAG):
    - Usa retrieval mejorado (MMR / formateo enumerado) y fallback honesto.
    - history es opcional; si viene, se inyecta al prompt docente.
    - Devuelve tanto la respuesta como la lista de fuentes consultadas.
    
    **Rate Limit**: 15 requests por minuto por IP
    """
    import time
    start_time = time.time()
    
    # Sanitizar y validar entrada
    q = sanitize_text(inp.text or "", max_length=2000)
    
    is_valid, error_msg = validate_input(q, min_length=3, max_length=2000)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Validar historial si existe
    history = sanitize_text(inp.history or "", max_length=5000) if inp.history else ""
    if history and len(history) > 5000:
        raise HTTPException(status_code=400, detail="El historial es demasiado largo (máx. 5000 caracteres)")

    # Verificar caché
    cached_response = get_cached_response(q, "rag", rag=True, history=history)
    if cached_response:
        logger.info(f"Cache hit for teacher endpoint: {q[:50]}...")
        log_metric("cache_hit", 1, endpoint="teacher")
        return TeacherOut(
            text=cached_response.get("text", ""),
            sources=cached_response.get("sources", [])
        )

    try:
        answer_dict = chatbot_teacher(question=q, history=history)
        response_text = answer_dict.get("text", "⚠️ Respuesta vacía")
        sources = answer_dict.get("sources", [])
        
        # Validar que la respuesta no esté vacía
        if not response_text or len(response_text.strip()) == 0:
            response_text = "Lo siento, no pude generar una respuesta basada en los documentos. Por favor, intenta reformular tu pregunta."
        
        # Almacenar en caché
        response_dict = {"text": response_text, "sources": sources}
        set_cached_response(q, "rag", response_dict, rag=True, history=history)
        
        # Log métricas
        duration = (time.time() - start_time) * 1000
        log_metric("teacher_duration_ms", duration)
        log_metric("cache_miss", 1, endpoint="teacher")
        
        return TeacherOut(
            text=response_text,
            sources=sources if isinstance(sources, list) else [],
        )
    except HTTPException:
        raise
    except Exception as e:
        from backend.utils import log_error
        log_error(e, context={"endpoint": "teacher", "question": q[:100]})
        raise HTTPException(status_code=500, detail=f"Error en RAG: {str(e)}")













