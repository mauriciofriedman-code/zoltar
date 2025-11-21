"""
Endpoint para streaming de respuestas usando Server-Sent Events (SSE).
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional
import json
import asyncio

# RAG y prompts
from backend.rag_pipeline import chatbot_simple, chatbot_teacher
from backend.prompt_baseline import BASELINE_SYSTEM_PROMPT

# Utilidades
from backend.utils import (
    sanitize_text,
    validate_input,
    logger,
    log_metric
)

try:
    from backend.prompt_baseline import ENGINEERED_SYSTEM_PROMPT
except Exception:
    ENGINEERED_SYSTEM_PROMPT = BASELINE_SYSTEM_PROMPT

router = APIRouter(tags=["stream"])
limiter = Limiter(key_func=get_remote_address)


class StreamIn(BaseModel):
    text: str = Field(..., min_length=1, description="Consulta del usuario")
    mode: str = Field(default="engineered", description='Modo: "baseline", "engineered", o "rag"')
    history: Optional[str] = Field(default=None, description="Historial opcional para modo RAG")


async def stream_llm_response(text: str, system_prompt: str, is_rag: bool = False, history: str = ""):
    """
    Genera respuesta del LLM y la envía como stream.
    """
    from backend.llm_loader import get_chat_llm
    from backend.rag_pipeline import answer_with_rag
    
    llm = get_chat_llm()
    
    if is_rag:
        from backend.retrieve import get_retriever
        from backend.rag_pipeline import _contexts_to_text_and_sources
        from backend.prompt_teacher import build_teacher_prompt
        
        retriever = get_retriever(k=5)
        contexts = retriever.invoke(text) or []
        
        if not contexts:
            yield f"data: {json.dumps({'type': 'error', 'content': 'No se encontraron documentos relevantes.'})}\n\n"
            return
        
        context_text, sources = _contexts_to_text_and_sources(contexts)
        system_prompt = build_teacher_prompt(context_text, text, history)
        
        # Enviar fuentes primero
        yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contexto:\n{context_text}\n\nPregunta:\n{text}"}
        ]
    else:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    
    # Stream de respuesta
    try:
        # Usar astream para streaming
        async for chunk in llm.astream(messages):
            if hasattr(chunk, "content") and chunk.content:
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.content})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    except Exception as e:
        logger.error(f"Error en streaming: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@router.post("/stream")
@limiter.limit("10/minute")  # Rate limiting más estricto para streaming
async def stream_endpoint(request: Request, inp: StreamIn):
    """
    Endpoint de streaming de respuestas usando Server-Sent Events (SSE).
    
    **Rate Limit**: 10 requests por minuto por IP
    
    **Formato de eventos**:
    - `chunk`: Fragmento de texto de la respuesta
    - `sources`: Lista de fuentes (solo modo RAG)
    - `done`: Indica que la respuesta está completa
    - `error`: Error en la generación
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
    is_rag = mode == "rag"
    
    if not is_rag:
        if mode not in ["baseline", "engineered"]:
            mode = "engineered"
        system_prompt = (
            BASELINE_SYSTEM_PROMPT if mode == "baseline"
            else ENGINEERED_SYSTEM_PROMPT
        )
        history_str = ""
    else:
        system_prompt = ""  # Se construye en stream_llm_response
        history_str = sanitize_text(inp.history or "", max_length=5000) if inp.history else ""
    
    async def generate():
        try:
            async for chunk in stream_llm_response(q, system_prompt, is_rag, history_str):
                yield chunk
            
            # Log métricas
            duration = (time.time() - start_time) * 1000
            log_metric("stream_duration_ms", duration, mode=mode)
        except Exception as e:
            from backend.utils import log_error
            log_error(e, context={"endpoint": "stream", "question": q[:100]})
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Deshabilitar buffering en nginx
        }
    )

