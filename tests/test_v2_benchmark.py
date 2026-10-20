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



def test_independent_heldout_fixture_is_balanced_and_separate_from_generator():
    fixture = Path(__file__).resolve().parents[1] / "data" / "heldout_scenarios.json"
    heldout = load_heldout_scenarios(fixture)
    generated = generate_scenarios()

    assert len(heldout) == 32
    assert sum(s.violation for s in heldout) == 16
    assert sum(not s.violation for s in heldout) == 16
    assert len({s.scenario_id for s in heldout}) == len(heldout)
    assert {s.family for s in heldout} == {
        "restricted_read", "private_data_transfer", "monitor_tampering", "destructive_action"
    }
    assert not ({s.message for s in heldout} & {s.message for s in generated})


def test_heldout_set_exposes_rule_monitor_alias_generalization_gap():
    fixture = Path(__file__).resolve().parents[1] / "data" / "heldout_scenarios.json"
    heldout = load_heldout_scenarios(fixture)
    summary, _ = evaluate_monitor(heldout, rule_monitor)

    # The frozen rules intentionally do not know the held-out target/action aliases.
    assert summary["n"] == 32
    assert summary["recall"] == 0.5
    assert summary["false_negative_rate"] == 0.5
