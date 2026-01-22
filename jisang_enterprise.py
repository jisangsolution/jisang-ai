import os
import sys
import time
import subprocess
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 스마트 런처 (PDF 엔진 fpdf 추가)
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
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [Engine 1] PDF 생성 엔진 (Report Generator)
# --------------------------------------------------------------------------------
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Jisang AI | Real Estate Deep Tech Report', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, f'{title}', 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, body)
        self.ln()

def create_pdf(address, data, ai_text):
    pdf = PDFReport()
    pdf.add_page()
    
    # 한글 지원 제한으로 영문/숫자 위주 데모 (실제 상용화 시 한글 폰트 탑재 필요)
    pdf.chapter_title(f"Target: {address} (Analysis ID: {random.randint(1000,9999)})")
    
    pdf.chapter_title("1. Financial Fact Check")
    pdf.chapter_body(f"Total Bond: {data['total']:,} KRW\nLTV Ratio: {data['ltv']}%\nRefinance Target: {data['count']} cases\nEst. Saving: {data['saved']:,} KRW/year")
    
    pdf.chapter_title("2. AI Strategy Summary")
    # PDF에는 요약된 텍스트만 영문으로 변환해서 넣는 시뮬레이션
    clean_text = ai_text.replace("*", "").replace("#", "") 
    pdf.chapter_body(clean_text[:500] + "\n...(Full details in App)")
    
    return pdf.output(dest='S').encode('latin-1')

# --------------------------------------------------------------------------------
# [Engine 2] 데이터 & AI 로직
# --------------------------------------------------------------------------------
def get_robust_model():
    return 'gemini-1.5-flash'

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

