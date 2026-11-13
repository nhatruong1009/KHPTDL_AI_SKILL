#!/usr/bin/env bash
# Wait for a benchmark run to finish, then grade it and build the report.
# Detached-safe: survives the Claude session ending. Re-runnable (grade.py skips graded runs).
#   nohup setsid bash benchmark/finish_run.sh oulad-1 > finish.log 2>&1 &
set -u
RUN_ID="${1:?run id}"
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="${BENCH_RUNS_ROOT:-$HOME/.cache/skill-bench/runs}/$RUN_ID"
cd "$HERE"
echo "[$(date -u +%FT%TZ)] waiting for run_bench $RUN_ID"
# anchor on the interpreter so this loop (and any shell whose command line merely mentions the run) never matches itself
while pgrep -f "^python3? [^ ]*run_bench\.py --run-id $RUN_ID( |$)" >/dev/null; do sleep 30; done
echo "[$(date -u +%FT%TZ)] runs finished -> grading"
python3 grade.py "$RUN_DIR" --concurrency 4
echo "[$(date -u +%FT%TZ)] grading done -> report"
python3 report.py "$RUN_DIR"
echo "[$(date -u +%FT%TZ)] DONE -> $HERE/results/$RUN_ID/report.md"
