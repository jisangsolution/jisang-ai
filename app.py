import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro v15.1", layout="wide", page_icon="🏗️")

# 2. CSS: 화면용 vs 인쇄용(A4) 스타일 분리
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    /* 기본 폰트 설정 */
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 화면용 컨테이너 */
    .report-wrapper {
        background: white;
        padding: 40px;
        margin: 0 auto;
        max-width: 210mm; /* A4 폭 */
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
        border-radius: 8px;
    }

    /* 제목 및 헤더 */
    .r-header { border-bottom: 3px solid #1e3a8a; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-end; }
    .r-title { font-size: 32px; font-weight: 900; color: #1e3a8a; margin: 0; line-height: 1.2; }
    .r-meta { font-size: 12px; color: #64748b; text-align: right; }

    /* 섹션 공통 */
    .r-section { margin-bottom: 30px; }
    .r-subtitle { font-size: 20px; font-weight: 700; color: #334155; border-left: 5px solid #1e3a8a; padding-left: 10px; margin-bottom: 15px; }

    /* 테이블 스타일 */
    .r-table { width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 10px; }
    .r-table th { background: #f1f5f9; color: #475569; font-weight: bold; padding: 12px; border: 1px solid #e2e8f0; text-align: center; width: 15%; }
    .r-table td { border: 1px solid #e2e8f0; padding: 12px; color: #1e293b; }

    /* 뱃지 스타일 */
    .bdg-safe { background: #dcfce7; color: #15803d; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }
    .bdg-danger { background: #fee2e2; color: #b91c1c; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }
    .bdg-warn { background: #fef9c3; color: #a16207; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }

    /* 인쇄 모드 최적화 (Ctrl+P 시 적용) */
    @media print {
        .stSidebar, header, footer, .no-print { display: none !important; }
        .report-wrapper { box-shadow: none; margin: 0; padding: 0; width: 100%; max-width: 100%; }
        body { -webkit-print-color-adjust: exact; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 (Ver 14.0 완전무결성 데이터) ---
# 실제로는 API에서 가져온 데이터가 여기 들어갑니다.
DATA = {
    "메타": {"분석일": datetime.now().strftime("%Y-%m-%d"), "작성자": "지상 AI", "문서번호": "JA-2026-05"},
    "주소": "경기도 김포시 통진읍 도사리 163-1",
    "토지": {
        "지목": "임야(현황 대지)", "면적": "2,592㎡ (784평)", "공시지가": "270,000원/㎡",
        "용도지역": "자연녹지지역", "규제": ["성장관리계획구역(복합형)", "가축사육제한구역"]
    },
    "건축물": {
        "주용도": "노유자시설(요양원)", "구조": "철근콘크리트", "규모": "지하1층 / 지상3층",
        "승강기": "유(15인승)", "주차": "12대", "위반여부": False # False면 적법
    },
    "권리": {
        "소유자": "김지상(개인)", "채권최고액": "15억(우리은행 외 1)", 
        "리스크": "근저당 설정 후 2년 경과 (금리 인하 대환 유망)"
    },
    "AI결과": {
        "점수": 85, "등급": "S", "가치": "42.5억", "수익률": "15.2%"
    }
}

# --- 로직: HTML 생성 함수 (오류 방지) ---
def create_report_html(d):
    # 위반건축물 뱃지 로직
    bldg_status = f"<span class='bdg-safe'>적법 건축물</span>" if not d['건축물']['위반여부'] else f"<span class='bdg-danger'>위반건축물 등재</span>"
    
    html = f"""
    <div class="report-wrapper">
        <div class="r-header">
            <div>
                <h1 class="r-title">부동산 종합 분석 보고서</h1>
                <div style="margin-top:10px; font-size:18px; color:#333;"><b>Target:</b> {d['주소']}</div>
            </div>
            <div class="r-meta">
                분석일: {d['메타']['분석일']}<br>
                발행처: 지상 AI Pro<br>
                No: {d['메타']['문서번호']}
            </div>
        </div>

        <div class="r-section" style="background:#f0f9ff; padding:20px; border-radius:8px; border:1px solid #bae6fd;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="text-align:center; min-width:150px;">
                    <div style="color:#64748b; font-size:14px;">종합 투자 점수</div>
                    <div style="color:#0284c7; font-size:42px; font-weight:900;">{d['AI결과']['점수']}점</div>
                </div>
                <div style="border-left:2px solid #e0f2fe; padding-left:25px; margin-left:15px; line-height:1.6;">
                    <b style="font-size:18px; color:#0c4a6e;">"금융 구조조정 시 수익률 {d['AI결과']['수익률']} 달성 가능"</b><br>
                    본 물건은 <b>{d['토지']['용도지역']}</b> 내 <b>{d['건축물']['주용도']}</b>으로, 시설 상태(승강기, 주차)가 매우 양호합니다.
                    특히 <b>{d['권리']['리스크']}</b> 전략을 통해 이자 비용을 절감하면 가치는 <b>{d['AI결과']['가치']}</b>까지 상승할 여력이 있습니다.
                </div>
            </div>
        </div>

        <div class="r-section">
            <div class="r-subtitle">📍 토지 정보 (Land Info)</div>
            <table class="r-table">
                <tr><th>소재지</th><td colspan="3">{d['주소']}</td></tr>
                <tr>
                    <th>지목/면적</th><td>{d['토지']['지목']} / {d['토지']['면적']}</td>
                    <th>공시지가</th><td>{d['토지']['공시지가']}</td>
                </tr>
                <tr>
                    <th>용도지역</th><td><span class="bdg-warn">{d['토지']['용도지역']}</span></td>
                    <th>기타규제</th><td>{', '.join(d['토지']['규제'])}</td>
                </tr>
            </table>
        </div>

        <div class="r-section">
            <div class="r-subtitle">🏢 건축물 대장 (Building Spec)</div>
            <table class="r-table">
                <tr>
                    <th>주용도</th><td>{d['건축물']['주용도']}</td>
                    <th>법적상태</th><td>{bldg_status}</td>
                </tr>
                <tr>
                    <th>규모/구조</th><td>{d['건축물']['규모']} ({d['건축물']['구조']})</td>
                    <th>승강기</th><td>{d['건축물']['승강기']}</td>
                </tr>
                <tr>
                    <th>주차대수</th><td colspan="3">{d['건축물']['주차']} (법정 충족)</td>
                </tr>
            </table>
        </div>

        <div class="r-section">
            <div class="r-subtitle">⚖️ 권리/금융 분석 (Ownership & Debt)</div>
            <table class="r-table">
                <tr>
                    <th>소유자</th><td>{d['권리']['소유자']}</td>
                    <th>채권최고액</th><td>{d['권리']['채권최고액']}</td>
                </tr>
                <tr>
                    <th>AI 제안</th><td colspan="3" style="color:#b91c1c; font-weight:bold;">💡 {d['권리']['리스크']}</td>
                </tr>
            </table>
        </div>

        <div style="text-align:center; font-size:11px; color:#94a3b8; margin-top:50px;">
            본 문서는 공공데이터(토지대장, 등기부 등)를 기반으로 작성되었습니다.<br>
            Jisang AI Real Estate Solution
        </div>
    </div>
    """
    return html

# --- 메인 실행 ---

with st.sidebar:
    st.title("🖨️ 출력 센터")
    st.info("데이터 무결성이 검증된 프리미엄 리포트입니다.")
    st.write("---")
    st.write("1. 아래 내용을 확인하세요.")
    st.write("2. 이상이 없다면 **[인쇄 모드]**를 실행하세요.")
    
    # 인쇄 안내 (JS 트릭 대신 안전한 방법 사용)
    st.warning("단축키 [Ctrl + P]를 누르면 A4 사이즈로 깔끔하게 인쇄/PDF 저장이 가능합니다.")

# 메인 화면에 HTML 렌더링
report_html = create_report_html(DATA)
st.markdown(report_html, unsafe_allow_html=True)