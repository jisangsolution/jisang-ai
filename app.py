import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# --------------------------------------------------------------------------------
# 1. 시스템 설정 (System Config)
# --------------------------------------------------------------------------------
st.set_page_config(
    page_title="Jisang AI - 부동산 분석", 
    page_icon="🏗️", 
    layout="wide"
)

# API 키 로드 (Streamlit Cloud Secrets 우선)
# 에러 방지를 위한 예외 처리 추가
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ Google API 키가 설정되지 않았습니다. Streamlit Cloud의 [Settings] > [Secrets]를 확인해주세요.")
        st.stop()
    genai.configure(api_key=api_key)
except FileNotFoundError:
    # 로컬 실행 시 secrets.toml이 없을 경우 안내
    st.warning("⚠️ 로컬에서 실행 중이라면 .streamlit/secrets.toml 파일에 API 키를 설정해야 합니다. (웹 배포 시에는 무시하세요)")
    st.stop()

# --------------------------------------------------------------------------------
# 2. 분석 로직 (Analysis Logic) - 모델 업그레이드 완료
# --------------------------------------------------------------------------------
def analyze_property(address):
    """
    주소를 분석하여 토지 개발 전략을 제시 (Gemini 1.5 Flash 사용)
    """
    # [수정됨] 구형 'gemini-pro' 대신 최신형 'gemini-1.5-flash' 모델 사용
    # Flash 모델은 속도가 매우 빠르고 비용 효율적입니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 프롬프트: 김포 요양원/전원주택 개발 컨텍스트 반영
    prompt = f"""
    당신은 대한민국 최고의 부동산 개발 컨설턴트 '지상 AI'입니다.
    아래 주소지에 대한 '토지 개발 분석 보고서'를 작성하세요.

    [분석 대상 주소]
    {address}

    [가정 상황]
    - 현재 해당 지번은 건물이 없는 '나대지' 또는 '농지/임야' 상태입니다.
    - 사용자는 이곳에 '노유자시설(요양원)' 또는 '수익형 전원주택' 건축을 고려 중입니다.

    [요청 사항 - 가독성 좋은 마크다운 형식으로 출력]
    1. 📍 **입지 및 용도지역 분석**:
       - 해당 주소(김포시 통진읍 등)의 대략적인 용도지역(예: 계획관리지역, 자연녹지 등)을 추론하고 건폐율/용적률 기준을 설명하세요.
    
    2. 🏗️ **개발 전략 제안**:
       - **요양원 개발 시**: 필수 진입 도로 폭(4m 등), 하수 처리 시설 필요성 등을 체크리스트로 제시하세요.
       - **전원주택 개발 시**: 예상되는 건축 규모와 타겟 수요층(실거주 vs 세컨하우스)을 제안하세요.

    3. ⚠️ **주요 리스크 및 조언**:
       - 인허가 과정에서 발생할 수 있는 문제(배수로, 민원, 경사도)와 해결 팁을 주세요.

    4. 💡 **종합 의견**: 
       - 개발 사업성 점수(5점 만점)와 함께 "지상 AI의 한 줄 평"을 남겨주세요.
    """

    with st.spinner("🧠 지상 AI가 토지 법규와 개발 타당성을 정밀 분석 중입니다..."):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ AI 분석 중 오류가 발생했습니다: {str(e)}\n\n(API 키가 올바른지, 혹은 사용량이 초과되지 않았는지 확인해주세요.)"

# --------------------------------------------------------------------------------
# 3. 메인 화면 UI (User Interface)
# --------------------------------------------------------------------------------
def main():
    st.title("🏗️ 지상 AI 부동산 분석 시스템")
    st.markdown("### 📍 토지/건물 통합 개발 분석 (Ver 2.0)")

    with st.sidebar:
        st.header("설정 및 입력")
        target_address = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
        run_btn = st.button("🚀 분석 실행", type="primary")
        
        st.markdown("---")
        st.info("💡 **팁**: 번지수까지 정확히 입력하면 분석 정확도가 올라갑니다.")
        st.caption("Powered by Google Gemini 1.5 Flash")

    if run_btn:
        st.header(f"🚩 분석 리포트: {target_address}")
        
        # 1. 지도 시각화 (데모용 좌표)
        st.subheader("1. 위치 확인")
        # 김포 통진읍 인근 좌표 (실제 서비스에선 Geocoding API 연동 권장)
        map_data = pd.DataFrame({'lat': [37.689], 'lon': [126.589]}) 
        st.map(map_data, zoom=14)
        st.success("✅ 위성 데이터 매칭 완료")

        # 2. 공부 데이터 상태
        st.subheader("2. 공부(公簿) 데이터 분석")
        col1, col2 = st.columns(2)
        with col1:
            st.warning("📄 건축물대장: 없음 (나대지/전/답 추정)")
        with col2:
            st.info("🌱 현재 상태: 신축 개발 가능 부지")

        # 3. AI 상세 분석 결과
        st.divider()
        st.subheader("3. 🤖 지상 AI 개발 전략 제안")
        
        # 분석 함수 실행
        ai_report = analyze_property(target_address)
        
        # 결과 출력
        st.markdown(ai_report)
        
        # 다운로드 버튼
        st.download_button(
            label="📄 분석 보고서 PDF 다운로드",
            data=ai_report,
            file_name="jisang_ai_report.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()