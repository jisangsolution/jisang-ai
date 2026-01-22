import os
import sys
import subprocess
import urllib.request
import pandas as pd
from datetime import datetime

# [Step 0] 스마트 런처 (엔터프라이즈 엔진 'reportlab' 설치)
def setup_environment():
    required = {
        "streamlit": "streamlit", 
        "plotly": "plotly", 
        "google-generativeai": "google.generativeai", 
        "python-dotenv": "dotenv", 
        "reportlab": "reportlab"  # ★ 엔진 교체
    }
    needs_install = []
    
    for pkg, mod in required.items():
        try:
            __import__(mod)
        except ImportError:
            needs_install.append(pkg)
    
    if needs_install:
        print("🛠️ [시스템] 엔터프라이즈 PDF 엔진(ReportLab) 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U"] + needs_install)
        os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", __file__])

    # 한글 폰트 다운로드
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path) or os.path.getsize(font_path) < 100:
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        try: urllib.request.urlretrieve(url, font_path)
        except: pass

if "streamlit" not in sys.modules:
    setup_environment()
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

# ================================================================================
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# ★ ReportLab 라이브러리 (안정성 최강)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import io

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [Engine 1] 리포트랩 PDF 생성기 (Perfect Korean PDF)
# --------------------------------------------------------------------------------
def generate_perfect_pdf(address, context):
    # 메모리 버퍼 생성
    buffer = io.BytesIO()
    
    # 캔버스 생성 (A4 사이즈)
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # 폰트 등록 (한글 깨짐 원천 봉쇄)
    font_path = "NanumGothic.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        font_name = 'NanumGothic'
    else:
        font_name = 'Helvetica' # 폰트 없을 시 영문이라도 출력
        
    # --- [페이지 디자인 시작] ---
    
    # 1. 헤더 (우측 상단)
    c.setFont(font_name, 10)
    c.drawRightString(width - 20*mm, height - 20*mm, "Jisang AI Universe Report")
    c.line(20*mm, height - 22*mm, width - 20*mm, height - 22*mm)
    
    # 2. 타이틀 (중앙)
    c.setFont(font_name, 22)
    c.drawCentredString(width / 2, height - 50*mm, "부동산 5대 영역 종합 분석 보고서")
    
    # 3. 기본 정보 박스
    c.setFillColorRGB(0.95, 0.95, 0.95) # 연회색 배경
    c.rect(20*mm, height - 90*mm, width - 40*mm, 30*mm, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0) # 글자색 검정 복구
    
    c.setFont(font_name, 12)
    c.drawString(25*mm, height - 70*mm, f"분석 대상: {address}")
    c.drawString(25*mm, height - 80*mm, f"발행 일자: {datetime.now().strftime('%Y년 %m월 %d일')}")
    c.drawString(120*mm, height - 80*mm, "분석 기관: 지상 AI 파트너스")
    
    # 4. 핵심 분석 결과 (Body)
    y_pos = height - 110*mm
    c.setFont(font_name, 16)
    c.drawString(20*mm, y_pos, "1. 핵심 금융 및 세무 분석 (Fact Check)")
    y_pos -= 10*mm
    
    c.setFont(font_name, 11)
    line_height = 8*mm
    
    facts = [
        f"• [금융] 연간 이자 절감 예상액: {context['finance_saving']:,} 원",
        f"• [세무] 예상 취득세 (공장): {context['tax_est']:,} 원 ({context['tax_rate']}%)",
        f"• [개발] 신축 분양 예상 수익: {context['dev_profit']:,} 원 (ROI {context['dev_roi']}%)",
        f"• [위험] 발견된 권리 리스크: {context['restrictions']}"
    ]
    
    for fact in facts:
        c.drawString(25*mm, y_pos, fact)
        y_pos -= line_height
        
    y_pos -= 10*mm
    
    # 5. AI 솔루션 (Box)
    c.setFont(font_name, 16)
    c.drawString(20*mm, y_pos, "2. AI 심층 솔루션 제언")
    y_pos -= 8*mm
    
    advice_text = [
        "현재 해당 물건은 '신탁등기' 및 '압류' 리스크로 인해 일반적인 담보대출이 불가능합니다.",
        "지상 AI의 알고리즘은 [대부업 상환]과 [신탁 말소]를 동시에 진행하는",
        "'통합 대환 솔루션'을 최적의 해결책으로 제시합니다.",
        "이를 통해 연간 수천만 원의 금융 비용을 절감하고 자산 가치를 회복할 수 있습니다."
    ]
    
    c.setFont(font_name, 11)
    for line in advice_text:
        c.drawString(25*mm, y_pos, line)
        y_pos -= line_height

    # 6. 푸터 (Disclaimer)
    c.setFont(font_name, 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width / 2, 20*mm, "[면책 조항] 본 보고서는 시뮬레이션 결과이며 법적 효력이 없습니다.")
    
    # 저장 및 반환
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

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

    # 보고서 다운로드 섹션
    st.markdown("---")
    st.subheader("📑 보고서 다운로드")
    
    # PDF 생성 (ReportLab)
    try:
        pdf_file = generate_perfect_pdf(st.session_state['current_addr'], context)
        
        col_d1, col_d2 = st.columns([1, 3])
        with col_d1:
            st.download_button(
                label="📄 한글 정밀 보고서 (.pdf)",
                data=pdf_file,
                file_name="Jisang_Universe_Report.pdf",
                mime="application/pdf",
                type="primary"
            )
        with col_d2:
            st.caption("👈 **[엔터프라이즈 엔진 적용]** ReportLab 기술로 한글/레이아웃이 완벽한 PDF를 생성합니다.")
            
    except Exception as e:
        st.error(f"PDF 생성 오류: {e}")

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