"""
Author       : Radon
Date         : 2026-05-23 21:03:00
LastEditors  : Radon
LastEditTime : 2026-05-23 21:18:57
Description  : Plot heatmap chart
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


def format_param(value: float) -> str:
    """Format temperature/top_p values for axis labels."""
    value = float(value)
    return f"{value:.1f}" if value.is_integer() else f"{value:g}"


def process_csv(csv_path: str) -> pd.DataFrame:
    """Process CSV file and return legal-rate data for plotting.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file

    Returns
    -------
    pd.DataFrame
        Processed dataframe with one row for each SUT and temperature+top_p pair
    """
    df = pd.read_csv(csv_path, dtype={"legal": str, "correct": str, "new": str})

    conds = pd.Series(True, index=df.index)
    if "group" in df.columns:
        conds &= df["group"].isin(DEFAULT_GROUPS)
    if "confidence" in df.columns:
        conds &= df["confidence"] == DEFAULT_CONFIDENCE

    chart_df = df[conds].copy()
    chart_df["legal_value"] = chart_df["legal"].str.upper().eq("TRUE").astype(int)
    chart_df["param"] = chart_df.apply(
        lambda row: f"{format_param(row['temperature'])}+{format_param(row['top_p'])}",
        axis=1,
    )

    proc_df = (
        chart_df.groupby(["group", "sut", "temperature", "top_p", "param"], as_index=False)["legal_value"]
        .mean()
        .rename(columns={"legal_value": "legal_rate"})
    )
    return proc_df


def build_pivot_df(plot_df: pd.DataFrame, group: str, combo_order: list[str], sut_order: list[str]) -> pd.DataFrame:
    """Build a heatmap matrix for one group."""
    group_df = plot_df[plot_df["group"] == group]
    return (
        group_df.pivot(index="sut", columns="param", values="legal_rate")
        .reindex(index=sut_order, columns=combo_order)
        * 100
    )


def plot_heatmap_chart(plot_df: pd.DataFrame):
    """Plot legal-rate heatmap for temperature/top_p combinations.

    Parameters
    ----------
    plot_df : pd.DataFrame
        Processed dataframe for plotting
    """
    combo_order = (
        plot_df[["temperature", "top_p", "param"]]
        .drop_duplicates()
        .sort_values(["temperature", "top_p"])["param"]
        .tolist()
    )
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
        pivot_df = build_pivot_df(plot_df, group, combo_order, sut_order)
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
            cbar_kws={"label": "Legal rate (%)", "shrink": 0.75},
            ax=ax,
        )

        ax.set_title(group, fontsize=LABEL_FONT_SIZE, pad=12)
        ax.set_xlabel("Legal Rate", fontsize=LABEL_FONT_SIZE)
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
    fig.savefig(os.path.join(os.path.dirname(__file__), "heatmap-legal.pdf"), dpi=300)
    plt.close(fig)


def main(args: argparse.Namespace):
    """Plot heatmap chart.

    Parameters
    ----------
    args : argparse.Namespace
        Command arguments
    """
    plot_df = process_csv(args.csv)
    plot_heatmap_chart(plot_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot legal-rate heatmap.")
    parser.add_argument("--csv", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()
    main(args)
