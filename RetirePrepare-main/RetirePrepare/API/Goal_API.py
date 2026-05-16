import streamlit as st
from API import Common_API

# 필요 자산 입력 함수
def GetGoalInfo():
    st.subheader("필요 자산 입력", divider="orange")

    # 세션 상태 데이터 불러오기
    goal_info = st.session_state.goal_info

    goal_info["Goal_Age"] = Common_API.Input("현재 나이", 1, goal_info, "Goal_Age", "만 나이를 입력하세요.")
    goal_info["MonthExpense"] = Common_API.Input("예상 월 생활비", 1, goal_info, "MonthExpense", "만 55세 이후 예상 월 생활비를 현재 물가로 입력하세요. (단위:만원)")
    goal_info["InvestRate"] = Common_API.Input("예상 수익률", 0.1, goal_info, "InvestRate", "만 55세 이후 예상 수익률을 입력하세요. (0~100%)")
    goal_info["InflationRate"] = Common_API.Input("예상 물가 상승률", 0.1, goal_info, "InflationRate", "만 55세 이후 예상 물가 상승률을 입력하세요. (0~100%)")
    goal_info["NationalPension"] = Common_API.Input("국민 연금 월 수령액", 1, goal_info, "NationalPension", "예상 국민연금 수령액을 입력하세요. (단위:만원)")

    if st.button("계산"):
        st.session_state.goal_info = goal_info

# 필요 자산 계산 함수
def GetReqFund():
    goal_info = st.session_state.goal_info

    if not goal_info or any(v is None for v in goal_info.values()):
        st.warning("모든 정보를 입력해야 합니다.")
        return

    # 생활비 사용 기간 (35년)
    RetireAge = 55
    LifeExpect = 90
    goal_info["RemainRetireYear"] = max(RetireAge - goal_info["Goal_Age"], 0)
    goal_info["RemainLifeYear"] = max(LifeExpect - goal_info["Goal_Age"], 0)

    # 35년 동안 사용할 총 금액 산출
    TotalReqFund = 0
    Age = RetireAge
    for year in range(int(goal_info["RemainRetireYear"]), int(goal_info["RemainLifeYear"]), 1):
        Age += 1
        NationalPension = goal_info["NationalPension"] * 12 if Age >= 65 else 0
        YearExpense = ((goal_info["MonthExpense"] * 12) * (1 + goal_info["InflationRate"] / 100) ** year - NationalPension) / (1 + goal_info["InvestRate"] / 100) ** (year - goal_info["RemainRetireYear"])
        TotalReqFund += YearExpense

    goal_info["TotalReqFund"] = TotalReqFund
    st.success(f"{RetireAge} 세에 필요한 총 유동 자산(국민 연금 반영) : {TotalReqFund:,.2f} 만원")