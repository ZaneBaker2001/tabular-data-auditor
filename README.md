# Tabular Data Auditor

Validate CSV/Parquet datasets for ML labeling / ingestion pipelines using a declarative YAML schema (types, required columns, regex/range/choice rules, uniqueness, nullability, etc.).

## Features
- YAML-driven schema & rule definitions
- Fast validation with pandas
- JSON and CSV validation reports
- Pretty console summary
- Dockerized CLI for reproducibility


## Local Install: 
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

## Quick Start
- Validate a CSV against the example config
- python -m dataset_qa validate examples/data.csv configs/example.yaml \
  --json-report report.json \
  --csv-report  report.csv

## File Locations and Descriptions
```bash
tabular-data-auditor/
  README.md               # Project overview and usage instructions
  pyproject.toml          # Project metadata, dependencies, and build config
  Dockerfile              # Docker container setup
  .gitignore              # Files/directories to ignore in Git

  dataset_qa/             # Main application package
    __init__.py           # Package version info
    cli.py                # CLI entry point using argparse
    config.py             # YAML schema loader & validation models
    rules.py              # Core validation rules (regex, range, choice)
    validator.py          # Validation engine with error tracking
    report.py             # Report generation in CSV/JSON

  configs/                # Example configuration files
    example.yaml          # A full YAML schema with all supported rules

  examples/               # Sample datasets to test the validator
    data.csv              # Sample data with intentional errors

  tests/                  # Unit tests
    test_validator.py     # Tests for validation logic


