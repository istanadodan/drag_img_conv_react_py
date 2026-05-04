import json
from pathlib import Path
from typing import List, Optional, Literal
from pydantic import BaseModel


class ResizeOption(BaseModel):
    """이미지 리사이징 설정"""

    mode: Optional[str] = None
    ratio: Optional[float] = None  # 축소 비율 (0.5 = 50%)
    long_side_length: Optional[int] = None  # 긴 쪽의 길이


class Zone(BaseModel):
    """config.json의 zone 항목"""

    id: str
    label: str
    description: Optional[str] = None
    quality: int
    color: Optional[str] = None
    resize: Optional[ResizeOption] = None


class Settings(BaseModel):
    """config.json 스키마"""

    zones: List[Zone]
    max_workers: int = 4

    @classmethod
    def load(cls):
        """config.json에서 로드"""
        config_path = Path(__file__).parent.parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def save(self):
        """config.json에 저장"""
        config_path = Path(__file__).parent.parent / "config.json"
        data = self.model_dump(mode="json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# 전역 설정 인스턴스
settings = Settings.load()
