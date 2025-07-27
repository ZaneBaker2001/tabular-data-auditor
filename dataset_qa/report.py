from typing import List, Optional
import json
import pandas as pd

from .validator import ValidationError


def to_dataframe(errors: List[ValidationError]) -> pd.DataFrame:
    return pd.DataFrame([{
        "row": e.row,
        "column": e.column,
        "error_type": e.error_type,
        "message": e.message,
        "value": e.value,
    } for e in errors])


def write_json(errors: List[ValidationError], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([e.__dict__ for e in errors], f, ensure_ascii=False, indent=2)


def write_csv(errors: List[ValidationError], path: str):
    df = to_dataframe(errors)
    df.to_csv(path, index=False)
