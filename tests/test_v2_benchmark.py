import csv
from pathlib import Path
from src.v2_benchmark import evaluate_monitor, generate_scenarios, keyword_monitor, load_heldout_scenarios, metrics_for, rule_monitor

def test_default_benchmark_has_600_scenarios_and_is_reproducible():
    assert len(generate_scenarios()) == 600
    assert generate_scenarios() == generate_scenarios()

def test_generated_messages_have_substantial_surface_diversity():
    scenarios = generate_scenarios()
    assert len({s.message for s in scenarios}) > 200

def test_ground_truth_is_balanced():
    scenarios = generate_scenarios()
    assert sum(s.violation for s in scenarios) == 300
    assert sum(not s.violation for s in scenarios) == 300

def test_all_four_families_are_present():
    assert {s.family for s in generate_scenarios()} == {
        "restricted_read", "private_data_transfer", "monitor_tampering", "destructive_action"}

def test_rule_monitor_matches_structured_labels_in_toy_data():
    scenarios = generate_scenarios()
    assert all(rule_monitor(s) for s in scenarios if s.violation)
    assert not any(rule_monitor(s) for s in scenarios if not s.violation)

def test_keyword_monitor_misses_some_indirect_violations():
    assert any(s.violation and not keyword_monitor(s) for s in generate_scenarios())

def test_metrics_count_every_scenario_and_are_bounded():
    scenarios = generate_scenarios()
    metrics = metrics_for(scenarios, [rule_monitor(s) for s in scenarios])
    assert metrics["n"] == len(scenarios)
    assert metrics["tp"] + metrics["fp"] + metrics["tn"] + metrics["fn"] == len(scenarios)
    for key in ("precision", "recall", "f1", "false_positive_rate", "false_negative_rate"):
        assert 0 <= metrics[key] <= 1



def test_expanded_heldout_fixture_is_balanced_and_separate_from_generator():
    fixture = Path(__file__).resolve().parents[1] / "data" / "heldout_scenarios.json"
    heldout = load_heldout_scenarios(fixture)
    generated = generate_scenarios()

    assert len(heldout) == 128
    assert sum(s.violation for s in heldout) == 64
    assert sum(not s.violation for s in heldout) == 64
    assert len({s.scenario_id for s in heldout}) == len(heldout)
    assert len({s.message for s in heldout}) >= 120
    assert not ({s.message for s in heldout} & {s.message for s in generated})
    assert {s.family for s in heldout} == {
        "restricted_read", "private_data_transfer", "monitor_tampering", "destructive_action"
    }


def test_expanded_heldout_has_balanced_labels_within_each_policy_family():
    fixture = Path(__file__).resolve().parents[1] / "data" / "heldout_scenarios.json"
    heldout = load_heldout_scenarios(fixture)

    for family in {s.family for s in heldout}:
        subset = [s for s in heldout if s.family == family]
        assert len(subset) == 32
        assert sum(s.violation for s in subset) == 16
        assert sum(not s.violation for s in subset) == 16


def test_expanded_heldout_cases_include_rationales_and_challenge_metadata():
    fixture = Path(__file__).resolve().parents[1] / "data" / "heldout_scenarios.json"
    heldout = load_heldout_scenarios(fixture)

    assert all(s.annotation_rationale.strip() for s in heldout)
    assert len({s.challenge_type for s in heldout}) >= 15
    assert {"none", "medium", "high", "critical"} <= {s.severity for s in heldout}


def test_frozen_rule_monitor_misses_some_expanded_heldout_aliases():
    fixture = Path(__file__).resolve().parents[1] / "data" / "heldout_scenarios.json"
    heldout = load_heldout_scenarios(fixture)
    summary, _ = evaluate_monitor(heldout, rule_monitor)

    assert summary["n"] == 128
    assert summary["recall"] < 1.0
    assert summary["false_negative_rate"] > 0.0



def test_reviewer_worksheet_has_all_cases_and_hides_gold_labels():
    root = Path(__file__).resolve().parents[1]
    with (root / "data" / "heldout_review_template.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 128
    assert {row["scenario_id"] for row in rows} == {
        f"EVAL2-{index:03d}" for index in range(1, 129)
    }
    assert all(row["reviewer_a_label"] == "" and row["reviewer_b_label"] == "" for row in rows)
    assert all(row["adjudicated_label"] == "" for row in rows)
    assert all("violation" not in row and "annotation_rationale" not in row for row in rows)
