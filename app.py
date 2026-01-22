import streamlit as st
import requests
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ 지상 AI 부동산 개발 타당성 분석")
st.caption("Ver 4.0 - Advanced Context & Detail Prompting")

# 2. 사이드바: 상세 입력 받기
with st.sidebar:
    st.header("📝 사업 개요 입력")
    
    # 주소
    address = st.text_input("대상지 주소", value="경기도 김포시 통진읍 도사리 163-1")
    
    # 용도 선택
    purpose = st.selectbox(
        "개발 희망 용도", 
        ["요양원/실버타운", "전원주택 단지", "물류창고", "근린생활시설(상가)", "스마트팜"]
    )
    
    # 면적 및 예산
    area = st.number_input("토지 면적 (평)", min_value=10, value=100, step=10)
    budget = st.slider("가용 예산 (건축비 포함)", 1, 50, 5, format="%d억 원")
    
    st.divider()
    run_btn = st.button("🚀 상세 분석 실행", type="primary")

# 3. 분석 함수 (프롬프트 고도화)
def run_advanced_analysis(addr, purp, area, bdgt, api_key):
    model_name = "gemini-flash-latest" # 가장 안정적인 모델 유지
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # [핵심] 입력받은 데이터를 모두 프롬프트에 녹여냅니다.
    prompt_text = f"""
    당신은 25년 경력의 부동산 개발 컨설턴트이자 건축사입니다.
    아래 조건에 맞춰 개발 타당성 보고서를 작성해주세요.

    [사업 개요]
    1. 주소: {addr}
    2. 희망 용도: {purp}
    3. 토지 면적: {area}평
    4. 가용 예산: {bdgt}억 원

    [요청 사항]
    1. {addr}의 입지적 특징 (교통, 배후수요)을 {purp} 관점에서 비판적으로 분석하세요.
    2. {area}평 대지에 {purp}을(를) 지을 때의 예상 건축 규모(건폐율/용적률 고려)를 추산하세요.
    3. 예산 {bdgt}억 원으로 건축이 가능한지, 자금 부족 시 대안은 무엇인지 냉정하게 평가하세요.
    4. 인허가 리스크 및 규제 사항을 점검하세요.
    5. 종합 결론 (추천/보류/비추천)을 명확히 내리세요.

    출력 형식: 깔끔한 마크다운 보고서 형식
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

# 4. 결과 화면
if run_btn:
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    
    if not api_key:
        st.error("⚠️ API 키가 없습니다.")
    else:
        st.divider()
        st.subheader(f"📊 {purpose} 개발 전략 보고서")
        
        # 지도 바로가기 버튼 (편의 기능)
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("🗺️ 네이버 지도로 보기", f"https://map.naver.com/v5/search/{address}")
        with col2:
            st.link_button("🗺️ 카카오맵으로 보기", f"https://map.kakao.com/link/search/{address}")

        # 분석 실행
        with st.spinner(f"🤖 AI가 '{purpose}' 개발 타당성을 정밀 분석 중입니다..."):
            result = run_advanced_analysis(address, purpose, area, budget, api_key)
            st.markdown(result)