# vector_store.py

import os
from dotenv import load_dotenv
from typing import List, Optional

# LangChain 코어 및 커뮤니티 모듈
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

# Upstage 임베딩 함수 사용
from langchain_upstage import UpstageEmbeddings

# 이전 단계에서 만든 문서 로더 import
from document_loader import load_documents 

# .env 파일에서 환경 변수 로드
load_dotenv() 

# 벡터 DB 저장 경로
CHROMA_PATH = "chroma_db"

# 🔥 일관된 임베딩 모델명 사용
EMBEDDING_MODEL = "solar-embedding-1-large"  # 또는 "solar-embedding-1-small"


def get_embedding_function():
    """
    Upstage 임베딩 함수를 반환합니다.
    모델명을 한 곳에서 관리하여 일관성 유지.
    """
    return UpstageEmbeddings(model=EMBEDDING_MODEL)


def create_vectorstore(documents: List[Document]) -> Optional[Chroma]:
    """
    문서 리스트를 임베딩하여 Chroma 벡터 DB에 저장합니다.
    
    Args:
        documents: 임베딩할 Document 객체 리스트
        
    Returns:
        생성된 Chroma vectorstore 또는 None
    """
    if not documents:
        print("❌ 문서 리스트가 비어 있어 벡터 DB를 생성할 수 없습니다.")
        return None

    embedding_function = get_embedding_function()
    
    # Chroma에 문서 임베딩 저장
    print(f"📦 총 {len(documents)}개 청크를 벡터 DB에 저장 중...")
    try:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embedding_function,
            persist_directory=CHROMA_PATH  # 자동으로 디스크에 저장됨
        )
        print(f"✅ 벡터 DB 생성 및 '{CHROMA_PATH}'에 저장 완료.")
        return vectorstore
    except Exception as e:
        print(f"❌ 벡터 DB 생성 중 오류 발생: {e}")
        return None


def get_vectorstore() -> Optional[Chroma]:
    """
    기존에 저장된 벡터 DB를 로드합니다.
    
    Returns:
        로드된 Chroma vectorstore 또는 None
    """
    if not os.path.exists(CHROMA_PATH):
        print(f"⚠️  벡터 DB 경로 '{CHROMA_PATH}'를 찾을 수 없습니다. 먼저 생성해야 합니다.")
        return None

    try:
        embedding_function = get_embedding_function()
        vectorstore = Chroma(
            persist_directory=CHROMA_PATH, 
            embedding_function=embedding_function
        )
        print(f"✅ 벡터 DB '{CHROMA_PATH}' 로드 완료.")
        return vectorstore
    except Exception as e:
        print(f"❌ 벡터 DB 로드 중 오류 발생: {e}")
        return None


def search_documents(query: str, k: int = 5) -> List[Document]:
    """
    쿼리와 유사한 문서를 검색합니다.
    
    Args:
        query: 검색할 질문/키워드
        k: 반환할 문서 개수 (기본값: 5)
        
    Returns:
        유사한 문서 리스트
    """
    vectorstore = get_vectorstore()
    if vectorstore is None:
        print("❌ 벡터 DB가 로드되지 않아 검색할 수 없습니다.")
        return []
    
    try:
        results = vectorstore.similarity_search(query, k=k)
        print(f"🔍 '{query}' 검색 결과: {len(results)}개 문서 발견")
        return results
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {e}")
        return []


def search_with_score(query: str, k: int = 5) -> List[tuple]:
    """
    쿼리와 유사한 문서를 유사도 점수와 함께 반환합니다.
    
    Args:
        query: 검색할 질문/키워드
        k: 반환할 문서 개수
        
    Returns:
        (Document, score) 튜플의 리스트
    """
    vectorstore = get_vectorstore()
    if vectorstore is None:
        print("❌ 벡터 DB가 로드되지 않아 검색할 수 없습니다.")
        return []
    
    try:
        results = vectorstore.similarity_search_with_score(query, k=k)
        print(f"🔍 '{query}' 검색 결과: {len(results)}개 문서 발견 (점수 포함)")
        return results
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {e}")
        return []


# --- 테스트 및 DB 생성 실행 (10개 파일 전체 로드) ---
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 벡터 DB 생성 프로세스 시작")
    print("=" * 60)
    
    # 1. 문서 로드 (10개 파일 경로 전체 사용)
    document_paths = [
        "data/1. 보고서_템플릿.docx",
        "data/2. 출장신청서_양식.pdf",
        "data/3. 출장신청서_홍길동_예시.pdf",
        "data/4. 예산신청서_간소화_2024.docx",
        "data/5. 예산_집행_보고서_작성_팁.pdf",
        "data/6. 인사_평가_가이드라인.docx",
        "data/7. 장비구매_절차_안내.pdf",
        "data/8. 보도자료_작성_예시_2023.pdf",
        "data/9. 내부결재_기안서_양식.docx",
        "data/10. 민원처리_응대_FAQ.pdf",
    ]

    all_documents = []
    
    print("\n📂 문서 로드 시작...")
    print("-" * 60)
    for path in document_paths:
        if os.path.exists(path):
            print(f"  📄 로딩 중: {path}")
            loaded = load_documents(path)
            all_documents.extend(loaded)
            print(f"     ✓ {len(loaded)}개 청크 로드됨")
        else:
            print(f"  ⚠️  파일 없음: {path}")

    print("-" * 60)
    print(f"📊 로드 완료. 총 청크 수: {len(all_documents)}개\n")
    
    # 2. 벡터 스토어 생성
    if all_documents:
        vectorstore = create_vectorstore(all_documents)
        
        if vectorstore:
            print("\n" + "=" * 60)
            print("🎉 벡터 DB 생성 성공!")
            print("=" * 60)
            
            # 3. 간단한 검색 테스트
            print("\n🧪 검색 기능 테스트 중...")
            test_query = "출장신청서 작성 방법"
            test_results = search_documents(test_query, k=3)
            
            if test_results:
                print(f"\n검색 쿼리: '{test_query}'")
                print("검색 결과:")
                for i, doc in enumerate(test_results, 1):
                    print(f"\n[{i}] {doc.metadata.get('source', 'Unknown')}")
                    print(f"    내용: {doc.page_content[:100]}...")
            
            print("\n✨ 모든 프로세스 완료!")
        else:
            print("\n❌ 벡터 DB 생성 실패")
    else:
        print("❌ 로딩된 문서가 없어 벡터 DB 생성을 건너뛰었습니다.")
        print("   파일 경로 및 document_loader.py를 확인해 주세요.")
    
    print("=" * 60)