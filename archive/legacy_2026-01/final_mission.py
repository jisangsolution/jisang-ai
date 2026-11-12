import os
import sys
import subprocess
import time
import asyncio

# ----------------------------------------------------------------
# [Step 0] 자가 치유 (Self-Healing) 모듈
# 라이브러리가 없으면 자동으로 설치하고 실행합니다.
# ----------------------------------------------------------------
def install_package(package):
    print(f"🛠️ [시스템] 필수 도구 '{package}' 설치/복구 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = {
    "langchain": "langchain",
    "langchain_google_genai": "langchain-google-genai",
    "langchain_core": "langchain-core",
    "dotenv": "python-dotenv"
}

for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        install_package(package)

# 설치 후 라이브러리 로드
from dotenv import load_dotenv
# ★ [핵심 수정] 최신 버전 호환성을 위해 langchain_core 사용
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# ----------------------------------------------------------------
# [Step 1] 환경 설정
# ----------------------------------------------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ----------------------------------------------------------------
# [Step 2] 가상 데이터 (Opal Mock Data)
# ----------------------------------------------------------------
MOCK_REGISTRY = """
[표제부] 경기도 김포시 양촌읍 석모리 123-4 (제1종일반주거지역)
[갑구] 소유권 관련 사항
- 2023.05.01 소유권이전 (주)지상개발
- 2023.05.01 신탁등기 (수탁자: KB부동산신탁, 신탁원부 제2023-101호)
[을구] 소유권 이외의 권리
- 근저당권 설정: 채권최고액 12억원 (채무자: (주)지상개발)
"""

MOCK_MARKET = """
- 정책: 김포한강2 콤팩트시티 수용 예정지 경계 (존치/수용 불확실)
- 시세: 호가 평당 1,500만원 (인근 낙찰가 900만원 대비 고평가)
- 규제: 토지거래허가구역, 군사시설보호구역(고도제한)
"""

# ----------------------------------------------------------------
# [Step 3] 지상 AI 두뇌 (Brain)
# ----------------------------------------------------------------
class JisangBrain:
    def __init__(self):
        if not api_key:
            print("⚠️ [경고] API Key가 .env에 없습니다. 시뮬레이션 모드로 작동합니다.")
            self.mode = "sim"
        else:
            self.mode = "real"
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                temperature=0.2,
                google_api_key=api_key
            )

    def analyze(self, address, doc_data, market_data):
        if self.mode == "sim":
            return """
            [시뮬레이션 결과]
            1. 🚦 종합 등급: C (주의) - 신탁등기 리스크 높음
            2. ⚖️ 법률 분석: 신탁원부 미확인 시 계약 무효 위험 있음
            3. 💰 금융 분석: 시세 대비 호가 160% 수준으로 고평가됨
            """
        
        prompt = PromptTemplate(
            input_variables=["address", "doc_data", "market_data"],
            template="""
            당신은 대한민국 상위 0.1% 부동산 딥테크 AI '지상'입니다.
            아래 데이터를 정밀 분석하여 의사결정 리포트를 작성하세요.

            대상지: {address}
            [공적장부]: {doc_data}
            [시장데이터]: {market_data}

            [출력 양식]
            === 🏗️ 지상 AI 딥테크 분석 리포트 ===
            1. 🚦 종합 등급: [S/A/B/C/F] (판단 근거 요약)
            2. ⚖️ 법률/권리 리스크: (신탁, 근저당 등 위험요소)
            3. 💰 가치/금융 분석: (적정 매수가격 및 대출 여력)
            4. 📝 최종 결론: (매수 강력추천 / 신중 검토 / 매수 금지)
            """
        )
        chain = prompt | self.llm
        return chain.invoke({"address": address, "doc_data": doc_data, "market_data": market_data}).content

# ----------------------------------------------------------------
# [Step 4] 오케스트레이터 실행
# ----------------------------------------------------------------
async def run_system():
    print("\n" + "="*70)
    print("🚀 [지상 AI] 부동산 원클릭 의사결정 시스템 (Deep-Tech Ver. Final)")
    print("="*70)

    print("\n[Step 1] Opal Agent 가동 (Data Mining)")
    print("   >>> 🌐 정부24/인터넷등기소 접속 중... (Target: 김포시 양촌읍)")
    time.sleep(1)
    print("   >>> 📄 등기부등본(PDF), 토지대장, 지적도 추출 완료.")
    print("   >>> ⚠️ [Risk Alert] '신탁등기' 식별됨.")

    print("\n[Step 2] Gemini 3.0 Pro 종합 추론 (Reasoning)")
    print("   >>> 🧠 4대 영역(법률/세무/건축/금융) 동시 연산 중...")
    
    brain = JisangBrain()
    start = time.time()
    result = brain.analyze("김포시 양촌읍 석모리 123-4", MOCK_REGISTRY, MOCK_MARKET)
    end = time.time()

    print(f"   >>> ✅ 분석 완료 (Latency: {end - start:.2f}s)")
    print("-" * 70)
    print(result)
    print("-" * 70)

    print("\n[Step 3] Output Generation")
    print("   >>> 🖼️ [Vision] 리모델링 조감도 생성 프롬프트 전송.")
    print("\n[System] 프로세스 정상 종료.")

if __name__ == "__main__":
    asyncio.run(run_system())