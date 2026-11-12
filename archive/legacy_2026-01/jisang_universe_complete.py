import os
import sys
import subprocess
import urllib.request
import pandas as pd
from datetime import datetime

# [Step 0] 스마트 런처 & 폰트 자동 세팅
def setup_environment():
    # 1. 라이브러리 설치
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

    # 2. 한글 폰트 다운로드 (PDF용)
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        try:
            urllib.request.urlretrieve(url, font_path)
        except:
            pass

if "streamlit" not in sys.modules:
    setup_environment()
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [Engine 1] 한글 PDF 생성기 (Korean PDF Generator)
# --------------------------------------------------------------------------------
class PDF(FPDF):
    def header(self):
        font_path = 'NanumGothic.ttf' if os.path.exists('NanumGothic.ttf') else 'Arial'
        if font_path == 'NanumGothic.ttf':
            self.add_font('NanumGothic', '', font_path, uni=True)
            self.set_font('NanumGothic', '', 10)
        else:
            self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Jisang AI Universe Report', 0, 1, 'R')
        self.ln(5)

def generate_korean_pdf(address, context):
    pdf = PDF()
    pdf.add_page()
    
    font_name = 'NanumGothic' if os.path.exists("NanumGothic.ttf") else 'Arial'
    if font_name == 'NanumGothic':
        pdf.add_font(font_name, '', 'NanumGothic.ttf', uni=True)
    
    # 1. 타이틀
    pdf.set_font(font_name, '', 20)
    pdf.cell(0, 15, "부동산 5대 영역 종합 분석 보고서", 0, 1, 'C')
    pdf.ln(10)
    
    # 2. 개요
    pdf.set_font(font_name, '', 12)
    pdf.cell(0, 10, f"분석 대상: {address}", 0, 1)
    pdf.cell(0, 10, f"발행 일자: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
    pdf.ln(5)
    
    # 3. 상세 분석
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font(font_name, '', 14)
    pdf.cell(0, 10, "1. 핵심 분석 요약", 0, 1, 'L', True)
    pdf.ln(5)
    
    pdf.set_font(font_name, '', 11)
    lines = [
        f"💰 [금융] 연간 이자 절감액: {context['finance_saving']:,} 원",
        f"⚖️ [세무] 예상 취득세: {context['tax_est']:,} 원 ({context['tax_rate']}%)",
        f"🏗️ [개발] 예상 분양 수익: {context['dev_profit']:,} 원 (ROI {context['dev_roi']}%)",
        f"🚨 [리스크] 발견된 권리하자: {context['restrictions']}"
    ]
    for line in lines:
        pdf.cell(0, 8, line, 0, 1)
        
    pdf.ln(10)
    pdf.set_font(font_name, '', 14)
    pdf.cell(0, 10, "2. AI 솔루션 제언", 0, 1, 'L', True)
    pdf.ln(5)
    pdf.set_font(font_name, '', 11)
    pdf.multi_cell(0, 7, f"현재 해당 물건은 {context['restrictions']} 등의 권리 리스크가 존재하여 일반적인 매매나 대출 실행이 어렵습니다. 지상 AI 파트너스를 통해 '신탁 말소'와 '대환'을 동시에 진행하는 통합 솔루션을 권장합니다.")
    
    return pdf.output(dest='S').encode('latin-1')

# --------------------------------------------------------------------------------
# [Engine 2] 도메인 계산기
# --------------------------------------------------------------------------------
class DomainExpert:
    @staticmethod
    def calc_finance(total_debt):
        return int(total_debt * 0.10)

    @staticmethod
    def calc_tax(price):
        rate = 0.046 
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
    if any(k in user_input for k in ["안내", "도와줘", "메뉴"]):
        return "👋 **환영합니다.**\n\n1. **금융**: 이자 절감\n2. **세무**: 취득세 계산\n3. **개발**: 수익률 분석\n4. **권리**: 리스크 진단"
    if any(k in user_input for k in ["금융", "이자", "대출"]):
        return f"💰 **금융 분석**: 연간 **{context['finance_saving']:,}원** 절감이 가능합니다."
    if any(k in user_input for k in ["세금", "취득", "양도"]):
        return f"⚖️ **세무 분석**: 예상 취득세는 **{context['tax_est']:,}원**입니다."
    if any(k in user_input for k in ["개발", "수익"]):
        return f"🏗️ **개발 분석**: 예상 수익은 **{context['dev_profit']:,}원** (ROI {context['dev_roi']}%)입니다."
    return "죄송합니다. '안내해줘'라고 입력해 보세요."

# --------------------------------------------------------------------------------
# [UI] Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Jisang AI Universe", page_icon="🌌", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
    st.title("🌌 Jisang Universe")
    
    st.markdown("### 📍 분석 대상")
    addr_input = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1")
    
    if st.button("🚀 분석 실행", type="primary", use_container_width=True):
        st.session_state['current_addr'] = addr_input
        st.session_state.uni_chat = [{"role": "assistant", "content": f"안녕하세요! **'{addr_input}'** 전담 AI입니다."}]

if 'current_addr' not in st.session_state:
    st.session_state['current_addr'] = "김포시 통진읍 도사리 163-1"

# Data Setup
price, debt = 850000000, 600000000
saving = DomainExpert.calc_finance(debt)
tax, tax_rate = DomainExpert.calc_tax(price)
profit, roi = DomainExpert.calc_development(price, 363)
context = {"finance_saving": saving, "tax_est": tax, "tax_rate": tax_rate, "dev_profit": profit, "dev_roi": roi, "restrictions": "신탁등기, 압류"}

# Main Layout
st.title(f"🏢 {st.session_state['current_addr']} 종합 분석")
tab1, tab2, tab3 = st.tabs(["📊 통합 대시보드", "💬 AI 컨시어지", "📂 B2B 포트폴리오"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 금융 (이자절감)", f"{saving/10000:,.0f}만 원/년")
    c2.metric("⚖️ 세무 (예상취득세)", f"{tax/10000:,.0f}만 원")
    c3.metric("🏗️ 개발 (예상수익)", f"{profit/10000:,.0f}만 원")
    
    st.markdown("---")
    col_risk, col_sol = st.columns([1, 2])
    with col_risk:
        st.error(f"🔴 권리 위험: {context['restrictions']}")
    with col_sol:
        st.success("**✅ 지상 AI 통합 솔루션**")
        st.write("- **금융**: 고금리 대환 실행\n- **세무**: 중과세 배제 검토\n- **개발**: 공장 증축 타당성 확인")

    # ★ [복구 완료] 한글 PDF 다운로드 버튼
    st.markdown("---")
    st.subheader("📑 보고서 다운로드")
    
    # PDF 생성
    pdf_data = generate_korean_pdf(st.session_state['current_addr'], context)
    
    col_d1, col_d2 = st.columns([1, 3])
    with col_d1:
        st.download_button(
            label="📄 한글 정밀 보고서 (.pdf)",
            data=pdf_data,
            file_name="Jisang_Report.pdf",
            mime="application/pdf",
            type="primary"
        )
    with col_d2:
        st.caption("👈 클릭 시 5대 영역(금융/세무/개발 등) 상세 분석 결과가 담긴 PDF 파일이 다운로드됩니다.")

with tab2:
    st.subheader("💬 AI 부동산 비서")
    if "uni_chat" not in st.session_state:
        st.session_state.uni_chat = [{"role": "assistant", "content": f"안녕하세요! **'{st.session_state['current_addr']}'** 분석을 완료했습니다."}]
    
    for msg in st.session_state.uni_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("질문 입력 (예: 안내해줘, 이자 절감액은?)"):
        st.session_state.uni_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        reply = get_universe_response(prompt, context)
        st.session_state.uni_chat.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

with tab3:
    st.subheader("💼 포트폴리오 관리 (B2B)")
    data = {"주소": [st.session_state['current_addr'], "서울시 강남구"], "평가액": ["8.5억", "25억"], "추천전략": ["대환/말소", "추가대출"]}
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 엑셀 다운로드 (.csv)", df.to_csv().encode('utf-8'), "portfolio.csv")