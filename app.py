import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. 시스템 설정
st.set_page_config(page_title="Jisang AI - 부동산 분석", page_icon="🏗️", layout="wide")

# 2. API 키 설정 (공백 제거 로직 포함)
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key.strip())
    else:
        st.error("⚠️ Secrets에 GOOGLE_API_KEY가 없습니다.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")
    st.stop()

# 3. 분석 실행 함수 (최신 v1 규격 적용)
def analyze_property(address):
    try:
        # [핵심 변경] 모델 호출 시 최신 안정화 버전인 'gemini-1.5-flash'를 사용합니다.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        당신은 부동산 전문가 '지상 AI'입니다.
        주소: {address}
        이 부지에 요양원이나 전원주택 개발이 가능한지 분석하고 전략 보고서를 작성하세요.
        입지 분석, 건축 리스크, 종합 의견을 포함하세요.
        """

        # API 호출
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # 에러 메시지를 더 구체적으로 표시하여 진단을 돕습니다.
        return f"❌ AI 분석 중 오류가 발생했습니다.\n\n상세내용: {str(e)}"

# 4. 메인 화면 UI
def main():
    st.title("🏗️ 지상 AI 부동산 분석 시스템")
    st.caption("Ver 2.5 - Stable Connection Mode")

    with st.sidebar:
        target_address = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
        run_btn = st.button("🚀 분석 실행", type="primary")

    if run_btn:
        st.header(f"🚩 분석 리포트: {target_address}")
        
        # 지도 (데모용)
        st.map(pd.DataFrame({'lat': [37.689], 'lon': [126.589]}), zoom=14)
        
        st.divider()
        st.subheader("🤖 지상 AI 개발 전략 제안")
        
        with st.spinner("🧠 구글 최신 엔진으로 분석 중..."):
            result = analyze_property(target_address)
            st.markdown(result)

if __name__ == "__main__":
    main()