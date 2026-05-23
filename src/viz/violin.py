"""
Author       : Radon
Date         : 2026-05-23 19:32:48
LastEditors  : Radon
LastEditTime : 2026-05-23 19:55:19
Description  : Plot violin chart
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
METRIC_ORDER = ["LR", "CR"]


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
    conds = ((df["group"].str.startswith("single_", na=False)) | (df["confidence"] == "EXP")) & (df["temperature"] == 1.0) & (df["top_p"] == 1.0)
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
            datalist.append([sut, group, "legal_rate", legal_rate])
            datalist.append([sut, group, "corr_rate", corr_rate])
    proc_df = pd.DataFrame(datalist, columns=["sut", "group", "metric", "rate"])
    return proc_df


def plot_violin_chart(plot_df: pd.DataFrame):
    """Plot violin chart for different groups

    Parameters
    ----------
    plot_df : pd.DataFrame
        Processed dataframe for plotting
    """
    chart_df = plot_df.copy()
    chart_df["rate_pct"] = chart_df["rate"] * 100
    chart_df["metric_label"] = chart_df["metric"].map({"legal_rate": "LR", "corr_rate": "CR"})

    sns.set_theme(style="ticks", rc={"font.family": "serif", "font.serif": FONT_SERIF})
    fig, ax = plt.subplots(figsize=(20, 8))
    sns.violinplot(
        data=chart_df,
        x="group",
        y="rate_pct",
        hue="metric_label",
        hue_order=METRIC_ORDER,
        split=True,
        inner="quart",
        fill=False,
        ax=ax,
    )

    ax.set_xlabel("")
    ax.set_ylabel("Rate (%)", fontsize=LABEL_FONT_SIZE)
    ax.tick_params(axis="both", which="both", labelsize=TICK_FONT_SIZE, colors="black", length=6, width=1.5)
    ax.set_xticks(
        ax.get_xticks(),
        [label.get_text().removeprefix("single_") for label in ax.get_xticklabels()],
        rotation=45,
        ha="right",
        rotation_mode="anchor",
    )

    legend = ax.get_legend()
    if legend:
        handles, labels = ax.get_legend_handles_labels()
        legend.remove()
        fig.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.02),
            ncol=len(METRIC_ORDER),
            frameon=False,
            fontsize=LEGEND_FONT_SIZE,
        )

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.36)
    fig.savefig(os.path.join(os.path.dirname(__file__), "violin.pdf"), dpi=300)
    plt.close(fig)


def main(args: argparse.Namespace):
    df = process_csv(args.csv)
    plot_violin_chart(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot violin chart.")
    parser.add_argument("--csv", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()
    main(args)
