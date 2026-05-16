import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

#For Test

def GetExchangeRate():
    st.subheader("현재 환율 정보", divider="orange")
    account_info = st.session_state.account_info
    url = "https://finance.naver.com/marketindex/"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    account_info["exchange_rate"] = soup.select_one(".market1 .value").text
    st.info("미국USD : " + account_info["exchange_rate"] + "원")

    # 쉼표 제거 후 float 변환
    account_info["exchange_rate"] = float(account_info["exchange_rate"].replace(",", ""))

def GetAccountInfo():
    st.subheader("분석 계좌 정보 입력", divider="orange")
    account_info = st.session_state.account_info
    uploaded_file = st.file_uploader("", type=["xls", "xlsx"], label_visibility="collapsed")

    if uploaded_file is not None:
        # 엑셀 파일을 데이터프레임으로 변환
        df = pd.read_excel(uploaded_file).dropna()
        df.loc[(df["Unit"] == "달러"), "Amount"] *= account_info["exchange_rate"]
        account_info["data"] = df.drop("Unit", axis=1)

def Circlechart(df, Key):
    # 한글 폰트 적용
    plt.rc("font", family="Malgun Gothic")  # Windows (Mac은 AppleGothic)

    labels = df[Key]
    sizes = df["Amount"]
    colors = plt.cm.Paired.colors  # 색상 자동 지정

    # 도넛 차트 생성
    fig, ax = plt.subplots(figsize=(1.5,1.5))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors,
        wedgeprops={'edgecolor': 'white'}, pctdistance=0.75  # 퍼센트 숫자 위치 조정
    )

    # 텍스트 스타일 조정
    for text in texts:
        text.set_fontsize(4.5)  # 라벨 폰트 크기 조정
        text.set_fontweight("bold")
    for text in autotexts:
        text.set_fontsize(4.5)
        text.set_fontweight("bold")

    col1, col2, col3 = st.columns([1, 1.5, 1])  # 좌, 중앙, 우 컬럼 분할

    with col2:  # 중앙 컬럼에 차트 넣기
        st.pyplot(fig, use_container_width=False)

def AccountAnalysis_account():
    if "data" not in st.session_state["account_info"]:
        return

    df = st.session_state.account_info["data"]
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("일반 계좌 분석", divider="gray")
            df_norm = df[df["Account"] == "일반계좌"].groupby("Account_sub")["Amount"].sum().reset_index()
            df_norm["Amount"] = round(df_norm["Amount"], 0)
            Circlechart(df_norm, "Account_sub")

            df_norm.loc[len(df_norm)] = ["합계", df_norm["Amount"].sum()]
            st.dataframe(df_norm, use_container_width=True)
        with col2:
            st.subheader("연금 계좌 분석", divider="gray")
            df_pension = df[df["Account"] == "연금계좌"].groupby("Account_sub")["Amount"].sum().reset_index()
            df_pension["Amount"] = round(df_pension["Amount"], 0)
            Circlechart(df_pension, "Account_sub")

            df_pension.loc[len(df_pension)] = ["합계", df_pension["Amount"].sum()]
            st.dataframe(df_pension, use_container_width=True)
