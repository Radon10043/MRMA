"""
Author       : Radon
Date         : 2026-05-23 20:02:31
LastEditors  : Radon
LastEditTime : 2026-05-28 19:31:34
Description  : Plot pairgrid chart
"""
import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

FONT_SERIF = ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"]
LABEL_FONT_SIZE = 24
TICK_FONT_SIZE = 18
TITLE_FONT_SIZE = 22
LEGEND_FONT_SIZE = 20
CONFIDENCE_ORDER = ["EXP", "QUA", "LOG", "LIN", "VAN"]
METRIC_ORDER = ["LR (%)", "CR (%)"]
METRIC_PALETTE = {
    "LR (%)": "#1f77b4",
    "CR (%)": "#ff7f0e",
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
    conds = (df["group"] == "close") & (df["temperature"] == 1.0) & (df["top_p"] == 1.0)
    tmp_df = df[conds].copy()
    datalist = list()
    for sut in tmp_df["sut"].unique():
        for conf in tmp_df["confidence"].unique():
            sub_df = tmp_df[(tmp_df["sut"] == sut) & (tmp_df["confidence"] == conf)]
            total_cand = len(sub_df)
            legal_cand = len(sub_df[sub_df["legal"] == "TRUE"])
            corr_cand = len(sub_df[sub_df["correct"] == "TRUE"])
            legal_rate = legal_cand / total_cand if total_cand > 0 else 0
            corr_rate = corr_cand / total_cand if total_cand > 0 else 0
            datalist.append([sut, conf, "LR (%)", legal_rate])
            datalist.append([sut, conf, "CR (%)", corr_rate])
    proc_df = pd.DataFrame(datalist, columns=["sut", "confidence", "metric", "rate"])
    return proc_df


def plot_pairgrid_chart(plot_df: pd.DataFrame):
    """Plot pairgrid chart for different groups

    Parameters
    ----------
    plot_df : pd.DataFrame
        Processed dataframe for plotting
    """
    chart_df = plot_df.copy()
    chart_df["rate_pct"] = chart_df["rate"] * 100

    confidence_order = [conf for conf in CONFIDENCE_ORDER if conf in chart_df["confidence"].unique()]
    confidence_order.extend(conf for conf in chart_df["confidence"].unique() if conf not in confidence_order)
    sut_order = chart_df["sut"].drop_duplicates().tolist()
    y_pos = {sut: idx for idx, sut in enumerate(sut_order)}
    metric_offsets = {"LR (%)": -0.14, "CR (%)": 0.14}
    wide_df = chart_df.pivot(index=["sut", "metric"], columns="confidence", values="rate_pct").reset_index()
    wide_df.columns.name = None

    sns.set_theme(style="whitegrid", rc={"font.family": "serif", "font.serif": FONT_SERIF})
    fig_width = max(16, 3.4 * len(confidence_order))
    fig_height = max(8, 0.32 * len(sut_order) + 1.8)

    def dotplot(x, y, color, label, **kwargs):
        ax = plt.gca()
        ax.scatter(
            x,
            y.map(y_pos) + metric_offsets[label],
            s=70,
            color=color,
            edgecolor="white",
            linewidth=0.8,
            label=label,
            zorder=3,
        )

    grid = sns.PairGrid(
        data=wide_df,
        x_vars=confidence_order,
        y_vars=["sut"],
        hue="metric",
        hue_order=METRIC_ORDER,
        palette=METRIC_PALETTE,
        height=fig_height,
        aspect=fig_width / (fig_height * len(confidence_order)),
    )
    grid.map(dotplot)
    axes = list(grid.axes.flat)
    fig = grid.figure

    for ax, confidence in zip(axes, confidence_order):

        ax.set_title(confidence, fontsize=TITLE_FONT_SIZE, pad=4)
        ax.set_xlim(-5, 105)
        ax.set_xticks(range(0, 101, 20))
        ax.set_xlabel("")
        ax.tick_params(axis="x", labelsize=TICK_FONT_SIZE, colors="black", length=5, width=1.2, pad=2)
        ax.tick_params(axis="y", labelsize=TICK_FONT_SIZE, colors="black", length=0)
        ax.grid(axis="x", visible=False)
        ax.grid(axis="y", color="#cfcfcf", linewidth=1.0)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

    for ax in axes:
        ax.set_yticks(range(len(sut_order)))
        ax.set_ylim(len(sut_order) - 0.5, -0.5)
    axes[0].set_yticks(range(len(sut_order)), labels=sut_order, fontsize=TICK_FONT_SIZE)
    axes[0].set_ylabel("")
    for ax in axes[1:]:
        ax.set_ylabel("")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        ncol=len(METRIC_ORDER),
        frameon=False,
        fontsize=LEGEND_FONT_SIZE,
    )

    fig.tight_layout()
    fig.subplots_adjust(top=0.92, bottom=0.09, wspace=0.22)
    fig.savefig(os.path.join(os.path.dirname(__file__), "pairgrid.pdf"), dpi=300)
    plt.close(fig)


def main(args: argparse.Namespace):
    df = process_csv(args.csv)
    plot_pairgrid_chart(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot pairgrid chart.")
    parser.add_argument("--csv", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()
    main(args)
