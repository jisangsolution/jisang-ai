import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정 및 스타일 (토지이음 스타일 벤치마킹)
st.set_page_config(page_title="지상 AI Pro v14.0", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
    .main { background-color: #fdfdfd; }
    .header-box { background: #1e3a8a; color: white; padding: 15px; border-radius: 5px 5px 0 0; font-weight: bold; }
    .info-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    .info-table td, .info-table th { border: 1px solid #e2e8f0; padding: 10px; font-size: 0.9rem; }
    .info-table th { background-color: #f1f5f9; color: #334155; font-weight: 600; width: 150px; }
    .badge-violation { background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }
    .badge-safe { background-color: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }
    .section-title { font-size: 1.2rem; font-weight: bold; color: #1e293b; margin-top: 20px; margin-bottom: 10px; border-left: 5px solid #1e3a8a; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ 지상 AI: 부동산 초격차 토탈 솔루션")
st.caption("Ver 14.0 - Data Integrity System (Land, Building, Registry)")

# --- [Core] 데이터 무결성 구조체 (DB Schema) ---
# 실제 API 연동 시 이 구조체에 데이터를 매핑합니다.
DB_INTEGRITY = {
    "도사리 163-1": {
        "토지정보": {
            "소재지": "경기도 김포시 통진읍 도사리 163-1번지",
            "지목": "임야 (사실상 대지)",
            "면적": "2,592㎡ (약 784평)",
            "공시지가": "270,000원/㎡ (2025/01)",
            "지역지구_국토법": ["도시지역", "자연녹지지역", "성장관리계획구역(복합형)"],
            "지역지구_타법령": ["가축사육제한구역(모든축종 제한)", "준보전산지", "성장관리권역"],
            "도시계획조례": ["김포시 도시계획 조례 별표16(건축할 수 있는 건축물)", "개발행위허가 기준 적용"],
            "도면": "image_54bf8d.png" # 가상 매핑
        },
        "건축물대장": {
            "주구조": "철근콘크리트구조",
            "주용도": "노유자시설(요양원)",
            "건폐율": "18.5% (법정 20% 이하)",
            "용적률": "65.2% (법정 80% 이하)",
            "규모": "지하 1층 / 지상 3층",
            "연면적": "1,680.5㎡",
            "사용승인일": "2018-05-20",
            "주차장": "옥외 12대 (법정 10대)",
            "정화조": "오수처리시설 (30톤/일)",
            "승강기": "승객용 1대 (15인승)",
            "위반건축물": False,
            "변동이력": ["2020-01: 소유자 주소변경", "2023-05: 1층 용도변경(사무소->식당)"]
        },
        "권리분석": {
            "소유자": "김지상 (개인)",
            "근저당": [
                {"순위": 1, "권리자": "우리은행 (1금융)", "채권최고액": "12억", "설정일": "2018-06-15"},
                {"순위": 2, "권리자": "김포축협 (상호금융)", "채권최고액": "3억", "설정일": "2021-03-10"}
            ],
            "압류": "없음",
            "리스크": "2순위 대출 금리 상승 우려 (대환 필요)"
        }
    }
}

# --- 로직 함수 ---

def analyze_debt(registry_data):
    """등기부 데이터를 분석하여 대출 리스크 및 대환 기회 포착"""
    loans = registry_data['근저당']
    total_debt = sum([int(l['채권최고액'].replace("억", "")) for l in loans])
    
    # 대환 대출 신호 포착 (설정일 2년 경과 여부)
    refinance_target = []
    today = datetime.now()
    for l in loans:
        setup_date = datetime.strptime(l['설정일'], "%Y-%m-%d")
        if (today - setup_date).days > 730: # 2년 경과
            refinance_target.append(f"{l['권리자']}({l['설정일']})")
            
    return total_debt, refinance_target

# --- UI 레이아웃 ---

with st.sidebar:
    st.header("🔍 무결성 조회")
    address_input = st.text_input("주소 입력", "김포시 통진읍 도사리 163-1")
    
    if st.button("🚀 원클릭 통합 조회", type="primary", use_container_width=True):
        if "도사리 163-1" in address_input:
            st.session_state['target_data'] = DB_INTEGRITY["도사리 163-1"]
        else:
            st.error("데모 버전에서는 '도사리 163-1' 데이터만 열람 가능합니다.")

# --- 메인 화면 ---

if 'target_data' in st.session_state:
    data = st.session_state['target_data']
    land = data['토지정보']
    bldg = data['건축물대장']
    reg = data['권리분석']
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📄 토지이음(규제)", "🏢 건축물대장", "⚖️ 권리/등기", "🤖 AI 종합진단"])
    
    # 1. 토지이음 탭 (토지정보)
    with tab1:
        st.subheader("📍 토지이용계획확인원 (Data Integrity)")
        
        # HTML 테이블로 정밀하게 구현
        st.markdown(f"""
        <table class="info-table">
            <tr><th>소재지</th><td colspan="3">{land['소재지']}</td></tr>
            <tr><th>지목</th><td>{land['지목']}</td><th>면적</th><td>{land['면적']}</td></tr>
            <tr><th>개별공시지가</th><td colspan="3">{land['공시지가']}</td></tr>
            <tr><th>지역지구(국토법)</th><td colspan="3">{', '.join(land['지역지구_국토법'])}</td></tr>
            <tr><th>지역지구(타법령)</th><td colspan="3">{', '.join(land['지역지구_타법령'])}</td></tr>
            <tr><th>지자체 조례</th><td colspan="3" style='color:blue;'>{', '.join(land['도시계획조례'])}</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.info("💡 **핵심 포인트**: '자연녹지지역'이면서 '성장관리계획구역(복합형)'이므로 일반 자연녹지보다 건폐율 인센티브 가능성이 있습니다.")

    # 2. 건축물대장 탭
    with tab2:
        st.subheader("🏢 일반건축물대장 (Facility Spec)")
        
        # 위반건축물 뱃지 처리
        violation_badge = "<span class='badge-violation'>위반건축물 등재</span>" if bldg['위반건축물'] else "<span class='badge-safe'>위반사항 없음</span>"
        
        st.markdown(f"""
        <table class="info-table">
            <tr><th>건물 상태</th><td colspan="3">{violation_badge}</td></tr>
            <tr><th>주용도</th><td>{bldg['주용도']}</td><th>주구조</th><td>{bldg['주구조']}</td></tr>
            <tr><th>규모</th><td>{bldg['규모']}</td><th>사용승인일</th><td>{bldg['사용승인일']}</td></tr>
            <tr><th>건폐율/용적률</th><td>{bldg['건폐율']} / {bldg['용적률']}</td><th>연면적</th><td>{bldg['연면적']}</td></tr>
            <tr><th>주차장</th><td>{bldg['주차장']}</td><th>정화조</th><td>{bldg['정화조']}</td></tr>
            <tr><th>승강기</th><td colspan="3">{bldg['승강기']}</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
        with st.expander("🔄 변동 이력 확인"):
            for history in bldg['변동이력']:
                st.text(f"- {history}")

    # 3. 권리분석 탭 (등기부 파싱)
    with tab3:
        st.subheader("⚖️ 권리관계 및 금융 분석 (Ownership & Debt)")
        
        total_debt, targets = analyze_debt(reg)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("소유자 구분", reg['소유자'])
        c2.metric("총 채권최고액", f"{total_debt}억 원")
        c3.metric("근저당 설정 건수", f"{len(reg['근저당'])}건")
        
        st.markdown("##### 🏦 근저당 설정 내역")
        df_loans = pd.DataFrame(reg['근저당'])
        st.dataframe(df_loans, use_container_width=True, hide_index=True)
        
        if targets:
            st.markdown(f"""
            <div style='background:#fefce8; padding:15px; border-radius:10px; border:1px solid #facc15;'>
                <b>💰 대환 대출(Refinancing) 기회 포착!</b><br>
                설정일로부터 2년 이상 경과한 대출이 <b>{len(targets)}건</b> 있습니다.<br>
                최근 금리 하락 기조를 반영하여 대환 컨설팅을 제안할 수 있습니다.<br>
                대상: {', '.join(targets)}
            </div>
            """, unsafe_allow_html=True)

    # 4. AI 종합진단 (무결성 기반)
    with tab4:
        st.subheader("🤖 AI 부동산 심층 브리핑")
        # 실제로는 여기서 LLM을 호출하지만, 무결성 테스트를 위해 정적 분석 결과 출력
        st.markdown(f"""
        **[종합 분석 결과]**
        
        1.  **입지 및 규제**: 본 토지는 **{land['면적'].split(' ')[0]}** 규모의 **{land['지역지구_국토법'][1]}**입니다. 특히 **성장관리계획구역** 지정으로 인해 개발 행위 시 인센티브 적용 여부를 반드시 지자체 조례를 통해 확인해야 합니다.
        2.  **건축물 가치**: **{bldg['사용승인일'][:4]}년** 준공된 건물로 비교적 신축에 속하며, **승강기와 오수처리시설**이 완비되어 있어 요양원 운영에 최적화되어 있습니다. 위반건축물 등재 내역이 없어 권리상 깨끗합니다.
        3.  **금융 리스크**: 1순위(우리은행)와 2순위(김포축협) 대출이 혼재되어 있습니다. 1순위 대출은 설정 후 **{datetime.now().year - 2018}년**이 경과하였으므로, 감정가 상승분을 반영한 **대환 대출**을 통해 추가 유동성을 확보하거나 금리를 낮출 수 있는 포인트가 있습니다.
        
        **👉 결론**: 시설 상태 우수하며, 금융 구조조정(Refinancing)을 통한 수익률 개선이 기대되는 물건입니다.
        """)

else:
    st.info("👈 왼쪽 사이드바에서 [원클릭 통합 조회]를 실행하여 데이터 무결성을 검증하세요.")