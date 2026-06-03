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


def read_profile(csv_path: Path) -> tuple[list[float], list[float]]:
    times: list[float] = []
    depths: list[float] = []

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            times.append(float(row["time_ms"]))
            depths.append(float(row["depth_m"]))

    return times, depths


def render_profile(source_name: str, target_name: str) -> None:
    csv_path = FIGURE_DIR / source_name
    pdf_path = FIGURE_DIR / target_name

    times, depths = read_profile(csv_path)

    def format_time(milliseconds: float, _position: int) -> str:
        total_seconds = int(round(milliseconds / 1000.0))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"

        return f"{minutes}:{seconds:02d}"

    figure, axis = plt.subplots(figsize=(7.2, 3.8))
    axis.plot(times, depths, color="#0f4c81", linewidth=1.8)
    axis.xaxis.set_major_formatter(FuncFormatter(format_time))
    axis.set_xlabel("Time (h:min:s)")
    axis.set_ylabel("Depth (m)")
    axis.invert_yaxis()
    axis.grid(True, linewidth=0.4, alpha=0.35)
    axis.margins(x=0)
    figure.tight_layout()
    figure.savefig(pdf_path, format="pdf")
    plt.close(figure)


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    render_profile("profile_20m.csv", "profile_20m.pdf")
    render_profile("profile_50m.csv", "profile_50m.pdf")
    render_profile("profile_90m.csv", "profile_90m.pdf")


if __name__ == "__main__":
    main()