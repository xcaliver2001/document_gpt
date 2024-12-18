import time
import streamlit as st

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃",
)

st.title("DocumentGPT")

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.write(message)
    if save:
        st.session_state["messages"].append({"message": message, "role": role})


for message in st.session_state["messages"]:
    send_message(
        message["message"],
        message["role"],
        save=False,
    )

with st.chat_message("user"):
    st.write("assistant: Hello, how can I help you today?")
message = st.chat_input("Send a message to the ai ")

with st.status("Embedding your message...", expanded=True) as status :
    time.sleep(1)
    st.write("Reading your message...")
    time.sleep(1)
    st.write("Embedding your message...")
    time.sleep(1)
    status.update(label = "Embedded your message", state = "complete")


if message:
    send_message(message, "human")
    time.sleep(2)
    send_message(f"You said: {message}", "ai")

    with st.sidebar:
        st.write(st.session_state)