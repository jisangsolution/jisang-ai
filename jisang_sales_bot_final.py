import os
import sys
import time
import subprocess
import random
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 스마트 런처
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
# [Engine 1] 하이브리드 챗봇 엔진 (Hybrid Chat Engine)
# Strategy: Rule-based First -> AI Fallback
# --------------------------------------------------------------------------------
def get_hybrid_response(user_input, context_data):
    """
    1단계: 핵심 키워드가 있으면 Python 데이터로 즉시 답변 (정확도 100%, 속도 최상)
    2단계: 키워드가 없으면 Gemini AI에게 질의 (자유도 높음)
    """
    user_input = user_input.lower()
    
    # [Rule 1] 공동담보 / 채권 관련 질문
    if any(k in user_input for k in ["공동", "담보", "채권", "얼마", "목록"]):
        bonds_list = "\n".join([f"- **{b['bank']}**: {b['amount']:,}원 ({b['date']} 설정)" for b in context_data['raw_bonds']])
        return f"""
        📋 **등기부 채권(공동담보) 현황**입니다.
        
        {bonds_list}
        
        총 채권액은 **{context_data['total']:,}원**이며, 이는 시세 대비 **{context_data['ltv']}%** 수준입니다.
        이 중 고금리 대출을 선별하여 정리하는 것이 핵심입니다.
        """

    # [Rule 2] 대환 / 금리 / 이자 / 절약 관련 질문
    if any(k in user_input for k in ["대환", "금리", "이자", "절약", "아낄"]):
        return f"""
        💰 **금융 최적화 분석 결과**입니다.
        
        현재 보유하신 대출 중 일부(대부업 등)를 1금융권으로 전환할 경우,
        **연간 약 {context_data['saved']:,}원**의 이자를 즉시 줄일 수 있습니다.
        
        월 250만 원의 현금 흐름이 개선되는 효과가 있습니다. 바로 진행 절차를 안내해 드릴까요?
        """

    # [Rule 3] 신탁 / 압류 / 리스크 관련 질문
    if any(k in user_input for k in ["신탁", "압류", "위험", "리스크", "안전"]):
        return f"""
        🚨 **권리 리스크 긴급 진단**
        
        현재 이 물건에는 **{context_data['restrictions']}** 등기가 설정되어 있습니다.
        특히 '신탁등기' 상태에서는 임의로 계약하거나 대출을 받을 수 없습니다.
        
        반드시 **신탁 말소 동의**와 **채무 변제**가 동시에 이루어져야 안전합니다. 전문가의 조력이 필수적인 단계입니다.
        """

    # [Fallback] AI 모델 호출 (일반 대화)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        부동산 비서로서 답변. 데이터: {context_data}. 질문: {user_input}.
        친절하고 전문적인 어조로 답변하고, 끝에 전문가 상담을 권유할 것.
        """
        response = model.generate_content(prompt)
        return response.text
    except:
        return "죄송합니다. 상세 상담을 위해 우측 '전문가 호출' 버튼을 눌러주시면 담당자가 바로 연락드리겠습니다."

# --------------------------------------------------------------------------------
# [Engine 2] 리포트 엔진
# --------------------------------------------------------------------------------
class ReportEngine:
    @staticmethod
    def create_safe_pdf(facts):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Jisang AI | Analysis Report", 0, 1, 'C')
        pdf.ln(10)
        
        asset_id = f"ASSET-{random.randint(10000, 99999)}"
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Ref ID: {asset_id}", 0, 1)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Summary", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"- LTV Ratio: {facts['ltv']}%", 0, 1)
        pdf.cell(0, 10, f"- Total Debt: {facts['total']:,} KRW", 0, 1)
        pdf.cell(0, 10, f"- Annual Saving: {facts['saved']:,} KRW", 0, 1)
        pdf.ln(10)
        pdf.multi_cell(0, 7, "High risk detected. Immediate refinancing recommended.")
        return pdf.output(dest='S').encode('latin-1', errors='replace')

    @staticmethod
    def create_excel_csv(data_list):
        df = pd.DataFrame(data_list)
        return df.to_csv(index=False).encode('utf-8-sig')

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
            "restrictions": raw_data['restrictions'],
            "raw_bonds": raw_data['bonds'] # 챗봇용 원본 데이터 전달
        }

def run_simulation(addr):
    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기", "압류"]
    }
    facts = FactChecker.process(raw)
    
    # 리포트용 요약
    ai_text = f"""
    ### 💡 AI 분석 요약
    * **상태**: 현재 **LTV {facts['ltv']}%**로 고위험군입니다. 특히 {raw['restrictions']}가 있어 일반 거래가 불가능합니다.
    * **기회**: **연 {facts['saved']/10000:,.0f}만 원** 절감이 가능한 대환 대상입니다.
    * **제안**: 우측 챗봇에게 **"공동담보 보여줘"**라고 물어보세요.
    """
    return raw, facts, ai_text

# --------------------------------------------------------------------------------
# [UI/UX] Hybrid Sales Bot Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI Hybrid Bot", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .chat-container { height: 500px; display: flex; flex-direction: column; }
    .user-msg { background-color: #e0f2fe; padding: 10px; border-radius: 15px; margin: 5px 0 5px auto; max-width: 80%; text-align: right; color: #000; }
    .bot-msg { background-color: #f3f4f6; padding: 10px; border-radius: 15px; margin: 5px auto 5px 0; max-width: 90%; text-align: left; color: #000; border-left: 4px solid #3b82f6; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
    st.title("Jisang AI")
    st.caption("Hybrid Sales Bot v7.0")
    
    st.markdown("### 📂 B2B 포트폴리오")
    addr_input = st.text_area("주소 입력", "김포시 통진읍 도사리 163-1\n서울시 강남구 역삼동 825-1", height=100)
    
    if st.button("🚀 분석 & 상담 시작", type="primary", use_container_width=True):
        st.session_state['run_analysis'] = True
        st.session_state['messages'] = {}

if 'run_analysis' in st.session_state and st.session_state['run_analysis']:
    address_list = [a.strip() for a in addr_input.split('\n') if a.strip()]
    all_results = []
    
    st.title("🤖 지상 AI: 부동산 자산 관리 솔루션")
    
    tabs = st.tabs([f"📍 {a[:6]}.." for a in address_list])
    
    for i, tab in enumerate(tabs):
        with tab:
            curr_addr = address_list[i]
            raw, facts, ai_text = run_simulation(curr_addr)
            all_results.append(facts)
            
            # Layout
            c_left, c_right = st.columns([1, 1])
            
            # [LEFT] Report
            with c_left:
                st.subheader("📑 정밀 분석 리포트")
                with st.container(height=550):
                    st.markdown(ai_text)
                    st.markdown("---")
                    m1, m2 = st.columns(2)
                    m1.metric("LTV", f"{facts['ltv']}%", "High Risk", delta_color="inverse")
                    m2.metric("예상 절감액", f"{facts['saved']/10000:,.0f}만 원", "Profit")
                    
                    df_chart = pd.DataFrame({"State": ["Current", "Optimized"], "Cost": [facts['total']*0.06, facts['total']*0.06 - facts['saved']]})
                    fig = px.bar(df_chart, x="State", y="Cost", color="State", title="금융비용 최적화", height=200)
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
                    
                    st.markdown("---")
                    b1, b2 = st.columns(2)
                    with b1:
                        pdf = ReportEngine.create_safe_pdf(facts)
                        st.download_button("📄 PDF 다운로드", pdf, f"Report_{i}.pdf", "application/pdf", key=f"pdf_{i}", use_container_width=True)
                    with b2:
                        if st.button("📞 담당자 호출", key=f"call_{i}", use_container_width=True, type="primary"):
                            st.toast("✅ 담당자 배정 완료. 5분 내 연락드립니다.")

            # [RIGHT] Hybrid Chatbot
            with c_right:
                st.subheader(f"💬 AI 부동산 비서 ({curr_addr})")
                
                chat_key = f"chat_history_{i}"
                if chat_key not in st.session_state:
                    st.session_state[chat_key] = [
                        {"role": "bot", "content": f"안녕하세요! '{curr_addr}' 전담 비서입니다. \n\n**'공동담보 목록'**이나 **'대환 절차'**라고 물어보시면 즉시 답변해 드립니다."}
                    ]
                
                # Chat History
                chat_container = st.container(height=480)
                for msg in st.session_state[chat_key]:
                    role_class = "user-msg" if msg['role'] == 'user' else "bot-msg"
                    icon = "👤" if msg['role'] == 'user' else "🤖"
                    chat_container.markdown(f'<div class="{role_class}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

                # Input
                with st.form(key=f"chat_form_{i}", clear_on_submit=True):
                    user_input = st.text_input("질문 입력...", key=f"input_{i}")
                    cols = st.columns([4, 1])
                    with cols[1]:
                        submit = st.form_submit_button("전송")
                
                if submit and user_input:
                    st.session_state[chat_key].append({"role": "user", "content": user_input})
                    
                    # ★ Hybrid Engine 호출
                    context_data = {
                        "address": curr_addr, "ltv": facts['ltv'], "total": facts['total'], 
                        "saved": facts['saved'], "restrictions": raw['restrictions'], "raw_bonds": raw['bonds']
                    }
                    
                    # 즉시 답변 (No Spinner for Rule-based)
                    bot_reply = get_hybrid_response(user_input, context_data)
                    
                    st.session_state[chat_key].append({"role": "bot", "content": bot_reply})
                    st.rerun()

    st.markdown("---")
    csv = ReportEngine.create_excel_csv(all_results)
    st.download_button("📥 전체 분석 결과 (CSV)", csv, "Portfolio.csv", "text/csv")
    