from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field, validator


DTypeLiteral = Literal["int", "float", "string", "bool", "datetime"]


class DatasetConfig(BaseModel):
    primary_key: Optional[List[str]] = Field(default=None, description="List of columns forming the primary key")
    datetime_formats: List[str] = Field(default_factory=lambda: ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"])


class ColumnRule(BaseModel):
    column: str
    dtype: DTypeLiteral = "string"
    required: bool = False
    unique: bool = False
    allow_null: bool = True

    # Value constraints
    regex: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    choices: Optional[List[Any]] = None

    @validator("min", "max", pre=True)
    def _cast_numeric(cls, v):  # type: ignore
        if v is None:
            return v
        try:
            return float(v)
        except Exception:
            raise ValueError("min/max must be numeric")


class Config(BaseModel):
    dataset: DatasetConfig = DatasetConfig()
    columns: List[ColumnRule]


def load_config(path: str) -> Config:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(**data)
