# workflow.py

"""
LangGraph를 사용한 멀티 에이전트 워크플로우 통합
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, List, Annotated, Optional
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

# Agent들 import (agents 패키지에서)
from agents.question_analyzer import QuestionAnalyzer
from agents.search_agent import SearchAgent
from agents.answer_generator import AnswerGenerator
from agents.verification_agent import VerificationAgent

# 결과 저장 함수
from save_results import save_to_txt, save_to_json, save_to_markdown
from vector_store import get_db_path

# .env 파일 로드
load_dotenv()


# 전체 워크플로우 상태 정의
class WorkflowState(TypedDict):
    """LangGraph 워크플로우의 전체 상태"""
    # 사용자 입력
    question: str
    
    # 질문 분석 결과
    intent: str
    document_type: Optional[str]
    urgency: str
    
    # 검색 결과
    search_results: List[Document]
    templates: List[Document]
    examples: List[Document]
    related: List[Document]
    
    # 답변 생성 결과
    answer: str
    summary: str
    tips: str
    
    # 검증 결과
    is_verified: bool
    warnings: List[str]


class HandoverWorkflow:
    """인수인계 AI 워크플로우 클래스"""
    
    def __init__(self, session_id: str = "default"):
        # 각 Agent 초기화
        self.question_analyzer = QuestionAnalyzer()
        
        # 세션별 벡터 DB 경로 설정
        db_path = get_db_path(session_id)
        self.search_agent = SearchAgent(vectorstore_path=db_path)
        
        self.answer_generator = AnswerGenerator()
        self.verification_agent = VerificationAgent()
        
        # 워크플로우 그래프 생성
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()
    
    def _create_workflow(self) -> StateGraph:
        """
        LangGraph 워크플로우를 생성합니다.
        
        Returns:
            컴파일 가능한 StateGraph
        """
        # 워크플로우 그래프 초기화
        workflow = StateGraph(WorkflowState)
        
        # 노드 추가 (각 Agent를 노드로)
        workflow.add_node("analyze", self.question_analyzer.analyze)
        workflow.add_node("search", self.search_agent.search_with_metadata)
        workflow.add_node("generate", self.answer_generator.generate)
        workflow.add_node("verify", self.verification_agent.verify)
        
        # 엣지 정의 (순차적 실행)
        workflow.add_edge("analyze", "search")
        workflow.add_edge("search", "generate")
        workflow.add_edge("generate", "verify")
        workflow.add_edge("verify", END)
        
        # 시작 노드 설정
        workflow.set_entry_point("analyze")
        
        return workflow
    
    def run(self, question: str, save_result: bool = True) -> WorkflowState:
        """
        워크플로우를 실행합니다.
        
        Args:
            question: 사용자 질문
            save_result: 결과를 파일로 저장할지 여부 (기본값: True)
            
        Returns:
            최종 상태 (답변 포함)
        """
        # 초기 상태
        initial_state = {
            "question": question,
            "intent": "",
            "document_type": None,
            "urgency": "보통",
            "search_results": [],
            "templates": [],
            "examples": [],
            "related": [],
            "answer": "",
            "summary": "",
            "tips": "",
            "is_verified": False,
            "warnings": []
        }
        
        try:
            # 워크플로우 실행
            final_state = self.app.invoke(initial_state)
            
            # 결과 저장 (조용히)
            if save_result and final_state.get("answer"):
                try:
                    save_to_txt(final_state, output_dir="results")
                    save_to_json(final_state, output_dir="results")
                    save_to_markdown(final_state, output_dir="results")
                except Exception as e:
                    pass
            
            return final_state
            
        except Exception as e:
            print(f"\n❌ 워크플로우 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                **initial_state,
                "answer": "죄송합니다. 처리 중 오류가 발생했습니다.",
                "summary": "오류 발생",
                "warnings": [str(e)]
            }


def display_result(result: WorkflowState):
    """
    워크플로우 결과를 보기 좋게 출력합니다.
    
    Args:
        result: 워크플로우 실행 결과
    """
    print("\n" + "=" * 60)
    print("📋 최종 결과")
    print("=" * 60)
    
    print(f"\n❓ 질문: {result['question']}")
    print(f"🎯 의도: {result['intent']}")
    print(f"📄 문서 유형: {result.get('document_type', 'N/A')}")
    print(f"⏰ 긴급도: {result['urgency']}")
    
    print(f"\n" + "-" * 60)
    print("💬 답변")
    print("-" * 60)
    print(result['answer'])
    
    # 경고 사항
    if result.get('warnings'):
        print(f"\n" + "-" * 60)
        print("⚠️  경고 사항")
        print("-" * 60)
        for warning in result['warnings']:
            print(f"  {warning}")
    
    # 검색 결과 통계
    print(f"\n" + "-" * 60)
    print("📊 검색 통계")
    print("-" * 60)
    print(f"  검색 결과: {len(result.get('search_results', []))}개")
    print(f"  템플릿: {len(result.get('templates', []))}개")
    print(f"  예시: {len(result.get('examples', []))}개")
    print(f"  관련 문서: {len(result.get('related', []))}개")
    
    print("\n" + "=" * 60)


# --- 테스트 코드 ---
if __name__ == "__main__":
    # 워크플로우 초기화
    workflow = HandoverWorkflow()
    
    # 테스트 질문들
    test_questions = [
        "출장신청서 어떻게 작성하나요?",
        "예산 신청서 급해요",
        "보고서 작성 시 주의사항은?",
    ]
    
    print("=" * 60)
    print("HandoverWorkflow 통합 테스트")
    print("=" * 60)
    
    all_results = []  # 모든 결과 저장용
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n\n{'#' * 60}")
        print(f"# 테스트 {i}/{len(test_questions)}")
        print(f"{'#' * 60}\n")
        
        # 워크플로우 실행 (자동 저장 활성화)
        result = workflow.run(question, save_result=True)
        all_results.append(result)
        
        # 결과 출력
        display_result(result)
        
        # 구분선
        if i < len(test_questions):
            print("\n\n" + "=" * 60)
            print("다음 테스트로 이동...")
            print("=" * 60)
    
    print("\n\n" + "=" * 60)
    print("✨ 모든 테스트 완료!")
    print(f"📁 결과는 'results/' 폴더에 저장되었습니다.")
    print("=" * 60)