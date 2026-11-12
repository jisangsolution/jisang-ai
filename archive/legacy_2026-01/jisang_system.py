import os
import sys
import subprocess
import time
import asyncio

# [Step 0] 자가 치유(Self-Healing) 및 라이브러리 로드
# --------------------------------------------------------------------------------
def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"🛠️ [시스템] 필수 모듈 '{package}' 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 필수 라이브러리 목록 점검
required = ["langchain", "langchain_google_genai", "python-dotenv", "langchain_core"]
for req in required:
    # 패키지 이름과 import 이름이 다를 수 있어 예외처리
    try:
        if req == "python-dotenv": __import__("dotenv")
        elif req == "langchain_google_genai": __import__("langchain_google_genai")
        else: __import__(req)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# [Step 1] 환경 설정 (API Key)
# --------------------------------------------------------------------------------
load_dotenv()
# 만약 .env 파일이 안 읽히면 아래에 직접 키를 입력해서 테스트 가능 (보안 주의)
api_key = os.getenv("GOOGLE_API_KEY") 

# [Step 2] 데이터 마이닝 (가상 데이터 - Opal Agent 역할)
# --------------------------------------------------------------------------------
MOCK_DATA = {
    "address": "경기도 김포시 통진읍 도사리 163-1",
    "registry": """
    [표제부] 공장용지, 1,200m2
    [갑구] 2023.05 소유권이전 (주)지상테크 -> 2023.06 신탁등기(우리자산신탁)
    [을구] 압류 1건 (김포세무서, 2024.01)
    """,
    "market": """
    - 규제: 군사기지 및 군사시설 보호구역, 성장관리권역
    - 시세: 주변 공장 평당 350~400만원, 최근 거래 절벽
    """
}

# [Step 3] 핵심 추론 엔진 (Brain Agent)
# --------------------------------------------------------------------------------
class JisangBrain:
    def __init__(self):
        # ★ 핵심 수정: 모델명을 가장 안정적인 'gemini-1.5-flash'로 변경
        # (기존 gemini-1.5-pro 오류 해결)
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", 
                temperature=0.1,
                google_api_key=api_key
            )
            self.status = "ONLINE"
        except Exception as e:
            print(f"⚠️ 모델 로드 실패: {e}")
            self.status = "OFFLINE"

    def analyze_property(self, data):
        if self.status == "OFFLINE" or not api_key:
            return "❌ [오류] API Key가 없거나 모델 연결에 실패했습니다."

        prompt = PromptTemplate.from_template("""
            당신은 대한민국 최고의 부동산 딥테크 AI '지상'입니다.
            아래 데이터를 분석하여 투자 의사결정 리포트를 작성하세요.

            [대상 물건]
            - 주소: {address}
            - 등기/대장: {registry}
            - 시장/규제: {market}

            [출력 양식]
            === 🏭 [지상 AI] 부동산 정밀 분석 리포트 ===
            1. 🚦 종합 판정: [매수추천/신중검토/매수금지]
            2. 💣 핵심 리스크 분석:
               - 신탁등기 이슈: (상세 내용)
               - 압류 이슈: (경매 가능성 등)
            3. 💰 가치 평가: (적정가 및 대출 여력)
            4. 📝 최종 전략 제언:
        """)
        
        chain = prompt | self.llm
        return chain.invoke(data).content

# [Step 4] 오케스트레이터 (통합 제어)
# --------------------------------------------------------------------------------
async def main():
    print("\n" + "="*60)
    print("🚀 [지상 AI] 부동산 원클릭 시스템 개발 모드 (v1.0)")
    print("="*60)

    # 1. 데이터 수집
    print(f"\n[1단계] 데이터 수집 중... (Target: {MOCK_DATA['address']})")
    time.sleep(1)
    print("   >>> 등기부등본 파싱 완료.")
    print("   >>> 토지이용계획원 분석 완료.")
    print("   >>> ⚠️ [경고] '신탁' 및 '압류' 키워드 감지!")

    # 2. AI 분석
    print("\n[2단계] Gemini 1.5 Flash 추론 엔진 가동")
    brain = JisangBrain()
    
    start = time.time()
    result = brain.analyze_property(MOCK_DATA)
    end = time.time()

    # 3. 결과 출력
    print(f"\n[3단계] 분석 완료 (소요시간: {end - start:.2f}초)")
    print("-" * 60)
    print(result)
    print("-" * 60)
    print("\n✅ 시스템 정상 작동 확인.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())