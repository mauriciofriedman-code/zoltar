from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from backend.rag_pipeline import answer_with_rag, chatbot_teacher
from backend.prompt_baseline import BASELINE_SYSTEM_PROMPT

# ENGINEERED opcional
try:
    from backend.prompt_baseline import ENGINEERED_SYSTEM_PROMPT
except Exception:
    ENGINEERED_SYSTEM_PROMPT = BASELINE_SYSTEM_PROMPT

router = APIRouter(tags=["answer"])


# =====================
# Models de request/resp
# =====================

class AnswerIn(BaseModel):
    text: str = Field(..., min_length=1, description="Consulta del usuario")
    rag: bool = Field(False, description="Si true, usa el oráculo docente (RAG)")
    mode: str = Field("engineered", description='Usado cuando rag=false. "baseline" o "engineered"')
    history: Optional[str] = Field(default=None, description="Historial breve opcional para el oráculo docente")
    top_k: Optional[int] = Field(default=None, ge=1, le=12, description="Override del número de pasajes a recuperar (k)")


class AnswerOut(BaseModel):
    text: str
    rag: bool
    mode: str


# ============
#   Endpoint
# ============

@router.post("/answer", response_model=AnswerOut)
def universal_answer(inp: AnswerIn):
    """
    Endpoint universal:
    - rag=true  -> Oráculo Docente (RAG) con historial opcional (sí hace fallback).
    - rag=false -> Modelo simple (baseline/engineered) con RAG detrás (sin fallback).
    """
    q = (inp.text or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Falta 'text'")

    k = int(inp.top_k) if inp.top_k else None

    if inp.rag:
        try:
            answer_dict = chatbot_teacher(
                question=q,
                history=inp.history or "",
                k=(k or 6)
            )
            return AnswerOut(
                text=answer_dict.get("text", "⚠️ Respuesta vacía"),
                rag=True,
                mode="teacher"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en RAG docente: {e}")

    # Modelo simple (sin fallback)
    try:
        mode = (inp.mode or "engineered").lower()
        system_prompt = BASELINE_SYSTEM_PROMPT if mode == "baseline" else ENGINEERED_SYSTEM_PROMPT

        answer_dict = answer_with_rag(
            question=q,
            system_prompt=system_prompt,
            k=(k or 5),
            allow_fallback=False
        )
        return AnswerOut(
            text=answer_dict.get("text", "⚠️ Respuesta vacía"),
            rag=False,
            mode="baseline" if mode == "baseline" else "engineered"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en modelo simple: {e}")










