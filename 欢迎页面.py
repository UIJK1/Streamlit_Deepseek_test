import streamlit as st
from openai import OpenAI
chat = None
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ""
elif st.session_state["OPENAI_API_KEY"] != "":
    chat = OpenAI(
        api_key=st.session_state["OPENAI_API_KEY"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
if "message" not in st.session_state:
    st.session_state.message = []  # 存储聊天记录

st.set_page_config(page_title="欢迎", page_icon="🤖", layout="wide")
st.title("欢迎使用小卢AI")
with st.container():
        st.warning("请在API Key设置页面输入API Key")
        start = st.button("点击开始")
        if start:
            st.switch_page("pages/API_Key.py")
