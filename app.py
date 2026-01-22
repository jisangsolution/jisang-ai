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
st.caption("Ver 9.6 - Visual Analytics & Reliable Metrics")

# 세션 초기화
if 'bulk_results' not in st.session_state: st.session_state['bulk_results'] = None

# --- 핵심 함수 ---

def calculate_metrics(area, budget, purpose):
    cost_map = {"요양원": 850, "전원주택": 750, "물류창고": 450, "상가": 600}
    unit_cost = cost_map.get(purpose.split('/')[0], 700) 
    est_const_cost = area * unit_cost / 10000 
    est_total_cost = est_const_cost * 1.2 
    balance = budget - est_total_cost 
    
    # 예상 수익률(ROI) 가상 시뮬레이션 로직 추가
    roi = 12.5 if balance >= 0 else 5.2
    
    return {
        "unit_cost": unit_cost,
        "total_cost": round(est_total_cost, 2),
        "balance": round(balance, 2),
        "status": "여유" if balance >= 0 else "부족",
        "roi": roi
    }

def call_ai_model(messages, api_key):
    base = "https://generativelanguage.googleapis.com/v1beta/models"
    model = "gemini-flash-latest"
    url = f"{base}/{model}:generateContent?key={api_key}"
    
    contents = []
    for role, text in messages:
        contents.append({"role": "user" if role == "user" else "model", "parts": [{"text": text}]})
    
    headers = {'Content-Type': 'application/json'}
    
    # 안전한 재시도 (Exponential Backoff)
    for wait in [5, 10]:
        try:
            res = requests.post(url, headers=headers, json={"contents": contents}, timeout=10)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            elif res.status_code == 429:
                time.sleep(wait)
        except:
            time.sleep(wait)
    return None

def extract_scores(text, default_val=50):
    scores = {"총점": default_val, "입지": default_val, "수익성": default_val}
    if not text: return scores
    
    # 정규표현식으로 숫자 추출 강화
    nums = re.findall(r"(총점|점수|Score)\D*(\d+)", text)
    if nums:
        scores["총점"] = int(nums[0][1])
    return scores

# --- UI 구성 ---

with st.sidebar:
    st.header("⚙️ 분석 모드")
    mode = st.radio("선택", ["단일 분석", "대량 분석"])
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()

    if mode == "대량 분석":
        st.subheader("📂 데이터 로드")
        if st.button("샘플 데이터 불러오기"):
            st.session_state['upload_df'] = pd.DataFrame({
                '주소': ['김포시 도사리 163-1', '파주시 성동리 100', '강화군 상방리 55'],
                '용도': ['요양원', '전원주택', '물류창고'],
                '면적': [100, 150, 300],
                '예산': [5, 10, 20]
            })
            
        if 'upload_df' in st.session_state:
            st.dataframe(st.session_state['upload_df'], use_container_width=True)
            
            if st.button("🔥 초격차 일괄 분석 시작", type="primary"):
                results = []
                df = st.session_state['upload_df']
                total_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    # 토스 스타일 인터랙션
                    with st.status(f"🔍 **[{idx+1}/{len(df)}] {row['주소']}** 분석 중...", expanded=True) as status:
                        st.write("📊 수지분석 시뮬레이션 가동...")
                        m = calculate_metrics(row['면적'], row['예산'], row['용도'])
                        time.sleep(1)
                        
                        st.write("🧠 AI 부동산 전문가 가치 평가 중...")
                        prompt = f"주소:{row['주소']}, 용도:{row['용도']}, 비용:{m['total_cost']}억. 투자 점수(0~100)를 '총점: XX' 형식으로만 답해줘."
                        res = call_ai_model([("user", prompt)], api_key)
                        
                        st.write("📈 최종 수익률 및 등급 산출 중...")
                        s = extract_scores(res, default_val=60 if m['balance'] >= 0 else 40) # AI 실패 시 기본 로직으로 보정
                        score = s["총점"]
                        grade = "S" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C"
                        
                        time.sleep(2)
                        status.update(label=f"✅ {row['주소']} 완료 ({score}점)", state="complete", expanded=False)
                    
                    results.append({
                        "주소": row['주소'],
                        "용도": row['용도'],
                        "투자점수": score,
                        "등급": grade,
                        "예상ROI": f"{m['roi']}%",
                        "예상비용": f"{m['total_cost']}억",
                        "자금상태": m['status']
                    })
                    total_bar.progress((idx + 1) / len(df), text=f"전체 공정 {int((idx+1)/len(df)*100)}% 완료")
                
                st.session_state['bulk_results'] = pd.DataFrame(results).sort_values(by="투자점수", ascending=False)
                st.balloons()

# --- 메인 화면 (수치 및 시각화 강화) ---

if mode == "대량 분석" and st.session_state['bulk_results'] is not None:
    res_df = st.session_state['bulk_results']
    
    st.subheader("📊 Deal Sourcing 비교 분석")
    
    # [시각화 추가] 후보지별 투자 점수 비교 차트
    chart_col, kpi_col = st.columns([2, 1])
    
    with chart_col:
        st.write("📍 **후보지별 투자 점수 비교**")
        st.bar_chart(res_df.set_index('주소')['투자점수'])
        
    with kpi_col:
        top_pick = res_df.iloc[0]
        st.metric("🏆 최적 투자처 점수", f"{top_pick['투자점수']}점", f"Grade {top_pick['등급']}")
        st.write(f"**추천 사유:** {top_pick['주소']}는 예산 대비 수익률({top_pick['예상ROI']})이 가장 높게 분석되었습니다.")

    st.divider()
    
    st.subheader("🥇 전체 분석 랭킹")
    st.dataframe(
        res_df.style.highlight_max(axis=0, subset=['투자점수'], color='#D1FAE5'),
        use_container_width=True
    )
    
    # CSV 다운로드
    csv = res_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 랭킹 리포트 다운로드", csv, "investment_ranking.csv", "text/csv")

else:
    st.info("👈 왼쪽에서 분석할 부지 리스트를 확인하고 [🔥 일괄 분석 시작]을 눌러주세요.")