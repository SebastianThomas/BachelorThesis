#!/usr/bin/env python3
"""Generate a LaTeX table of flash-log depth-error statistics.

Reads flash_profile_diff_summary.csv from each config x depth combination and
emits a single LaTeX table with min / max / avg / median depth error columns.

Inputs:  figures/results/{config}/{depth}/flash_profile_diff_summary.csv
Outputs: content/generated/05_results_flash_profile_diff_summary.tex
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "content" / "generated"
INPUT_ROOT = ROOT / "figures" / "results"

CONFIG_LABELS = {
    "baseline-fixed": "Baseline fixed",
    "exp":            "Exponential",
    "lin-exp":        "Linear-exponential",
}

DEPTHS = ["20m", "50m", "90m"]

OUTPUT_NAME = "05_results_flash_profile_diff_summary.tex"
CAPTION = "Flash log depth accuracy: signed error between logged and interpolated dive profile depth"
TABLE_LABEL = "tab:flash_profile_diff_summary"


def read_summary(csv_path: Path) -> dict[str, str]:
    with csv_path.open(newline="") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    if not rows:
        raise RuntimeError(f"empty summary: {csv_path}")
    return rows[0]


def format_row(config: str, depth: str, row: dict[str, str]) -> str:
    count = row["count"]
    mn = float(row["min_diff_m"])
    mx = float(row["max_diff_m"])
    avg = float(row["avg_diff_m"])
    median = float(row["median_diff_m"])
    return (
        f"{config} & {depth} & {count} & "
        f"{mn:.3f} & {mx:.3f} & {avg:.3f} & {median:.3f} \\\\"
    )


def build_table() -> str:
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\renewcommand{\\arraystretch}{1.15}",
        "\\begin{tabular}{llrrrrr}",
        "\\toprule",
        "Configuration & Profile & Points & Min [m] & Max [m] & Avg [m] & Median [m] \\\\",
        "\\midrule",
    ]

    for config_key, config_label in CONFIG_LABELS.items():
        for depth in DEPTHS:
            csv_path = INPUT_ROOT / config_key / depth / "flash_profile_diff_summary.csv"
            row = read_summary(csv_path)
            lines.append(format_row(config_label, depth, row))

    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            f"\\caption{{{CAPTION}}}",
            f"\\label{{{TABLE_LABEL}}}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / OUTPUT_NAME
    output_file.write_text(build_table(), encoding="utf-8")
    print(f"wrote {output_file}")


if __name__ == "__main__":
    main()
