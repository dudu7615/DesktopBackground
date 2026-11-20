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
    def _dict2Font(cls, v: object) -> object:
        # 兼容旧写法 font: ["msyh.ttc", 60]：老版本安装目录里的 config.yml
        # 会被保留下来（见 packaging/setup.iss），不能让升级后直接起不来
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return {"name": v[0], "size": v[1]}
        return v

    @field_serializer("font")
    def _font2dict(self, v: Font) -> dict[str, str | int]:
        return v.model_dump()
