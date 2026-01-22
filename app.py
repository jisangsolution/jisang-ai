import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(page_title="지상 AI 자가진단", page_icon="🩺", layout="wide")

st.title("🩺 지상 AI 자가 진단 및 분석 시스템")

# 1. API 키 준비
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()

# 2. 사용 가능한 모델 목록 조회 함수 (진단용)
def get_available_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # 채팅/텍스트 생성이 가능한 모델만 필터링
            models = [m['name'].replace('models/', '') for m in data.get('models', []) 
                      if 'generateContent' in m.get('supportedGenerationMethods', [])]
            return models
        else:
            return []
    except:
        return []

# 3. 분석 실행 함수 (자동 우회 시도)
def run_smart_analysis(address):
    # 시도할 모델명 우선순위 리스트
    candidate_models = [
        "gemini-1.5-flash-001",  # 1순위: 특정 버전 명시
        "gemini-1.5-flash-latest", # 2순위: 최신 버전 별칭
        "gemini-1.5-flash",      # 3순위: 일반 별칭
        "gemini-pro"             # 4순위: 구형 안정 버전
    ]
    
    # 사용 가능한 모델 조회
    available_models = get_available_models()
    
    # 사용 가능한 것 중 가장 좋은 것 선택
    valid_model = None
    for model in candidate_models:
        if model in available_models:
            valid_model = model
            break
            
    # 만약 매칭되는 게 없으면 목록의 첫 번째 것 사용
    if not valid_model and available_models:
        valid_model = available_models[0]
    
    if not valid_model:
        return f"❌ 오류: 사용할 수 있는 AI 모델이 없습니다.\n(검색된 모델 목록: {available_models})"

    # 선택된 모델로 분석 시도
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{valid_model}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": f"부동산 전문가로서 '{address}' 부지의 요양원/전원주택 개발 전략을 상세히 보고서로 작성해줘."}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return f"✅ **연결 성공! (사용 모델: {valid_model})**\n\n" + response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ 서버 응답 오류 ({valid_model}): {response.text}"
            
    except Exception as e:
        return f"❌ 통신 오류: {str(e)}"

# 4. 화면 UI
with st.sidebar:
    st.header("📍 분석 대상")
    address = st.text_input("주소", value="경기도 김포시 통진읍 도사리 163-1")
    if st.button("🚀 분석 실행", type="primary"):
        st.session_state['run'] = True

if st.session_state.get('run'):
    st.divider()
    with st.spinner("🤖 사용 가능한 AI 모델을 검색하고 분석 중입니다..."):
        result = run_smart_analysis(address)
        if "❌" in result:
            st.