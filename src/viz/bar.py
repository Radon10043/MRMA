"""
Author       : Radon
Date         : 2026-05-21 22:20:21
LastEditors  : Radon
LastEditTime : 2026-06-05 16:35:50
Description  : Plot bar chart
"""

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

FONT_SERIF = ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"]
GROUP_ORDER = ["close", "hybrid", "open"]
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
    df = pd.read_csv(csv_path, dtype={"legal": str, "correct": str, "new": str})
    conds = df["group"].isin(["close", "hybrid", "open"]) & (df["temperature"] == 1.0) & (df["top_p"] == 1.0) & (df["confidence"] == "EXP")
    tmp_df = df[conds]
    datalist = list()
    for sut in tmp_df["sut"].unique():
        for group in tmp_df["group"].unique():
            sub_df = tmp_df[(tmp_df["sut"] == sut) & (tmp_df["group"] == group)]
            total_cand = len(sub_df)
            new_cand = len(sub_df[sub_df["new"] == "TRUE"])
            new_rate = new_cand / total_cand if total_cand > 0 else 0
            datalist.append([sut, group, new_rate])
    proc_df = pd.DataFrame(datalist, columns=["sut", "group", "new_rate"])
    return proc_df


def plot_bar_chart(plot_df: pd.DataFrame):
    """Plot bar chart for different type of SUT

    Parameters
    ----------
    plot_df : pd.DataFrame
        Processed dataframe for plotting
    """
    # Sort SUTs by correct rate in the selected group in descending order.
    chart_df = plot_df.copy()
    sut_order = (
        chart_df[chart_df["group"] == "close"]
        .sort_values(["new_rate", "sut"], ascending=[False, True])["sut"]
        .tolist()
    )

    chart_df["sut"] = pd.Categorical(chart_df["sut"], categories=sut_order, ordered=True)
    chart_df.sort_values(["sut", "group"], inplace=True)
    chart_df["new_rate_pct"] = chart_df["new_rate"] * 100

    sns.set_theme(style="ticks", rc={"font.family": "serif", "font.serif": FONT_SERIF})
    fig, ax = plt.subplots(figsize=(20, 3))
    sns.barplot(
        data=chart_df,
        x="sut",
        y="new_rate_pct",
        hue="group",
        hue_order=GROUP_ORDER,
        palette=GROUP_PALETTE,
        ax=ax,
    )

    ax.set_xlabel("")
    ax.set_ylabel("IR (%)")
    ax.set_ylim(0, 105)
    ax.set_yticks(range(0, 101, 20))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.25),
        ncol=len(GROUP_ORDER),
        title="",
        frameon=False,
    )

    fig.tight_layout()
    fig.subplots_adjust(top=0.9, wspace=0.35)
    fig.savefig(os.path.join(os.path.dirname(__file__), "bar.pdf"), dpi=300)
    plt.close(fig)


def main(args: argparse.Namespace):
    """Plot bar chart for different categories of SUT

    Parameters
    ----------
    args : argparse.Namespace
        Command arguments
    """
    plot_df = process_csv(args.csv)
    plot_bar_chart(plot_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot bar chart")
    parser.add_argument("--csv", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()
    main(args)
