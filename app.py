import streamlit as st
import requests
import pandas as pd
import json
import re
import time
from datetime import datetime

# 1. 페이지 설정 및 프리미엄 테마 적용
st.set_page_config(page_title="지상 AI Pro v10", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .report-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .star-active { color: #facc15; font-size: 1.4rem; }
    .star-inactive { color: #d1d5db; font-size: 1.4rem; }
    .kpi-title { font-size: 0.9rem; color: #6b7280; margin-bottom: 5px; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ 지상 AI: 부동산 개발 통합 솔루션")
st.caption("Ver 10.0 - Premium Analytics & Global Geocoding")

# 세션 상태 초기화
if 'results' not in st.session_state: st.session_state['results'] = None

# --- 핵심 비즈니스 로직 ---

# 실시간 주소 좌표 변환 (Geocoding)
def get_coords(addr):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={addr}&format=json&limit=1"
        headers = {'User-Agent': 'JisangAI_v10'}
        res = requests.get(url, headers=headers, timeout=5).json()
        if res: return float(res[0]['lat']), float(res[0]['lon'])
    except: pass
    return 37.5665, 126.9780 # 실패 시 서울시청

# 정밀 별점 생성 (90점 = 4.5개)
def render_stars(score):
    rating = score / 20
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    return "⭐" * full + "🌗" * half + "☆" * (5 - full - half)

def calculate_biz_metrics(area, budget, purpose):
    costs = {"요양원": 850, "전원주택": 750, "물류창고": 450, "상가": 650}
    unit = costs.get(purpose.split('/')[0], 700)
    total = (area * unit / 10000) * 1.25 # 예비비 포함
    balance = budget - total
    roi = 15.2 if balance >= 0 else 4.8
    return {"total": round(total, 2), "balance": round(balance, 2), "roi": roi, "unit": unit}

def call_expert_ai(msg, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={key}"
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": msg}]}]}, timeout=10)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: return None

# --- UI 레이아웃 ---

with st.sidebar:
    st.header("⚙️ 분석 마스터")
    mode = st.radio("분석 모드", ["단일 상세 분석", "대량 Deal Sourcing"])
    key = st.secrets.get("GOOGLE_API_KEY", "").strip()

    if mode == "대량 Deal Sourcing":
        if st.button("📈 투자 후보지 샘플 로드"):
            st.session_state['df'] = pd.DataFrame({
                '주소': ['경기도 김포시 통진읍 도사리 163-1', '경기도 파주시 탄현면 성동리 100', '인천시 강화군 화도면 상방리 55'],
                '용도': ['요양원', '전원주택', '물류창고'], '면적': [100, 150, 300], '예산': [15, 12, 18]
            })
        
        if 'df' in st.session_state:
            st.dataframe(st.session_state['df'], use_container_width=True)
            if st.button("🔥 초격차 분석 시작", type="primary"):
                processed = []
                bar = st.progress(0)
                for i, row in st.session_state['df'].iterrows():
                    with st.status(f"분석 중: {row['주소']}") as s:
                        m = calculate_biz_metrics(row['면적'], row['예산'], row['용도'])
                        prompt = f"{row['주소']} {row['용도']} 분석. 점수(0-100)만 '점수:XX'로 답해."
                        res = call_expert_ai(prompt, key)
                        score = int(re.findall(r"\d+", res)[0]) if res else (70 if m['balance'] >= 0 else 45)
                        lat, lon = get_coords(row['주소'])
                        s.update(label=f"완료: {row['주소']}", state="complete")
                    
                    processed.append({
                        "주소": row['주소'], "투자점수": score, "별점": render_stars(score),
                        "예상비용": f"{m['total']}억", "ROI": f"{m['roi']}%", "lat": lat, "lon": lon
                    })
                    bar.progress((i+1)/len(st.session_state['df']))
                st.session_state['results'] = pd.DataFrame(processed).sort_values("투자점수", ascending=False)
                st.balloons()

# --- 메인 대시보드 ---

if st.session_state['results'] is not None:
    res = st.session_state['results']
    
    # 1. 최상단 요약 대시보드
    st.subheader("📊 부동산 자산 가치 비교 분석")
    col_chart, col_top = st.columns([2, 1])
    
    with col_chart:
        st.bar_chart(res.set_index('주소')['투자점수'], horizontal=True, color="#1e3a8a")
    
    with col_top:
        best = res.iloc[0]
        st.markdown(f"""
            <div class='report-card'>
                <p class='kpi-title'>🏆 최적 투자 추천지</p>
                <p class='kpi-value'>{best['투자점수']}점</p>
                <p style='font-size:1.2rem;'>{best['별점']}</p>
                <hr>
                <p><b>위치:</b> {best['주소']}</p>
                <p><b>기대수익률:</b> <span style='color:green;'>{best['ROI']}</span></p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 2. 개별 부지 상세 분석 (지도 및 외부연동)
    st.subheader("🥇 상세 투자 분석 및 현장 확인")
    for i, row in res.iterrows():
        with st.expander(f"{row['별점']} [{row['투자점수']}점] {row['주소']}"):
            c1, c2 = st.columns([1, 1.2])
            with c1:
                st.markdown(f"""
                    <div style='padding:10px; background:#f8fafc; border-radius:10px;'>
                        <p><b>💰 예상 투입 자금:</b> {row['예상비용']}</p>
                        <p><b>📈 사업 수익성(ROI):</b> {row['ROI']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.divider()
                st.write("🔗 **외부 공공 데이터/지도 연동**")
                m1, m2 = st.columns(2)
                m1.link_button("🗺️ 네이버 지도 (로드뷰)", f"https://map.naver.com/v5/search/{row['주소']}")
                m2.link_button("🗺️ 카카오 맵 (지적도)", f"https://map.kakao.com/link/search/{row['주소']}")
                
                # 프리미엄 보고서 낱개 다운로드
                report_md = f"# {row['주소']} 타당성 리포트\n\n- 점수: {row['투자점수']}\n- 등급: {row['별점']}\n- 비용: {row['예상비용']}"
                st.download_button("📥 상세 보고서 다운로드 (MD)", report_md, f"Report_{i}.md", key=f"btn_{i}")

            with c2:
                # 실시간 좌표 반영된 지도
                st.map(pd.DataFrame({'lat': [row['lat']], 'lon': [row['lon']]}), zoom=14)

    # 3. 통합 엑셀 다운로드
    st.divider()
    csv_data = res.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 전체 분석 데이터셋(Excel) 저장", csv_data, "Jisang_AI_Asset_Management.csv", "text/csv", type="primary")

else:
    st.info("👈 왼쪽 사이드바에서 분석 대상을 선택하고 [분석 시작]을 눌러주세요.")