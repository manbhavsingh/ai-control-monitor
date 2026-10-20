"""Generate plots from V2 benchmark CSV outputs; requires matplotlib."""
from pathlib import Path
import csv

def make_plots(summary_csv: Path, output_dir: Path, prefix: str = "") -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with summary_csv.open(newline="",encoding="utf-8") as f:
        summaries=list(csv.DictReader(f))
    if not summaries:
        return
    metrics=["precision","recall","f1","false_positive_rate","false_negative_rate"]
    names=[r["monitor"] for r in summaries]
    x=list(range(len(names)))
    width=0.15
    fig,ax=plt.subplots(figsize=(10,5))
    for i,metric in enumerate(metrics):
        values=[float(r.get(metric,0) or 0) for r in summaries]
        ax.bar([v+(i-2)*width for v in x],values,width=width,label=metric.replace("_"," "))
    ax.set_xticks(x)
    ax.set_xticklabels(names,rotation=15)
    ax.set_ylim(0,1.05)
    ax.set_ylabel("Score")
    ax.set_title("V2 monitor metrics (synthetic benchmark)")
    ax.legend(ncol=3,fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir/f"{prefix}monitor_metrics.png",dpi=160)
    plt.close(fig)
    pred_path=output_dir/f"{prefix}predictions.csv"
    if not pred_path.exists():
        return
    with pred_path.open(newline="",encoding="utf-8") as f:
        predictions=list(csv.DictReader(f))
    for name in sorted({r["monitor"] for r in predictions}):
        subset=[r for r in predictions if r["monitor"]==name]
        tp=sum(r["error_type"]=="true_positive" for r in subset)
        fp=sum(r["error_type"]=="false_positive" for r in subset)
        tn=sum(r["error_type"]=="true_negative" for r in subset)
        fn=sum(r["error_type"]=="false_negative" for r in subset)
        fig,ax=plt.subplots(figsize=(4.5,4))
        matrix=[[tn,fp],[fn,tp]]
        im=ax.imshow(matrix,interpolation="nearest")
        ax.set_xticks([0,1],labels=["Predicted safe","Predicted violation"])
        ax.set_yticks([0,1],labels=["Actually safe","Actually violation"])
        ax.set_title(f"Confusion matrix: {name}")
        for i in range(2):
            for j in range(2):
                ax.text(j,i,str(matrix[i][j]),ha="center",va="center")
        fig.colorbar(im,ax=ax,fraction=0.046,pad=0.04)
        fig.tight_layout()
        fig.savefig(output_dir/f"{prefix}confusion_{name}.png",dpi=160)
        plt.close(fig)
