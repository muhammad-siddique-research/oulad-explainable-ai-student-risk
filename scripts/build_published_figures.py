"""Draw publication-ready SVG summaries from archived aggregate CSVs only.

This script never reads row-level learner records or synthetic test fixtures.
Charts inherit the evidentiary limits of the committed summaries; a plotting
run is NOT an independent statistical replication of the OULAD analysis.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COLORS = {
    "prevalence": "#87929E",
    "logistic_l2": "#168A80",
    "random_forest": "#E7A64A",
    "xgboost": "#30598F",
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / "results" / name).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#B7C4CF",
        "axes.labelcolor": "#25384A",
        "xtick.color": "#4B5E6B",
        "ytick.color": "#4B5E6B",
        "svg.hashsalt": "oulad-aggregate-figures-2026",
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#FFFFFF",
        "savefig.facecolor": "#FFFFFF",
    })


def save(fig: plt.Figure, path: Path, *, png: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="svg", bbox_inches="tight", metadata={"Date": None})
    if png:
        fig.savefig(path.with_suffix(".png"), format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def comparison(output_dir: Path, *, png: bool = False) -> None:
    source = {r["model"]: r for r in read_csv("primary_models.csv")}
    keys = ["prevalence", "logistic_l2", "random_forest", "xgboost"]
    labels = ["Prevalence\nonly", "Logistic\nRegression", "Random\nForest", "XGBoost"]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.9), sharey=True)
    for ax, (field, heading, maximum) in zip(
        axs,
        [
            ("AP", "Average precision  ↑", 0.85),
            ("AUC", "ROC-AUC  ↑", 0.85),
            ("Brier", "Brier score  ↓", 0.28),
        ],
    ):
        values = [float(source[k][field]) for k in keys]
        locations = np.arange(len(keys))
        bars = ax.barh(
            locations, values,
            color=[COLORS[k] for k in keys], height=0.59, zorder=3,
        )
        ax.set_xlim(0, maximum)
        ax.set_title(heading, loc="left", weight="bold", pad=16, color="#24364A")
        ax.set_xticks(np.linspace(0, maximum, 5))
        ax.grid(axis="x", color="#E7EDF2", zorder=0)
        ax.set_yticks(locations, labels)
        ax.invert_yaxis()
        for bar, value in zip(bars, values):
            ax.text(
                value + maximum * 0.018,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.3f}",
                va="center", fontsize=9, color="#24364A", weight="bold",
            )
    fig.suptitle(
        "Early academic risk | Models on held-out course presentations",
        fontsize=15, color="#163A55", weight="bold", y=1.04,
    )
    fig.text(
        0.01, -0.045,
        "OULAD archived aggregate results | n = 7,239 | AP prevalence = 0.4223 |"
        " descriptive prediction, not causal or independently re-replicated",
        fontsize=9, color="#526779",
    )
    fig.tight_layout(w_pad=2.4)
    save(fig, output_dir / "heldout_model_comparison.svg", png=png)


def portability(output_dir: Path, *, png: bool = False) -> None:
    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for row in read_csv("leave_one_module_out.csv"):
        grouped.setdefault(row["heldout_module"], {})[row["model"]] = row
    modules = sorted(grouped)
    deltas_ap = [
        float(grouped[m]["xgboost"]["AP"]) - float(grouped[m]["logistic_l2"]["AP"])
        for m in modules
    ]
    deltas_brier = [
        float(grouped[m]["xgboost"]["Brier"]) - float(grouped[m]["logistic_l2"]["Brier"])
        for m in modules
    ]
    fig, axes = plt.subplots(1, 2, figsize=(12.7, 4.9), sharex=True)
    for ax, (deltas, label, better_positive) in zip(
        axes,
        [
            (deltas_ap, "Δ Average precision  (XGBoost − Logistic)", True),
            (deltas_brier, "Δ Brier score  (XGBoost − Logistic)", False),
        ],
    ):
        x = np.arange(len(modules))
        colors = [
            "#168A80" if (v > 0 if better_positive else v < 0) else "#C76B43"
            for v in deltas
        ]
        ax.bar(x, deltas, color=colors, width=0.65, zorder=3)
        ax.axhline(0, lw=1.1, color="#7B8EA1")
        ax.grid(axis="y", color="#E8EDF1", zorder=0)
        ax.set_xticks(x, modules)
        ax.set_title(label, loc="left", weight="bold", fontsize=10.7, pad=16)
        pad = max(abs(v) for v in deltas) * 0.1
        ax.set_ylim(min(deltas) - 2 * pad, max(deltas) + 3 * pad)
        for idx, delta in enumerate(deltas):
            ax.text(
                idx, delta + (pad * 0.30 if delta >= 0 else -pad * 0.30),
                (f"{delta:+.3f}" if better_positive else f"{delta:+.4f}"),
                va="bottom" if delta >= 0 else "top",
                ha="center", fontsize=8.8, color="#23384A",
            )
    fig.suptitle(
        "Leave-one-module-out | Ranking better ≠ estimating risk better",
        fontsize=14.5, color="#163A55", weight="bold", y=1.04,
    )
    fig.text(
        0.01, -0.055,
        "Teal = favorable to XGBoost; orange = favorable to Logistic. "
        "Green AP differences and adverse Brier shifts can coexist. "
        "Seven context-level tests; archived aggregate results only.",
        fontsize=9, color="#526779",
    )
    fig.tight_layout(w_pad=3.2)
    save(fig, output_dir / "module_transportability.svg", png=png)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "figures")
    parser.add_argument("--png", action="store_true", help="Also generate 180-dpi PNG previews")
    args = parser.parse_args()
    style()
    comparison(args.output_dir, png=args.png)
    portability(args.output_dir, png=args.png)
    print(f"Created aggregate-only figures in {args.output_dir}")


if __name__ == "__main__":
    main()
