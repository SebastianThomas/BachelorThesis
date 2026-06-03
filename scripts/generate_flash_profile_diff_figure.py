#!/usr/bin/env python3
"""Generate per-depth PDF figures of flash-log depth error across configurations.

For each depth profile (20m, 50m, 90m), plots the signed depth difference
(flash_depth - interpolated_profile_depth) over time for all three algorithm
configurations. One PDF per depth.

Inputs:  figures/results/{config}/{depth}/flash_profile_diff.csv
Outputs: figures/results/flash_profile_diff_{depth}.pdf
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "figures" / "results"

CONFIG_LABELS = {
    "lin-exp":        "Linear-exponential",
    "baseline-fixed": "Baseline fixed",
    "exp":            "Exponential",
}

CONFIG_COLORS = {
    "lin-exp":        "#0f4c81",
    "baseline-fixed": "#e05c1a",
    "exp":            "#2a9d2a",
}

DEPTHS = ["20m", "50m", "90m"]


def read_diff(csv_path: Path) -> tuple[list[float], list[float]]:
    times: list[float] = []
    diffs: list[float] = []
    with csv_path.open(newline="") as f:
        for row in csv.DictReader(line for line in f if not line.startswith("#")):
            try:
                times.append(float(row["time_ms"]))
                diffs.append(float(row["depth_diff_m"]))
            except (KeyError, ValueError):
                continue
    return times, diffs


def format_time(milliseconds: float, _pos: int) -> str:
    total_seconds = int(round(milliseconds / 1000.0))
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def render_depth(depth: str) -> None:
    figure, axis = plt.subplots(figsize=(7.2, 3.8))

    plotted_any = False
    for config_key, config_label in CONFIG_LABELS.items():
        csv_path = FIGURE_DIR / config_key / depth / "flash_profile_diff.csv"
        if not csv_path.exists():
            continue
        times, diffs = read_diff(csv_path)
        if not times:
            continue
        axis.plot(
            times,
            diffs,
            label=f"{config_label} (n={len(times)})",
            color=CONFIG_COLORS[config_key],
            linewidth=1.6,
            marker="o",
            markersize=3.5,
        )
        plotted_any = True

    if not plotted_any:
        plt.close(figure)
        return

    axis.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.6)
    axis.invert_yaxis()
    axis.xaxis.set_major_formatter(FuncFormatter(format_time))
    axis.set_xlabel("Time (min:s)")
    axis.set_ylabel("Depth error (m)  [down = flash deeper]")
    axis.legend(fontsize=8)
    axis.grid(True, linewidth=0.4, alpha=0.35)
    axis.margins(x=0.02)
    figure.tight_layout()

    out_path = FIGURE_DIR / f"flash_profile_diff_{depth}.pdf"
    figure.savefig(out_path, format="pdf")
    plt.close(figure)
    print(f"wrote {out_path}")


def main() -> None:
    for depth in DEPTHS:
        render_depth(depth)


if __name__ == "__main__":
    main()
