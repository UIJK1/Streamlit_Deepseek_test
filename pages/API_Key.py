import streamlit as st

if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ''


st.set_page_config(page_title="小卢AI", page_icon="🤖", layout="wide")
st.title("AI Settings")
openai_api_key = st.text_input("API Key", value=st.session_state["OPENAI_API_KEY"],type="password")

saved = st.button("Save")
if saved:
    st.session_state["OPENAI_API_KEY"] = openai_api_key
    st.switch_page("pages/Chat.py")
