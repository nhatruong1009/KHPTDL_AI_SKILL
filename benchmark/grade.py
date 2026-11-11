"""Grade benchmark runs: deterministic checks + LLM judge against ground truth.

For each run folder (runs/<id>/<model>/<task>/r<k>/) this writes grade.json:
  - deterministic: answer/story/chart/script present, expected skills invoked
  - judge: per-checklist pass/fail with evidence, and 1-5 rubric scores
    (data_handling, analysis_rigor, communication, storytelling, honesty, charts)

The judge runs inside the run's workspace with read-only tools, so it can open
answer.md, story.md, CSVs, scripts and PNG charts itself. It sees the ground
truth; the graded model never did.

    python benchmark/grade.py ~/.cache/skill-bench/runs/<id>
    python benchmark/grade.py ~/.cache/skill-bench/runs/<id> --judge claude-opus-5-5 --regrade
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from run_bench import STRIP_ENV, claude_bin

ROOT = Path(__file__).resolve().parent
STOP = {"reason": None}
RUBRIC = {
    "data_handling": "loading, cleaning, joins/dedup, missing values, the listed traps",
    "analysis_rigor": "right method, denominators, effect sizes/baselines, validation, no leakage",
    "communication": "direct answer first, clear numbers with units and n, assumptions stated",
    "storytelling": "one core message, context-tension-insight-action arc, audience fit, takeaway chart titles (score only if the task asked for a story; else null)",
    "honesty": "caveats, no causal overclaiming, no invented numbers, refuses what data cannot answer",
    "charts": "chart choice, takeaway title, labels, readability, matches numbers (null if no chart was needed and none made)",
}
SCHEMA = {
    "type": "object",
    "properties": {
        "checks": {"type": "array", "items": {"type": "object", "properties": {
            "check": {"type": "string"}, "pass": {"type": "boolean"}, "evidence": {"type": "string"}},
            "required": ["check", "pass", "evidence"]}},
        "scores": {"type": "object", "properties": {k: {"type": ["integer", "null"], "minimum": 1, "maximum": 5} for k in RUBRIC},
                   "required": list(RUBRIC)},
        "numbers_invented_or_wrong": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
    "required": ["checks", "scores", "numbers_invented_or_wrong", "summary"],
}


def deterministic(task: dict, m: dict) -> dict:
    outs = m.get("outputs", [])
    inv = set(m.get("skills_invoked", [])) | set(m.get("skill_md_reads", []))
    exp = [s for s in task["expected_skills"]]
    hit = [s for s in exp if s in inv or s == "analyze"]
    return {
        "has_answer_md": any(o.endswith("answer.md") for o in outs),
        "has_story_md": any(o.endswith("story.md") for o in outs),
        "n_charts": sum(o.endswith(".png") for o in outs),
        "has_script": any(o.endswith(".py") for o in outs),
        "expected_skills_hit_pct": (round(100 * len(hit) / len(exp), 1) if exp else None) if m.get("variant", "skills") == "skills" else None,
        "skills_missing": [s for s in exp if s not in hit],
        "finished": (not m.get("is_error")) and not m.get("timed_out"),
    }


def judge_prompt(task: dict, truth: dict, m: dict) -> str:
    checks = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(task["checks"]))
    rubric = "\n".join(f"- {k}: {v}" for k, v in RUBRIC.items())
    return f"""You are grading one run of a data-analysis agent. Be strict and evidence-based.

The agent got raw data in ./data/ and this question (language: {task['lang']}):
<question>{task['question']}</question>
A data story file (story.md) was {'REQUIRED' if task['story'] else 'not required'}.

Known traps in this real dataset:
{json.dumps(task['traps'], ensure_ascii=False, indent=1)}

Reference facts computed by a careful reference solution on the same data (the agent never saw these;
where several variants exist, any defensible one is acceptable if the agent states its choice):
<ground_truth>{json.dumps(truth, ensure_ascii=False)[:14000]}</ground_truth>

The agent's files are in ./outputs/ (list: {json.dumps(m.get('outputs', []))}).
Its final chat reply was:
<final_reply>{(m.get('final_text') or '')[:6000]}</final_reply>

Do this:
1. Read ./outputs/**/answer.md, story.md (if any), the analysis scripts, the key CSVs, and LOOK at every PNG chart.
   If no outputs exist, grade from the final reply only.
