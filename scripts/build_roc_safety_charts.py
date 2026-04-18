#!/usr/bin/env python3
"""
Build safety ROC curves from raw CSV files in `data/safety/`.
For each model, produces two PNG images:
  1. Auditing Budget vs Safety (one line per monitor)
  2. Auditing Budget vs Budgeted Safety (one line per monitor)

Usage:
    python3 build_roc_safety_charts.py
"""

import os
import glob
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
DATA_DIR = os.path.join(REPO_ROOT, "data", "safety")
IMG_DIR = os.path.join(REPO_ROOT, "analyses", "charts", "roc-safety")
os.makedirs(IMG_DIR, exist_ok=True)

IMG_W, IMG_H = 960, 700
IMG_SCALE = 2

# ---------------------------------------------------------------------------
# Paper-ready theme
# ---------------------------------------------------------------------------
PAPER_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Arial, Helvetica, sans-serif", size=26, color="#222"),
    title_font=dict(size=34, color="#111"),
    legend=dict(
        font=dict(size=22),
        bgcolor="rgba(255,255,255,0.9)",
        # bordercolor="#ccc",
        # borderwidth=1,
        orientation="h",
        yanchor="top",
        y=-0.20,
        xanchor="left",
        x=-0.05,

    ),
    margin=dict(l=90, r=50, t=100, b=120),
)

MONITOR_COLORS = {
    "git_diff_monitor": "#2980b9",
    "full_trajectory_monitor": "#e67e22",
    "composite_scorer": "#8e44ad",
}

MONITOR_LABELS = {
    "git_diff_monitor": "Git Diff",
    "full_trajectory_monitor": "Full Trajectory",
    "composite_scorer": "Composite",
}

MONITORS = ["git_diff_monitor", "full_trajectory_monitor", "composite_scorer"]

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
frames = []
for csv_path in sorted(glob.glob(os.path.join(DATA_DIR, "*.csv"))):
    short_name = os.path.splitext(os.path.basename(csv_path))[0]
    tmp = pd.read_csv(csv_path)
    tmp["model"] = short_name
    frames.append(tmp)

df = pd.concat(frames, ignore_index=True)
MODELS = sorted(df["model"].unique())

print(f"Loaded {len(df)} rows, models: {MODELS}")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def save_fig(fig, name):
    path = os.path.join(IMG_DIR, f"{name}.png")
    fig.write_image(path, width=IMG_W, height=IMG_H, scale=IMG_SCALE)
    print(f"  -> {path}")


# ---------------------------------------------------------------------------
# Build ROC charts
# ---------------------------------------------------------------------------
def compute_auc(xs, ys):
    """Trapezoidal AUC, normalized to 0–1 (divides by 100*100)."""
    auc = 0.0
    for i in range(1, len(xs)):
        auc += (xs.iloc[i] - xs.iloc[i - 1]) * (ys.iloc[i] + ys.iloc[i - 1]) / 2
    return auc / 10000


def build_roc_for_model(model, y_col, y_label, title_suffix, filename_suffix):
    """Build a single ROC-style chart for one model."""
    mdf = df[df["model"] == model]
    model_name = mdf["model_name"].values[0]

    fig = go.Figure()

    auc_parts = []
    for monitor in MONITORS:
        sub = mdf[mdf["monitor_name"] == monitor].sort_values("auditing_budget")
        auc = compute_auc(sub["auditing_budget"], sub[y_col])
        auc_parts.append(f"{MONITOR_LABELS[monitor]}: {auc:.3f}")
        fig.add_trace(go.Scatter(
            x=sub["auditing_budget"],
            y=sub[y_col],
            mode="lines",
            name=f"{MONITOR_LABELS[monitor]} (AUC={auc:.3f})",
            line=dict(color=MONITOR_COLORS[monitor], width=2.5),
        ))

    fig.update_layout(
        **PAPER_LAYOUT,
        title=dict(text=model_name, x=0.5, xanchor="center"),
        xaxis=dict(title="Auditing Budget", range=[0, 100], dtick=10,
                    ticksuffix="%", gridcolor="#e0e0e0",
                    zeroline=True, zerolinecolor="#ccc", title_standoff=20,
                    ticklabelshift=8),
        yaxis=dict(title=y_label, range=[0, 105],
                    ticksuffix="%", gridcolor="#e0e0e0",
                    title_standoff=10,
                    ticklabelstandoff=8),
    )

    save_fig(fig, f"{model}_{filename_suffix}")

    # Also a zoomed 0-10% version
    fig.update_layout(
        title=dict(text=model_name, x=0.5, xanchor="center"),
        xaxis=dict(range=[0, 10], dtick=1, ticksuffix="%"),
    )
    save_fig(fig, f"{model}_{filename_suffix}_zoom10")

    return fig


def build_all_roc_charts():
    """Build per-model PNG charts."""
    for model in MODELS:
        print(f"\n  Model: {model}")
        build_roc_for_model(model, "safety", "Safety",
                            "Auditing Budget vs Safety", "safety_roc")
        build_roc_for_model(model, "budgeted_safety", "Budgeted Safety",
                            "Auditing Budget vs Budgeted Safety", "budgeted_safety_roc")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Building per-model safety ROC PNGs...")
    build_all_roc_charts()

    print(f"\nDone! {len(os.listdir(IMG_DIR))} images in {IMG_DIR}")
