"""
Author       : Radon
Date         : 2026-05-23 19:32:48
LastEditors  : Radon
LastEditTime : 2026-06-06 10:56:12
Description  : Plot violin chart
"""

import argparse
import os
from functools import lru_cache
from io import BytesIO

import cairosvg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

FONT_SERIF = ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"]
LABEL_FONT_SIZE = 24
TICK_FONT_SIZE = 20
LEGEND_FONT_SIZE = 20
METRIC_ORDER = ["LR", "CR"]
ICON_SIZE = 72
ICON_ZOOM = 0.28
ICON_X_OFFSET = 0
ICON_Y_OFFSET = 0
MODEL_VENDOR_PATTERNS = (
    ("openai", ("chatgpt", "gpt", "o3", "o4")),
    ("anthropic", ("claude",)),
    ("deepseek", ("deepseek",)),
    ("google", ("gemini",)),
    ("zai", ("glm",)),
    ("xai", ("grok",)),
    ("hunyuan", ("hunyuan",)),
    ("moonshot", ("kimi",)),
    ("qwen", ("qwen",)),
)


@lru_cache(maxsize=None)
def load_svg_icon(svg_path: str, size: int = ICON_SIZE) -> np.ndarray:
    """Convert an SVG icon to a transparent RGBA array for Matplotlib."""
    png_data = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
    image = Image.open(BytesIO(png_data)).convert("RGBA") # type: ignore
    return np.asarray(image)


def vendor_for_model(model_name: str) -> str | None:
    plain_name = model_name.removeprefix("single_").lower()
    for vendor, patterns in MODEL_VENDOR_PATTERNS:
        if any(pattern in plain_name for pattern in patterns):
            return vendor
    return None


def add_vendor_icons(fig, ax, labels: list[str]):
    """Add provider icons before model-name tick labels."""
    icon_dir = os.path.join(os.path.dirname(__file__), "icons")
    renderer = fig.canvas.get_renderer()
    for tick_label, label in zip(ax.get_xticklabels(), labels):
        vendor = vendor_for_model(label)
        if vendor is None:
            continue

        icon_path = os.path.join(icon_dir, f"{vendor}.svg")
        if not os.path.exists(icon_path):
            continue

        label_bbox = tick_label.get_window_extent(renderer=renderer)
        icon_x = label_bbox.x0 + ICON_X_OFFSET
        icon_y = label_bbox.y0 + ICON_Y_OFFSET
        icon_xy = fig.transFigure.inverted().transform((icon_x, icon_y))
        icon = OffsetImage(load_svg_icon(icon_path), zoom=ICON_ZOOM)
        icon_box = AnnotationBbox(
            icon,
            icon_xy,
            xycoords=fig.transFigure,
            frameon=False,
            pad=0,
            box_alignment=(1, 0.5),
            annotation_clip=False,
        )
        fig.add_artist(icon_box)


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
    fig, ax = plt.subplots(figsize=(20, 6))
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
    ax.set_ylim(-40, 140)
    ax.set_yticks(range(-25, 126, 25))
    ax.tick_params(axis="both", which="both", labelsize=TICK_FONT_SIZE, colors="black", length=6, width=1.5)
    tick_labels = [label.get_text().removeprefix("single_") for label in ax.get_xticklabels()]
    ax.set_xticks(
        ax.get_xticks(),
        tick_labels,
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
    fig.subplots_adjust(bottom=0.42)
    fig.canvas.draw()
    add_vendor_icons(fig, ax, tick_labels)
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
