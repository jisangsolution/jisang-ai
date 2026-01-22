import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", layout="wide", page_icon="🏢")
st.title("🏢 지상 AI: 부동산 개발 타당성 & 수지분석")
st.caption("Ver 8.0 - AI Scoring & Visual Analytics")

# 세션 초기화
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'metrics' not in st.session_state:
    st.session_state['metrics'] = {}
if 'scores' not in st.session_state:
    st.session_state['scores'] = {}

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

# 3. AI 분석 로직 (점수 파싱 기능 추가)
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

# 4. 점수 파싱 헬퍼 함수
def parse_scores(text):
    # AI 응답에서 "점수: 80" 같은 패턴을 찾음
    try:
        # 기본값
        scores = {"입지": 50, "수요": 50, "수익성": 50, "안정성": 50, "총점": 50}
        
        # 정규표현식으로 추출 시도
        lines = text.split('\n')
        for line in lines:
            if "총점" in line and ":" in line:
                scores["총점"] = int(re.sub(r'[^0-9]', '', line.split(':')[1]))
            if "입지" in line and ":" in line:
                scores["입지"] = int(re.sub(r'[^0-9]', '', line.split(':')[1]))
            if "수요" in line and ":" in line:
                scores["수요"] = int(re.sub(r'[^0-9]', '', line.split(':')[1]))
            if "수익성" in line and ":" in line:
                scores["수익성"] = int(re.sub(r'[^0-9]', '', line.split(':')[1]))
            if "안정성" in line and ":" in line:
                scores["안정성"] = int(re.sub(r'[^0-9]', '', line.split(':')[1]))
        return scores
    except:
        return {"입지": 0, "수요": 0, "수익성": 0, "안정성": 0, "총점": 0}

# 5. HTML 리포트 생성기
def create_html_report(addr, purp, area, bdgt, metrics, ai_text, scores):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    html = """
    <style>
        .report-container { font-family: 'Malgun Gothic', sans-serif; padding: 40px; border: 1px solid #ddd; background: white; color: #333; }
        .header { border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 30px; }
        .title { font-size: 28px; font-weight: bold; color: #1E3A8A; }
        .meta { font-size: 14px; color: #666; margin-top: 5px; }
        .section-title { font-size: 20px; font-weight: bold; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; }
        .kpi-box { display: flex; justify-content: space-between; background: #F3F4F6; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .kpi-item { text-align: center; flex: 1; }
        .kpi-value { font-size: 22px; font-weight: bold; color: #1E3A8A; }
        .kpi-label { font-size: 13px; color: #555; margin-top: 5px; }
        .score-box { background: #E0E7FF; padding: 15px; text-align: center; border-radius: 10px; margin-bottom: 20px; }
        .score-val { font-size: 36px; font-weight: 900; color: #1E3A8A; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }
        th { background-color: #f0f2f5; font-weight: bold; color: #333; }
        .content { line-height: 1.6; font-size: 15px; }
        .footer { margin-top: 50px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
    """
    
    html += f"<div class='report-container'>"
    html += f"<div class='header'><div class='title'>부동산 개발 타당성 분석 보고서</div>"
    html += f"<div class='meta'>분석 일자: {today} | 작성: 지상 AI 시스템</div></div>"
    
    # 종합 점수 섹션
    html += f"<div class='score-box'><div class='score-label'>AI 투자 매력도 종합 점수</div>"
    html += f"<div class='score-val'>{scores.get('총점', 0)}점 / 100점</div></div>"
    
    html += f"<div class='section-title'>1. 사업 개요 및 투자 지표</div>"
    html += f"<div class='kpi-box'>"
    html += f"<div class='kpi-item'><div class='kpi-value'>{metrics['unit_cost']}만</div><div class='kpi-label'>평당 건축비</div></div>"
    html += f"<div class='kpi-item'><div class='kpi-value'>{metrics['total_cost']}억</div><div class='kpi-label'>총 소요 비용</div></div>"
    color = "red" if metrics['balance'] < 0 else "green"
    html += f"<div class='kpi-item'><div class='kpi-value' style='color:{color}'>{metrics['balance']}억</div><div class='kpi-label'>자금 과부족</div></div>"
    html += f"</div>"
    html += f"<ul><li><b>주소:</b> {addr}</li><li><b>용도:</b> {purp}</li><li><b>면적:</b> {area}평</li><li><b>예산:</b> {bdgt}억 원</li></ul>"
    
    html += f"<div class='section-title'>2. 전문가 심층 분석</div>"
    html += f"<div class='content'>{ai_text}</div>"
    html += f"<div class='footer'>Powered by Jisang AI | 본 보고서는 참고용입니다.</div></div>"
    
    return html

