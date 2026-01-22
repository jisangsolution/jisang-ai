import streamlit as st
import requests

st.set_page_config(page_title="지상 AI 최종 진단", page_icon="🕵️", layout="wide")
st.title("🕵️ 지상 AI: 구글 서버 직통 진단")

# 1. API 키 확인
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ API 키가 없습니다.")
    st.stop()

# 키 일부만 보여주기 (보안)
st.info(f"🔑 적용된 키: `{api_key[:4]}...{api_key[-4:]}`")

# 2. 구글 서버에 '사용 가능한 모델 목록' 직접 요청 (라이브러리 미사용)
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

if st.button("🚀 서버 상태 확인 (클릭)", type="primary"):
    try:
        response = requests.get(url)
        data = response.json()
        
        st.divider()
        st.subheader("📡 구글 서버 응답 원문")
        
        # 3. 결과 분석
        if response.status_code == 200:
            # 성공 시: 모델 목록 출력
            if "models" in data:
                models = [m['name'] for m in data['models']]
                st.success("✅ **연결 성공!** 사용 가능한 모델 목록:")
                st.code(models)
                st.balloons()
            else:
                st.warning("⚠️ 연결은 됐는데, 사용 가능한 모델이 하나도 없습니다. (프로젝트 설정 문제)")
                st.json(data)
        else:
            # 실패 시: 정확한 에러 메시지 출력
            st.error(f"❌ **서버 거절 (코드 {response.status_code})**")
            st.error("구글이 보낸 거절 사유:")
            st.json(data) # 여기에 진짜 이유가 나옵니다.
            
            # 4. 자주 발생하는 원인 해설
            if "User location is not supported" in str(data):
                st.warning("👉 원인: 현재 접속한 국가(IP)에서 API를 차단 중입니다.")
            elif "API key not valid" in str(data):
                st.warning("👉 원인: 키가 틀렸거나 삭제되었습니다.")
            elif "billing" in str(data).lower():
                st.warning("👉 원인: **결제 계정 연동 필요** (무료 티어라도 카드 등록이 필요할 수 있습니다).")
            elif "has not enabled" in str(data):
                st.warning("👉 원인: API가 아직 활성화되지 않았습니다.")

    except Exception as e:
        st.error(f"통신 오류: {e}")