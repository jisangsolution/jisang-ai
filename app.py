import streamlit as st
import google.generativeai as genai
import pandas as pd

# --------------------------------------------------------------------------------
# 1. 시스템 설정
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI - 부동산 분석", page_icon="🏗️", layout="wide")

# API 키 로드 및 설정
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ Secrets에 GOOGLE_API_KEY가 없습니다.")
        st.stop()
    api_key = api_key.strip()  # 공백 제거 안전장치
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")
    st.stop()

# --------------------------------------------------------------------------------
# 2. 모델 자동 탐색 로직 (Universal Model Hunter) ⭐
# --------------------------------------------------------------------------------
def get_working_model():
    """
    작동 가능한 모델을 순서대로 테스트하여 가장 좋은 모델을 반환합니다.
    """
    # 테스트할 모델 후보군 (최신순)
    candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    
    logs = []
    
    for model_name in candidates:
        try:
            # 연결 시도
            model = genai.GenerativeModel(model_name)
            # 가벼운 인사로 생존 확인
            model.generate_content("Hi")
            return model, model_name  # 성공하면 즉시 반환
        except Exception as e:
            logs.append(f"{model_name} 실패: {str(e)}")
            continue
            
    # 모든 모델 실패 시
    return None, logs

# --------------------------------------------------------------------------------
# 3. 분석 로직
# --------------------------------------------------------------------------------
def analyze_property(address):
    # 작동하는 모델 찾기
    model, model_info = get_working_model()
    
    if not model:
        return f"""
        ❌ **모든 AI 모델 연결 실패**
        
        [진단 로그]
        {model_info}
        
        **해결책**: API 키가 연결된 Google Cloud 프로젝트에서 'Generative AI API'가 활성화되어 있는지 확인하거나, 새 프로젝트에서 키를 다시 발급받으세요.
        """

    prompt = f"""
    당신은 부동산 전문가 '지상 AI'입니다.
    주소: {address}
    
    이 땅이 나대지(빈 땅)라고 가정하고, 요양원이나 전원주택 개발 전략을 제안해주세요.
    입지, 도로 조건, 건축 리스크를 포함하여 마크다운 형식으로 보고서를 작성하세요.
    """

    with st.spinner(f"🧠 연결 성공! '{model_info}' 엔진으로 분석 중..."):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"분석 중 오류 발생: {str(e)}"

# --------------------------------------------------------------------------------
# 4. 메인 UI
# --------------------------------------------------------------------------------
def main():
    st.title("🏗️ 지상 AI 부동산 분석 시스템")
    st.caption("Universal Compatibility Mode On")

    with st.sidebar:
        target_address = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
        run_btn = st.button("🚀 분석 실행", type="primary")

    if run_btn:
        st.header(f"🚩 분석 리포트: {target_address}")
        
        # 지도 표시 (데모)
        st.subheader("1. 위치 확인")
        st.map(pd.DataFrame({'lat': [37.689], 'lon': [126.589]}), zoom=14)
        
        st.divider()
        st.subheader("2. 🤖 지상 AI 개발 전략")
        
        # 분석 실행
        report = analyze_property(target_address)
        st.markdown(report)

if __name__ == "__main__":
    main()