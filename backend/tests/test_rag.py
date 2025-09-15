# backend/test_rag.py
from backend.rag_pipeline import chatbot_teacher, chatbot_baseline

print("=== 🔍 PRUEBA RAG ===")

q = "Explica qué es la evaluación formativa"

print("\n--- BASELINE ---")
print(chatbot_baseline(q))

print("\n--- TEACHER RAG ---")
print(chatbot_teacher(q))
