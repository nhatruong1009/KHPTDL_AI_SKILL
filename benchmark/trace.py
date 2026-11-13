"""Turn run transcripts into readable step-by-step files.

For every run folder under results/<run_id>/runs/<config>/<task>/r<k>/ that has a
transcript.jsonl, writes steps.md next to it. It also writes results/<run_id>/skills_trace.md,
a table of which skills each run loaded and in what order.

    python benchmark/trace.py results/v2-skills
    python benchmark/trace.py results/v2-skills --full     # do not shorten texts and commands
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def short(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if n <= 0 or len(s) <= n else s[: n - 1] + "…"


def describe_tool(name: str, inp: dict, n: int) -> str:
    if name == "Skill":
        return f"**SKILL `{inp.get('skill', '?')}`**" + (f" (args: {short(inp.get('args', ''), n)})" if inp.get("args") else "")
    if name == "Bash":
        return f"Bash: `{short(inp.get('command', ''), n)}`"
    if name in ("Read", "Write", "Edit", "NotebookEdit"):
        p = str(inp.get("file_path", ""))
        p = p.split("/workspace/", 1)[-1]
        if "/.claude/skills/" in p or p.startswith(".claude/skills/"):
            return f"{name} **skill file** `{p}`"
        return f"{name} `{p}`"
    if name in ("Glob", "Grep"):
        return f"{name} `{short(inp.get('pattern', ''), n)}`"
    if name == "TodoWrite":
        todos = inp.get("todos", [])
        return "TodoWrite: " + "; ".join(f"[{t.get('status', '')}] {short(t.get('content', ''), 60)}" for t in todos)
    return f"{name}: {short(json.dumps(inp, ensure_ascii=False), n)}"


def trace_run(rdir: Path, n: int) -> dict:
    lines = (rdir / "transcript.jsonl").read_text(errors="replace").splitlines()
    m = json.loads((rdir / "metrics.json").read_text()) if (rdir / "metrics.json").exists() else {}
    g = json.loads((rdir / "grade.json").read_text()) if (rdir / "grade.json").exists() else {}
    steps, skills, errors, final = [], [], 0, ""
    pending = {}  # tool_use_id -> step index (to mark errors)
    for line in lines:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "assistant":
            for c in ev.get("message", {}).get("content", []):
                if c.get("type") == "text" and c.get("text", "").strip():
                    steps.append(("text", short(c["text"], n)))
                elif c.get("type") == "tool_use":
                    inp = c.get("input", {}) or {}
                    if c["name"] == "Skill":
                        skills.append(str(inp.get("skill", "?")))
                    pending[c.get("id")] = len(steps)
                    steps.append(("tool", describe_tool(c["name"], inp, n)))
        elif t == "user":
            content = ev.get("message", {}).get("content", [])
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                        errors += 1
                        i = pending.get(c.get("tool_use_id"))
                        if i is not None:
                            kind, txt = steps[i]
                            res = c.get("content")
                            res = res if isinstance(res, str) else " ".join(x.get("text", "") for x in res or [] if isinstance(x, dict))
                            steps[i] = (kind, txt + f"  \n  ↳ **lỗi:** {short(res, 200)}")
        elif t == "result":
            final = ev.get("result", "") or ""

    cfg, task, rep = rdir.parent.parent.name, rdir.parent.name, rdir.name
    head = [f"# {task} · {cfg} · {rep}", ""]
    head.append("| | |\n|---|---|")
    if g.get("overall") is not None:
        head.append(f"| Điểm overall / accuracy / quality | {g['overall']} / {g.get('accuracy_pct')} / {g.get('quality_pct')} |")
    if m:
        head.append(f"| Thời gian · chi phí · số turn | {m.get('wall_s')} s · ${(m.get('cost_usd') or 0):.3f} · {m.get('num_turns')} |")
    head.append(f"| Skill đã nạp (theo thứ tự) | {' → '.join(f'`{s}`' for s in skills) or '(không có)'} |")
    head.append(f"| Lỗi công cụ | {errors} |")
    head.append("")
    body = ["## Các bước", ""]
    k = 0
    for kind, txt in steps:
        if kind == "tool":
            k += 1
            body.append(f"{k}. {txt}")
        else:
            body.append(f"\n> {txt}\n")
    if final:
        body += ["", "## Trả lời cuối cùng", "", final if n <= 0 else short(final, 3000)]
    failed = [c for c in (g.get("judge") or {}).get("checks", []) if not c.get("pass")]
    if failed:
        body += ["", "## Tiêu chí bị trượt (giám khảo)", ""] + [f"- {c['check']}  \n  ↳ {c['evidence']}" for c in failed]
    (rdir / "steps.md").write_text("\n".join(head + body) + "\n")
    return {"cfg": cfg, "task": task, "rep": rep, "skills": skills, "overall": g.get("overall"),
            "n_tools": k, "errors": errors, "path": rdir}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    root = Path(a.results_dir)
    rows = [trace_run(p.parent, 0 if a.full else 300) for p in sorted(root.glob("runs/*/*/r*/transcript.jsonl"))]
    out = ["# Skill đã nạp theo từng lượt chạy", "",
           "Mỗi dòng dẫn tới `steps.md` của lượt đó (các bước, lệnh, file, lỗi, trả lời cuối, tiêu chí bị trượt).", "",
           "| Task | Cấu hình | Lần | Điểm | Số bước | Skill đã nạp (theo thứ tự) |", "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["task"], r["cfg"], r["rep"])):
        link = r["path"].relative_to(root) / "steps.md"
        out.append(f"| {r['task']} | {r['cfg']} | [{r['rep']}]({link}) | {r['overall']} | {r['n_tools']} | "
                   f"{' → '.join(r['skills']) or '—'} |")
    (root / "skills_trace.md").write_text("\n".join(out) + "\n")
    print(f"{len(rows)} runs -> {root / 'skills_trace.md'}")


if __name__ == "__main__":
    main()
