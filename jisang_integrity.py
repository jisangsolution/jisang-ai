import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime
from dateutil.relativedelta import relativedelta # 날짜 정밀 계산용

# [Step 0] 필수 라이브러리 점검
def check_and_install(package, import_name=None):
    if import_name is None: import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"🛠️ [시스템] '{package}' 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

check_and_install("python-dotenv", "dotenv")
check_and_install("langchain-google-genai")
check_and_install("langchain")
check_and_install("python-dateutil", "dateutil") # 날짜 계산 필수

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --------------------------------------------------------------------------------
# [Step 1] Fact Checker (Python 정밀 계산기) - AI 아님, 절대 오차 없음
# --------------------------------------------------------------------------------
class FactChecker:
    @staticmethod
    def calculate_months_passed(date_string):
        """날짜 문자열(YYYY.MM.DD)을 받아 오늘 기준 경과 개월 수를 정확히 계산"""
        try:
            target_date = datetime.strptime(date_string, "%Y.%m.%d")
            today = datetime.now()
            diff = relativedelta(today, target_date)
            months = diff.years * 12 + diff.months
            return months
        except ValueError:
            return 0

    @staticmethod
    def is_safe_ratio(bond_total, market_price):
        """담보비율 기계적 계산"""
        if market_price == 0: return 0
        return round((bond_total / market_price) * 100, 2)

# --------------------------------------------------------------------------------
# [Step 2] Raw Data (OCR/파싱된 원본 데이터라고 가정)
# --------------------------------------------------------------------------------
RAW_DATA = {
    "address": "김포시 통진읍 도사리 163-1",
    "market_price": 800000000, # 시세 8억 가정
    "bonds": [
        {"bank": "국민은행", "date": "2020.06.01", "amount": 500000000, "type": "1금융"},
        {"bank": "러시앤캐시", "date": "2023.12.01", "amount": 300000000, "type": "대부업"}
    ],
    "restrictions": ["신탁등기(우리자산신탁)", "가압류(김포세무서)"]
}

# --------------------------------------------------------------------------------
# [Step 3] Pre-Processing (전처리: 사실 확정 단계)
# AI에게 넘기기 전에 Python이 '팩트'를 확정 짓습니다.
# --------------------------------------------------------------------------------
def preprocess_data(data):
    report = []
    
    # 1. 대환대출 타겟팅 (날짜 계산)
    for bond in data['bonds']:
        months = FactChecker.calculate_months_passed(bond['date'])
        is_target = "✅대환대상(24개월↑)" if months >= 24 else "신규대출"
        report.append(f"- {bond['bank']}: 설정후 {months}개월 경과 -> {is_target}")
    
    # 2. 총 채권액 합산 (단순 덧셈)
    total_bond = sum(b['amount'] for b in data['bonds'])
    ltv = FactChecker.is_safe_ratio(total_bond, data['market_price'])
    
    report.append(f"- 총 채권액: {format(total_bond, ',')}원 (LTV: {ltv}%)")
    
    return "\n".join(report)

# --------------------------------------------------------------------------------
# [Step 4] AI Insight Engine (가치 판단만 수행)
# --------------------------------------------------------------------------------
class JisangIntegrityEngine:
    def __init__(self):
        if not api_key: sys.exit(1)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.0, # ★ 창의성 0% 설정 (팩트 기반 답변 강제)
            google_api_key=api_key
        )

    def analyze(self, raw_facts, calculated_facts):
        prompt = PromptTemplate.from_template("""
            [Strict Rules]
            1. You are a strict auditor. Do NOT infer or guess any numbers.
            2. Use ONLY the provided 'Computed Facts'.
            3. Analyze the risk based on these facts.

            [Input Data]
            - Raw Limitations: {raw_restrictions}
            - Computed Facts (Trusted): 
            {calculated_facts}

            [Output Format]
            === 🛡️ [지상 AI] 데이터 무결성 검증 리포트 ===
            1. 🔢 수치 검증 (Python Calculated):
               (LTV 및 대환대출 대상 여부 그대로 출력)
            
            2. 🚦 리스크 판단 (AI Analysis):
               - 권리 리스크: (신탁/압류에 대한 법적 해석만 기술)
               - 금융 리스크: (LTV 비율에 따른 위험도 평가)

            3. 💡 전문가 제언:
               (대환대출 실행 전략 및 신탁 말소 필요성)
        """)
        
        chain = prompt | self.llm
        return chain.invoke({
            "raw_restrictions": ", ".join(RAW_DATA['restrictions']),
            "calculated_facts": calculated_facts
        }).content

# --------------------------------------------------------------------------------
# [Step 5] 실행 (Orchestration)
# --------------------------------------------------------------------------------
async def main():
    print("\n" + "="*80)
    print("🛡️ [지상 AI] 무결성(Integrity) 최우선 시스템 가동")
    print("   >> 전략: Python이 계산하고, AI는 해석한다. (No Hallucination)")
    print("="*80)

    # 1. Python 정밀 계산 (Pre-processing)
    print(f"\n[Phase 1] Fact Checker 가동 (수치 정밀 계산)")
    computed_facts = preprocess_data(RAW_DATA)
    print("   >>> 계산 결과 확정:")
    print(computed_facts)

    # 2. AI 분석
    print("\n[Phase 2] Gemini 1.5 Flash 해석 (Inference 0%)")
    engine = JisangIntegrityEngine()
    
    start = time.time()
    result = engine.analyze(RAW_DATA['restrictions'], computed_facts)
    end = time.time()

    print(f"   >>> ✅ 검증 완료 (Latency: {end - start:.2f}s)")
    print("-" * 80)
    print(result)
    print("-" * 80)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())