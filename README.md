# GuardRail Lab: A Small AI-Control Evaluation Benchmark

**Project type:** Technical AI safety / AI control / evaluation  
**Stack:** Python 3.10+, pytest  
**Goal:** Test whether simple monitors detect simulated AI-agent actions that violate explicit task constraints.

> This is an educational benchmark, not evidence that real frontier AI systems are safe. The agent behaviors are scripted simulations, allowing experiments to be reproduced without API keys or paid model access.

## Research question

How reliably can a lightweight monitor detect constraint violations by an agent, and what trade-off does stricter monitoring create between catching violations and raising false alarms?

## What it does

- Runs scripted agent actions in a toy environment.
- Labels actions against transparent safety constraints.
- Compares keyword-based, structured rule-based, and combined monitors.
- Measures precision, recall, F1, false-positive rate, and false-negative rate.
- Runs unit tests and exports `results/experiment_results.csv`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python run_experiment.py
python -m pytest -q
```

The core benchmark uses the Python standard library. `pytest` runs tests.

## Repository layout

```text
ai-control-monitor/
├── README.md
├── research_brief.md
├── requirements.txt
├── run_experiment.py
├── src/
│   ├── __init__.py
│   └── monitor.py
├── tests/
│   └── test_monitor.py
└── results/
    └── experiment_results.csv
```

## Experimental design

Each scenario records an action type, target, agent message, and ground-truth label indicating whether the action violates the policy. The benchmark includes hard cases: violations described neutrally and harmless actions containing suspicious-sounding words.

### Metrics

- **Precision:** Of all alerts, the fraction that were genuine violations.
- **Recall:** Of all violations, the fraction detected.
- **F1:** Harmonic mean of precision and recall.
- **False-positive rate:** Harmless actions incorrectly flagged / all harmless actions.
- **False-negative rate:** Violations missed / all violations.

## Important limitations

1. Scenarios are synthetic and small; results do not generalize to real AI agents.
2. Labels are authored for this benchmark and have not been independently adjudicated.
3. A rule-based monitor can only detect violations its rules describe.
4. The combined monitor may improve recall while reducing precision.
5. A stronger follow-up would use blinded human-written scenarios, multiple reviewers, model-generated action traces, and confidence intervals.

## Suggested extensions

1. Add a monitor that sees only structured tool-call metadata, not the agent's message.
2. Add severity-weighted metrics so high-impact violations count more.
3. Compare a language-model judge against rule-based baselines, with human adjudication.
4. Test distribution shift with paraphrases and novel violation patterns.
5. Report bootstrap confidence intervals across scenario families.

## How to describe this honestly on a CV

**AI Control Monitor Benchmark (Python, AI Safety):** Built a reproducible toy benchmark comparing keyword-based and rule-based monitors for simulated agent constraint violations; evaluated precision, recall, F1, and false-positive/negative rates, with tests for false alarms and missed violations.

Do not claim this proves AI systems can be controlled or that you evaluated real frontier models.


## Version 2: Expanded AI-control evaluation

V2 generates **600 deterministic synthetic scenarios** across four policy families and compares:
- keyword-only monitoring,
- structured rule-based monitoring,
- an optional API-backed AI judge (explicit opt-in; may incur costs).

It exports per-scenario predictions, false-positive/false-negative analysis, subgroup metrics by family and wording style, summary metrics, and plots.

```bash
pip install -r requirements.txt
python run_v2_experiment.py
python -m pytest -q
```

To run the optional AI judge, set `OPENAI_API_KEY` and then use `python run_v2_experiment.py --with-llm --llm-limit 40`. Never commit API keys.

See [the V2 research protocol](report/V2_RESEARCH_REPORT.md). Results are synthetic and do not establish real-world AI safety. A GitHub Actions workflow runs tests and the benchmark on pushes and pull requests; its generated outputs are downloadable as workflow artifacts.
