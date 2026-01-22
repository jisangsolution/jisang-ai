import streamlit as st
import requests
import pandas as pd
import json
import re
import time
from datetime import datetime

# 1. 페이지 설정 및 프리미엄 테마
st.set_page_config(page_title="지상 AI Pro v10.1", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .report-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ 지상 AI: 부동산 개발 통합 솔루션")
st.caption("Ver 10.1 - Premium Report & Map Integrated")

# 세션 상태 초기화
if 'results' not in st.session_state: st.session_state['results'] = None

# --- 비즈니스 로직 함수 ---

def get_coords(addr):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={addr}&format=json&limit=1"
        headers = {'User-Agent': 'JisangAI_v10.1'}
        res = requests.get(url, headers=headers, timeout=5).json()
        if res: return float(res[0]['lat']), float(res[0]['lon'])
    except: pass
    return 37.5665, 126.9780 # 기본값 서울

def render_stars(score):
    rating = score / 20
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    return "⭐" * full + "🌗" * half + "☆" * (5 - full - half)

def calculate_biz_metrics(area, budget, purpose):
    costs = {"요양원": 850, "전원주택": 750, "물류창고": 450, "상가": 650}
    unit = costs.get(purpose.split('/')[0], 700)
    total = (area * unit / 10000) * 1.25
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
    st.header("⚙️ 분석 모드")
    mode = st.radio("모드 선택", ["단일 상세 분석", "대량 Deal Sourcing"])
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
                        "예상비용": f"{m['total']}억", "ROI": f"{m['roi']}%", "lat": lat, "lon": lon, "용도": row['용도']
                    })
                    bar.progress((i+1)/len(st.session_state['df']))
                st.session_state['results'] = pd.DataFrame(processed).sort_values("투자점수", ascending=False)
                st.balloons()

# --- 메인 대시보드 ---

if st.session_state['results'] is not None:
    res = st.session_state['results']
    
    st.subheader("📊 Deal Sourcing 종합 분석 리포트")
    col_chart, col_top = st.columns([2, 1])
    
    with col_chart:
        # 가로형 차트로 주소지가 잘리지 않게 표시
        st.bar_chart(res.set_index('주소')['투자점수'], horizontal=True, color="#1e3a8a")
    
    with col_top:
        best = res.iloc[0]
        st.markdown(f"""
            <div class='report-card'>
                <p style='color:#64748b; font-size:0.9rem;'>🏆 최적 투자 추천</p>
                <h2 style='color:#1e3a8a; margin:0;'>{best['투자점수']}점</h2>
                <p style='font-size:1.5rem; margin:10px 0;'>{best['별점']}</p>
                <hr style='border:0.5px solid #e2e8f0;'>
                <p><b>위치:</b> {best['주소']}</p>
                <p><b>기대수익률:</b> <span style='color:#16a34a; font-weight:bold;'>{best['ROI']}</span></p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("🥇 상세 투자 분석 및 현장 확인")
    for i, row in res.iterrows():
        with st.expander(f"{row['별점']} [{row['투자점수']}점] {row['주소']} ({row['용도']})"):
            c1, c2 = st.columns([1, 1.2])
            with c1:
                st.info(f"💰 예상 소요 비용: {row['예상비용']} | ROI: {row['ROI']}")
                
                # 지도 연결 버튼
                st.write("🔗 **현장 지도 연동**")
                m1, m2 = st.columns(2)
                m1.link_button("🗺️ 네이버 지도", f"https://map.naver.com/v5/search/{row['주소']}")
                m2.link_button("🗺️ 카카오 맵", f"https://map.kakao.com/link/search/{row['주소']}")
                
                st.divider()
                # 프리미엄 보고서 다운로드
                report_md = f"# {row['주소']} 타당성 분석 보고서\n\n- 점수: {row['투자점수']}점\n- 별점: {row['별점']}\n- 예상비용: {row['예상비용']}\n- 기대수익률: {row['ROI']}"
                st.download_button(f"📥 상세 보고서(.md) 저장", report_md, f"Report_{i}.md", key=f"dl_{i}")

            with c2:
                # 실시간 좌표 반영 지도
                st.map(pd.DataFrame({'lat': [row['lat']], 'lon': [row['lon']]}), zoom=14)

    # 전체 데이터셋 다운로드
    st.divider()
    csv_data = res.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 전체 분석 데이터셋(Excel) 다운로드", csv_data, "Jisang_AI_Asset_Analysis.csv", "text/csv", type="primary")

else:
    st.info("👈 왼쪽에서 데이터를 로드하고 [초격차 분석 시작]을 눌러주세요.")