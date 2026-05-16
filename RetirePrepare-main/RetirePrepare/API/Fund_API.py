import streamlit as st
import pandas as pd
from API import Common_API

# 투자 정보 입력 함수
def GetInvestInfo():
    st.subheader("투자 정보 입력", divider="orange")

    invest_info = st.session_state.invest_info

    invest_info["Fund_Age"] = Common_API.Input("현재 나이", 1, invest_info, "Fund_Age", "만 나이를 입력하세요.")
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("투자 정보(연금 제외)", divider="gray")
            invest_info["Seed"] = Common_API.Input("초기 자금", 1, invest_info, "Seed", "(단위:만원)")
            invest_info["YearIncome"] = Common_API.Input("연 추가 납입액", 1, invest_info, "YearIncome", "(단위:만원)")
            invest_info["YearInvestRate"] = Common_API.Input("예상 수익률", 0.1, invest_info, "YearInvestRate", "(0~100%)")
        with col2:
            st.subheader("개인 연금", divider="gray")
            invest_info["PersonalPensionSeed"] = Common_API.Input("현재 자금", 1, invest_info, "PersonalPensionSeed", "(단위:만원)")
            invest_info["YearPersonalPension"] = Common_API.Input("연 추가 납입액", 1, invest_info, "YearPersonalPension", "(단위:만원)")
            invest_info["YearPensionRate"] = Common_API.Input("예상 수익률", 0.1, invest_info, "YearPensionRate", "(0~100%)")
        with col3:
            st.subheader("IRP", divider="gray")
            invest_info["IRPSeed"] = Common_API.Input("현재 자금", 1, invest_info, "IRPSeed", "(단위:만원)")
            invest_info["YearIRP"] = Common_API.Input("연 추가 납입액", 1, invest_info, "YearIRP", "(단위:만원)")
            invest_info["YearIRPRate"] = Common_API.Input("예상 수익률", 0.1, invest_info, "YearIRPRate", "(0~100%)")

    if st.button("계산"):
        st.session_state.invest_info = invest_info

# 투자 자산 예상 계산 함수
def GetExpectInvest():
    invest_info = st.session_state.invest_info

    if not invest_info or any(v is None for v in invest_info.values()):
        st.warning("모든 정보를 입력해야 합니다.")
        return

    df = pd.DataFrame()
    RetireAge = 55
    Duration = int(RetireAge - invest_info["Fund_Age"])

    df.loc[0, "Invest"] = invest_info["Seed"]
    df.loc[0, "PersonalPension"] = invest_info["PersonalPensionSeed"]
    df.loc[0, "IRP"] = invest_info["IRPSeed"]
    df.loc[0, "Total"] = round(df.loc[0, "Invest"] + df.loc[0, "PersonalPension"] + df.loc[0, "IRP"], 2)

    for year in range(1, Duration, 1):
        df.loc[year, "Invest"] = round((df.loc[year - 1, "Invest"] + invest_info["YearIncome"]) * (1 + round(invest_info["YearInvestRate"]/100, 3)), 2)
        df.loc[year, "PersonalPension"] = round((df.loc[(year - 1), "PersonalPension"] + invest_info["YearPersonalPension"]) * (1 + round(invest_info["YearPensionRate"]/100, 3)), 2)
        df.loc[year, "IRP"] = round((df.loc[(year - 1), "IRP"] + invest_info["YearIRP"]) * (1 + round(invest_info["YearIRPRate"]/100, 3)), 2)
        df.loc[year, "Total"] = round(df.loc[year, "Invest"] + df.loc[year, "PersonalPension"] + df.loc[year, "IRP"], 2)

    st.dataframe(df, use_container_width=True)
    st.success(f"55세 예상 투자 자산은 {df.loc[max(Duration - 1, 0), 'Total']:,.2f}만원")
    st.write(f"- 연금 외 투자 : {df.loc[max(Duration - 1, 0), "Invest"]:,.2f}만원")
    st.write(f"- 개인연금 : {df.loc[max(Duration - 1, 0), "PersonalPension"]:,.2f}만원")
    st.write(f"- IRP : {df.loc[max(Duration - 1, 0), "IRP"]:,.2f}만원")