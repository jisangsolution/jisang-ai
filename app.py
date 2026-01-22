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
st.caption("Ver 9.4 - Safety First & Exponential Backoff")

# 세션 초기화
if 'analysis_result' not in st.session_state: st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []
if 'metrics' not in st.session_state: st.session_state['metrics'] = {}
if 'scores' not in st.session_state: st.session_state['scores'] = {}
if 'bulk_results' not in st.session_state: st.session_state['bulk_results'] = None

# --- 핵심 함수 ---

def calculate_metrics(area, budget, purpose):
    cost_map = {"요양원": 850, "전원주택": 750, "물류창고": 450, "상가": 600}
    unit_cost = cost_map.get(purpose.split('/')[0], 700) 
    est_const_cost = area * unit_cost / 10000 
    est_total_cost = est_const_cost * 1.2 
    balance = budget - est_total_cost 
    return {
        "unit_cost": unit_cost,
        "total_cost": round(est_total_cost, 2),
        "balance": round(balance, 2),
        "status": "여유" if balance >= 0 else "부족"
    }

# [Ver 9.4 핵심] 지수적 백오프 (점점 더 오래 기다리기)
def call_ai_model(messages, api_key):
    base = "https://generativelanguage.googleapis.com/v1beta/models"
    model = "gemini-flash-latest"
    url = f"{base}/{model}:generateContent?key={api_key}"
    
    contents = []
    for role, text in messages:
        r = "user" if role == "user" else "model"
        contents.append({"role": r, "parts": [{"text": text}]})
    payload = {"contents": contents}
    headers = {'Content-Type': 'application/json'}
    
    # 1차 시도 -> 실패시 10초 대기 -> 실패시 30초 대기
    wait_times = [10, 30, 60] 
    
    for i, wait in enumerate(wait_times):
        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            elif res.status_code == 429:
                # 429 에러는 '잠시 멈춤' 신호 -> 길게 대기
                time.sleep(wait) 
                continue 
            else:
                return None
        except:
            time.sleep(wait)
            continue
            
    return None # 3번 다 실패하면 None 반환

