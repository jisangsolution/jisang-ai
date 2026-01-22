import os
import sys
import time
import asyncio

# ----------------------------------------------------------------
# [긴급 패치] LangChain 버전 호환성 해결
# ----------------------------------------------------------------
try:
    from langchain_core.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    try:
        from langchain.prompts import PromptTemplate
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        print("❌ 필수 라이브러리가 없습니다. 'pip install langchain-google-genai langchain-core' 실행 필요.")
        sys.exit(1)

from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ----------------------------------------------------------------
# [Mock Data] 김포시 통진읍 도사리 163-1 (실전 시뮬레이션 데이터)
# ----------------------------------------------------------------
MOCK_REGISTRY = """
[표제부] 경기도 김포시 통진읍 도사리 163-1
- 지목: 공장용지 (일부 계획관리지역)
[갑구] 소유권 사항
- 2022.11.15 소유권이전 (주)미래테크
- 2022.11.15 담보신탁등기 (수탁자: 우리자산신탁) *권리분석 필수*
[을구] 소유권 이외의 권리
- 압류: 김포세무서 (체납처분) - 2024.01.10 기입
"""

MOCK_MARKET = """
- 입지: 수도권제2순환고속도로 서김포통진IC 인근, 소규모 공장 밀집 지역
- 규제: 군사기지 및 군사시설 보호구역(통제보호구역), 성장관리권역
- 시세: 평당 350~400만 원 선 (최근 거래 둔화)
"""

# ----------------------------------------------------------------
# [Brain] 지능형 분석 엔진
# ----------------------------------------------------------------
class JisangBrain:
    def __init__(self):
        if not api_key:
            self.mode = "sim"
        else:
            self.mode = "real"
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                temperature=0.1, # 팩트 위주 분석을 위해 온도 낮춤
                google_api_key=api_key
            )

    def analyze(self, address, doc_data, market_data):
        if self.mode == "sim":
            return "⚠️ API 키 확인 필요. (시뮬레이션: 통진읍 공장용지 신탁 리스크 높음)"
        
        prompt = PromptTemplate(
            input_variables=["address", "doc_data", "market_data"],
            template="""
            당신은 김포/검단 지역 전문 부동산 딥테크 AI '지상'입니다.
            입력된 주소지의 리스크를 정밀 타격하여 분석하세요.

            대상지: {address}
            [공적장부]: {doc_data}
            [시장/규제]: {market_data}

            [출력 양식]
            === 🏭 지상 AI 공장/토지 정밀 분석 리포트 ===
            1. 🚦 종합 등급: [S/A/B/C/F] (판단 이유 간략히)
            2. 💣 핵심 리스크: (신탁 및 세무서 압류 분석 - 경매 진행 가능성 등)
            3. 🏗️ 입지/규제 분석: (군사시설보호구역 및 IC 접근성 가치)
            4. 📝 최종 전략: (매수 금지 / 압류 말소 조건부 계약 / 전문가 상담)
            """
        )
        chain = prompt | self.llm
        return chain.invoke({"address": address, "doc_data": doc_data, "market_data": market_data}).content

# ----------------------------------------------------------------
# [Main] 실행 로직
# ----------------------------------------------------------------
async def run():
    print("\n" + "="*70)
    print(f"🚀 [지상 AI] 부동산 원클릭 시스템 가동 (Target: 통진읍 도사리)")
    print("="*70)

    print("\n[Step 1] Opal Agent 가동 (정부24/온나라지도)")
    print("   >>> 🌐 주소지 파싱: '김포시 통진읍 도사리 163-1'")
    time.sleep(1)
    print("   >>> ⚠️ [경고] '담보신탁' 및 '세무서 압류' 등기 발견!")

    print("\n[Step 2] Gemini 3.0 Pro 정밀 권리분석")
    
    brain = JisangBrain()
    start = time.time()
    # 실제 주소와 데이터를 넣어줍니다.
    result = brain.analyze("김포시 통진읍 도사리 163-1", MOCK_REGISTRY, MOCK_MARKET)
    end = time.time()

    print(f"   >>> ✅ 분석 완료 (Latency: {end - start:.2f}s)")
    print("-" * 70)
    print(result)
    print("-" * 70)

if __name__ == "__main__":
    asyncio.run(run())