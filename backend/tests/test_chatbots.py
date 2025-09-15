# backend/test_chatbots.py
from backend.rag_pipeline import chatbot_baseline, chatbot_teacher

def main():
    question = "¿Cuál es el aporte principal de estos artículos académicos?"

    print("\n--- Chatbot Baseline ---")
    print(chatbot_baseline(question))

    print("\n--- Chatbot Teacher ---")
    print(chatbot_teacher(question))

if __name__ == "__main__":
    main()

