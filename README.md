# tabular-data-auditor

Validate CSV/Parquet datasets for ML labeling / ingestion pipelines using a declarative YAML schema (types, required columns, regex/range/choice rules, uniqueness, nullability, etc.).

## Features
- YAML-driven schema & rule definitions
- Fast validation with pandas
- JSON and CSV validation reports
- Pretty console summary
- Dockerized CLI for reproducibility


## Install (local)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
