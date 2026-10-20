from src.monitor import (
    SCENARIOS,
    calculate_metrics,
    combined_monitor,
    keyword_monitor,
    rule_monitor,
)


def by_id(scenario_id):
    return next(s for s in SCENARIOS if s.scenario_id == scenario_id)


def test_keyword_monitor_catches_explicit_phrase():
    assert keyword_monitor(by_id("S03")) is True


def test_keyword_monitor_can_miss_neutral_wording():
    assert keyword_monitor(by_id("S12")) is False


def test_rule_monitor_uses_structured_metadata():
    assert rule_monitor(by_id("S12")) is True


def test_refusal_can_trigger_keyword_false_alarm():
    # The message mentions a restricted target while explicitly refusing the action.
    assert keyword_monitor(by_id("S13")) is True
    assert by_id("S13").violation is False


def test_combined_monitor_catches_rule_only_case():
    assert combined_monitor(by_id("S12")) is True


def test_metrics_sum_to_dataset_size():
    metrics = calculate_metrics(SCENARIOS, combined_monitor)
    assert metrics["tp"] + metrics["fp"] + metrics["tn"] + metrics["fn"] == len(SCENARIOS)


def test_metric_ranges():
    for monitor in (keyword_monitor, rule_monitor, combined_monitor):
        metrics = calculate_metrics(SCENARIOS, monitor)
        for key in ("precision", "recall", "f1", "false_positive_rate", "false_negative_rate"):
            assert 0.0 <= metrics[key] <= 1.0
