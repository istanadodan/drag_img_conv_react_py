import asyncio
import uuid
import os
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from services.converter import image_format_converter, ResizeConfig
from services.websocket_manager import websocket_manager
from schemas.ws import FileResult, JobUpdate
from schemas.upload import ResizeConfig

class FileData(BaseModel):
    filename: str
    bytes: bytes


class ConversionJobState(BaseModel):
    """변환 작업 상태"""

    job_id: str
    zone_id: str
    quality: int
    resize: dict | None = None  # 리사이징 설정
    total: int
    done: int = 0
    state: str = "pending"  # "pending", "running", "done"
    results: List[FileResult] = []


class ConversionQueue:
    """HEIC 변환 작업 큐 관리"""

    def __init__(self, max_workers: int = os.cpu_count() or 4):
        self.jobs: Dict[str, ConversionJobState] = {}
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="heic_converter"
        )

    async def enqueue(
        self,
        zone_id: str,
        quality: int,
        file_paths: List[Path],
        resize_config: ResizeConfig,
    ) -> str:
        """
        변환 작업을 큐에 등록하고 job_id 반환 (파일 경로 기반)

        Args:
            zone_id: 존 ID
            quality: JPEG 품질
            file_paths: HEIC 파일 경로 리스트
            resize: 리사이징 설정 (선택사항)

        Returns:
            job_id: 생성된 작업 ID
        """
        job_id = str(uuid.uuid4())

        job_state = ConversionJobState(
            job_id=job_id,
            zone_id=zone_id,
            quality=quality,
            resize=resize_config.model_dump(),
            total=len(file_paths),
        )
        self.jobs[job_id] = job_state

        # 백그라운드 작업 실행
        asyncio.create_task(self._process(job_id, quality, file_paths, resize_config))

        return job_id

    async def enqueue_from_bytes(
        self,
        zone_id: str,
        quality: int,
        file_data_list: List[Dict],
        output_dir: Path,
        resize_config: ResizeConfig,
    ) -> str:
        """
        변환 작업을 큐에 등록 (bytes 기반 - 메모리에서 처리)

        Args:
            zone_id: 존 ID
            quality: JPEG 품질
            file_data_list: [{"filename": str, "bytes": bytes}, ...] 리스트
            output_dir: 출력 디렉토리
            resize_config: 리사이징 설정

        Returns:
            job_id: 생성된 작업 ID
        """
        job_id = str(uuid.uuid4())

        job_state = ConversionJobState(
            job_id=job_id,
            zone_id=zone_id,
            quality=quality,
            resize=resize_config.model_dump(),
            total=len(file_data_list),
        )
        self.jobs[job_id] = job_state

        # 백그라운드 작업 실행
        asyncio.create_task(
            self._process_from_bytes(job_id, quality, file_data_list, output_dir, resize_config)
        )

        return job_id

    async def _process(
        self,
        job_id: str,
        quality: int,
        file_paths: List[Path],
        resize_config: ResizeConfig,
    ):
        """작업 처리 (백그라운드 - 병렬 처리)"""
        job_state = self.jobs[job_id]
        job_state.state = "running"

        await websocket_manager.broadcast(
            job_id,
            JobUpdate(
                job_id=job_id,
                done=0,
                total=job_state.total,
                state="running",
                latest=None,
            ),
        )

        loop = asyncio.get_event_loop()

        # 모든 파일을 병렬로 처리
        async def process_file(file_path: Path):
            try:
                result = await loop.run_in_executor(
                    self.executor,
                    image_format_converter.convert_with_suffix,
                    file_path,
                    quality,
                    resize_config,
                    True,  # keep_origin
                )
                return FileResult(
                    file=file_path.name,
                    status=result["status"],
                    output=result["output"],
                    error=result.get("error"),
                )
            except Exception as e:
                return FileResult(
                    file=file_path.name,
                    status="failed",
                    output=None,
                    error=str(e),
                )

        # gather()로 모든 파일을 동시에 처리
        results = await asyncio.gather(*[process_file(fp) for fp in file_paths])

        # 결과를 하나씩 처리하며 WebSocket 브로드캐스트
        for file_result in results:
            job_state.results.append(file_result)
            job_state.done += 1

            await websocket_manager.broadcast(
                job_id,
                JobUpdate(
                    job_id=job_id,
                    done=job_state.done,
                    total=job_state.total,
                    state="running",
                    latest=file_result,
                ),
            )

        job_state.state = "done"
        await websocket_manager.broadcast(
            job_id,
            JobUpdate(
                job_id=job_id,
                done=job_state.done,
                total=job_state.total,
                state="done",
                latest=None,
                results=job_state.results,
            ),
        )

    async def _process_from_bytes(
        self,
        job_id: str,
        quality: int,
        file_data_list: List[Dict],
        output_dir: Path,
        resize_config: ResizeConfig,
    ):
        """bytes 기반 작업 처리 (백그라운드 - 병렬 처리)"""
        job_state = self.jobs[job_id]
        job_state.state = "running"

        await websocket_manager.broadcast(
            job_id,
            JobUpdate(
                job_id=job_id,
                done=0,
                total=job_state.total,
                state="running",
                latest=None,
            ),
        )

        loop = asyncio.get_event_loop()

        # 모든 파일을 병렬로 처리
        async def process_file_bytes(file_data: Dict):
            try:
                result = await loop.run_in_executor(
                    self.executor,
                    image_format_converter.convert_from_bytes,
                    file_data["bytes"],
                    file_data["filename"],
                    output_dir,
                    quality,
                    resize_config,
                )
                return FileResult(
                    file=file_data["filename"],
                    status=result["status"],
                    output=result["output"],
                    error=result.get("error"),
                )
            except Exception as e:
                return FileResult(
                    file=file_data["filename"],
                    status="failed",
                    output=None,
                    error=str(e),
                )

        # gather()로 모든 파일을 동시에 처리
        results = await asyncio.gather(*[process_file_bytes(fd) for fd in file_data_list])

        # 결과를 하나씩 처리하며 WebSocket 브로드캐스트
        for file_result in results:
            job_state.results.append(file_result)
            job_state.done += 1

            await websocket_manager.broadcast(
                job_id,
                JobUpdate(
                    job_id=job_id,
                    done=job_state.done,
                    total=job_state.total,
                    state="running",
                    latest=file_result,
                ),
            )

        job_state.state = "done"
        await websocket_manager.broadcast(
            job_id,
            JobUpdate(
                job_id=job_id,
                done=job_state.done,
                total=job_state.total,
                state="done",
                latest=None,
                results=job_state.results,
            ),
        )

    def get_state(self, job_id: str) -> ConversionJobState | None:
        """작업 상태 조회"""
        return self.jobs.get(job_id)


conversion_queue = ConversionQueue(max_workers=4)
