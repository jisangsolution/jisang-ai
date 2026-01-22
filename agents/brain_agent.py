import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class JisangBrain:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ [경고] API Key가 없습니다. .env 파일을 확인하세요.")
            self.llm = None
        else:
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2, google_api_key=api_key)

    def analyze(self, address, doc_data, market_data):
        if not self.llm:
            return "❌ API Key 오류로 분석 불가"
        
        prompt = PromptTemplate(
            input_variables=["address", "doc_data", "market_data"],
            template="""
            당신은 대한민국 상위 0.1% 부동산 딥테크 AI '지상'입니다.
            다음 데이터를 분석하여 원클릭 리포트를 작성하세요.

            주소: {address}
            [공적장부 요약]: {doc_data}
            [시장 데이터]: {market_data}

            [출력 양식]
            === 🏢 지상 AI 딥테크 분석 리포트 ===
            1. 🚦 종합 등급: [S/A/B/C/F]
            2. ⚖️ 법률 리스크: (신탁, 가압류 등 권리분석)
            3. 💰 금융/가치: (적정 시세 및 대출 한도 추정)
            4. 📝 최종 결론: (매수 추천/보류/위험)
            """
        )
        chain = prompt | self.llm
        return chain.invoke({"address": address, "doc_data": doc_data, "market_data": market_data}).content
