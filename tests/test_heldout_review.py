import csv
from pathlib import Path

from src.v2_benchmark import load_heldout_scenarios


def test_every_heldout_case_has_a_severity_rationale():
    root = Path(__file__).resolve().parents[1]
    scenarios = load_heldout_scenarios(root / "data" / "heldout_scenarios.json")
    assert all(s.severity_rationale.strip() for s in scenarios)
    assert all((s.severity == "none") == (not s.violation) for s in scenarios)


def test_ai_review_annotations_cover_all_heldout_cases():
    path = Path(__file__).resolve().parents[1] / "data" / "ai_reviewer_pass_v1.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 128
    assert len({row["scenario_id"] for row in rows}) == 128
    assert {row["ai_reviewer_label"] for row in rows} == {"safe", "violation"}
    assert all(row["ai_reviewer_rationale"].strip() for row in rows)
