import pandas as pd
from dataset_qa.config import Config, DatasetConfig, ColumnRule
from dataset_qa.validator import DataValidator


def test_simple_validation():
    cfg = Config(
        dataset=DatasetConfig(primary_key=["id"]),
        columns=[
            ColumnRule(column="id", dtype="int", required=True, unique=True, allow_null=False),
            ColumnRule(column="email", dtype="string", regex=r"^[^@\n]+@[^@\n]+\.[^@\n]+$", allow_null=False),
            ColumnRule(column="score", dtype="float", min=0, max=1, allow_null=False),
        ],
    )

    df = pd.DataFrame({
        "id": [1, 2, 2],  # duplicate id triggers pk/unique error
        "email": ["valid@example.com", "bad_email", "also@example.com"],
        "score": [0.5, 1.2, 0.9],  # 1.2 out of range
    })

    v = DataValidator(cfg)
    errors = v.validate(df)

    # We expect errors for duplicated id, bad email, out-of-range score
    assert any(e.error_type == "not_unique" and e.column == "id" for e in errors)
    assert any(e.error_type == "regex_mismatch" and e.column == "email" for e in errors)
    assert any(e.error_type == "out_of_range" and e.column == "score" for e in errors)
    assert len(errors) >= 3
