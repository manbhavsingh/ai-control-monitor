"""Run the toy AI-control monitor benchmark and export metrics."""
import csv
from pathlib import Path

from src.monitor import (
    SCENARIOS,
    calculate_metrics,
    combined_monitor,
    false_cases,
    keyword_monitor,
    rule_monitor,
)

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

MONITORS = {
    "keyword": keyword_monitor,
    "rule": rule_monitor,
    "combined": combined_monitor,
}


def main():
    rows = []
    print("GuardRail Lab — toy AI-control monitor benchmark")
    print(f"Scenarios: {len(SCENARIOS)}")
    print()
    for name, monitor in MONITORS.items():
        metrics = calculate_metrics(SCENARIOS, monitor)
        rows.append({"monitor": name, **metrics})
        errors = false_cases(SCENARIOS, monitor)
        print(f"[{name}]")
        print("  " + " | ".join(f"{k}={v}" for k, v in metrics.items()))
        print(f"  false positives: {errors['false_positives']}")
        print(f"  false negatives: {errors['false_negatives']}")
        print()

    out = RESULTS / "experiment_results.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved results to: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
