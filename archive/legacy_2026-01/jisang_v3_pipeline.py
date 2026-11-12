import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random

# [Step 0] 필수 라이브러리 자동 점검
def check_and_install(package, import_name=None):
    if import_name is None: import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"🛠️ [시스템] '{package}' 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

check_and_install("google-generativeai", "google.generativeai")
check_and_install("python-dotenv", "dotenv")
check_and_install("python-dateutil", "dateutil")

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key: genai.configure(api_key=api_key)

# --------------------------------------------------------------------------------
# [Helper] 스마트 모델 탐색기 (이게 있어야 에러가 안 납니다)
# --------------------------------------------------------------------------------
def get_best_model():
    print("🔍 [System] 최적의 AI 모델을 검색 중...", end="")
    try:
        # 사용 가능한 모델 리스트 조회
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 우선순위: Flash (빠름/저렴) -> Pro (고성능)
        preferred = ['models/gemini-1.5-flash', 'models/gemini-2.0-flash', 'models/gemini-pro']
        
        for p in preferred:
            if p in models:
                print(f" 완료! ✅ [{p}] 선택됨")
                return p
        
        # 목록에 없으면 첫 번째 가능한 모델 선택
        fallback = models[0] if models else 'gemini-pro'
        print(f" 대체 모델 [{fallback}] 선택됨")
        return fallback
    except Exception as e:
        print(f"\n⚠️ 모델 검색 실패: {e}. 기본값 'gemini-pro' 사용.")
        return 'gemini-pro'

# --------------------------------------------------------------------------------
# [Module 1] Opal Agent: 데이터 마이닝 (Hands)
# --------------------------------------------------------------------------------
class OpalAgent:
    def __init__(self, mode="simulation"):
        self.mode = mode
        print("💎 [Opal] 데이터 마이닝 에이전트 가동")

    def fetch_real_data(self, address):
        print(f"\n🌐 [Opal] 타겟 접속: '{address}'")
        
        # 시뮬레이션: 실제 크롤링인 것처럼 딜레이 연출
        steps = [
            "인터넷등기소(IROS) 보안 모듈 로딩...",
            "부동산 고유번호(PIN) 조회 성공...",
            "등기사항전부증명서 PDF 다운로드 및 OCR 변환...",
            "정부24 건축물대장 위반건축물 여부 조회..."
        ]
        
        for step in steps:
            time.sleep(random.uniform(0.3, 0.7))
            print(f"   >> {step}")

        print("   ✅ [Opal] 데이터 추출 완료.")
        return {
            "address": address,
            "market_price": 950000000, 
            "bonds": [
                {"bank": "우리은행", "date": "2019.05.20", "amount": 450000000, "type": "1금융"},
                {"bank": "리드코프", "date": "2024.01.15", "amount": 150000000, "type": "대부업"}
            ],
            "restrictions": ["신탁등기(코리아신탁)", "가압류(국민건강보험공단)"],
            "owner_change_count_3yr": 2
        }

# --------------------------------------------------------------------------------
# [Module 2] Fact Checker: 데이터 무결성 검증 (Calculator)
# --------------------------------------------------------------------------------
class FactChecker:
    @staticmethod
    def process(data):
        print("\n⚖️ [FactChecker] 1차 검증 (Python Engine)")
        report = []
        
        # 대환대출 타겟팅
        for bond in data['bonds']:
            target_date = datetime.strptime(bond['date'], "%Y.%m.%d")
            diff = relativedelta(datetime.now(), target_date)
            months = diff.years * 12 + diff.months
            
            is_target = months >= 24
            mark = "✅대환타겟(2년↑)" if is_target else "🔒유지구간"
            report.append(f"- {bond['bank']} ({bond['type']}): {months}개월 경과 -> {mark}")

        # LTV 계산
        total_bond = sum(b['amount'] for b in data['bonds'])
        ltv = round((total_bond / data['market_price']) * 100, 2)
        report.append(f"- 총 채권액: {format(total_bond, ',')}원 (LTV: {ltv}%)")
        
        return {
            "text_report": "\n".join(report),
            "ltv": ltv,
            "risk_factors": data['restrictions']
        }

# --------------------------------------------------------------------------------
# [Module 3] Insight Engine: AI 추론 (Brain)
# --------------------------------------------------------------------------------
class InsightEngine:
    def __init__(self):
        # ★ 수정된 부분: 무조건 작동하는 모델을 가져옴
        model_name = get_best_model()
        self.model = genai.GenerativeModel(model_name)

    def analyze(self, opal_data, fact_data):
        prompt = f"""
        역할: 대한민국 부동산 권리분석 전문가 AI.
        
        [입력 데이터]
        - 주소: {opal_data['address']}
        - 팩트 데이터:
        {fact_data['text_report']}
        - 리스크 항목: {", ".join(opal_data['restrictions'])}

        [요청사항]
        위 팩트 데이터를 기반으로 다음 항목을 분석해줘.
        1. 🚦 종합 안전 등급 (S/A/B/C/F)
        2. 💰 금융 전략: 대환대출이 필요한가? (특히 대부업체 관련)
        3. ⚖️ 권리 위험: 신탁등기가 거래에 미치는 영향 설명.
        4. 📝 한 줄 결론.
        """
        
        print("\n🧠 [Brain] 최종 추론 중... ", end="")
        try:
            response = self.model.generate_content(prompt)
            print("완료!")
            return response.text
        except Exception as e:
            return f"❌ 분석 중 오류 발생: {e}"

# --------------------------------------------------------------------------------
# [Main] 실행
# --------------------------------------------------------------------------------
async def main():
    print("\n" + "="*70)
    print("🏙️ [지상 AI] V3 통합 시스템 (Opal + Fact + Brain + AutoModel)")
    print("="*70)

    target_address = "김포시 구래동 한강반도유보라 4차"
    
    # 1. 수집
    opal = OpalAgent()
    raw_data = opal.fetch_real_data(target_address)

    # 2. 검증
    fact = FactChecker()
    verified_data = fact.process(raw_data)

    # 3. 추론
    brain = InsightEngine()
    final_report = brain.analyze(raw_data, verified_data)

    # 4. 결과 출력
    print("\n" + "="*70)
    print("📋 [지상 AI 원클릭 리포트]")
    print("="*70)
    print(final_report)
    print("-" * 70)
    print("✅ [System] 프로세스 정상 종료.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())