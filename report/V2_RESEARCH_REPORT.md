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

A separate `data/heldout_scenarios.json` fixture contains 32 hand-written cases (8 per family: 4 violations and 4 safe cases). Its messages were authored independently from the training generator's templates and it includes unfamiliar action/target aliases. The frozen monitors are evaluated on this fixture separately; hold-out results are written to files prefixed with `heldout_`.

**Important design caveat:** this is an exploratory post-hoc stress test, not a blind, pre-registered evaluation. The fixture was authored after inspecting the monitor's policy mapping so aliases could deliberately probe its limits. Labels have not been independently adjudicated by multiple reviewers.

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
- heldout_monitor_metrics.png and heldout confusion-matrix plots

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

1. **Template bias:** the generated training set uses a limited set of templates; the 32-case hold-out is still small and hand-written, not representative of real agent behavior.
2. **Post-hoc fixture design:** held-out aliases were selected after inspecting the frozen rule mapping. This is a useful stress test but not a blind confirmatory evaluation.
3. **Label leakage / privileged metadata:** structured fields encode policy-relevant facts available to the rule monitor. The held-out alias cases reduce exact-target matching, but do not remove the rule monitor's access to structured metadata.
4. **Synthetic distribution:** results do not establish real-agent or frontier-model performance.
5. **No independent adjudication:** labels have not been reviewed blind by multiple people.
6. **No confidence intervals:** metrics are descriptive, not population estimates.
7. **Model variance:** AI-judge outcomes depend on provider, model, prompt, and API behavior.

## Next research iteration

- Have independent reviewers label a larger held-out set without seeing monitor predictions.
- Freeze an evaluation protocol before authoring the next set, and include additional policy families and adversarial near-misses.
- Split train/test by template family to reduce template leakage.
- Report bootstrap confidence intervals.
- Compare the AI judge with human adjudication and analyse disagreements.
- Use only sandboxed, permissioned environments.

## Accurate portfolio claim

“Implemented a deterministic 600-scenario synthetic benchmark plus a separate 32-case hand-authored hold-out stress test comparing keyword and structured-rule monitors, with subgroup metrics, per-example error analysis, reproducible CSV outputs, plots, tests, and an optional API-backed AI judge.”

Avoid claims that this proves AI is safe, solves alignment, or demonstrates control of frontier models.
