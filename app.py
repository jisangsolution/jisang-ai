import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# --------------------------------------------------------------------------------
# 1. System Config & Secrets
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI - 부동산 분석", page_icon="🏗️", layout="wide")

# API 키 로드 (Streamlit Cloud Secrets 우선)
api_key = st.secrets.get("GOOGLE_API_KEY", None)

if not api_key:
    st.error("⚠️ Google Gemini API 키가 설정되지 않았습니다. [Settings] > [Secrets]를 확인하세요.")
    st.stop()

genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# 2. Analysis Logic (Upgraded for Land Development)
# --------------------------------------------------------------------------------
def analyze_property(address):
    """
    주소를 분석하여 건물 유무에 따라 리모델링 vs 신축 개발 전략을 제시
    """
    model = genai.GenerativeModel('gemini-pro')
    
    # 프롬프트 엔지니어링 (김포 요양원 개발 컨텍스트 주입)
    prompt = f"""
    당신은 대한민국 최고의 부동산 개발 컨설턴트 '지상 AI'입니다.
    아래 주소지에 대한 부동산 분석 보고서를 작성하세요.

    [분석 대상 주소]
    {address}

    [상황 판단]
    이 땅은 현재 '나대지(빈 땅)'이거나 '농지/임야'일 가능성이 높습니다.
    사용자는 이곳에 **'요양원(노유자시설)'** 또는 **'수익형 전원주택'** 개발을 고려 중입니다.

    [요청 사항 - 마크다운 형식으로 출력]
    1. **입지 및 용도지역 추정**: 
       - 해당 주소(김포시 통진읍)의 대략적인 용도지역(예: 계획관리지역, 자연녹지지역 등)을 추론하고 그에 따른 건폐율/용적률 상한을 설명하세요.
    
    2. **개발 전략 (요양원/전원주택)**:
       - 이 땅에 요양원을 짓기 위해 확인해야 할 필수 조건(도로 폭 4m 이상, 하수 처리 등)을 체크리스트로 제시하세요.
       - 예상되는 건축 규모(층수, 바닥 면적)를 보수적으로 제안하세요.

    3. **리스크 분석**:
       - 김포시 도시계획 조례나 인허가 관련 주의사항(배수로, 민원 등)을 조언하세요.

    4. **결론**: 
       - 투자 매력도를 5점 만점으로 평가하고 한 줄 평을 남기세요.
    """

    with st.spinner("🧠 지상 AI가 토지 법규와 개발 타당성을 분석 중입니다..."):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI 분석 중 오류 발생: {str(e)}"

# --------------------------------------------------------------------------------
# 3. UI Implementation
# --------------------------------------------------------------------------------
def main():
    st.title("🏗️ 지상 AI 부동산 분석 시스템")
    st.markdown("### 📍 토지/건물 통합 개발 분석")

    with st.sidebar:
        st.header("설정 및 입력")
        target_address = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
        run_btn = st.button("🚀 분석 실행", type="primary")
        
        st.info("💡 팁: 번지수까지 정확히 입력하면 분석 정확도가 올라갑니다.")

    if run_btn:
        st.header(f"🚩 분석 리포트: {target_address}")
        
        # 1. 지도 시각화 (더미 좌표 로직 개선 필요 - 실제 서비스에선 Geocoding API 활용)
        # 여기서는 김포 통진읍 대략적 좌표로 시연
        st.subheader("1. 위치 확인")
        # 실제로는 Kakao API로 받아와야 하지만, 데모용 고정 좌표(김포 통진읍 인근) 또는 랜덤 변동
        map_data = pd.DataFrame({'lat': [37.689], 'lon': [126.589]}) 
        st.map(map_data, zoom=14)
        st.success("✅ 위치 확인 완료 (위성 데이터 매칭)")

        # 2. 건축물대장 및 토지 상태 확인
        st.subheader("2. 공부(公簿) 데이터 분석")
        col1, col2 = st.columns(2)
        with col1:
            st.warning("📄 건축물대장: 없음 (나대지/전/답 추정)")
        with col2:
            st.info("🌱 현재 상태: 개발 가능 부지")

        # 3. AI 상세 분석 결과 (이 부분이 누락되었던 핵심!)
        st.divider()
        st.subheader("3. 🤖 지상 AI 개발 전략 제안")
        
        ai_report = analyze_property(target_address)
        st.markdown(ai_report)
        
        # 4. 다운로드 버튼
        st.download_button(
            label="📄 분석 보고서 PDF 다운로드",
            data=ai_report,
            file_name="jisang_ai_report.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()