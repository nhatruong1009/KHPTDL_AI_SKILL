"""Everest: member vs hired-staff mortality by decade and before/after 1990.
Run from project root: python outputs/everest-safety/analysis.py
Uses expedition-level totals (members, member_deaths, hired_staff, hired_staff_deaths)
from data/expeditions.csv, which cover all expeditions (members.csv only has rows for
recorded persons). Member-level cross-check is printed at the end.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
OUT = HERE

exp = pd.read_csv(os.path.join(DATA, "expeditions.csv"))
mem = pd.read_csv(os.path.join(DATA, "members.csv"))

ERA_POST = "1990-2019 (thương mại)"
ERA_PRE = "1921-1989 (trước 1990)"

ev = exp[exp.peak_id == "EVER"].copy()
ev["decade"] = (ev.year // 10 * 10).astype(int)
ev["era"] = np.where(ev.year >= 1990, ERA_POST, ERA_PRE)


def rate_ci(d, n):
    """Death rate per 1000 with exact (Clopper-Pearson) 95% CI."""
    if n == 0:
        return np.nan, np.nan, np.nan
    lo = stats.beta.ppf(0.025, d, n - d + 1) if d > 0 else 0.0
    hi = stats.beta.ppf(0.975, d + 1, n - d) if d < n else 1.0
    return 1000 * d / n, 1000 * lo, 1000 * hi


def summarise(g):
    mem_n, mem_d = g.members.sum(), g.member_deaths.sum()
    hir_n, hir_d = g.hired_staff.sum(), g.hired_staff_deaths.sum()
    r_m, lo_m, hi_m = rate_ci(mem_d, mem_n)
    r_h, lo_h, hi_h = rate_ci(hir_d, hir_n)
    return pd.Series({
        "expeditions": len(g),
        "members": mem_n, "member_deaths": mem_d,
        "member_death_per_1000": r_m, "member_ci_lo": lo_m, "member_ci_hi": hi_m,
        "hired_staff": hir_n, "hired_deaths": hir_d,
        "hired_death_per_1000": r_h, "hired_ci_lo": lo_h, "hired_ci_hi": hi_h,
        "hired_per_member": hir_n / mem_n if mem_n else np.nan,
        "oxygen_share": g.oxygen_used.mean(),
        "success_share": (g.termination_reason.str.startswith("Success (main")).mean(),
        "zero_hired_share": (g.hired_staff == 0).mean(),
    })


by_dec = ev.groupby("decade").apply(summarise, include_groups=False)
by_era = ev.groupby("era").apply(summarise, include_groups=False)
overall = summarise(ev)


def rate_ratio_test(d1, n1, d2, n2):
    """Rate ratio (group1 / group2), Wald 95% CI on log scale, Fisher exact p-value."""
    if min(d1, d2) == 0:
        return np.nan, np.nan, np.nan, np.nan
    rr = (d1 / n1) / (d2 / n2)
    se = np.sqrt(1 / d1 - 1 / n1 + 1 / d2 - 1 / n2)
    lo, hi = np.exp(np.log(rr) - 1.96 * se), np.exp(np.log(rr) + 1.96 * se)
    _, p = stats.fisher_exact([[d1, n1 - d1], [d2, n2 - d2]])
    return rr, lo, hi, p


# Hired vs member rate ratio within each decade and era
tests = []
groups = [(f"{k}s", v) for k, v in ev.groupby("decade")] + list(ev.groupby("era"))
for label, g in groups:
    mn, md = g.members.sum(), g.member_deaths.sum()
    hn, hd = g.hired_staff.sum(), g.hired_staff_deaths.sum()
    rr, lo, hi, p = rate_ratio_test(hd, hn, md, mn)
    tests.append({"group": label, "hired_vs_member_RR": rr, "RR_ci_lo": lo, "RR_ci_hi": hi,
                  "fisher_p": p, "hired_deaths": hd, "hired_n": hn,
                  "member_deaths": md, "member_n": mn})
tests = pd.DataFrame(tests)

# Sensitivity: 2010s excluding 2014-2015 (Khumbu icefall years, 28 of 40 hired deaths in the 2010s)
s = ev[(ev.decade == 2010) & (~ev.year.isin([2014, 2015]))]
sens = summarise(s)
sens.to_csv(os.path.join(OUT, "sensitivity_2010s_excl_2014_2015.csv"), header=["value"])

# Post-1990 vs pre-1990 rate ratio, members and hired separately
pre, post = by_era.loc[ERA_PRE], by_era.loc[ERA_POST]
rr_m = rate_ratio_test(post.member_deaths, post.members, pre.member_deaths, pre.members)
rr_h = rate_ratio_test(post.hired_deaths, post.hired_staff, pre.hired_deaths, pre.hired_staff)
era_cmp = pd.DataFrame({
    "metric": ["member death per 1000", "hired death per 1000"],
    "pre_1990": [pre.member_death_per_1000, pre.hired_death_per_1000],
    "post_1990": [post.member_death_per_1000, post.hired_death_per_1000],
    "RR_post_vs_pre": [rr_m[0], rr_h[0]],
    "RR_ci_lo": [rr_m[1], rr_h[1]],
    "RR_ci_hi": [rr_m[2], rr_h[2]],
    "fisher_p": [rr_m[3], rr_h[3]],
})

# Death causes (member-level file, died flag)
mev = mem[mem.peak_id == "EVER"].copy()
mev["era"] = np.where(mev.year >= 1990, ERA_POST, ERA_PRE)
mev["who"] = np.where(mev.hired, "hired", "member")
cause = (mev[mev.died].groupby(["era", "who", "death_cause"]).size()
         .rename("deaths").reset_index())

# Member-level cross-check against expedition totals
xchk = mev.groupby(["era", "who"]).agg(rows=("died", "size"), deaths=("died", "sum")).reset_index()

# Save tables
by_dec.round(3).to_csv(os.path.join(OUT, "mortality_by_decade.csv"))
by_era.round(3).to_csv(os.path.join(OUT, "mortality_by_era.csv"))
tests.round(4).to_csv(os.path.join(OUT, "rate_ratio_tests.csv"), index=False)
era_cmp.round(4).to_csv(os.path.join(OUT, "pre_post_1990_comparison.csv"), index=False)
cause.to_csv(os.path.join(OUT, "death_cause_by_era.csv"), index=False)

# Chart 1: death rate per 1000 by decade, members vs hired (with exact 95% CI)
x = by_dec.index.values
bd = by_dec[by_dec.index >= 1950]  # 1920s-1940s have <50 members each: CIs too wide to plot
xb = bd.index.values
fig, ax = plt.subplots(figsize=(10, 5.5))
w = 3.5
for off, prefix, lab, color in [(-w / 2, "member", "Thành viên đoàn", "#1f4e79"),
                                (w / 2, "hired", "Nhân viên được thuê", "#d9822b")]:
    r = bd[f"{prefix}_death_per_1000"]
    lo = bd[f"{prefix}_ci_lo"]
    hi = bd[f"{prefix}_ci_hi"]
    ax.bar(xb + off, r, width=w, color=color, label=lab)
    ax.errorbar(xb + off, r, yerr=[r - lo, hi - r], fmt="none", ecolor="black", capsize=3, lw=1)
ax.axvline(1989.5, color="grey", ls="--", lw=1)
ax.set_xlabel("Thập kỷ (từ 1950s; 1920s–1940s có quá ít người để so sánh)")
ax.set_ylabel("Số ca tử vong trên 1.000 người")
ax.set_title("Tỉ lệ tử vong trên Everest đã giảm hơn một nửa sau 1990, nhất là ở nhân viên được thuê")
ax.set_xticks(xb)
ax.set_xticklabels([f"{int(v)}s" for v in xb])
ax.legend()
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_death_rate_by_decade.png"), dpi=150)
plt.close(fig)

# Chart 2: expeditions per decade and hired staff per member (1950s onward)
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.bar(xb, bd.expeditions, width=7, color="#9db9d5", label="Số đoàn leo")
ax.set_xlabel("Thập kỷ (từ 1950s)")
ax.set_ylabel("Số đoàn leo")
ax.set_xticks(xb)
ax.set_xticklabels([f"{int(v)}s" for v in xb])
ax2 = ax.twinx()
ax2.plot(xb, bd.hired_per_member, color="#d9822b", marker="o", label="Nhân viên được thuê trên mỗi thành viên")
ax2.set_ylabel("Nhân viên được thuê trên mỗi thành viên")
ax.set_title("Từ 1990, số đoàn leo tăng mạnh và số nhân viên được thuê trên mỗi thành viên tăng dần")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_expeditions_and_hired_ratio.png"), dpi=150)
plt.close(fig)

# Chart 3: oxygen use and summit success by decade
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(xb, bd.oxygen_share * 100, marker="o", color="#1f4e79", label="Tỉ lệ đoàn dùng oxy (%)")
ax.plot(xb, bd.success_share * 100, marker="s", color="#2e8b57", label="Tỉ lệ đoàn lên đỉnh chính (%)")
ax.set_xlabel("Thập kỷ (từ 1950s)")
ax.set_ylabel("% đoàn leo")
ax.set_xticks(xb)
ax.set_xticklabels([f"{int(v)}s" for v in xb])
ax.set_title("Tỉ lệ lên đỉnh chính tăng từ khoảng 30% (1980s) lên khoảng 67% (2000s–2010s)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_oxygen_success_by_decade.png"), dpi=150)
plt.close(fig)

# Console summary
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
print("== Overall (Everest) ==")
print(overall.round(3).to_string())
print("\n== By decade ==")
print(by_dec.round(2).to_string())
print("\n== By era ==")
print(by_era.round(2).to_string())
print("\n== Rate ratios hired vs member ==")
print(tests.round(3).to_string(index=False))
print("\n== Post-1990 vs pre-1990 ==")
print(era_cmp.round(3).to_string(index=False))
print("\n== Member-level cross-check (members.csv, EVER) ==")
print(xchk.to_string(index=False))
print("\n== Death causes (member-level) ==")
print(cause.sort_values(["era", "who", "deaths"], ascending=[True, True, False]).to_string(index=False))