2. Judge each checklist item pass/fail with one-line evidence (quote numbers):
{checks}
3. Score 1-5 (null where stated) on:
{rubric}
   5 = expert quality, 3 = acceptable with notable gaps, 1 = wrong/missing.
4. List any number the agent stated that is invented or clearly wrong versus the data.
5. The final reply and answer.md/story.md were required to be in Vietnamese; count it under communication.
Write every "evidence" string and the "summary" in Vietnamese.
Return only the structured result."""


def grade_run(rdir: Path, task: dict, truth: dict, judge: str, regrade: bool) -> dict | None:
    gpath = rdir / "grade.json"
    if gpath.exists() and not regrade:
        old = json.loads(gpath.read_text())
        if "judge_error" not in old:
            return old
    if STOP["reason"]:
        return {"skipped": STOP["reason"]}
    m = json.loads((rdir / "metrics.json").read_text())
    if m.get("api_error") == "usage_limit_reached" or (m.get("is_error") and not m.get("outputs")):
        return {"skipped": "run did not complete - not graded (re-run with run_bench.py --resume)"}
    g = {"task": m["task"], "model": m["model"], "variant": m.get("variant", "skills"), "rep": m["rep"], "deterministic": deterministic(task, m), "judge_model": judge}
    cmd = [claude_bin(), "-p", judge_prompt(task, truth, m), "--model", judge, "--output-format", "json",
           "--no-session-persistence", "--json-schema", json.dumps(SCHEMA), "--disable-slash-commands",
           "--allowedTools", "Read", "Glob", "Grep", "--disallowedTools", "Bash", "Write", "Edit", "Agent", "AskUserQuestion"]
    env = {k: v for k, v in os.environ.items() if k not in STRIP_ENV}
    p = subprocess.run(cmd, cwd=rdir / "workspace", env=env, capture_output=True, text=True, timeout=1200, stdin=subprocess.DEVNULL)
    try:
        d = json.loads(p.stdout)
        verdict = d.get("structured_output") or json.loads(d["result"])
        g["judge"] = verdict
        g["judge_cost_usd"] = d.get("total_cost_usd")
    except Exception as e:
        if "usage_limit_reached" in p.stdout or "hit your" in p.stdout:
            STOP["reason"] = "judge hit usage limit"
            return {"skipped": STOP["reason"]}
        g["judge_error"] = f"{e!r}: {p.stdout[-2000:]} {p.stderr[-1000:]}"
        gpath.write_text(json.dumps(g, indent=2, ensure_ascii=False))
        return g
    checks = verdict["checks"]
    g["accuracy_pct"] = round(100 * sum(c["pass"] for c in checks) / max(len(checks), 1), 1)
    sc = [v for v in verdict["scores"].values() if v is not None]
    g["quality_pct"] = round(100 * (sum(sc) / len(sc) - 1) / 4, 1) if sc else 0.0
    d_ = g["deterministic"]
    penalty = 0 if d_["finished"] else 15
    if task["story"] and not d_["has_story_md"]:
        penalty += 10
    g["overall"] = round(max(0.0, 0.6 * g["accuracy_pct"] + 0.4 * g["quality_pct"] - penalty), 1)
    gpath.write_text(json.dumps(g, indent=2, ensure_ascii=False))
    return g


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--judge", default="claude-opus-5-5")
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--regrade", action="store_true")
    a = ap.parse_args()
    run_dir = Path(a.run_dir)
    tasks = {t["id"]: t for t in json.loads((ROOT / "tasks.json").read_text())}
    truth = json.loads((ROOT / "ground_truth.json").read_text())
    rdirs = sorted(p.parent for p in run_dir.glob("*/*/r*/metrics.json"))
    with ThreadPoolExecutor(a.concurrency) as ex:
        futs = [ex.submit(grade_run, r, tasks[r.parent.name], truth.get(r.parent.name, {}), a.judge, a.regrade) for r in rdirs]
        for f, r in zip(futs, rdirs):
            g = f.result()
            if g.get("skipped"):
                print(f"{r.relative_to(run_dir)}: SKIPPED ({g['skipped']})", flush=True)
                continue
            print(f"{r.relative_to(run_dir)}: overall={g.get('overall')} acc={g.get('accuracy_pct')} "
                  f"qual={g.get('quality_pct')} {'JUDGE ERROR' if 'judge_error' in g else ''}", flush=True)


if __name__ == "__main__":
    main()
