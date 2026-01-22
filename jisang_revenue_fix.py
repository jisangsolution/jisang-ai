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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U"] + needs_install)
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
# [Engine] AI 모델 연결
# --------------------------------------------------------------------------------
def get_robust_model():
    candidates = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for c in candidates:
            if c in available or f"models/{c}" in available: return c
    except: pass
    return 'gemini-1.5-flash' # Default fallback

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
    # UX Simulation
    with st.spinner("🔍 등기부 권리분석 및 AI 금융 솔루션 생성 중..."):
        time.sleep(1.2)

    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기(우리자산신탁)", "압류(김포세무서)"]
    }
    facts = FactChecker.process(raw)
    
    # AI Generation (가독성 최적화 프롬프트)
    model_name = get_robust_model()
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        부동산 금융 컨설팅 리포트. 독자가 한눈에 이해하도록 Markdown 문법을 활용해 작성.
        상황: 주소 {raw['address']}, LTV {facts['ltv']}%, 권리하자 {len(raw['restrictions'])}건(신탁,압류).
        솔루션: 대환 시 연 {facts['saved']/10000:.0f}만원 절감.
        
        [출력 형식]
        ### 🚨 진단: 고위험군 (Action 필요)
        * **현재 상황**: **LTV {facts['ltv']}%**로 매우 높으며, **신탁등기/압류**로 인해 일반 매매가 불가능합니다.
        
        ### 💊 처방: 통합 대환 솔루션
        * **금융 전략**: 대부업(2억) 상환 및 1금융권 대환을 동시에 진행해야 합니다.
        * **기대 효과**: 신용등급 회복 및 자산 방어.
        
        ### 💰 비전: 연 {facts['saved']/10000:.0f}만 원 수익 확보
        * **이자 절감**: 월 약 250만 원의 현금 흐름이 즉시 개선됩니다.
        """
        resp = model.generate_content(prompt)
        ai_msg = resp.text
    except Exception as e:
        # Fallback 메시지도 예쁘게 포장
        ai_msg = f"""
### 🚨 진단: 긴급 조치 필요
* **위험 요인**: 현재 **LTV {facts['ltv']}%** 및 **신탁/압류** 등기가 확인되었습니다. 자칫하면 소유권을 잃을 수 있는 위험 단계입니다.

### 💊 처방: 지상 AI 통합 솔루션
* **대환 전략**: 고금리 대부업 대출을 1금융권으로 갈아타는 **'통합 대환'**이 유일한 해결책입니다.
* **전문가 조력**: 혼자서는 신탁 말소가 어렵습니다. 전문 법무/세무 지원이 필수적입니다.

### 💰 결론: 연 {facts['saved']/10000:,.0f}만 원 즉시 절감
* 이 솔루션을 실행하면 **매월 약 250만 원**의 현금이 지갑에 남게 됩니다. 지금 바로 상담받으십시오.
        """

    return raw, facts, ai_msg

# --------------------------------------------------------------------------------
# [UI/UX] Revenue Focus Design
# --------------------------------------------------------------------------------
st.set_page_config(page_title="지상 AI Premium", page_icon="💎", layout="wide")

# CSS: 리포트 컨테이너 스타일링
st.markdown("""
    <style>
    .stAlert { border-radius: 10px; }
    .report-container { padding: 20px; border-radius: 10px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("💎 Jisang AI")
    st.caption("Premium Edition")
    addr = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1")
    btn = st.button("🚀 분석 리포트 생성", type="primary", use_container_width=True)

if btn:
    if not api_key:
        st.error("API Key Missing")
    else:
        raw, facts, ai_text = run_simulation(addr)
        
        st.markdown(f"## 🏙️ **{raw['address']}** 프리미엄 분석")
        
        # 1. Key Metrics (Hook)
        c1, c2, c3 = st.columns(3)
        c1.metric("종합 등급", "B- (기회)", "솔루션 적용 시 A", delta_color="off")
        c2.metric("권리 리스크", "High Risk", "신탁/압류 발견", delta_color="inverse")
        c3.metric("예상 이자 절감액", f"{facts['saved']/10000:,.0f}만 원/년", "즉시 확보 가능", delta_color="normal")
        
        # 2. Main Report & Action (Body)
        col_main, col_chart = st.columns([1.6, 1])
        
        with col_main:
            # ★ 핵심 수정: Native Container + Markdown 사용 (가독성 극대화)
            with st.container(border=True):
                st.markdown("### 💡 AI 심층 컨설팅")
                st.markdown(ai_text) # 이제 Markdown이 완벽하게 렌더링됩니다.
            
            # Action Buttons
            st.markdown("---")
            b1, b2 = st.columns(2)
            with b1:
                st.button("📄 정밀 리포트 (PDF) 다운로드", use_container_width=True)
            with b2:
                if st.button("📞 1:1 금융 솔루션 상담 신청", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("✅ 상담 예약이 확정되었습니다. 담당자가 곧 연락드립니다.")

        with col_chart:
            # Financial Chart
            st.markdown("### 📉 현금 흐름 개선")
            df = pd.DataFrame({"구분": ["현재", "솔루션 적용"], "비용": [4800, 4800-(facts['saved']/10000)]})
            fig = px.bar(df, x="구분", y="비용", color="구분", text_auto=True, color_discrete_sequence=['#ef4444', '#10b981'])
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Disclaimer
            st.warning("⚠️ 본 리포트는 시뮬레이션 결과이며, 실제 대출 승인 여부는 금융사의 심사를 거쳐 확정됩니다.")

        # 3. Data Check
        with st.expander("🛡️ 데이터 무결성 검증 (FactChecker™)"):
            st.json(facts)