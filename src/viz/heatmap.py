import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ..utils import *


def main(args: argparse.Namespace):
    df = pd.read_excel(args.excel, sheet_name=args.sheet, engine="calamine")
    df["test_result"] = df["test_result"].map({True: 1, False: 0, "TIMEOUT": 0.5})

    # Preprocess data
    pivot_df = df.pivot_table(
        index=["sut", "group"],
        columns=["iden_temp", "iden_top_p"],
        values="test_result",
        aggfunc="mean",
    )
    pivot_df.sort_index(
        axis=0,
        inplace=True,
        key=lambda x: x.str.lower(),
        ascending=True,
    )

    # Plot heatmap
    sns.set_theme(style="white")
    plt.figure(figsize=(12, 20))
    cmap = sns.color_palette("light:#0B62DD", as_cmap=True)
    sns.heatmap(pivot_df, cmap=cmap, linewidths=0.5, cbar_kws={"shrink": 0.5})

    plt.tight_layout()
    plt.savefig(args.output, dpi=300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot heatmap.")
    parser.add_argument("--excel", type=str, required=True, help="Path to the Excel file")
    parser.add_argument("--sheet", type=str, required=True, help="Name of the sheet to plot")
    parser.add_argument("--output", type=str, default=os.path.join(os.path.dirname(__file__), "heatmap.pdf"), help="Path to the output file")
    args = parser.parse_args()
    main(args)
