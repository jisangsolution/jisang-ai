import streamlit as st
import google.generativeai as genai
import pandas as pd

# --------------------------------------------------------------------------------
# 1. 시스템 설정
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI - 부동산 분석", page_icon="🏗️", layout="wide")

# API 키 로드
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ Google API 키가 없습니다. [Settings] > [Secrets]를 확인하세요.")
        st.stop()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")
    st.stop()

# --------------------------------------------------------------------------------
# 2. 스마트 모델 선택 로직 (핵심 업그레이드 ⭐)
# --------------------------------------------------------------------------------
def get_available_model():
    """작동 가능한 모델을 자동으로 찾습니다."""
    try:
        # 1순위: 최신형 Flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        # 테스트 호출 (가볍게 인사)
        model.generate_content("Hello")
        return model, "Gemini 1.5 Flash (최신형)"
    except:
        try:
            # 2순위: 1.5 Pro
            model = genai.GenerativeModel('gemini-1.5-pro')
            model.generate_content("Hello")
            return model, "Gemini 1.5 Pro (고성능)"
        except:
            try:
                # 3순위: 구형 Pro
                model = genai.GenerativeModel('gemini-pro')
                model.generate_content("Hello")
                return model, "Gemini Pro (기본)"
            except:
                return None, "없음"

# --------------------------------------------------------------------------------
# 3. 분석 로직
# --------------------------------------------------------------------------------
def analyze_property(address):
    model, model_name = get_available_model()
    
    if not model:
        # 모델을 하나도 못 찾았을 때 -> 키 문제임이 확실함
        return """
        ❌ **AI 연결 실패**
        
        사용 중인 API 키로는 어떠한 AI 모델에도 접근할 수 없습니다.
        **[해결 방법]**
        1. [Google AI Studio](https://aistudio.google.com/)에 접속하세요.
        2. **'Get API key'**를 눌러 **새로운 키(Create new key)**를 발급받으세요.
        3. Streamlit Cloud의 **[Secrets]** 설정에 새 키를 붙여넣으세요.
        """

    prompt = f"""
    당신은 부동산 전문가 '지상 AI'입니다.
    주소: {address}
    
    이 땅이 나대지(빈 땅)라고 가정하고, 요양원이나 전원주택 개발 전략을 제안해주세요.
    입지, 도로 조건, 건축 리스크를 포함하여 마크다운 형식으로 보고서를 작성하세요.
    """

    with st.spinner(f"🧠 {model_name} 엔진으로 분석 중..."):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"오류 발생: {str(e)}"

# --------------------------------------------------------------------------------
# 4. 메인 화면
# --------------------------------------------------------------------------------
def main():
    st.title("🏗️ 지상 AI 부동산 분석 시스템")
    st.caption("Auto-Switching AI Engine Loaded")

    with st.sidebar:
        target_address = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
        run_btn = st.button("🚀 분석 실행", type="primary")

    if run_btn:
        st.header(f"🚩 분석 리포트: {target_address}")
        
        # 지도 (데모용)
        st.map(pd.DataFrame({'lat': [37.689], 'lon': [126.589]}), zoom=14)
        
        st.divider()
        st.subheader("🤖 AI 개발 전략 제안")
        
        report = analyze_property(target_address)
        st.markdown(report)

if __name__ == "__main__":
    main()