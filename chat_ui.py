import streamlit as st
import requests

st.title("UniMate Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask UniMate...")

if user_input:
    st.session_state.messages.append(("user", user_input))

    r = requests.post(
        "http://127.0.0.1:8000/chat",
        json={"message": user_input}
    )

    reply = r.json()

    st.session_state.messages.append(("bot", str(reply)))

for role, msg in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)