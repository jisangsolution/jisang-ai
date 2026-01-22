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
st.caption("Ver 9.0 - Bulk Analysis & Ranking System")

# 세션 초기화
if 'analysis_result' not in st.session_state: st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []
if 'metrics' not in st.session_state: st.session_state['metrics'] = {}
if 'scores' not in st.session_state: st.session_state['scores'] = {}
if 'bulk_results' not in st.session_state: st.session_state['bulk_results'] = None

# --- 핵심 함수 모음 ---

def calculate_metrics(area, budget, purpose):
    cost_map = {"요양원": 850, "전원주택": 750, "물류창고": 450, "상가": 600}
    # 매핑되지 않은 용도는 기본값 700
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
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return None
    except:
        return None

def extract_data(full_text):
    default_scores = {"입지": 0, "수요": 0, "수익성": 0, "안정성": 0, "총점": 0}
    if not full_text: return default_scores, ""
    
    try:
        json_match = re.search(r"```json\s*({.*?})\s*```", full_text, re.DOTALL)
        if json_match:
            scores = json.loads(json_match.group(1))
            html_content = re.sub(r"```json.*?```", "", full_text, flags=re.DOTALL).strip()
            return scores, html_content
        else:
            return default_scores, full_text
    except:
        return default_scores, full_text

def create_html_report(addr, purp, area, bdgt, metrics, ai_text, scores):
    # (이전 버전과 동일한 HTML 생성 로직 - 간소화하여 포함)
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
    st.header("⚙️ 분석 모드 선택")
    mode = st.radio("모드", ["단일 분석 (Single)", "대량 분석 (Batch)"])
    
    api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
    if not api_key: st.error("API 키가 필요합니다.")

    if mode == "단일 분석 (Single)":
        st.subheader("📝 정보 입력")
        address = st.text_input("주소", "김포시 통진읍 도사리 163-1")
        purpose = st.selectbox("용도", ["요양원", "전원주택", "물류창고", "상가"])
        area = st.number_input("면적(평)", 100)
        budget = st.slider("예산(억)", 1, 100, 5)
        
        if st.button("🚀 분석 실행", type="primary"):
            if not api_key: st.stop()
            with st.spinner("AI 분석 중..."):
                m = calculate_metrics(area, budget, purpose)
                st.session_state['metrics'] = m
                
                prompt = f"""
                주소:{address}, 용도:{purpose}, 면적:{area}평, 예산:{budget}억.
                (계산: 비용{m['total_cost']}억, 잔액{m['balance']}억)
                
                [형식]
                1. ```json {{ "입지":00, "수요":00, "수익성":00, "안정성":00, "총점":00 }} ```
                2. 그 아래 순수 HTML 태그로 상세 보고서 작성 (마크다운 X).
                """
                res = call_ai_model([("user", prompt)], api_key)
                if res:
                    s, h = extract_data(res)
                    st.session_state['scores'] = s
                    st.session_state['analysis_result'] = h

    else: # 대량 분석 모드
        st.subheader("📂 엑셀 업로드")
        st.info("엑셀 파일에 '주소', '용도', '면적', '예산' 컬럼이 있어야 합니다.")
        
        # 샘플 데이터 생성 버튼
        if st.button("기본 샘플 데이터 사용하기"):
            sample_data = pd.DataFrame({
                '주소': ['김포시 통진읍 도사리 163-1', '파주시 탄현면 성동리 100', '강화군 화도면 상방리 55'],
                '용도': ['요양원', '전원주택', '물류창고'],
                '면적': [100, 150, 300],
                '예산': [5, 10, 20]
            })
            st.session_state['upload_df'] = sample_data
            
        uploaded_file = st.file_uploader("또는 파일 업로드 (.xlsx)", type=['xlsx'])
        if uploaded_file:
            st.session_state['upload_df'] = pd.read_excel(uploaded_file)
            
        if 'upload_df' in st.session_state:
            st.dataframe(st.session_state['upload_df'], height=150)
            
            if st.button("🔥 일괄 분석 시작"):
                if not api_key: st.stop()
                results = []
                df = st.session_state['upload_df']
                progress_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    with st.spinner(f"{idx+1}/{len(df)} 분석 중: {row['주소']}..."):
                        m = calculate_metrics(row['면적'], row['예산'], row['용도'])
                        prompt = f"""
                        간단 분석 요청. 주소:{row['주소']}, 용도:{row['용도']}, 예산:{row['예산']}억.
                        (비용{m['total_cost']}억).
                        [형식] ```json {{ "입지":00, "수요":00, "수익성":00, "안정성":00, "총점":00 }} ```
                        """
                        res = call_ai_model([("user", prompt)], api_key)
                        score = 0
                        grade = "F"
                        if res:
                            s, _ = extract_data(res)
                            score = s.get('총점', 0)
                            grade = "S" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C"
                        
                        results.append({
                            "주소": row['주소'],
                            "용도": row['용도'],
                            "총점": score,
                            "등급": grade,
                            "예상비용": f"{m['total_cost']}억",
                            "자금상태": m['status']
                        })
                        time.sleep(1) # API 제한 방지
                        progress_bar.progress((idx + 1) / len(df))
                
                st.session_state['bulk_results'] = pd.DataFrame(results).sort_values(by="총점", ascending=False)
                st.success("대량 분석 완료!")

# --- 메인 화면 ---

if mode == "단일 분석 (Single)":
    if st.session_state['analysis_result']:
        s = st.session_state['scores']
        st.subheader(f"🏆 투자 매력도: {s.get('총점', 0)}점")
        
        # 차트
        c1, c2 = st.columns([1, 3])
        with c1:
            grade = "S" if s.get('총점',0)>=90 else "A" if s.get('총점',0)>=80 else "B" if s.get('총점',0)>=70 else "C"
            st.metric("등급", grade)
        with c2:
            chart_df = pd.DataFrame({'점수': [s.get('입지',0), s.get('수요',0), s.get('수익성',0), s.get('안정성',0)]}, 
                                    index=['입지', '수요', '수익성', '안정성'])
            st.bar_chart(chart_df)
            
        t1, t2 = st.tabs(["📄 프리미엄 보고서", "💬 AI 파트너"])
        with t1:
            html = create_html_report(address, purpose, area, budget, st.session_state['metrics'], st.session_state['analysis_result'], s)
            st.components.v1.html(html, height=800, scrolling=True)
        with t2:
            # 대화 기능 유지
            for r, t in st.session_state['chat_history']:
                if r != "system":
                    with st.chat_message(r): st.write(t)
            if q := st.chat_input("질문 입력"):
                with st.chat_message("user"): st.write(q)
                st.session_state['chat_history'].append(("user", q))
                ans = call_ai_model(st.session_state['chat_history'], api_key)
                with st.chat_message("assistant"): st.write(ans)
                st.session_state['chat_history'].append(("assistant", ans))

else: # 대량 분석 모드 결과 화면
    if st.session_state['bulk_results'] is not None:
        st.divider()
        st.subheader("🥇 Deal Sourcing 랭킹 (Top Picks)")
        
        # 1등 강조
        top_pick = st.session_state['bulk_results'].iloc[0]
        st.info(f"👑 **최고 추천 투자처:** {top_pick['주소']} ({top_pick['용도']}) - **{top_pick['총점']}점 (Grade {top_pick['등급']})**")
        
        # 전체 데이터 테이블
        st.dataframe(st.session_state['bulk_results'], use_container_width=True)
        
        # 다운로드
        csv = st.session_state['bulk_results'].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 랭킹 리포트 다운로드 (CSV)", csv, "investment_ranking.csv", "text/csv")