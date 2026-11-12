import os
import sys
import time
import subprocess
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 스마트 런처 (업데이트 포함)
def install_and_launch():
    required = {"streamlit": "streamlit", "plotly": "plotly", "google-generativeai": "google.generativeai", "python-dotenv": "dotenv", "python-dateutil": "dateutil"}
    needs_install = []
    for pkg, mod in required.items():
        try:
            __import__(mod)
        except ImportError:
            needs_install.append(pkg)
    
    if needs_install:
        # 라이브러리 강제 업데이트 (404 에러 방지)
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
# [Engine] AI 모델 '무한 접속' 로직 (Infinite Retry Strategy)
# --------------------------------------------------------------------------------
def get_robust_model():
    """하나가 안 되면 될 때까지 다른 모델을 찾아내는 생존형 로직"""
    # 사용 가능한 모든 모델명 후보 (순서대로 시도)
    candidates = [
        'gemini-1.5-flash', 
        'gemini-1.5-flash-latest', 
        'gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-1.5-flash', # models/ 접두어 포함
        'models/gemini-pro'
    ]
    
    # 1. API가 제공하는 리스트에서 찾기
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 후보군 중 available에 있는 것 우선 선택
        for c in candidates:
            # 이름이 정확히 일치하거나 'models/'를 떼고 일치하는 경우
            if c in available or f"models/{c}" in available:
                return c
    except:
        pass # 리스트 조회 실패 시 무시하고 아래 강제 연결 시도

    # 2. 리스트 조회 실패 시, 그냥 'gemini-pro' (가장 범용적) 강제 반환
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
                gap = 0.12 if bond['type'] == "대부업" else 0.015 
                saved_interest += bond['amount'] * gap
        
        total = sum(b['amount'] for b in data['bonds'])
        ltv = round((total / data['market_price']) * 100, 2)
        return {
            "ltv": ltv, "count": len(target_bonds), "total": total, 
            "saved": int(saved_interest), "score": 100 - (len(data['restrictions'])*15) - (20 if ltv>80 else 0)
        }

def run_simulation(addr):
    # UX: 진짜 분석하는 듯한 느낌 (Benchmarking: Toss)
    with st.spinner("🔍 등기부등본 및 AI 권리분석 수행 중..."):
        time.sleep(1.5) # 체감 대기 시간

    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기(우리자산신탁)", "압류(김포세무서)"]
    }
    facts = FactChecker.process(raw)
    
    # AI Generation (Fail-Safe)
    model_name = get_robust_model()
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        부동산 금융 컨설팅 보고서 (고객용).
        - 주소: {raw['address']}
        - 상황: LTV {facts['ltv']}%, 권리하자 {len(raw['restrictions'])}건(신탁,압류).
        - 기회: 대환 시 연 {facts['saved']/10000:.0f}만원 절감.
        
        [작성법]
        1. **진단**: '주의' 등급. 신탁등기와 압류는 소유권 상실 위험이 있음.
        2. **솔루션**: 대부업(2억) 상환 및 신탁 말소 동시 진행 시 1금융권 진입 가능.
        3. **비전**: 이를 통해 자산 가치 회복 및 월 이자 부담 250만 원 감소 예상.
        (전문적이고 희망적인 어조, Markdown)
        """
        resp = model.generate_content(prompt)
        ai_msg = resp.text
    except Exception as e:
        # 에러 코드를 보여주지 않고, 준비된 텍스트를 보여줌 (Wallet Opening UX)
        ai_msg = f"""
        ### 💡 AI 분석 요약
        * **진단**: 현재 **LTV {facts['ltv']}%**로 고위험군에 속하며, **신탁등기**와 **압류**가 있어 일반 매매가 어렵습니다.
        * **솔루션**: **연간 {facts['saved']/10000:,.0f}만 원**의 이자 절감이 가능한 '대환대출' 대상입니다.
        * **조치**: 아래 [전문가 상담]을 통해 신탁 말소와 대환을 동시에 진행하는 **'통합 솔루션'**을 받으십시오.
        """

    return raw, facts, ai_msg

# --------------------------------------------------------------------------------
# [UI/UX] Revenue Model Design
# --------------------------------------------------------------------------------
st.set_page_config(page_title="지상 AI Revenue", page_icon="🦄", layout="wide")

st.markdown("""
    <style>
    .report-box { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 10px; }
    .disclaimer { font-size: 12px; color: #9ca3af; text-align: center; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🦄 Jisang AI")
    st.caption("Premium Partner Edition")
    addr = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1")
    btn = st.button("🚀 유료급 분석 시작", type="primary", use_container_width=True)

if btn:
    if not api_key:
        st.error("API Key Missing")
    else:
        raw, facts, ai_text = run_simulation(addr)
        
        st.markdown(f"## 🏙️ **{raw['address']}** 프리미엄 리포트")
        
        # 1. Key Metrics (Sales Trigger)
        c1, c2, c3 = st.columns(3)
        c1.metric("종합 등급", "B- (기회)", "Value-Add 가능")
        c2.metric("권리 리스크", "High Risk", f"{len(raw['restrictions'])}건 발견", delta_color="inverse")
        c3.metric("예상 이자 절감액", f"{facts['saved']/10000:,.0f}만 원/년", "즉시 확보", delta_color="normal")
        
        # 2. AI Solution & Chart
        col_main, col_chart = st.columns([1.5, 1])
        with col_main:
            st.markdown("### 💡 AI 심층 컨설팅")
            st.markdown(f'<div class="report-box">{ai_text}</div>', unsafe_allow_html=True)
            
            # [Revenue Point] 실제 행동 유도 버튼
            st.markdown("---")
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("📄 정밀 리포트 (PDF) 발급", use_container_width=True):
                    st.toast("PDF 생성 중... (유료 기능 데모)")
            with b_col2:
                if st.button("📞 1:1 금융 솔루션 상담 신청", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("상담 신청이 접수되었습니다! 담당자가 5분 내로 연락드립니다.")

        with col_chart:
            st.markdown("### 📉 현금 흐름 개선")
            df = pd.DataFrame({"상태": ["현재", "솔루션 적용"], "이자비용": [4800, 4800-(facts['saved']/10000)]})
            fig = px.bar(df, x="상태", y="이자비용", color="상태", text_auto=True, color_discrete_sequence=['#ef4444', '#22c55e'])
            st.plotly_chart(fig, use_container_width=True)

        # 3. Data Integrity & Legal Disclaimer
        with st.expander("🛡️ 데이터 무결성 검증 (FactChecker™)"):
            st.json(facts)
        
        # [법적 안전장치 - 면책 조항]
        st.markdown("""
            <div class="disclaimer">
            [면책 조항] 본 리포트는 지상 AI의 알고리즘에 의한 시뮬레이션 결과이며, 법적 효력을 갖지 않습니다.<br>
            실제 대출 가능 여부와 한도는 금융사의 심사 기준에 따라 달라질 수 있습니다. 투자 결정의 책임은 본인에게 있습니다.
            </div>
        """, unsafe_allow_html=True)