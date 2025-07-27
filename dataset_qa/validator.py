from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
from rich.console import Console
from rich.table import Table

from .config import Config, ColumnRule
from . import rules as R

console = Console()


@dataclass
class ValidationError:
    row: int
    column: str
    error_type: str
    message: str
    value: object


class DataValidator:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def validate(self, df: pd.DataFrame) -> List[ValidationError]:
        errors: List[ValidationError] = []
        cfg = self.cfg

        # Check required columns
        for col_rule in cfg.columns:
            if col_rule.required and col_rule.column not in df.columns:
                errors.append(ValidationError(
                    row=-1,
                    column=col_rule.column,
                    error_type="missing_column",
                    message=f"Required column '{col_rule.column}' is missing",
                    value=None,
                ))

        # Only validate columns that exist
        present_rules: List[ColumnRule] = [r for r in cfg.columns if r.column in df.columns]

        # Coerce dtypes
        for r in present_rules:
            try:
                df[r.column] = R.coerce_dtype(df[r.column], r.dtype, cfg.dataset.datetime_formats)
            except Exception as e:
                errors.append(ValidationError(
                    row=-1,
                    column=r.column,
                    error_type="dtype_coercion_failed",
                    message=str(e),
                    value=None,
                ))

        # Nullability & required
        for r in present_rules:
            if not r.allow_null:
                null_mask = df[r.column].isna()
                for idx in df[null_mask].index:
                    errors.append(ValidationError(
                        row=int(idx),
                        column=r.column,
                        error_type="null_not_allowed",
                        message="Null value not allowed",
                        value=None,
                    ))

        # Regex, range, choices
        for r in present_rules:
            series = df[r.column]
            if r.regex:
                mask = R.regex_mismatch(series, r.regex)
                for idx in df[mask].index:
                    errors.append(ValidationError(
                        row=int(idx),
                        column=r.column,
                        error_type="regex_mismatch",
                        message=f"Value does not match regex {r.regex}",
                        value=series.loc[idx],
                    ))
            if r.min is not None or r.max is not None:
                mask = R.out_of_range(series, r.min, r.max)
                for idx in df[mask].index:
                    errors.append(ValidationError(
                        row=int(idx),
                        column=r.column,
                        error_type="out_of_range",
                        message=f"Value not in range [{r.min}, {r.max}]",
                        value=series.loc[idx],
                    ))
            if r.choices:
                mask = R.not_in_choices(series, r.choices)
                for idx in df[mask].index:
                    errors.append(ValidationError(
                        row=int(idx),
                        column=r.column,
                        error_type="not_in_choices",
                        message=f"Value not in allowed set {r.choices}",
                        value=series.loc[idx],
                    ))

        # Uniqueness
        for r in present_rules:
            if r.unique:
                dup_mask = df[r.column].duplicated(keep=False)
                for idx in df[dup_mask].index:
                    errors.append(ValidationError(
                        row=int(idx),
                        column=r.column,
                        error_type="not_unique",
                        message="Duplicate value where unique required",
                        value=df.loc[idx, r.column],
                    ))

        # Primary key uniqueness
        pk = self.cfg.dataset.primary_key
        if pk:
            if any(c not in df.columns for c in pk):
                errors.append(ValidationError(
                    row=-1,
                    column=",".join(pk),
                    error_type="missing_pk_column",
                    message=f"Primary key columns missing from dataset: {pk}",
                    value=None,
                ))
            else:
                dup_mask = df.duplicated(subset=pk, keep=False)
                for idx in df[dup_mask].index:
                    errors.append(ValidationError(
                        row=int(idx),
                        column=",".join(pk),
                        error_type="pk_not_unique",
                        message="Primary key is not unique",
                        value=df.loc[idx, pk].to_dict() if hasattr(df.loc[idx, pk], 'to_dict') else tuple(df.loc[idx, pk]),
                    ))

        return errors

    @staticmethod
    def print_summary(errors: List[ValidationError], df: pd.DataFrame, cfg: Config):
        table = Table(title="Validation Summary")
        table.add_column("Metric")
        table.add_column("Value", justify="right")

        total_errors = len(errors)
        failing_rows = len({e.row for e in errors if e.row >= 0})

        table.add_row("Rows", str(len(df)))
        table.add_row("Columns", str(len(df.columns)))
        table.add_row("Errors", str(total_errors))
        table.add_row("Failing rows", str(failing_rows))

        console.print(table)

        # Top error types
        if total_errors:
            err_types: Dict[str, int] = {}
            for e in errors:
                err_types[e.error_type] = err_types.get(e.error_type, 0) + 1
            top = sorted(err_types.items(), key=lambda x: x[1], reverse=True)[:10]
            console.print("\nTop error types:")
            for et, count in top:
                console.print(f" - {et}: {count}")
