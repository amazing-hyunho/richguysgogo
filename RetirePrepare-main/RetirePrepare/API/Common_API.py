import streamlit as st
import pandas as pd

# 세션 상태 초기화 함수
def initialize_session():
    if "goal_info" not in st.session_state:
        st.session_state.goal_info = {}
    if "invest_info" not in st.session_state:
        st.session_state.invest_info = {}
    if "account_info" not in st.session_state:
        st.session_state.account_info = {}

def Input(name, step, session_info, field, explain):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; height: 38px;">
            <b>{name}</b>
        </div>
        """,
        unsafe_allow_html=True)
    with col2:
        invest_amount = st.number_input("", step=float(step), value=session_info.get(field, None), placeholder=explain, label_visibility="collapsed", key = field)

    return invest_amount