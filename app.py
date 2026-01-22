import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ 지상 AI 부동산 개발 타당성 분석")
st.caption("Ver 4.1 - Report Download & UI Tabs")

# 2. 사이드바: 상세 입력
with st.sidebar:
    st.header("📝 사업 개요 입력")
    
    address = st.text_input("대상지 주소", value="경기도 김포시 통진읍 도사리 163-1")
    
    purpose = st.selectbox(
        "개발 희망 용도", 
        ["요양원/실버타운", "전원주택 단지", "물류창고", "근린생활시설(상가)", "스마트팜"]
    )
    
    area = st.number_input("토지 면적 (평)", min_value=10, value=100, step=10)
    budget = st.slider("가용 예산 (건축비 포함)", 1, 50, 5, format="%d억 원")
    
    st.divider()
    run_btn = st.button("🚀 상세 분석 실행", type="primary")

# 3. 분석 함수
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
    payload = { "contents": [{ "parts": [{"text": prompt_text}] }] }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        elif response.status_code == 429:
            return "❌ 무료 사용량이 초과되었습니다. 잠시 후 다시 시도해주세요."
        else:
            return f"❌ 오류 ({response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 시스템 오류: {str(e)}"

# 4. 결과 처리 및 다운로드
if run_btn:
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    
    if not api_key:
        st.error("⚠️ API 키가 없습니다.")
    else:
        st.divider()
        
        # 탭 구성 (UI 깔끔하게 정리)
        tab1, tab2 = st.tabs(["📊 분석 결과 보고서", "🗺️ 지도 확인"])
        
        with st.spinner("🤖 AI가 보고서를 작성 중입니다..."):
            result_text = run_analysis(address, purpose, area, budget, api_key)
            
            # 탭 1: 보고서 및 다운로드
            with tab1:
                if "❌" in result_text:
                    st.error(result_text)
                else:
                    st.markdown(result_text)
                    st.divider()
                    
                    # [핵심] 다운로드 버튼
                    # 현재 시간으로 파일명 생성
                    now_str = datetime.now().strftime("%Y%m%d_%H%M")