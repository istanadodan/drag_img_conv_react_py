from typing import Optional, Any
from pydantic import BaseModel, model_validator, field_validator, Field
from fastapi import Form
from core.enums import ResizeMode


class ResizeConfig(BaseModel):
    """리사이징 설정"""

    use_resize: bool = False
    mode: Optional[ResizeMode] = None
    ratio: Optional[float] = None
    long_side_length: Optional[int] = None

    @classmethod
    def as_form(
        cls,
        use_resize: str = Form("false"),
        mode: Optional[ResizeMode] = Form(None),
        ratio: Optional[float] = Form(None),
        long_side_length: Optional[int] = Form(None),
    ):
        return cls(
            use_resize=True if use_resize == "true" else False,
            mode=mode,
            ratio=ratio,
            long_side_length=long_side_length,
        )

    @model_validator(mode="after")
    def validate_mode_params(self):
        if self.use_resize:
            if not ResizeMode.of(self.mode or ""):
                raise ValueError(f"mode not validate. {self.mode}")

        return self


class ZoneOrderReq(BaseModel):
    zone_id: str = Field(
        ..., alias="zoneId", description="The ID of the zone to reorder"
    )
    order: int = Field(..., description="The new order position for the zone")

    @field_validator("order")
    def validate_zone_exists(cls, v):
        if isinstance(v, int):
            return v + 1
        return v
