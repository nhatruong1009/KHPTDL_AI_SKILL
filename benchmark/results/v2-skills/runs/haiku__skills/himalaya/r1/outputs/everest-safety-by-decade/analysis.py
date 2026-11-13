"""Everest death rates: expedition members vs hired staff, by decade and by era (pre/post 1990).
Run from the project root: python -I outputs/everest-safety-by-decade/analysis.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
OUT = HERE

ERA_PRE = "Trước 1990"
ERA_POST = "1990 trở đi (thương mại)"

exp = pd.read_csv(os.path.join(DATA, "expeditions.csv"))
mem = pd.read_csv(os.path.join(DATA, "members.csv"), low_memory=False)

ex = exp[exp.peak_id == "EVER"].copy()
mm = mem[mem.peak_id == "EVER"].copy()
for df in (ex, mm):
    df["decade"] = (df.year // 10 * 10).astype(int)
    df["era"] = np.where(df.year >= 1990, ERA_POST, ERA_PRE)


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    d = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / d
    return c - h, c + h


# ---- Expedition-level (README definition of denominators) ----
def agg_exp(df, key):
    g = df.groupby(key).agg(
        expeditions=("expedition_id", "size"),
        members=("members", "sum"),
        member_deaths=("member_deaths", "sum"),
        hired_staff=("hired_staff", "sum"),
        hired_staff_deaths=("hired_staff_deaths", "sum"),
    ).reset_index()
    g["member_death_rate_pct"] = 100 * g.member_deaths / g.members
    g["hired_death_rate_pct"] = 100 * g.hired_staff_deaths / g.hired_staff
    return g


by_decade = agg_exp(ex, "decade")
by_era = agg_exp(ex, "era")


# ---- Person-level cross-check (members.csv) ----
def agg_person(df, key):
    g = df.groupby([key, "hired"]).agg(persons=("died", "size"), deaths=("died", "sum")).reset_index()
    g["group"] = np.where(g.hired, "hired", "member")
    w = g.pivot_table(index=key, columns="group", values=["persons", "deaths"], aggfunc="sum")
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    w = w.reset_index()
    w["member_death_rate_pct_persons"] = 100 * w.deaths_member / w.persons_member
    w["hired_death_rate_pct_persons"] = 100 * w.deaths_hired / w.persons_hired
    return w


pe_decade = agg_person(mm, "decade")
pe_era = agg_person(mm, "era")


# ---- Tests: pre-1990 vs 1990+ (expedition-level counts) ----
tests = []
rows = by_era.set_index("era")
a, b = rows.loc[ERA_PRE], rows.loc[ERA_POST]
for grp, col_d, col_n in [("thành viên", "member_deaths", "members"),
                          ("nhân viên được thuê", "hired_staff_deaths", "hired_staff")]:
    table = [[a[col_d], a[col_n] - a[col_d]], [b[col_d], b[col_n] - b[col_d]]]
    _, p = stats.fisher_exact(table)
    ci_a = wilson(a[col_d], a[col_n])
    ci_b = wilson(b[col_d], b[col_n])
    tests.append({
        "nhóm": grp,
        "tỉ lệ trước 1990 (%)": round(100 * a[col_d] / a[col_n], 2),
        "CI95 trước 1990 (%)": f"{100*ci_a[0]:.2f}–{100*ci_a[1]:.2f}",
        "tỉ lệ 1990+ (%)": round(100 * b[col_d] / b[col_n], 2),
        "CI95 1990+ (%)": f"{100*ci_b[0]:.2f}–{100*ci_b[1]:.2f}",
        "p (Fisher)": p,
    })
tests = pd.DataFrame(tests)


# ---- Trend within the commercial era ----
ex_c = ex[ex.year >= 1990]
trend_rows = []
for grp, col_d, col_n in [("thành viên", "member_deaths", "members"),
                          ("nhân viên được thuê", "hired_staff_deaths", "hired_staff")]:
    sub = ex_c[ex_c[col_n] > 0]
    r = stats.linregress(sub.year, sub[col_d] / sub[col_n])
    trend_rows.append({"nhóm": grp, "độ dốc/năm (tỉ lệ)": r.slope, "p": r.pvalue})
trend = pd.DataFrame(trend_rows)


# ---- Save ----
by_decade.round(3).to_csv(os.path.join(OUT, "death_rate_by_decade.csv"), index=False)
by_era.round(3).to_csv(os.path.join(OUT, "death_rate_by_era.csv"), index=False)
pe_decade.round(3).to_csv(os.path.join(OUT, "death_rate_by_decade_persons.csv"), index=False)
tests.to_csv(os.path.join(OUT, "era_tests.csv"), index=False)
trend.to_csv(os.path.join(OUT, "trend_1990plus.csv"), index=False)

print("== Theo thập kỷ (expedition-level) ==")
print(by_decade.round(2).to_string(index=False))
print("\n== Theo kỷ nguyên ==")
print(by_era.round(2).to_string(index=False))
print("\n== Cross-check person-level (members.csv), theo thập kỷ ==")
print(pe_decade.round(2).to_string(index=False))
print("\n== Cross-check person-level, theo kỷ nguyên ==")
print(pe_era.round(2).to_string(index=False))
print("\n== Kiểm định trước/sau 1990 ==")
print(tests.to_string(index=False))
print("\n== Xu hướng sau 1990 ==")
print(trend.to_string(index=False))


# ---- Chart: rates by decade ----
fig, ax = plt.subplots(figsize=(9, 5.2))
d = by_decade.set_index("decade")
ax.plot(d.index, d["member_death_rate_pct"], marker="o", lw=2.5, color="#1f4e79",
        label="Thành viên đoàn thám hiểm")
ax.plot(d.index, d["hired_death_rate_pct"], marker="o", lw=2.5, color="#c55a11",
        label="Nhân viên được thuê")
ax.axvline(1989.5, color="grey", ls="--", lw=1)
ymax = max(d["member_death_rate_pct"].max(), d["hired_death_rate_pct"].max())
ax.set_ylim(0, ymax * 1.15)
ax.text(1990, ymax * 1.05, "Kỷ nguyên thương mại (từ 1990)", fontsize=9, color="grey")
ax.set_xlabel("Thập kỷ")
ax.set_ylabel("Tỉ lệ tử vong (% trên tổng số người)")
ax.set_title("Tỉ lệ tử vong trên Everest giảm rõ từ sau 1990 ở cả hai nhóm, và không còn giảm thêm sau 2000")
ax.legend(frameon=False)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "death_rate_by_decade.png"), dpi=150)
print("\nSaved outputs.")
