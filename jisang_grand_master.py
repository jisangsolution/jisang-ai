import os
import sys
import time
import subprocess
import random
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 스마트 오토 런처
def install_and_launch():
    required = {
        "streamlit": "streamlit", "plotly": "plotly", 
        "google-generativeai": "google.generativeai", 
        "python-dotenv": "dotenv", "python-dateutil": "dateutil",
        "fpdf": "fpdf"
    }
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
import google.generativeai as genai
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [Engine 1] 리포트 엔진 (PDF & Excel)
# --------------------------------------------------------------------------------
class ReportEngine:
    @staticmethod
    def create_safe_pdf(facts):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Jisang AI | Executive Summary", 0, 1, 'C')
        pdf.ln(10)
        
        asset_id = f"ASSET-{random.randint(10000, 99999)}"
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Ref ID: {asset_id}", 0, 1)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "1. Financial Analysis", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"- Score: {facts['score']}/100", 0, 1)
        pdf.cell(0, 10, f"- LTV: {facts['ltv']}%", 0, 1)
        pdf.cell(0, 10, f"- Debt: {facts['total']:,} KRW", 0, 1)
        pdf.cell(0, 10, f"- Saving: {facts['saved']:,} KRW/year", 0, 1)
        
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "2. AI Recommendation", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 7, "High LTV risk detected. Recommended to proceed with refinancing immediately to secure cash flow.")
        
        return pdf.output(dest='S').encode('latin-1', errors='replace')

    @staticmethod
    def create_excel_csv(data_list):
        df = pd.DataFrame(data_list)
        return df.to_csv(index=False).encode('utf-8-sig')

# --------------------------------------------------------------------------------
# [Engine 2] 하이브리드 인텔리전스
# --------------------------------------------------------------------------------
def get_hybrid_analysis(prompt, facts, mode):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text, "Gemini 1.5 Flash"
    except:
        risk = "고위험" if facts['ltv'] > 70 else "안정"
        fallback = f"""
### 🚨 시스템 진단 ({risk} 단계)
* **정밀 분석**: 현재 **LTV {facts['ltv']}%**로 {risk}군에 속합니다. 특히 **연간 {facts['saved']/10000:,.0f}만 원**의 불필요한 이자 비용이 발생하고 있습니다.
* **{mode} 솔루션**: 데이터 팩트 체크 결과 **'통합 대환'** 및 **'신탁 말소'**가 가장 시급한 과제입니다.
* **전문가 제언**: 수치상 명백한 자산 가치 상승 기회가 확인됩니다. 즉시 실행 단계로 넘어가십시오.
        """
        return fallback, "Jisang-Hybrid Engine"

class FactChecker:
    @staticmethod
    def process(raw_data):
        target_bonds = []
        saved_interest = 0
        for bond in raw_data['bonds']:
            t_date = datetime.strptime(bond['date'], "%Y.%m.%d")
            diff = relativedelta(datetime.now(), t_date)
            months = diff.years * 12 + diff.months
            is_target = months >= 24 or bond['type'] == "대부업"
            if is_target:
                target_bonds.append(bond)
                gap = 0.12 if bond['type'] == "대부업" else 0.015 
                saved_interest += bond['amount'] * gap
        
        total = sum(b['amount'] for b in raw_data['bonds'])
        ltv = round((total / raw_data['market_price']) * 100, 2)
        score = 100 - (len(raw_data['restrictions'])*15) - (20 if ltv>80 else 0)
        
        return {
            "address": raw_data['address'],
            "ltv": ltv, "count": len(target_bonds), "total": total, 
            "saved": int(saved_interest), "score": score,
            "restrictions": raw_data['restrictions']
        }

