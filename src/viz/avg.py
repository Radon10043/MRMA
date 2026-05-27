"""
Author       : Radon
Date         : 2026-05-25 11:18:44
LastEditors  : Radon
LastEditTime : 2026-05-25 13:01:29
Description  : Calculate average values
"""
import argparse
import os

import pandas as pd

GROUP_COLUMNS = ["sut", "frequency", "type", "group", "confidence", "temperature", "top_p"]
RATE_COLUMNS = ["legal", "correct", "new"]


def main(args: argparse.Namespace):
    """Calculate average values

    Parameters
    ----------
    args : argparse.Namespace
        Arguments
    """
    df = pd.read_csv(args.csv, keep_default_na=False)
    df["temperature"] = pd.to_numeric(df["temperature"])
    df["top_p"] = pd.to_numeric(df["top_p"])

    for column in RATE_COLUMNS:
        df[column] = df[column].eq("TRUE").astype(float)

    avg_df = df.groupby(GROUP_COLUMNS, as_index=False)[RATE_COLUMNS].mean()
    avg_df.columns = GROUP_COLUMNS + ["legal_rate", "correct_rate", "new_rate"]

    output = os.path.join("data", "avg.csv")
    avg_df.to_csv(output, index=False, float_format="%.6f")
    print(f"wrote {output} with {len(avg_df)} grouped rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate data-avg.csv")
    parser.add_argument("--csv", default="data/data.csv", help="Input CSV path")
    args = parser.parse_args()
    main(args)
