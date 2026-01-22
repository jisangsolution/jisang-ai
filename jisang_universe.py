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
# [Engine 1] 5대 영역 전문 계산기 (Domain Calculators)
# --------------------------------------------------------------------------------
class DomainExpert:
    @staticmethod
    def calc_finance(total_debt):
        # 대부업(15%) -> 1금융(5%) 전환 시 절감액
        saving = int(total_debt * 0.10)
        return saving

    @staticmethod
    def calc_tax(price, area_type="factory"):
        # 취득세 간이 계산 (공장: 4.6%, 주택: 1.1~3.5%)
        rate = 0.046 if area_type == "factory" else 0.011
        tax = int(price * rate)
        return tax, rate * 100

    @staticmethod
    def calc_development(price, size):
        # 개발 수익률 시뮬레이션 (건축비 평당 500, 분양가 평당 1000 가정)
        cost = size * 5000000 # 건축비
        revenue = size * 10000000 # 분양수입
        profit = revenue - cost - price
        roi = (profit / (price + cost)) * 100
        return int(profit), round(roi, 2)

# --------------------------------------------------------------------------------
# [Engine 2] 스마트 챗봇 (Intent Navigation)
# --------------------------------------------------------------------------------
def get_universe_response(user_input, context):
    user_input = user_input.lower()
    
    # 1. 네비게이션 (Intent: Guide/Help)
    if any(k in user_input for k in ["안내", "도와줘", "시작", "뭐", "기능", "메뉴"]):
        return """
        🤖 **지상 AI 유니버스에 오신 것을 환영합니다.**
        원하시는 분석 분야를 말씀해 주세요:
        
        1. **💰 금융**: "이자 얼마나 줄일 수 있어?"
        2. **⚖️ 세무**: "취득세 계산해줘."
        3. **🏗️ 개발**: "이 땅 개발하면 얼마나 벌어?"
        4. **📋 권리**: "신탁등기가 뭐야?"
        """

    # 2. 금융 (Finance)
    if any(k in user_input for k in ["금융", "이자", "대출", "대환", "금리"]):
        return f"""
        💰 **금융 최적화 분석**
        현재 대출 구조를 분석한 결과, **연간 {context['finance_saving']:,}원**의 이자 절감이 가능합니다.
        대부업 대출을 1금융권으로 대환하는 '통합 금융 솔루션'을 제안합니다.
        """

    # 3. 세무 (Tax)
    if any(k in user_input for k in ["세금", "세무", "취득", "양도", "비용"]):
        return f"""
        ⚖️ **예상 세금 분석**
        이 물건(공장용지) 매입 시 예상 취득세는 약 **{context['tax_est']:,}원** ({context['tax_rate']}%)입니다.
        법인 명의 취득 시 중과세 여부를 검토하려면 전문가 상담을 요청하세요.
        """

    # 4. 개발 (Development)
    if any(k in user_input for k in ["개발", "건축", "수익", "시행", "분양"]):
        return f"""
        🏗️ **개발 타당성 분석 (가상 시뮬레이션)**
        이 부지에 공장을 신축하여 분양할 경우, 예상 수익은 **{context['dev_profit']:,}원** (ROI {context['dev_roi']}%)입니다.
        *건폐율/용적률 및 상세 설계에 따라 달라질 수 있습니다.*
        """

    # 5. 권리/리스크 (Risk)
    if any(k in user_input for k in ["권리", "신탁", "압류", "위험"]):
        return f"""
        🚨 **권리 리스크 경고**
        현재 **{context['restrictions']}**가 설정되어 있어 소유권 행사가 제한됩니다.
        일반 매매 계약은 위험하며, 반드시 신탁 말소 동의서를 선행해야 합니다.
        """

    # Fallback: AI 연결
    return "죄송합니다. 더 구체적으로 질문해 주시거나, 우측 '전문가 호출' 버튼을 눌러주세요."

# --------------------------------------------------------------------------------
# [UI/UX] Universe Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI Universe", page_icon="🌌", layout="wide")

