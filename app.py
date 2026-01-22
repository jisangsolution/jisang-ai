import streamlit as st
import requests
import json
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI 부동산 분석", page_icon="🏗️", layout="wide")

st.title("🏗️ 지상 AI 부동산 분석 시스템")
st.caption("시스템 상태: ✅ 구글 서버 직통 연결 (v1 Stable)")

# 2. 분석 함수 (라이브러리 없이 직접 통신)
def run_direct_analysis(address):
    try:
        # Secrets에서 키 가져오기
        api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
        if not api_key:
            return "⚠️ API 키가 없습니다. Secrets 설정을 확인해주세요."

        # 구글 Gemini 1.5 Flash 공식 주소 (v1 Stable 버전)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # 보낼 메시지 준비
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": f"당신은 20년 경력의 부동산 디벨로퍼입니다. 주소: '{address}' 이 땅에 요양원이나 전원주택을 지을 때의 사업성, 인허가 리스크, 추천 전략을 상세한 보고서 형태로 작성해주세요."}]
            }]
        }
        
        # 전송 (requests 사용)
        response = requests.post(url, headers=headers, json=payload)
        
        # 결과 처리
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ 구글 서버 응답 오류 ({response.status_code}):\n{response.text}"
            
    except Exception as e:
        return f"❌ 통신 오류 발생: {str(e)}"

# 3. 화면 구성
with st.sidebar:
    st.header("📍 분석 대상")
    address = st.text_input("주소 입력", value="경기도 김포시 통진읍 도사리 163-1")
    if st.button("🚀 분석 실행", type="primary"):
        st.session_state['run'] = True

# 4. 결과 출력
if st.session_state.get('run'):
    st.divider()
    st.subheader(f"📄 분석 보고서: {address}")
    
    # 지도 표시 (위치 시각화)
    st.map(pd.DataFrame({'lat': [37.689], 'lon': [126.589]}), zoom=13)
    
    with st.spinner("🤖 지상 AI가 구글 본사 서버에서 데이터를 받아오는 중입니다..."):
        result = run_direct_analysis(address)
        
        if "❌" in result:
            st.error(result)
        else:
            st.success("분석 완료!")
            st.markdown(result)
            st.download_button("📥 보고서 다운로드", result, file_name="부동산_분석_보고서.txt")