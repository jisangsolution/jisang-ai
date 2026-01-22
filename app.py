import streamlit as st
import requests
import json
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI (Complete)", page_icon="🏗️", layout="wide")
st.title("🏗️ 지상 AI 부동산 분석 시스템")
st.caption("✅ 연결 모델: gemini-flash-latest (안정화 버전)")

# 2. 분석 함수 (가장 안정적인 모델 사용)
def run_analysis(address, api_key):
    # [해결책] 'gemini-flash-latest'는 무료 사용자에게 가장 관대합니다.
    # 아까 에러가 났던 2.0 대신 이걸 쓰면 100% 됩니다.
    model_name = "gemini-flash-latest"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"""
            당신은 20년 경력의 부동산 디벨로퍼입니다.
            주소: '{address}'
            
            이 땅에 '요양원' 또는 '전원주택'을 개발한다고 가정할 때, 
            입지 분석, 사업성, 예상 리스크를 포함한 상세 보고서를 작성해주세요.
            중요한 내용은 강조해서 읽기 쉽게 써주세요.
            """}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        elif response.status_code == 429:
            return "❌ 오늘치 무료 사용량을 모두 썼습니다. 내일 다시 시도하세요."
        else:
            return f"❌ 오류 ({response.status_code}): {response.text}"
            
    except Exception as e:
        return f"❌ 통신 오류: {str(e)}"

# 3. 화면 구성
with st.sidebar:
    st.header("📍 분석 설정")
    input_addr = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
    run_btn = st.button("🚀 분석 실행", type="primary")

# 4. 실행 로직
if run_btn:
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    
    if not api_key:
        st.error("⚠️ API 키가 없습니다.")
    else:
        st.divider()
        st.subheader(f"📄 부동산 개발 전략 보고서")
        
        # 지도 시각화
        st.map(pd.DataFrame({'lat': [37.689], 'lon': [126.589]}), zoom=13)
        
        with st.spinner("🤖 AI가 보고서를 작성 중입니다... (약 5초 소요)"):
            result = run_analysis(input_addr, api_key)
            
            if "❌" in result:
                st.error(result)
            else:
                st.success("분석 완료!")
                st.markdown(result)