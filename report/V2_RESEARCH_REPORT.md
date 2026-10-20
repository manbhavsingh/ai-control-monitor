# GuardRail Lab V2: Research Protocol

## Summary

GuardRail Lab V2 is a reproducible synthetic benchmark comparing monitors that classify whether a proposed agent action violates an explicit toy policy. Four scenario families cover restricted reads, private-data transfers, monitoring tampering, and unapproved destructive actions. The default generator creates 600 examples from a fixed seed.

**Important:** This is a toy benchmark with hand-authored templates and metadata-derived labels, not evidence that real advanced AI systems are controllable.

## Research questions

1. How often does text-only keyword matching miss indirectly worded violations?
2. How does a structured rule monitor compare when it can inspect action metadata?
3. What errors does an optional AI-based judge make on a reproducible subset?
4. Which wording styles and policy families account for false positives and false negatives?

## Dataset generation

The default creates 4 policy families × 2 ground-truth labels × 75 examples = 600 examples. Messages use direct, indirect, benign-mention, and refusal wording. Structured metadata includes action type, target, data class, approval, and refusal status.

The rule monitor has access to structured metadata closely related to the ground-truth label. This is not a fair claim of general superiority; it is a useful policy-enforcement baseline with privileged information. Template diversity is limited and all labels are synthetic.

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

1. **Template bias:** a limited set of hand-written templates is not representative of real agent behavior.
2. **Label leakage:** structured fields strongly influence both rule predictions and labels.
3. **Synthetic distribution:** results do not establish real-agent or frontier-model performance.
4. **No independent adjudication:** labels have not been reviewed blind by multiple people.
5. **No confidence intervals:** metrics are descriptive, not population estimates.
6. **Model variance:** AI-judge outcomes depend on provider, model, prompt, and API behavior.

## Next research iteration

- Have independent reviewers label a held-out set without seeing monitor predictions.
- Add paraphrases after monitor rules are frozen.
- Split train/test by template family to reduce template leakage.
- Report bootstrap confidence intervals.
- Compare the AI judge with human adjudication and analyse disagreements.
- Use only sandboxed, permissioned environments.

## Accurate portfolio claim

“Implemented a deterministic 600-scenario synthetic benchmark comparing keyword and structured-rule monitors, with subgroup metrics, per-example error analysis, reproducible CSV outputs, plots, tests, and an optional API-backed AI judge.”

Avoid claims that this proves AI is safe, solves alignment, or demonstrates control of frontier models.
