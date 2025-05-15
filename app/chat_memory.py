chat_history = []

def add_to_history(user_query: str, bot_response: str):
    chat_history.append({
        "user": user_query,
        "bot": bot_response
    })

def get_history():
    return chat_history[-5:]  # Return last 5 exchanges (or customize)