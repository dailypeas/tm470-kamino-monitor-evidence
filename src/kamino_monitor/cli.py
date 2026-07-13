"""Command-line entry point."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from .core import InputError, Thresholds, load_fixture_document, make_run_result
from .retrieval import retrieve_transaction, retrieve_wallet


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Explainable Kamino-related transaction review prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)
    fixture = subparsers.add_parser("analyse-fixture")
    fixture.add_argument("--input", type=Path, required=True)
    wallet = subparsers.add_parser("analyse-wallet")
    wallet.add_argument("--wallet", required=True)
    transaction = subparsers.add_parser("analyse-transaction")
    transaction.add_argument("--signature", required=True)
    for child in (fixture, wallet, transaction):
        child.add_argument("--output-dir", type=Path, required=True)
        child.add_argument("--rapid-count", type=int, default=3)
        child.add_argument("--rapid-window", type=int, default=600)
        child.add_argument("--failure-count", type=int, default=2)
        child.add_argument("--failure-window", type=int, default=600)
    return parser


def _write_outputs(output_dir: Path, result: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    fields = [
        "signature", "timestamp", "status", "kamino_relevance", "rapid_status", "rapid_triggered",
        "rapid_count", "failure_status", "failure_triggered", "failure_count", "priority",
    ]
    with (output_dir / "analysis.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in result["records"]:
            rapid = record["indicators"]["rapid_relevant_activity"]
            failures = record["indicators"]["repeated_failed_relevant_transactions"]
            writer.writerow(
                {
                    "signature": record["signature"],
                    "timestamp": record["timestamp"],
                    "status": record["status"],
                    "kamino_relevance": record["kamino_relevance"],
                    "rapid_status": rapid["status"],
                    "rapid_triggered": rapid["triggered"],
                    "rapid_count": rapid.get("observed_count"),
                    "failure_status": failures["status"],
                    "failure_triggered": failures["triggered"],
                    "failure_count": failures.get("observed_count"),
                    "priority": record["priority"],
                }
            )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        thresholds = Thresholds(
            rapid_count=args.rapid_count,
            rapid_window_seconds=args.rapid_window,
            failure_count=args.failure_count,
            failure_window_seconds=args.failure_window,
        )
        if args.command == "analyse-fixture":
            document = json.loads(args.input.read_text(encoding="utf-8"))
            case_id, transactions = load_fixture_document(document)
        elif args.command == "analyse-wallet":
            case_id, transactions = f"live-wallet:{args.wallet}", retrieve_wallet(args.wallet)
        else:
            case_id, transactions = f"live-transaction:{args.signature}", retrieve_transaction(args.signature)
        result = make_run_result(case_id, transactions, thresholds)
        _write_outputs(args.output_dir, result)
        print(json.dumps(result["summary"], indent=2))
        return 0
    except (InputError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

