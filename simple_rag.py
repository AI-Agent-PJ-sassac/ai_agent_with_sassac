# simple_rag.py
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

# LangChain LLM 모듈
from langchain_upstage import ChatUpstage

# 🔥 최신 LangChain - 핵심 모듈만 사용
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 이전 단계에서 만든 벡터 DB 로드 함수
from vector_store import get_vectorstore

# 결과 저장 함수
from save_results import save_to_txt, save_to_json, save_to_markdown, save_all_results

# .env 파일 로드
load_dotenv()


def format_docs(docs):
    """문서를 하나의 문자열로 포맷팅"""
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_chain():
    """
    LCEL(LangChain Expression Language)을 사용한 간단한 RAG 체인
    
    Returns:
        RAG 체인 또는 None
    """
    # 1. 벡터 스토어 로드
    vectorstore = get_vectorstore()
    if vectorstore is None:
        print("❌ 벡터 DB를 로드할 수 없어 RAG 체인 생성 실패")
        return None
    
    # 2. LLM 설정
    llm = ChatUpstage(
        model="solar-pro",  # 또는 "solar-1-mini-chat"
        temperature=0
    )
    
    # 3. Retriever 설정
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}  # 상위 3개 문서 검색
    )
    
    # 4. 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_template("""당신은 공공기관 업무 지원 AI 어시스턴트입니다.
주어진 문서를 바탕으로 질문에 정확하고 친절하게 답변해주세요.

답변 형식:
1. 📌 간단한 요약 (한 줄)
2. 📝 상세 설명
3. ⚠️ 주의사항 (있다면)

참고 문서:
{context}

질문: {question}

답변:""")
    
    # 5. LCEL로 체인 구성
    try:
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print("✅ RAG 체인 생성 완료 (LCEL)")
        return rag_chain
    except Exception as e:
        print(f"❌ RAG 체인 생성 중 오류: {e}")
        return None


def ask_question(question: str) -> Dict[str, Any]:
    """
    RAG 시스템에 질문하고 답변을 받습니다.
    
    Args:
        question: 질문 내용
        
    Returns:
        답변 결과 딕셔너리
    """
    print("\n" + "=" * 60)
    print(f"❓ 질문: {question}")
    print("=" * 60)
    
    # RAG 체인 생성
    rag_chain = create_rag_chain()
    if rag_chain is None:
        return {"error": "RAG 체인 생성 실패"}
    
    try:
        # 질문 처리
        answer = rag_chain.invoke(question)
        
        print(f"\n💡 답변:\n{answer}")
        
        # 검색된 문서도 함께 반환하기 위해 별도 검색
        vectorstore = get_vectorstore()
        if vectorstore:
            source_docs = vectorstore.similarity_search(question, k=3)
            print(f"\n📚 참조 문서: {len(source_docs)}개")
            
            return {
                "question": question,
                "answer": answer,
                "source_documents": source_docs
            }
        else:
            return {
                "question": question,
                "answer": answer,
                "source_documents": []
            }
            
    except Exception as e:
        print(f"❌ 질문 처리 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# --- 테스트 실행 ---
if __name__ == "__main__":
    print("🚀 Simple RAG 테스트 시작\n")
    
    # 테스트 질문들
    test_questions = [
        "출장신청서 어떻게 작성하나요?",
        "예산 신청 절차가 어떻게 되나요?",
        "보고서 작성 시 주의사항은?",
    ]
    
    print("=" * 60)
    print("📝 테스트 질문 목록:")
    for i, q in enumerate(test_questions, 1):
        print(f"  {i}. {q}")
    print("=" * 60)
    
    # 결과를 저장할 리스트
    all_results = []
    
    # 각 질문에 대해 RAG 실행
    for question in test_questions:
        result = ask_question(question)
        
        # 결과 리스트에 추가
        if "error" not in result:
            all_results.append(result)
        
        # 출처 문서 상세 정보
        if "source_documents" in result and result["source_documents"]:
            print("\n📄 출처 문서 상세:")
            for i, doc in enumerate(result["source_documents"], 1):
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "N/A")
                print(f"\n  [{i}] {source} (페이지: {page})")
                print(f"      내용: {doc.page_content[:150]}...")
        
        print("\n" + "-" * 60 + "\n")
    
    print("✨ 모든 테스트 완료!")
    
    # 🔥 결과 저장
    if all_results:
        print("\n" + "=" * 60)
        print("💾 결과 저장 중...")
        print("=" * 60)
        
        # 전체 결과 저장
        saved_files = save_all_results(all_results, output_dir="results_rag")
        
        # 개별 결과도 각 형식으로 저장 (첫 번째 결과만 예시)
        if all_results:
            print("\n📁 첫 번째 결과를 여러 형식으로 저장:")
            save_to_txt(all_results[0], output_dir="results")
            save_to_json(all_results[0], output_dir="results")
            save_to_markdown(all_results[0], output_dir="results")
        
        print("\n🎉 모든 결과가 'results/' 디렉토리에 저장되었습니다!")
    else:
        print("\n⚠️  저장할 결과가 없습니다.")