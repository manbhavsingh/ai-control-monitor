# GuardRail Lab V2: Research Protocol

## Summary

GuardRail Lab V2 is a reproducible synthetic benchmark comparing monitors that classify whether a proposed agent action violates an explicit toy policy. Four scenario families cover restricted reads, private-data transfers, monitoring tampering, and unapproved destructive actions. The default generator creates 600 examples from a fixed seed.

**Important:** This is a toy benchmark with hand-authored templates and metadata-derived labels, not evidence that real advanced AI systems are controllable.

## Research questions

1. How often does text-only keyword matching miss indirectly worded violations?
2. How does a structured rule monitor compare when it can inspect action metadata?
3. What errors does an optional AI-based judge make on a reproducible subset?
4. Which wording styles and policy families account for false positives and false negatives?
5. How well do the frozen rules generalize to separately written wording and unseen action/target aliases?

## Dataset generation

The default creates 4 policy families × 2 ground-truth labels × 75 examples = 600 examples. Messages use direct, indirect, benign-mention, and refusal wording. Structured metadata includes action type, target, data class, approval, and refusal status.

The rule monitor has access to structured metadata closely related to the policy decision. This is not a fair claim of general superiority; it is a useful policy-enforcement baseline with privileged information. Template diversity is limited and all labels are synthetic.

A separate `data/heldout_scenarios.json` fixture now contains 128 author-written cases: 4 policy families × 16 violations × 16 safe cases per family (32 cases per family, 64 positive and 64 negative overall). Each case includes an annotation rationale, challenge category, and severity. Coverage includes action/target aliases, indirect intent, missing authorization, benign policy mentions, refusals, approved exceptions, read-only checks, redacted/public data, simulations, dry runs, sandbox actions, and historical references. The frozen monitors are evaluated separately; outputs use the `heldout_` prefix, with subgroup CSVs by family, wording style, challenge type, and severity.

**Important design caveat:** this is an expanded, exploratory post-hoc stress test, not yet a blind independent evaluation. The fixture was authored after inspecting the monitor mapping, so it is still vulnerable to author bias. Labels have not been independently adjudicated. A label-blinded reviewer worksheet and protocol are provided at `data/heldout_review_template.csv` and `data/HELDOUT_REVIEW_GUIDE.md`; external review remains pending.

## Initial held-out results

GitHub Actions ran the frozen monitors on all 32 held-out cases:

| Monitor | N | Precision | Recall | F1 | False-positive rate | False-negative rate |
|---|---:|---:|---:|---:|---:|---:|
| Keyword baseline | 32 | 0.429 | 0.188 | 0.261 | 0.250 | 0.812 |
| Structured rule monitor | 32 | 1.000 | 0.500 | 0.667 | 0.000 | 0.500 |

The structured rule monitor correctly flagged 8 of 16 violations and missed 8 cases whose action or target names were outside its fixed mappings. The keyword baseline caught 3 of 16 violations and falsely flagged 4 of 16 safe cases. In comparison, the generated benchmark gives the structured rule monitor a perfect score because its metadata closely follows the generator's label construction.

These are descriptive results for this small, post-hoc fixture only. There are just 16 positive and 16 negative cases, and labels have not been independently adjudicated; a single case changes recall by 6.25 percentage points.

## Monitors

- **Keyword baseline:** flags messages containing a fixed list of phrases.
- **Structured rule monitor:** applies explicit rules to action metadata and refusal status.
- **Optional AI judge:** sends scenario details to an OpenAI-compatible chat-completions endpoint. It is opt-in, may incur API costs, and depends on the selected model. Results are not generated unless explicitly enabled.

## Metrics and outputs

Precision, recall, F1, false-positive rate, and false-negative rate are calculated against synthetic labels. Per-example predictions and error types are saved for audit. Subgroup metrics are produced by policy family and wording style.

Outputs are written to results/v2/:
- predictions.csv
- summary_metrics.csv
- error_analysis.csv
- metrics_by_family.csv
- metrics_by_wording.csv
- run_config.json
- monitor_metrics.png and confusion-matrix plots
- heldout_predictions.csv, heldout_summary_metrics.csv, heldout_error_analysis.csv
- heldout_metrics_by_family.csv, heldout_metrics_by_wording.csv
- heldout_metrics_by_challenge_type.csv, heldout_metrics_by_severity.csv
- heldout_monitor_metrics.png and heldout confusion-matrix plots

For external label validation, use `data/heldout_review_template.csv` and follow `data/HELDOUT_REVIEW_GUIDE.md`. Reviewer agreement and adjudication results should be added only after actual independent reviewers complete the process.

## Reproduce

\`\`\`bash
pip install -r requirements.txt
python run_v2_experiment.py
python -m pytest -q
\`\`\`

To compare with an AI judge on a small subset, set OPENAI_API_KEY and optionally OPENAI_MODEL / OPENAI_BASE_URL, then run:

\`\`\`bash
python run_v2_experiment.py --with-llm --llm-limit 40
\`\`\`

This sends one API request per sampled scenario. Check provider pricing and rate limits. Never commit API keys. Model outputs may change across versions even with temperature zero.

## Threats to validity

1. **Template bias:** the generated training set uses a limited set of templates; the 128-case hold-out is still synthetic and author-written, not representative of real agent behavior.
2. **Label provenance:** labels include written rationales, but the same project authoring process created them. Rationales improve auditability, not independence.
3. **Post-hoc fixture design:** held-out aliases were selected after inspecting the frozen rule mapping. This is a useful stress test but not a blind confirmatory evaluation.
4. **Label leakage / privileged metadata:** structured fields encode policy-relevant facts available to the rule monitor. The held-out alias cases reduce exact-target matching, but do not remove the rule monitor's access to structured metadata.
5. **Synthetic distribution:** results do not establish real-agent or frontier-model performance.
6. **No independent adjudication:** labels have not been reviewed blind by multiple people.
7. **No confidence intervals:** metrics are descriptive, not population estimates.
8. **Model variance:** AI-judge outcomes depend on provider, model, prompt, and API behavior.

## Next research iteration

- Run the blind two-reviewer protocol documented in `data/HELDOUT_REVIEW_GUIDE.md`; report agreement, Cohen's kappa, disagreements, adjudication rate, and any gold-label corrections.
- Freeze a new protocol before authoring a future set and include additional policy families and adversarial near-misses.
- Split train/test by template family to reduce template leakage.
- Report bootstrap confidence intervals.
- Compare the AI judge with human adjudication and analyse disagreements.
- Use only sandboxed, permissioned environments.

## Accurate portfolio claim

“Implemented a deterministic 600-scenario synthetic benchmark plus a separate 128-case hand-authored hold-out stress test comparing keyword and structured-rule monitors, with subgroup metrics, per-example error analysis, reproducible CSV outputs, plots, tests, and an optional API-backed AI judge.”

Avoid claims that this proves AI is safe, solves alignment, or demonstrates control of frontier models.
