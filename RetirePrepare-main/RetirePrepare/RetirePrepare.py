import streamlit as st
from API import Common_API

st.set_page_config(layout = "wide")

# 세션 초기화
Common_API.initialize_session()

pages = {
    "자산 계산(만 55세 은퇴)" : [
        st.Page("./InvestCalc/Goal.py", title = "📊 필요 자산 계산"),
        st.Page("./InvestCalc/Fund.py", title = "📈 은퇴 시점 예상 투자 자산")
        ],
    "자산 분석" : [
        st.Page("./Portfolio/Portfolio.py", title = "📊 계좌 분석")
    ]
}

pg = st.navigation(pages)
pg.run()