"""Health spending vs life expectancy, income-adjusted (World Bank WDI extracts).

Primary cross-section: 2019 (last pre-COVID year with broad coverage).
Robustness: 2010 and 2023.
Run from the project root:  python outputs/health-spend-vs-life-expectancy/analysis.py
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = "data"
OUT = "outputs/health-spend-vs-life-expectancy"
os.makedirs(OUT, exist_ok=True)
PRIMARY_YEAR = 2019
ROBUST_YEARS = [2010, 2023]

FILES = {
    "le": f"{D}/life_expectancy/API_SP.DYN.LE00.IN_DS2_en_csv_v2_259172.csv",
    "hx": f"{D}/health_expenditure_per_capita/API_SH.XPD.CHEX.PC.CD_DS2_en_csv_v2_3808.csv",
    "gdp": f"{D}/gdp_per_capita_ppp/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_1247.csv",
}
META = f"{D}/life_expectancy/Metadata_Country_API_SP.DYN.LE00.IN_DS2_en_csv_v2_259172.csv"
YEARS = [str(y) for y in range(1960, 2026)]


def load_wide(path):
    df = pd.read_csv(path, skiprows=4)
    return df.set_index("Country Code")[YEARS].apply(pd.to_numeric, errors="coerce")


meta = pd.read_csv(META).rename(columns={"Country Code": "code"}).set_index("code")
# Keep real countries/territories: WB aggregates have no Region in metadata.
country_codes = set(meta.index[meta["Region"].notna()])
wide = {k: load_wide(p) for k, p in FILES.items()}


def build(year):
    c = str(year)
    d = pd.DataFrame({
        "LE": wide["le"][c],
        "HX": wide["hx"][c],
        "GDP": wide["gdp"][c],
    })
    d = d.loc[d.index.isin(country_codes)].dropna()
    d["logHX"] = np.log(d["HX"])
    d["logGDP"] = np.log(d["GDP"])
    d["name"] = pd.read_csv(FILES["le"], skiprows=4).set_index("Country Code")["Country Name"].reindex(d.index)
    d["region"] = meta["Region"].reindex(d.index)
    d["income"] = meta["IncomeGroup"].reindex(d.index)
    return d


def ols(X, y):
    X1 = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    resid = y - X1 @ beta
    n, k = X1.shape
    s2 = resid @ resid / (n - k)
    cov = s2 * np.linalg.inv(X1.T @ X1)
    se = np.sqrt(np.diag(cov))
    r2 = 1 - resid @ resid / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, r2, resid


def income_curve(logGDP, LE):
    """Expected LE as a function of log GDP/capita: cubic polynomial fit (income-only benchmark)."""
    coef = np.polyfit(logGDP, LE, 3)
    return coef


summary_rows = []
primary = build(PRIMARY_YEAR)
print(f"Primary year {PRIMARY_YEAR}: n={len(primary)} countries with LE, health spend and GDP")

# 1) Raw association
r_raw, p_raw = stats.pearsonr(primary["logHX"], primary["LE"])
rho_raw, prho_raw = stats.spearmanr(primary["HX"], primary["LE"])
print(f"Raw: Pearson r(logHX, LE)={r_raw:.3f} (p={p_raw:.2g}); Spearman rho(HX, LE)={rho_raw:.3f}")

# Quartiles of health spend
primary["HX_quartile"] = pd.qcut(primary["HX"], 4, labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"])
quart = primary.groupby("HX_quartile", observed=True).agg(
    n=("LE", "size"), median_HX_usd=("HX", "median"), mean_LE=("LE", "mean"),
    median_GDP=("GDP", "median"))
quart.to_csv(f"{OUT}/spend_quartiles_{PRIMARY_YEAR}.csv")
print(quart.round(1).to_string())

# 2) Income-only benchmark: LE ~ cubic(logGDP)
coef = income_curve(primary["logGDP"].values, primary["LE"].values)
primary["LE_expected_income"] = np.polyval(coef, primary["logGDP"])
primary["gap_income"] = primary["LE"] - primary["LE_expected_income"]
r2_income = 1 - ((primary["LE"] - primary["LE_expected_income"]) ** 2).sum() / ((primary["LE"] - primary["LE"].mean()) ** 2).sum()
print(f"Income-only curve R^2 = {r2_income:.3f}")

# 3) Does spending add beyond income? Linear OLS with both logs
beta, se, r2_both, _ = ols(primary[["logGDP", "logHX"]].values, primary["LE"].values)
beta_h = beta[2]; se_h = se[2]
t = beta_h / se_h
p = 2 * (1 - stats.t.cdf(abs(t), len(primary) - 3))
print(f"OLS LE ~ logGDP + logHX: b_logGDP={beta[1]:.2f} (se {se[1]:.2f}), b_logHX={beta_h:.2f} (se {se_h:.2f}, p={p:.2g}), R2={r2_both:.3f}")
beta_g, se_g, r2_g, _ = ols(primary[["logGDP"]].values, primary["LE"].values)
beta_x, se_x, r2_x, _ = ols(primary[["logHX"]].values, primary["LE"].values)
print(f"OLS LE ~ logGDP only R2={r2_g:.3f}; LE ~ logHX only R2={r2_x:.3f}")

# Partial correlation of LE and logHX given logGDP (residual-on-residual)
_, _, _, res_le = ols(primary[["logGDP"]].values, primary["LE"].values)
_, _, _, res_hx = ols(primary[["logGDP"]].values, primary["logHX"].values)
pr, pp = stats.pearsonr(res_hx, res_le)
print(f"Partial r(LE, logHX | logGDP) = {pr:.3f} (p={pp:.2g})")

# Bootstrap CI for the partial coefficient on logHX
rng = np.random.default_rng(42)
boots = []
for _ in range(2000):
    idx = rng.integers(0, len(primary), len(primary))
    b, *_ = ols(primary[["logGDP", "logHX"]].values[idx], primary["LE"].values[idx])
    boots.append(b[2])
ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
print(f"Bootstrap 95% CI for b_logHX: [{ci_lo:.2f}, {ci_hi:.2f}]")

# Interpretation: effect of doubling spend, income-adjusted
print(f"Doubling health spend (log2) ~ {beta_h*np.log(2):.2f} years LE (income-adjusted, linear model); "
      f"bootstrap 95% CI [{ci_lo*np.log(2):.2f}, {ci_hi*np.log(2):.2f}]")

# Robustness across years
rob_rows = []
for y in [PRIMARY_YEAR] + ROBUST_YEARS:
    d = build(y)
    b, s, r2, _ = ols(d[["logGDP", "logHX"]].values, d["LE"].values)
    rr, _ = stats.pearsonr(d["logHX"], d["LE"])
    rob_rows.append({"year": y, "n": len(d), "r_raw_logHX_LE": rr,
                     "b_logHX_income_adj": b[2], "se": s[2], "R2_both": r2})
rob = pd.DataFrame(rob_rows)
rob.to_csv(f"{OUT}/robustness_by_year.csv", index=False)
print(rob.round(3).to_string())

# 4) Ranking by gap vs income benchmark
primary = primary.sort_values("gap_income", ascending=False)
cols = ["name", "region", "income", "LE", "HX", "GDP", "LE_expected_income", "gap_income"]
out = primary[cols].round(2)
out.to_csv(f"{OUT}/gap_vs_income_{PRIMARY_YEAR}.csv", index_label="code")
print("\nTop 15 OVER expectation:")
print(out.head(15).to_string())
print("\nTop 15 UNDER expectation:")
print(out.tail(15).iloc[::-1].to_string())

# Vietnam
vn = out.loc[out.index == "VNM"]
rank = list(out.index).index("VNM") + 1
print(f"\nVietnam (VNM) rank {rank} of {len(out)} by gap (1 = most above expectation):")
print(vn.to_string())
pct = 100 * (out["gap_income"] < vn["gap_income"].iloc[0]).mean()
print(f"Vietnam gap percentile: {pct:.0f}")
# Comparable peers: same income group as Vietnam in current WB metadata
vn_group = meta.loc["VNM", "IncomeGroup"]
peers = out[out["income"] == vn_group]
peer_rank = list(peers.index).index("VNM") + 1
print(f"\nVietnam (WB group today: {vn_group}) among peers: rank {peer_rank} of {len(peers)} by gap")
print(f"Peer gap median = {peers['gap_income'].median():+.2f}; Vietnam gap = {out.loc['VNM','gap_income']:+.2f}")
print("Peers ranked (first 8 and last 8):")
print(pd.concat([peers.head(8), peers.tail(8)])[["name", "LE", "HX", "GDP", "gap_income"]].round(2).to_string())
# Bootstrap-free sanity: Vietnam health spend vs income-group median
print(f"Vietnam HX=${out.loc['VNM','HX']:.0f} vs peer-group median HX=${peers['HX'].median():.0f}; GDP=${out.loc['VNM','GDP']:.0f} vs peer median ${peers['GDP'].median():.0f}")

# Vietnam in other years
for y in [2010, 2023]:
    d = build(y)
    if "VNM" in d.index:
        dd = d.copy()
        c = np.polyfit(dd["logGDP"], dd["LE"], 3)
        dd["gap"] = dd["LE"] - np.polyval(c, dd["logGDP"])
        print(f"Vietnam {y}: LE={dd.loc['VNM','LE']:.1f}, HX=${dd.loc['VNM','HX']:.0f}, GDP=${dd.loc['VNM','GDP']:.0f}, gap={dd.loc['VNM','gap']:+.2f}, rank {list(dd.sort_values('gap', ascending=False).index).index('VNM')+1}/{len(dd)}")

# Charts
inc_colors = {"Low income": "#1b9e77", "Lower middle income": "#7570b3",
              "Upper middle income": "#d95f02", "High income": "#1f78b4"}

fig, ax = plt.subplots(figsize=(8, 5.5))
for g, sub in primary.groupby("income"):
    ax.scatter(sub["HX"], sub["LE"], s=22, alpha=0.75, label=g, color=inc_colors.get(g, "grey"))
ax.set_xscale("log")
ax.set_xlabel("Health expenditure per capita, US$ (log scale)")
ax.set_ylabel("Life expectancy at birth (years)")
ax.set_title(f"Higher health spending goes with longer life, {PRIMARY_YEAR}\n(but mostly because richer countries spend more)")
v = primary.loc["VNM"]
ax.annotate("Vietnam", (v["HX"], v["LE"]), xytext=(8, -12), textcoords="offset points", fontsize=9, color="black",
            arrowprops=dict(arrowstyle="-", color="grey"))
ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/chart1_spend_vs_le.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5.5))
for g, sub in primary.groupby("income"):
    ax.scatter(sub["GDP"], sub["LE"], s=22, alpha=0.75, label=g, color=inc_colors.get(g, "grey"))
xs = np.linspace(np.log(primary["GDP"].min()), np.log(primary["GDP"].max()), 200)
ax.plot(np.exp(xs), np.polyval(coef, xs), color="black", lw=1.5, label="Income-only expectation")
ax.set_xscale("log")
ax.set_xlabel("GDP per capita, PPP US$ (log scale)")
ax.set_ylabel("Life expectancy at birth (years)")
ax.set_title(f"Life expectancy vs income, {PRIMARY_YEAR}: the benchmark line")
top = pd.concat([out.head(3), out.tail(3), out.loc[["VNM"]]])
for code, r in top.iterrows():
    ax.annotate(r["name"], (r["GDP"], r["LE"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/chart2_income_benchmark.png", dpi=150)
plt.close(fig)

# Top/bottom gap chart
fig, ax = plt.subplots(figsize=(8, 7))
sel = pd.concat([out.head(12), out.tail(12), out.loc[["VNM"]]]).drop_duplicates()
sel = sel.sort_values("gap_income")
colors = ["#b2182b" if x < 0 else "#2166ac" for x in sel["gap_income"]]
colors = ["#f4a582" if c == "VNM" else col for c, col in zip(sel.index, colors)]
ax.barh(sel["name"], sel["gap_income"], color=colors)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Years of life expectancy above (+) / below (−) income-based expectation")
ax.set_title(f"Income-adjusted life expectancy gap, {PRIMARY_YEAR}\n(Vietnam highlighted)")
ax.tick_params(axis="y", labelsize=7)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/chart3_gap_ranking.png", dpi=150)
plt.close(fig)
print("\nCharts saved.")
