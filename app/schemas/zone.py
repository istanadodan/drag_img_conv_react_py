from pydantic import BaseModel, field_validator
from core.config import ResizeOption
from typing import Optional


class ZoneResponse(BaseModel):
    """GET /api/zones 응답"""

    id: str
    label: str
    description: Optional[str] = None
    quality: int
    color: Optional[str] = None
    resize: Optional[ResizeOption] = None
    order: int


class ZoneCreate(BaseModel):
    """POST /api/zones 요청"""

    id: str
    label: str
    description: Optional[str] = None
    quality: int
    color: Optional[str] = None
    resize: Optional[ResizeOption] = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        if not v or len(v) < 2:
            raise ValueError("id must be at least 2 characters")
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "id can only contain alphanumeric characters, hyphens, and underscores"
            )
        return v

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v):
        if not 1 <= v <= 100:
            raise ValueError("quality must be between 1 and 100")
        return v
