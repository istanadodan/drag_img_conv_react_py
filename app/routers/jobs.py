from pathlib import Path
from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.responses import FileResponse
from services.conversion_queue import conversion_queue
from services.websocket_manager import websocket_manager
from schemas.job import JobStatusResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}")
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    작업 상태 조회 (폴링용)

    Args:
        job_id: 작업 ID

    Returns:
        현재 작업 상태
    """
    job_state = conversion_queue.get_state(job_id)
    if not job_state:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    return JobStatusResponse(
        job_id=job_state.job_id,
        zone_id=job_state.zone_id,
        quality=job_state.quality,
        total=job_state.total,
        done=job_state.done,
        state=job_state.state,
        results=[r.model_dump() for r in job_state.results],
    )


@router.get("/{job_id}/file/{filename}")
async def download_converted_file(job_id: str, filename: str):
    """
    변환된 파일 다운로드

    Args:
        job_id: 작업 ID
        filename: 다운로드할 파일명 (예: IMG001_q85.jpg)

    Returns:
        파일 바이너리 (Blob)
    """
    job_state = conversion_queue.get_state(job_id)
    if not job_state:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # 파일 경로 조회 (upload_dir에서 찾음)
    upload_dir = Path("/tmp/heic_uploads")
    file_path = upload_dir / filename

    # 경로 검증 (보안: 상위 디렉토리 접근 방지)
    try:
        file_path.resolve().relative_to(upload_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid file path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket 엔드포인트: 실시간 작업 진행 상황 스트림

    연결 후 JobUpdate 메시지를 수신

    Args:
        job_id: 작업 ID
    """
    # job_id 검증
    job_state = conversion_queue.get_state(job_id)
    if not job_state:
        await websocket.close(code=4004, reason=f"Job not found: {job_id}")
        return

    # WebSocket 연결 등록
    logger.info(f"ws connection try id: {job_id}")
    await websocket_manager.connect(job_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        websocket_manager.disconnect(job_id, websocket)
