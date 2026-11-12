import os
import sys
import subprocess
import pandas as pd
from datetime import datetime

# [Step 0] 스마트 런처
def install_and_launch():
    required = {"streamlit": "streamlit", "plotly": "plotly", "google-generativeai": "google.generativeai", "python-dotenv": "dotenv", "fpdf": "fpdf"}
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

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [Engine] 도메인 계산기
# --------------------------------------------------------------------------------
class DomainExpert:
    @staticmethod
    def calc_finance(total_debt):
        return int(total_debt * 0.10) # 10% 절감 가정

    @staticmethod
    def calc_tax(price):
        rate = 0.046 # 공장 취득세율
        return int(price * rate), rate * 100

    @staticmethod
    def calc_development(price, size):
        cost = size * 5000000 
        revenue = size * 10000000
        profit = revenue - cost - price
        roi = (profit / (price + cost)) * 100
        return int(profit), round(roi, 2)

# --------------------------------------------------------------------------------
# [Chatbot] 응답 로직
# --------------------------------------------------------------------------------
def get_universe_response(user_input, context):
    user_input = user_input.lower()
    
    if any(k in user_input for k in ["안내", "도와줘", "시작", "기능", "메뉴"]):
        return """
        👋 **지상 AI 유니버스에 오신 것을 환영합니다.**
        
        원하시는 분석 분야를 선택하거나 질문해 주세요:
        
        1. **금융 분석**: "이자 얼마나 줄일 수 있어?"
        2. **세무 계산**: "취득세 계산해줘."
        3. **개발 타당성**: "이 땅 개발하면 얼마나 벌어?"
        4. **권리 분석**: "신탁등기가 뭐야?"
        """
    if any(k in user_input for k in ["금융", "이자", "대출", "대환"]):
        return f"💰 **금융 분석**: 연간 **{context['finance_saving']:,}원**의 이자 절감이 가능합니다. 대환 상담을 잡아드릴까요?"
    if any(k in user_input for k in ["세금", "세무", "취득", "양도"]):
        return f"⚖️ **세무 분석**: 예상 취득세는 **{context['tax_est']:,}원** ({context['tax_rate']}%)입니다."
    if any(k in user_input for k in ["개발", "건축", "수익"]):
        return f"🏗️ **개발 분석**: 신축 분양 시 예상 수익은 **{context['dev_profit']:,}원** (ROI {context['dev_roi']}%)입니다."
    if any(k in user_input for k in ["권리", "신탁", "압류", "위험"]):
        return f"🚨 **권리 경고**: 현재 **{context['restrictions']}**가 설정되어 있어 주의가 필요합니다."

    return "죄송합니다. '안내해줘'라고 입력하시면 메뉴를 보여드립니다."

# --------------------------------------------------------------------------------
# [UI] Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI Universe", page_icon="🌌", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
    st.title("🌌 Jisang Universe")
    st.caption("Total Real Estate Platform")
    
    # ★ [복구 완료] 주소 입력창을 다시 살렸습니다.
    st.markdown("### 📍 분석 대상")
    addr_input = st.text_input("주소를 입력하세요", "김포시 통진읍 도사리 163-1")
    
    if st.button("🚀 분석 실행", type="primary", use_container_width=True):
        st.toast(f"'{addr_input}' 분석 데이터 로드 완료")
        st.session_state['current_addr'] = addr_input # 주소 저장
        # 채팅 기록 리셋 (새 주소 분석 시)
        st.session_state.uni_chat = [{"role": "assistant", "content": f"안녕하세요! **'{addr_input}'** 전담 AI입니다. 무엇을 도와드릴까요?"}]

# 초기값 설정
if 'current_addr' not in st.session_state:
    st.session_state['current_addr'] = "김포시 통진읍 도사리 163-1"

# Mock Data (시뮬레이션용 고정값)
price = 850000000
debt = 600000000
saving = DomainExpert.calc_finance(debt)
tax, tax_rate = DomainExpert.calc_tax(price)
profit, roi = DomainExpert.calc_development(price, 363)

context = {
    "finance_saving": saving,
    "tax_est": tax,
    "tax_rate": tax_rate,
    "dev_profit": profit,
    "dev_roi": roi,
    "restrictions": "신탁등기, 압류"
}

# Main Layout
st.title(f"🏢 {st.session_state['current_addr']} 종합 분석")
st.markdown("#### 금융 · 세무 · 개발 · 중개 · 정책을 하나로 연결합니다.")

tab1, tab2, tab3 = st.tabs(["📊 통합 대시보드", "💬 AI 컨시어지", "📂 B2B 포트폴리오"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 금융 (이자절감)", f"{saving/10000:,.0f}만 원/년", "High Impact")
    c2.metric("⚖️ 세무 (예상취득세)", f"{tax/10000:,.0f}만 원", f"{tax_rate}%")
    c3.metric("🏗️ 개발 (예상수익)", f"{profit/10000:,.0f}만 원", f"ROI {roi}%")
    
    st.markdown("---")
    col_risk, col_sol = st.columns([1, 2])
    with col_risk:
        st.error(f"🔴 권리 위험: {context['restrictions']}")
    with col_sol:
        st.success("**✅ 지상 AI 통합 솔루션**")
        st.write("1. **금융**: 고금리 대부업 대환 실행")
        st.write("2. **세무**: 중과세 배제 요건 검토")
        st.write("3. **개발**: 건폐율 상향 조정 가능성 타진")

with tab2:
    st.subheader("💬 AI 부동산 비서")
    
    if "uni_chat" not in st.session_state:
        st.session_state.uni_chat = [{"role": "assistant", "content": f"안녕하세요! **'{st.session_state['current_addr']}'** 분석을 완료했습니다."}]
    
    # Chat Display
    for msg in st.session_state.uni_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat Input
    if prompt := st.chat_input("질문 입력 (예: 안내해줘, 이자 절감액은?)"):
        st.session_state.uni_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        reply = get_universe_response(prompt, context)
        st.session_state.uni_chat.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    st.markdown("---")
    if st.button("📞 전문가 호출 (Premium)", type="primary", use_container_width=True):
        st.balloons()
        st.success("접수 완료. 담당자가 연락드립니다.")

with tab3:
    st.subheader("💼 포트폴리오 관리 (B2B)")
    data = {
        "주소": [st.session_state['current_addr'], "서울시 강남구 역삼동", "부산시 해운대구 우동"],
        "평가액": ["8.5억", "25억", "12억"],
        "리스크": ["신탁/압류", "근저당", "깨끗함"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)