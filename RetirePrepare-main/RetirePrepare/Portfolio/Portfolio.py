import sys
import os

# 현재 파일의 상위 경로를 가져와 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from API import Common_API
from API import Portfolio_API

# 세션 초기화
Common_API.initialize_session()

st.header("📊 계좌 분석")
Portfolio_API.GetExchangeRate()
Portfolio_API.GetAccountInfo()

st.subheader("🍩 계좌 비중 분석", divider="orange")
Portfolio_API.AccountAnalysis_account()