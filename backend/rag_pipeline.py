# backend/rag_pipeline.py

from typing import List, Dict, Any, Tuple
from backend.llm_loader import get_chat_llm
from backend.retrieve import get_retriever
from backend.prompt_teacher import build_teacher_prompt


def safe_response(llm, messages: List[Dict]) -> str:
    """Envuelve la invocación al LLM y devuelve siempre texto plano."""
    try:
        response = llm.invoke(messages)
        if hasattr(response, "content"):
            return response.content
        if isinstance(response, dict) and "content" in response:
            return response["content"]
        return str(response)
    except Exception as e:
        print(f"[safe_response] Error: {e}")
        return f"Error al generar respuesta: {e}"


def _contexts_to_text_and_sources(
    contexts: List[Any],
    enumerate_blocks: bool = True,
    max_chars_total: int = 6000,
    max_chars_per_block: int = 1200,
) -> Tuple[str, List[str]]:
    """
    Convierte documentos recuperados en texto enumerado + lista de referencias.
    """
    parts, total = [], 0
    sources: List[str] = []

    for i, c in enumerate(contexts, start=1):
        md = getattr(c, "metadata", {}) or {}
        doc_id = md.get("doc_id", "N/A")
        title = md.get("title", md.get("source", "Desconocido"))
        authors = md.get("authors", "Autores desconocidos")
        page = md.get("page", "N/A")
        source = md.get("source", "Fuente desconocida")

        block_txt = getattr(c, "page_content", "") or ""
        if len(block_txt) > max_chars_per_block:
            block_txt = block_txt[:max_chars_per_block].rsplit(" ", 1)[0] + "…"

        header = (
            f"Título: {title}\n"
            f"Autores: {authors}\n"
            f"Página: {page}\n"
            f"Fuente: {source}"
        )

        if enumerate_blocks:
            body = f"[{i}] {header}\nContenido:\n{block_txt}"
        else:
            body = f"{header}\nContenido:\n{block_txt}"

        if total + len(body) > max_chars_total:
            break

        parts.append(body)
        total += len(body)

        ref = f"{title} (p.{page})"
        if ref not in sources:
            sources.append(ref)

    return "\n\n".join(parts).strip(), sources


FALLBACK_NO_CONTEXT = (
    "Soy un asistente educativo con acceso a documentos. "
    "No encontré fragmentos relevantes para tu consulta.\n\n"
    "👉 Puedes intentar con preguntas más específicas como:\n"
    "- '¿Cómo se puede usar la IA en evaluación formativa?'\n"
    "- 'Ventajas de los chatbots educativos en secundaria'\n\n"
    "Mis respuestas se basan exclusivamente en los documentos cargados."
)


def answer_with_rag(
    question: str,
    system_prompt: str = "",
    k: int = 5,
    allow_fallback: bool = True
) -> Dict:
    """
    Devuelve un dict con:
    - text: respuesta del modelo
    - sources: lista de referencias citadas
    """
    llm = get_chat_llm()

    try:
        retriever = get_retriever(k=k)
        contexts = retriever.invoke(question) or []
    except Exception:
        if not allow_fallback:
            return {"text": "No se pudo recuperar información desde el índice.", "sources": []}
        return {"text": FALLBACK_NO_CONTEXT, "sources": []}

    if not contexts:
        return {"text": FALLBACK_NO_CONTEXT, "sources": []}

    context_text, sources = _contexts_to_text_and_sources(contexts)

    prompt = (
        system_prompt or
        "Eres un experto en tecnología educativa.\n"
        "Responde preguntas sobre el uso de la inteligencia artificial y la generación artificial (GenIA) en educación.\n"
        "Usa solamente la información proporcionada en el contexto.\n"
        "No inventes ni rellenes con conocimiento externo."
    )

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Contexto:\n{context_text}\n\nPregunta:\n{question}"}
    ]

    answer = safe_response(llm, messages)

    return {"text": answer.strip(), "sources": sources}


def chatbot_simple(conversation: List[Dict], system_prompt: str = "") -> Dict:
    """
    Chat directo sin retrieval, solo con historial + system_prompt.
    """
    llm = get_chat_llm()
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.extend(conversation)
    answer = safe_response(llm, messages)

    return {"text": answer.strip(), "sources": []}


def chatbot_teacher(question: str, history: str = "") -> Dict:
    """
    Chat para docentes, usando prompt especial + history si aplica.
    """
    system_prompt = build_teacher_prompt(history.strip() if history else "")
    return answer_with_rag(question=question, system_prompt=system_prompt)


























