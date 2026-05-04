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

    # 파일명으로 부터 저장될 위치를 추정한다.
    # 파일명형태: 20250427_140700
    # 연도값을 가져와 "D:\mPictures\Album\Album 연도" 폴더를 찾는다.
    # 그리고 월과 일을 가져와 그 하위에 /월/일 형태의 폴더를 만들고 그 위치를 기준으로 한다.
    base_filename = files[0].filename
    year = base_filename[:4]
    month_day = f"{base_filename[4:6]}/{base_filename[6:8]}"

    # 출력 디렉토리 준비
    output_dir = Path("/mPictures/Album/") / f"Album {year}" / month_day

    # 파일 bytes 수집 (메모리에서 처리)
    file_data = []
    for file in files:
        if not file.filename:
            continue
        content = await file.read()
        file_data.append({
            "filename": file.filename,
            "bytes": content,
        })

    # 작업 큐에 등록 (bytes 기반)
    job_id = await conversion_queue.enqueue_from_bytes(
        zone_id, zone.quality, file_data, output_dir, resize_config
    )

    return EnqueueResponse(job_id=job_id, total=len(file_data))
