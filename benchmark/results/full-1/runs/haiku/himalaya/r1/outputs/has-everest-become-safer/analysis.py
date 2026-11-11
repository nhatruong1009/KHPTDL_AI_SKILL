"""Has climbing Mount Everest become safer over time?

Death rates for expedition members vs hired staff, by decade, and the
pre-commercial (1921-1989) vs commercial (1990-2019) comparison.

Run:  python -I analysis.py   (from this folder; reads ../../data, read-only)
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
COMMERCIAL_START = 1990
PRE = "Pre-commercial (1921-1989)"
COM = "Commercial (1990-2019)"

# ---------- load ----------
exp_all = pd.read_csv(os.path.join(DATA, "expeditions.csv"))
mem_all = pd.read_csv(os.path.join(DATA, "members.csv"), low_memory=False)
exp = exp_all[exp_all.peak_id == "EVER"].copy()
mem = mem_all[mem_all.peak_id == "EVER"].copy()
print(f"Everest expeditions: {len(exp)} ({exp.year.min()}-{exp.year.max()})")
print(f"Everest member rows: {len(mem)}")

# Expedition-level totals are the complete record of people and deaths.
# Member-level rows are used for roles, causes and summit detail.
exp["era"] = np.where(exp.year >= COMMERCIAL_START, COM, PRE)
mem["era"] = np.where(mem.year >= COMMERCIAL_START, COM, PRE)
exp["decade"] = (exp.year // 10) * 10
mem["decade"] = (mem.year // 10) * 10


def wilson(k, n, z=1.96):
    """Wilson 95% CI for a proportion k/n."""
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1 + z ** 2 / n
    centre = (p + z ** 2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return (centre - half, centre + half)


# ---------- 1. decade table (expedition-level totals) ----------
g = exp.groupby("decade")
dec = pd.DataFrame({
    "expeditions": g.size(),
    "members": g.members.sum(),
    "member_deaths": g.member_deaths.sum(),
    "hired_staff": g.hired_staff.sum(),
    "hired_staff_deaths": g.hired_staff_deaths.sum(),
})
dec["member_death_rate_pct"] = 100 * dec.member_deaths / dec.members
dec["hired_death_rate_pct"] = 100 * dec.hired_staff_deaths / dec.hired_staff
dec["hired_per_member"] = dec.hired_staff / dec.members
dec["small_sample_flag"] = (dec.members < 100) | (dec.hired_staff < 100)
dec = dec.reset_index()
dec.round(3).to_csv(os.path.join(HERE, "decade_death_rates.csv"), index=False)
print("\nDecade table:\n", dec.round(2).to_string(index=False))

# ---------- 2. era comparison with CIs and tests ----------
era_rows = []
for era_name, sub in exp.groupby("era"):
    for who, k_col, n_col in [("Expedition members", "member_deaths", "members"),
                              ("Hired staff", "hired_staff_deaths", "hired_staff")]:
        k, n = int(sub[k_col].sum()), int(sub[n_col].sum())
        lo, hi = wilson(k, n)
        era_rows.append({"era": era_name, "group": who, "deaths": k, "people": n,
                         "death_rate_pct": 100 * k / n, "ci_low_pct": 100 * lo, "ci_high_pct": 100 * hi})
era = pd.DataFrame(era_rows)
era.round(3).to_csv(os.path.join(HERE, "era_death_rates.csv"), index=False)
print("\nEra table:\n", era.round(3).to_string(index=False))

pre = exp[exp.era == PRE]
com = exp[exp.era == COM]
tests = []
for who, k_col, n_col in [("Expedition members", "member_deaths", "members"),
                          ("Hired staff", "hired_staff_deaths", "hired_staff")]:
    table = np.array([
        [pre[k_col].sum(), pre[n_col].sum() - pre[k_col].sum()],
        [com[k_col].sum(), com[n_col].sum() - com[k_col].sum()],
    ])
    chi2, p, _, _ = stats.chi2_contingency(table, correction=False)
    rr = (com[k_col].sum() / com[n_col].sum()) / (pre[k_col].sum() / pre[n_col].sum())
    tests.append({"group": who, "rate_ratio_commercial_vs_pre": rr, "chi2": chi2, "p_value": p})
tests = pd.DataFrame(tests)
tests.to_csv(os.path.join(HERE, "era_tests.csv"), index=False)
print("\nEra tests (person-level chi-square; ignores expedition clustering):\n", tests.to_string(index=False))

# ---------- 3. sensitivity: commercial era without the 2014 and 2015 disasters ----------
# 2014 (Khumbu icefall) and 2015 (base camp avalanche) are the two worst years for hired-staff
# deaths in this data (see top_years_hired_deaths.csv). Event names are outside context, not from data.
sens_rows = []
for label, sub in [("Commercial, all years", com),
                   ("Commercial, excl. 2014-2015", com[~com.year.isin([2014, 2015])])]:
    k, n = int(sub.hired_staff_deaths.sum()), int(sub.hired_staff.sum())
    sens_rows.append({"sample": label, "group": "Hired staff", "deaths": k, "people": n, "death_rate_pct": 100 * k / n})
    k, n = int(sub.member_deaths.sum()), int(sub.members.sum())
    sens_rows.append({"sample": label, "group": "Expedition members", "deaths": k, "people": n, "death_rate_pct": 100 * k / n})
for dec_start in [1990, 2000, 2010]:
    sub = exp[(exp.decade == dec_start) & (~exp.year.isin([2014, 2015]))]
    k, n = int(sub.hired_staff_deaths.sum()), int(sub.hired_staff.sum())
    sens_rows.append({"sample": f"{dec_start}s excl. 2014-2015", "group": "Hired staff", "deaths": k, "people": n, "death_rate_pct": 100 * k / n})
    k, n = int(sub.member_deaths.sum()), int(sub.members.sum())
    sens_rows.append({"sample": f"{dec_start}s excl. 2014-2015", "group": "Expedition members", "deaths": k, "people": n, "death_rate_pct": 100 * k / n})
sens = pd.DataFrame(sens_rows)
sens.round(3).to_csv(os.path.join(HERE, "sensitivity_excl_2014_2015.csv"), index=False)
print("\nSensitivity:\n", sens.round(3).to_string(index=False))

# Single-year spikes in deaths
yr = exp.groupby("year").agg(hired_staff_deaths=("hired_staff_deaths", "sum"),
                             member_deaths=("member_deaths", "sum"),
                             hired_staff=("hired_staff", "sum"),
                             members=("members", "sum"))
top_years = yr.sort_values("hired_staff_deaths", ascending=False).head(8)
top_years.to_csv(os.path.join(HERE, "top_years_hired_deaths.csv"))
print("\nTop years by hired-staff deaths:\n", top_years.to_string())

# ---------- 4. commercial-era changes (member-level detail) ----------
mem_m = mem[~mem.hired].copy()  # expedition members (not hired)
mem_m["summit"] = mem_m.success.astype(bool)
change = []
for era_name, sub in mem_m.groupby("era"):
    change.append({
        "era": era_name,
        "member_rows": len(sub),
        "oxygen_share_pct": 100 * sub.oxygen_used.mean(),
        "summit_share_pct": 100 * sub.summit.mean(),
        "deaths_per_100_summits": 100 * sub.died.sum() / max(sub.summit.sum(), 1),
        "median_age": sub.age.median(),
        "female_share_pct": 100 * (sub.sex == "F").mean(),
    })
change = pd.DataFrame(change)
change.round(2).to_csv(os.path.join(HERE, "era_member_profile.csv"), index=False)
print("\nMember profile by era:\n", change.round(2).to_string(index=False))

# Death causes among Everest deaths in the member table, by era
deaths_mem = mem[mem.died]
causes = pd.crosstab(deaths_mem.death_cause, deaths_mem.era)
causes_share = 100 * causes / causes.sum()
causes_out = causes.join(causes_share, lsuffix="_deaths", rsuffix="_share_pct").round(1)
causes_out.to_csv(os.path.join(HERE, "death_causes_by_era.csv"))
print("\nDeath causes by era (member table; counts and share of each era's deaths):\n", causes_out.to_string())
print("Death totals (member table):", causes.sum().to_dict())

# Expedition structure by era
per_exp = exp.groupby("era").agg(
    expeditions=("expedition_id", "size"),
    mean_members=("members", "mean"),
    mean_hired=("hired_staff", "mean"),
    oxygen_expedition_share_pct=("oxygen_used", lambda s: 100 * s.mean()),
    agency_named_share_pct=("trekking_agency", lambda s: 100 * s.notna().mean()),
)
per_exp.round(2).to_csv(os.path.join(HERE, "era_expedition_profile.csv"))
print("\nExpedition profile by era:\n", per_exp.round(2).to_string())

# ---------- 5. charts ----------
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
C_MEM, C_HIRED, C_GREY = "#1f4e79", "#c0504d", "#7f7f7f"

# Chart 1: death rates by decade (1960s onward; 1950s has only 9 expeditions)
d = dec[dec.decade >= 1960].copy()
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(d.decade, d.hired_death_rate_pct, marker="o", color=C_HIRED, lw=2.2, label="Hired staff")
ax.plot(d.decade, d.member_death_rate_pct, marker="o", color=C_MEM, lw=2.2, label="Expedition members")
ax.axvline(COMMERCIAL_START, color=C_GREY, ls="--", lw=1)
ax.set_ylim(0, max(d.hired_death_rate_pct.max(), d.member_death_rate_pct.max()) * 1.3)
ax.text(COMMERCIAL_START + 1, 0.08, "Commercial era\nbegins (1990)", color=C_GREY, fontsize=10)
ax.set_xlabel("Decade of expedition")
ax.set_ylabel("Deaths per 100 people on expeditions")
ax.set_title("Everest death rates by decade: hired staff vs expedition members")
ax.legend(frameon=False, loc="upper right")
for x, h, m in zip(d.decade, d.hired_death_rate_pct, d.member_death_rate_pct):
    hi_above = h >= m
    ax.annotate(f"{h:.1f}", (x, h), textcoords="offset points", xytext=(0, 8 if hi_above else -16),
                ha="center", fontsize=9, color=C_HIRED)
    ax.annotate(f"{m:.1f}", (x, m), textcoords="offset points", xytext=(0, -16 if hi_above else 8),
                ha="center", fontsize=9, color=C_MEM)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart1_death_rate_by_decade.png"), dpi=150)
plt.close(fig)

# Chart 2: era comparison with 95% CIs
fig, ax = plt.subplots(figsize=(8, 5))
labels = ["Pre-commercial\n(1921-1989)", "Commercial\n(1990-2019)"]
x = np.arange(2)
w = 0.35
for i, (who, col) in enumerate([("Expedition members", C_MEM), ("Hired staff", C_HIRED)]):
    sub = era[era.group == who].set_index("era").loc[[PRE, COM]]
    yerr = [sub.death_rate_pct - sub.ci_low_pct, sub.ci_high_pct - sub.death_rate_pct]
    ax.bar(x + (i - 0.5) * w, sub.death_rate_pct, w, color=col, label=who, yerr=yerr, capsize=4)
    for xi, v in zip(x + (i - 0.5) * w, sub.death_rate_pct):
        ax.text(xi, v + 0.25, f"{v:.1f}%", ha="center", fontsize=10)
ax.set_xticks(x, labels)
ax.set_ylabel("Deaths per 100 people (95% CI)")
ax.set_title("Death rate on Everest, before vs during the commercial era")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart2_era_comparison.png"), dpi=150)
plt.close(fig)

# Chart 3: people on expeditions per decade
fig, ax = plt.subplots(figsize=(9, 5))
d2 = dec[dec.decade >= 1950]
ax.bar(d2.decade, d2.members, width=7, color=C_MEM, alpha=0.85, label="Expedition members")
ax.bar(d2.decade, d2.hired_staff, width=3, color=C_HIRED, alpha=0.9, label="Hired staff (above base camp)")
ax.set_xlabel("Decade of expedition")
ax.set_ylabel("People on Everest expeditions (total)")
ax.set_title("Everest: people on expeditions per decade")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart3_people_by_decade.png"), dpi=150)
plt.close(fig)

print("\nDone. Outputs written to", HERE)
