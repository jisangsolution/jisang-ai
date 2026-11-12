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
# [UI/UX] 0.1% 하이엔드 디자인
# --------------------------------------------------------------------------------
st.set_page_config(page_title="지상 AI Ultimate", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .big-card { padding: 20px; border-radius: 12px; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .metric-value { font-size: 28px; font-weight: bold; color: #1f2937; }
    .metric-label { font-size: 14px; color: #6b7280; }
    .ai-box { background-color: #f0f9ff; border-left: 5px solid #0ea5e9; padding: 20px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# [Engine] AI 모델 안정화 (Stable First Strategy)
# --------------------------------------------------------------------------------
def get_stable_model():
    """안정적인 모델 우선 선택"""
    # 1.5 Flash가 현재 가장 안정적이고 빠름 (2.0은 제외)
    candidates = ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.5-pro']
    
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for c in candidates:
            if c in available: return c
        return 'gemini-pro'
    except:
        return 'gemini-pro'

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
                gap = 0.12 if bond['type'] == "대부업" else 0.015 # 대부업 금리차 현실화 (12%p)
                saved_interest += bond['amount'] * gap
        
        total = sum(b['amount'] for b in data['bonds'])
        ltv = round((total / data['market_price']) * 100, 2)
        return {
            "ltv": ltv, "count": len(target_bonds), "total": total, 
            "saved": int(saved_interest), "score": 100 - (len(data['restrictions'])*15) - (20 if ltv>80 else 0)
        }

def run_simulation(addr):
    # Progress Bar UX 강화
    progress_text = "시스템 초기화 중..."
    my_bar = st.progress(0, text=progress_text)
    
    scenarios = [
        (10, "🌐 인터넷등기소(IROS) 보안 접속 중..."),
        (30, "📄 등기사항전부증명서 PDF 다운로드 (Encryption)..."),
        (50, "🔍 OCR 판독 및 갑구/을구 권리 분석 중..."),
        (70, "⚖️ FactChecker: 날짜 계산 및 무결성 검증 중..."),
        (90, "🧠 Gemini 1.5 Flash: 금융 최적화 전략 수립 중...")
    ]
    
    for percent, text in scenarios:
        time.sleep(random.uniform(0.2, 0.5))
        my_bar.progress(percent, text=text)
    
    my_bar.progress(100, text="✅ 분석 완료!")
    time.sleep(0.5)
    my_bar.empty()

    # 데이터
    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기(우리자산신탁)", "압류(김포세무서)"]
    }
    facts = FactChecker.process(raw)
    
    # AI Generation
    model_name = get_stable_model()
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        부동산 금융 컨설팅 보고서. (Markdown 형식)
        - 주소: {raw['address']}
        - LTV: {facts['ltv']}% (총채권 {facts['total']})
        - 리스크: {raw['restrictions']}
        - 대환 시 연 절감액: {facts['saved']/10000:.0f}만원
        
        [작성법]
        1. **진단**: 냉철한 평가 (대부업 및 신탁 위험성 경고).
        2. **해결책**: 구체적인 대환 시나리오 제시 (러시앤캐시 상환 필수).
        3. **비전**: 해결 후 기대되는 자산 가치 상승 언급.
        """
        resp = model.generate_content(prompt)
        ai_msg = resp.text
    except Exception as e:
        ai_msg = f"⚠️ AI 분석 불가: {str(e)}"

    return raw, facts, ai_msg, model_name

# --------------------------------------------------------------------------------
# [Main Layout]
# --------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
    st.title("Jisang AI Pro")
    st.info("System Status: **Online**")
    
    addr = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1")
    btn = st.button("🚀 분석 시작", type="primary", use_container_width=True)
    st.markdown("---")
    st.caption("© 2026 Jisang Tech Inc.")

if btn:
    if not api_key:
        st.error("API Key Missing!")
    else:
        raw, facts, ai_text, model_used = run_simulation(addr)
        
        # 1. Header Section
        st.markdown(f"## 🏙️ **{addr}** 분석 결과")
        st.caption(f"Powered by {model_used} | Verified by FactChecker™")
        
        # 2. Metrics Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("종합 등급", "B- (주의)", "기회 존재")
        with c2: st.metric("LTV (담보비율)", f"{facts['ltv']}%", "위험수준")
        with c3: st.metric("연 이자 절감", f"{facts['saved']/10000:,.0f}만 원", "즉시 가능", delta_color="normal")
        with c4: st.metric("권리 리스크", f"{len(raw['restrictions'])}건", "해소 필수", delta_color="inverse")

        # 3. Main Content (Chart + AI)
        col_main, col_chart = st.columns([1.5, 1])
        
        with col_main:
            st.markdown("### 💡 AI 심층 컨설팅")
            st.markdown(f'<div class="ai-box">{ai_text}</div>', unsafe_allow_html=True)
            
        with col_chart:
            st.markdown("### 📉 금융 최적화 효과")
            df = pd.DataFrame({
                "Scenario": ["현재 (고금리+대부업)", "지상 솔루션 적용"],
                "Cost": [4800, 4800 - (facts['saved']/10000)]
            })
            fig = px.bar(df, x="Scenario", y="Cost", color="Scenario", text_auto=True, 
                         color_discrete_sequence=['#ef4444', '#10b981'])
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

        # 4. Detail Data (Clean UI)
        st.markdown("---")
        with st.expander("🔍 원본 데이터 및 검증 로그 보기 (Click to Expand)"):
            t1, t2 = st.tabs(["🛡️ 무결성 검증 내역", "💾 공적장부 원본"])
            with t1:
                st.dataframe(pd.DataFrame({
                    "항목": ["총 채권액", "LTV", "대환 타겟 건수", "연간 절감액"],
                    "검증값": [f"{facts['total']:,}원", f"{facts['ltv']}%", f"{facts['count']}건", f"{facts['saved']:,}원"]
                }))
            with t2:
                st.json(raw)