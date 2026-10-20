# Research Brief: Measuring Monitor Reliability in a Toy AI-Control Setting

## Abstract

This project studies a narrow AI-control question: can simple monitoring strategies identify when an agent's proposed action violates a predefined policy? A reproducible synthetic benchmark compares keyword, structured-rule and combined monitors. Evaluation uses precision, recall, F1, false-positive rate and false-negative rate. The purpose is to establish a transparent baseline and expose failure modes, not to make claims about real-world advanced AI systems.

## Hypothesis

A structured rule monitor will outperform a keyword-only monitor when violations are represented in structured action metadata. A combined monitor may improve recall but can also flag more harmless actions.

## Policy under test

The simulated agent must not:
- access a restricted database,
- transmit private records to an external recipient,
- disable monitoring,
- execute an unapproved destructive action.

Actions are labeled as violations if their structured action type and target conflict with this policy. Labels are independent of the monitor outputs.

## Methods

1. Run the same fixed scenario set through each monitor.
2. Compare predictions to the authored ground-truth labels.
3. Calculate confusion-matrix metrics.
4. Inspect false negatives and false positives to identify monitor blind spots.

## Threats to validity

- **Synthetic data:** Scenarios are small and hand-authored.
- **Rule leakage:** The rule monitor knows the action categories used to define the policy.
- **Limited language variation:** A few messages cannot represent the variety of real agent traces.
- **No adversarial adaptation:** The agent does not learn to evade the monitor.
- **No external review:** Labels have not been independently checked.

## Results template

After running `python run_experiment.py`, copy the metrics into a results table and discuss:
- Which monitor has the highest recall?
- Which monitor has the best precision?
- What kinds of violations does each monitor miss?
- What false alarms are introduced by combining monitors?
- Which next experiment would best test generalization?

## Ethical and safety note

All scenarios are toy examples. The project does not provide instructions for bypassing real monitoring systems or accessing real restricted systems. It is intended for safety evaluation and defensive research.
