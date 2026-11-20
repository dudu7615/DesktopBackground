from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)


class Font(BaseModel):
    name: str
    # 0 或负数字号会让 ImageFont.truetype 直接抛异常，对应任务就静默停了
    size: int = Field(gt=0, description="字号，必须大于 0")


class Config(BaseModel):
    name: str
    size: tuple[int, int]
    font: Font
    color: tuple[int, int, int]
    #: 至少要有 weather 和 exam 两项，见下面的校验
    place: dict[str, tuple[int, int]]

    @field_validator("font", mode="before")
    @classmethod
    def _dict2Font(cls, v: object) -> object:
        # 兼容旧写法 font: ["msyh.ttc", 60]：老版本安装目录里的 config.yml
        # 会被保留下来（见 packaging/setup.iss），不能让升级后直接起不来
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return {"name": v[0], "size": v[1]}
        return v

    @model_validator(mode="after")
    def _checkPlace(self) -> "Config":
        # 缺 key 的话运行时才会在 config.place["exam"] 处抛 KeyError，那时
        # 对应任务静默停止、只留一张不更新的壁纸。在启动时就说清楚缺什么。
        missing = [k for k in ("weather", "exam") if k not in self.place]
        if missing:
            raise ValueError(f"place 缺少必要项：{', '.join(missing)}")
        return self

    @field_serializer("font")
    def _font2dict(self, v: Font) -> dict[str, str | int]:
        return v.model_dump()
