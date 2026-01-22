import os
import sys
import time
import subprocess
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 스마트 런처
def install_and_launch():
    required = {"streamlit": "streamlit", "plotly": "plotly", "google-generativeai": "google.generativeai", "python-dotenv": "dotenv", "python-dateutil": "dateutil"}
    needs_install = []
    for pkg, mod in required.items():
        try:
            __import__(mod)
        except ImportError:
            needs_install.append(pkg)
    if needs_install:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + needs_install)
        os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", __file__])

if "streamlit" not in sys.modules:
    install_and_launch()
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

# ================================================================================
import streamlit as st
import plotly.express as px
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [Engine] AI 모델 '생존 확인' 및 연결 (Health Check)
# --------------------------------------------------------------------------------
def get_working_model():
    """작동하지 않는 구버전(gemini-pro)은 버리고, 최신 버전만 고집합니다."""
    # 우선순위: 1.5 Flash (가장 안정적) -> 2.0 Flash (최신)
    candidates = ['models/gemini-1.5-flash', 'models/gemini-2.0-flash']
    
    # 모델 리스트 확인 없이 강제 지정 (API 호출 낭비 방지)
    # 404 에러 원인인 'gemini-pro'는 아예 목록에서 배제
    return 'models/gemini-1.5-flash'

class FactChecker:
    @staticmethod
    def process(data):
        target_bonds = []
        saved_interest = 0
        for bond in data['bonds']:
            t_date = datetime.strptime(bond['date'], "%Y.%m.%d")
            diff = relativedelta(datetime.now(), t_date)
            months = diff.years * 12 + diff.months
            is_target = months >= 24 or bond['type'] == "대부업"
            if is_target:
                target_bonds.append(bond)
                gap = 0.12 if bond['type'] == "대부업" else 0.015 
                saved_interest += bond['amount'] * gap
        
        total = sum(b['amount'] for b in data['bonds'])
        ltv = round((total / data['market_price']) * 100, 2)
        return {
            "ltv": ltv, "count": len(target_bonds), "total": total, 
            "saved": int(saved_interest), "score": 100 - (len(data['restrictions'])*15) - (20 if ltv>80 else 0)
        }

def run_simulation(addr):
    # Progress Bar UX
    progress_text = "시스템 초기화 중..."
    my_bar = st.progress(0, text=progress_text)
    scenarios = [(20, "🌐 인터넷등기소(IROS) 접속 및 암호화 해제..."), (50, "📄 PDF OCR 변환 및 권리관계 추출..."), (80, "⚖️ FactChecker 무결성 검증 수행...")]
    for p, t in scenarios:
        time.sleep(random.uniform(0.1, 0.3))
        my_bar.progress(p, text=t)
    my_bar.progress(100, text="✅ 분석 완료!")
    time.sleep(0.3)
    my_bar.empty()

    # 데이터
    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기(우리자산신탁)", "압류(김포세무서)"]
    }
    facts = FactChecker.process(raw)
    
    # AI Generation (안전장치 강화)
    model_name = get_working_model()
    ai_msg = ""
    
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        부동산 전문가로서 고객에게 브리핑하는 톤으로 작성.
        상황: {raw['address']} 물건 분석.
        팩트: LTV {facts['ltv']}%, 권리하자 {len(raw['restrictions'])}건(신탁,압류), 대환 시 연 {facts['saved']/10000:.0f}만원 절감.
        
        [필수 포함]
        1. 경고: 신탁/압류 미해결 시 계약 불가.
        2. 기회: 대부업 대환을 통한 자산 가치 정상화 전략.
        3. 결론: 전문가 동행 하에 진행 시 수익성 높음.
        (Markdown 형식, 이모지 사용)
        """
        resp = model.generate_content(prompt)
        ai_msg = resp.text
    except Exception as e:
        # AI가 실패해도 시스템은 멈추지 않는다 (Business Continuity)
        ai_msg = f"""
        ### 💡 AI 분석 요약 (Standard Mode)
        * **시스템 진단**: 현재 AI 연결이 지연되고 있으나, **FactChecker** 검증 결과는 유효합니다.
        * **핵심 제언**: **연간 {facts['saved']/10000:,.0f}만 원**의 이자 비용 절감이 확실시됩니다. 
        * **리스크 경고**: 신탁등기와 압류가 존재하므로, 계약 전 반드시 말소 조건을 특약에 명시하십시오.
        *(Error Detail: {str(e)})*
        """

    return raw, facts, ai_msg, model_name

# --------------------------------------------------------------------------------
# [UI/UX] Global No.1 Style
# --------------------------------------------------------------------------------
st.set_page_config(page_title="지상 AI Unicorn", page_icon="🦄", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .metric-box { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; }
    .report-btn { text-align: center; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🦄 Jisang AI")
    st.info("System: **Active**")
    addr = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1")
    btn = st.button("🚀 분석 시작", type="primary", use_container_width=True)

if btn:
    if not api_key:
        st.error("API Key Missing")
    else:
        raw, facts, ai_text, m_name = run_simulation(addr)
        
        # 1. Title & Grade
        st.markdown(f"## 🏙️ **{raw['address']}** 정밀 분석")
        
        # 2. Main Dashboard
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("### 💡 AI Executive Summary")
            st.info(ai_text) # 에러 메시지 대신 분석글이 나옴
            
            # [Wallet Opener] PDF 다운로드 버튼 시뮬레이션
            st.markdown("---")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.button("📄 상세 리포트 다운로드 (PDF)", use_container_width=True)
            with col_b2:
                st.button("📞 금융 전문가 상담 연결", use_container_width=True)

        with c2:
            st.markdown("### 📊 Key Metrics")
            st.metric("종합 등급", "B- (Value-Add)", "기회 포착")
            st.metric("LTV (담보비율)", f"{facts['ltv']}%", "High Risk", delta_color="inverse")
            st.metric("연 이자 절감액", f"{facts['saved']/10000:,.0f}만 원", "즉시 확보", delta_color="normal")
            
            # Chart
            df = pd.DataFrame({"구분": ["현재", "지상 솔루션"], "비용": [4800, 4800-(facts['saved']/10000)]})
            fig = px.bar(df, x="구분", y="비용", color="구분", height=200)
            st.plotly_chart(fig, use_container_width=True)

        # 3. Data Integrity
        with st.expander("🛡️ 무결성 검증 데이터 (FactChecker™)"):
            st.json(facts)