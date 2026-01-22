    import os
import sys
import time
import subprocess
import urllib.request
from datetime import datetime

# [Step 0] 필수 라이브러리 및 폰트 자동 세팅
def setup_environment():
    # 1. 라이브러리 설치
    required = {"streamlit": "streamlit", "fpdf": "fpdf"}
    needs_install = []
    for pkg, mod in required.items():
        try:
            __import__(mod)
        except ImportError:
            needs_install.append(pkg)
    if needs_install:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + needs_install)
        os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", __file__])

    # 2. 한글 폰트(나눔고딕) 자동 다운로드
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        print("🛠️ [시스템] 한글 폰트 리소스 다운로드 중... (나눔고딕)")
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        try:
            urllib.request.urlretrieve(url, font_path)
            print("✅ 폰트 설치 완료.")
        except:
            print("⚠️ 폰트 다운로드 실패. 인터넷 연결을 확인하세요.")

if "streamlit" not in sys.modules:
    setup_environment()
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

# ================================================================================
import streamlit as st
from fpdf import FPDF

# --------------------------------------------------------------------------------
# [Engine] 한글 PDF 생성 엔진 (Korean PDF Generator)
# --------------------------------------------------------------------------------
class PDF(FPDF):
    def header(self):
        # 폰트가 있을 때만 한글 적용
        if os.path.exists("NanumGothic.ttf"):
            self.add_font('NanumGothic', '', 'NanumGothic.ttf', uni=True)
            self.set_font('NanumGothic', '', 10)
        else:
            self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Jisang AI Real Estate Solution', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        if os.path.exists("NanumGothic.ttf"):
            self.set_font('NanumGothic', '', 8)
        else:
            self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_korean_pdf(address, data, ai_summary):
    pdf = PDF()
    pdf.add_page()
    
    # 폰트 로드 (파일이 없으면 에러 방지 위해 Arial 사용)
    font_name = 'NanumGothic' if os.path.exists("NanumGothic.ttf") else 'Arial'
    if font_name == 'NanumGothic':
        pdf.add_font(font_name, '', 'NanumGothic.ttf', uni=True)
    
    # 1. 타이틀
    pdf.set_font(font_name, '', 24)
    pdf.cell(0, 20, "부동산 정밀 분석 보고서", 0, 1, 'C')
    pdf.ln(10)
    
    # 2. 기본 정보 박스
    pdf.set_fill_color(240, 242, 246)
    pdf.rect(10, 45, 190, 40, 'F')
    
    pdf.set_font(font_name, '', 12)
    pdf.set_xy(15, 50)
    pdf.cell(30, 10, "분석 대상:", 0, 0)
    pdf.set_font(font_name, '', 12) # 볼드체 효과 대신 크기 유지
    pdf.cell(0, 10, address, 0, 1)
    
    pdf.set_xy(15, 60)
    pdf.set_font(font_name, '', 12)
    pdf.cell(30, 10, "작성 일자:", 0, 0)
    pdf.cell(0, 10, datetime.now().strftime("%Y년 %m월 %d일"), 0, 1)
    
    pdf.set_xy(15, 70)
    pdf.cell(30, 10, "분석 기관:", 0, 0)
    pdf.cell(0, 10, "지상 AI 엔터프라이즈 (Jisang AI)", 0, 1)
    
    pdf.ln(20)
    
    # 3. 핵심 지표 (Financial Facts)
    pdf.set_font(font_name, '', 16)
    pdf.cell(0, 10, "1. 핵심 금융 지표 (Fact Check)", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # 밑줄
    pdf.ln(5)
    
    pdf.set_font(font_name, '', 12)
    facts = [
        f"• LTV (담보인정비율): {data['ltv']}% (고위험군 진입)" if data['ltv'] > 70 else f"• LTV (담보인정비율): {data['ltv']}% (안정권)",
        f"• 총 채권액: {data['total']:,} 원",
        f"• 연간 이자 절감 예상액: {data['saved']:,} 원",
        f"• 권리 침해 내역: {data['restrictions']}"
    ]
    
    for fact in facts:
        pdf.cell(0, 8, fact, 0, 1)
    
    pdf.ln(10)
    
    # 4. AI 심층 분석 (AI Analysis)
    pdf.set_font(font_name, '', 16)
    pdf.cell(0, 10, "2. AI 솔루션 및 제언", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font(font_name, '', 11)
    # AI 텍스트 줄바꿈 처리
    pdf.multi_cell(0, 7, ai_summary)
    
    pdf.ln(20)
    
    # 5. 면책 조항 (Disclaimer)
    pdf.set_font(font_name, '', 10)
    pdf.set_text_color(100, 100, 100) # 회색
    pdf.multi_cell(0, 5, "[면책 조항] 본 보고서는 AI 알고리즘 및 공공 데이터를 기반으로 작성된 참고 자료입니다. 실제 대출 실행 가능 여부와 금리는 금융사의 최종 심사에 따라 달라질 수 있으며, 이에 대한 법적 책임은 지지 않습니다.")
    
    return pdf.output(dest='S').encode('latin-1')

# --------------------------------------------------------------------------------
# [UI] Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="한글 리포트 생성기", page_icon="📄")

st.title("📄 지상 AI 한글 보고서 생성기")
st.markdown("특허받은 **'동적 폰트 주입 기술'**로 별도 설정 없이 완벽한 한글 PDF를 발행합니다.")

# 입력 데이터 시뮬레이션
addr = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1")

# 가상 데이터
data = {
    "ltv": 70.59,
    "total": 600000000,
    "saved": 30000000,
    "restrictions": "신탁등기, 압류(김포세무서)"
}

ai_text = """
현재 해당 물건은 LTV 70%를 초과하는 고위험 자산으로 분류됩니다. 특히 '신탁등기'가 설정되어 있어 일반적인 담보대출이나 매매가 불가능한 '잠김(Lock)' 상태입니다.

[솔루션 제안]
1. 우선순위: 고금리 대부업 자금을 상환하여 신용등급을 회복해야 합니다.
2. 실행방안: 지상 AI 파트너스(신한은행/OK캐피탈)를 통해 '통합 대환 대출'을 신청하십시오.
3. 기대효과: 이를 통해 연간 약 3,000만 원의 금융 비용을 절감하고, 압류를 해제하여 정상적인 재산권 행사가 가능해집니다.
"""

st.markdown("---")
st.subheader("📊 분석 결과 미리보기")
st.info(ai_text)

if st.button("🚀 한글 PDF 보고서 다운로드", type="primary"):
    with st.spinner("한글 폰트 렌더링 및 PDF 생성 중..."):
        # PDF 생성 함수 호출
        pdf_bytes = generate_korean_pdf(addr, data, ai_text)
        
        st.download_button(
            label="📥 리포트 다운로드 (.pdf)",
            data=pdf_bytes,
            file_name=f"지상AI_보고서_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
        st.success("생성 완료! 위 버튼을 눌러 다운로드하세요.")

# 디버깅 정보
if os.path.exists("NanumGothic.ttf"):
    st.caption("✅ 시스템 상태: 한글 폰트(NanumGothic) 정상 로드됨")
else:
    st.caption("⚠️ 시스템 상태: 폰트 다운로드 대기 중 (최초 실행 시 자동 설치됨)")