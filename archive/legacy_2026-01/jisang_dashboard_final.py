import os
import sys
import time
import subprocess
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 스마트 런처 (Smart Launcher) - 무한 설치 버그 수정
# --------------------------------------------------------------------------------
def install_and_launch():
    # 패키지명(pip install 이름) : 모듈명(import 이름) 매핑
    required = {
        "streamlit": "streamlit",
        "plotly": "plotly",
        "google-generativeai": "google.generativeai",
        "python-dotenv": "dotenv",
        "python-dateutil": "dateutil"
    }
    
    needs_install = []
    print("🛠️ [시스템] 필수 엔진 점검 중...", end="")
    
    for package, module in required.items():
        try:
            __import__(module)
        except ImportError:
            needs_install.append(package)
    
    if needs_install:
        print(f"\n⚠️ 필수 도구 설치가 필요합니다: {', '.join(needs_install)}")
        print("⏳ 설치 중... (약 30초 소요)")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + needs_install)
            print("✅ 설치 완료! 대시보드를 실행합니다.")
            # 설치 직후 재실행 (Windows 환경 호환성 확보)
            os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", __file__])
        except Exception as e:
            print(f"❌ 설치 중 오류 발생: {e}")
            sys.exit(1)
    else:
        print(" 완료! (모든 엔진 정상)")

# Streamlit 구동 로직 (재귀 호출 방지)
if "streamlit" not in sys.modules:
    install_and_launch()
    # 설치가 다 되어있다면 Streamlit으로 실행 전환
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

