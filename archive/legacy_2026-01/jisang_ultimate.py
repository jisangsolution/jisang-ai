import os
import sys
import subprocess
import time
import asyncio
from datetime import datetime
from dateutil.relativedelta import relativedelta

# [Step 0] 필수 라이브러리 자동 설치 (Self-Healing)
# --------------------------------------------------------------------------------
def check_and_install(package, import_name=None):
    if import_name is None: import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"🛠️ [시스템] 필수 도구 '{package}' 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# LangChain을 버리고 Google 순정 SDK 사용 (안정성 100%)
check_and_install("google-generativeai", "google.generativeai")
check_and_install("python-dotenv", "dotenv")
check_and_install("python-dateutil", "dateutil")

import google.generativeai as genai
from dotenv import load_dotenv

# [Step 1] 환경 설정 및 모델 자동 탐색 (Auto-Discovery)
# --------------------------------------------------------------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ [오류] .env 파일에서 API Key를 찾을 수 없습니다.")
    sys.exit(1)

genai.configure(api_key=api_key)

def get_best_model():
    """사용 가능한 모델 목록을 조회하여 최적의 모델을 자동 선택"""
    print("\n🔍 [시스템] 사용 가능한 AI 모델 검색 중...")
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 우선순위: Flash 1.5 -> Pro 1.5 -> Pro 1.0 -> 아무거나
        if 'models/gemini-1.5-flash' in available_models:
            return 'models/gemini-1.5-flash'
        elif 'models/gemini-1.5-pro' in available_models:
            return 'models/gemini-1.5-pro'
        elif 'models/gemini-pro' in available_models:
            return 'models/gemini-pro'
        else:
            return available_models[0] # 아무거나 되는 거 선택
    except Exception as e:
        print(f"⚠️ 모델 검색 실패: {e}")
        return 'gemini-pro' # 기본값 시도

# [Step 2] Fact Checker (데이터 무결성 엔진)
# --------------------------------------------------------------------------------
class FactChecker:
    @staticmethod
    def calculate_months_passed(date_string):
        try:
            target_date = datetime.strptime(date_string, "%Y.%m.%d")
            today = datetime.now()
            diff = relativedelta(today, target_date)
            return diff.years * 12 + diff.months
        except ValueError:
            return 0

    @staticmethod
    def is_safe_ratio(bond_total, market_price):
        if market_price == 0: return 0
        return round((bond_total / market_price) * 100, 2)

# [Step 3] 가상 데이터 (통진읍 도사리)
# --------------------------------------------------------------------------------
RAW_DATA = {
    "address": "김포시 통진읍 도사리 163-1",
    "market_price": 800000000, 
    "bonds": [
        {"bank": "국민은행", "date": "2020.06.01", "amount": 500000000, "type": "1금융"},
        {"bank": "러시앤캐시", "date": "2023.12.01", "amount": 300000000, "type": "대부업"}
    ],
    "restrictions": ["신탁등기(우리자산신탁)", "가압류(김포세무서)"]
}

# [Step 4] Pre-Processing (사실 확정)
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

# [Step 5] 실행 (Orchestration)
# --------------------------------------------------------------------------------
def main():
    print("\n" + "="*80)
    print("🛡️ [지상 AI] 부동산 무결성(Integrity) 시스템 가동")
    print("   >> 전략: Python Fact Check + Google Native SDK (No LangChain Errors)")
    print("="*80)

    # 1. 모델 선택
    selected_model_name = get_best_model()
    print(f"✅ [연결 성공] 선택된 모델: {selected_model_name}")

    # 2. Python 정밀 계산
    print(f"\n[Phase 1] Fact Checker 가동 (수치 정밀 계산)")
    computed_facts = preprocess_data(RAW_DATA)
    print("   >>> 계산 결과 확정:")
    print(computed_facts)

    # 3. AI 분석
    print("\n[Phase 2] AI Insight 해석 (Inference Start)")
    try:
        model = genai.GenerativeModel(selected_model_name)
        
        prompt = f"""
        당신은 엄격한 부동산 권리분석 전문가 AI입니다.
        아래 제공된 [확정된 사실]만을 바탕으로 리포트를 작성하세요. 숫자를 직접 계산하지 마세요.

        [입력 데이터]
        - 주소: {RAW_DATA['address']}
        - 등기상 제한권리: {", ".join(RAW_DATA['restrictions'])}
        - 확정된 사실(Python 계산됨):
        {computed_facts}

        [출력 양식]
        === 🛡️ [지상 AI] 데이터 무결성 검증 리포트 ===
        1. 🔢 수치 검증:
           (확정된 사실 내용을 요약 출력)
        
        2. 🚦 리스크 신호등:
           - 권리 리스크: (신탁/압류의 법적 위험성 설명)
           - 금융 리스크: (LTV 100% 초과 및 대부업체 사용의 위험성 경고)

        3. 💡 전문가 제언:
           (대환대출 가능성 및 경매 방어 전략 제시)
        """

        response = model.generate_content(prompt)
        print("-" * 80)
        print(response.text)
        print("-" * 80)
        print("\n🎉 [성공] 모든 프로세스가 정상적으로 완료되었습니다.")

    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()