def extract_data(full_text):
    default_scores = {"입지": 0, "수요": 0, "수익성": 0, "안정성": 0, "총점": 0}
    if not full_text: return default_scores, ""
    
    html_content = full_text
    scores = default_scores.copy()
    
    try:
        # 1. JSON 파싱
        json_match = re.search(r"({.*?})", full_text, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
                if "총점" in json_data:
                    scores.update(json_data)
                    html_content = full_text.replace(json_match.group(1), "").strip()
                    html_content = re.sub(r"```json|```", "", html_content).strip()
                    return scores, html_content
            except: pass

        # 2. 강제 패턴 매칭 (하이브리드)
        patterns = {
            "총점": r"(총점|종합 점수|Total Score)\D*(\d+)",
            "입지": r"(입지)\D*(\d+)",
            "수요": r"(수요)\D*(\d+)",
            "수익성": r"(수익성)\D*(\d+)",
            "안정성": r"(안정성)\D*(\d+)"
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, full_text)
            if match:
                target_key = "총점" if key in ["총점", "종합 점수", "Total Score"] else key
                scores[target_key] = int(match.group(2))
        
        return scores, full_text
    except:
        return default_scores, full_text

def create_html_report(addr, purp, area, bdgt, metrics, ai_text, scores):
    ai_text = ai_text.replace("```html", "").replace("```", "")
    html = f"""
    <div style='font-family:Malgun Gothic; padding:30px; border:1px solid #ddd; background:white;'>
        <h2 style='color:#1E3A8A; border-bottom:2px solid #1E3A8A;'>부동산 개발 타당성 보고서</h2>
        <div style='background:#E0E7FF; padding:15px; text-align:center; border-radius:10px; margin:20px 0;'>
            <span style='color:#555;'>AI 종합 투자 점수</span><br>
            <span style='font-size:32px; font-weight:bold; color:#1E3A8A;'>{scores.get('총점',0)}점</span>
        </div>
        <table style='width:100%; border-collapse:collapse; margin-bottom:20px;'>
            <tr style='background:#f8f9fa;'><th style='border:1px solid #ddd; padding:10px;'>항목</th><th style='border:1px solid #ddd; padding:10px;'>내용</th></tr>
            <tr><td style='border:1px solid #ddd; padding:10px;'>주소</td><td style='border:1px solid #ddd; padding:10px;'>{addr}</td></tr>
            <tr><td style='border:1px solid #ddd; padding:10px;'>용도/면적</td><td style='border:1px solid #ddd; padding:10px;'>{purp} / {area}평</td></tr>
            <tr><td style='border:1px solid #ddd; padding:10px;'>총 비용/과부족</td><td style='border:1px solid #ddd; padding:10px;'>{metrics['total_cost']}억 / {metrics['balance']}억 ({metrics['status']})</td></tr>
        </table>
        <div style='line-height:1.6;'>{ai_text}</div>
    </div>
    """
    return html

# --- UI 구성 ---

with st.sidebar:
    st.header("⚙️ 분석 모드")
    mode = st.radio("선택", ["단일 분석", "대량 분석"])
    
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    if not api_key: st.error("API 키 필요")

    if mode == "단일 분석":
        st.subheader("📝 입력")
        address = st.text_input("주소", "김포시 통진읍 도사리 163-1")
        purpose = st.selectbox("용도", ["요양원", "전원주택", "물류창고", "상가"])
        area = st.number_input("면적", 100)
        budget = st.slider("예산(억)", 1, 100, 5)
        
        if st.button("🚀 실행", type="primary"):
            if not api_key: st.stop()
            with st.spinner("분석 중..."):
                m = calculate_metrics(area, budget, purpose)
                st.session_state['metrics'] = m
                prompt = f"""
                주소:{address}, 용도:{purpose}, 면적:{area}평, 예산:{budget}억.
                (계산: 비용{m['total_cost']}억, 잔액{m['balance']}억)
                [형식]
                1. ```json {{ "입지":00, "수요":00, "수익성":00, "안정성":00, "총점":00 }} ```
                2. 상세 HTML 보고서 작성.
                """
                res = call_ai_model([("user", prompt)], api_key)
                if res:
                    s, h = extract_data(res)
                    st.session_state['scores'] = s
                    st.session_state['analysis_result'] = h

    else: # 대량 분석
        st.subheader("📂 엑셀 처리")
        if st.button("샘플 데이터 로드"):
            st.session_state['upload_df'] = pd.DataFrame({
                '주소': ['김포시 통진읍 도사리 163-1', '파주시 탄현면 성동리 100', '강화군 화도면 상방리 55'],
                '용도': ['요양원', '전원주택', '물류창고'],
                '면적': [100, 150, 300],
                '예산': [5, 10, 20]
            })
            
        if 'upload_df' in st.session_state:
            st.dataframe(st.session_state['upload_df'], height=150)
            
            if st.button("🔥 일괄 분석 시작"):
                if not api_key: st.stop()
                results = []
                raw_logs = []
                df = st.session_state['upload_df']
                bar = st.progress(0)
                status_box = st.empty() # 상태 메시지용 박스
                
                for idx, row in df.iterrows():
                    status_box.info(f"⏳ 분석 중 ({idx+1}/{len(df)}): {row['주소']} ...")
                    
                    m = calculate_metrics(row['면적'], row['예산'], row['용도'])
                    prompt = f"""
                    부동산 심사역 역할.
                    주소:{row['주소']}, 용도:{row['용도']}, 예산:{row['예산']}억.
                    예상비용{m['total_cost']}억.
                    
                    [필수] 투자 점수(0~100) 평가.
                    답변 형식: "총점: 85, 입지: 80, 수요: 90, 수익성: 80, 안정성: 90"
                    설명 생략. 점수만 출력.
                    """
                    res = call_ai_model([("user", prompt)], api_key)
                    
                    score = 0
                    grade = "F"
                    if res:
                        s, _ = extract_data(res)
                        score = s.get('총점', 0)
                        grade = "S" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C"
                        raw_logs.append(f"[{row['주소']}] {res}")
                    else:
                        raw_logs.append(f"[{row['주소']}] ❌ 3회 재시도 실패 (과부하)")
                    
                    results.append({
                        "주소": row['주소'],
                        "총점": score,
                        "등급": grade,
                        "예상비용": f"{m['total_cost']}억",
                        "상태": m['status']
                    })
                    
                    # [안전 장치] 과부하 방지를 위한 강제 휴식
                    status_box.warning(f"⚠️ API 과부하 방지를 위해 10초간 대기합니다...")
                    time.sleep(10) # 10초 대기
                    bar.progress((idx + 1) / len(df))
                
                status_box.success("모든 분석이 완료되었습니다!")
                st.session_state['bulk_results'] = pd.DataFrame(results).sort_values(by="총점", ascending=False)
                st.session_state['logs'] = raw_logs
                st.success("완료!")

# --- 메인 화면 ---

if mode == "단일 분석":
    if st.session_state['analysis_result']:
        s = st.session_state['scores']
        st.subheader(f"🏆 점수: {s.get('총점', 0)}점")
        c1, c2 = st.columns([1, 3])
        c1.metric("등급", "S" if s.get('총점',0)>=90 else "A" if s.get('총점',0)>=80 else "B" if s.get('총점',0)>=70 else "C")
        c2.bar_chart(pd.DataFrame({'점수': [s.get('입지',0), s.get('수요',0), s.get('수익성',0), s.get('안정성',0)]}, index=['입지', '수요', '수익성', '안정성']))
        html = create_html_report(address, purpose, area, budget, st.session_state['metrics'], st.session_state['analysis_result'], s)
        st.components.v1.html(html, height=800, scrolling=True)

else: 
    if st.session_state['bulk_results'] is not None:
        st.divider()
        st.subheader("🥇 랭킹 (Top Picks)")
        
        if not st.session_state['bulk_results'].empty:
            top = st.session_state['bulk_results'].iloc[0]
            st.info(f"👑 1위: {top['주소']} - **{top['총점']}점 ({top['등급']})**")
            st.dataframe(st.session_state['bulk_results'], use_container_width=True)
            
            with st.expander("🔍 AI 응답 로그 확인"):
                for log in st.session_state.get('logs', []):
                    st.text(log)