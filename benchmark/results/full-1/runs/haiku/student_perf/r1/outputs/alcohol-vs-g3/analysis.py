"""Is workday (Dalc) / weekend (Walc) alcohol use associated with lower final grade (G3)?

Data: student-mat.csv (Math) + student-por.csv (Portuguese), merged on the 13 keys from
student-merge.R (382 students appear in both files).

Design decisions (see answer.md):
- Each file row is one course enrolment (G3 is course-specific), so the stacked data has
  one row per enrolment (395 Math + 649 Portuguese = 1044 rows).
- Students in both files are linked (pair id) and standard errors are clustered by student.
- G3 == 0 is treated as a non-completion code (not a real grade) in the primary analysis;
  it is kept in a sensitivity analysis.
- Course, school, sex, age, study time, past failures, absences are adjusted for; a second
  model adds the earlier period grades G1 and G2.
Only numpy / pandas / scipy / matplotlib are used (statsmodels not available here).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]  # project workspace
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent

TEXT_COLS = {"school", "sex", "address", "famsize", "Pstatus", "Mjob", "Fjob", "reason",
             "guardian", "schoolsup", "famsup", "paid", "activities", "nursery", "higher",
             "internet", "romantic"}
KEYS = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
        "Mjob", "Fjob", "reason", "nursery", "internet"]


def load(fname):
    df = pd.read_csv(DATA / fname, sep=";", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df.apply(lambda s: s.str.strip().str.strip('"'))
    for c in df.columns:
        if c not in TEXT_COLS:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.reset_index(drop=True)


mat = load("student-mat.csv")
por = load("student-por.csv")
assert mat[["G1", "G2", "G3", "Dalc", "Walc"]].notna().all().all()
assert por[["G1", "G2", "G3", "Dalc", "Walc"]].notna().all().all()

# ---------- Link students who appear in both files ----------
# R-style merge count (cartesian within identical keys) - should be 382
r_style = mat.merge(por, on=KEYS)
print("R-style merge rows:", len(r_style))
# One-to-one pairing: k-th Math row with k-th Portuguese row having identical keys
mat["k"] = mat.groupby(KEYS).cumcount()
por["k"] = por.groupby(KEYS).cumcount()
pairs = mat.reset_index().merge(por.reset_index(), on=KEYS + ["k"], suffixes=("_m", "_p"))
print("one-to-one linked students:", len(pairs))
mat_pair = dict(zip(pairs["index_m"], pairs["index_p"]))
por_pair = dict(zip(pairs["index_p"], pairs["index_m"]))

# ---------- Stack into one row per course enrolment ----------
def build(df, course_por, pair_map, prefix):
    d = df.copy()
    d["course_por"] = course_por
    d["overlap"] = [i in pair_map for i in d.index]
    if course_por == 0:
        d["sid"] = [f"pair{i}_{pair_map[i]}" if i in pair_map else f"math{i}" for i in d.index]
    else:
        d["sid"] = [f"pair{pair_map[i]}_{i}" if i in pair_map else f"port{i}" for i in d.index]
    d["school_gp"] = (d["school"] == "GP").astype(int)
    d["sex_m"] = (d["sex"] == "M").astype(int)
    d["course"] = "Portuguese" if course_por else "Math"
    return d


long = pd.concat([build(mat, 0, mat_pair, "m"), build(por, 1, por_pair, "p")], ignore_index=True)
long["heavy_dalc"] = (long["Dalc"] >= 4).astype(int)
long["heavy_walc"] = (long["Walc"] >= 4).astype(int)
print("enrolment rows:", len(long), "| unique students:", long["sid"].nunique(),
      "| overlap students:", len(pairs))
print("G3==0 rows:", int((long.G3 == 0).sum()), "| of which G2>0:", int(((long.G3 == 0) & (long.G2 > 0)).sum()))


# ---------- Helpers ----------
def cluster_ols(d, y, xcols, cluster="sid"):
    xcols = [c for c in xcols if d[c].nunique() > 1]
    X = np.column_stack([np.ones(len(d))] + [d[c].to_numpy(float) for c in xcols])
    yv = d[y].to_numpy(float)
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ yv
    e = yv - X @ b
    n, k = X.shape
    codes = pd.factorize(d[cluster])[0]
    G = codes.max() + 1
    meat = np.zeros((k, k))
    for g in range(G):
        idx = codes == g
        s = X[idx].T @ e[idx]
        meat += np.outer(s, s)
    adj = (G / (G - 1)) * ((n - 1) / (n - k))
    V = adj * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    tcrit = stats.t.ppf(0.975, G - 1)
    terms = ["const"] + xcols
    res = pd.DataFrame({"term": terms, "coef": b, "se": se,
                        "ci_low": b - tcrit * se, "ci_high": b + tcrit * se,
                        "p": 2 * stats.t.sf(np.abs(b / se), G - 1)})
    ss_tot = ((yv - yv.mean()) ** 2).sum()
    r2 = 1 - (e @ e) / ss_tot
    return res, n, G, r2


def std_beta(d, x, y):
    return d[x].std() / d[y].std()


BASE = ["course_por", "school_gp", "sex_m", "age", "studytime", "failures", "absences"]
PRIOR = BASE + ["G1", "G2"]

variants = {
    "primary (G3>0, all enrolments)": long[long.G3 > 0],
    "sensitivity: keep G3==0": long,
    "Math only (G3>0)": long[(long.G3 > 0) & (long.course_por == 0)],
    "Portuguese only (G3>0)": long[(long.G3 > 0) & (long.course_por == 1)],
    "one row per student (drop Portuguese copy of overlap, G3>0)":
        long[(long.G3 > 0) & ~((long.course_por == 1) & long.overlap)],
}

rows = []
for vname, d in variants.items():
    specs = {
        "M0 unadjusted Dalc": ["Dalc"],
        "M0 unadjusted Walc": ["Walc"],
        "M0 unadjusted Dalc+Walc": ["Dalc", "Walc"],
        "M1 adjusted Dalc+Walc": ["Dalc", "Walc"] + BASE,
        "M2 adjusted + G1,G2 Dalc+Walc": ["Dalc", "Walc"] + PRIOR,
    }
    for mname, xs in specs.items():
        res, n, G, r2 = cluster_ols(d, "G3", xs)
        for _, r in res.iterrows():
            if r.term in ("Dalc", "Walc"):
                rows.append({"variant": vname, "model": mname, "term": r.term,
                             "coef_grade_pts_per_level": r.coef, "se": r.se,
                             "ci_low": r.ci_low, "ci_high": r.ci_high, "p": r.p,
                             "std_beta": r.coef * std_beta(d, r.term, "G3"),
                             "n_rows": n, "n_clusters": G, "r2": r2})
reg = pd.DataFrame(rows)
reg.to_csv(OUT / "regression_results.csv", index=False)
pd.set_option("display.width", 250)
print(reg.round(3).to_string(index=False))

# ---------- Bivariate effect sizes on primary sample ----------
prim = variants["primary (G3>0, all enrolments)"]
eff = []
for col in ["Dalc", "Walc"]:
    rho, p_rho = stats.spearmanr(prim[col], prim["G3"])
    eff.append({"measure": f"Spearman rho {col} vs G3", "value": rho, "ci_low": np.nan,
                "ci_high": np.nan, "p": p_rho, "n": len(prim)})
for col in ["heavy_dalc", "heavy_walc"]:
    hi = prim.loc[prim[col] == 1, "G3"]
    lo = prim.loc[prim[col] == 0, "G3"]
    n1, n2 = len(hi), len(lo)
    sp = np.sqrt(((n1 - 1) * hi.var(ddof=1) + (n2 - 1) * lo.var(ddof=1)) / (n1 + n2 - 2))
    d_ = (hi.mean() - lo.mean()) / sp
    se_d = np.sqrt((n1 + n2) / (n1 * n2) + d_ ** 2 / (2 * (n1 + n2)))
    J = 1 - 3 / (4 * (n1 + n2) - 9)  # Hedges small-sample correction
    g = d_ * J
    t_p = stats.ttest_ind(hi, lo, equal_var=False)
    u_p = stats.mannwhitneyu(hi, lo, alternative="two-sided").pvalue
    eff.append({"measure": f"{col} (>=4) mean diff, grade pts (high - low)",
                "value": hi.mean() - lo.mean(), "ci_low": np.nan, "ci_high": np.nan,
                "p": t_p.pvalue, "n": n1 + n2, "n_high": n1, "n_low": n2,
                "mean_high": hi.mean(), "mean_low": lo.mean()})
    eff.append({"measure": f"{col} Hedges g (high vs low)", "value": g,
                "ci_low": g - 1.96 * se_d * J, "ci_high": g + 1.96 * se_d * J,
                "p": u_p, "n": n1 + n2, "n_high": n1, "n_low": n2})
eff = pd.DataFrame(eff)
eff.to_csv(OUT / "effect_sizes.csv", index=False)
print(eff.round(3).to_string(index=False))

# ---------- Descriptives ----------
desc = prim.groupby("Dalc")["G3"].agg(["count", "mean", "median"]).round(2)
desc2 = prim.groupby("Walc")["G3"].agg(["count", "mean", "median"]).round(2)
print("G3 by Dalc (primary):\n", desc.to_string())
print("G3 by Walc (primary):\n", desc2.to_string())
desc.to_csv(OUT / "g3_by_dalc.csv")
desc2.to_csv(OUT / "g3_by_walc.csv")

# ---------- Are G3==0 rows different in alcohol use? ----------
zero = long[long.G3 == 0]
nonzero = long[long.G3 > 0]
print("G3==0 rows: n=%d, mean Dalc=%.2f, mean Walc=%.2f, mean G2=%.2f" %
      (len(zero), zero.Dalc.mean(), zero.Walc.mean(), zero.G2.mean()))
print("G3>0 rows : n=%d, mean Dalc=%.2f, mean Walc=%.2f, mean G2=%.2f" %
      (len(nonzero), nonzero.Dalc.mean(), nonzero.Walc.mean(), nonzero.G2.mean()))
print("MWU Dalc zero vs nonzero p=%.3f" % stats.mannwhitneyu(zero.Dalc, nonzero.Dalc).pvalue)
print("MWU Walc zero vs nonzero p=%.3f" % stats.mannwhitneyu(zero.Walc, nonzero.Walc).pvalue)

# ---------- Chart ----------
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
for ax, col, title in [(axes[0], "Dalc", "Workday alcohol (Dalc)"),
                       (axes[1], "Walc", "Weekend alcohol (Walc)")]:
    g = prim.groupby(col)["G3"]
    m, n_, s = g.mean(), g.count(), g.std()
    ci = stats.t.ppf(0.975, n_ - 1) * s / np.sqrt(n_)
    ax.errorbar(m.index, m.values, yerr=ci.values, fmt="o-", color="#1f4e79", capsize=4)
    for x, mv, nn in zip(m.index, m.values, n_.values):
        ax.annotate(f"n={nn}", (x, mv), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8)
    ax.set_title(title)
    ax.set_xlabel("Level (1 = very low, 5 = very high)")
    ax.grid(alpha=0.3)
axes[0].set_ylabel("Mean final grade G3 (95% CI)")
fig.suptitle("Final grade by alcohol consumption (G3>0, both courses, enrolment rows)")
fig.tight_layout()
fig.savefig(OUT / "g3_by_alcohol.png", dpi=150)
print("saved outputs")
