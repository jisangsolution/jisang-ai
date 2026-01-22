import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 (압도적 UI/UX)
st.set_page_config(page_title="지상 AI: 부동산 투자 분석", layout="wide", page_icon="🏢")
st.title("🏢 지상 AI: 부동산 개발 타당성 & 수지분석 시스템")
st.caption("Ver 6.0 - Investment Dashboard & ROI Simulator")

# 세션 초기화
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'metrics' not in st.session_state:
    st.session_state['metrics'] = {}

# 2. 핵심 함수: 파이썬 수지분석 (Logic)
def calculate_metrics(area, budget, purpose):
    # 용도별 평당 건축비 추정 (2025년 기준, 단위: 만원)
    cost_map = {
        "요양원/실버타운": 850,
        "전원주택 단지": 750,
        "물류창고": 450,
        "상가건물": 600
    }
    
    unit_cost = cost_map.get(purpose, 700)
    est_const_cost = area * unit_cost / 10000 # 억 단위 환산
    est_total_cost = est_const_cost * 1.2 # 설계/감리/예비비 20% 추가
    
    balance = budget - est_total_cost # 과부족액
    
    return {
        "unit_cost": unit_cost,
        "total_cost": round(est_total_cost, 2),
        "balance": round(balance, 2),
        "status": "자금 여유" if balance >= 0 else "자금 부족"
    }

# 3. 핵심 함수: AI 분석 (Insight) - 안전 조립식
def call_ai_model(messages, api_key):
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    model_name = "gemini-flash-latest"
    url = f"{base_url}/{model_name}:generateContent?key={api_key}"
    
    contents = []
    for role, text in messages:
        api_role = "user" if role == "user" else "model"
        part = {"text": text}
        contents.append({"role": api_role, "parts": [part]})
    
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

# 4. 사이드바 (입력)
with st.sidebar:
    st.header("📝 투자 정보 입력")
    address = st.text_input("대상지 주소", value="경기도 김포시 통진읍 도사리 163-1")
    purpose = st.selectbox("개발 용도", ["요양원/실버타운", "전원주택 단지", "물류창고", "상가건물"])
    area = st.number_input("건축 연면적 (평)", value=100)
    budget = st.slider("가용 예산 (억)", 1, 100, 5)
    
    st.divider()
    
    if st.button("🚀 원클릭 수익성 분석", type="primary"):
        api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
        if not api_key:
            st.error("API 키 확인 필요")
        else:
            with st.spinner("💰 1차: 파이썬이 수지타산을 계산 중..."):
                metrics = calculate_metrics(area, budget, purpose)
                st.session_state['metrics'] = metrics
            
            with st.spinner("🧠 2차: AI가 입지와 리스크를 분석 중..."):
                # 프롬프트: 파이썬 계산 결과를 AI에게 검증 요청
                prompt = f"""
                [사업 개요]
                주소: {address}, 용도: {purpose}, 면적: {area}평, 예산: {budget}억
                
                [1차 계산 결과]
                평당 건축비: {metrics['unit_cost']}만원
                총 소요 비용(예상): {metrics['total_cost']}억
                자금 상황: {metrics['balance']}억 ({metrics['status']})
                
                [요청 사항]
                위 계산 결과를 바탕으로, 부동산 디벨로퍼 관점에서 냉철한 심층 보고서를 작성해주세요.
                1. 입지 분석 (해당 주소의 실제 지리적 특성)
                2. 사업성 평가 (위 예산으로 현실적으로 가능한지 비평)
                3. 리스크 및 규제 (요양원/전원주택 등 용도별 특이사항)
                4. 결론 (추천/비추천 명시)
                """
                
                result = call_ai_model([("user", prompt)], api_key)
                st.session_state['analysis_result'] = result
                st.session_state['chat_history'] = [("user", prompt), ("assistant", result)]

# 5. 메인 대시보드 (돈이 되는 정보)
if st.session_state['analysis_result']:
    # (1) 경영 대시보드 (KPI)
    st.subheader("📊 투자 타당성 대시보드")
    m = st.session_state['metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("평당 건축비 (추정)", f"{m['unit_cost']}만 원")
    col2.metric("총 소요 예산", f"{m['total_cost']}억 원")
    
    # 자금 상황에 따라 색상 변경
    balance_display = f"{m['balance']}억 원"
    if m['balance'] >= 0:
        col3.metric("예상 잔여금", balance_display, delta="안정")
    else:
        col3.metric("자금 부족액", balance_display, delta="-위험", delta_color="inverse")
        
    col4.metric("종합 판정", m['status'])
    
    st.divider()

    # (2) 상세 분석 탭
    tab1, tab2, tab3 = st.tabs(["📄 AI 심층 리포트", "💬 AI 파트너 대화", "🗺️ 위치 확인"])
    
    with tab1:
        st.markdown(st.session_state['analysis_result'])
        
        # 다운로드
        now_str = datetime.now().strftime("%Y%m%d")
        st.download_button("📥 보고서 PDF용 저장 (.md)", st.session_state['analysis_result'], f"Report_{now_str}.md")

    with tab2:
        # 채팅 UI
        for role, msg in st.session_state['chat_history'][2:]:
            with st.chat_message(role):
                st.write(msg)
        
        if user_input := st.chat_input("추가 질문 (예: 대출은 얼마나 나올까?)"):
            api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
            st.session_state['chat_history'].append(("user", user_input))
            with st.chat_message("user"):
                st.write(user_input)
            
            with st.spinner("분석 중..."):
                response = call_ai_model(st.session_state['chat_history'], api_key)
                st.session_state['chat_history'].append(("assistant", response))
                with st.chat_message("assistant"):
                    st.write(response)

    with tab2: # 탭 공유 버그 방지 - 지도 탭 분리
        pass
    
    with tab3:
        # 지도 기능 (간단 버전)
        st.info(f"📍 사업지: {address}")
        # 주소 좌표 변환은 안정성을 위해 기본값 or 이전 로직 사용 권장 (여기선 UI 중심)
        st.map(pd.DataFrame({'lat': [37.689], 'lon': [126.589]}), zoom=14)
        st.caption("*정확한 지번 좌표 연동은 추후 업데이트됩니다.")

elif not st.session_state['analysis_result']:
    st.info("👈 왼쪽에서 예산과 평수를 입력하고 [원클릭 수익성 분석]을 눌러보세요.")