from typing import List, Optional
from pydantic import BaseModel


class ResizeInfo(BaseModel):
    """리사이징 정보"""
    mode: str  # "ratio" 또는 "fixed"
    width: Optional[int] = None
    height: Optional[int] = None


class EnqueueResponse(BaseModel):
    """POST /api/upload/{zone_id} 응답"""
    job_id: str
    total: int


class JobStatusResponse(BaseModel):
    """GET /api/jobs/{job_id} 응답"""
    job_id: str
    zone_id: str
    quality: int
    resize: Optional[ResizeInfo] = None
    total: int
    done: int
    state: str  # "pending", "running", "done"
    results: List[dict] = []
