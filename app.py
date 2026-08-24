# app.py
import streamlit as st
from agent import ask

st.set_page_config(page_title="Trợ lý AI Nông nghiệp Rau củ", page_icon="🥬")
st.title("🥬 Trợ lý AI Nông nghiệp Rau củ")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Hỏi về cây trồng, bệnh, kỹ thuật canh tác..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu..."):
            answer = ask(question)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})