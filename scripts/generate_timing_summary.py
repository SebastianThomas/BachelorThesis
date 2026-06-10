#!/usr/bin/env python3
"""Generate LaTeX timing tables from summary.csv files.

nanos values in the logs are corrupted by RTT field-tearing, so all time values
are derived from cycles using CLOCK_HZ = 16 MHz (62.5 ns/cycle).

Table families (structurally identical within each family):
  - Rate tables:        Samples | Avg cyc | Avg t | Min cyc | Min t | Max cyc | Max t | Total cyc | Total [ms]
  - Computation tables: Samples | Avg cyc | Avg t | Med cyc | Med t | Min cyc | Min t | Max cyc | Max t | Total cyc | Total [total_unit]
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "content" / "generated"
INPUT_ROOT = ROOT / "figures" / "results"

CLOCK_HZ = 16_000_000  # STM32L476 configured at 16 MHz

CONFIG_LABELS = {
    "baseline-fixed": "Baseline fixed",
    "exp": "Exponential",
    "lin-exp": "Linear-exponential",
}

DEPTHS = ["20m", "50m", "90m", "200m"]


def read_timing_row(csv_path: Path, row_label: str) -> dict[str, str] | None:
    if not csv_path.exists():
        return None
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(line for line in handle if not line.startswith("#"))
        for row in rows:
            if row["label"] == row_label:
                return row
    return None


def cycles_to_unit(cycles: int, unit: str) -> float:
    if unit == "s":
        return cycles / CLOCK_HZ
    if unit == "ms":
        return cycles / (CLOCK_HZ / 1_000)
    return cycles / (CLOCK_HZ / 1_000_000)  # us


def unit_col_header(unit: str) -> str:
    if unit == "s":
        return "[\\si{\\second}]"
    if unit == "ms":
        return "[\\si{\\milli\\second}]"
    return "[\\si{\\micro\\second}]"


def total_precision(unit: str) -> int:
    return 3 if unit == "s" else (1 if unit == "us" else 1)


# ---------------------------------------------------------------------------
# Rate table family
# Columns: Samples | Avg cyc | Avg t | Min cyc | Min t | Max cyc | Max t | Total cyc | Total [ms]
# ---------------------------------------------------------------------------

def format_rate_row(config: str, depth: str, row: dict[str, str],
                    unit: str, precision: int, total_unit: str) -> str:
    count     = int(row["count"])
    avg_cyc   = int(row["avg_cycles"])
    min_cyc   = int(row["min_cycles"])
    max_cyc   = int(row["max_cycles"])
    sum_cyc   = int(row["sum_cycles"])
    fmt       = f".{precision}f"
    tfmt      = f".{total_precision(total_unit)}f"
    return (
        f"{config} & {depth} & {count} & "
        f"{avg_cyc} & {cycles_to_unit(avg_cyc, unit):{fmt}} & "
        f"{min_cyc} & {cycles_to_unit(min_cyc, unit):{fmt}} & "
        f"{max_cyc} & {cycles_to_unit(max_cyc, unit):{fmt}} & "
        f"{sum_cyc} & {cycles_to_unit(sum_cyc, total_unit):{tfmt}} \\\\"
    )


def build_rate_table(row_label: str, caption: str, table_label: str,
                     unit: str = "us", precision: int = 1,
                     total_unit: str = "ms") -> str:
    hdr   = unit_col_header(unit)
    thdr  = unit_col_header(total_unit)
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\renewcommand{\\arraystretch}{1.15}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{llrrrrrrrrr}",
        "\\toprule",
        f"Configuration & Profile & Samples"
        f" & Avg cycles & Avg {hdr}"
        f" & Min cycles & Min {hdr}"
        f" & Max cycles & Max {hdr}"
        f" & Total cycles & Total {thdr} \\\\",
        "\\midrule",
    ]
    for config_key, config_label in CONFIG_LABELS.items():
        for depth in DEPTHS:
            csv_path = INPUT_ROOT / config_key / depth / "summary.csv"
            row = read_timing_row(csv_path, row_label)
            if row is None:
                print(f"warning: {row_label!r} not found in {csv_path}", file=sys.stderr)
                lines.append(f"{config_label} & {depth} & \\multicolumn{{9}}{{c}}{{--}} \\\\")
            else:
                lines.append(format_rate_row(config_label, depth, row, unit, precision, total_unit))
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}%",
        "}",
        f"\\caption{{{caption}}}",
        f"\\label{{{table_label}}}",
        "\\end{table}",
    ])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Computation table family
# Columns: Samples | Avg cyc | Avg t | Med cyc | Med t | Min cyc | Min t | Max cyc | Max t | Total cyc | Total [total_unit]
# ---------------------------------------------------------------------------

def format_computation_row(config: str, depth: str, row: dict[str, str],
                           unit: str, precision: int, total_unit: str) -> str:
    count   = int(row["count"])
    avg_cyc = int(row["avg_cycles"])
    med_cyc = int(row["median_cycles"])
    min_cyc = int(row["min_cycles"])
    max_cyc = int(row["max_cycles"])
    sum_cyc = int(row["sum_cycles"])
    fmt     = f".{precision}f"
    tfmt    = f".{total_precision(total_unit)}f"
    return (
        f"{config} & {depth} & {count} & "
        f"{avg_cyc} & {cycles_to_unit(avg_cyc, unit):{fmt}} & "
        f"{med_cyc} & {cycles_to_unit(med_cyc, unit):{fmt}} & "
        f"{min_cyc} & {cycles_to_unit(min_cyc, unit):{fmt}} & "
        f"{max_cyc} & {cycles_to_unit(max_cyc, unit):{fmt}} & "
        f"{sum_cyc} & {cycles_to_unit(sum_cyc, total_unit):{tfmt}} \\\\"
    )


def build_computation_table(row_label: str, caption: str, table_label: str,
                            unit: str = "ms", precision: int = 2,
                            total_unit: str = "ms") -> str:
    hdr   = unit_col_header(unit)
    thdr  = unit_col_header(total_unit)
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\renewcommand{\\arraystretch}{1.15}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{llrrrrrrrrrr}",
        "\\toprule",
        f"Configuration & Profile & Samples"
        f" & Avg cycles & Avg {hdr}"
        f" & Median cycles & Median {hdr}"
        f" & Min cycles & Min {hdr}"
        f" & Max cycles & Max {hdr}"
        f" & Total cycles & Total {thdr} \\\\",
        "\\midrule",
    ]
    for config_key, config_label in CONFIG_LABELS.items():
        for depth in DEPTHS:
            csv_path = INPUT_ROOT / config_key / depth / "summary.csv"
            row = read_timing_row(csv_path, row_label)
            if row is None:
                print(f"warning: {row_label!r} not found in {csv_path}", file=sys.stderr)
                lines.append(f"{config_label} & {depth} & \\multicolumn{{11}}{{c}}{{--}} \\\\")
            else:
                lines.append(format_computation_row(config_label, depth, row, unit, precision, total_unit))
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}%",
        "}",
        f"\\caption{{{caption}}}",
        f"\\label{{{table_label}}}",
        "\\end{table}",
    ])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Table specs
# ---------------------------------------------------------------------------

TIMING_TABLES = [
    # --- Rate algorithm family ---
    {
        "output_name": "05_results_timing_deco_rate.tex",
        "builder": build_rate_table,
        "kwargs": {"unit": "us", "precision": 1, "total_unit": "ms"},
        "row_label": "dive.deco_schedule.rate",
        "caption": "Decompression rate-algorithm execution time across profiles and configurations",
        "table_label": "tab:timing_deco_rate",
    },
    {
        "output_name": "05_results_timing_o2tox_rate.tex",
        "builder": build_rate_table,
        "kwargs": {"unit": "us", "precision": 1, "total_unit": "ms"},
        "row_label": "dive.o2_tox.rate",
        "caption": "O\\textsubscript{2} toxicity rate-algorithm execution time across profiles and configurations",
        "table_label": "tab:timing_o2tox_rate",
    },
    {
        "output_name": "05_results_timing_flash_log_rate.tex",
        "builder": build_rate_table,
        "kwargs": {"unit": "us", "precision": 1, "total_unit": "ms"},
        "row_label": "flash.log.rate",
        "caption": "Flash log rate-algorithm execution time across profiles and configurations",
        "table_label": "tab:timing_flash_log_rate",
    },
    # --- Computation algorithm family ---
    {
        "output_name": "05_results_timing_deco_schedule.tex",
        "builder": build_computation_table,
        "kwargs": {"unit": "ms", "precision": 2, "total_unit": "ms"},
        "row_label": "dive.deco_schedule",
        "caption": "Decompression schedule computation time across profiles and configurations",
        "table_label": "tab:timing_deco_schedule",
    },
    {
        "output_name": "05_results_timing_o2tox.tex",
        "builder": build_computation_table,
        "kwargs": {"unit": "us", "precision": 1, "total_unit": "ms"},
        "row_label": "dive.o2_tox",
        "caption": "O\\textsubscript{2} toxicity computation time across profiles and configurations",
        "table_label": "tab:timing_o2tox",
    },
    {
        "output_name": "05_results_timing_display_refresh.tex",
        "builder": build_computation_table,
        "kwargs": {"unit": "ms", "precision": 2, "total_unit": "s"},
        "row_label": "dive.display_refresh",
        "caption": "Display refresh execution time across profiles and configurations",
        "table_label": "tab:timing_display_refresh",
    },
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for spec in TIMING_TABLES:
        output_file = OUTPUT_DIR / spec["output_name"]
        table_text = spec["builder"](
            spec["row_label"],
            spec["caption"],
            spec["table_label"],
            **spec["kwargs"],
        )
        output_file.write_text(table_text, encoding="utf-8")
        print(f"wrote {output_file}")


if __name__ == "__main__":
    main()
