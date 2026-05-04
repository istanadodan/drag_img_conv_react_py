from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from core.config import settings
from routers import zones, uploads, jobs
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 라이프사이클 관리"""
    logger.info(f"HEIC to JPG Converter API 시작 - max_workers: {settings.max_workers}")
    yield
    logger.info("HEIC to JPG Converter API 종료")


def create_app() -> FastAPI:
    """FastAPI 앱 생성"""
    app = FastAPI(
        title="HEIC to JPG Converter API",
        description="HEIC 파일을 JPG로 변환하는 REST API 서버",
        lifespan=lifespan,
    )

    # CORS 미들웨어
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handlers
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(_: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "detail": [
                    {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
                    for error in exc.errors()
                ]
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    # 라우터 등록
    app.include_router(zones.router)
    app.include_router(uploads.router)
    app.include_router(jobs.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn, os

    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, workers=os.cpu_count()
    )
