# backend/rag_pipeline.py
from typing import List, Any, Tuple, Dict
from backend.llm_loader import get_chat_llm
from backend.retrieve import get_retriever
from backend.prompt_baseline import BASELINE_SYSTEM_PROMPT
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
    Convierte documentos recuperados en texto compacto y ordenado.
    Devuelve: (texto_contexto, lista_de_fuentes).
    """
    parts, total = [], 0
    sources: List[str] = []

    for i, c in enumerate(contexts, start=1):
        md = getattr(c, "metadata", {}) or {}
        doc_id = md.get("doc_id", "Desconocido")
        title = md.get("title", md.get("source", "Documento sin título"))
        authors = md.get("authors", "Autores desconocidos")
        page = md.get("page", "N/A")
        source = md.get("source", "Fuente desconocida")

        block_txt = getattr(c, "page_content", "") or ""
        if len(block_txt) > max_chars_per_block:
            block_txt = block_txt[:max_chars_per_block].rsplit(" ", 1)[0] + "…"

        header = (
            f"Documento ID: {doc_id}\n"
            f"Título: {title}\n"
            f"Autores: {authors}\n"
            f"Página: {page}\n"
            f"Fuente: {source}"
        )

        if enumerate_blocks:
            body = f"[{i}]\n{header}\nContenido:\n{block_txt}"
        else:
            body = f"{header}\nContenido:\n{block_txt}"

        if total + len(body) > max_chars_total:
            remaining = max_chars_total - total
            if remaining <= 0:
                break
            body = body[:remaining].rsplit(" ", 1)[0] + "…"
            parts.append(body)
            break

        parts.append(body)
        total += len(body)

        # Guardar fuente simplificada para devolver al frontend
        ref = f"{title} (p.{page})"
        if ref not in sources:
            sources.append(ref)

    return "\n\n".join(parts).strip(), sources


FALLBACK_NO_CONTEXT = (
    "Soy tu tutor con RAG. No encontré fragmentos relevantes en los documentos.\n\n"
    "👉 Intenta mejorar tu búsqueda:\n"
    "- Sé más específico (ejemplo: en lugar de 'Pesaj', pregunta '¿qué simboliza el Seder de Pesaj?').\n"
    "- Usa autores o títulos si los conoces.\n"
    "- Divide tu consulta en pasos más concretos.\n\n"
    "Importante: respondo únicamente en base a los documentos cargados."
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
    - sources: lista de referencias extraídas
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
        if not allow_fallback:
            return {"text": "No encontré información suficiente en los documentos.", "sources": []}
        return {"text": FALLBACK_NO_CONTEXT, "sources": []}

    context_text, sources = _contexts_to_text_and_sources(contexts, enumerate_blocks=True)

    # 🔑 Prompt pedagógico optimizado
    system_prompt = system_prompt or (
        "Eres un maestro experto en educación y judaísmo. "
        "Responde de manera clara, pedagógica y aplicada al aula. "
        "Usa exclusivamente el contexto proporcionado. "
        "No digas 'los documentos dicen'; responde como docente. "
        "Incluye ejemplos prácticos o educativos cuando sea posible. "
        "Si falta información, acláralo y sugiere cómo investigar más."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Pregunta: {question}\n\nContexto:\n{context_text}"},
    ]

    print("=== CONTEXTO RECUPERADO ===")
    print(context_text)
    print("===========================")

    answer = safe_response(llm, messages)
    return {"text": answer, "sources": sources}


def chatbot_baseline(question: str) -> Dict:
    return answer_with_rag(question, BASELINE_SYSTEM_PROMPT, k=5, allow_fallback=False)


def chatbot_teacher(question: str, history: str = "", k: int = 6) -> Dict:
    """
    Devuelve dict con text + sources.
    """
    llm = get_chat_llm()
    try:
        retriever = get_retriever(k=k)
        contexts = retriever.invoke(question) or []
    except Exception:
        return {"text": FALLBACK_NO_CONTEXT, "sources": []}

    if not contexts:
        return {"text": FALLBACK_NO_CONTEXT, "sources": []}

    context_text, sources = _contexts_to_text_and_sources(contexts, enumerate_blocks=True)

    teacher_system = (
        "Eres un maestro experto en educación y judaísmo. "
        "Debes responder con profundidad pedagógica y ejemplos prácticos."
    )
    teacher_prompt = build_teacher_prompt(
        context=context_text,
        user_message=question,
        history=history,
    )

    messages = [
        {"role": "system", "content": teacher_system},
        {"role": "user", "content": teacher_prompt},
    ]

    answer = safe_response(llm, messages)
    return {"text": answer, "sources": sources}


def chatbot_simple(question: str, system_prompt: str) -> Dict:
    llm = get_chat_llm()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    answer = safe_response(llm, messages)
    return {"text": answer, "sources": []}

























