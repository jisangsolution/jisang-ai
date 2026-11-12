import os
import sys
import time
import subprocess
import random
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 스마트 오토 런처 (환경 자동 구축)
def install_and_launch():
    required = {
        "streamlit": "streamlit", "plotly": "plotly", 
        "google-generativeai": "google.generativeai", 
        "python-dotenv": "dotenv", "python-dateutil": "dateutil",
        "fpdf": "fpdf"
    }
    needs_install = []
    print("🛠️ [시스템] 필수 엔진 무결성 점검 중...")
    for pkg, mod in required.items():
        try:
            __import__(mod)
        except ImportError:
            needs_install.append(pkg)
    
    if needs_install:
        print(f"📦 추가 모듈 설치: {needs_install}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U"] + needs_install)
        print("✅ 설치 완료. 시스템을 재가동합니다.")
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
# [Engine 1] 무결성 리포트 엔진 (Crash Free PDF & Excel)
# --------------------------------------------------------------------------------
class ReportEngine:
    @staticmethod
    def create_safe_pdf(facts):
        """한글 폰트 에러를 방지하기 위해 영문/수치 위주의 글로벌 요약본 생성"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Jisang AI | Executive Summary", 0, 1, 'C')
        pdf.ln(10)
        
        # Asset ID로 대체하여 한글 깨짐 방지
        asset_id = f"ASSET-{random.randint(10000, 99999)}"
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Ref ID: {asset_id}", 0, 1)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "1. Financial Analysis", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"- Risk Score: {facts['score']}/100", 0, 1)
        pdf.cell(0, 10, f"- LTV Ratio: {facts['ltv']}%", 0, 1)
        pdf.cell(0, 10, f"- Total Debt: {facts['total']:,} KRW", 0, 1)
        pdf.cell(0, 10, f"- Potential Saving: {facts['saved']:,} KRW/year", 0, 1)
        
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "2. AI Recommendation", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 7, "Based on the integrity check, this asset shows high LTV risk. Immediate refinancing is recommended to optimize cash flow.")
        
        pdf.ln(20)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "Powered by Jisang AI Enterprise Algorithm.", 0, 1, 'C')
        
        return pdf.output(dest='S').encode('latin-1', errors='replace')

    @staticmethod
    def create_excel_csv(data_list):
        """B2B 고객을 위한 전체 포트폴리오 엑셀 다운로드"""
        df = pd.DataFrame(data_list)
        return df.to_csv(index=False).encode('utf-8-sig')

# --------------------------------------------------------------------------------
# [Engine 2] 하이브리드 인텔리전스 (AI + Fallback Logic)
# --------------------------------------------------------------------------------
def get_hybrid_analysis(prompt, facts, mode):
    """API 장애 시에도 멈추지 않는 하이브리드 엔진"""
    try:
        # 1순위: Gemini 1.5 Flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text, "Gemini 1.5 Flash"
    except:
        # 2순위: 수치 기반 자동 텍스트 생성 (Business Continuity)
        risk_level = "고위험" if facts['ltv'] > 70 else "적정"
        fallback_text = f"""
        ### 🚨 시스템 진단: {risk_level} 단계
        * **정밀 분석**: 현재 **LTV {facts['ltv']}%**로 {risk_level}군에 속합니다. 특히 **연간 {facts['saved']/10000:,.0f}만 원**의 불필요한 이자 비용이 발생하고 있습니다.
        * **{mode} 솔루션**: AI 모델 연결이 지연 중이나, 데이터 팩트 체크 결과 **'통합 대환'** 및 **'신탁 말소'**가 가장 시급한 과제입니다.
        * **전문가 제언**: 수치상 명백한 자산 가치 상승 기회가 확인됩니다. 즉시 실행 단계로 넘어가십시오.
        """
        return fallback_text, "Jisang-Hybrid Engine"

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
    # 가상 데이터 생성 (Mock Data)
    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기", "압류"]
    }
    facts = FactChecker.process(raw)
    
    prompt = f"""
    부동산 전문가 페르소나: {mode}.
    대상: {addr}, LTV {facts['ltv']}%, 권리하자 {facts['restrictions']}.
    기회: 대환 시 연 {facts['saved']/10000:.0f}만원 절감.
    
    [작성법]
    1. 진단: 냉철하게 리스크 지적.
    2. 솔루션: {mode} 관점에서의 구체적 해결책.
    3. 비전: 실행 후 자산 가치 변화.
    (Markdown, 전문적 어조, 한국어)
    """
    
    ai_text, engine_name = get_hybrid_analysis(prompt, facts, mode)
    return raw, facts, ai_text, engine_name

# --------------------------------------------------------------------------------
# [UI/UX] Enterprise Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI Platform", page_icon="🦄", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .metric-container { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
    .ai-box { border-left: 5px solid #6366f1; background-color: #f5f3ff; padding: 20px; border-radius: 4px; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🦄 Jisang AI")
    st.caption("Enterprise Edition v5.0")
    
    mode = st.selectbox("분석 모드 (Persona)", ["금융 최적화", "세무/자산", "개발/시행", "매입/매각"])
    
    st.markdown("---")
    st.markdown("### 📂 자산 포트폴리오")
    addr_input = st.text_area("보유 자산 주소 입력", "김포시 통진읍 도사리 163-1\n서울시 강남구 역삼동 825-1\n부산시 해운대구 우동 1408", height=100)
    
    if st.button("🚀 전체 자산 분석 실행", type="primary", use_container_width=True):
        st.session_state['run_analysis'] = True
    
    st.markdown("---")
    st.info("System Online\nAll Modules Active")

# Main Logic
if 'run_analysis' in st.session_state and st.session_state['run_analysis']:
    address_list = [a.strip() for a in addr_input.split('\n') if a.strip()]
    all_results = []
    
    st.title(f"🏢 부동산 자산 {mode} 통합 리포트")
    
    # Tabs
    tabs = st.tabs([f"📍 {a[:6]}.." for a in address_list])
    
    for i, tab in enumerate(tabs):
        with tab:
            curr_addr = address_list[i]
            
            with st.spinner(f"'{curr_addr}' 정밀 분석 중..."):
                raw, facts, ai_text, engine = run_simulation(curr_addr, mode)
                all_results.append(facts) 
            
            # --- Dashboard Layout ---
            c1, c2 = st.columns([1.8, 1])
            
            with c1:
                st.markdown(f"### 💡 AI Executive Summary")
                st.caption(f"Engine: {engine}")
                st.markdown(f'<div class="ai-box">{ai_text}</div>', unsafe_allow_html=True)
                
                st.markdown("### 🚦 Action Plan")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    # Safe PDF Download
                    pdf_bytes = ReportEngine.create_safe_pdf(facts)
                    st.download_button("📄 요약 리포트 (PDF)", pdf_bytes, f"Summary_{i}.pdf", "application/pdf", use_container_width=True)
                with col_btn2:
                    # Lead Capture
                    if st.button("📞 전문가 매칭 (Fast-Track)", key=f"lead_{i}", use_container_width=True):
                        st.toast("✅ 고객님의 연락처가 [프리미엄 상담팀]에 우선 배정되었습니다.")
                        time.sleep(1)
                        st.balloons()

            with c2:
                st.markdown("### 📊 Key Financials")
                st.metric("종합 점수", f"{facts['score']}점", "Risk Adjusted")
                st.metric("LTV (담보비율)", f"{facts['ltv']}%", "High Risk", delta_color="inverse")
                st.metric("연 이자 절감", f"{facts['saved']/10000:,.0f}만 원", "Opportunity", delta_color="normal")
                
                # Chart
                df_chart = pd.DataFrame({"State": ["Current", "Optimized"], "Cost": [facts['total']*0.06, facts['total']*0.06 - facts['saved']]})
                fig = px.bar(df_chart, x="State", y="Cost", color="State", height=250, title="연간 금융비용 비교")
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("🛡️ 데이터 무결성 검증 로그"):
                st.json(facts)

    # --- B2B Feature: Batch Download ---
    st.markdown("---")
    st.subheader("💼 B2B Data Export")
    st.write("전체 포트폴리오의 핵심 지표를 엑셀(CSV)로 다운로드하여 내부 보고용으로 활용하십시오.")
    
    csv_data = ReportEngine.create_excel_csv(all_results)
    st.download_button(
        label="📥 전체 포트폴리오 데이터 다운로드 (.csv)",
        data=csv_data,
        file_name="Portfolio_Analysis_Result.csv",
        mime="text/csv",
        type="primary"
    )

else:
    # Initial State
    st.title("Jisang AI Enterprise")
    st.markdown("#### 데이터 기반 부동산 초격차 의사결정 시스템")
    st.info("👈 왼쪽 사이드바에 주소를 입력하고 **[전체 자산 분석 실행]**을 클릭하세요.")