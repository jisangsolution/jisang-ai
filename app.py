import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", layout="wide")
st.title("🏗️ 지상 AI 부동산 분석")
st.caption("Ver 4.3 - Save Check Version")

# 세션 초기화
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None

# 2. 분석 함수 (안전 조립식)
def run_analysis(addr, purp, area, bdgt, api_key):
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    model_name = "gemini-flash-latest"
    url = f"{base_url}/{model_name}:generateContent?key={api_key}"
    
    # 텍스트 조립 (한 줄씩 변수에 담기 - 절대 안 잘림)
    prompt = f"주소: {addr}\n"
    prompt += f"용도: {purp}\n"
    prompt += f"면적: {area}평\n"
    prompt += f"예산: {bdgt}억\n"
    prompt += "위 정보로 개발 타당성 보고서(입지,사업성,리스크,결론)를 작성해줘."
    
    # 데이터 포장 (짧은 줄로 구성)
    part = {"text": prompt}
    content = {"parts": [part]}
    payload = {"contents": [content]}
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        elif response.status_code == 429:
            return "❌ 사용량 초과. 잠시 후 시도하세요."
        else:
            return f"❌ 오류 {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ 시스템 오류: {str(e)}"

# 3. 화면 구성
with st.sidebar:
    st.header("📝 입력")
    address = st.text_input("주소", value="김포시 통진읍 도사리 163-1")
    purpose = st.selectbox("용도", ["요양원", "전원주택", "물류창고"])
    area = st.number_input("면적", 100)
    budget = st.slider("예산(억)", 1, 50, 5)
    
    if st.button("🚀 실행"):
        key = st.secrets.get("GOOGLE_API_KEY", "").strip()
        if not key:
            st.error("API 키 없음")
        else:
            with st.spinner("분석 중..."):
                res = run_analysis(address, purpose, area, budget, key)
                st.session_state['analysis_result'] = res

    if st.session_state['analysis_result']:
        st.divider()
        st.download_button("📥 저장", st.session_state['analysis_result'], "report.md")

# 4. 결과 출력
if st.session_state['analysis_result']:
    st.divider()
    st.markdown(st.session_state['analysis_result'])