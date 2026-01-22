import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime
from dateutil.relativedelta import relativedelta 

# [Step 0] 라이브러리 자동 점검
def check_and_install(package, import_name=None):
    if import_name is None: import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"🛠️ [시스템] 필수 도구 '{package}' 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

check_and_install("python-dotenv", "dotenv")
check_and_install("langchain-google-genai")
check_and_install("langchain")
check_and_install("python-dateutil", "dateutil")

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --------------------------------------------------------------------------------
# [Step 1] Fact Checker (Python 정밀 계산기) - 무결성 핵심
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
# [Step 2] Raw Data (가상 데이터)
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
# [Step 3] Pre-Processing (사실 확정)
# --------------------------------------------------------------------------------
def preprocess_data(data):
    report = []
    
    # 1. 대환대출 타겟팅
    for bond in data['bonds']:
        months = FactChecker.calculate_months_passed(bond['date'])
        target_mark = "✅대환대상(24개월↑)" if months >= 24 else "신규대출"
        report.append(f"- {bond['bank']}: 설정후 {months}개월 경과 -> {target_mark}")
    
    # 2. 총 채권액 합산
    total_bond = sum(b['amount'] for b in data['bonds'])
    ltv = FactChecker.is_safe_ratio(total_bond, data['market_price'])
    
    report.append(f"- 총 채권액: {format(total_bond, ',')}원 (LTV: {ltv}%)")
    return "\n".join(report)

# --------------------------------------------------------------------------------
# [Step 4] AI Insight Engine (가치 판단)
# --------------------------------------------------------------------------------
class JisangIntegrityEngine:
    def __init__(self):
        if not api_key:
            print("❌ API Key가 없습니다. .env 파일을 확인하세요.")
            sys.exit(1)
        
        # ★ 핵심 수정: 모델명을 가장 안정적인 'gemini-pro'로 변경 (404 에러 해결책)
        try:
            print("🔌 [연결] Google Gemini Pro (Stable) 모델에 접속 중...")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro", 
                temperature=0.0, # 팩트 기반 분석 강제
                google_api_key=api_key
            )
        except Exception as e:
            print(f"⚠️ 모델 연결 실패: {e}")
            sys.exit(1)

    def analyze(self, raw_facts, calculated_facts):
        prompt = PromptTemplate.from_template("""
            [Strict Role]
            You are a strict real estate auditor.
            Use ONLY the provided 'Computed Facts' by Python.
            Do NOT calculate numbers yourself.

            [Input Data]
            - Raw Risks: {raw_restrictions}
            - Verified Facts: 
            {calculated_facts}

            [Output Format]
            === 🛡️ [지상 AI] 데이터 무결성 검증 리포트 ===
            1. 🔢 수치 검증 (Python Calculated):
               (Verified Facts 내용 그대로 출력)
            
            2. 🚦 리스크 판단 (AI Analysis):
               - 권리 리스크: (신탁/압류에 대한 법적 해석)
               - 금융 리스크: (LTV 및 대부업체 이용에 따른 위험성 평가)

            3. 💡 전문가 제언:
               (대환대출 실행 전략 및 리스크 해소 방안)
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
    print("🛡️ [지상 AI] 무결성(Integrity) 시스템 가동 (Model: Gemini Pro)")
    print("   >> 전략: Python이 계산하고, AI는 해석한다.")
    print("="*80)

    # 1. Python 정밀 계산
    print(f"\n[Phase 1] Fact Checker 가동 (수치 정밀 계산)")
    computed_facts = preprocess_data(RAW_DATA)
    print("   >>> 계산 결과 확정:")
    print(computed_facts)

    # 2. AI 분석
    print("\n[Phase 2] Gemini Pro 해석 (Inference Start)")
    try:
        engine = JisangIntegrityEngine()
        start = time.time()
        result = engine.analyze(RAW_DATA['restrictions'], computed_facts)
        end = time.time()

        print(f"   >>> ✅ 검증 완료 (Latency: {end - start:.2f}s)")
        print("-" * 80)
        print(result)
        print("-" * 80)
    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생: {e}")
        print("💡 팁: .env 파일의 API KEY가 정확한지 다시 확인하세요.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())