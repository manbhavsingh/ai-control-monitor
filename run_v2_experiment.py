"""Run V2 synthetic benchmark; export metrics, predictions, errors, and plots."""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
from src.v2_benchmark import evaluate_monitor, generate_scenarios, load_heldout_scenarios, keyword_monitor, rule_monitor, metrics_for, scenario_to_dict

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "v2"

def write_csv(path: Path, rows: list[dict]) -> None:
    if rows:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

def subgroup_rows(rows: list[dict], group_key: str) -> list[dict]:
    output = []
    groups = sorted({r[group_key] for r in rows})
    for monitor in sorted({r["monitor"] for r in rows}):
        for group in groups:
            subset = [r for r in rows if r["monitor"] == monitor and r[group_key] == group]
            if not subset:
                continue
            tp = sum(r["violation"] in (True, "True") and r["predicted_violation"] in (True, "True") for r in subset)
            fp = sum(r["violation"] in (False, "False") and r["predicted_violation"] in (True, "True") for r in subset)
            tn = sum(r["violation"] in (False, "False") and r["predicted_violation"] in (False, "False") for r in subset)
            fn = sum(r["violation"] in (True, "True") and r["predicted_violation"] in (False, "False") for r in subset)
            output.append({"monitor":monitor,group_key:group,**metrics_for_counts(tp,fp,tn,fn,len(subset))})
    return output

def metrics_for_counts(tp: int, fp: int, tn: int, fn: int, n: int) -> dict:
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    fpr=fp/(fp+tn) if fp+tn else 0.0
    fnr=fn/(fn+tp) if fn+tp else 0.0
    return {"n":n,"tp":tp,"fp":fp,"tn":tn,"fn":fn,"precision":round(precision,4),
        "recall":round(recall,4),"f1":round(f1,4),"false_positive_rate":round(fpr,4),
        "false_negative_rate":round(fnr,4)}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-family-label",type=int,default=75,help="examples per family and ground-truth label; default creates 600")
    parser.add_argument("--seed",type=int,default=20261020)
    parser.add_argument("--with-llm",action="store_true",help="call the configured OpenAI-compatible judge (may incur API costs)")
    parser.add_argument("--llm-limit",type=int,default=40,help="maximum number of scenarios sent to the AI judge")
    args=parser.parse_args()
    scenarios=generate_scenarios(args.per_family_label,args.seed)
    OUT.mkdir(parents=True,exist_ok=True)
    all_rows=[]
    summaries=[]
    for name,monitor in {"keyword":keyword_monitor,"rule":rule_monitor}.items():
        summary,rows=evaluate_monitor(scenarios,monitor)
        summary["monitor"]=name
        summaries.append(summary)
        for row in rows:
            row["monitor"]=name
        all_rows.extend(rows)

    # Evaluate the separately authored fixture without tuning monitors on it.
    heldout_scenarios = load_heldout_scenarios(ROOT / "data" / "heldout_scenarios.json")
    heldout_rows = []
    heldout_summaries = []
    for name, monitor in {"keyword": keyword_monitor, "rule": rule_monitor}.items():
        summary, rows = evaluate_monitor(heldout_scenarios, monitor)
        summary["monitor"] = name
        summary["dataset"] = "independent_heldout_v1"
        heldout_summaries.append(summary)
        for row in rows:
            row["monitor"] = name
        heldout_rows.extend(rows)

    if args.with_llm:
        if not os.environ.get("OPENAI_API_KEY"):
            parser.error("--with-llm requires OPENAI_API_KEY")
        from src.llm_judge import llm_judge
        groups={}
        for s in scenarios:
            groups.setdefault((s.family,s.violation),[]).append(s)
        llm_scenarios=[]
        keys=sorted(groups)
        limit=min(args.llm_limit,len(scenarios))
        while len(llm_scenarios)<limit:
            added=False
            for key in keys:
                if groups[key]:
                    llm_scenarios.append(groups[key].pop(0))
                    added=True
                    if len(llm_scenarios)>=limit:
                        break
            if not added:
                break
        predictions=[]
        for i,scenario in enumerate(llm_scenarios,start=1):
            print(f"AI judge {i}/{len(llm_scenarios)}: {scenario.scenario_id}")
            predictions.append(llm_judge(scenario))
        summary=metrics_for(llm_scenarios,predictions)
        summary.update({"monitor":"llm_judge","model":os.environ.get("OPENAI_MODEL","gpt-4o-mini")})
        summaries.append(summary)
        for scenario,prediction in zip(llm_scenarios,predictions):
            row=scenario_to_dict(scenario)
            row["predicted_violation"]=prediction
            row["monitor"]="llm_judge"
            row["error_type"]=("false_positive" if prediction and not scenario.violation else
                "false_negative" if not prediction and scenario.violation else
                "true_positive" if prediction and scenario.violation else "true_negative")
            all_rows.append(row)

    write_csv(OUT/"predictions.csv",all_rows)
    write_csv(OUT/"summary_metrics.csv",summaries)
    write_csv(OUT/"error_analysis.csv",[r for r in all_rows if r["error_type"] in ("false_positive","false_negative")])
    write_csv(OUT/"metrics_by_family.csv",subgroup_rows(all_rows,"family"))
    write_csv(OUT/"metrics_by_wording.csv",subgroup_rows(all_rows,"wording_style"))

    write_csv(OUT/"heldout_predictions.csv", heldout_rows)
    write_csv(OUT/"heldout_summary_metrics.csv", heldout_summaries)
    write_csv(OUT/"heldout_error_analysis.csv", [r for r in heldout_rows if r["error_type"] in ("false_positive","false_negative")])
    write_csv(OUT/"heldout_metrics_by_family.csv", subgroup_rows(heldout_rows, "family"))
    write_csv(OUT/"heldout_metrics_by_wording.csv", subgroup_rows(heldout_rows, "wording_style"))
    with (OUT/"run_config.json").open("w",encoding="utf-8") as f:
        json.dump({"seed":args.seed,"per_family_label":args.per_family_label,"scenario_count":len(scenarios),
            "heldout_dataset":"data/heldout_scenarios.json","heldout_scenario_count":len(heldout_scenarios),
            "llm_enabled":args.with_llm,"llm_limit":args.llm_limit if args.with_llm else 0,
            "llm_model":os.environ.get("OPENAI_MODEL") if args.with_llm else None},f,indent=2)
    try:
        from src.plot_results import make_plots
        make_plots(OUT/"summary_metrics.csv",OUT)
        make_plots(OUT/"heldout_summary_metrics.csv",OUT,prefix="heldout_")
    except ImportError:
        print("matplotlib missing; skipped plots. Install requirements.txt.")
    print("\nSummary")
    for m in summaries:
        print(f"{m['monitor']:>12} | n={m['n']:>4} | P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} FPR={m['false_positive_rate']:.3f} FNR={m['false_negative_rate']:.3f}")
    print("\nHeld-out summary (separately authored cases)")
    for m in heldout_summaries:
        print(f"{m['monitor']:>12} | n={m['n']:>4} | P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} FPR={m['false_positive_rate']:.3f} FNR={m['false_negative_rate']:.3f}")
    print(f"\nOutputs saved to {OUT.relative_to(ROOT)}/")

if __name__ == "__main__":
    main()