st.markdown("""
    <style>
    .chat-box { height: 500px; border: 1px solid #eee; padding: 15px; border-radius: 10px; background: #fafafa; display: flex; flex-direction: column; }
    .bot-msg { background: #eef2ff; padding: 10px; border-radius: 10px; margin-bottom: 10px; text-align: left; border-left: 4px solid #6366f1; }
    .user-msg { background: #ffffff; padding: 10px; border-radius: 10px; margin-bottom: 10px; text-align: right; border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🌌 Jisang Universe")
    st.caption("Total Real Estate Platform")
    
    st.info("대상: 김포시 통진읍 도사리 163-1")
    if st.button("🔄 분석 데이터 갱신"):
        st.toast("최신 등기/대장 데이터 로드 완료")

# Main Data Preparation (Simulation)
price = 850000000 # 시세
debt = 600000000 # 채권액
saving = DomainExpert.calc_finance(debt)
tax, tax_rate = DomainExpert.calc_tax(price)
profit, roi = DomainExpert.calc_development(price, 363) # 363평 가정

context = {
    "finance_saving": saving,
    "tax_est": tax,
    "tax_rate": tax_rate,
    "dev_profit": profit,
    "dev_roi": roi,
    "restrictions": "신탁등기, 압류"
}

# Layout
st.title("🏢 부동산 종합 의사결정 플랫폼")
st.markdown("#### 금융 · 세무 · 개발 · 중개 · 정책을 하나로 연결합니다.")

tab1, tab2, tab3 = st.tabs(["📊 통합 대시보드", "💬 AI 컨시어지", "📂 B2B 포트폴리오"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 금융 (이자절감)", f"{saving/10000:,.0f}만 원/년", "High Impact")
    c2.metric("⚖️ 세무 (예상취득세)", f"{tax/10000:,.0f}만 원", f"{tax_rate}%")
    c3.metric("🏗️ 개발 (예상수익)", f"{profit/10000:,.0f}만 원", f"ROI {roi}%")
    
    st.markdown("---")
    st.markdown("### 🚦 종합 리스크 신호등")
    col_risk, col_sol = st.columns([1, 2])
    with col_risk:
        st.error(f"🔴 권리 위험: {context['restrictions']}")
        st.warning(f"🟡 LTV: {round(debt/price*100, 2)}% (주의)")
    with col_sol:
        st.success("**✅ 지상 AI 솔루션**")
        st.write("1. **금융**: 대부업 대환으로 현금흐름 개선")
        st.write("2. **세무**: 과밀억제권역 제외 확인 -> 중과세 배제")
        st.write("3. **개발**: 건폐율 40% 적용 시 공장 증축 가능성 있음")

with tab2:
    st.subheader("💬 무엇이든 물어보세요")
    
    # Chat Logic
    if "uni_chat" not in st.session_state:
        st.session_state.uni_chat = [{"role": "bot", "content": "안녕하세요! 부동산의 모든 것, 지상 AI입니다. \n\n**'안내해줘'**라고 입력하시면 메뉴를 보여드립니다."}]
    
    # Display Chat
    chat_container = st.container(height=450)
    for msg in st.session_state.uni_chat:
        align = "text-align: right;" if msg['role'] == 'user' else ""
        bg = "#f0f2f6" if msg['role'] == 'bot' else "white"
        chat_container.markdown(f"<div style='padding:10px; background:{bg}; border-radius:10px; margin-bottom:5px; {align}'>{msg['content']}</div>", unsafe_allow_html=True)
    
    # Input
    with st.form("chat_form", clear_on_submit=True):
        u_input = st.text_input("질문 입력 (예: 개발 수익은 얼마야?, 취득세는?)")
        if st.form_submit_button("전송"):
            st.session_state.uni_chat.append({"role": "user", "content": u_input})
            reply = get_universe_response(u_input, context)
            st.session_state.uni_chat.append({"role": "bot", "content": reply})
            st.rerun()

    # Call Expert
    if st.button("📞 분야별 전문가 호출 (Premium)", type="primary", use_container_width=True):
        st.success("요청이 접수되었습니다. (금융/세무/개발 팀 동시 배정)")

with tab3:
    st.subheader("💼 포트폴리오 관리 (B2B)")
    st.info("보유하신 50개 필지에 대한 일괄 분석 데이터를 제공합니다.")
    
    # Mock Dataframe
    data = {
        "주소": ["김포시 통진읍", "서울시 강남구", "부산시 해운대구"],
        "평가액": ["8.5억", "25억", "12억"],
        "리스크": ["신탁/압류", "근저당", "깨끗함"],
        "추천전략": ["대환/말소", "추가대출", "매각"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 전체 리포트 다운로드 (Excel)", df.to_csv().encode('utf-8'), "portfolio.csv")