def run_simulation(addr, mode):
    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기", "압류"]
    }
    facts = FactChecker.process(raw)
    
    prompt = f"""
    역할: 부동산 금융 전문가.
    대상: {addr}, LTV {facts['ltv']}%.
    목표: {mode} 관점에서 이자 절감({facts['saved']/10000:.0f}만원)의 중요성 강조.
    
    [작성법]
    Markdown 사용.
    1. 🔍 진단: 리스크 명시.
    2. 💊 처방: 구체적 행동(대환/말소).
    3. 💰 효과: 자산 가치 상승.
    """
    ai_text, engine = get_hybrid_analysis(prompt, facts, mode)
    return raw, facts, ai_text, engine

# --------------------------------------------------------------------------------
# [UI/UX] Grand Master Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI Platform", page_icon="🏢", layout="wide")

# Styling
st.markdown("""
    <style>
    .report-card { background-color: #f8f9fa; border-radius: 10px; padding: 20px; border: 1px solid #e9ecef; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2563eb; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
    st.title("Jisang AI")
    st.caption("Grand Master Edition")
    
    mode = st.selectbox("분석 관점", ["금융 최적화", "세무/자산", "개발/시행", "매입/매각"])
    
    st.markdown("---")
    st.markdown("**📂 B2B 포트폴리오**")
    addr_input = st.text_area("주소 입력 (Batch)", "김포시 통진읍 도사리 163-1\n서울시 강남구 역삼동 825-1\n부산시 해운대구 우동 1408", height=120)
    
    if st.button("🚀 전체 자산 분석 실행", type="primary", use_container_width=True):
        st.session_state['run_analysis'] = True

# Main Logic
if 'run_analysis' in st.session_state and st.session_state['run_analysis']:
    address_list = [a.strip() for a in addr_input.split('\n') if a.strip()]
    all_results = []
    
    st.title(f"🏢 부동산 자산 {mode} 통합 리포트")
    
    tabs = st.tabs([f"📍 {a[:6]}.." for a in address_list])
    
    for i, tab in enumerate(tabs):
        with tab:
            curr_addr = address_list[i]
            
            with st.spinner(f"Processing: {curr_addr}"):
                raw, facts, ai_text, engine = run_simulation(curr_addr, mode)
                all_results.append(facts)
            
            # Layout
            c1, c2 = st.columns([1.8, 1])
            
            with c1:
                # Native Container for AI Text (Fixing Readability)
                with st.container(border=True):
                    st.subheader(f"💡 AI Insight ({engine})")
                    st.markdown(ai_text)
                
                st.markdown("### 🚦 Action Plan")
                b1, b2 = st.columns(2)
                with b1:
                    pdf = ReportEngine.create_safe_pdf(facts)
                    # ★ Key 추가로 중복 에러 방지
                    st.download_button("📄 PDF 리포트", pdf, f"Report_{i}.pdf", "application/pdf", key=f"pdf_{i}", use_container_width=True)
                with b2:
                    if st.button("📞 전문가 매칭", key=f"match_{i}", use_container_width=True):
                        st.toast("매칭 요청이 접수되었습니다.")

            with c2:
                st.markdown("### 📊 Key Financials")
                st.metric("종합 점수", f"{facts['score']}점")
                st.metric("LTV", f"{facts['ltv']}%", "High Risk", delta_color="inverse")
                st.metric("연 절감액", f"{facts['saved']/10000:,.0f}만 원", "Opportunity")
                
                # Chart (Fixing Duplicate ID Error)
                df_chart = pd.DataFrame({"State": ["Before", "After"], "Cost": [facts['total']*0.06, facts['total']*0.06 - facts['saved']]})
                fig = px.bar(df_chart, x="State", y="Cost", color="State", title="금융비용 비교")
                # ★ Key 추가가 핵심 솔루션
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")

    # B2B Export
    st.markdown("---")
    st.subheader("💼 B2B Data Export")
    csv = ReportEngine.create_excel_csv(all_results)
    st.download_button("📥 전체 분석 결과 다운로드 (.csv)", csv, "Portfolio.csv", "text/csv", type="primary")

else:
    st.title("Jisang AI Platform")
    st.info("👈 왼쪽 사이드바에서 **[전체 자산 분석 실행]**을 클릭하십시오.")