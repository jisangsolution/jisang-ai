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
# [Engine 1] 챗봇 전용 무중단 연결 엔진 (Robust Chat Engine)
# --------------------------------------------------------------------------------
def get_chat_response(messages, context_data):
    """
    대화 기록과 부동산 데이터를 결합하여 끊김 없는 답변 생성
    """
    # 1. 시스템 프롬프트 (페르소나 정의)
    system_prompt = f"""
    당신은 '지상 AI' 부동산 전문 비서입니다.
    현재 분석 중인 물건 데이터:
    - 주소: {context_data['address']}
    - LTV: {context_data['ltv']}% (고위험 여부 판단)
    - 총 채권액: {context_data['total']:,}원
    - 권리하자: {context_data['restrictions']} (신탁/압류 등)
    - 솔루션: 연간 {context_data['saved']:,}원 이자 절감 가능
    
    [행동 지침]
    1. 사용자의 질문에 위 데이터를 근거로 구체적으로 답변하세요.
    2. '공동담보'나 '신탁' 같은 전문 용어는 쉽게 풀어서 설명하세요.
    3. 답변 끝에는 반드시 "더 자세한 내용은 전문가 상담을 통해 확인하시겠습니까?"라고 정중히 제안하세요. (영업 기회 포착)
    4. 한국어로 답변하세요.
    """
    
    # 2. 모델 순환 호출 (Fail-over)
    models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash']
    
    # 대화 히스토리 포맷팅
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    full_prompt = f"{system_prompt}\n\n[이전 대화]\n{history_text}\n\nAI 답변:"

    for m in models:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content(full_prompt)
            if response.text:
                return response.text
        except:
            continue
    
    return "죄송합니다. 현재 접속량이 많아 연결이 지연되고 있습니다. 우측 '전문가 매칭' 버튼을 눌러주시면 담당자가 직접 전화드리겠습니다."

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
        pdf.ln(5)
        pdf.multi_cell(0, 7, "Recommendation: High risk detected. Please proceed with the refinancing consultation.")
        
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
            "restrictions": raw_data['restrictions']
        }

def run_simulation(addr):
    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기", "압류"]
    }
    facts = FactChecker.process(raw)
    
    # 리포트용 짧은 요약
    ai_text = f"""
    ### 💡 AI 분석 요약
    * **상태**: 현재 **LTV {facts['ltv']}%**로 고위험군입니다. 특히 {raw['restrictions']}가 있어 일반 거래가 불가능합니다.
    * **기회**: **연 {facts['saved']/10000:,.0f}만 원** 절감이 가능한 대환 대상입니다.
    * **제안**: 우측 챗봇에게 "어떻게 해결해?"라고 물어보시거나, 하단 버튼으로 전문가를 호출하세요.
    """
    return raw, facts, ai_text

