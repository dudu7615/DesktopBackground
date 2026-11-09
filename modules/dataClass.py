from pydantic import (
    BaseModel,
    field_validator,
    field_serializer,
)


class Font(BaseModel):
    name: str
    size: int


class Config(BaseModel):
    name: str
    size: tuple[int, int]
    font: Font
    color: tuple[int, int, int]
    place: dict[str, tuple[int, int]]

    @field_validator("font", mode="before")
    @classmethod
    def _dict2Font(cls, v: dict[str, str | int]) -> Font:
        return Font.model_validate(v)

    @field_serializer("font")
    def _font2dict(self, v: Font) -> dict[str, str | int]:
        return v.model_dump()
