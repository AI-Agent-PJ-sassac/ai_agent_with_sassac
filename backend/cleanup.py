
import os
import shutil
import time
import asyncio
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SessionCleanup")

def cleanup_old_sessions(data_dir: str = "data", db_dir: str = "chroma_db", max_age_seconds: int = 3600):
    """
    지정된 시간(초)보다 오래된 세션 데이터와 벡터 DB를 삭제합니다.
    기본값: 1시간 (3600초)
    """
    now = time.time()
    deleted_count = 0
    
    # 1. 문서 데이터 폴더 청소
    if os.path.exists(data_dir):
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            
            # .gitkeep 등은 건너뜀
            if item.startswith("."):
                continue
                
            # 디렉토리이고 (세션 폴더), 수정 시간이 오래된 경우
            if os.path.isdir(item_path):
                try:
                    mtime = os.path.getmtime(item_path)
                    if now - mtime > max_age_seconds:
                        shutil.rmtree(item_path)
                        logger.info(f"Deleted expired data session: {item}")
                        deleted_count += 1
                except Exception as e:
                    logger.error(f"Error cleaning data session {item}: {e}")

    # 2. 벡터 DB 폴더 청소
    if os.path.exists(db_dir):
        for item in os.listdir(db_dir):
            item_path = os.path.join(db_dir, item)
            
            # 기본 DB(default)가 아닌 경우에만 삭제 고려 (선택 사항)
            if item == "default" or item.startswith("."):
                continue
                
            if os.path.isdir(item_path):
                try:
                    mtime = os.path.getmtime(item_path)
                    if now - mtime > max_age_seconds:
                        shutil.rmtree(item_path)
                        logger.info(f"Deleted expired DB session: {item}")
                        deleted_count += 1
                except Exception as e:
                    logger.error(f"Error cleaning DB session {item}: {e}")
                    
    if deleted_count > 0:
        logger.info(f"Cleanup complete. Removed {deleted_count} expired sessions.")

async def periodic_cleanup_task(interval_seconds: int = 600, max_age_seconds: int = 3600):
    """
    주기적으로 청소 작업을 수행하는 백그라운드 태스크
    기본값: 10분마다 검사, 1시간 지난 데이터 삭제
    """
    while True:
        try:
            cleanup_old_sessions(max_age_seconds=max_age_seconds)
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}")
        
        # 다음 주기까지 대기
        await asyncio.sleep(interval_seconds)
