import streamlit as st
import requests
import pandas as pd
import json
import re
import time
from datetime import datetime

# 1. 페이지 설정 (최신 앱 스타일)
st.set_page_config(page_title="지상 AI Pro", layout="wide", page_icon="🏢")

# 커스텀 CSS로 디자인 세련되게 다듬기
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    .star-rating { color: #facc15; font-size: 1.2rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ 지상 AI: 부동산 개발 타당성 분석")
st.caption("Ver 9.9 - Premium UX & Horizontal Analytics")

# 세션 초기화
if 'bulk_results' not in st.session_state: st.session_state['bulk_results'] = None

# --- 핵심 로직 함수 ---

def calculate_metrics(area, budget, purpose):
    cost_map = {"요양원": 850, "전원주택": 750, "물류창고": 450, "상가": 600}
    unit_cost = cost_map.get(purpose.split('/')[0], 700) 
    total_cost = (area * unit_cost / 10000) * 1.2 
    roi = 12.5 if budget >= total_cost else 5.2
    return {"total_cost": round(total_cost, 2), "roi": roi, "balance": round(budget - total_cost, 2)}

def get_star_ui(score):
    # 0.5단위 별점 로직 최적화
    rating = score / 20
    full = int(rating)
    half = "🌗" if (rating - full) >= 0.5 else ""
    empty = "☆" * (5 - full - (1 if half else 0))
    return f"{'⭐' * full}{half}{empty}"

def call_ai(msg, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={key}"
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": msg}]}]}, timeout=10)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: return None

# --- 사이드바 및 분석 엔진 ---

with st.sidebar:
    st.header("⚙️ 분석 설정")
    mode = st.radio("모드 선택", ["단일 분석", "대량 분석"])
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()

    if mode == "대량 분석":
        if st.button("샘플 데이터 로드"):
            st.session_state['df'] = pd.DataFrame({
                '주소': ['경기도 김포시 통진읍 도사리 163-1', '경기도 파주시 탄현면 성동리 100', '인천시 강화군 화도면 상방리 55'],
                '용도': ['요양원', '전원주택', '물류창고'], '면적': [100, 150, 300], '예산': [5, 10, 20]
            })
        
        if 'df' in st.session_state:
            st.dataframe(st.session_state['df'], use_container_width=True)
            if st.button("🚀 초격차 일괄 분석 실행", type="primary"):
                results = []
                bar = st.progress(0)
                for idx, row in st.session_state['df'].iterrows():
                    with st.status(f"🔍 {row['주소']} 분석 중...") as s:
                        m = calculate_metrics(row['면적'], row['예산'], row['용도'])
                        prompt = f"주소:{row['주소']}, 비용:{m['total_cost']}억. 투자점수(0-100)만 '점수:XX'로 답해."
                        ai_res = call_ai(prompt, api_key)
                        score = int(re.findall(r"\d+", ai_res)[0]) if ai_res else (60 if m['balance'] >= 0 else 40)
                        s.update(label=f"✅ {row['주소']} 완료", state="complete")
                    
                    results.append({
                        "주소": row['주소'], "투자점수": score, "별점": get_star_ui(score),
                        "예상비용": f"{m['total_cost']}억", "수익률": f"{m['roi']}%"
                    })
                    bar.progress((idx+1)/len(st.session_state['df']))
                st.session_state['bulk_results'] = pd.DataFrame(results).sort_values("투자점수", ascending=False)
                st.balloons()

# --- 메인 대시보드 (가로형 차트 적용) ---

if mode == "대량 분석" and st.session_state['bulk_results'] is not None:
    res = st.session_state['bulk_results']
    
    st.subheader("📊 Deal Sourcing 비교 대시보드")
    
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.write("📍 **후보지별 투자 점수 (가로형 차트로 가독성 개선)**")
        # 가로형 막대 차트로 주소지가 잘리지 않게 표시
        st.bar_chart(res.set_index('주소')['투자점수'], horizontal=True, color="#1E3A8A")
    
    with c2:
        top = res.iloc[0]
        st.metric("🏆 최적 투자처", f"{top['투자점수']}점", top['별점'])
        st.success(f"**추천:** {top['주소']}\n\n예상 수익률 {top['수익률']}로 분석되었습니다.")

    st.divider()

    st.subheader("🥇 상세 분석 랭킹 및 지도 확인")
    for i, row in res.iterrows():
        with st.expander(f"{row['별점']} [{row['투자점수']}점] {row['주소']}"):
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.write(f"**💰 예상 소요 비용:** {row['예상비용']}")
                st.write(f"**📈 예상 수익률:** {row['수익률']}")
                st.divider()
                st.link_button("🗺️ 네이버 지도 확인", f"https://map.naver.com/v5/search/{row['주소']}")
                st.link_button("🗺️ 카카오 맵 확인", f"https://map.kakao.com/link/search/{row['주소']}")
            with col_b:
                # 위도/경도 기본 좌표 (샘플)
                lat, lon = (37.689, 126.589) if "김포" in row['주소'] else (37.75, 126.68)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=13)

    csv = res.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 분석 결과 엑셀 다운로드", csv, "Jisang_AI_Final.csv", "text/csv", type="primary")

else:
    st.info("👈 왼쪽에서 분석할 리스트를 로드하고 [초격차 일괄 분석]을 눌러주세요.")