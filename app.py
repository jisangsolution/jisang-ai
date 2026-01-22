import streamlit as st
import pandas as pd
import time
import textwrap
import urllib.parse
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro v17.0", layout="wide", page_icon="🏗️")

# 2. 통합 CSS (채팅창 + 리포트 + 뱃지)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 챗봇 스타일 */
    .chat-row { padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    .chat-user { background: #e0f2fe; text-align: right; margin-left: 20%; }
    .chat-ai { background: #f1f5f9; text-align: left; margin-right: 20%; }
    
    /* 리포트 스타일 (Ver 15.3 계승) */
    .report-wrapper { background: white; padding: 40px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .r-header { border-bottom: 2px solid #1e3a8a; padding-bottom: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; }
    .r-title { font-size: 28px; font-weight: 900; color: #1e3a8a; margin: 0; }
    .r-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .r-table th { background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px; font-weight: 700; text-align: center; width: 18%; }
    .r-table td { border: 1px solid #e2e8f0; padding: 8px; color: #333; }
    
    /* 뱃지 */
    .bdg { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 700; }
    .bdg-ok { background: #dcfce7; color: #15803d; }
    .bdg-no { background: #fee2e2; color: #b91c1c; }
    
    @media print {
        .stSidebar, .stButton, .stChatInput, header, footer, .no-print, .stTabs { display: none !important; }
        .report-wrapper { border: none; padding: 0; margin: 0; width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ 지상 AI: 초격차 부동산 통합 솔루션")
st.caption("Ver 17.0 - Map, Kakao, Chatbot & Report Total Package")

# 세션 초기화
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []
if 'final_results' not in st.session_state: st.session_state['final_results'] = None

# --- [Core] 데이터 엔진 (Mock API) ---
INTEGRITY_DB = {
    "도사리 163-1": {
        "토지": {"면적": "2,592㎡", "지목": "임야(현황 대지)", "공시지가": "270,000원", "용도지역": "자연녹지지역", "규제": ["성장관리계획구역"]},
        "건축물": {"주용도": "노유자시설", "규모": "지하1/지상3", "승강기": "유", "위반여부": False},
        "권리": {"소유자": "김지상", "채권": "15억(우리은행)", "리스크": "대환대출 유망"},
        "좌표": [37.689, 126.589]
    },
    "성동리 100": {
        "토지": {"면적": "495㎡", "지목": "대", "공시지가": "890,000원", "용도지역": "계획관리지역", "규제": ["역사문화보존지역"]},
        "건축물": {"주용도": "단독주택", "규모": "지상2층", "승강기": "무", "위반여부": True},
        "권리": {"소유자": "박건축", "채권": "없음", "리스크": "권리관계 깨끗함"},
        "좌표": [37.785, 126.695]
    },
    "상방리 55": {
        "토지": {"면적": "990㎡", "지목": "잡종지", "공시지가": "150,000원", "용도지역": "보전관리지역", "규제": ["접도구역"]},
        "건축물": {"주용도": "창고시설", "규모": "지상1층", "승강기": "무", "위반여부": False},
        "권리": {"소유자": "이물류", "채권": "5억(새마을금고)", "리스크": "2금융권 고금리"},
        "좌표": [37.605, 126.450]
    }
}

# --- 로직 함수 ---

def analyze_batch_item(row):
    addr_key = next((k for k in INTEGRITY_DB if k in row['주소']), None)
    data = INTEGRITY_DB.get(addr_key, {
        "토지": {"면적": "-", "용도지역": "확인불가", "규제": []},
        "건축물": {"주용도": "-", "위반여부": False},
        "권리": {"채권": "-", "리스크": "정보 없음"},
        "좌표": [37.5665, 126.9780]
    })
    
    budget = row['예산']
    total_cost = (row['면적'] * 800 / 10000) * 1.2
    balance = budget - total_cost
    roi = 15.2 if balance >= 0 else 3.5
    score = 80 - (30 if data['건축물']['위반여부'] else 0) + (10 if balance >= 0 else -10)
    
    return {"주소": row['주소'], "용도": row['용도'], "점수": score, "ROI": roi, "비용": round(total_cost, 2), "데이터": data}

def create_report_html(item):
    d = item['데이터']
    b_stat = "<span class='bdg bdg-ok'>적법</span>" if not d['건축물']['위반여부'] else "<span class='bdg bdg-no'>위반건축물</span>"
    parts = [
        '<div class="report-wrapper">',
        '<div class="r-header">',
        f'<div><div class="r-title">부동산 가치 분석 보고서</div><div>Target: {item["주소"]}</div></div>',
        f'<div style="text-align:right; font-size:11px;">DATE: {datetime.now().strftime("%Y-%m-%d")}<br>REF: JA-BIZ-{int(time.time())}</div>',
        '</div>',
        f'<div style="background:#f1f5f9; padding:15px; border-radius:8px; margin-bottom:20px;">',
        f'<div style="font-size:36px; font-weight:900; color:#1e3a8a;">{item["점수"]}점 <span style="font-size:16px;">(ROI {item["ROI"]}%)</span></div>',
        f'<div style="margin-top:5px; font-size:13px;">💡 <b>AI 제안:</b> {d["권리"]["리스크"]}</div></div>',
        '<table class="r-table">',
        f'<tr><th>면적/지목</th><td>{d["토지"]["면적"]} / {d["토지"]["지목"]}</td><th>공시지가</th><td>{d["토지"]["공시지가"]}</td></tr>',
        f'<tr><th>용도지역</th><td>{d["토지"]["용도지역"]}</td><th>규제사항</th><td>{", ".join(d["토지"]["규제"])}</td></tr>',
        f'<tr><th>건물용도</th><td>{d["건축물"]["주용도"]}</td><th>위반여부</th><td>{b_stat}</td></tr>',
        f'<tr><th>소유자</th><td>{d["권리"]["소유자"]}</td><th>채권최고액</th><td>{d["권리"]["채권"]}</td></tr>',
        '</table></div>'
    ]
    return "".join(parts)

# [카카오톡 공유 링크 생성]
def get_kakao_link(item):
    text = f"[지상AI] {item['주소']} 분석 결과\n점수: {item['점수']}점\nROI: {item['ROI']}%\n리스크: {item['데이터']['권리']['리스크']}"
    encoded_text = urllib.parse.quote(text)
    return f"https://sharer.kakao.com/talk/friends/picker/link?url=https://jisang-ai.streamlit.app&text={encoded_text}"

# --- UI 레이아웃 ---

with st.sidebar:
    st.header("🏢 분석 센터")
    if st.button("📂 투자 후보지 샘플 로드"):
        st.session_state['input_df'] = pd.DataFrame({
            '주소': ['김포시 통진읍 도사리 163-1', '파주시 탄현면 성동리 100', '강화군 화도면 상방리 55'],
            '용도': ['요양원', '전원주택', '물류창고'], '면적': [100, 150, 300], '예산': [15, 12, 18]
        })
    
    if 'input_df' in st.session_state:
        if st.button("🚀 초격차 원클릭 분석", type="primary"):
            results = []
            bar = st.progress(0)
            for i, row in st.session_state['input_df'].iterrows():
                res = analyze_batch_item(row)
                time.sleep(0.3)
                results.append(res)
                bar.progress((i+1)/len(st.session_state['input_df']))
            st.session_state['final_results'] = pd.DataFrame(results).sort_values("점수", ascending=False)
            st.success("분석 완료!")

# --- 메인 화면 (탭 구성) ---

if st.session_state['final_results'] is not None:
    df = st.session_state['final_results']
    
    # 탭으로 기능 분리 (UX 최적화)
    tab1, tab2, tab3 = st.tabs(["📊 분석 대시보드", "🤖 AI 부동산 상담", "🖨️ 리포트 다운로드"])
    
    # [Tab 1] 분석 결과 & 지도 & 카카오톡
    with tab1:
        st.subheader("🥇 Deal Sourcing 랭킹")
        st.bar_chart(df.set_index('주소')['점수'], horizontal=True, color='#1e3a8a')
        
        for i, row in df.iterrows():
            d = row['데이터']
            with st.expander(f"[{row['점수']}점] {row['주소']} - {d['토지']['용도지역']}"):
                c1, c2 = st.columns([1.5, 1])
                with c1:
                    st.info(f"💰 예상비용: {row['비용']}억 | ROI: {row['ROI']}%")
                    if d['건축물']['위반여부']: st.error("🚨 위반건축물 (주의)")
                    
                    st.write("---")
                    # [카카오톡 & 지도 연동]
                    k_col, n_col, daum_col = st.columns(3)
                    k_col.link_button("💬 카톡 공유", get_kakao_link(row))
                    
                    # 한글 주소 인코딩
                    enc_addr = urllib.parse.quote(row['주소'])
                    n_col.link_button("📍 네이버 지도", f"https://map.naver.com/v5/search/{enc_addr}")
                    daum_col.link_button("📍 카카오 맵", f"https://map.kakao.com/link/search/{enc_addr}")

                with c2:
                    st.map(pd.DataFrame({'lat': [d['좌표'][0]], 'lon': [d['좌표'][1]]}), zoom=14)

    # [Tab 2] AI 부동산 상담봇 (Consultant)
    with tab2:
        st.subheader("🤖 지상 AI 부동산 파트너")
        st.info("분석된 토지에 대해 무엇이든 물어보세요. (예: 도사리 땅에 카페 해도 돼?)")
        
        # 채팅 기록 표시
        for msg in st.session_state['chat_history']:
            role_class = "chat-user" if msg["role"] == "user" else "chat-ai"
            st.markdown(f"<div class='chat-row {role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

        # 채팅 입력
        if prompt := st.chat_input("질문을 입력하세요..."):
            st.session_state['chat_history'].append({"role": "user", "content": prompt})
            st.markdown(f"<div class='chat-row chat-user'>{prompt}</div>", unsafe_allow_html=True)
            
            # AI 답변 시뮬레이션 (분석 데이터 기반)
            top_pick = df.iloc[0]
            answer = f"네, 분석된 **{top_pick['주소']}** ({top_pick['데이터']['토지']['용도지역']})를 기준으로 답변드립니다. 해당 지역은 {top_pick['데이터']['권리']['리스크']} 상황이므로, 대환 대출을 먼저 해결하시면 개발 수익성이 {top_pick['ROI']}%까지 개선될 수 있습니다."
            
            time.sleep(1)
            st.session_state['chat_history'].append({"role": "assistant", "content": answer})
            st.rerun()

    # [Tab 3] 리포트 다운로드 (A4 인쇄)
    with tab3:
        st.subheader("🖨️ 보고서 출력 센터")
        st.warning("아래 버튼을 누르면 인쇄용 뷰가 펼쳐집니다. [Ctrl + P]로 PDF 저장하세요.")
        
        if st.checkbox("📄 전체 리포트 뷰어 열기"):
            full_html = ""
            for i, row in df.iterrows():
                full_html += create_report_html(row)
            st.markdown(full_html, unsafe_allow_html=True)

else:
    st.info("👈 사이드바에서 [엑셀 로드] 후 분석을 시작하세요.")