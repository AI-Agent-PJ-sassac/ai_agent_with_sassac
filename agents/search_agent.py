# agents/search_agent.py

import os
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_upstage import UpstageEmbeddings

# .env 파일 로드
load_dotenv()

# 벡터 DB 경로
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "solar-embedding-1-large"


# 워크플로우 상태 정의
class SearchState(TypedDict):
    """검색 Agent의 상태"""
    question: str
    intent: str
    document_type: str | None
    urgency: str
    search_results: List[Document]
    templates: List[Document]
    examples: List[Document]
    related: List[Document]


class SearchAgent:
    """고급 검색 기능을 제공하는 Agent"""
    
    def __init__(self, vectorstore_path: str = None):
        """
        Args:
            vectorstore_path: Chroma DB 경로 (None이면 자동으로 프로젝트 루트에서 찾음)
        """
        # 경로가 지정되지 않으면 프로젝트 루트의 chroma_db 사용
        if vectorstore_path is None:
            # 현재 파일(search_agent.py)의 위치에서 프로젝트 루트 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # agents/ -> 프로젝트 루트
            vectorstore_path = os.path.join(project_root, "chroma_db")
        
        # 임베딩 함수
        self.embedding_function = UpstageEmbeddings(model=EMBEDDING_MODEL)
        
        # Chroma DB 로드
        if os.path.exists(vectorstore_path):
            self.vectorstore = Chroma(
                persist_directory=vectorstore_path,
                embedding_function=self.embedding_function
            )
            print(f"✅ 벡터 DB 로드 완료: {vectorstore_path}")
        else:
            print(f"⚠️  벡터 DB를 찾을 수 없습니다: {vectorstore_path}")
            self.vectorstore = None
    
    def _classify_documents(self, docs: List[Document]) -> Dict[str, List[Document]]:
        """검색된 문서를 템플릿, 예시, 관련 문서로 분류"""
        templates = []
        examples = []
        related = []
        
        for doc in docs:
            source = doc.metadata.get("source", "").lower()
            
            if "템플릿" in source or "양식" in source or "template" in source:
                templates.append(doc)
            elif "예시" in source or "사례" in source or "example" in source:
                examples.append(doc)
            else:
                related.append(doc)
        
        return {
            "templates": templates,
            "examples": examples,
            "related": related
        }
    
    def _apply_filters(self, docs: List[Document], filters: Dict[str, Any]) -> List[Document]:
        """메타데이터 필터 적용"""
        filtered_docs = []
        
        for doc in docs:
            if filters.get("document_type"):
                doc_type = doc.metadata.get("document_type", "")
                source = doc.metadata.get("source", "")
                if (filters["document_type"].lower() not in doc_type.lower() and 
                    filters["document_type"].lower() not in source.lower()):
                    continue
            
            filtered_docs.append(doc)
        
        return filtered_docs if filtered_docs else docs
    
    def search_with_metadata(self, state: SearchState) -> SearchState:
        """질문 분석 결과를 바탕으로 고급 검색 수행"""
        question = state["question"]
        intent = state["intent"]
        document_type = state.get("document_type")
        urgency = state.get("urgency", "보통")
        
        print(f"\n🔍 검색 Agent 작동: '{question}'")
        print(f"   의도: {intent}, 문서유형: {document_type}, 긴급도: {urgency}")
        
        if not self.vectorstore:
            print("   ❌ 벡터 DB를 사용할 수 없습니다.")
            return {
                **state,
                "search_results": [],
                "templates": [],
                "examples": [],
                "related": []
            }
        
        try:
            # 1. 벡터 검색
            search_results = self.vectorstore.similarity_search(question, k=10)
            print(f"   📦 초기 검색 결과: {len(search_results)}개 문서")
            
            # 2. 메타데이터 필터 적용
            filters = {
                "document_type": document_type,
                "urgency": urgency
            }
            filtered_results = self._apply_filters(search_results, filters)
            print(f"   🎯 필터 적용 후: {len(filtered_results)}개 문서")
            
            # 3. 문서 분류
            classified = self._classify_documents(filtered_results)
            
            print(f"   📄 템플릿: {len(classified['templates'])}개")
            print(f"   💡 예시: {len(classified['examples'])}개")
            print(f"   🔗 관련 문서: {len(classified['related'])}개")
            
            # 4. 상태 업데이트
            new_state = {
                **state,
                "search_results": filtered_results[:5],
                "templates": classified["templates"][:3],
                "examples": classified["examples"][:3],
                "related": classified["related"][:3]
            }
            
            print(f"   ✅ 검색 완료")
            return new_state
            
        except Exception as e:
            print(f"   ❌ 검색 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return {
                **state,
                "search_results": [],
                "templates": [],
                "examples": [],
                "related": []
            }


# --- 테스트 코드 ---
if __name__ == "__main__":
    search_agent = SearchAgent()
    
    test_states = [
        {
            "question": "출장신청서 어떻게 작성하나요?",
            "intent": "템플릿_찾기",
            "document_type": "출장신청서",
            "urgency": "보통",
            "search_results": [],
            "templates": [],
            "examples": [],
            "related": []
        }
    ]
    
    print("=" * 60)
    print("SearchAgent 테스트")
    print("=" * 60)
    
    for i, test_state in enumerate(test_states, 1):
        print(f"\n[테스트 {i}]")
        result_state = search_agent.search_with_metadata(test_state)
        
        print(f"\n📊 최종 결과:")
        print(f"  - 검색 결과: {len(result_state.get('search_results', []))}개")
        print(f"  - 템플릿: {len(result_state.get('templates', []))}개")
        print(f"  - 예시: {len(result_state.get('examples', []))}개")
        print(f"  - 관련: {len(result_state.get('related', []))}개")
        
        if result_state.get('templates'):
            print(f"\n  템플릿 문서:")
            for doc in result_state['templates']:
                print(f"    - {doc.metadata.get('source', 'Unknown')}")
        
        print("-" * 60)
    
    print("\n✨ 모든 테스트 완료!")