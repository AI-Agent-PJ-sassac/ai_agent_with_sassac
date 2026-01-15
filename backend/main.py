
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os
from typing import List, Dict, Optional

# 기존 로직 임포트 (경로 이동에 따라 수정)
from workflow import HandoverWorkflow
from vector_store import load_documents, create_vectorstore, get_vectorstore, rebuild_database, get_db_path
from cleanup import periodic_cleanup_task
import asyncio
# 필요한 경우 추가 임포트

app = FastAPI(title="공공기관 인수인계 AI Agent API")

# 세션별 워크플로우 인스턴스 관리
active_workflows: Dict[str, HandoverWorkflow] = {}

def get_session_workflow(session_id: str) -> HandoverWorkflow:
    """세션 ID에 해당하는 워크플로우 반환 (없으면 생성)"""
    if session_id not in active_workflows:
        print(f"🆕 New session started: {session_id}")
        active_workflows[session_id] = HandoverWorkflow(session_id=session_id)
    return active_workflows[session_id]

class ChatRequest(BaseModel):
    question: str

@app.on_event("startup")
async def startup_event():
    # 백그라운드 청소 태스크 시작 (10분마다 돌면서 1시간 지난 파일 삭제)
    asyncio.create_task(periodic_cleanup_task(interval_seconds=600, max_age_seconds=3600))


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(request: ChatRequest, x_session_id: Optional[str] = Header("default", alias="X-Session-ID")):
    workflow = get_session_workflow(x_session_id)
    
    try:
        result = workflow.run(request.question, save_result=True)
        return {
            "answer": result['answer'],
            "warnings": result.get('warnings', []),
            "search_results": result.get('search_results', []),
            "templates": result.get('templates', []),
            "examples": result.get('examples', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...), 
    x_session_id: Optional[str] = Header("default", alias="X-Session-ID")
):
    try:
        # 1. 파일 저장 (세션별 폴더 격리)
        # 예: backend/data/{session_id}/filename
        base_upload_dir = "data"
        if not x_session_id or x_session_id == "default":
             session_dir = base_upload_dir
        else:
             session_dir = os.path.join(base_upload_dir, x_session_id)
             
        os.makedirs(session_dir, exist_ok=True)
        file_path = os.path.join(session_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. 문서 로드 및 청킹
        documents = load_documents(file_path)
        if not documents:
             raise HTTPException(status_code=400, detail="Failed to load documents from file")

        # 3. Vector DB 업데이트 (세션 ID 전달)
        vectorstore = get_vectorstore(session_id=x_session_id)
        if vectorstore:
            vectorstore.add_documents(documents)
            message = f"Successfully added {len(documents)} chunks to Vector DB ({x_session_id})."
        else:
            # DB가 없으면 새로 생성
            create_vectorstore(documents, session_id=x_session_id)
            message = f"Created new Vector DB with {len(documents)} chunks ({x_session_id})."
            
            # 워크플로우 재생성 (DB 연결 갱신 등 필요 시)
            # HandoverWorkflow는 init 시 DB 경로를 잡으므로, 
            # 이미 생성된 인스턴스는 문제 없지만, 확실히 하기 위해 재생성 가능
            active_workflows[x_session_id] = HandoverWorkflow(session_id=x_session_id)

        return {"filename": file.filename, "message": message, "chunks": len(documents)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/db/refresh")
async def refresh_db(x_session_id: Optional[str] = Header("default", alias="X-Session-ID")):
    try:
        # 세션별 데이터 폴더 경로
        base_upload_dir = "data"
        if not x_session_id or x_session_id == "default":
             data_dir = base_upload_dir
        else:
             data_dir = os.path.join(base_upload_dir, x_session_id)

        # DB 재생성
        result = rebuild_database(data_dir=data_dir, session_id=x_session_id)
        
        if result["success"]:
             # 워크플로우 재초기화
            active_workflows[x_session_id] = HandoverWorkflow(session_id=x_session_id)
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

