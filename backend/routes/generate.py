from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# RAG y prompts
from backend.rag_pipeline import chatbot_simple
from backend.prompt_baseline import BASELINE_SYSTEM_PROMPT

# Si no existe ENGINEERED, cae a BASELINE
try:
    from backend.prompt_baseline import ENGINEERED_SYSTEM_PROMPT
except Exception:
    ENGINEERED_SYSTEM_PROMPT = BASELINE_SYSTEM_PROMPT

router = APIRouter(tags=["generate"])


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
def generate_endpoint(inp: GenerateIn):
    """
    Chatbot simple (baseline / engineered) sin RAG.
    - Aquí el modelo puede alucinar, porque no está grounded en documentos.
    """
    q = (inp.text or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Falta 'text'")

    # Elegir prompt
    system_prompt = (
        BASELINE_SYSTEM_PROMPT if inp.mode.lower() == "baseline"
        else ENGINEERED_SYSTEM_PROMPT
    )

    try:
        answer = chatbot_simple(q, system_prompt)
        return GenerateOut(text=answer)
    except Exception:
        raise HTTPException(status_code=500, detail="Error en generación simple")













