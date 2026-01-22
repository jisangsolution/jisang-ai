import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro v13.0", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
    .info-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    .risk-high { color: #dc2626; font-weight: bold; }
    .success-text { color: #16a34a; font-weight: bold; }
    .stMetric { background: #f8fafc; border-radius: 8px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ 지상 AI: 토지 정보 무결성 엔진")
st.caption("Ver 13.0 - 대장 면적·공시지가·도로조건·규제정보 통합")

# --- [연구 결과] 토지 정밀 데이터베이스 (공공 API 연동 모사) ---
LAND_MASTER_DATA = {
    "도사리 163-1": {
        "면적": "330㎡ (약 100평)",
        "용도지역": "자연녹지지역",
        "도로조건": "세로(가) - 승용차 진입 가능",
        "공시지가": "452,000원/㎡",
        "규제": ["가축사육제한구역", "군사시설보호구역"],
        "지구단위계획": "해당없음",
        "lat": 37.689, "lon": 126.589
    },
    "성동리 100": {
        "면적": "495㎡ (약 150평)",
        "용도지역": "계획관리지역",
        "도로조건": "소로2류(폭 8M~10M) 접합",
        "공시지가": "890,000원/㎡",
        "규제": ["성장관리계획구역", "역사문화환경보존지역"],
        "지구단위계획": "성동지구단위계획구역",
        "lat": 37.785, "lon": 126.695
    }
}

# --- 비즈니스 로직 ---

def get_land_details(addr):
    for key in LAND_MASTER_DATA:
        if key in addr: return LAND_MASTER_DATA[key]
    return None

def analyze_investment_risk(data):
    risk_score = 0
    messages = []
    
    # 도로 조건 분석
    if "맹지" in data['도로조건'] or "불가능" in data['도로조건']:
        risk_score += 40
        messages.append("⚠️ 도로 미접합 리스크 (건축 허가 불투명)")
    else:
        messages.append("✅ 도로 접합 (건축 가능성 높음)")
        
    # 규제 분석
    if len(data['규제']) > 1:
        risk_score += 20
        messages.append(f"⚠️ 중복 규제 확인: {', '.join(data['규제'])}")
        
    return 100 - risk_score, messages

# --- UI 레이아웃 ---

with st.sidebar:
    st.header("🔍 정밀 분석 설정")
    address = st.text_input("분석 주소", "경기도 김포시 통진읍 도사리 163-1")
    key = st.secrets.get("GOOGLE_API_KEY", "").strip()

    if st.button("🚀 정밀 데이터 분석", type="primary", use_container_width=True):
        land_info = get_land_details(address)
        if land_info:
            score, risks = analyze_investment_risk(land_info)
            st.session_state['land_data'] = land_info
            st.session_state['score'] = score
            st.session_state['risks'] = risks
            
            # AI 리포트 생성 (무결성 정보 주입)
            prompt = f"""
            부동산 전문가로서 다음 토지 정보를 분석하세요:
            주소: {address}
            면적: {land_info['면적']}, 도로: {land_info['도로조건']}, 공시지가: {land_info['공시지가']}
            규제상황: {', '.join(land_info['규제'])}
            위 정보를 바탕으로 '개발 실현 가능성'을 냉정하게 평가하세요.
            """
            with st.spinner("AI 전문가 보고서 작성 중..."):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={key}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['ai_report'] = res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error("해당 주소의 정밀 데이터가 DB에 없습니다. (도사리 163-1 또는 성동리 100 입력)")

# --- 메인 대시보드 ---

if 'land_data' in st.session_state:
    d = st.session_state['land_data']
    
    st.subheader(f"📍 {address} 토지 인텔리전스 리포트")
    
    # 1. 4대 핵심 지표
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("대장 면적", d['면적'])
    c2.metric("개별공시지가", d['공시지가'])
    c3.metric("도로 조건", d['도로조건'].split('-')[0])
    c4.metric("지구단위계획", d['지구단위계획'])

    st.divider()

    # 2. 리스크 분석 & 지도
    col_map, col_risk = st.columns([1.5, 1])
    
    with col_map:
        st.write("🌍 **현장 위치 (정밀 좌표 매핑)**")
        st.map(pd.DataFrame({'lat': [d['lat']], 'lon': [d['lon']]}), zoom=14)
        st.link_button("🌐 토지이음 규제정보 상세확인", "https://www.eum.go.kr/")

    with col_risk:
        st.write("⚖️ **법적 규제 및 리스크 검토**")
        for msg in st.session_state['risks']:
            if "⚠️" in msg: st.markdown(f"<p class='risk-high'>{msg}</p>", unsafe_allow_html=True)
            else: st.markdown(f"<p class='success-text'>{msg}</p>", unsafe_allow_html=True)
        
        st.info(f"**기타 규제:** {', '.join(d['규제'])}")

    st.divider()

    # 3. AI 최종 감정평가
    st.subheader("📄 AI 데이터 무결성 분석 결과")
    st.markdown(st.session_state['ai_report'])