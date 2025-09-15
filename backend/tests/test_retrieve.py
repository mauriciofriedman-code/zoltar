# backend/test_retrieve.py
from routes.retrieve import get_retriever

def main():
    retriever = get_retriever(k=3)
    # API moderna: invoke en vez de get_relevant_documents
    docs = retriever.invoke("¿Cuál es el tema principal de los artículos?")

    print(f"Se encontraron {len(docs)} documentos relevantes:")
    for d in docs:
        print("-", d.metadata.get("source"), "|", d.page_content[:100], "...")

if __name__ == "__main__":
    main()

