import sys
import os

# 현재 파일의 상위 경로를 가져와 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from API import Common_API
from API import Fund_API

# 세션 초기화
Common_API.initialize_session()

st.header("📈 은퇴 시점 예상 투자 자산")
Fund_API.GetInvestInfo()
Fund_API.GetExpectInvest()