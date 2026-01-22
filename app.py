import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", layout="wide", page_icon="🏗️")
st.title("🏗️ 지상 AI: 부동산 개발 타당성 분석")
st.caption("Ver 5.0 - Real Map & Interactive Chat")

# 세션 상태 초기화
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'lat' not in st.session_state:
    st.session_state['lat'] = 37.5665 # 기본값 서울
if 'lon' not in st.session_state:
    st.session_state['lon'] = 126.9780

# 2. 기능 함수들

# (1) 주소로 좌표 찾기 (지오코딩 - OpenStreetMap 사용)
def get_coordinates(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': address, 'format': 'json', 'limit': 1}
        headers = {'User-Agent': 'JisangAI/1.0'}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200 and len(response.json()) > 0:
            data = response.json()[0]
            return float(data['lat']), float(data['lon'])
        else:
            return None, None
    except:
        return None, None

# (2) AI 분석 및 대화 함수 (안전 조립식)
def call_ai_model(messages, api_key):
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    model_name = "gemini-flash-latest"
    url = f"{base_url}/{model_name}:generateContent?key={api_key}"
    
    # 메시지 포맷 변환
    contents = []
    for role, text in messages:
        # role 변환 (user/model)
        api_role = "user" if role == "user" else "model"
        
        # 안전한 파츠 조립
        part = {"text": text}
        content = {"role": api_role, "parts": [part]}
        contents.append(content)
    
    payload = {"contents": contents}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ 오류 {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ 통신 오류: {str(e)}"

# 3. 사이드바 (입력)
with st.sidebar:
    st.header("📝 사업 정보 입력")
    address = st.text_input("주소", value="경기도 김포시 통진읍 도사리 163-1")
    purpose = st.selectbox("용도", ["요양원/실버타운", "전원주택 단지", "물류창고", "상가건물"])
    area = st.number_input("대지 면적 (평)", value=100)
    budget = st.slider("가용 예산 (억)", 1, 100, 5)
    
    st.divider()
    
    if st.button("🚀 분석 실행", type="primary"):
        api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
        if not api_key:
            st.error("API 키가 없습니다.")
        else:
            with st.spinner("🌍 위치를 찾고 AI가 분석 중입니다..."):
                # 1. 좌표 찾기
                lat, lon = get_coordinates(address)
                if lat:
                    st.session_state['lat'] = lat
                    st.session_state['lon'] = lon
                
                # 2. 프롬프트 작성
                prompt = f"주소: {address}\n용도: {purpose}\n면적: {area}평\n예산: {budget}억\n"
                prompt += "위 정보를 바탕으로 심층 개발 타당성 보고서를 작성해주세요.\n"
                prompt += "입지(교통/수요), 법적 리스크, 사업성 분석, 종합 의견을 포함하세요."
                
                # 3. AI 호출
                initial_msg = [("user", prompt)]
                result = call_ai_model(initial_msg, api_key)
                
                # 4. 결과 저장
                st.session_state['analysis_result'] = result
                st.session_state['chat_history'] = [("user", prompt), ("assistant", result)]

    # 다운로드 버튼
    if st.session_state['analysis_result']:
        st.divider()
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("📥 보고서 저장 (.md)", st.session_state['analysis_result'], f"Report_{now_str}.md")

# 4. 메인 화면
if st.session_state['analysis_result']:
    # 탭 구성
    tab1, tab2 = st.tabs(["📊 분석 보고서", "🗺️ 현장 지도"])
    
    with tab1:
        st.markdown(st.session_state['analysis_result'])
        st.divider()
        st.subheader("💬 AI 개발 컨설턴트와 대화하기")
        
        # 채팅 기록 표시
        for role, msg in st.session_state['chat_history'][2:]: # 초기 프롬프트 제외하고 표시
            with st.chat_message(role):
                st.write(msg)
        
        # 채팅 입력
        if user_input := st.chat_input("보고서 내용 중 궁금한 점을 물어보세요..."):
            api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
            
            # 사용자 메시지 표시
            with st.chat_message("user"):
                st.write(user_input)
            
            # 히스토리에 추가
            st.session_state['chat_history'].append(("user", user_input))
            
            # AI 응답 요청
            with st.spinner("생각 중..."):
                # 전체 대화 맥락을 보냄
                ai_response = call_ai_model(st.session_state['chat_history'], api_key)
                
                with st.chat_message("assistant"):
                    st.write(ai_response)
                
                st.session_state['chat_history'].append(("assistant", ai_response))

    with tab2:
        st.info(f"📍 지도 위치: {address}")
        # 동적 좌표 지도 표시
        data = pd.DataFrame({'lat': [st.session_state['lat']], 'lon': [st.session_state['lon']]})
        st.map(data, zoom=14)
        
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("네이버 지도 보기", f"https://map.naver.com/v5/search/{address}")
        with c2:
            st.link_button("카카오맵 보기", f"https://map.kakao.com/link/search/{address}")

elif not st.session_state['analysis_result']:
    st.info("👈 왼쪽 사이드바에 정보를 입력하고 [🚀 분석 실행]을 눌러주세요.")