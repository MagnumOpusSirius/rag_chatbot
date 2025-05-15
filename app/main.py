from rag_pipeline import rag_chat_response
from chat_memory import add_to_history

def main():
    print("💬 Ask a question about your application (type 'exit' to quit):\n")
    while True:
        user_query = input("You: ")
        if user_query.lower() in ['exit', 'quit']:
            break

        response = rag_chat_response(user_query)
        add_to_history(user_query, response)

        print(f"\n🤖 Bot: {response}\n")

if __name__ == "__main__":
    main()