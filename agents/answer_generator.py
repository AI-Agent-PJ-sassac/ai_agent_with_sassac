# agents/answer_generator.py

import os
from dotenv import load_dotenv
from typing import TypedDict, List

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage

# .env 파일 로드
load_dotenv()


# 워크플로우 상태 정의
class AnswerState(TypedDict):
    """답변 생성 Agent의 상태"""
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


class AnswerGenerator:
    """구조화된 답변을 생성하는 Agent"""
    
    def __init__(self):
        # Solar Pro LLM (답변 생성용)
        self.llm = ChatUpstage(model="solar-pro", temperature=0.3)
        
        # 답변 생성 프롬프트
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """당신은 공공기관 업무 지원 AI 어시스턴트입니다.
                주어진 문서를 바탕으로 질문에 정확하고 친절하게 답변해주세요.
                
                # 답변 형식
                반드시 다음 형식으로 답변하세요:
                
                📌 요약:
                (한 줄로 핵심 답변)
                
                📝 상세 설명:
                (단계별 또는 상세한 설명)
                
                💡 작성 팁 및 주의사항:
                (실무에 도움되는 팁, 주의사항, 자주 하는 실수 등)
                
                # 답변 작성 가이드
                1. 요약은 한 문장으로 명확하게
                2. 상세 설명은 2-5개 항목으로 구조화
                3. 팁은 실무에서 바로 적용 가능한 것으로
                4. 전문 용어는 쉽게 풀어서 설명
                5. 긴급도가 '높음'이면 간소화된 방법 우선 안내
                """
            ),
            (
                "user",
                """질문: {question}
                
                의도: {intent}
                문서 유형: {document_type}
                긴급도: {urgency}
                
                참고 문서:
                
                [템플릿 문서]
                {templates}
                
                [작성 예시]
                {examples}
                
                [관련 문서]
                {related}
                
                위 형식에 맞춰 답변을 생성하세요."""
            )
        ])
        
        # 체인 구성
        self.chain = self.prompt | self.llm
    
    def _format_documents(self, docs: List[Document], max_content_length: int = 500) -> str:
        """문서 리스트를 프롬프트에 넣을 문자열로 변환"""
        if not docs:
            return "없음"
        
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content[:max_content_length]
            if len(doc.page_content) > max_content_length:
                content += "..."
            formatted.append(f"{i}. 출처: {source}\n내용: {content}\n")
        
        return "\n".join(formatted)
    
    def _parse_answer(self, raw_answer: str) -> dict:
        """LLM 응답을 파싱하여 구조화"""
        parsed = {
            "summary": "",
            "details": "",
            "tips": ""
        }
        
        try:
            if "📌" in raw_answer:
                sections = raw_answer.split("📌")
                if len(sections) > 1:
                    summary_part = sections[1].split("📝")[0] if "📝" in sections[1] else sections[1]
                    parsed["summary"] = summary_part.replace("요약", "").replace(":", "").strip()
            
            if "📝" in raw_answer:
                details_part = raw_answer.split("📝")[1].split("💡")[0] if "💡" in raw_answer else raw_answer.split("📝")[1]
                parsed["details"] = details_part.replace("상세 설명", "").replace(":", "").strip()
            
            if "💡" in raw_answer:
                tips_part = raw_answer.split("💡")[1]
                parsed["tips"] = tips_part.replace("작성 팁 및 주의사항", "").replace(":", "").strip()
            
        except Exception as e:
            print(f"   ⚠️  답변 파싱 중 오류: {e}")
            parsed["summary"] = "답변을 생성했습니다."
            parsed["details"] = raw_answer
        
        return parsed
    
    def generate(self, state: AnswerState) -> AnswerState:
        """검색 결과를 바탕으로 구조화된 답변 생성"""
        question = state["question"]
        intent = state["intent"]
        document_type = state.get("document_type", "알 수 없음")
        urgency = state.get("urgency", "보통")
        
        try:
            # 문서 포맷팅
            templates_str = self._format_documents(state.get("templates", []))
            examples_str = self._format_documents(state.get("examples", []))
            related_str = self._format_documents(state.get("related", []))
            
            # LLM 호출
            response = self.chain.invoke({
                "question": question,
                "intent": intent,
                "document_type": document_type,
                "urgency": urgency,
                "templates": templates_str,
                "examples": examples_str,
                "related": related_str
            })
            
            raw_answer = response.content
            parsed = self._parse_answer(raw_answer)
            
            new_state = {
                **state,
                "answer": raw_answer,
                "summary": parsed["summary"],
                "tips": parsed["tips"]
            }
            
            return new_state
            
        except Exception as e:
            return {
                **state,
                "answer": "죄송합니다. 답변 생성 중 오류가 발생했습니다.",
                "summary": "오류 발생",
                "tips": ""
            }


# --- 테스트 코드 ---
if __name__ == "__main__":
    answer_gen = AnswerGenerator()
    
    from langchain_core.documents import Document
    
    test_state = {
        "question": "출장신청서 어떻게 작성하나요?",
        "intent": "템플릿_찾기",
        "document_type": "출장신청서",
        "urgency": "보통",
        "search_results": [
            Document(
                page_content="출장신청서는 출장 목적, 일정, 예상 경비를 기재하여 작성합니다.",
                metadata={"source": "출장신청서_양식.pdf"}
            )
        ],
        "templates": [
            Document(
                page_content="출장신청서 양식: 출장지, 출장기간, 출장목적, 예상경비 항목을 포함합니다.",
                metadata={"source": "출장신청서_템플릿.docx"}
            )
        ],
        "examples": [],
        "related": []
    }
    
    print("=" * 60)
    print("AnswerGenerator 테스트")
    print("=" * 60)
    
    result_state = answer_gen.generate(test_state)
    
    print(f"\n" + "=" * 60)
    print("생성된 답변")
    print("=" * 60)
    print(result_state["answer"])
    print("\n" + "✨ 테스트 완료!")