from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from core.config import settings
from services.conversion_queue import conversion_queue
from schemas.job import EnqueueResponse
from schemas.upload import ResizeConfig

router = APIRouter(prefix="/api/upload", tags=["uploads"])


@router.post("/{zone_id}")
async def upload_and_enqueue(
    zone_id: str,
    files: List[UploadFile] = File(...),
    resize_config: ResizeConfig = Depends(ResizeConfig.as_form),
    output_path: str = Form(None),
) -> EnqueueResponse:
    """
    파일 업로드 및 변환 작업 큐 등록

    Args:
        zone_id: 존 ID
        files: 업로드된 HEIC 파일 리스트
        resize: 리사이징 설정 (use_resize, ratio, long_side_length)

    Returns:
        job_id, total 파일 수
    """
    # files 검증
    if not (files and isinstance(files, list) and len(files) > 0 and files[0].filename):
        raise HTTPException(status_code=400, detail="No files provided")

    # zone_id 검증
    zone = next((z for z in settings.zones if z.id == zone_id), None)
    if not zone:
        raise HTTPException(status_code=400, detail=f"Unknown zone_id: {zone_id}")

    # 출력 디렉토리 준비: output_path(사용자가 선택한 폴더명)가 있으면 사용, 없으면 기본 경로 사용
    base_dir = Path("/mPictures/Album/")
    base_filename = files[0].filename
    year = base_filename[:4]

    if output_path:
      # 사용자가 폴더를 선택한 경우: Album {year} / {선택한 폴더명}
      output_dir = base_dir / f"Album {year}" / output_path
    else:
      # 기본 경로: 파일명으로부터 위치 추정 (연도/월/일 구조)
      # 파일명형태: 20250427_140700 → Album 2025/04/27
      month = base_filename[4:6]
      day = base_filename[6:8]
      output_dir = base_dir / f"Album {year}" / month / day

    # 파일 bytes 수집 (메모리에서 처리)
    file_data = []
    for file in files:
        if not file.filename:
            continue
        content = await file.read()
        file_data.append(
            {
                "filename": file.filename,
                "bytes": content,
            }
        )

    # 작업 큐에 등록 (bytes 기반)
    job_id = await conversion_queue.enqueue_from_bytes(
        zone_id, zone.quality, file_data, output_dir, resize_config
    )

    return EnqueueResponse(job_id=job_id, total=len(file_data))
