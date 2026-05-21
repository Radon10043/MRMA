"""
Author       : Radon
Date         : 2026-05-21 22:20:21
LastEditors  : Radon
LastEditTime : 2026-05-22 00:33:17
Description  : Plot box chart
"""

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

FONT_SERIF = ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"]
LABEL_FONT_SIZE = 24
TICK_FONT_SIZE = 20
LEGEND_FONT_SIZE = 20
GROUP_ORDER = ["close", "hybrid", "open"]
GROUP_PALETTE = {
    "close": "#9ecae1",
    "hybrid": "#fdd0a2",
    "open": "#bdbdbd",
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
    df = pd.read_csv(csv_path, dtype={"legal": str, "correct": str, "new": str})
    conds = df["group"].isin(["close", "hybrid", "open"]) & (df["temperature"] == 1.0) & (df["top_p"] == 1.0) & (df["confidence"] == "EXP")
    tmp_df = df[conds]
    datalist = list()
    for sut in tmp_df["sut"].unique():
        for group in tmp_df["group"].unique():
            sub_df = tmp_df[(tmp_df["sut"] == sut) & (tmp_df["group"] == group)]
            sut_type = sub_df["type"].iloc[0]
            total_cand = len(sub_df)
            legal_cand = len(sub_df[sub_df["legal"] == "TRUE"])
            corr_cand = len(sub_df[sub_df["correct"] == "TRUE"])
            legal_rate = legal_cand / total_cand if total_cand > 0 else 0
            corr_rate = corr_cand / total_cand if total_cand > 0 else 0
            datalist.append([sut, group, sut_type, legal_rate, corr_rate])
    proc_df = pd.DataFrame(datalist, columns=["sut", "group", "type", "legal_rate", "corr_rate"])
    return proc_df


def plot_box_chart(plot_df: pd.DataFrame):
    """Plot box chart for different type of SUT

    Parameters
    ----------
    plot_df : pd.DataFrame
        Processed dataframe for plotting
    """
    chart_df = plot_df.copy()
    chart_df["legal_rate_pct"] = chart_df["legal_rate"] * 100
    chart_df["corr_rate_pct"] = chart_df["corr_rate"] * 100

    sns.set_theme(style="ticks", rc={"font.family": "serif", "font.serif": FONT_SERIF})
    fig, axes = plt.subplots(1, 2, figsize=(13, 7), sharex=True)
    common_kwargs = {
        "data": chart_df,
        "x": "type",
        "hue": "group",
        "hue_order": GROUP_ORDER,
        "palette": GROUP_PALETTE,
        "width": 0.52,
        "linewidth": 1.5,
        "boxprops": {"edgecolor": "black"},
        "whiskerprops": {"color": "black", "linewidth": 1.5},
        "capprops": {"color": "black", "linewidth": 1.5},
        "medianprops": {"color": "black", "linewidth": 1.5},
        "flierprops": {
            "markeredgecolor": "black",
            "markerfacecolor": "white",
            "markersize": 4,
        },
    }

    sns.boxplot(y="legal_rate_pct", ax=axes[0], **common_kwargs)
    sns.boxplot(y="corr_rate_pct", ax=axes[1], **common_kwargs)

    axes[0].set_ylabel("LR (%)", fontsize=LABEL_FONT_SIZE)
    axes[1].set_ylabel("CR (%)", fontsize=LABEL_FONT_SIZE)

    for ax in axes:
        ax.set_xlabel("")
        ax.set_facecolor("none")
        ax.grid(False)
        ax.tick_params(axis="both", which="both", labelsize=TICK_FONT_SIZE, colors="black", length=6, width=1.5)
        ax.set_ylim(-5, 105)
        ax.set_yticks(range(0, 101, 20))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("black")
        ax.spines["bottom"].set_color("black")
        ax.spines["left"].set_linewidth(1.5)
        ax.spines["bottom"].set_linewidth(1.5)
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

    handles, labels = axes[0].get_legend_handles_labels()
    for ax in axes:
        legend = ax.get_legend()
        if legend:
            legend.remove()
    fig.legend(handles, labels, loc="upper center", ncol=len(labels), frameon=False, fontsize=LEGEND_FONT_SIZE)

    fig.tight_layout()
    fig.subplots_adjust(top=0.88, wspace=0.35)
    fig.savefig(os.path.join(os.path.dirname(__file__), "box.pdf"), dpi=300)
    plt.close(fig)


def main(args: argparse.Namespace):
    """Plot box chart for different categories of SUT

    Parameters
    ----------
    args : argparse.Namespace
        Command arguments
    """
    plot_df = process_csv(args.csv)
    plot_box_chart(plot_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot box chart")
    parser.add_argument("--csv", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()
    main(args)
