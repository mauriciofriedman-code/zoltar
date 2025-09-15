# backend/test_retrieve.py
from backend.retrieve import get_retriever

def main():
    retriever = get_retriever(k=3)
    docs = retriever.invoke("¿Cuál es el tema principal de los artículos?")

    print(f"Se encontraron {len(docs)} documentos relevantes:")
    for d in docs:
        print("-", d.metadata.get("source"), "|", d.page_content[:100], "...")

