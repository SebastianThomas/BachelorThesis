#!/usr/bin/env bash
# Run from the BachelorThesis root.
set -euo pipefail

TARGET="../stdc_stm32_rs/target"
RESULTS="figures/results"
FILES="decision.csv summary.csv profile.csv flash_log_profile.csv flash_profile_diff.csv flash_profile_diff_summary.csv"

copy_latest() {
  local pattern="$1" dst="$2"
  local src
  src=$(ls -dt "$TARGET"/$pattern 2>/dev/null | head -1)
  if [ -z "$src" ]; then
    echo "SKIP (no match): $pattern" >&2
    return
  fi
  echo "COPY: $pattern → $(basename "$src")" >&2
  mkdir -p "$dst"
  for f in $FILES; do
    [ -f "$src/$f" ] && cp "$src/$f" "$dst/$f" && echo "  $f → $dst"
  done
}

copy_latest "rtt-live-sim-[0-9]*.20m-*.tables"   "$RESULTS/lin-exp/20m"
copy_latest "rtt-live-sim-[0-9]*.50m-*.tables"   "$RESULTS/lin-exp/50m"
copy_latest "rtt-live-sim-[0-9]*.90m-*.tables"   "$RESULTS/lin-exp/90m"
copy_latest "rtt-live-sim-[0-9]*.200m-*.tables"  "$RESULTS/lin-exp/200m"
copy_latest "rtt-live-sim-exp-*.20m-*.tables"    "$RESULTS/exp/20m"
copy_latest "rtt-live-sim-exp-*.50m-*.tables"    "$RESULTS/exp/50m"
copy_latest "rtt-live-sim-exp-*.90m-*.tables"    "$RESULTS/exp/90m"
copy_latest "rtt-live-sim-exp-*.200m-*.tables"   "$RESULTS/exp/200m"
copy_latest "rtt-live-sim-fixed-*.20m-*.tables"  "$RESULTS/baseline-fixed/20m"
copy_latest "rtt-live-sim-fixed-*.50m-*.tables"  "$RESULTS/baseline-fixed/50m"
copy_latest "rtt-live-sim-fixed-*.90m-*.tables"  "$RESULTS/baseline-fixed/90m"
copy_latest "rtt-live-sim-fixed-*.200m-*.tables" "$RESULTS/baseline-fixed/200m"
