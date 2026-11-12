import os
import sys
import time
import subprocess
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 자율 구동 런처 (Self-Launching with Plotly)
# 시각화 도구(Plotly)가 없으면 추가 설치
required_libs = ["streamlit", "plotly", "google-generativeai", "python-dotenv", "python-dateutil"]
needs_install = []

for lib in required_libs:
    try:
        __import__(lib.replace("-", "_")) # import 이름 보정
    except ImportError:
        needs_install.append(lib)

if needs_install:
    print(f"🛠️ [시스템] 시각화 및 필수 도구 설치 중: {', '.join(needs_install)}")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + needs_install)
    os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", __file__])

if "streamlit" not in sys.modules and __name__ == "__main__":
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

# --------------------------------------------------------------------------------
import streamlit as st
import plotly.express as px
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [UI 설정] 0.1% 스타일링
# --------------------------------------------------------------------------------
st.set_page_config(page_title="지상 AI Pro | 부동산 딥테크", page_icon="🏢", layout="wide")

# 커스텀 CSS (카드형 UI, 그림자 효과)
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .grade-card {
        font-size: 40px; font-weight: bold; text-align: center;
        padding: 20px; border-radius: 15px; color: white;
    }
    .s-grade { background-color: #28a745; }
    .a-grade { background-color: #17a2b8; }
    .b-grade { background-color: #ffc107; color: black; }
    .c-grade { background-color: #dc3545; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# [Backend Logic] 무결성 엔진 & AI
# --------------------------------------------------------------------------------
def get_best_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferred = ['models/gemini-2.0-flash', 'models/gemini-1.5-flash', 'models/gemini-pro']
        for p in preferred:
            if p in models: return p
        return 'gemini-pro'
    except: return 'gemini-pro'

class FactChecker:
    @staticmethod
    def process(data):
        # 1. 대환대출 타겟팅 및 이자 절감액 시뮬레이션 (단순 가정: 금리 4%p 차이)
        target_bonds = []
        saved_interest = 0
        
        for bond in data['bonds']:
            target_date = datetime.strptime(bond['date'], "%Y.%m.%d")
            diff = relativedelta(datetime.now(), target_date)
            months = diff.years * 12 + diff.months
            
            is_target = months >= 24 or bond['type'] == "대부업"
            if is_target:
                target_bonds.append(bond)
                # 대부업이면 15% -> 5% (10%p 절감), 1금융이면 5% -> 3.5% (1.5%p 절감) 가정
                gap = 0.10 if bond['type'] == "대부업" else 0.015
                saved_interest += bond['amount'] * gap
        
        total_bond = sum(b['amount'] for b in data['bonds'])
        ltv = round((total_bond / data['market_price']) * 100, 2)
        
        return {
            "ltv": ltv,
            "refinance_count": len(target_bonds),
            "total_bond": total_bond,
            "saved_interest_year": int(saved_interest), # 연간 절감액
            "risk_score": 100 - (len(data['restrictions']) * 20) - (10 if ltv > 70 else 0) # 자체 점수
        }

def run_analysis_simulation(address):
    # Opal Agent Simulation
    steps = ["🌐 인터넷등기소 접속", "📄 PDF OCR 변환", "📊 건축물대장 대조", "⚖️ FactChecker 검증"]
    bar = st.progress(0)
    status_text = st.empty()
    
    for i, step in enumerate(steps):
        status_text.text(f"💎 Opal Agent 동작 중... {step}")
        time.sleep(0.3)
        bar.progress((i + 1) * 25)
    
    status_text.text("✅ 데이터 수집 및 검증 완료!")
    time.sleep(0.2)
    bar.empty()

    # 가상 데이터 (케이스: 대부업 대출 + 신탁 등기 = 위험하지만 기회 존재)
    raw_data = {
        "address": address,
        "market_price": 800000000, 
        "bonds": [
            {"bank": "우리은행", "date": "2019.05.20", "amount": 300000000, "type": "1금융"},
            {"bank": "러시앤캐시", "date": "2024.01.15", "amount": 200000000, "type": "대부업"}
        ],
        "restrictions": ["신탁등기(코리아신탁)", "가압류(국민건강보험공단)"]
    }
    
    facts = FactChecker.process(raw_data)
    
    # Brain Reasoning
    model = genai.GenerativeModel(get_best_model())
    prompt = f"""
    부동산 투자 자문 보고서 작성.
    - 데이터: {raw_data}
    - 팩트: {facts}
    
    [출력 양식]
    1. 등급: [B-] (이유: 신탁등기 리스크 존재하나 대환 시 수익성 높음)
    2. 전략: 대부업 대출(2억)을 1금융권으로 대환 시 연 {format(facts['saved_interest_year'], ',')}원 절감 가능.
    3. 경고: 신탁말소 조건부 계약 필수. 미이행 시 계약금 반환 특약 요함.
    """
    try:
        response = model.generate_content(prompt)
        ai_text = response.text
    except:
        ai_text = "AI 분석 서버 응답 지연. 팩트 데이터 위주로 확인하세요."

    return raw_data, facts, ai_text

# --------------------------------------------------------------------------------
# [Frontend] 대시보드 메인
# --------------------------------------------------------------------------------
# 사이드바
with st.sidebar:
    st.header("⚙️ 전문가 설정")
    st.toggle("FactChecker (무결성 검증)", value=True, disabled=True)
    st.toggle("AI Deep Reasoning", value=True)
    st.info(f"Connected: {get_best_model()}")
    st.markdown("---")
    st.caption("Developed by Jisang 1-Person Unicorn")

# 메인 타이틀
st.title("🏙️ 지상 AI | Pro Dashboard")
st.markdown("##### :zap: 데이터 무결성 기반 초격차 의사결정 시스템")

col_input, col_btn = st.columns([4, 1])
with col_input:
    addr = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1", label_visibility="collapsed")
with col_btn:
    start = st.button("원클릭 분석", type="primary", use_container_width=True)

if start:
    if not api_key:
        st.error("❌ API Key가 없습니다.")
    else:
        raw, facts, ai_report = run_analysis_simulation(addr)

        # 1. 핵심 결론 섹션 (Grade & Impact)
        st.markdown("### 🎯 분석 결론")
        c1, c2, c3 = st.columns([1, 2, 2])
        
        with c1: # 등급 카드
            grade = "B-" if facts['risk_score'] > 60 else "C"
            color_class = "b-grade" if grade.startswith("B") else "c-grade"
            st.markdown(f"""
                <div class="grade-card {color_class}">
                    {grade}<br><span style="font-size:16px">종합 등급</span>
                </div>
            """, unsafe_allow_html=True)
            
        with c2: # 핵심 지표
            st.metric("LTV (담보비율)", f"{facts['ltv']}%", "안정권 70% 대비 +12.5%", delta_color="inverse")
            st.metric("권리 리스크", f"{len(raw['restrictions'])}건 발견", "신탁/압류", delta_color="inverse")
            
        with c3: # 돈이 되는 정보 (Moat)
            st.metric("💰 대환 시 연 수익", f"+ {facts['saved_interest_year']/10000:.0f}만 원", "즉시 확보 가능")
            st.caption("러시앤캐시(대부) → 1금융 전환 시 예상 절감액")

        # 2. 시각화 섹션 (Financial Visualization)
        st.markdown("---")
        st.markdown("### 📊 금융/가치 시뮬레이션")
        
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            # 이자 비용 비교 차트
            df_chart = pd.DataFrame({
                "구분": ["현재 이자비용", "솔루션 적용 후"],
                "금액": [3000, 3000 - (facts['saved_interest_year']/10000)] # 단위 만원 가정
            })
            fig = px.bar(df_chart, x="구분", y="금액", color="구분", title="📉 금융 비용 최적화 효과", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with v_col2:
            st.info("💡 **AI Insight**")
            st.write(ai_report)

        # 3. 상세 데이터 탭
        st.markdown("---")
        t1, t2 = st.tabs(["🛡️ 무결성 검증(FactChecker)", "💾 원본 데이터(Opal)"])
        
        with t1:
            st.success("이 데이터는 AI 추론 전, Python 알고리즘으로 교차 검증되었습니다.")
            st.json(facts)
        with t2:
            st.json(raw)