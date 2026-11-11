"""Aggregate a graded run into results/<run_id>/: summary.csv, report.md, charts.

    python benchmark/report.py runs/<id>
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
COLORS = {"haiku__noskills": "#9fd8cf", "haiku__skills": "#2a9d8f", "sonnet__noskills": "#f4b8a6", "sonnet__skills": "#e76f51",
          "haiku": "#2a9d8f", "sonnet": "#e76f51"}


def load(run_dir: Path) -> pd.DataFrame:
    rows = []
    tasks = {t["id"]: t for t in json.loads((ROOT / "tasks.json").read_text())}
    for mp in sorted(run_dir.glob("*/*/r*/metrics.json")):
        m = json.loads(mp.read_text())
        gp = mp.parent / "grade.json"
        g = json.loads(gp.read_text()) if gp.exists() else {}
        j = g.get("judge", {})
        d = g.get("deterministic", {})
        rows.append({
            "task": m["task"], "topic": tasks[m["task"]]["topic"], "model": m["model"], "variant": m.get("variant", "skills"),
            "config": f"{m['model']}__{m.get('variant', 'skills')}", "effort": m.get("effort"), "rep": m["rep"],
            "thinking_tokens": m.get("thinking_tokens"),
            "overall": g.get("overall"), "accuracy_pct": g.get("accuracy_pct"), "quality_pct": g.get("quality_pct"),
            **{f"s_{k}": v for k, v in j.get("scores", {}).items()},
            "checks_passed": sum(c["pass"] for c in j.get("checks", [])), "checks_total": len(j.get("checks", [])),
            "wall_s": m["wall_s"], "api_s": m["duration_api_s"], "cost_usd": m["cost_usd"], "turns": m["num_turns"],
            "input_tokens": m["input_tokens"], "output_tokens": m["output_tokens"],
            "cache_read_tokens": m["cache_read_tokens"], "cache_write_tokens": m["cache_write_tokens"],
            "total_tokens": m["total_tokens"], "tool_calls": sum(m["tools"].values()), "tool_errors": m["tool_errors"],
            "skills_used": ",".join(sorted(set(m["skills_invoked"]) | set(m.get("skill_md_reads", [])))),
            "skill_hit_pct": d.get("expected_skills_hit_pct"), "has_story": d.get("has_story_md"),
            "n_charts": d.get("n_charts"), "finished": d.get("finished"), "timed_out": m["timed_out"],
            "judge_cost_usd": g.get("judge_cost_usd"), "judge_summary": j.get("summary", g.get("judge_error", "")),
            "failed_checks": " | ".join(c["check"][:90] for c in j.get("checks", []) if not c["pass"]),
        })
    return pd.DataFrame(rows)


def charts(df: pd.DataFrame, out: Path) -> None:
    models = [m for m in COLORS if m in df.config.unique()] + [m for m in df.config.unique() if m not in COLORS]
    # 1. score by task, grouped bars
    piv = df.groupby(["task", "config"]).overall.mean().unstack()[models]
    ax = piv.plot.barh(figsize=(8, 5), color=[COLORS.get(m, "grey") for m in models], width=0.75)
    ax.set_xlim(0, 100); ax.set_xlabel("Điểm tổng (0-100)"); ax.set_ylabel("")
    ax.set_title("Điểm tổng theo từng task", loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout(); plt.savefig(out / "score_by_task.png", dpi=150); plt.close()
    # 2. cost vs score, time vs score
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, x, lab in [(axes[0], "cost_usd", "Chi phí mỗi task (USD)"), (axes[1], "wall_s", "Thời gian mỗi task (giây)")]:
        for m in models:
            s = df[df.config == m]
            ax.scatter(s[x], s.overall, s=60, color=COLORS.get(m, "grey"), label=m, alpha=0.85)
            for _, r in s.iterrows():
                ax.annotate(r.task, (r[x], r.overall), fontsize=7, xytext=(4, 2), textcoords="offset points", color="#555")
        ax.set_xlabel(lab); ax.set_ylabel("Điểm tổng"); ax.set_ylim(0, 105)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False)
    fig.suptitle("Chất lượng so với chi phí và thời gian", x=0.06, ha="left", fontweight="bold")
    plt.tight_layout(); plt.savefig(out / "score_vs_cost_time.png", dpi=150); plt.close()
    # 3. rubric profile
    rub = [c for c in df.columns if c.startswith("s_")]
    prof = df.groupby("config")[rub].mean().T.loc[:, models]
    prof.index = [i[2:] for i in prof.index]
    ax = prof.plot.bar(figsize=(8, 4), color=[COLORS.get(m, "grey") for m in models], rot=0)
    ax.set_ylim(0, 5); ax.set_ylabel("Điểm giám khảo (1-5)"); ax.set_title("Hồ sơ rubric theo cấu hình", loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout(); plt.savefig(out / "rubric_profile.png", dpi=150); plt.close()


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else (f"{v:,.3f}" if isinstance(v, float) and abs(v) < 10 else
                                                               f"{v:,.1f}" if isinstance(v, float) else str(v)) for v in r) + " |")
    return "\n".join(lines)


def main() -> None:
    run_dir = Path(sys.argv[1]).resolve()
    out = ROOT / "results" / run_dir.name
    out.mkdir(parents=True, exist_ok=True)
    df = load(run_dir)
    n_all = len(df)
    df = df[df.overall.notna()].copy()
    print(f"{len(df)}/{n_all} runs graded and included", flush=True)
    df.to_csv(out / "summary.csv", index=False)
    # keep per-run evidence in the project (outputs, metrics, grade, transcript - not the raw data)
    for mp in run_dir.glob("*/*/r*/metrics.json"):
        rd = mp.parent
        dst = out / "runs" / rd.relative_to(run_dir)
        dst.mkdir(parents=True, exist_ok=True)
        for f in ("metrics.json", "grade.json", "transcript.jsonl"):
            if (rd / f).exists():
                shutil.copy2(rd / f, dst / f)
        if (rd / "workspace" / "outputs").exists():
            shutil.copytree(rd / "workspace" / "outputs", dst / "outputs", dirs_exist_ok=True)
    charts(df, out)
    by_model = df.groupby("config").agg(
        tasks=("task", "count"), overall=("overall", "mean"), accuracy=("accuracy_pct", "mean"), quality=("quality_pct", "mean"),
        storytelling=("s_storytelling", "mean"), cost_total=("cost_usd", "sum"), cost_per_task=("cost_usd", "mean"),
        time_per_task_s=("wall_s", "mean"), tokens_per_task=("total_tokens", "mean"), output_tokens_per_task=("output_tokens", "mean"),
        thinking_tokens_per_task=("thinking_tokens", "mean"), charts_per_task=("n_charts", "mean"),
        turns_per_task=("turns", "mean"), skill_hit_pct=("skill_hit_pct", "mean"), finished=("finished", "sum"),
    ).reset_index()
    by_model["score_per_dollar"] = by_model.overall / by_model.cost_per_task
    per_task = df[["task", "config", "overall", "accuracy_pct", "quality_pct", "s_storytelling", "wall_s", "cost_usd",
                   "total_tokens", "output_tokens", "turns", "skill_hit_pct", "n_charts", "has_story"]].sort_values(["task", "config"])
    fails = df[["task", "config", "failed_checks"]].sort_values(["task", "config"])
    # skills effect: skills minus baseline, same model and task
    eff = ""
    if df.variant.nunique() > 1:
        pv = df.pivot_table(index=["task", "model"], columns="variant", values=["overall", "accuracy_pct", "quality_pct", "cost_usd", "wall_s"])
        delta = pd.DataFrame({f"d_{k}": pv[(k, "skills")] - pv[(k, "noskills")] for k in ["overall", "accuracy_pct", "quality_pct", "cost_usd", "wall_s"]}).reset_index()
        delta.to_csv(out / "skills_effect.csv", index=False)
        eff = "## Hiệu quả của skills (có skills - không skills, cùng model và task)\n" + md_table(delta.round(3)) + "\n\n" + \
              md_table(delta.groupby("model")[[c for c in delta.columns if c.startswith("d_")]].mean().reset_index().round(3))
    txt = [f"# Benchmark bộ skill - lượt chạy `{run_dir.name}`", "",
           "## Theo cấu hình (model __ biến thể)", md_table(by_model.round(3)), "",
           "![](score_by_task.png)", "", "![](score_vs_cost_time.png)", "", "![](rubric_profile.png)", "",
           eff, "",
           "## Theo từng task", md_table(per_task.round(3)), "",
           "## Các tiêu chí bị trượt", md_table(fails), "",
           "## Nhận xét của giám khảo"]
    for _, r in df.sort_values(["task", "config"]).iterrows():
        txt.append(f"- **{r.task} / {r.config}** ({r.overall}): {r.judge_summary}")
    (out / "report.md").write_text("\n".join(txt), encoding="utf-8")
    print(by_model.round(3).to_string())
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
