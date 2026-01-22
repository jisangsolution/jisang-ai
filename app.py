import streamlit as st
import google.generativeai as genai

# 1. 페이지 기본 설정
st.set_page_config(page_title="지상 AI", page_icon="🏗️", layout="wide")
st.title("🏗️ 지상 AI 부동산 분석 시스템")

# 2. 안전한 API 연결 함수 (자동 우회 기능 포함)
def run_analysis_safe(address, api_key):
    try:
        # API 키 설정
        genai.configure(api_key=api_key)
        
        # [핵심] 1순위(Flash)가 안 되면 2순위(Pro)로 자동 전환하는 로직
        models_to_try = ["gemini-1.5-flash", "gemini-pro"]
        
        model = None
        last_error = ""

        for model_name in models_to_try:
            try:
                # 모델 연결 시도
                test_model = genai.GenerativeModel(model_name)
                # 연결 테스트 (가벼운 인사)
                test_model.generate_content("Hello")
                # 성공하면 채택
                model = test_model
                break 
            except Exception as e:
                last_error = str(e)
                continue # 다음 모델 시도

        if not model:
            return f"❌ 모든 AI 모델 연결 실패. (원인: {last_error})"

        # 3. 진짜 분석 실행
        prompt = f"""
        당신은 20년 경력의 부동산 디벨로퍼입니다.
        주소: {address}
        이 땅에 요양원이나 전원주택을 지을 때의 입지 분석, 규제 사항, 사업성 전략을
        전문적인 보고서 형태로 작성해주세요.
        """
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"❌ 시스템 오류: {str(e)}"

# 3. 화면 구성 및 실행
with st.sidebar:
    addr = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
    btn = st.button("🚀 분석 실행", type="primary")

if btn:
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    
    if not api_key:
        st.error("⚠️ API 키가 없습니다. Settings > Secrets를 확인하세요.")
    else:
        st.divider()
        with st.spinner("🤖 지상 AI가 가장 안정적인 경로로 분석 중입니다..."):
            result = run_analysis_safe(addr, api_key)
            
            if "❌" in result:
                st.error(result)
            else:
                st.success("분석 완료!")
                st.markdown(result)