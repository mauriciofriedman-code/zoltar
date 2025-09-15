# backend/llm_loader.py
import os
from dotenv import load_dotenv
from backend.config import EMBEDDINGS_PROVIDER, CHAT_MODEL, CHAT_TEMPERATURE, EMBEDDINGS_MODEL

# Carga variables de entorno desde .env si existe
load_dotenv()


def get_chat_llm():
    """
    Devuelve el modelo de chat principal (OpenAI).
    Configurable desde config.py.
    Requiere la variable de entorno OPENAI_API_KEY.
    """
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("⚠️ Falta definir la variable de entorno OPENAI_API_KEY")

    return ChatOpenAI(
        model=CHAT_MODEL,
        temperature=CHAT_TEMPERATURE,
        openai_api_key=api_key
    )


def get_embeddings(provider: str = None):
    """
    Devuelve el proveedor de embeddings (Hugging Face o OpenAI),
    definido de manera centralizada en config.py
    """
    provider = provider or EMBEDDINGS_PROVIDER

    if provider == "hf":
        # Paquete moderno sin deprecations
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            encode_kwargs={"normalize_embeddings": True}
        )

    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("⚠️ Falta definir la variable de entorno OPENAI_API_KEY")
        return OpenAIEmbeddings(
            model=EMBEDDINGS_MODEL,
            openai_api_key=api_key
        )

    else:
        raise ValueError("EMBEDDINGS_PROVIDER debe ser 'hf' o 'openai'")


# 🚀 NUEVO: función generate para invocar rápido al LLM
def generate(prompt: str) -> str:
    """
    Ejecuta el modelo de chat con un prompt simple y devuelve la respuesta.
    """
    llm = get_chat_llm()
    try:
        response = llm.invoke(prompt)
        if hasattr(response, "content"):
            return response.content
        if isinstance(response, dict) and "content" in response:
            return response["content"]
        return str(response)
    except Exception as e:
        return f"⚠️ Error al generar respuesta: {e}"














