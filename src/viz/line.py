"""
Author       : Radon
Date         : 2026-05-21 19:54:42
LastEditors  : Radon
LastEditTime : 2026-05-21 22:16:49
Description  : Plot line chart
"""
import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

LABEL_FONT_SIZE = 26
TICK_FONT_SIZE = 22
LEGEND_FONT_SIZE = 22
LEGEND_TITLE_FONT_SIZE = 24
LINE_WIDTH = 3
MARKER_SIZE = 10
GROUP_ORDER = ["close", "hybrid", "open"]
GROUP_MARKERS = {
    "close": "o",
    "hybrid": "^",
    "open": "s",
}
GROUP_PALETTE = {
    "close": "#1f77b4",
    "hybrid": "#ff7f0e",
    "open": "#808080",
}


def process_csv(csv_path: str) -> pd.DataFrame:
    """Process CSV file and return the processed dataframe

    Parameters
    ----------
    csv_path : str
        Path to the CSV file

    Returns
    -------
    pd.DataFrame
        Processed dataframe
    """
    df = pd.read_csv(csv_path, dtype={
        "legal": str, "correct": str, "new": str
    })
    conds = (
        df["group"].isin(["close", "hybrid", "open"]) &
        (df["temperature"] == 1.0) &
        (df["top_p"] == 1.0) &
        (df["confidence"] == "EXP")
    )
    tmp_df = df[conds]
    datalist = list()
    for sut in tmp_df["sut"].unique():
        for group in tmp_df["group"].unique():
            sub_df = tmp_df[(tmp_df["sut"] == sut) & (tmp_df["group"] == group)]
            total_cand = len(sub_df)
            legal_cand = len(sub_df[sub_df["legal"] == "TRUE"])
            corr_cand = len(sub_df[sub_df["correct"] == "TRUE"])
            legal_rate = legal_cand / total_cand if total_cand > 0 else 0
            corr_rate = corr_cand / total_cand if total_cand > 0 else 0
            datalist.append([sut, group, legal_rate, corr_rate])
    proc_df = pd.DataFrame(datalist, columns=["sut", "group", "legal_rate", "corr_rate"])
    return proc_df


def plot_legal_chart(plot_df: pd.DataFrame):
    """Plot the line chart of legal rate

    Parameters
    ----------
    plot_df : pd.DataFrame
        Dataframe containing the data to be plotted
    """
    # Sort SUTs by legal rate in the selected group in descending order.
    chart_df = plot_df.copy()
    sut_order = (
        chart_df[chart_df["group"] == "close"]
        .sort_values(["legal_rate", "sut"], ascending=[False, True])["sut"]
        .tolist()
    )

    chart_df["sut"] = pd.Categorical(chart_df["sut"], categories=sut_order, ordered=True)
    chart_df.sort_values(["sut", "group"], inplace=True)
    chart_df["legal_rate_pct"] = chart_df["legal_rate"] * 100

    sns.set_theme(
        style="white",
        rc={
            "axes.labelsize": LABEL_FONT_SIZE,
            "xtick.labelsize": TICK_FONT_SIZE,
            "ytick.labelsize": TICK_FONT_SIZE,
            "legend.fontsize": LEGEND_FONT_SIZE,
            "legend.title_fontsize": LEGEND_TITLE_FONT_SIZE,
        },
    )

    fig, ax = plt.subplots(figsize=(30, 10))
    sns.lineplot(
        x="sut",
        y="legal_rate_pct",
        hue="group",
        hue_order=GROUP_ORDER,
        palette=GROUP_PALETTE,
        style="group",
        style_order=GROUP_ORDER,
        markers=GROUP_MARKERS,
        dashes=False,
        data=chart_df,
        ax=ax,
        sort=False,
        linewidth=LINE_WIDTH,
        markersize=MARKER_SIZE,
    )

    ax.set_xlabel("Software Under Test", fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel("LR (%)", fontsize=LABEL_FONT_SIZE)
    ax.set_ylim(0, 105)
    ax.set_yticks(range(0, 105, 10))
    ax.tick_params(axis="both", labelsize=TICK_FONT_SIZE)
    ax.grid(False)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("black")
        spine.set_linewidth(1.5)

    legend = ax.get_legend()
    if legend:
        legend.set_title("Group")
        legend.set_loc("lower left")
        legend.get_title().set_fontsize(LEGEND_TITLE_FONT_SIZE)
        for text in legend.get_texts():
            text.set_fontsize(LEGEND_FONT_SIZE)

    fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(__file__), "legal.pdf"), dpi=300)
    plt.close(fig)


def plot_corr_rate(plot_df: pd.DataFrame):
    """Plot the line chart of correct rate

    Parameters
    ----------
    plot_df : pd.DataFrame
        Dataframe containing the data to be plotted
    """
    # Sort SUTs by correct rate in the selected group in descending order.
    chart_df = plot_df.copy()
    sut_order = (
        chart_df[chart_df["group"] == "close"]
        .sort_values(["corr_rate", "sut"], ascending=[False, True])["sut"]
        .tolist()
    )

    chart_df["sut"] = pd.Categorical(chart_df["sut"], categories=sut_order, ordered=True)
    chart_df.sort_values(["sut", "group"], inplace=True)
    chart_df["corr_rate_pct"] = chart_df["corr_rate"] * 100

    sns.set_theme(
        style="white",
        rc={
            "axes.labelsize": LABEL_FONT_SIZE,
            "xtick.labelsize": TICK_FONT_SIZE,
            "ytick.labelsize": TICK_FONT_SIZE,
            "legend.fontsize": LEGEND_FONT_SIZE,
            "legend.title_fontsize": LEGEND_TITLE_FONT_SIZE,
        },
    )

    fig, ax = plt.subplots(figsize=(30, 10))
    sns.lineplot(
        x="sut",
        y="corr_rate_pct",
        hue="group",
        hue_order=GROUP_ORDER,
        palette=GROUP_PALETTE,
        style="group",
        style_order=GROUP_ORDER,
        markers=GROUP_MARKERS,
        dashes=False,
        data=chart_df,
        ax=ax,
        sort=False,
        linewidth=LINE_WIDTH,
        markersize=MARKER_SIZE,
    )

    ax.set_xlabel("Software Under Test", fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel("CR (%)", fontsize=LABEL_FONT_SIZE)
    ax.set_ylim(0, 105)
    ax.set_yticks(range(0, 105, 10))
    ax.tick_params(axis="both", labelsize=TICK_FONT_SIZE)
    ax.grid(False)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("black")
        spine.set_linewidth(1.5)

    legend = ax.get_legend()
    if legend:
        legend.set_title("Group")
        legend.set_loc("lower left")
        legend.get_title().set_fontsize(LEGEND_TITLE_FONT_SIZE)
        for text in legend.get_texts():
            text.set_fontsize(LEGEND_FONT_SIZE)

    fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(__file__), "correct.pdf"), dpi=300)
    plt.close(fig)


def main(args: argparse.Namespace):
    """Plot the line chart

    Parameters
    ----------
    args : argparse.Namespace
        Command arguments
    """
    plot_df = process_csv(args.csv)
    plot_legal_chart(plot_df)
    plot_corr_rate(plot_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot legality and accuracy rates for MR candidates.")
    parser.add_argument("--csv", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()
    main(args)
