#!/usr/bin/env python3

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


def read_profile(csv_path: Path) -> tuple[list[float], list[float]]:
    times: list[float] = []
    depths: list[float] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                times.append(float(row["time_ms"]))
                depths.append(float(row["depth_m"]))
            except (KeyError, ValueError):
                continue
    return times, depths


def format_time(milliseconds: float, _position: int) -> str:
    total_seconds = int(round(milliseconds / 1000.0))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def render_depth(depth: str) -> None:
    figure, axis = plt.subplots(figsize=(7.2, 3.8))

    plotted_any = False
    for config_key, config_label in CONFIG_LABELS.items():
        csv_path = FIGURE_DIR / config_key / depth / "profile.csv"
        if not csv_path.exists():
            continue
        times, depths_data = read_profile(csv_path)
        if not times:
            continue
        axis.plot(
            times,
            depths_data,
            label=f"{config_label} (n={len(times)})",
            color=CONFIG_COLORS[config_key],
            linewidth=1.8,
        )
        plotted_any = True

    if not plotted_any:
        plt.close(figure)
        return

    axis.invert_yaxis()
    axis.xaxis.set_major_formatter(FuncFormatter(format_time))
    axis.set_xlabel("Time (h:min:s)")
    axis.set_ylabel("Depth (m)")
    axis.legend(fontsize=8)
    axis.grid(True, linewidth=0.4, alpha=0.35)
    axis.margins(x=0)
    figure.tight_layout()

    out_path = FIGURE_DIR / f"profile_{depth}.pdf"
    figure.savefig(out_path, format="pdf")
    plt.close(figure)
    print(f"wrote {out_path}")


def main() -> None:
    for depth in DEPTHS:
        render_depth(depth)


if __name__ == "__main__":
    main()
