#!/usr/bin/env python3

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "content" / "generated"
INPUT_ROOT = ROOT / "figures" / "results"

CONFIG_LABELS = {
    "baseline-fixed": "Baseline fixed",
    "exp": "Exponential",
    "lin-exp": "Linear-exponential",
}

DEPTHS = ["20m", "50m", "90m"]

SUMMARIES = [
    {
        "output_name": "05_results_o2tox_decision_summary.tex",
        "row_label": "dive.o2_tox.rate",
        "caption": "O2Tox decision summary across profiles and configurations",
        "table_label": "tab:o2tox_decision_summary",
    },
    {
        "output_name": "05_results_decompression_decision_summary.tex",
        "row_label": "dive.deco_schedule.rate",
        "caption": "Decompression decision summary across profiles and configurations",
        "table_label": "tab:decision_summary",
    },
    {
        "output_name": "05_results_display_refresh_decision_summary.tex",
        "row_label": "dive.display_refresh.rate",
        "caption": "Display refresh decision summary across profiles and configurations",
        "table_label": "tab:display_refresh_decision_summary",
    },
    {
        "output_name": "05_results_flash_log_decision_summary.tex",
        "row_label": "flash.log.rate",
        "caption": "Flash log rate decision summary across profiles and configurations",
        "table_label": "tab:flash_log_decision_summary",
    },
]


def read_summary_row(csv_path: Path, row_label: str) -> dict[str, str] | None:
    if not csv_path.exists():
        return None
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(line for line in handle if not line.startswith("#"))
        for row in rows:
            if row["label"] == row_label:
                return row
    return None


def format_row(config: str, depth: str, row: dict[str, str]) -> str:
    return (
        f"{config} & {depth} & {row['count']} & {row['due_count']} & "
        f"{row['not_due_count']} & {float(row['avg_skipped_seconds']):.3f} & "
        f"{float(row['max_skipped_seconds']):.3f} \\\\"
    )


def build_table(row_label: str, caption: str, table_label: str) -> str:
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\renewcommand{\\arraystretch}{1.15}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{llrrrrr}",
        "\\toprule",
        "Configuration & Profile & Decisions & Due & Not due & Avg skipped [s] & Max skipped [s] \\\\",
        "\\midrule",
    ]

    for config_key, config_label in CONFIG_LABELS.items():
        for depth in DEPTHS:
            csv_path = INPUT_ROOT / config_key / depth / "decision.csv"
            row = read_summary_row(csv_path, row_label)
            if row is None:
                print(f"warning: {row_label} not found in {csv_path}", file=sys.stderr)
                lines.append(f"{config_label} & {depth} & \\multicolumn{{5}}{{c}}{{--}} \\\\")
            else:
                lines.append(format_row(config_label, depth, row))

    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}%",
            "}",
            f"\\caption{{{caption}}}",
            f"\\label{{{table_label}}}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for summary in SUMMARIES:
        output_file = OUTPUT_DIR / summary["output_name"]
        output_file.write_text(
            build_table(summary["row_label"], summary["caption"], summary["table_label"]),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
