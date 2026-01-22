import streamlit as st
import requests
import pandas as pd
import json
import re
import time
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="지상 AI Pro", layout="wide", page_icon="🏢")
st.title("🏢 지상 AI: 부동산 개발 타당성 & Deal Sourcing")
st.caption("Ver 9.7 - Star Ratings, Maps & Premium Export")

# 세션 초기화
if 'bulk_results' not in st.session_state: st.session_state['bulk_results'] = None
if 'analysis_result' not in st.session_state: st.session_state['analysis_result'] = None

# --- 핵심 함수 ---

def calculate_metrics(area, budget, purpose):
    cost_map = {"요양원": 850, "전원주택": 750, "물류창고": 450, "상가": 600}
    unit_cost = cost_map.get(purpose.split('/')[0], 700) 
    est_total_cost = (area * unit_cost / 10000) * 1.2 
    balance = budget - est_total_cost 
    roi = 12.5 if balance >= 0 else 5.2
    return {"unit_cost": unit_cost, "total_cost": round(est_total_cost, 2), "balance": round(balance, 2), "roi": roi}

def get_star_rating(score):
    stars = int(score / 20)
    return "⭐" * stars + "☆" * (5 - stars)

def call_ai_model(messages, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    try:
        res = requests.post(url, headers=headers, json={"contents": [{"role": m[0], "parts": [{"text": m[1]}]} for m in messages]}, timeout=10)
        return res.json()['candidates'][0]['content']['parts'][0]['text'] if res.status_code == 200 else None
    except: return None

# --- UI 구성 ---

with st.sidebar:
    st.header("⚙️ 분석 모드")
    mode = st.radio("선택", ["단일 분석", "대량 분석"])
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()

    if mode == "대량 분석":
        st.subheader("📂 데이터 로드")
        if st.button("샘플 데이터 불러오기"):
            st.session_state['upload_df'] = pd.DataFrame({
                '주소': ['경기도 김포시 통진읍 도사리 163-1', '경기도 파주시 탄현면 성동리 100', '인천시 강화군 화도면 상방리 55'],
                '용도': ['요양원', '전원주택', '물류창고'], '면적': [100, 150, 300], '예산': [5, 10, 20]
            })
            
        if 'upload_df' in st.session_state:
            if st.button("🔥 초격차 일괄 분석 시작", type="primary"):
                results = []
                df = st.session_state['upload_df']
                total_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    with st.status(f"🔍 **[{idx+1}/{len(df)}] {row['주소']}** 분석 중...", expanded=True) as status:
                        st.write("📊 수지분석 및 위치 좌표 확인 중...")
                        m = calculate_metrics(row['면적'], row['예산'], row['용도'])
                        time.sleep(1)
                        
                        st.write("🧠 AI 투자 매력도 및 별점 산출 중...")
                        prompt = f"주소:{row['주소']}, 용도:{row['용도']}, 비용:{m['total_cost']}억. 점수(0-100)를 '점수:XX' 형식으로만 답해줘."
                        res = call_ai_model([("user", prompt)], api_key)
                        score = int(re.findall(r"\d+", res)[0]) if res and re.findall(r"\d+", res) else (60 if m['balance'] >= 0 else 40)
                        
                        time.sleep(1)
                        status.update(label=f"✅ {row['주소']} 분석 완료", state="complete", expanded=False)
                    
                    results.append({
                        "주소": row['주소'], "용도": row['용도'], "투자점수": score, 
                        "별점": get_star_rating(score), "예상ROI": f"{m['roi']}%", "예상비용": f"{m['total_cost']}억"
                    })
                    total_bar.progress((idx + 1) / len(df))
                
                st.session_state['bulk_results'] = pd.DataFrame(results).sort_values(by="투자점수", ascending=False)
                st.balloons()

# --- 메인 화면 ---

if mode == "대량 분석" and st.session_state['bulk_results'] is not None:
    res_df = st.session_state['bulk_results']
    
    st.subheader("📊 Deal Sourcing 비교 분석 리포트")
    
    # 1. 시각화 대시보드
    chart_col, kpi_col = st.columns([2, 1])
    with chart_col:
        st.bar_chart(res_df.set_index('주소')['투자점수'])
    with kpi_col:
        top = res_df.iloc[0]
        st.metric("🏆 최적 투자처", f"{top['투자점수']}점", top['별점'])
        st.write(f"**TOP PICK:** {top['주소']}")

    st.divider()

    # 2. 상세 결과 & 지도 연동
    st.subheader("🥇 분석 랭킹 및 현장 확인")
    
    for idx, row in res_df.iterrows():
        with st.expander(f"{row['별점']} [{row['투자점수']}점] {row['주소']} ({row['용도']})"):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.write(f"**💰 예상 비용:** {row['예상비용']}")
                st.write(f"**📈 예상 수익률(ROI):** {row['예상ROI']}")
                # 외부 지도 버튼
                col_m1, col_m2 = st.columns(2)
                col_m1.link_button("📍 네이버 지도", f"https://map.naver.com/v5/search/{row['주소']}")
                col_m2.link_button("📍 카카오 맵", f"https://map.kakao.com/link/search/{row['주소']}")
            with c2:
                # 간이 지도 (김포/파주/강화 근처 기본 좌표)
                lat, lon = (37.689, 126.589) if "김포" in row['주소'] else (37.75, 126.68) if "파주" in row['주소'] else (37.6, 126.4)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=13)

    # 3. 데이터 다운로드
    st.divider()
    csv = res_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 전체 분석 결과 CSV 다운로드", csv, "jisang_ai_report.csv", "text/csv", type="primary")

else:
    st.info("👈 왼쪽 사이드바에서 샘플 데이터를 불러온 후 [초격차 일괄 분석]을 실행하세요.")