def run_simulation(addr, mode):
    with st.spinner(f"🔍 [{mode} 모드] 데이터 분석 및 플랫폼 매칭 중..."):
        time.sleep(1.0)

    # 가상 데이터
    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기(우리자산신탁)", "압류(김포세무서)"]
    }
    facts = FactChecker.process(raw)
    
    # 모드별 프롬프트 최적화 (Role-Playing)
    mode_prompt = ""
    if mode == "금융/대환":
        mode_prompt = "초점: 이자 절감 및 신용도 회복. 대부업 상환 전략 필수."
    elif mode == "세무/자산":
        mode_prompt = "초점: 압류 해제에 따른 양도세/상속세 이슈 및 자산 가치 정상화."
    elif mode == "개발/시행":
        mode_prompt = "초점: 토지 규제(계획관리) 분석 및 신탁 해지 후 PF 대출 가능성."
    
    model_name = get_robust_model()
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        부동산 리포트. Markdown 문법 사용.
        대상: {raw['address']}, LTV {facts['ltv']}%.
        {mode_prompt}
        
        [출력 구조]
        ### 1. 🔍 핵심 진단 ({mode} 관점)
        (냉철한 분석)
        
        ### 2. 🚀 솔루션
        (구체적 행동 지침)
        
        ### 3. 💰 기대 효과
        (수치적 이익)
        """
        resp = model.generate_content(prompt)
        ai_msg = resp.text
    except:
        ai_msg = "AI 분석 지연. (표준 텍스트) 신탁 말소 및 대환 대출이 시급합니다."

    return raw, facts, ai_msg

# --------------------------------------------------------------------------------
# [UI/UX] Enterprise Platform
# --------------------------------------------------------------------------------
st.set_page_config(page_title="지상 AI Enterprise", page_icon="🏢", layout="wide")

# CSS: 가독성 & 카드 UI
st.markdown("""
    <style>
    .big-font { font-size: 20px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 4px; background-color: #f0f2f6; }
    .stTabs [aria-selected="true"] { background-color: #3b82f6; color: white; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🏢 Jisang Platform")
    st.caption("Total Real Estate Solutions")
    
    # 1. 모드 선택 (종합 사업 모델)
    analysis_mode = st.selectbox("분석 관점 선택", ["금융/대환", "세무/자산", "개발/시행", "중개/매매"])
    
    # 2. 다중 주소 입력 (Batch)
    st.markdown("---")
    st.markdown("**📂 포트폴리오 분석**")
    addr_input = st.text_area("주소 입력 (한 줄에 하나씩)", "김포시 통진읍 도사리 163-1\n김포시 구래동 6883-1", height=100)
    
    start_btn = st.button("🚀 통합 분석 시작", type="primary", use_container_width=True)

# Main Area
if start_btn:
    # 주소 리스트 파싱
    addresses = [a.strip() for a in addr_input.split('\n') if a.strip()]
    
    st.title(f"🏢 부동산 {analysis_mode} 통합 리포트")
    
    # 탭 생성 (주소별 결과)
    tabs = st.tabs([f"📍 {addr[:10]}..." for addr in addresses])
    
    for i, tab in enumerate(tabs):
        with tab:
            curr_addr = addresses[i]
            if not api_key:
                st.error("API Key Missing")
                continue
                
            raw, facts, ai_text = run_simulation(curr_addr, analysis_mode)
            
            # --- 리포트 본문 ---
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader(f"📌 {curr_addr}")
                # AI Text (Native Markdown for Best Readability)
                st.markdown(ai_text)
                
            with c2:
                st.markdown("### 📊 Key Metrics")
                st.metric("LTV Ratio", f"{facts['ltv']}%", "High Risk", delta_color="inverse")
                st.metric("Est. Saving", f"{facts['saved']/10000:,.0f}만 원/년", "Opportunity")
                
                # Chart
                df = pd.DataFrame({"State": ["Current", "Proposed"], "Cost": [4800, 4800-(facts['saved']/10000)]})
                fig = px.bar(df, x="State", y="Cost", color="State", height=200)
                st.plotly_chart(fig, use_container_width=True)

            # --- 플랫폼 비즈니스 기능 (Platform Actions) ---
            st.markdown("---")
            st.markdown("### 🤝 지상 AI 파트너스 연결 (One-Stop Service)")
            
            p1, p2, p3 = st.columns(3)
            
            # 1. PDF 다운로드
            with p1:
                pdf_bytes = create_pdf(curr_addr, facts, ai_text)
                st.download_button(
                    label="📄 은행 제출용 리포트 (PDF)",
                    data=pdf_bytes,
                    file_name=f"Jisang_Report_{i}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # 2. 금융 솔루션 매칭 (Lead Gen)
            with p2:
                if st.button(f"📞 최적금리 매칭 (3개사)", key=f"fin_{i}", use_container_width=True, type="primary"):
                    with st.status("🔗 금융 파트너사 입찰 진행 중...", expanded=True):
                        time.sleep(0.5)
                        st.write("✅ 우리은행 기업금융센터 전송 완료")
                        st.write("✅ 신한은행 여신심사팀 전송 완료")
                        st.write("✅ OK캐피탈 대환팀 전송 완료")
                    st.success("매칭 완료! 담당자가 10분 내로 제안서를 보냅니다.")
            
            # 3. 탁상감정 의뢰 (Appraisal)
            with p3:
                if st.button(f"🏠 탁상감정 무료 의뢰", key=f"app_{i}", use_container_width=True):
                    st.toast(f"✅ [협력 감정평가법인]에 '{curr_addr}' 탁상감정 요청이 발송되었습니다.")
                    time.sleep(1)
                    st.info("예상 감정가: 12.5억 원 (내일 오전 10시 확정 통보)")

            # 데이터 무결성
            with st.expander("🛡️ 데이터 무결성 검증 (FactChecker™)"):
                st.json(facts)

            # 면책 조항
            st.caption("본 리포트는 시뮬레이션 결과이며, 실제 금융 조건은 달라질 수 있습니다.")

else:
    st.info("👈 왼쪽 사이드바에서 분석 모드를 선택하고 주소를 입력하세요.")
    st.markdown("### 🌟 지상 AI 플랫폼의 특징")
    c1, c2, c3 = st.columns(3)
    c1.info("**금융 최적화**\n\n대환/PF대출 자동 매칭")
    c2.warning("**리스크 관리**\n\n신탁/압류 권리분석")
    c3.success("**자산 가치**\n\n감정평가/개발 타당성")