import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ 지상 AI 부동산 개발 타당성 분석")
st.caption("Ver 4.2 - Result Preservation & Multi-Download")

# [핵심] 분석 결과를 기억하기 위한 저장소(Session State) 초기화
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None
if 'addr' not in st.session_state:
    st.session_state['addr'] = ""
if 'purpose' not in st.session_state:
    st.session_state['purpose'] = ""

# 2. 분석 함수
def run_analysis(addr, purp, area, bdgt, api_key):
    model_name = "gemini-flash-latest"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt_text = f"""
    당신은 25년 경력의 부동산 개발 컨설턴트입니다.
    
    [사업 개요]
    - 주소: {addr}
    - 용도: {purp}
    - 면적: {area}평
    - 예산: {bdgt}억 원

    [요청 사항]
    위 조건을 바탕으로 상세한 '개발 타당성 검토 보고서'를 작성해주세요.
    1. 입지 분석 (SWOT 관점)
    2. 건축 규모 추산 (건폐율/용적률 고려)
    3. 예산 적정성 평가 (구체적 비용 내역 추산 포함)
    4. 규제 및 리스크 (인허가 이슈)
    5. 최종 제안

    출력 형식: 가독성 좋은 마크다운(Markdown) 포맷
    """
    
    headers = {'Content-Type': 'application/json'}
    payload = { "contents": [{ "parts": [{"text": prompt_