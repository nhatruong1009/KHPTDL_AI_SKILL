"""Run the skill benchmark: every (model x task x rep) in an isolated workspace.

Each workspace = a copy of the project's .claude/skills + the task's raw data
in ./data/. Claude Code is called headless (`claude -p`) with
`/analyze data/ : <question>`, and the full stream-json transcript is saved.
Per run we record wall time, API time, tokens, cost, turns, tool and skill
usage into metrics.json.

    python benchmark/run_bench.py                         # all tasks, haiku + sonnet
    python benchmark/run_bench.py --tasks wine_quality --models haiku
    python benchmark/run_bench.py --reps 2 --concurrency 3

Env: CLAUDE_BIN (path to the claude binary) - defaults to `claude` on PATH,
then to the VS Code extension binary in $CLAUDE_CODE_EXECPATH.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
MODELS = {  # small / medium tier; large tier intentionally skipped
    "haiku": "claude-haiku-5-5",
    "sonnet": "claude-sonnet-5-5",
}
ALLOWED_TOOLS = [
    "Read", "Write", "Edit", "Glob", "Grep", "Skill", "TodoWrite",
    *[f"Bash({c}:*)" for c in ("python", "python3", "ls", "head", "tail", "cat", "wc", "mkdir",
                               "find", "file", "du", "grep", "cd", "sort", "uniq", "cut", "awk", "sed", "echo")],
]
DISALLOWED_TOOLS = ["AskUserQuestion", "Agent", "WebFetch", "WebSearch", "Artifact", "Workflow"]
SYSTEM_NOTE = (
    "You are running inside an automated, non-interactive benchmark. Nobody can answer questions: "
    "never ask the user anything, make reasonable assumptions and state them. Work only inside the "
    "current directory. Raw data is in ./data/ and is read-only. Write all outputs under ./outputs/. "
    "Write the final reply, answer.md, story.md and chart titles/labels in Vietnamese "
    "(keep column names and code identifiers as they are)."
)
STRIP_ENV = ["CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_CHILD_SESSION",
             "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_PID", "CLAUDE_EFFORT"]


def claude_bin() -> str:
    if os.environ.get("CLAUDE_BIN"):
        return os.environ["CLAUDE_BIN"]
    found = shutil.which("claude")
    if found:
        return found
    if os.environ.get("CLAUDE_CODE_EXECPATH"):
        return os.environ["CLAUDE_CODE_EXECPATH"]
    raise SystemExit("claude binary not found - set CLAUDE_BIN")


VARIANTS = ("skills", "noskills")


def build_prompt(task: dict, variant: str) -> str:
    if variant == "skills":
        return f"/analyze data/ : {task['question']}"
    # baseline: same question, no project skills in the workspace, no slash command
    return f"Dữ liệu nằm trong ./data/. Hãy trả lời câu hỏi sau từ dữ liệu này:\n\n{task['question']}"


def make_workspace(ws: Path, task_id: str, variant: str) -> None:
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True)
    if variant == "skills":
        (ws / ".claude").mkdir()
        shutil.copytree(PROJECT / ".claude" / "skills", ws / ".claude" / "skills")
    shutil.copytree(ROOT / "data" / task_id, ws / "data")
    # own git root -> Claude Code treats the workspace as the project (no leakage from the parent repo)
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)


def parse_transcript(path: Path) -> dict:
    tools, skills, skill_reads, tool_errors, result = Counter(), [], [], 0, None
    for line in path.read_text(errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "assistant":
            for c in ev.get("message", {}).get("content", []):
                if c.get("type") == "tool_use":
                    tools[c["name"]] += 1
                    inp = c.get("input", {}) or {}
                    if c["name"] == "Skill":
                        skills.append(str(inp.get("skill", "?")))
                    fp = str(inp.get("file_path", "")) + " " + str(inp.get("command", ""))
                    for name in re.findall(r"\.claude/skills/([\w-]+)/SKILL\.md", fp):
                        skill_reads.append(name)
        elif t == "user":
            content = ev.get("message", {}).get("content", [])
            if isinstance(content, list):
                tool_errors += sum(1 for c in content if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"))
        elif t == "result":
            result = ev
    return {"tools": dict(tools), "skills_invoked": skills, "skill_md_reads": skill_reads, "tool_errors": tool_errors, "result": result}


STOP = {"reason": None}  # set when the account hits its usage limit -> skip remaining jobs


def is_complete(rdir: Path) -> bool:
    mp = rdir / "metrics.json"
    if not mp.exists():
        return False
    m = json.loads(mp.read_text())
    return not m.get("is_error") and not m.get("timed_out")


def run_one(task: dict, model_key: str, variant: str, rep: int, run_dir: Path, args) -> dict:
    ws = run_dir / f"{model_key}__{variant}" / task["id"] / f"r{rep}" / "workspace"
    if args.resume and is_complete(ws.parent):
        return {**json.loads((ws.parent / "metrics.json").read_text()), "skipped": "already complete"}
    if STOP["reason"]:
        return {"task": task["id"], "skipped": STOP["reason"]}
    make_workspace(ws, task["id"], variant)
    prompt = build_prompt(task, variant)
    cmd = [claude_bin(), "-p", prompt, "--model", MODELS.get(model_key, model_key), "--effort", args.effort,
           "--output-format", "stream-json", "--verbose", "--no-session-persistence",
           "--permission-mode", "acceptEdits", "--append-system-prompt", SYSTEM_NOTE,
           "--max-budget-usd", str(args.budget),
           "--allowedTools", *ALLOWED_TOOLS, "--disallowedTools", *DISALLOWED_TOOLS]
    env = {k: v for k, v in os.environ.items() if k not in STRIP_ENV}
    tr = ws.parent / "transcript.jsonl"
    t0 = time.time()
    timed_out = False
    with open(tr, "w") as out, open(ws.parent / "stderr.txt", "w") as err:
        try:
            subprocess.run(cmd, cwd=ws, env=env, stdout=out, stderr=err, timeout=args.timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            timed_out = True
    wall = time.time() - t0
    p = parse_transcript(tr)
    res = p.pop("result") or {}
    usage = res.get("usage", {})
    outputs = sorted(str(f.relative_to(ws)) for f in (ws / "outputs").rglob("*") if f.is_file()) if (ws / "outputs").exists() else []
    m = {
        "task": task["id"], "model": model_key, "model_id": MODELS.get(model_key, model_key), "rep": rep,
        "variant": variant, "effort": args.effort,
        "thinking_tokens": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
        "wall_s": round(wall, 1), "duration_api_s": round(res.get("duration_api_ms", 0) / 1000, 1),
        "cost_usd": res.get("total_cost_usd"), "num_turns": res.get("num_turns"),
        "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0),
        "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
        "cache_write_tokens": usage.get("cache_creation_input_tokens", 0),
        "model_usage": res.get("modelUsage"),
        "subtype": res.get("subtype"), "is_error": res.get("is_error", True), "timed_out": timed_out,
        "api_error": res.get("api_error"),
        "final_text": res.get("result", ""), "outputs": outputs, **p,
    }
    m["total_tokens"] = m["input_tokens"] + m["output_tokens"] + m["cache_read_tokens"] + m["cache_write_tokens"]
    (ws.parent / "metrics.json").write_text(json.dumps(m, indent=2, ensure_ascii=False))
    if m["api_error"] == "usage_limit_reached":
        STOP["reason"] = f"usage limit: {m['final_text']}"
    return m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=list(MODELS))
    ap.add_argument("--tasks", nargs="+", default=None)
    ap.add_argument("--variants", nargs="+", default=["skills"], choices=VARIANTS,
                    help="skills = /analyze with project skills; noskills = baseline without .claude/skills")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--resume", action="store_true", help="skip runs that already completed without error")
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=2700, help="seconds per run")
    ap.add_argument("--budget", type=float, default=8.0, help="max USD per run")
    ap.add_argument("--run-id", default=datetime.now().strftime("%Y%m%d-%H%M%S"))
    ap.add_argument("--runs-root", default=os.environ.get("BENCH_RUNS_ROOT", str(Path.home() / ".cache" / "skill-bench" / "runs")),
                    help="where workspaces live; keep it on a local disk (git init fails on some shared folders)")
    args = ap.parse_args()

    tasks = json.loads((ROOT / "tasks.json").read_text())
    if args.tasks:
        tasks = [t for t in tasks if t["id"] in args.tasks]
    missing = [t["id"] for t in tasks if not (ROOT / "data" / t["id"]).exists()]
    if missing:
        raise SystemExit(f"data missing for {missing} - run: python -I benchmark/fetch_data.py")
    run_dir = Path(args.runs_root) / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    # interleave models so both tiers progress together; heavy tasks first
    # order: variant (as given, e.g. skills first, baseline last) -> task -> model; with --concurrency 1 runs strictly one by one
    jobs = [(t, m, v, r) for r in range(1, args.reps + 1) for v in args.variants for t in tasks for m in args.models]
    print(f"run {args.run_id}: {len(jobs)} jobs -> {run_dir}", flush=True)
    if not args.resume:
        (run_dir / "config.json").write_text(json.dumps({**vars(args), "model_ids": {m: MODELS.get(m, m) for m in args.models},
                                                         "tasks": [t["id"] for t in tasks]}, indent=2))
    with ThreadPoolExecutor(args.concurrency) as ex:
        futs = {ex.submit(run_one, t, m, v, r, run_dir, args): (t["id"], f"{m}__{v}", r) for t, m, v, r in jobs}
        for f in as_completed(futs):
            tid, m, r = futs[f]
            try:
                x = f.result()
                if x.get("skipped"):
                    print(f"[skip] {m:16s} {tid:18s} r{r} {x['skipped']}", flush=True)
                    continue
                print(f"[done] {m:16s} {tid:18s} r{r} {x['wall_s']:7.1f}s ${x['cost_usd'] or 0:.3f} "
                      f"turns={x['num_turns']} skills={x['skills_invoked']} err={x['is_error']} timeout={x['timed_out']}", flush=True)
            except Exception as e:  # keep the batch going
                print(f"[fail] {m} {tid} r{r}: {e!r}", flush=True)
    if STOP["reason"]:
        print(f"STOPPED EARLY - {STOP['reason']}. Re-run the same command with --resume after the reset.", flush=True)
        raise SystemExit(3)


if __name__ == "__main__":
    main()
