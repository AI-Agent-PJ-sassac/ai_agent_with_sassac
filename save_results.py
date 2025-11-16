# save_results.py
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


def save_to_txt(result: Dict[str, Any], output_dir: str = "results") -> str:
    """
    RAG 결과를 텍스트 파일로 저장
    
    Args:
        result: ask_question 함수의 반환값
        output_dir: 저장할 디렉토리
        
    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 파일명 생성 (타임스탬프 포함)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rag_result_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # 텍스트 파일 작성
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("RAG 시스템 답변 결과\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"📅 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("❓ 질문\n")
        f.write("-" * 80 + "\n")
        f.write(f"{result.get('question', 'N/A')}\n\n")
        
        f.write("💡 답변\n")
        f.write("-" * 80 + "\n")
        f.write(f"{result.get('answer', 'N/A')}\n\n")
        
        # 출처 문서
        source_docs = result.get('source_documents', [])
        if source_docs:
            f.write("📚 참조 문서\n")
            f.write("-" * 80 + "\n")
            for i, doc in enumerate(source_docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                f.write(f"\n[{i}] {source} (페이지: {page})\n")
                f.write(f"내용: {doc.page_content[:200]}...\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    return filepath


def save_to_json(result: Dict[str, Any], output_dir: str = "results") -> str:
    """
    RAG 결과를 JSON 파일로 저장
    
    Args:
        result: ask_question 함수의 반환값
        output_dir: 저장할 디렉토리
        
    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rag_result_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # JSON 직렬화 가능한 형태로 변환
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "question": result.get("question", ""),
        "answer": result.get("answer", ""),
        "source_documents": []
    }
    
    # 문서 정보 추가
    for doc in result.get("source_documents", []):
        json_data["source_documents"].append({
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "N/A"),
            "content": doc.page_content
        })
    
    # JSON 파일 저장
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return filepath


def save_to_markdown(result: Dict[str, Any], output_dir: str = "results") -> str:
    """
    RAG 결과를 Markdown 파일로 저장
    
    Args:
        result: ask_question 함수의 반환값
        output_dir: 저장할 디렉토리
        
    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rag_result_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Markdown 파일 작성
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# RAG 시스템 답변 결과\n\n")
        f.write(f"📅 **생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("## ❓ 질문\n\n")
        f.write(f"{result.get('question', 'N/A')}\n\n")
        
        f.write("## 💡 답변\n\n")
        f.write(f"{result.get('answer', 'N/A')}\n\n")
        
        # 출처 문서
        source_docs = result.get('source_documents', [])
        if source_docs:
            f.write("## 📚 참조 문서\n\n")
            for i, doc in enumerate(source_docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                f.write(f"### [{i}] {source}\n\n")
                f.write(f"- **페이지**: {page}\n")
                f.write(f"- **내용**:\n\n")
                f.write(f"```\n{doc.page_content[:300]}...\n```\n\n")
        
        f.write("---\n")
    
    return filepath


def save_all_results(results: List[Dict[str, Any]], output_dir: str = "results") -> Dict[str, str]:
    """
    여러 RAG 결과를 하나의 파일로 저장
    
    Args:
        results: ask_question 결과 리스트
        output_dir: 저장할 디렉토리
        
    Returns:
        저장된 파일 경로들
    """
    # 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 전체 결과를 하나의 텍스트 파일로
    txt_file = os.path.join(output_dir, f"all_results_{timestamp}.txt")
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("RAG 시스템 전체 테스트 결과\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"📅 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"📊 총 질문 수: {len(results)}개\n\n")
        
        for i, result in enumerate(results, 1):
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"질문 #{i}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"❓ 질문: {result.get('question', 'N/A')}\n\n")
            f.write(f"💡 답변:\n{result.get('answer', 'N/A')}\n\n")
            
            source_docs = result.get('source_documents', [])
            if source_docs:
                f.write(f"📚 참조 문서: {len(source_docs)}개\n")
                for j, doc in enumerate(source_docs, 1):
                    source = doc.metadata.get('source', 'Unknown')
                    f.write(f"  [{j}] {source}\n")
            f.write("\n")
    
    # 2. JSON 파일로도 저장
    json_file = os.path.join(output_dir, f"all_results_{timestamp}.json")
    json_data = []
    for result in results:
        item = {
            "question": result.get("question", ""),
            "answer": result.get("answer", ""),
            "num_sources": len(result.get("source_documents", []))
        }
        json_data.append(item)
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(results),
            "results": json_data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 전체 결과가 저장되었습니다:")
    print(f"   - {txt_file}")
    print(f"   - {json_file}")
    
    return {
        "txt": txt_file,
        "json": json_file
    }


# 간단한 사용 예시
if __name__ == "__main__":
    # 테스트 데이터
    test_result = {
        "question": "출장신청서 어떻게 작성하나요?",
        "answer": "출장신청서는 다음과 같이 작성합니다...",
        "source_documents": []
    }
    
    # 각 형식으로 저장 테스트
    save_to_txt(test_result)
    save_to_json(test_result)
    save_to_markdown(test_result)
    
    print("\n✨ 저장 기능 테스트 완료!")