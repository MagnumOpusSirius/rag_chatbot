import streamlit as st

def show_chat_interface(chat_callback):
    st.title("📚 Document Q&A Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask a question:")
    if user_input:
        response = chat_callback(user_input)
        st.session_state.chat_history.append((user_input, response))

    for user_q, bot_a in reversed(st.session_state.chat_history):
        st.markdown(f"**You:** {user_q}")
        st.markdown(f"**Assistant:** {bot_a}")