# 6. 사이드바
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
            with st.spinner("1단계: 수지 분석 중..."):
                m = calculate_metrics(area, budget, purpose)
                st.session_state['metrics'] = m
            
            with st.spinner("2단계: AI가 점수를 매기고 보고서를 작성 중..."):
                # 프롬프트: 점수 산출 요청 추가
                prompt = f"""
                당신은 냉철한 부동산 심사역입니다.
                주소:{address}, 용도:{purpose}, 면적:{area}평, 예산:{budget}억.
                (계산결과: 평당{m['unit_cost']}만, 총비용{m['total_cost']}억, 잔액{m['balance']}억)
                
                [작성 규칙]
                1. 맨 첫 줄에 반드시 아래 형식으로 점수를 매기세요. (0~100점)
                   <점수데이터>
                   입지: 00
                   수요: 00
                   수익성: 00
                   안정성: 00
                   총점: 00
                   </점수데이터>
                
                2. 그 다음 줄부터는 보고서 본문을 **순수 HTML 태그**로 작성하세요. (<h3>, <p>, <table>, <ul> 등)
                3. 마크다운(##, **)은 절대 사용 금지.
                4. 입지, 수익성, 리스크, 종합의견 순으로 작성.
                """
                
                full_text = call_ai_model([("user", prompt)], key)
                
                # 점수와 본문 분리
                scores = parse_scores(full_text)
                # 점수 데이터 부분 제거하고 순수 HTML만 남기기 (간단 처리)
                clean_html = re.sub(r'<점수데이터>.*?</점수데이터>', '', full_text, flags=re.DOTALL).strip()
                
                st.session_state['scores'] = scores
                st.session_state['analysis_result'] = clean_html

# 7. 메인 화면
if st.session_state['analysis_result']:
    m = st.session_state['metrics']
    s = st.session_state['scores']
    
    # 1. 상단 스코어 보드
    st.subheader("🏆 AI 투자 매력도 진단")
    
    col_score, col_chart = st.columns([1, 2])
    
    with col_score:
        # 총점 표시
        st.metric("종합 투자 점수", f"{s.get('총점',0)}점", delta="우수" if s.get('총점',0) >= 80 else "보통")
        
        # 등급 배지
        grade = "S" if s.get('총점',0) >= 90 else "A" if s.get('총점',0) >= 80 else "B" if s.get('총점',0) >= 70 else "C"
        st.info(f"투자 등급: **{grade} 등급**")
        
    with col_chart:
        # 막대 차트 시각화
        chart_data = pd.DataFrame({
            '항목': ['입지', '수요', '수익성', '안정성'],
            '점수': [s.get('입지',0), s.get('수요',0), s.get('수익성',0), s.get('안정성',0)]
        })
        st.bar_chart(chart_data.set_index('항목'))
        
    st.divider()
    
    # 2. 탭 구성
    t1, t2 = st.tabs(["📄 프리미엄 보고서", "💬 AI 파트너"])
    
    with t1:
        html_report = create_html_report(address, purpose, area, budget, m, st.session_state['analysis_result'], s)
        st.components.v1.html(html_report, height=800, scrolling=True)

    with t2:
        for r, t in st.session_state['chat_history']:
            if r != "system":
                with st.chat_message(r): st.write(t)
        
        if q := st.chat_input("궁금한 점을 물어보세요"):
            key = st.secrets.get("GOOGLE_API_KEY", "").strip()
            with st.chat_message("user"): st.write(q)
            msgs = st.session_state['chat_history'] + [("user", q)]
            ans = call_ai_model(msgs, key)
            with st.chat_message("assistant"): st.write(ans)
            st.session_state['chat_history'].append(("user", q))
            st.session_state['chat_history'].append(("assistant", ans))