# --------------------------------------------------------------------------------
# [UI/UX] Sales Chatbot Platform
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI Sales Bot", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .report-container { padding: 15px; border: 1px solid #ddd; border-radius: 10px; background: white; height: 600px; overflow-y: auto; }
    .chat-container { padding: 15px; border: 1px solid #3b82f6; border-radius: 10px; background: #fefffe; height: 600px; display: flex; flex-direction: column; }
    .user-msg { background-color: #e0f2fe; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .bot-msg { background-color: #f3f4f6; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; margin-right: auto; max-width: 90%; border-left: 4px solid #3b82f6; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
    st.title("Jisang AI")
    st.caption("Sales Chatbot Edition")
    
    st.markdown("### 📂 B2B 포트폴리오")
    addr_input = st.text_area("주소 입력", "김포시 통진읍 도사리 163-1\n서울시 강남구 역삼동 825-1", height=100)
    
    if st.button("🚀 분석 & 상담 시작", type="primary", use_container_width=True):
        st.session_state['run_analysis'] = True
        st.session_state['messages'] = {} # 대화 기록 초기화

if 'run_analysis' in st.session_state and st.session_state['run_analysis']:
    address_list = [a.strip() for a in addr_input.split('\n') if a.strip()]
    all_results = []
    
    st.title("🤖 부동산 자산 관리 & AI 상담")
    
    tabs = st.tabs([f"📍 {a[:6]}.." for a in address_list])
    
    for i, tab in enumerate(tabs):
        with tab:
            curr_addr = address_list[i]
            raw, facts, ai_text = run_simulation(curr_addr)
            all_results.append(facts)
            
            # --- Layout: 5:5 Split (Report vs Chat) ---
            c_left, c_right = st.columns([1, 1])
            
            # [LEFT] 정적 리포트 (Static Data)
            with c_left:
                st.subheader("📑 정밀 분석 리포트")
                with st.container(height=600):
                    st.markdown(ai_text)
                    st.markdown("---")
                    
                    # Metrics
                    m1, m2 = st.columns(2)
                    m1.metric("LTV (담보비율)", f"{facts['ltv']}%", "High Risk", delta_color="inverse")
                    m2.metric("예상 절감액", f"{facts['saved']/10000:,.0f}만 원", "Profit")
                    
                    # Chart
                    df_chart = pd.DataFrame({"State": ["Current", "Optimized"], "Cost": [facts['total']*0.06, facts['total']*0.06 - facts['saved']]})
                    fig = px.bar(df_chart, x="State", y="Cost", color="State", title="금융비용 최적화", height=250)
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
                    
                    # Buttons
                    st.markdown("---")
                    b1, b2 = st.columns(2)
                    with b1:
                        pdf = ReportEngine.create_safe_pdf(facts)
                        st.download_button("📄 PDF 리포트", pdf, f"Report_{i}.pdf", "application/pdf", key=f"pdf_{i}", use_container_width=True)
                    with b2:
                        if st.button("📞 담당자 호출", key=f"call_{i}", use_container_width=True, type="primary"):
                            st.toast("담당자에게 알림을 보냈습니다. 5분 내 연락드립니다.")

            # [RIGHT] 세일즈 챗봇 (Sales Bot)
            with c_right:
                st.subheader(f"💬 AI 부동산 비서 ({curr_addr})")
                
                # 채팅 기록 초기화
                chat_key = f"chat_history_{i}"
                if chat_key not in st.session_state:
                    st.session_state[chat_key] = [
                        {"role": "bot", "content": f"안녕하세요! '{curr_addr}' 분석을 완료했습니다. \n\n보유하신 대출 중 **대부업 대출**을 1금융권으로 대환하면 **연 {facts['saved']/10000:,.0f}만 원**을 아낄 수 있습니다. \n\n진행 절차나 공동담보 해지에 대해 궁금한 점이 있으신가요?"}
                    ]
                
                # 채팅 UI 컨테이너
                chat_container = st.container(height=520)
                
                # 대화 내용 출력
                for msg in st.session_state[chat_key]:
                    if msg['role'] == 'user':
                        chat_container.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        chat_container.markdown(f'<div class="bot-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

                # 입력창 (Form으로 감싸서 엔터키 전송 지원)
                with st.form(key=f"chat_form_{i}", clear_on_submit=True):
                    user_input = st.text_input("질문 입력 (예: 공동담보 목록 보여줘)", key=f"input_{i}")
                    submit_button = st.form_submit_button("전송 ⬆️")
                
                if submit_button and user_input:
                    # 1. 사용자 메시지 추가
                    st.session_state[chat_key].append({"role": "user", "content": user_input})
                    
                    # 2. AI 응답 생성 (강화된 연결성)
                    context_data = {
                        "address": curr_addr, "ltv": facts['ltv'], "total": facts['total'], 
                        "saved": facts['saved'], "restrictions": raw['restrictions']
                    }
                    
                    # 즉시 렌더링을 위해 Rerun 전에 spinner 사용
                    with chat_container:
                        with st.spinner("분석 중..."):
                            bot_reply = get_chat_response(st.session_state[chat_key], context_data)
                    
                    st.session_state[chat_key].append({"role": "bot", "content": bot_reply})
                    st.rerun()

    # B2B Export
    st.markdown("---")
    csv = ReportEngine.create_excel_csv(all_results)
    st.download_button("📥 전체 분석 결과 (CSV)", csv, "Portfolio.csv", "text/csv")

else:
    st.title("Jisang AI Sales Bot")
    st.info("👈 왼쪽 사이드바에서 **[분석 & 상담 시작]**을 클릭하세요.")