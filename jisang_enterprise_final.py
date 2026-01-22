import os
import sys
import time
import subprocess
import random
import io
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
        # pip install -U 로 강제 업데이트
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
# [Engine 1] 리포트 생성 엔진 (Crash 방지)
# --------------------------------------------------------------------------------
class ReportGenerator:
    @staticmethod
    def create_markdown(address, facts, ai_text):
        """한글이 완벽하게 지원되는 마크다운 리포트"""
        content = f"""
# 부동산 종합 분석 리포트
**대상**: {address}
**작성일**: {datetime.now().strftime('%Y-%m-%d')}
**분석툴**: Jisang AI Enterprise

---
## 1. 핵심 데이터 (Fact Check)
* **LTV (담보비율)**: {facts['ltv']}%
* **총 채권액**: {facts['total']:,} 원
* **대환 타겟**: {facts['count']} 건
* **연간 예상 절감액**: {facts['saved']:,} 원

---
## 2. AI 심층 컨설팅
{ai_text}

---
## 3. 면책 조항
본 리포트는 시뮬레이션 결과이며 법적 효력이 없습니다.
"""
        return content.encode('utf-8')

    @staticmethod
    def create_english_pdf(address, facts):
        """에러 없이 작동하는 영문 요약 PDF (Global Standard)"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Jisang AI | Real Estate Summary", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Target: {address} (ID: {random.randint(1000,9999)})", 0, 1)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "1. Financial Facts", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"- LTV Ratio: {facts['ltv']}%", 0, 1)
        pdf.cell(0, 10, f"- Total Bond: {facts['total']:,} KRW", 0, 1)
        pdf.cell(0, 10, f"- Est. Saving: {facts['saved']:,} KRW/year", 0, 1)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "2. AI Diagnosis (Summary)", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 7, "This property is classified as 'High Risk' due to high LTV. Refinancing is strongly recommended to improve cash flow.")
        
        return pdf.output(dest='S').encode('latin-1')

# --------------------------------------------------------------------------------
# [Engine 2] AI 모델 연결 (무한 재시도)
# --------------------------------------------------------------------------------
def get_robust_response(prompt):
    models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash']
    
    for m in models:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content(prompt)
            if response.text:
                return response.text, m
        except:
            continue
            
    # 모든 모델 실패 시 표준 텍스트 반환
    return """
    ### 🚨 시스템 분석 요약 (Offline Mode)
    * **진단**: 현재 **신탁등기** 및 **압류**가 확인되어 일반적인 매매나 대출이 제한될 수 있습니다.
    * **솔루션**: 전문가를 통한 **신탁 말소** 및 **통합 대환** 솔루션이 필요합니다.
    * **제언**: 아래 '1:1 금융 솔루션 상담'을 통해 상세 진단을 받으십시오.
    """, "Standard-Fallback"

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
    # 가상 데이터
    raw = {
        "address": addr, "market_price": 850000000,
        "bonds": [{"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
                  {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}],
        "restrictions": ["신탁등기(우리자산신탁)", "압류(김포세무서)"]
    }
    facts = FactChecker.process(raw)
    
    # 페르소나별 프롬프트
    role_desc = {
        "금융/대환": "대출 상담사 관점에서 이자 절감과 신용 회복 전략 제시",
        "세무/자산": "세무사 관점에서 압류 해제 시 양도세/상속세 절세 전략 제시",
        "개발/시행": "부동산 개발업자 관점에서 토지 규제 분석 및 PF 가능성 제시",
        "중개/매매": "공인중개사 관점에서 매물 적정가 및 거래 리스크 제시",
        "정책/기획": "정책 입안자 관점에서 해당 지역 규제 완화 가능성 제시"
    }
    
    prompt = f"""
    당신은 대한민국 최고의 부동산 전문가입니다.
    관점: {role_desc.get(mode, "종합 분석")}
    대상: {raw['address']}, LTV {facts['ltv']}%, 권리하자 {len(raw['restrictions'])}건.
    
    [출력 양식 (Markdown)]
    ### 1. 🔍 핵심 진단
    ### 2. 🚀 솔루션 ({mode} 특화)
    ### 3. 💰 기대 가치
    (명확하고 전문적인 어조로 작성)
    """
    
    ai_msg, used_model = get_robust_response(prompt)
    return raw, facts, ai_msg, used_model

# --------------------------------------------------------------------------------
# [UI/UX] Enterprise Dashboard
# --------------------------------------------------------------------------------
st.set_page_config(page_title="지상 AI Enterprise", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .big-font { font-size: 20px !important; }
    .success-box { padding:15px; background-color:#d4edda; color:#155724; border-radius:5px; margin-top:10px; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=50)
    st.title("Jisang Platform")
    st.caption("Total Real Estate Solutions")
    
    # 분석 모드 (5대 분야)
    analysis_mode = st.selectbox("분석 모드 (Persona)", 
        ["금융/대환", "세무/자산", "개발/시행", "중개/매매", "정책/기획"])
    
    st.markdown("---")
    st.markdown("**📂 포트폴리오 (Batch)**")
    # 예시 주소 자동 입력
    addr_input = st.text_area("주소 입력 (줄바꿈 구분)", 
        "김포시 통진읍 도사리 163-1\n서울시 강남구 역삼동 825-1\n경기도 고양시 일산동구 장항동 756", height=120)
    
    start_btn = st.button("🚀 통합 분석 실행", type="primary", use_container_width=True)
    st.markdown("---")
    st.info("System Online\nv4.0.0 Stable")

# Main
if start_btn:
    if not api_key:
        st.error("❌ API Key가 설정되지 않았습니다.")
    else:
        addresses = [a.strip() for a in addr_input.split('\n') if a.strip()]
        st.title(f"🏢 부동산 {analysis_mode} 종합 리포트")
        
        # 탭 생성
        tabs = st.tabs([f"📍 {a[:10]}.." for a in addresses])
        
        for i, tab in enumerate(tabs):
            with tab:
                curr_addr = addresses[i]
                
                # 분석 실행 (스피너로 로딩 연출)
                with st.spinner(f"AI가 '{curr_addr}'을(를) {analysis_mode} 관점에서 분석 중..."):
                    raw, facts, ai_text, model_name = run_simulation(curr_addr, analysis_mode)
                
                # 상단 메트릭
                m1, m2, m3 = st.columns(3)
                m1.metric("LTV (담보비율)", f"{facts['ltv']}%", "High Risk", delta_color="inverse")
                m2.metric("권리 리스크", f"{len(raw['restrictions'])}건", "신탁/압류", delta_color="inverse")
                m3.metric("잠재 가치 (절감액)", f"{facts['saved']/10000:,.0f}만 원/년", "기회", delta_color="normal")
                
                # 본문
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"### 💡 AI 심층 컨설팅 ({model_name})")
                    st.markdown(ai_text)
                    
                    st.markdown("---")
                    st.subheader("📑 리포트 다운로드")
                    d1, d2 = st.columns(2)
                    with d1:
                        # 한글 마크다운 다운로드
                        md_file = ReportGenerator.create_markdown(curr_addr, facts, ai_text)
                        st.download_button("📄 정밀 리포트 (한글 .md)", md_file, file_name=f"Report_{i}.md", use_container_width=True)
                    with d2:
                        # 영문 PDF 다운로드 (에러 방지용)
                        pdf_file = ReportGenerator.create_english_pdf(curr_addr, facts)
                        st.download_button("🇺🇸 Summary Report (.pdf)", pdf_file, file_name=f"Summary_{i}.pdf", use_container_width=True)

                with c2:
                    st.markdown("### 🤝 플랫폼 파트너스")
                    
                    # 1. 금융 매칭 (상태 유지 기능)
                    if f"match_{i}" not in st.session_state: st.session_state[f"match_{i}"] = False
                    
                    if not st.session_state[f"match_{i}"]:
                        if st.button(f"📞 금융 솔루션 매칭", key=f"btn_match_{i}", use_container_width=True):
                            st.session_state[f"match_{i}"] = True
                            st.rerun()
                    else:
                        st.success("✅ 매칭 요청 완료!")
                        st.caption("제안 도착: 신한은행, 우리은행, OK캐피탈")
                        st.button("상담 취소", key=f"cancel_{i}")

                    # 2. 탁상감정 의뢰
                    st.markdown("---")
                    if f"appr_{i}" not in st.session_state: st.session_state[f"appr_{i}"] = False
                    
                    if not st.session_state[f"appr_{i}"]:
                        if st.button(f"🏠 탁상감정 의뢰 (무료)", key=f"btn_appr_{i}", use_container_width=True):
                            st.session_state[f"appr_{i}"] = True
                            st.toast(f"문자 발송: [한국감정평가법인]에 '{curr_addr}' 의뢰 접수됨.")
                            st.rerun()
                    else:
                        st.info("🕒 감정 진행 중...")
                        st.caption(f"접수번호: 2026-{random.randint(10000,99999)}")
                    
                    # 차트
                    st.markdown("---")
                    df = pd.DataFrame({"State": ["Current", "Solution"], "Cost": [4800, 4800-(facts['saved']/10000)]})
                    fig = px.bar(df, x="State", y="Cost", color="State", height=200, title="현금 흐름 개선")
                    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 사이드바에서 분석 모드를 선택하고 '통합 분석 실행'을 누르세요.")
    st.markdown("#### 🌟 지상 AI 플랫폼의 차별점")
    st.markdown("""
    1. **완전무결 데이터**: Python 알고리즘 기반 팩트 체크
    2. **5대 전문 영역**: 금융, 세무, 개발, 중개, 정책 관점 분석
    3. **One-Stop 플랫폼**: 금융사 매칭 및 감정평가 자동 의뢰
    """)