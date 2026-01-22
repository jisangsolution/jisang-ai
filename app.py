import streamlit as st
import requests
import json
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI (Next Gen)", page_icon="🏗️", layout="wide")
st.title("🏗️ 지상 AI 부동산 분석 시스템")
st.caption("Powered by Google Gemini 2.0 Flash (Next Gen)")

# 2. 분석 함수 (지창배님의 슈퍼 계정 전용 모델 사용)
def run_analysis(address, api_key):
    # [핵심] 지창배님의 목록에 있던 'gemini-2.0-flash' 모델 사용
    # 이 모델은 속도가 매우 빠르고 분석력이 뛰어납니다.
    model_name = "gemini-2.0-flash"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"""
            당신은 20년 경력의 한국 부동산 개발 전문가입니다.
            대상지: '{address}'
            
            이 땅에 '요양원' 또는 '전원주택'을 개발한다고 가정할 때, 다음 내용을 포함한 심층 분석 보고서를 작성해주세요:
            1. 입지 분석 (교통, 접근성, 주변 환경)
            2. 법적 규제 및 인허가 리스크 점검
            3. 사업성 분석 (어떤 시설이 더 수익성이 높은지 추천)
            4. 결론 및 제안
            
            전문적인 톤으로, 중요 내용은 볼드체로 강조해서 써주세요.
            """}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ 오류 발생 ({response.status_code}):\n{response.text}"
            
    except Exception as e:
        return f"❌ 시스템 통신 오류: {str(e)}"

# 3. 화면 구성
with st.sidebar:
    st.header("📍 분석 설정")
    input_addr = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
    run_btn = st.button("🚀 차세대 AI 분석 시작", type="primary")

# 4. 실행 로직
if run_btn:
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    
    if not api_key:
        st.error("⚠️ API 키가 없습니다. Settings > Secrets를 확인하세요.")
    else:
        st.divider()
        st.subheader(f"📄 AI 개발 전략 보고서: {input_addr}")
        
        # 지도 시각화
        st.map(pd.DataFrame({'lat': [37.689], 'lon': [126.589]}), zoom=13)
        
        with st.spinner("🤖 Gemini 2.0 AI가 최신 데이터를 분석 중입니다..."):
            result = run_analysis(input_addr, api_key)
            
            if "❌" in result:
                st.error(result)
            else:
                st.success("분석 완료!")
                st.markdown(result)