# Skill benchmark

Benchmark for the `.claude/skills` set (orchestrator `analyze` + 15 sub-skills) on **real public data**,
comparing a small and a mid-size model (large tier intentionally skipped).

## Tasks (7 topics, all real downloaded data)

| id | Topic | Source | Input files | What it stresses |
|---|---|---|---|---|
| `retail_uk` | E-commerce | UCI #502 Online Retail II | 1 xlsx, 2 overlapping sheets, ~1.07M rows | dedup across sheets, cancellations, partial year (like-for-like), new vs returning, **story for CEO** (VI) |
| `student_perf` | Education | UCI #320 Student Performance | 2 `;` CSV + codebook + R merge script | joining 382 overlapping students by 13 attributes, G3=0 drop-outs, ordinal tests, effect sizes |
| `household_power` | Energy | UCI #235 Household Power | 2M-row `;` txt, `?` missing | kW->kWh, gaps, seasonality, anomaly detection, forecast with interval |
| `worldbank_health` | Public health | World Bank WDI API | 3 zips x (data + 2 metadata) | junk header rows, removing aggregates, wide->long, controlling for income, **story for Ministry of Health** (VI) |
| `himalaya` | Sports safety | TidyTuesday 2020-09-22 | 3 related CSV + readme | person-level denominators, small-n decades, event spikes, **story for general audience** |
| `wine_quality` | Food | UCI #186 Wine Quality | 2 CSV + names file | **relevance gate**: grape/price/country are not in the data -> must refuse (VI) |
| `bank_marketing` | Banking | UCI #222 Bank Marketing | 4 CSV versions + docs | choosing the right file, documented leakage (`duration`), imbalance, baseline |

Questions, traps and the grading checklist: [tasks.json](tasks.json).
Reference facts (computed from the real data by [reference.py](reference.py)): `ground_truth.json`.

## Pipeline

```
fetch_data.py   download raw data          -> benchmark/data/<task>/          (gitignored)
reference.py    reference solution          -> benchmark/ground_truth.json
run_bench.py    claude -p "/analyze data/ : <question>" per model x task x rep,
                isolated workspace (skills copy + data copy, own git root),
                stream-json transcript      -> ~/.cache/skill-bench/runs/<id>/<model>/<task>/r<k>/
grade.py        deterministic checks + LLM judge (reads outputs, CSVs, charts; sees ground truth)
report.py       summary.csv, report.md, charts, per-run evidence -> benchmark/results/<id>/
```

```bash
python -I benchmark/fetch_data.py
python -I benchmark/reference.py
cd benchmark
python run_bench.py --run-id full-1 --concurrency 3          # default models: haiku sonnet
python grade.py ~/.cache/skill-bench/runs/full-1             # judge: claude-opus-5-5 (--judge to change)
python report.py ~/.cache/skill-bench/runs/full-1
```

## Metrics

| Metric | From |
|---|---|
| wall time, API time, turns | runner clock + `result` event |
| input / output / cache-read / cache-write tokens, cost (USD, list price) | `result` event of `claude -p` |
| tool calls, tool errors, skills used (Skill tool calls + SKILL.md reads) | transcript |
| `accuracy_pct` | % of the task's checklist items the judge passed (checked against ground truth) |
| `quality_pct` | judge rubric 1-5 rescaled: data handling, rigor, communication, storytelling, honesty, charts |
| `overall` | 0.6 x accuracy + 0.4 x quality - penalties (unfinished run -15, required story.md missing -10) |

Judge cost is recorded separately (`judge_cost_usd`) and not counted in a task's cost.

## Caveats

- One rep per cell by default; agent runs vary - use `--reps 2+` before drawing fine-grained conclusions.
- The judge is an LLM; every verdict carries quoted evidence in `grade.json` for spot checks.
- User-level skills on the machine (e.g. `dataviz`, `xlsx`) are visible to the runs, as in real use.
- Permissions are an allowlist (file tools + python/ls/head/...); some shell constructs get denied and show up as `tool_errors`.
