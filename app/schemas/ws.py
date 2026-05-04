from typing import Optional
from pydantic import BaseModel


class FileResult(BaseModel):
    """파일 변환 결과"""
    file: str
    status: str  # "converted", "skipped", "failed"
    output: Optional[str] = None
    error: Optional[str] = None


class JobUpdate(BaseModel):
    """WebSocket 브로드캐스트 메시지"""
    job_id: str
    done: int
    total: int
    state: str  # "pending", "running", "done"
    latest: Optional[FileResult] = None
    results: Optional[list[FileResult]] = None  # 작업 완료 시 전체 결과
