import streamlit as st
from API import Common_API

# 필요 자산 입력 함수
def GetGoalInfo():
    st.subheader("💰 은퇴 설계 파라미터 입력", divider="orange")

    # 세션 상태 초기화
    if "goal_info" not in st.session_state:
        st.session_state.goal_info = {
            "Goal_Age": 35,
            "Retire_Age": 55,
            "MonthExpense": 300,
            "InvestRate": 4.0,
            "InflationRate": 2.0,
            "NationalPension": 150,
            "ExtraIncome": 50  # 추가된 고정 수입 기본값
        }
    
    goal_info = st.session_state.goal_info

    # 입력 필드 구성 (레이아웃 최적화)
    col1, col2 = st.columns(2)
    with col1:
        goal_info["Goal_Age"] = Common_API.Input("현재 나이 (만)", 1, goal_info, "Goal_Age", "현재 본인의 만 나이")
        goal_info["Retire_Age"] = Common_API.Input("목표 은퇴 나이 (만)", 1, goal_info, "Retire_Age", "은퇴를 계획하는 나이")
    
    with col2:
        goal_info["MonthExpense"] = Common_API.Input("예상 월 생활비 (현재가)", 1, goal_info, "MonthExpense", "은퇴 후 필요한 월 생활비 (단위:만원)")
        goal_info["NationalPension"] = Common_API.Input("국민연금 월 수령액", 1, goal_info, "NationalPension", "65세부터 수령할 월 연금액 (단위:만원)")

    st.write("---")
    col3, col4 = st.columns(2)
    with col3:
        # [신규] 고정 수입 입력 항목
        goal_info["ExtraIncome"] = Common_API.Input("은퇴 후 기타 월 고정 수입", 1, goal_info, "ExtraIncome", "임대료, 개인연금 등 은퇴 직후부터 발생할 월 수입 (단위:만원)")
        goal_info["InvestRate"] = Common_API.Input("은퇴 후 예상 수익률 (%)", 0.1, goal_info, "InvestRate", "자산 운용 수익률")
    
    with col4:
        st.caption("※ 고정 수입도 물가상승률에 따라 매년 증액되는 것으로 계산됩니다.")
        goal_info["InflationRate"] = Common_API.Input("예상 물가 상승률 (%)", 0.1, goal_info, "InflationRate", "매년 예상되는 물가 상승률")

    if st.button("은퇴 자산 계산하기", type="primary"):
        st.session_state.goal_info = goal_info
        st.rerun()

# 필요 자산 계산 및 결과 출력 함수
def GetReqFund():
    goal_info = st.session_state.goal_info

    if not goal_info or any(v is None for v in goal_info.values()):
        st.warning("정보를 입력한 후 계산 버튼을 눌러주세요.")
        return

    CurrentAge = goal_info["Goal_Age"]
    RetireAge = goal_info["Retire_Age"]
    LifeExpect = 90
    
    if CurrentAge >= RetireAge:
        st.error("목표 은퇴 나이를 현재보다 높게 설정해주세요.")
        return

    # 1. 시점 계산
    YearsUntilRetire = RetireAge - CurrentAge
    RetireLifeSpan = LifeExpect - RetireAge 

    # 2. 은퇴 '첫 해' 기준 물가가 반영된 금액들 (현재가 -> 은퇴 시점가)
    # 생활비와 기타 고정 수입 모두 물가상승률을 적용하여 은퇴 시점 가치로 변환
    InitialYearExpenseAtRetire = (goal_info["MonthExpense"] * 12) * (1 + goal_info["InflationRate"] / 100) ** YearsUntilRetire
    InitialExtraIncomeAtRetire = (goal_info["ExtraIncome"] * 12) * (1 + goal_info["InflationRate"] / 100) ** YearsUntilRetire

    TotalReqFund = 0
    
    # 3. 은퇴 기간 루프 (i = 은퇴 후 경과 년수)
    for i in range(int(RetireLifeSpan)):
        TargetAge = RetireAge + i
        
        # 매년 물가상승률에 따라 '생활비'와 '고정수입'이 동일하게 증액됨
        YearlyExpense = InitialYearExpenseAtRetire * (1 + goal_info["InflationRate"] / 100) ** i
        YearlyExtraIncome = InitialExtraIncomeAtRetire * (1 + goal_info["InflationRate"] / 100) ** i
        
        # 국민연금 (65세 이상 수령)
        # 국가에서 주는 연금도 보통 물가상승분을 반영하지만, 여기서는 입력값 기준으로 계산
        NationalPension = goal_info["NationalPension"] * 12 if TargetAge >= 65 else 0
        
        # [실질 필요 금액] = 지출(생활비) - 수입(고정수입 + 국민연금)
        NetExpense = YearlyExpense - (YearlyExtraIncome + NationalPension)
        
        # 은퇴 시점 가치로 할인 (수익률 반영)
        PresentValueAtRetire = NetExpense / (1 + goal_info["InvestRate"] / 100) ** i
        
        TotalReqFund += PresentValueAtRetire

    # 결과 출력
    st.divider()
    st.subheader(f"📊 은퇴 분석 결과 ({RetireAge}세 은퇴 기준)")
    
    # 음수 결과 처리 (이미 자산이 충분하여 저축이 필요 없는 경우)
    DisplayFund = max(TotalReqFund, 0)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("은퇴 후 생활 기간", f"{int(RetireLifeSpan)}년")
    c2.metric("은퇴 첫해 월 필요액", f"{InitialYearExpenseAtRetire/12:,.0f}만원")
    c3.metric("최종 필요 자산", f"{DisplayFund:,.0f} 만원")

    if TotalReqFund <= 0:
        st.balloons()
        st.success("축하합니다! 설정하신 고정 수입과 연금만으로도 은퇴 생활이 가능합니다.")
    else:
        with st.expander("상세 계산 로직 안내"):
            st.write(f"""
            - **고정 수입 증액**: 입력하신 기타 수입({goal_info['ExtraIncome']}만원)도 물가상승률에 따라 매년 증가한다고 가정했습니다.
            - **은퇴 첫해**: {RetireAge}세 시점의 월 생활비는 물가상승으로 인해 약 {InitialYearExpenseAtRetire/12:,.0f}만원이 됩니다.
            - **순 지출액**: 매년 '생활비 - (기타수입 + 국민연금)'을 계산하여, 부족한 금액을 은퇴 시점의 목돈으로 환산하여 합산했습니다.
            """)