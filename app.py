import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="지상 AI 최종 점검", page_icon="🗝️", layout="wide")

st.title("🗝️ 지상 AI 키 & 연결 점검")

# 1. API 키 로드 및 검증
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ Secrets에 키가 없습니다.")
        st.stop()
    
    # [중요] 키 공백 제거
    api_key = api_key.strip()
    
    # 🕵️‍♀️ 키 뒷자리 확인 (보안을 위해 뒷 4자리만 출력)
    key_tail = api_key[-4:]
    st.info(f"🔑 현재 웹사이트가 사용 중인 API 키 뒷자리: **{key_tail}**")
    
    # 연결 설정 (가장 기본 설정으로 복귀)
    genai.configure(api_key=api_key)

except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")
    st.stop()

# 2. 분석 실행 함수 (모델명에서 'models/' 제거하여 호환성 높임)
def run_analysis(address):
    try:
        # 모델명을 가장 단순하게 변경
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"부동산 전문가로서 {address}의 요양원/전원주택 개발 전략을 요약해줘."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

# 3. 실행 버튼
address = st.text_input("주소", value="경기도 김포시 통진읍 도사리 163-1")

if st.button("🚀 분석 실행", type="primary"):
    result = run_analysis(address)
    if "❌" in result:
        st.error(result)
        st.warning("☝️ 위 에러가 계속된다면, '현재 사용 중인 키 뒷자리'가 'jisang-ai' 프로젝트 키와 일치하는지 확인하세요.")
    else:
        st.success("✅ 분석 성공!")
        st.markdown(result)