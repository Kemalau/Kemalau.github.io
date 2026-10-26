#!/usr/bin/env python3
"""Plot the layer distribution of the public-question Top90 neurons.

Run from the repository root with a Python environment containing matplotlib:
    python scripts/build_neuron_distribution.py

The CSV contains the 90 selected native MLP coordinates. Layers 0–17 were
searched in Qwen2.5-7B-Instruct; layers 18–27 were outside the search.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "blog" / "assets"
OUTPUT = ASSETS / "sparse-mlp-neurons"
MODEL_LAYERS = 28
SEARCHED_LAYERS = range(18)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=OUTPUT / "neuron_distribution.csv")
    parser.add_argument("--font", type=Path, default=ASSETS / "fonts" / "et-book-roman.ttf")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()

    with args.csv.open(newline="", encoding="utf-8") as stream:
        coordinates = [(int(row["layer"]), int(row["neuron"]))
                       for row in csv.DictReader(stream)]
    if len(coordinates) != 90 or len(set(coordinates)) != 90:
        raise ValueError("Expected 90 unique neuron coordinates.")
    if any(layer not in SEARCHED_LAYERS or not 0 <= neuron < 18944
           for layer, neuron in coordinates):
        raise ValueError("A coordinate falls outside the recorded search.")
    counts = Counter(layer for layer, _ in coordinates)

    font_manager.fontManager.addfont(args.font)
    font_name = font_manager.FontProperties(fname=args.font).get_name()
    plt.rcParams.update({
        "font.family": font_name,
        "font.size": 13,
        "text.color": "#333C43",
        "axes.labelcolor": "#333C43",
        "xtick.color": "#65717C",
        "ytick.color": "#65717C",
        "axes.unicode_minus": False,
        "svg.fonttype": "path",
        "hatch.linewidth": 0.6,
        "savefig.facecolor": "white",
    })

    fig = plt.figure(figsize=(10, 4.65), dpi=140, facecolor="white")
    ax = fig.add_axes((0.085, 0.17, 0.89, 0.61))
    fig.text(0.085, 0.93, "Selected neurons across layers", fontsize=20,
             ha="left", va="center")
    fig.text(0.085, 0.86, "Public-question Top90 · 90 neurons selected from layers 0–17",
             fontsize=13, color="#65717C", ha="left", va="center")

    ax.axvspan(17.5, MODEL_LAYERS - 0.5, facecolor="#F4F6F5",
               edgecolor="#DCE2DF", hatch="///", linewidth=0, zorder=0)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E8ECEA", linewidth=0.7)
    ax.bar(list(SEARCHED_LAYERS), [counts[layer] for layer in SEARCHED_LAYERS],
           width=0.76, color="#287F7C", linewidth=0, zorder=3)
    for layer in SEARCHED_LAYERS:
        if counts[layer]:
            ax.text(layer, counts[layer] + 0.55, str(counts[layer]),
                    ha="center", va="bottom", color="#287F7C", fontsize=12)

    ax.text(22.5, 13.5, "Outside search\nLayers 18–27", ha="center", va="center",
            fontsize=14, linespacing=1.5, color="#7A857F",
            bbox={"facecolor": "#F4F6F5", "edgecolor": "none", "pad": 8})
    ax.set_xlim(-0.5, MODEL_LAYERS - 0.5)
    ax.set_ylim(0, 27)
    ax.set_xticks([0, 3, 6, 9, 12, 15, 17, 21, 24, 27])
    ax.set_yticks([0, 5, 10, 15, 20, 25])
    ax.set_xlabel("Layer index", labelpad=9)
    ax.set_ylabel("Selected neurons", labelpad=10)
    ax.tick_params(axis="both", length=3, width=0.7, color="#BBC5C6", pad=5)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["bottom", "left"]:
        ax.spines[side].set_color("#BBC5C6")
        ax.spines[side].set_linewidth(0.8)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ["png", "svg"]:
        destination = args.output_dir / f"figure_neuron_distribution.{suffix}"
        fig.savefig(destination, dpi=140)
        if suffix == "svg":
            destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines()) + "\n")
        print(destination.relative_to(ROOT) if destination.is_relative_to(ROOT) else destination)
    plt.close(fig)
    print("Neurons per layer:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
