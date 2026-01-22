import streamlit as st
import requests
import pandas as pd
import json
import re
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", layout="wide", page_icon="🏢")
st.title("🏢 지상 AI: 부동산 개발 타당성 & 수지분석")
st.caption("Ver 8.1 - Robust Scoring & JSON Parsing")

# 세션 초기화
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'metrics' not in st.session_state:
    st.session_state['metrics'] = {}
if 'scores' not in st.session_state:
    st.session_state['scores'] = {"입지": 0, "수요": 0, "수익성": 0, "안정성": 0, "총점": 0}

# 2. 수지분석 로직 (Python Logic)
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

# 3. AI 분석 로직 (JSON 강제)
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

# 4. [핵심 수정] 점수 추출 로직 (JSON 파싱)
def extract_data(full_text):
    # 기본값
    default_scores = {"입지": 50, "수요": 50, "수익성": 50, "안정성": 50, "총점": 50}
    html_content = full_text
    
    try:
        # 1. JSON 블록 찾기 (```json ... ```)
        json_match = re.search(r"```json\s*({.*?})\s*```", full_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            scores = json.loads(json_str)
            # HTML은 JSON 블록을 제외한 나머지 부분 (혹은 AI가 따로 줄 경우)
            # 이번 프롬프트에서는 JSON과 HTML을 명확히 분리 요청함
            parts = full_text.split("```json")
            if len(parts) > 0:
                # JSON 블록 앞이나 뒤에 있는 텍스트 중 HTML 태그가 있는 것을 찾음
                html_candidate = re.sub(r"```json.*?```", "", full_text, flags=re.DOTALL)
                html_content = html_candidate.strip()
            return scores, html_content
        else:
            return default_scores, full_text
            
    except Exception as e:
        print(f"Parsing Error: {e}")
        return default_scores, full_text

# 5. HTML 리포트 디자인
def create_html_report(addr, purp, area, bdgt, metrics, ai_text, scores):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 순수 HTML만 남기기 위해 마크다운 기호 제거 (안전장치)
    ai_text = ai_text.replace("```html", "").replace("```", "")
    
    html = """
    <style>
        .report-container { font-family: 'Malgun Gothic', sans-serif; padding: 40px; border: 1px solid #ddd; background: white; color: #333; }
        .header { border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 30px; }
        .title { font-size: 28px; font-weight: bold; color: #1E3A8A; }
        .meta { font-size: 14px; color: #666; margin-top: 5px; }
        .kpi-box { display: flex; justify-content: space-between; background: #F3F4F6; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .kpi-item { text-align: center; flex: 1; }
        .kpi-value { font-size: 22px; font-weight: bold; color: #1E3A8A; }
        .kpi-label { font-size: 13px; color: #555; margin-top: 5px; }
        .score-box { background: #E0E7FF; padding: 15px; text-align: center; border-radius: 10px; margin-bottom: 20px; }
        .score-val { font-size: 36px; font-weight: 900; color: #1E3A8A; }
        
        /* 테이블 스타일 강제 적용 */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: bold; color: #1E3A8A; }
        
        h3 { color: #1E3A8A; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-top: 30px; }
        li { margin-bottom: 5px; }
        .footer { margin-top: 50px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
    """
    
    html += f"<div class='report-container'>"
    html += f"<div class='header'><div class='title'>부동산 개발 타당성 분석 보고서</div>"
    html += f"<div class='meta'>분석 일자: {today} | 작성: 지상 AI 시스템</div></div>"
    
    # 점수 표시
    html += f"<div class='score-box'><div class='score-label'>AI 투자 매력도 종합 점수</div>"
    html += f"<div class='score-val'>{scores.get('총점', 0)}점 / 100점</div></div>"
    
    # KPI 표시
    html += f"<div class='kpi-box'>"
    html += f"<div class='kpi-item'><div class='kpi-value'>{metrics['unit_cost']}만</div><div class='kpi-label'>평당 건축비</div></div>"
    html += f"<div class='kpi-item'><div class='kpi-value'>{metrics['total_cost']}억</div><div class='kpi-label'>총 소요 비용</div></div>"
    color = "red" if metrics['balance'] < 0 else "green"
    html += f"<div class='kpi-item'><div class='kpi-value' style='color:{color}'>{metrics['balance']}억</div><div class='kpi-label'>자금 과부족</div></div>"
    html += f"</div>"
    
    html += f"<div class='content'>{ai_text}</div>"
    html += f"<div class='footer'>Powered by Jisang AI | 본 보고서는 참고용입니다.</div></div>"
    
    return html

# 6. 사이드바 UI
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
            with st.spinner("AI가 수익성 분석 및 점수를 산출 중입니다..."):
                # 1. 수지분석
                m = calculate_metrics(area, budget, purpose)
                st.session_state['metrics'] = m
                
                # 2. AI 프롬프트 (JSON + HTML 강제)
                prompt = f"""
                당신은 부동산 투자 심사역입니다.
                주소:{address}, 용도:{purpose}, 면적:{area}평, 예산:{budget}억.
                (계산결과: 평당{m['unit_cost']}만, 총비용{m['total_cost']}억, 잔액{m['balance']}억)
                
                [매우 중요: 출력 형식을 반드시 지키세요]
                
                첫 번째로, 아래 JSON 형식으로 점수 데이터를 출력하세요. (반드시 ```json 으로 감쌀 것)
                ```json
                {{
                    "입지": 85,
                    "수요": 70,
                    "수익성": 60,
                    "안정성": 75,
                    "총점": 72
                }}
                ```
                
                두 번째로, 그 아래에 보고서 본문을 순수 HTML 태그로 작성하세요.
                (<h3>, <p>, <table>, <ul> 태그 사용. 마크다운 사용 금지)
                내용 순서: 사업개요 -> 입지분석 -> 수익성분석 -> 리스크 및 제언
                """
                
                full_response = call_ai_model([("user", prompt)], key)
                
                # 데이터 분리 (JSON 점수 / HTML 본문)
                scores, clean_html = extract_data(full_response)
                
                st.session_state['scores'] = scores
                st.session_state['analysis_result'] = clean_html

# 7. 메인 대시보드
if st.session_state['analysis_result']:
    s = st.session_state['scores']
    
    # 상단 대시보드
    st.subheader("🏆 AI 투자 매력도 진단")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        total = s.get('총점', 0)
        st.metric("종합 투자 점수", f"{total}점", delta="우수" if total >= 80 else "보통")
        grade = "S" if total >= 90 else "A" if total >= 80 else "B" if total >= 70 else "C"
        st.info(f"투자 등급: **{grade} 등급**")
        
    with c2:
        # 차트 데이터 구성
        chart_df = pd.DataFrame({
            '점수': [s.get('입지',0), s.get('수요',0), s.get('수익성',0), s.get('안정성',0)]
        }, index=['입지', '수요', '수익성', '안정성'])
        st.bar_chart(chart_df)
    
    st.divider()
    
    t1, t2 = st.tabs(["📄 프리미엄 보고서", "💬 AI 파트너"])
    
    with t1:
        # HTML 렌더링
        html_report = create_html_report(address, purpose, area, budget, st.session_state['metrics'], st.session_state['analysis_result'], s)
        st.components.v1.html(html_report, height=800, scrolling=True)
        
    with t2:
        # 대화형 인터페이스
        for r, t in st.session_state['chat_history']:
            if r != "system":
                with st.chat_message(r): st.write(t)
        
        if q := st.chat_input("추가 질문하기"):
            key = st.secrets.get("GOOGLE_API_KEY", "").strip()
            with st.chat_message("user"): st.write(q)
            msgs = st.session_state['chat_history'] + [("user", q)]
            ans = call_ai_model(msgs, key)
            with st.chat_message("assistant"): st.write(ans)
            st.session_state['chat_history'].append(("user", q))
            st.session_state['chat_history'].append(("assistant", ans))