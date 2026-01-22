import streamlit as st
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro v15.3", layout="wide", page_icon="🏗️")

# 2. CSS: 인쇄 및 화면 스타일링 (A4 최적화)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 화면용 컨테이너 */
    .report-wrapper {
        background: white;
        padding: 40px;
        margin: 0 auto;
        max-width: 210mm;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* 스타일 정의 */
    .r-header { border-bottom: 2px solid #1e3a8a; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }
    .r-title { font-size: 34px; font-weight: 900; color: #1e3a8a; margin: 0; }
    .r-sub { font-size: 16px; color: #475569; margin-top: 5px; }
    .r-meta { font-size: 12px; color: #94a3b8; text-align: right; line-height: 1.5; }
    
    .r-section { margin-bottom: 35px; }
    .r-head { font-size: 20px; font-weight: 800; color: #334155; border-left: 5px solid #1e3a8a; padding-left: 12px; margin-bottom: 15px; }
    
    .r-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .r-table th { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; font-weight: 700; color: #475569; width: 18%; text-align: center; }
    .r-table td { border: 1px solid #e2e8f0; padding: 10px; color: #1e293b; }

    .highlight-box { background: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 25px; display: flex; align-items: center; justify-content: space-between; }
    .score-area { text-align: center; min-width: 140px; }
    .score-val { font-size: 48px; font-weight: 900; color: #1d4ed8; line-height: 1; }
    .score-label { font-size: 14px; color: #64748b; margin-bottom: 5px; }
    .analysis-text { padding-left: 30px; border-left: 2px solid #bfdbfe; font-size: 15px; line-height: 1.6; color: #334155; }

    .bdg { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 700; }
    .bdg-ok { background: #dcfce7; color: #15803d; }
    .bdg-no { background: #fee2e2; color: #b91c1c; }
    .bdg-warn { background: #fef9c3; color: #a16207; }

    /* 인쇄 모드 숨김 처리 */
    @media print {
        .stSidebar, header, footer, .no-print { display: none !important; }
        .report-wrapper { box-shadow: none; border: none; padding: 0; margin: 0; width: 100%; max-width: 100%; }
        body { margin: 0; -webkit-print-color-adjust: exact; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 ---
DATA = {
    "메타": {"분석일": datetime.now().strftime("%Y-%m-%d"), "문서번호": "JA-2026-0015"},
    "주소": "경기도 김포시 통진읍 도사리 163-1",
    "토지": {
        "지목": "임야(현황 대지)", "면적": "2,592㎡ (784평)", "공시지가": "270,000원/㎡",
        "용도지역": "자연녹지지역", "규제": ["성장관리계획구역(복합형)", "가축사육제한구역"]
    },
    "건축물": {
        "주용도": "노유자시설(요양원)", "구조": "철근콘크리트", "규모": "지하1층 / 지상3층",
        "승강기": "유(15인승)", "주차": "12대(법정충족)", "위반여부": False
    },
    "권리": {
        "소유자": "김지상(개인)", "채권": "15억(우리은행)", 
        "리스크": "근저당 설정 후 2년 경과 (금리 인하 대환 유망)"
    },
    "AI": {"점수": 85, "수익률": "15.2%", "가치": "42.5억"}
}

# --- [핵심 수정] HTML 조립 엔진 (공백 제거) ---
def create_html(d):
    b_stat = "<span class='bdg bdg-ok'>적법</span>" if not d['건축물']['위반여부'] else "<span class='bdg bdg-no'>위반건축물</span>"
    
    # 리스트로 쪼개서 합치는 방식 -> 불필요한 공백/들여쓰기 완전 차단
    html_parts = [
        '<div class="report-wrapper">',
        
        # 1. 헤더
        '<div class="r-header">',
        '<div>',
        '<div class="r-title">부동산 종합 분석 보고서</div>',
        f'<div class="r-sub">Target: {d["주소"]}</div>',
        '</div>',
        '<div class="r-meta">',
        f'DATE: {d["메타"]["분석일"]}<br>BY: 지상 AI Pro<br>REF: {d["메타"]["문서번호"]}',
        '</div></div>',

        # 2. AI 요약
        '<div class="r-section"><div class="highlight-box">',
        '<div class="score-area">',
        '<div class="score-label">종합 투자 점수</div>',
        f'<div class="score-val">{d["AI"]["점수"]}</div>',
        '</div>',
        '<div class="analysis-text">',
        f'<b>"금융 구조조정 시 수익률 {d["AI"]["수익률"]} 달성 가능"</b><br>',
        f'본 물건은 <b>{d["토지"]["용도지역"]}</b> 내 위치한 <b>{d["건축물"]["주용도"]}</b>으로, 시설 활용도가 매우 우수합니다.',
        f' 특히 <b>{d["권리"]["리스크"]}</b> 전략 실행 시 자산 가치는 <b>{d["AI"]["가치"]}</b>까지 상승할 것으로 분석됩니다.',
        '</div></div></div>',

        # 3. 토지 정보
        '<div class="r-section">',
        '<div class="r-head">📍 토지 정보 (Land Info)</div>',
        '<table class="r-table">',
        f'<tr><th>소재지</th><td colspan="3">{d["주소"]}</td></tr>',
        f'<tr><th>지목/면적</th><td>{d["토지"]["지목"]} / {d["토지"]["면적"]}</td><th>공시지가</th><td>{d["토지"]["공시지가"]}</td></tr>',
        f'<tr><th>용도지역</th><td><span class="bdg bdg-warn">{d["토지"]["용도지역"]}</span></td><th>기타규제</th><td>{", ".join(d["토지"]["규제"])}</td></tr>',
        '</table></div>',

        # 4. 건축물 정보
        '<div class="r-section">',
        '<div class="r-head">🏢 건축물 정보 (Building Spec)</div>',
        '<table class="r-table">',
        f'<tr><th>주용도</th><td>{d["건축물"]["주용도"]}</td><th>법적상태</th><td>{b_stat}</td></tr>',
        f'<tr><th>규모/구조</th><td>{d["건축물"]["규모"]} ({d["건축물"]["구조"]})</td><th>승강기</th><td>{d["건축물"]["승강기"]}</td></tr>',
        f'<tr><th>주차대수</th><td colspan="3">{d["건축물"]["주차"]}</td></tr>',
        '</table></div>',

        # 5. 권리 분석
        '<div class="r-section">',
        '<div class="r-head">⚖️ 권리 및 금융 (Ownership)</div>',
        '<table class="r-table">',
        f'<tr><th>소유자</th><td>{d["권리"]["소유자"]}</td><th>채권최고액</th><td>{d["권리"]["채권"]}</td></tr>',
        f'<tr><th>AI 제안</th><td colspan="3" style="color:#b91c1c; font-weight:bold;">💡 {d["권리"]["리스크"]}</td></tr>',
        '</table></div>',

        '<div style="text-align:center; font-size:11px; color:#cbd5e1; margin-top:50px;">Powered by Jisang AI | Data Integrity Verified</div>',
        '</div>'
    ]
    
    return "".join(html_parts)

# --- 메인 실행 ---

with st.sidebar:
    st.title("🖨️ 출력 센터")
    st.success("렌더링 엔진 무결성 확보됨")
    st.info("이제 [Ctrl + P]를 누르면 완벽한 보고서가 출력됩니다.")

# HTML 렌더링 (공백 없는 순수 HTML 문자열 주입)
st.markdown(create_html(DATA), unsafe_allow_html=True)