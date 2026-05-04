from typing import Optional, Any
from pydantic import BaseModel, model_validator, field_validator
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
