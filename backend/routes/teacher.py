# backend/routes/teacher.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# Import correcto desde backend
from backend.rag_pipeline import chatbot_teacher

router = APIRouter(tags=["teacher"])


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
def teacher_endpoint(inp: TeacherIn):
    """
    Oráculo Docente (RAG):
    - Usa retrieval mejorado (MMR / formateo enumerado) y fallback honesto.
    - history es opcional; si viene, se inyecta al prompt docente.
    - Devuelve tanto la respuesta como la lista de fuentes consultadas.
    """
    q = (inp.text or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Falta 'text'")

    try:
        answer_dict = chatbot_teacher(question=q, history=inp.history or "")
        return TeacherOut(
            text=answer_dict.get("text", "⚠️ Respuesta vacía"),
            sources=answer_dict.get("sources", []),
        )
    except Exception as e:
        # Log interno para debug
        print(f"[teacher] Error interno: {e}")
        raise HTTPException(status_code=500, detail="Error en RAG")













