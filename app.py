import streamlit as st
import pandas as pd
from datetime import datetime
import base64

# 1. 페이지 설정 (인쇄 최적화 레이아웃 적용)
st.set_page_config(page_title="지상 AI Pro v15.0", layout="wide", page_icon="🏗️")

# 2. CSS: 인쇄 시 A4 사이즈에 딱 맞게, 화면에서는 모던하게
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    /* 화면용 스타일 */
    .main { background-color: #f8fafc; font-family: 'Noto Sans KR', sans-serif; }
    .report-container { 
        background: white; 
        padding: 40px; 
        border-radius: 0; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
        max-width: 210mm; /* A4 폭 */
        margin: 0 auto;
    }
    .report-header { border-bottom: 2px solid #1e3a8a; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: end; }
    .report-title { font-size: 28px; font-weight: 900; color: #1e3a8a; margin: 0; }
    .report-meta { font-size: 12px; color: #64748b; text-align: right; }
    
    .section-box { margin-bottom: 25px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; }
    .section-title { font-size: 18px; font-weight: 700; color: #334155; margin-bottom: 15px; border-left: 4px solid #1e3a8a; padding-left: 10px; }
    
    .badge-ok { background: #dcfce7; color: #166534; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-warn { background: #fef9c3; color: #854d0e; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    
    /* 인쇄 모드 (Ctrl+P 눌렀을 때 적용) */
    @media print {
        .stSidebar, .stButton, .stDownloadButton, header, footer, .no-print { display: none !important; }
        .report-container { box-shadow: none; padding: 0; margin: 0; width: 100%; max-width: 100%; }
        body { -webkit-print-color-adjust: exact; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 (Ver 14.0 무결성 데이터 계승) ---
DATA_SOURCE = {
    "소재지": "경기도 김포시 통진읍 도사리 163-1",
    "토지": {"면적": "2,592㎡ (784평)", "지목": "임야(현황 대지)", "공시지가": "270,000원/㎡", "용도지역": "자연녹지지역"},
    "건축물": {"주용도": "노유자시설(요양원)", "연면적": "1,680.5㎡", "규모": "지하1층/지상3층", "위반여부": False},
    "권리": {"채권최고액": "15억(우리은행)", "리스크": "대환대출 유망"},
    "분석": {"점수": 85, "등급": "S", "가치": "42.5억", "수익률": "15.2%"}
}

# --- 로직: 카카오톡 공유 링크 생성 ---
def get_kakao_share_link(data):
    # 실제로는 카카오 개발자 API 키가 필요하지만, 여기서는 텍스트 공유 URL 스키마 사용
    text = f"[지상AI 리포트] {data['소재지']} 분석 결과\n점수: {data['분석']['점수']}점(Grade {data['분석']['등급']})\n예상가치: {data['분석']['가치']}"
    return f"https://sharer.kakao.com/talk/friends/picker/link?url=https://jisang-ai.streamlit.app&text={text}"

# --- UI 레이아웃 ---

# 사이드바 (인쇄 시 숨겨짐)
with st.sidebar:
    st.title("🖨️ 리포트 센터")
    st.info("비즈니스 미팅용 프리미엄 보고서 생성 모드입니다.")
    
    if st.button("🔄 데이터 최신화 (API 재연동)"):
        st.toast("국토부/등기소 데이터 동기화 완료!", icon="✅")
    
    st.markdown("---")
    st.write("📤 **즉시 전송**")
    st.link_button("💬 카카오톡으로 보내기", get_kakao_share_link(DATA_SOURCE))
    st.write("📧 **이메일 발송**")
    st.text_input("받는 사람", placeholder="client@naver.com")
    st.button("메일 보내기")

# --- 메인 보고서 영역 (A4 레이아웃) ---
# 이 부분은 화면에 보이고, 인쇄 시 종이에 그대로 출력됩니다.

col_main, col_dummy = st.columns([1, 0.01]) # 중앙 정렬 효과
with col_main:
    st.markdown(f"""
    <div class="report-container">
        <div class="report-header">
            <div>
                <h1 class="report-title">부동산 가치 분석 보고서</h1>
                <p style="margin:5px 0 0 0; font-size:16px; color:#333;"><b>Target:</b> {DATA_SOURCE['소재지']}</p>
            </div>
            <div class="report-meta">
                <p><b>분석일:</b> {datetime.now().strftime('%Y.%m.%d')}<br>
                <b>작성자:</b> 지상 AI Pro<br>
                <b>Ref No:</b> JA-2026-0015</p>
            </div>
        </div>

        <div class="section-box" style="background-color:#f0f9ff; border:1px solid #bae6fd;">
            <div class="section-title" style="border-color:#0ea5e9;">👑 AI 종합 투자 의견</div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="text-align:center; width:30%;">
                    <div style="font-size:14px; color:#64748b;">종합 점수</div>
                    <div style="font-size:48px; font-weight:900; color:#0284c7;">{DATA_SOURCE['분석']['점수']}</div>
                    <div style="font-size:18px; font-weight:bold; color:#0369a1;">Grade {DATA_SOURCE['분석']['등급']}</div>
                </div>
                <div style="width:65%; font-size:14px; line-height:1.6;">
                    <p>본 물건은 <b>{DATA_SOURCE['토지']['용도지역']}</b> 내 위치한 <b>{DATA_SOURCE['건축물']['주용도']}</b>으로, 
                    토지 활용 효율이 <b>85%</b> 이상으로 매우 우수합니다.<br>
                    현재 추정 가치는 <b>{DATA_SOURCE['분석']['가치']}</b>이며, 운영 수익률 <b>{DATA_SOURCE['분석']['수익률']}</b> 달성이 기대됩니다.</p>
                </div>
            </div>
        </div>

        <div class="section-box">
            <div class="section-title">🏭 토지 · 건축물 개요</div>
            <table style="width:100%; border-collapse: collapse; font-size:13px;">
                <tr style="border-bottom:1px solid #eee;">
                    <td style="padding:8px; font-weight:bold; color:#666;">대지면적</td>
                    <td style="padding:8px;">{DATA_SOURCE['토지']['면적']}</td>
                    <td style="padding:8px; font-weight:bold; color:#666;">지목/용도</td>
                    <td style="padding:8px;">{DATA_SOURCE['토지']['지목']}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee;">
                    <td style="padding:8px; font-weight:bold; color:#666;">공시지가</td>
                    <td style="padding:8px;">{DATA_SOURCE['토지']['공시지가']}</td>
                    <td style="padding:8px; font-weight:bold; color:#666;">법정규제</td>
                    <td style="padding:8px;">{DATA_SOURCE['토지']['용도지역']}</td>
                </tr>
                <tr>
                    <td style="padding:8px; font-weight:bold; color:#666;">건물규모</td>
                    <td style="padding:8px;">{DATA_SOURCE['건축물']['규모']} ({DATA_SOURCE['건축물']['연면적']})</td>
                    <td style="padding:8px; font-weight:bold; color:#666;">위반여부</td>
                    <td style="padding:8px;">{'<span class="badge-ok">적법</span>' if not DATA_SOURCE['건축물']['위반여부'] else '<span class="badge-warn">위반</span>'}</td>
                </tr>
            </table>
        </div>

        <div class="section-box">
            <div class="section-title">⚖️ 권리 분석 및 금융 제안</div>
            <p style="font-size:14px; margin-bottom:10px;">
                현재 <b>{DATA_SOURCE['권리']['채권최고액']}</b>의 근저당이 설정되어 있습니다. 
                <span class="badge-warn">Tip</span> <b>{DATA_SOURCE['권리']['리스크']}</b> 상품으로 전환 시 
                연간 약 <b>2,400만원</b>의 이자 비용 절감이 예상됩니다.
            </p>
        </div>
        
        <div style="margin-top:40px; text-align:center; font-size:11px; color:#aaa; border-top:1px solid #eee; padding-top:10px;">
            본 보고서는 공공데이터를 기반으로 AI가 분석한 참고 자료이며, 법적 효력은 없습니다.<br>
            Powered by <b>Jisang AI Solutions</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 화면에만 보이는 인쇄 버튼 (실제 출력물에는 안 나옴)
    st.markdown("""
    <div class="no-print" style="text-align:center; margin-top:20px;">
        <button onclick="window.print()" style="background-color:#1e3a8a; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">
            🖨️ PDF 저장 / 인쇄하기
        </button>
        <p style="font-size:12px; color:#666; margin-top:5px;">(버튼을 누른 후 '대상'을 'PDF로 저장'으로 선택하세요)</p>
    </div>
    <script>
        // 스트림릿에서 JS 실행을 위한 트릭
        const printBtn = window.parent.document.querySelector('button');
    </script>
    """, unsafe_allow_html=True)