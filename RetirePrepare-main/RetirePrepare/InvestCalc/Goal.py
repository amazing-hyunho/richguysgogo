import sys
import os

# 현재 파일의 상위 경로를 가져와 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from API import Common_API
from API import Goal_API


# 세션 초기화
Common_API.initialize_session()

st.header("📊 필요 자산 계산")
Goal_API.GetGoalInfo()
Goal_API.GetReqFund()

# # 대출 정보
# loan_principal = 500000000  # 대출 원금 5억 원
# annual_interest_rate = 0.04  # 연 이자율 4%
# loan_term_years = 40  # 대출 만기 40년
# payment_years = 20  # 20년 후 원금 계산

# # 월 이자율과 대출 기간 (개월 단위)
# monthly_interest_rate = annual_interest_rate / 12
# loan_term_months = loan_term_years * 12
# payment_months = payment_years * 12

# # 원리금 균등 상환 계산: 월 상환 금액 (M)
# monthly_payment = loan_principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_months) / ((1 + monthly_interest_rate) ** loan_term_months - 1)

# # 20년 후 원금 잔액 계산 (20년 동안 상환 후 남은 원금)
# remaining_principal = loan_principal * ((1 + monthly_interest_rate) ** loan_term_months - (1 + monthly_interest_rate) ** payment_months) / ((1 + monthly_interest_rate) ** loan_term_months - 1)

# # 결과 출력
# print(f"월 상환 금액: {monthly_payment:,.0f} 원")
# print(f"20년 후 남은 원금: {remaining_principal:,.0f} 원")