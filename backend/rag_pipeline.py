# backend/rag_pipeline.py
from typing import List, Any
from backend.llm_loader import get_chat_llm
from backend.retrieve import get_retriever
from backend.prompt_baseline import BASELINE_SYSTEM_PROMPT
from backend.prompt_teacher import build_teacher_prompt


def safe_response(llm, messages):
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


def _contexts_to_text(
    contexts: List[Any],
    enumerate_blocks: bool = True,
    max_chars_total: int = 3500,
    max_chars_per_block: int = 1000,
) -> str:
    """
    Convierte documentos recuperados en texto compacto y ordenado.
    Incluye doc_id, título, autores, página y fuente para dar contexto real.
    """
    parts, total = [], 0

    for i, c in enumerate(contexts, start=1):
        md = getattr(c, "metadata", {}) or {}
        doc_id = md.get("doc_id", "Desconocido")
        title = md.get("title", "Documento sin título")
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

    return "\n\n".join(parts).strip()


FALLBACK_NO_CONTEXT = (
    "Soy tu tutor con RAG. No encontré fragmentos relevantes en los documentos para responder tu consulta.\n\n"
    "Sugerencias para mejorar la búsqueda:\n"
    "- Sé más específico con autores, títulos o temas.\n"
    "- Indica el tipo de documento (artículo, reporte, guía).\n"
    "- Divide tu pregunta en partes más concretas.\n\n"
    "Importante: este modo responde únicamente con base en los documentos cargados."
)


def answer_with_rag(question: str, system_prompt: str = "", k: int = 5, allow_fallback: bool = True) -> str:
    llm = get_chat_llm()

    try:
        retriever = get_retriever(k=k)
        contexts = retriever.invoke(question) or []
    except Exception:
        if not allow_fallback:
            return "No se pudo recuperar información desde el índice."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{FALLBACK_NO_CONTEXT}\n\nPregunta: {question}"},
        ]
        return safe_response(llm, messages)

    if not contexts:
        if not allow_fallback:
            return "No encontré información suficiente en los documentos."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{FALLBACK_NO_CONTEXT}\n\nPregunta: {question}"},
        ]
        return safe_response(llm, messages)

    context_text = _contexts_to_text(contexts, enumerate_blocks=True)

    # 🔑 Prompt pedagógico optimizado
    system_prompt = system_prompt or (
        "Eres un maestro experto en educación y judaísmo. "
        "Tu tarea es responder de manera clara, pedagógica y aplicada al aula, "
        "usando exclusivamente el contexto de los documentos. "
        "No digas 'los documentos dicen', responde directamente como si enseñaras a un estudiante. "
        "Incluye ejemplos educativos o prácticos cuando sea posible. "
        "Si falta información, acláralo y sugiere cómo podría investigarse más."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Pregunta: {question}\n\nContexto disponible:\n{context_text}"},
    ]

    # Debug opcional
    print("=== CONTEXTO RECUPERADO ===")
    print(context_text)
    print("===========================")

    return safe_response(llm, messages)


def chatbot_baseline(question: str) -> str:
    return answer_with_rag(question, BASELINE_SYSTEM_PROMPT, k=5, allow_fallback=False)


def chatbot_teacher(question: str, history: str = "", k: int = 6) -> str:
    llm = get_chat_llm()
    try:
        retriever = get_retriever(k=k)
        contexts = retriever.invoke(question) or []
    except Exception:
        return FALLBACK_NO_CONTEXT

    if not contexts:
        return FALLBACK_NO_CONTEXT

    context_text = _contexts_to_text(contexts, enumerate_blocks=True)
    teacher_prompt = build_teacher_prompt(
        context=context_text,
        user_message=question,
        history=history,
    )
    messages = [{"role": "user", "content": teacher_prompt}]
    return safe_response(llm, messages)


def chatbot_simple(question: str, system_prompt: str) -> str:
    llm = get_chat_llm()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    return safe_response(llm, messages)

























