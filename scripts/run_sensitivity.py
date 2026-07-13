"""Run the documented threshold grid against every JSON fixture."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kamino_monitor.core import Thresholds, load_fixture_document, make_run_result  # noqa: E402


def main() -> None:
    rows = []
    for fixture_path in sorted((ROOT / "data/raw/fixtures").glob("*.json")):
        case_id, transactions = load_fixture_document(json.loads(fixture_path.read_text()))
        for rapid_count in (3, 4):
            for rapid_window in (300, 600, 900):
                for failure_count in (2, 3):
                    for failure_window in (300, 600, 900):
                        thresholds = Thresholds(
                            rapid_count, rapid_window, failure_count, failure_window
                        )
                        result = make_run_result(case_id, transactions, thresholds)
                        counts = result["summary"]["priority_counts"]
                        rows.append(
                            {
                                "case_id": case_id,
                                "rapid_count": rapid_count,
                                "rapid_window_seconds": rapid_window,
                                "failure_count": failure_count,
                                "failure_window_seconds": failure_window,
                                **counts,
                            }
                        )
    target = ROOT / "outputs/evaluation-results.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} threshold-case combinations to {target}")


if __name__ == "__main__":
    main()
