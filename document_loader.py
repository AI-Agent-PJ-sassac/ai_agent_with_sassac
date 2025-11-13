import os
from typing import List

# 1. Document 스키마
from langchain_core.documents import Document

# 2. Document Loaders
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

# 3. Text Splitter: 새로운 모듈 이름으로 임포트
# from langchain.text_splitter import RecursiveCharacterTextSplitter  <-- 이 줄을 삭제하고 아래로 대체
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_documents(file_path: str) -> List[Document]:
    """
    주어진 경로의 문서를 로드하고, 청크로 분할하며, 기본 메타데이터를 추가합니다.

    Args:
        file_path: 로드할 문서 파일의 경로 (PDF 또는 DOCX)

    Returns:
        List[Document]: 청크로 분할되고 메타데이터가 추가된 문서 리스트
    """
    # 1. 문서 로더 선택 및 로드
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif file_extension == ".docx":
        # Docx2txtLoader는 DOCX 파일을 텍스트로 변환하는 데 사용됩니다.
        loader = Docx2txtLoader(file_path)
    else:
        print(f"경고: 지원하지 않는 파일 형식입니다: {file_extension}")
        return []
    
    # 문서를 Document 객체 리스트로 로드
    documents = loader.load()

    # 2. 텍스트 청크 분할 (청크 크기 1000, 오버랩 200)
    # 이는 메모리 제약 및 검색 정확도를 위해 문서를 작은 단위로 나누는 과정입니다.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # 청크 분할된 Document 객체 리스트
    chunked_documents = text_splitter.split_documents(documents)
    
    # 3. 기본 메타데이터 추가
    file_name = os.path.basename(file_path)
    # 향후 메타데이터 자동 추출 시 사용할 기본 정보
    for doc in chunked_documents:
        doc.metadata["file_name"] = file_name
        doc.metadata["source"] = file_path
        # 문서유형, 작성일 등은 Phase 3에서 LLM으로 자동 추출 예정
        doc.metadata["문서유형"] = "미정"
        doc.metadata["작성연도"] = 0
        
    return chunked_documents

# --- 테스트 코드 (실제 파일 경로로 변경 필요) ---
if __name__ == "__main__":
    import os 

    # 1. 테스트할 파일 경로를 지정합니다. (10개 중 하나를 선택)
    # 반드시 해당 파일이 data/ 디렉토리에 존재해야 합니다.
    test_file_path = "data/1. 보고서_템플릿.docx"
    # test_file_path = "data/2. 출장신청서_양식.pdf" # PDF 파일 테스트 시

    if os.path.exists(test_file_path):
        print(f"--- {test_file_path} 로드 테스트 시작 ---")
        
        # load_documents 함수 호출
        test_docs = load_documents(test_file_path)
        
        if test_docs:
            print(f"성공: 파일 로드 및 분할 완료. 총 청크 수: {len(test_docs)}개")
            
            # 첫 번째 청크 내용 및 메타데이터 출력
            print("--- 첫 번째 청크 정보 ---")
            print(f"내용 (앞 100자): {test_docs[0].page_content[:100]}...")
            print(f"메타데이터: {test_docs[0].metadata}")
            print("-------------------------")
        else:
            print("경고: 문서는 존재하지만 로드된 청크가 0개입니다. 로더를 확인하세요.")
            
    else:
        print(f"오류: 테스트 파일이 없습니다. 경로를 확인하세요: {test_file_path}")