# ================================================================================
# [여기서부터 대시보드 코드]
# ================================================================================
import streamlit as st
import plotly.express as px
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [UI 디자인] 0.1% Pro Styling
# --------------------------------------------------------------------------------
st.set_page_config(page_title="지상 AI Pro | 부동산 딥테크", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    /* 등급 카드 스타일 */
    .grade-box {
        padding: 20px; border-radius: 12px; text-align: center; color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px;
    }
    .grade-s { background: linear-gradient(135deg, #00b09b, #96c93d); } /* Green */
    .grade-a { background: linear-gradient(135deg, #4facfe, #00f2fe); } /* Blue */
    .grade-b { background: linear-gradient(135deg, #f093fb, #f5576c); } /* Red/Pink */
    .grade-title { font-size: 48px; font-weight: 800; margin: 0; }
    .grade-desc { font-size: 16px; opacity: 0.9; }
    
    /* 메트릭 카드 스타일 */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa; border: 1px solid #dee2e6;
        padding: 15px; border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# [Backend Logic] Opal + FactChecker + Brain
# --------------------------------------------------------------------------------
def get_best_model():
    """모델 자동 탐색 (에러 방지)"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 2.0 Flash가 있으면 최우선 사용 (속도/성능 최강)
        preferred = ['models/gemini-2.0-flash', 'models/gemini-1.5-flash', 'models/gemini-pro']
        for p in preferred:
            if p in models: return p
        return 'gemini-pro'
    except: return 'gemini-pro'

class FactChecker:
    @staticmethod
    def process(data):
        target_bonds = []
        saved_interest = 0
        
        # 날짜 및 금리 시뮬레이션
        for bond in data['bonds']:
            target_date = datetime.strptime(bond['date'], "%Y.%m.%d")
            diff = relativedelta(datetime.now(), target_date)
            months = diff.years * 12 + diff.months
            
            # 24개월 이상이거나 대부업이면 타겟
            is_target = months >= 24 or bond['type'] == "대부업"
            if is_target:
                target_bonds.append(bond)
                # 절감액 추정: 대부업(10%p), 1금융(1.5%p)
                gap = 0.10 if bond['type'] == "대부업" else 0.015
                saved_interest += bond['amount'] * gap
        
        total_bond = sum(b['amount'] for b in data['bonds'])
        ltv = round((total_bond / data['market_price']) * 100, 2)
        
        return {
            "ltv": ltv,
            "refinance_count": len(target_bonds),
            "total_bond": total_bond,
            "saved_interest_year": int(saved_interest),
            "risk_score": 100 - (len(data['restrictions']) * 15) - (20 if ltv > 80 else 0)
        }

def run_simulation(address):
    # Opal Agent UI Simulation
    with st.status("💎 Opal Agent 가동 중...", expanded=True) as status:
        st.write("🌐 인터넷등기소(IROS) 접속 및 보안 모듈 로드...")
        time.sleep(0.4)
        st.write("📄 등기사항전부증명서(말소사항포함) 발급 완료")
        time.sleep(0.4)
        st.write("🏗️ 건축물대장 및 토지이용계획원 대조 중...")
        time.sleep(0.4)
        status.update(label="✅ 데이터 수집 및 무결성 검증 완료!", state="complete", expanded=False)

    # 가상 데이터 (케이스: 통진읍 도사리 공장)
    raw_data = {
        "address": address,
        "market_price": 850000000, 
        "bonds": [
            {"bank": "국민은행", "date": "2018.06.20", "amount": 400000000, "type": "1금융"},
            {"bank": "러시앤캐시", "date": "2024.01.10", "amount": 200000000, "type": "대부업"}
        ],
        "restrictions": ["신탁등기(우리자산신탁)", "압류(김포세무서)"]
    }
    
    facts = FactChecker.process(raw_data)
    
    # Brain (Gemini)
    model_name = get_best_model()
    model = genai.GenerativeModel(model_name)
    prompt = f"""
    부동산 권리분석 및 금융 컨설팅 리포트 작성.
    - 입력: {raw_data}
    - 팩트: {facts}
    
    [작성 원칙]
    1. 등급: B- (리스크는 있으나 금융 해결책 명확함)
    2. 핵심 전략: 대부업(2억) 및 신탁 말소 동시 진행 시 가치 상승분 설명.
    3. 톤앤매너: 냉철하고 전문적인 금융 전문가 어조.
    """
    try:
        response = model.generate_content(prompt)
        ai_report = response.text
    except:
        ai_report = "⚠️ AI 서버 연결 지연. 팩트 데이터 위주로 참고하십시오."

    return raw_data, facts, ai_report

# --------------------------------------------------------------------------------
# [Frontend] 메인 대시보드
# --------------------------------------------------------------------------------
# 사이드바
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=50)
    st.markdown("### **Jisang AI Pro**")
    st.caption("Ver 3.5.2 (Build 20260118)")
    st.markdown("---")
    st.success(f"🟢 System Online\n\nModel: {get_best_model()}")
    st.markdown("---")
    st.info("**Developer Mode**\n\nAll Modules Active")

# 메인 화면
st.title("🏙️ 지상 AI | 부동산 딥테크 솔루션")
st.markdown("##### :zap: 데이터 무결성(Integrity) 기반 초격차 의사결정 시스템")
st.markdown("---")

# 입력창
c1, c2 = st.columns([3, 1])
with c1:
    addr_input = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1", label_visibility="collapsed")
with c2:
    start_btn = st.button("🚀 원클릭 분석 시작", type="primary", use_container_width=True)

if start_btn:
    if not api_key:
        st.error("❌ API Key가 설정되지 않았습니다. .env 파일을 확인하세요.")
    else:
        raw, facts, ai_text = run_simulation(addr_input)

        # 1. 등급 및 핵심 지표
        st.markdown("### 🎯 분석 결론")
        col_grade, col_metrics = st.columns([1, 2])
        
        with col_grade:
            # 등급 로직
            score = facts['risk_score']
            if score >= 80: g_cls, g_txt = "grade-s", "S (강력 추천)"
            elif score >= 60: g_cls, g_txt = "grade-a", "A (안전)"
            elif score >= 40: g_cls, g_txt = "grade-b", "B- (주의/기회)"
            else: g_cls, g_txt = "grade-c", "C (위험)"
            
            st.markdown(f"""
                <div class="grade-box {g_cls}">
                    <p class="grade-title">{g_txt.split()[0]}</p>
                    <p class="grade-desc">{g_txt}</p>
                </div>
            """, unsafe_allow_html=True)

        with col_metrics:
            m1, m2, m3 = st.columns(3)
            m1.metric("LTV (담보비율)", f"{facts['ltv']}%", "안정권 대비 +20%", delta_color="inverse")
            m2.metric("권리 리스크", f"{len(raw['restrictions'])}건", "신탁/압류", delta_color="inverse")
            m3.metric("💰 대환 기대수익", f"연 {facts['saved_interest_year']/10000:,.0f}만 원", "즉시 절감", delta_color="normal")

        # 2. 금융 차트 (시각화)
        st.markdown("---")
        st.markdown("### 📊 금융 비용 최적화 시뮬레이션")
        
        chart_col, text_col = st.columns([1, 1])
        with chart_col:
            # Plotly 차트
            df_chart = pd.DataFrame({
                "상태": ["현재 (고금리)", "지상 AI 솔루션"],
                "연간 이자비용 (만원)": [4500, 4500 - (facts['saved_interest_year']/10000)]
            })
            fig = px.bar(df_chart, x="상태", y="연간 이자비용 (만원)", color="상태", text_auto=True,
                         color_discrete_sequence=['#ff6b6b', '#1dd1a1'])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
        with text_col:
            st.info("💡 **AI Insight**")
            st.write(ai_text)

        # 3. 상세 데이터 탭
        st.markdown("---")
        tab1, tab2 = st.tabs(["🛡️ 무결성 검증 데이터 (FactChecker)", "💾 원본 공적장부 (Opal)"])
        with tab1:
            st.json(facts)
        with tab2:
            st.json(raw)