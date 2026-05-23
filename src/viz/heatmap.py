"""
Author       : Radon
Date         : 2026-05-23 21:03:00
LastEditors  : Radon
LastEditTime : 2026-05-24 00:13:45
Description  : Plot legal-rate and correct-rate heatmap charts
"""

import argparse
import os

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import seaborn as sns

FONT_SERIF = ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"]
LABEL_FONT_SIZE = 24
TICK_FONT_SIZE = 18
CBAR_FONT_SIZE = 18
DEFAULT_GROUPS = ["close", "hybrid", "open"]
DEFAULT_CONFIDENCE = "EXP"
METRICS = {
    "legal": {
        "source_col": "legal",
        "rate_col": "legal_rate",
        "x_label": "Legal Rate",
        "cbar_label": "Legal rate (%)",
        "output": "heatmap-legal.pdf",
    },
    "correct": {
        "source_col": "correct",
        "rate_col": "corr_rate",
        "x_label": "Correct Rate",
        "cbar_label": "Correct rate (%)",
        "output": "heatmap-corr.pdf",
    },
}


def format_param(value: float) -> str:
    """Format temperature/top_p values for axis labels."""
    value = float(value)
    return f"{value:.1f}" if value.is_integer() else f"{value:g}"


def load_chart_df(csv_path: str) -> pd.DataFrame:
    """Load and filter CSV data used by all heatmaps."""
    df = pd.read_csv(csv_path, dtype={"legal": str, "correct": str, "new": str})

    conds = pd.Series(True, index=df.index)
    if "group" in df.columns:
        conds &= df["group"].isin(DEFAULT_GROUPS)
    if "confidence" in df.columns:
        conds &= df["confidence"] == DEFAULT_CONFIDENCE

    chart_df = df[conds].copy()
    chart_df["param"] = chart_df.apply(
        lambda row: f"{format_param(row['temperature'])}+{format_param(row['top_p'])}",
        axis=1,
    )
    return chart_df


def process_metric(chart_df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Process filtered CSV data and return one metric's rate data."""
    metric_cfg = METRICS[metric]
    value_col = f"{metric}_value"
    chart_df = chart_df.copy()
    chart_df[value_col] = chart_df[metric_cfg["source_col"]].str.upper().eq("TRUE").astype(int)
    proc_df = chart_df.groupby(["group", "sut", "temperature", "top_p", "param"])[value_col].mean().reset_index().rename(columns={value_col: metric_cfg["rate_col"]})
    return proc_df


def build_pivot_df(plot_df: pd.DataFrame, group: str, combo_order: list[str], sut_order: list[str], rate_col: str) -> pd.DataFrame:
    """Build a heatmap matrix for one group."""
    group_df = plot_df[plot_df["group"] == group]
    return group_df.pivot(index="sut", columns="param", values=rate_col).reindex(index=sut_order, columns=combo_order) * 100


def plot_heatmap_chart(plot_df: pd.DataFrame, metric: str):
    """Plot one heatmap for temperature/top_p combinations."""
    metric_cfg = METRICS[metric]
    combo_order = plot_df[["temperature", "top_p", "param"]].drop_duplicates().sort_values(["temperature", "top_p"])["param"].tolist()
    sut_order = sorted(plot_df["sut"].unique(), key=str.lower)
    group_order = [group for group in DEFAULT_GROUPS if group in plot_df["group"].unique()]

    sns.set_theme(style="white", rc={"font.family": "serif", "font.serif": FONT_SERIF})
    fig_width = max(18, 4.2 * len(group_order) + 2.2 * len(combo_order))
    fig_height = max(8, 0.35 * len(sut_order) + 2.5)
    fig, axes = plt.subplots(1, len(group_order), figsize=(fig_width, fig_height), sharey=True)
    if len(group_order) == 1:
        axes = [axes]

    cmap = LinearSegmentedColormap.from_list("blue_white_red", ["#3B6FB6", "#FFFFFF", "#B22222"])
    heatmap = None
    for idx, (ax, group) in enumerate(zip(axes, group_order)):
        pivot_df = build_pivot_df(
            plot_df,
            group,
            combo_order,
            sut_order,
            metric_cfg["rate_col"],
        )
        heatmap = sns.heatmap(
            pivot_df,
            cmap=cmap,
            vmin=0,
            vmax=100,
            center=50,
            linewidths=0.5,
            linecolor="white",
            annot=True,
            fmt=".1f",
            annot_kws={"fontsize": 9},
            cbar=idx == len(group_order) - 1,
            cbar_kws={"label": metric_cfg["cbar_label"], "shrink": 0.75},
            ax=ax,
        )

        ax.set_title(group, fontsize=LABEL_FONT_SIZE, pad=12)
        ax.set_xlabel(metric_cfg["x_label"], fontsize=LABEL_FONT_SIZE)
        ax.set_ylabel("")
        ax.tick_params(axis="x", labelsize=TICK_FONT_SIZE, rotation=45)
        ax.tick_params(axis="y", labelsize=TICK_FONT_SIZE, rotation=0)
        plt.setp(ax.get_xticklabels(), ha="right", rotation_mode="anchor")

    if heatmap is not None:
        # seaborn may return a heatmap whose collection has no colorbar attached
        cbar = getattr(heatmap.collections[0], "colorbar", None)
        if cbar is not None:
            cbar.ax.tick_params(labelsize=CBAR_FONT_SIZE)
            cbar.ax.yaxis.label.set_size(CBAR_FONT_SIZE)

    fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(__file__), metric_cfg["output"]), dpi=300)
    plt.close(fig)


def plot_all_heatmaps(csv_path: str):
    """Plot both legal-rate and correct-rate heatmaps."""
    chart_df = load_chart_df(csv_path)
    for metric in METRICS:
        plot_df = process_metric(chart_df, metric)
        plot_heatmap_chart(plot_df, metric)


def main(args: argparse.Namespace):
    """Plot heatmap charts.

    Parameters
    ----------
    args : argparse.Namespace
        Command arguments
    """
    plot_all_heatmaps(args.csv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot legal-rate and correct-rate heatmaps.")
    parser.add_argument("--csv", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()
    main(args)
