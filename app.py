import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Jisang AI - 진단 모드", page_icon="🩺", layout="wide")

# 1. API 키 가져오기
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ Secrets에 GOOGLE_API_KEY가 없습니다.")
        st.stop()
    # 공백 제거 처리 (실수 방지)
    api_key = api_key.strip()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")
    st.stop()

def debug_connection():
    """API 연결 상태를 정밀 진단합니다."""
    # 2. 모델 연결 테스트
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, AI!")
        return True, f"✅ 성공! 응답: {response.text}"
    except Exception as e:
        error_msg = str(e)
        # 에러 유형 분석
        if "403" in error_msg:
            return False, f"🚫 **403 권한 오류 (PERMISSION_DENIED)**:\n이 API 키는 유효하지만 사용 권한이 없습니다.\n\n[원인]\n1. 구글 클라우드 프로젝트에 결제 계정이 연결되지 않음.\n2. 'Generative AI API'가 활성화되지 않음.\n\n[상세 에러]\n{error_msg}"
        elif "400" in error_msg:
            return False, f"❌ **400 잘못된 요청 (INVALID_ARGUMENT)**:\nAPI 키 형식이 잘못되었습니다. 복사 과정에서 공백이 들어갔거나 키 값이 손상되었습니다.\n\n[상세 에러]\n{error_msg}"
        elif "404" in error_msg:
            return False, f"🔍 **404 모델 없음 (NOT_FOUND)**:\n라이브러리는 최신이지만 모델명을 찾을 수 없습니다.\n\n[상세 에러]\n{error_msg}"
        else:
            return False, f"⚠️ **기타 오류**: \n{error_msg}"

def main():
    st.title("🩺 지상 AI 긴급 진단 모드")
    st.info("현재 API 키가 작동하지 않는 정확한 원인을 분석합니다.")
    
    st.write(f"🔑 현재 입력된 키 확인 (앞 5자리): `{str(api_key)[:5]}...`")
    
    if st.button("🚀 진단 시작", type="primary"):
        with st.spinner("구글 서버와 통신 중..."):
            success, message = debug_connection()
            
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error("진단 결과: 연결 실패")
                st.markdown(message)

if __name__ == "__main__":
    main()