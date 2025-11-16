# agents/question_analyzer.py

import os
from dotenv import load_dotenv
from typing import TypedDict
import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage
from langchain_core.runnables import RunnablePassthrough

# .env 파일 로드
load_dotenv() 

# 워크플로우 상태 정의
class AnalysisState(TypedDict):
    """LangGraph의 상태 객체"""
    question: str
    intent: str                  # '템플릿_찾기', '프로세스_안내', '담당자_찾기', '일반_질문'
    document_type: str | None    # '보고서', '신청서', '기안서' 등
    urgency: str                 # '높음', '보통', '낮음'

class QuestionAnalyzer:
    """사용자 질문을 분석하여 의도와 키워드를 추출하는 Agent"""
    
    def __init__(self):
        # Solar LLM (분류 작업에 적합)
        self.llm = ChatUpstage(model="solar-1-mini-chat", temperature=0)
        
        # 질문 분석을 위한 프롬프트
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """당신은 공공기관의 질문 분석 및 라우팅 전문가입니다.
                주어진 질문을 분석하여 다음 4가지 의도 중 하나로 분류하고, 
                필요한 메타데이터(문서유형, 긴급도)를 JSON 형식으로 정확하게 추출하세요.
                
                # 의도 분류 기준
                1. 템플릿_찾기: 특정 양식이나 템플릿 파일 자체를 요청하는 경우. (예: "OOO 신청서 양식 줘", "최신 보고서 템플릿")
                2. 프로세스_안내: 어떤 업무를 처음 할 때의 '순서'나 '절차'를 요청하는 경우. (예: "A 업무 처음인데 순서가?", "장비 구매 절차")
                3. 담당자_찾기: 특정 업무나 문서의 담당자/연락처를 요청하는 경우. (예: "예산 담당자 누구야?", "인사팀 내선번호")
                4. 일반_질문: 위의 세 가지에 해당하지 않는 단순 정보 요청이나 작성 팁 요청. (예: "보고서 작성 시 주의사항", "출장 신청서 예시")
                
                # 긴급도 기준
                - 높음: '급해요', '빨리', '긴급', '당장' 등의 키워드가 포함된 경우.
                - 보통: 일반적인 요청.
                
                # 출력 형식 (반드시 JSON만 출력)
                {{
                  "intent": "분류된 의도",
                  "document_type": "문서 유형 또는 null",
                  "urgency": "긴급도"
                }}
                
                주의: 다른 텍스트 없이 JSON만 출력하세요.
                """
            ),
            ("user", "질문: {question}")
        ])
        
        # LCEL 체인 구성
        self.chain = self.prompt | self.llm 

    def _extract_json(self, text: str) -> dict:
        """
        LLM 응답에서 JSON을 안전하게 추출합니다.
        
        Args:
            text: LLM 응답 텍스트
            
        Returns:
            파싱된 JSON 딕셔너리
        """
        # 1. 코드 블록 제거
        if "```json" in text:
            match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
        elif "```" in text:
            match = re.search(r'```\s*(\{.*?\})\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
        
        # 2. 첫 번째 JSON 객체만 추출 (중첩 허용)
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        
        # 3. 파싱 실패 시 예외 발생
        raise ValueError("JSON을 찾을 수 없습니다.")

    def analyze(self, state: AnalysisState) -> AnalysisState:
        """분석을 실행하고 상태를 업데이트합니다."""
        question = state["question"]
        
        # LLM 호출
        response = self.chain.invoke({"question": question})
        
        try:
            # JSON 추출 및 파싱
            analysis_result = self._extract_json(response.content)
            
            # 상태 업데이트
            new_state = {
                "question": question,
                "intent": analysis_result.get("intent", "일반_질문"),
                "document_type": analysis_result.get("document_type"),
                "urgency": analysis_result.get("urgency", "보통")
            }
            return new_state
            
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            return {
                "question": question,
                "intent": "일반_질문",
                "document_type": None,
                "urgency": "보통"
            }

# --- 테스트 코드 ---
if __name__ == "__main__":
    analyzer = QuestionAnalyzer()
    
    test_cases = [
        "예산 신청서 급해요",
        "A 업무 처음인데 순서가 어떻게 되나요?",
        "보고서 작성 시 유의할 점",
        "출장신청서 양식 어디 있어요?",
        "인사팀 담당자 연락처 알려주세요",
    ]
    
    print("=" * 60)
    print("QuestionAnalyzer 테스트")
    print("=" * 60)
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n[테스트 {i}]")
        state = analyzer.analyze({
            "question": question,
            "intent": "",
            "document_type": None,
            "urgency": "보통"
        })
        print(f"결과: {state}")
        print("-" * 60)
    
    print("\n✨ 모든 테스트 완료!")