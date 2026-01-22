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
# [Engine 1] 리포트 엔진
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
        pdf.multi_cell(0, 7, "High LTV risk detected. Recommended to proceed with refinancing immediately.")
        return pdf.output(dest='S').encode('latin-1', errors='replace')

    @staticmethod
    def create_excel_csv(data_list):
        df = pd.DataFrame(data_list)
        return df.to_csv(index=False).encode('utf-8-sig')

# --------------------------------------------------------------------------------
# [Engine 2] AI 엔진 (분석 + 챗봇)
# --------------------------------------------------------------------------------
def get_ai_response(prompt, model_type="flash"):
    """통합 AI 호출 함수"""
    model_name = 'gemini-1.5-flash' if model_type == "flash" else 'gemini-pro'
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except:
        return "죄송합니다. 현재 AI 서버 연결이 원활하지 않습니다. 잠시 후 다시 시도해주세요."

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
    
    # 리포트 생성용 프롬프트
    prompt = f"""
    부동산 전문가 페르소나: {mode}. 대상: {addr}, LTV {facts['ltv']}%.
    기회: 대환 시 연 {facts['saved']/10000:.0f}만원 절감.
    작성법: 1.진단 2.솔루션 3.효과 (Markdown, 한국어)
    """
    ai_text = get_ai_response(prompt)
    return raw, facts, ai_text

# --------------------------------------------------------------------------------
# [UI/UX] Chatbot Integrated Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI Chatbot", page_icon="🤖", layout="wide")

# Styling
st.markdown("""
    <style>
    .chat-container { border: 1px solid #ddd; border-radius: 10px; padding: 10px; background-color: #f9f9f9; height: 400px; overflow-y: scroll; }
    .user-msg { text-align: right; color: blue; font-weight: bold; }
    .bot-msg { text-align: left; color: black; background-color: #eef; padding: 5px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
    st.title("Jisang AI")
    st.caption("Chatbot Edition v6.0")
    
    mode = st.selectbox("분석 관점", ["금융 최적화", "세무/자산", "개발/시행"])
    
    st.markdown("---")
    st.markdown("**📂 B2B 포트폴리오**")
    addr_input = st.text_area("주소 입력", "김포시 통진읍 도사리 163-1\n서울시 강남구 역삼동 825-1", height=100)
    
    if st.button("🚀 분석 & 챗봇 실행", type="primary", use_container_width=True):
        st.session_state['run_analysis'] = True
        # 챗봇 기록 초기화
        st.session_state['messages'] = {} 

if 'run_analysis' in st.session_state and st.session_state['run_analysis']:
    address_list = [a.strip() for a in addr_input.split('\n') if a.strip()]
    all_results = []
    
    st.title(f"🏢 부동산 자산 {mode} 통합 리포트")
    
    # 탭별로 주소 할당
    tabs = st.tabs([f"📍 {a[:6]}.." for a in address_list])
    
    for i, tab in enumerate(tabs):
        with tab:
            curr_addr = address_list[i]
            
            # 분석 데이터 로드 (캐싱 대신 매번 실행 시뮬레이션)
            raw, facts, ai_text = run_simulation(curr_addr, mode)
            all_results.append(facts)

            # --- Layout: Report (Left) vs Chatbot (Right) ---
            col_report, col_chat = st.columns([1.5, 1])
            
            with col_report:
                # 1. AI Insight
                with st.container(border=True):
                    st.subheader("💡 AI Executive Summary")
                    st.markdown(ai_text)
                
                # 2. Key Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("LTV", f"{facts['ltv']}%", "High Risk", delta_color="inverse")
                m2.metric("절감액", f"{facts['saved']/10000:,.0f}만원", "Profit")
                m3.metric("종합점수", f"{facts['score']}점")
                
                # 3. Chart
                df_chart = pd.DataFrame({"State": ["Before", "After"], "Cost": [facts['total']*0.06, facts['total']*0.06 - facts['saved']]})
                fig = px.bar(df_chart, x="State", y="Cost", color="State", height=250)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
                
                # 4. Actions
                b1, b2 = st.columns(2)
                with b1:
                    pdf = ReportEngine.create_safe_pdf(facts)
                    st.download_button("📄 PDF 다운로드", pdf, f"Report_{i}.pdf", "application/pdf", key=f"pdf_{i}", use_container_width=True)
                with b2:
                    if st.button("📞 전문가 매칭", key=f"match_{i}", use_container_width=True):
                        st.toast("전문가 매칭 요청 완료!")

            with col_chat:
                st.markdown(f"### 🤖 AI 부동산 비서 ({curr_addr})")
                st.info("이 물건에 대해 궁금한 점을 자유롭게 물어보세요. 제가 모든 데이터를 알고 있습니다.")
                
                # 채팅 기록 관리 (탭별 분리)
                chat_key = f"chat_{i}"
                if chat_key not in st.session_state:
                    st.session_state[chat_key] = [{"role": "assistant", "content": f"안녕하세요! '{curr_addr}' 전담 AI 비서입니다. 무엇을 도와드릴까요? (예: 대출 금리는 얼마까지 낮출 수 있어?)"}]

                # 채팅 화면 표시
                chat_container = st.container(height=400)
                for msg in st.session_state[chat_key]:
                    with chat_container.chat_message(msg["role"]):
                        st.write(msg["content"])

                # 사용자 입력 처리
                if prompt := st.chat_input(f"질문 입력 ({curr_addr})...", key=f"input_{i}"):
                    # 사용자 메시지 표시
                    st.session_state[chat_key].append({"role": "user", "content": prompt})
                    with chat_container.chat_message("user"):
                        st.write(prompt)

                    # AI 응답 생성 (Context Injection)
                    context = f"""
                    현재 분석 중인 물건 정보:
                    - 주소: {curr_addr}
                    - LTV: {facts['ltv']}%
                    - 총 채권액: {facts['total']}원
                    - 권리하자: {raw['restrictions']} (신탁, 압류)
                    - 솔루션 예상 절감액: 연간 {facts['saved']}원
                    
                    사용자 질문: {prompt}
                    
                    지침:
                    1. 위 데이터를 근거로 답변할 것.
                    2. 긍정적이고 전문적인 톤 유지.
                    3. 답변 끝에 '전문가 상담을 예약해 드릴까요?'라고 권유할 것.
                    """
                    
                    with chat_container.chat_message("assistant"):
                        with st.spinner("생각 중..."):
                            response = get_ai_response(context)
                            st.write(response)
                            st.session_state[chat_key].append({"role": "assistant", "content": response})

    # B2B Export
    st.markdown("---")
    csv = ReportEngine.create_excel_csv(all_results)
    st.download_button("📥 전체 분석 결과 (CSV)", csv, "Portfolio.csv", "text/csv")

else:
    st.title("Jisang AI Chatbot Platform")
    st.info("👈 왼쪽 사이드바에서 **[분석 & 챗봇 실행]**을 클릭하세요.")