import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", layout="wide", page_icon="🏢")
st.title("🏢 지상 AI: 부동산 개발 타당성 & 수지분석")
st.caption("Ver 7.0 - Premium Report Generation")

# 세션 초기화
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'metrics' not in st.session_state:
    st.session_state['metrics'] = {}

# 2. 수지분석 로직
def calculate_metrics(area, budget, purpose):
    cost_map = {"요양원/실버타운": 850, "전원주택 단지": 750, "물류창고": 450, "상가건물": 600}
    unit_cost = cost_map.get(purpose, 700)
    est_const_cost = area * unit_cost / 10000 
    est_total_cost = est_const_cost * 1.2 
    balance = budget - est_total_cost 
    
    return {
        "unit_cost": unit_cost,
        "total_cost": round(est_total_cost, 2),
        "balance": round(balance, 2),
        "status": "자금 여유" if balance >= 0 else "자금 부족"
    }

# 3. AI 분석 로직 (안전 조립식)
def call_ai_model(messages, api_key):
    base = "https://generativelanguage.googleapis.com/v1beta/models"
    model = "gemini-flash-latest"
    url = f"{base}/{model}:generateContent?key={api_key}"
    
    contents = []
    for role, text in messages:
        r = "user" if role == "user" else "model"
        contents.append({"role": r, "parts": [{"text": text}]})
    
    payload = {"contents": contents}
    headers = {'Content-Type': 'application/json'}
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error {res.status_code}: {res.text}"
    except Exception as e:
        return f"Sys Error: {str(e)}"

# 4. [신규] 프리미엄 리포트 HTML 생성기
def create_html_report(addr, purp, area, bdgt, metrics, ai_text):
    # 날짜
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 스타일 (CSS) - 깔끔한 A4 스타일
    html = """
    <style>
        .report-container { font-family: 'Malgun Gothic', sans-serif; padding: 40px; border: 1px solid #ddd; background: white; color: #333; }
        .header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 30px; }
        .title { font-size: 28px; font-weight: bold; color: #1E3A8A; }
        .meta { font-size: 14px; color: #666; margin-top: 5px; }
        .section { margin-top: 30px; margin-bottom: 20px; }
        .section-title { font-size: 20px; font-weight: bold; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-bottom: 15px; }
        .kpi-box { display: flex; justify-content: space-between; background: #F3F4F6; padding: 20px; border-radius: 10px; }
        .kpi-item { text-align: center; }
        .kpi-value { font-size: 24px; font-weight: bold; color: #1E3A8A; }
        .kpi-label { font-size: 14px; color: #555; }
        .content { line-height: 1.6; font-size: 16px; white-space: pre-line; }
        .footer { margin-top: 50px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
    """
    
    # 본문 조립
    html += f"<div class='report-container'>"
    html += f"<div class='header'><div class='title'>부동산 개발 타당성 분석 보고서</div>"
    html += f"<div class='meta'>분석 일자: {today} | 작성: 지상 AI 시스템</div></div>"
    
    # 1. 사업 개요
    html += f"<div class='section'><div class='section-title'>1. 사업 개요</div>"
    html += f"<ul><li><b>주소:</b> {addr}</li><li><b>용도:</b> {purp}</li>"
    html += f"<li><b>면적:</b> {area}평</li><li><b>예산:</b> {bdgt}억 원</li></ul></div>"
    
    # 2. 투자 지표 (KPI)
    html += f"<div class='section'><div class='section-title'>2. 투자 수익성 지표</div>"
    html += f"<div class='kpi-box'>"
    html += f"<div class='kpi-item'><div class='kpi-value'>{metrics['unit_cost']}만</div><div class='kpi-label'>평당 건축비</div></div>"
    html += f"<div class='kpi-item'><div class='kpi-value'>{metrics['total_cost']}억</div><div class='kpi-label'>총 소요 비용</div></div>"
    
    # 자금 상태 색상 처리
    color = "red" if metrics['balance'] < 0 else "green"
    html += f"<div class='kpi-item'><div class='kpi-value' style='color:{color}'>{metrics['balance']}억</div><div class='kpi-label'>자금 과부족</div></div>"
    html += f"</div></div>"
    
    # 3. AI 상세 분석
    html += f"<div class='section'><div class='section-title'>3. 전문가 심층 분석</div>"
    html += f"<div class='content'>{ai_text}</div></div>"
    
    html += f"<div class='footer'>본 보고서는 AI 분석 결과이며 법적 효력은 없습니다. | Powered by Jisang AI</div>"
    html += "</div>"
    
    return html

# 5. 사이드바
with st.sidebar:
    st.header("📝 입력")
    address = st.text_input("주소", value="김포시 통진읍 도사리 163-1")
    purpose = st.selectbox("용도", ["요양원/실버타운", "전원주택 단지", "물류창고", "상가건물"])
    area = st.number_input("면적(평)", 100)
    budget = st.slider("예산(억)", 1, 100, 5)
    
    if st.button("🚀 분석 실행", type="primary"):
        key = st.secrets.get("GOOGLE_API_KEY", "").strip()
        if not key:
            st.error("API 키 없음")
        else:
            with st.spinner("분석 중..."):
                # 1차 계산
                m = calculate_metrics(area, budget, purpose)
                st.session_state['metrics'] = m
                
                # 2차 AI
                prompt = f"주소:{address}, 용도:{purpose}, 면적:{area}평, 예산:{budget}억.\n"
                prompt += f"계산결과: 평당{m['unit_cost']}만, 총비용{m['total_cost']}억, 잔액{m['balance']}억.\n"
                prompt += "이 정보를 바탕으로 아주 구체적인 개발 보고서를 작성해줘."
                
                res = call_ai_model([("user", prompt)], key)
                st.session_state['analysis_result'] = res

# 6. 메인 화면
if st.session_state['analysis_result']:
    m = st.session_state['metrics']
    
    # 대시보드 표시
    st.subheader("📊 투자 타당성 대시보드")
    c1, c2, c3 = st.columns(3)
    c1.metric("총 소요 예산", f"{m['total_cost']}억")
    c2.metric("자금 과부족", f"{m['balance']}억", delta="부족" if m['balance'] < 0 else "여유")
    c3.metric("종합 판정", m['status'])
    st.divider()
    
    # 탭 구성
    t1, t2 = st.tabs(["📄 프리미엄 보고서 (인쇄용)", "💬 AI 대화"])
    
    with t1:
        st.success("✅ 분석이 완료되었습니다. 아래 보고서를 확인하세요.")
        
        # HTML 보고서 생성
        html_report = create_html_report(address, purpose, area, budget, m, st.session_state['analysis_result'])
        
        # 화면에 렌더링 (스크롤 박스 안에)
        st.components.v1.html(html_report, height=800, scrolling=True)
        
        # [팁] 인쇄 방법 안내
        st.info("💡 **팁:** 보고서 영역에 마우스를 대고 [우클릭] -> [인쇄] -> [PDF로 저장]을 선택하면 깔끔한 PDF 파일을 얻을 수 있습니다.")

    with t2:
        for r, t in st.session_state['chat_history']:
            if r != "system":
                with st.chat_message(r): st.write(t)
        
        if q := st.chat_input("질문 입력"):
            key = st.secrets.get("GOOGLE_API_KEY", "").strip()
            with st.chat_message("user"): st.write(q)
            # 대화 맥락 유지 (이전 로그 + 새 질문)
            msgs = st.session_state['chat_history'] + [("user", q)]
            ans = call_ai_model(msgs, key)
            with st.chat_message("assistant"): st.write(ans)