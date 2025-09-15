# backend/test_llm.py
import os
from dotenv import load_dotenv

from backend.llm_loader import get_chat_llm, get_embeddings

# Cargar variables de entorno
load_dotenv()

print("=== 🔍 PRUEBA LLM & EMBEDDINGS ===")

# Verifica API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ Falta definir OPENAI_API_KEY en .env")

# 1. Probar ChatOpenAI
print("\n--- ChatOpenAI ---")
llm = get_chat_llm()
resp = llm.invoke("Hola Zoltar, ¿puedes confirmarme que estás vivo?")
print("Respuesta del modelo:", resp.content if hasattr(resp, "content") else resp)

# 2. Probar Embeddings
print("\n--- Embeddings ---")
emb = get_embeddings()
vec = emb.embed_query("Inteligencia artificial en educación")
print("Dimensión del embedding:", len(vec))
print("Primeros 10 valores:", vec[:10])
