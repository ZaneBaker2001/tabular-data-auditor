import re
from typing import Any, Optional, Sequence
import pandas as pd


def coerce_dtype(series: pd.Series, dtype: str, datetime_formats: Sequence[str]):
    if dtype == "int":
        return pd.to_numeric(series, errors="coerce").astype("Int64")
    if dtype == "float":
        return pd.to_numeric(series, errors="coerce")
    if dtype == "bool":
        return series.astype("boolean")
    if dtype == "datetime":
        # try multiple formats, first success wins
        out = pd.to_datetime(series, errors="coerce", utc=False, format=None)
        # If a strict format list is provided, try them sequentially
        if out.isna().any() and datetime_formats:
            for fmt in datetime_formats:
                tmp = pd.to_datetime(series, errors="coerce", format=fmt)
                out = out.fillna(tmp)
        return out
    return series.astype("string")


def regex_mismatch(series: pd.Series, pattern: Optional[str]):
    if not pattern:
        return pd.Series(False, index=series.index)
    regex = re.compile(pattern)
    return ~series.fillna("").astype(str).apply(lambda x: bool(regex.match(x)))


def out_of_range(series: pd.Series, min_v: Optional[float], max_v: Optional[float]):
    mask = pd.Series(False, index=series.index)
    if min_v is not None:
        mask |= series < min_v
    if max_v is not None:
        mask |= series > max_v
    return mask.fillna(False)


def not_in_choices(series: pd.Series, choices: Optional[Sequence[Any]]):
    if not choices:
        return pd.Series(False, index=series.index)
    return ~series.isin(choices)
