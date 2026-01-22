import streamlit as st
import requests
import json
import pandas as pd

# 1. 기본 설정
st.set_page_config(page_title="지상 AI (Final)", page_icon="🏗️", layout="wide")
st.title("🏗️ 지상 AI 부동산 분석 시스템")

# 2. 분석 함수 (Google 공식 v1beta + Flash 모델 경로 고정)
def get_analysis(address, api_key):
    # 구글 Gemini 1.5 Flash 전용 주소 (v1beta)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"당신은 부동산 디벨로퍼입니다. 주소: '{address}'\n이 땅에 요양원이나 전원주택을 개발할 때의 입지 분석, 인허가 리스크, 사업성 전략을 상세한 보고서로 작성해주세요."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ 오류 발생 ({response.status_code}):\n{response.text}"
    except Exception as e:
        return f"❌ 통신 오류: {str(e)}"

# 3. 화면 구성
with st.sidebar:
    input_addr = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
    run_btn = st.button("🚀 분석 실행", type="primary")

# 4. 실행 로직
if run_btn:
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    
    if not api_key:
        st.error("⚠️ API 키가 없습니다. [Settings] > [Secrets]를 확인하세요.")
    else:
        st.divider()
        st.subheader(f"📄 분석 결과: {input_addr}")
        
        # 지도 표시
        st.map(pd.DataFrame({'lat': [37.689], 'lon': [126.589]}), zoom=13)
        
        with st.spinner("🤖 지상 AI가 최종 분석을 수행 중입니다..."):
            result = get_analysis(input_addr, api_key)
            st.markdown(result)