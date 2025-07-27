import argparse
import pandas as pd
from rich.console import Console

from .config import load_config
from .validator import DataValidator
from . import report

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dataset QA CLI")
    sub = parser.add_subparsers(dest="command")

    validate = sub.add_parser("validate", help="Validate a dataset against a YAML config")
    validate.add_argument("data", help="Path to CSV or Parquet file")
    validate.add_argument("config", help="Path to YAML config")
    validate.add_argument("--json-report", dest="json_report", help="Write JSON report to this file")
    validate.add_argument("--csv-report", dest="csv_report", help="Write CSV report to this file")

    return parser


def cmd_validate(args):
    cfg = load_config(args.config)

    if args.data.lower().endswith(".parquet"):
        df = pd.read_parquet(args.data)
    else:
        df = pd.read_csv(args.data)

    console.print(f"Validating [bold]{args.data}[/bold] against [bold]{args.config}[/bold] ...")
    validator = DataValidator(cfg)
    errors = validator.validate(df)

    validator.print_summary(errors, df, cfg)

    if args.json_report:
        report.write_json(errors, args.json_report)
        console.print(f"\nJSON report written to: [green]{args.json_report}[/green]")
    if args.csv_report:
        report.write_csv(errors, args.csv_report)
        console.print(f"CSV report written to: [green]{args.csv_report}[/green]")


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "validate":
        cmd_validate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
