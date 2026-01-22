import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI 부동산 분석", page_icon="🏗️", layout="wide")

# 2. API 연결 설정 (최신 규격 강제 적용)
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if api_key:
        # [핵심] 최신 v1 규격을 명시적으로 설정합니다.
        genai.configure(api_key=api_key.strip(), transport='rest') 
    else:
        st.error("⚠️ Secrets에 API 키가 없습니다.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ 연결 설정 오류: {e}")
    st.stop()

# 3. 분석 함수
def run_ai_analysis(address):
    try:
        # 가장 안정적인 최신 모델명 사용
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        prompt = f"부동산 전문가로서 다음 주소의 토지 개발 전략을 분석해줘: {address}"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # 에러 발생 시 구체적인 원인 출력
        return f"❌ 분석 중 오류 발생: {str(e)}\n\n(참고: API 활성화 여부와 키가 'jisang-ai' 프로젝트 것인지 확인 필요)"

# 4. 메인 UI
st.title("🏗️ 지상 AI 부동산 분석 시스템")
st.caption("Ver 3.0 - Direct API Access Mode")

with st.sidebar:
    addr = st.text_input("분석할 주소", value="경기도 김포시 통진읍 도사리 163-1")
    btn = st.button("🚀 분석 실행", type="primary")

if btn:
    st.divider()
    with st.spinner("🤖 지상 AI가 부지를 정밀 분석 중입니다..."):
        result = run_ai_analysis(addr)
        st.markdown(result)