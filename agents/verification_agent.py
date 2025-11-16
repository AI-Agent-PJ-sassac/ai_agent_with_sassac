# agents/verification_agent.py

import os
from dotenv import load_dotenv
from typing import TypedDict, List
from datetime import datetime

from langchain_core.documents import Document

# .env 파일 로드
load_dotenv()


# 워크플로우 상태 정의
class VerificationState(TypedDict):
    """검증 Agent의 상태"""
    question: str
    intent: str
    document_type: str | None
    urgency: str
    search_results: List[Document]
    templates: List[Document]
    examples: List[Document]
    related: List[Document]
    answer: str
    summary: str
    tips: str
    is_verified: bool
    warnings: List[str]


class VerificationAgent:
    """답변 품질을 검증하는 Agent"""
    
    def __init__(self):
        self.current_year = datetime.now().year
    
    def _check_document_freshness(self, docs: List[Document]) -> List[str]:
        """문서의 최신성을 확인합니다."""
        warnings = []
        old_docs = []
        
        for doc in docs:
            year = doc.metadata.get("year")
            if year and year < self.current_year - 2:
                source = doc.metadata.get("source", "Unknown")
                old_docs.append(f"{source} ({year}년)")
        
        if old_docs:
            warnings.append(
                f"⚠️  일부 문서가 2년 이상 오래되었습니다: {', '.join(old_docs[:3])}"
            )
        
        return warnings
    
    def _check_answer_completeness(self, state: VerificationState) -> List[str]:
        """답변의 완성도를 확인합니다."""
        warnings = []
        answer = state.get("answer", "")
        
        if len(answer) < 50:
            warnings.append("⚠️  답변이 너무 짧습니다.")
        
        if "📌" not in answer or "📝" not in answer:
            warnings.append("⚠️  답변이 권장 형식으로 구조화되지 않았습니다.")
        
        if not state.get("search_results") and not state.get("templates"):
            warnings.append("⚠️  참고 문서 없이 답변이 생성되었습니다.")
        
        return warnings
    
    def _check_intent_match(self, state: VerificationState) -> List[str]:
        """답변이 질문 의도와 일치하는지 확인합니다."""
        warnings = []
        intent = state.get("intent", "")
        answer = state.get("answer", "")
        
        if intent == "템플릿_찾기":
            if not any(keyword in answer for keyword in ["양식", "템플릿", "파일"]):
                warnings.append("⚠️  템플릿 관련 정보가 부족합니다.")
        
        elif intent == "프로세스_안내":
            if not any(keyword in answer for keyword in ["단계", "순서", "절차"]):
                warnings.append("⚠️  프로세스 단계별 설명이 부족합니다.")
        
        return warnings
    
    def _check_urgency_handling(self, state: VerificationState) -> List[str]:
        """긴급도에 따른 답변 적절성을 확인합니다."""
        warnings = []
        urgency = state.get("urgency", "보통")
        answer = state.get("answer", "")
        
        if urgency == "높음" and len(answer) > 1000:
            warnings.append("⚠️  긴급 질문이지만 답변이 너무 깁니다.")
        
        return warnings
    
    def verify(self, state: VerificationState) -> VerificationState:
        """답변의 품질을 종합적으로 검증합니다."""
        all_warnings = []
        
        all_warnings.extend(self._check_document_freshness(
            state.get("search_results", []) + 
            state.get("templates", []) + 
            state.get("examples", [])
        ))
        
        all_warnings.extend(self._check_answer_completeness(state))
        all_warnings.extend(self._check_intent_match(state))
        all_warnings.extend(self._check_urgency_handling(state))
        
        is_verified = len(all_warnings) == 0
        
        new_state = {
            **state,
            "is_verified": is_verified,
            "warnings": all_warnings
        }
        
        return new_state


# --- 테스트 코드 ---
if __name__ == "__main__":
    verifier = VerificationAgent()
    
    from langchain_core.documents import Document
    
    test_state_good = {
        "question": "출장신청서 어떻게 작성하나요?",
        "intent": "템플릿_찾기",
        "document_type": "출장신청서",
        "urgency": "보통",
        "search_results": [
            Document(
                page_content="출장신청서는 출장 목적, 일정, 예상 경비를 기재합니다.",
                metadata={"source": "출장신청서_양식.pdf", "year": 2024}
            )
        ],
        "templates": [],
        "examples": [],
        "related": [],
        "answer": """📌 요약:
출장신청서는 출장 목적, 일정, 예상 경비를 작성하여 제출하는 양식입니다.

📝 상세 설명:
1. 출장 목적과 장소 명확히 기재
2. 출장 기간 작성

💡 작성 팁:
- 출장 3일 전까지 제출""",
        "summary": "출장신청서는...",
        "tips": "출장 3일 전까지 제출"
    }
    
    print("=" * 60)
    print("VerificationAgent 테스트")
    print("=" * 60)
    
    result = verifier.verify(test_state_good)
    print(f"\n검증 결과: {'통과 ✅' if result['is_verified'] else '실패 ❌'}")
    print(f"경고 개수: {len(result['warnings'])}")
    print("\n✨ 테스트 완료!")