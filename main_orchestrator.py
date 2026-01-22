import sys
import os
import time
import asyncio

# [경로 강제 설정] agents 모듈을 못 찾는 에러 원천 봉쇄
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from agents.brain_agent import JisangBrain
except ImportError as e:
    print(f"❌ 모듈 로딩 실패: {e}")
    sys.exit(1)

# 가상 데이터 (Mockup)
MOCK_REGISTRY = """
[표제부] 김포시 양촌읍 석모리 123-4
[갑구] 소유자: (주)지상개발, 2023년 신탁등기(KB부동산신탁)
[을구] 근저당: 채권최고액 12억원
"""
MOCK_MARKET = """
정책: 김포 콤팩트시티 수용 예정지
시세: 호가 1500만원 (고평가)
"""

async def run():
    print("="*60)
    print("🚀 [지상 AI] 부동산 원클릭 의사결정 시스템 가동")
    print("="*60)
    
    print("\n[Step 1] Opal Agent 가동 (Data Mining)... 완료")
    print("[Step 2] Gemini 3.0 Pro 추론 시작...")
    
    brain = JisangBrain()
    start = time.time()
    result = brain.analyze("김포시 석모리 123-4", MOCK_REGISTRY, MOCK_MARKET)
    end = time.time()
    
    print(f"\n✅ 분석 완료 ({end-start:.2f}초)")
    print("-" * 60)
    print(result)
    print("-" * 60)

if __name__ == "__main__":
    asyncio.run(run())
