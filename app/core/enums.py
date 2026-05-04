from enum import StrEnum


class ResizeMode(StrEnum):
    FIXED = "fixed"
    RATIO = "ratio"

    @classmethod
    def of(cls, value: str):
        for item in cls:
            if item.value == value.lower():
                return item
