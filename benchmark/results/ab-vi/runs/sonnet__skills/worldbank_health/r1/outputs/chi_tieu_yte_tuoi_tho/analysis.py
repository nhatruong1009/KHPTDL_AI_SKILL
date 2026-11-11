import pandas as pd, numpy as np, glob, os
import statsmodels.api as sm
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join("outputs", "chi_tieu_yte_tuoi_tho")
os.makedirs(OUT, exist_ok=True)

def load(folder):
    f = glob.glob("data/" + folder + "/API*.csv")[0]
    return pd.read_csv(f, skiprows=4)

meta = pd.read_csv(glob.glob("data/life_expectancy/Metadata_Country*.csv")[0])
meta = meta[meta["Region"].notna()][["Country Code", "Region", "IncomeGroup"]]  # loại nhóm tổng hợp

def panel(year):
    d = {}
    for k, fo in [("le", "life_expectancy"), ("health", "health_expenditure_per_capita"), ("gdp", "gdp_per_capita_ppp")]:
        x = load(fo)
        d[k] = x.set_index("Country Code")[str(year)]
    names = load("life_expectancy").set_index("Country Code")["Country Name"]
    df = pd.DataFrame(d)
    df["name"] = names
    df = df.reset_index().merge(meta, on="Country Code")
    df = df.dropna(subset=["le", "health", "gdp"])
    df = df[(df.health > 0) & (df.gdp > 0)].copy()
    df["lh"] = np.log(df.health)
    df["lg"] = np.log(df.gdp)
    return df

def fit(df, cols):
    return sm.OLS(df.le, sm.add_constant(df[cols])).fit()

res = {}
rows = []
for yr in [2019, 2023]:
    df = panel(yr)
    s1 = stats.spearmanr(df.health, df.le)[0]
    m_h = fit(df, ["lh"]); m_g = fit(df, ["lg"]); m_b = fit(df, ["lh", "lg"])
    ci = m_b.conf_int()
    rows.append(dict(year=yr, n=len(df), pearson_raw=stats.pearsonr(df.health, df.le)[0], spearman_raw=s1,
                     pearson_log=stats.pearsonr(df.lh, df.le)[0],
                     r2_health=m_h.rsquared, r2_gdp=m_g.rsquared, r2_both=m_b.rsquared,
                     b_health_alone=m_h.params["lh"], b_gdp_alone=m_g.params["lg"],
                     b_health_both=m_b.params["lh"], p_health_both=m_b.pvalues["lh"],
                     ci_lo=ci.loc["lh", 0], ci_hi=ci.loc["lh", 1],
                     b_gdp_both=m_b.params["lg"], p_gdp_both=m_b.pvalues["lg"]))
    df["pred_gdp"] = m_g.predict(sm.add_constant(df[["lg"]]))
    df["resid_gdp"] = df.le - df.pred_gdp
    df["pred_both"] = m_b.predict(sm.add_constant(df[["lh", "lg"]]))
    df["resid_both"] = df.le - df.pred_both
    df["rank_resid_gdp"] = df.resid_gdp.rank(ascending=False).astype(int)
    df.to_csv(OUT + "/country_residuals_" + str(yr) + ".csv", index=False)
    res[yr] = (df, m_g, m_b)

summ = pd.DataFrame(rows).set_index("year").T
summ.to_csv(OUT + "/model_summary.csv")
print(summ.to_string())

df, m_g, m_b = res[2023]
df19 = res[2019][0]
s1 = stats.spearmanr(df.health, df.le)[0]
cols = ["name", "Region", "IncomeGroup", "le", "health", "gdp", "pred_gdp", "resid_gdp", "resid_both"]
top = df.sort_values("resid_gdp", ascending=False)
print("\nTOP over\n", top[cols].head(10).round(2).to_string())
print("\nBOTTOM\n", top[cols].tail(10).round(2).to_string())
top.head(10)[cols].to_csv(OUT + "/top10_vuot_ky_vong.csv", index=False)
top.tail(10)[cols].to_csv(OUT + "/top10_duoi_ky_vong.csv", index=False)
v = df[df["Country Code"] == "VNM"].iloc[0]
print("\nVN", v[cols + ["rank_resid_gdp"]].to_dict(), "of", len(df))
print("VN 2019", df19[df19["Country Code"] == "VNM"][["resid_gdp", "rank_resid_gdp"]].to_dict("records"), len(df19))
print("VN pct ranks health/gdp/le", (df.health < v.health).mean(), (df.gdp < v.gdp).mean(), (df.le < v.le).mean())
peer = df[(df.gdp > v.gdp * 0.7) & (df.gdp < v.gdp * 1.4)].sort_values("resid_gdp", ascending=False)
print("\nPEERS", len(peer))
print(peer[["name", "le", "health", "gdp", "resid_gdp"]].round(1).to_string())
peer[["name", "le", "health", "gdp", "resid_gdp"]].to_csv(OUT + "/peers_vietnam.csv", index=False)
print("peer median health", peer.health.median(), "VN health", v.health, "VN resid_both", v.resid_both)
mm = df.merge(df19[["Country Code", "resid_gdp"]], on="Country Code", suffixes=("", "_19"))
print("corr resid 19-23", mm.resid_gdp.corr(mm.resid_gdp_19))
print(df.groupby("IncomeGroup")[["le", "health", "gdp"]].median().round(1))
for g, s in df.groupby("IncomeGroup"):
    print(g, len(s), round(stats.spearmanr(s.health, s.le)[0], 2))
# nhóm: top/bottom theo region
print(top.head(10).Region.value_counts().to_dict(), top.tail(10).Region.value_counts().to_dict())

# ---- Biểu đồ 1
plt.rcParams.update({"font.size": 10})
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
a = ax[0]
a.scatter(df.health, df.le, s=14, c="#9aa5b1", alpha=.8); a.set_xscale("log")
a.scatter(v.health, v.le, s=90, c="#d62728", zorder=5)
a.annotate("Việt Nam", (v.health, v.le), xytext=(8, -14), textcoords="offset points", color="#d62728", fontweight="bold")
a.set_xlabel("Chi tiêu y tế bình quân đầu người (US$ hiện hành, thang log)"); a.set_ylabel("Tuổi thọ (năm)")
a.set_title("Chi tiêu y tế cao hơn đi cùng tuổi thọ cao hơn\n(Spearman = %.2f, n = %d, 2023)" % (s1, len(df)), loc="left")
b = ax[1]
b.scatter(df.gdp, df.le, s=14, c="#9aa5b1", alpha=.8); b.set_xscale("log")
xs = np.linspace(df.lg.min(), df.lg.max(), 100)
b.plot(np.exp(xs), m_g.params["const"] + m_g.params["lg"] * xs, c="#1f4e79", lw=2, label="Tuổi thọ kỳ vọng theo thu nhập")
for _, r in pd.concat([top.head(5), top.tail(5)]).iterrows():
    b.annotate(r["name"], (r.gdp, r.le), fontsize=7.5, xytext=(3, 3), textcoords="offset points")
b.scatter(v.gdp, v.le, s=90, c="#d62728", zorder=5)
b.annotate("Việt Nam", (v.gdp, v.le), xytext=(8, -16), textcoords="offset points", color="#d62728", fontweight="bold")
b.set_xlabel("GDP bình quân đầu người, PPP (US$ quốc tế hiện hành, thang log)"); b.set_ylabel("Tuổi thọ (năm)")
b.legend(loc="lower right", frameon=False)
b.set_title("Thu nhập giải thích phần lớn chênh lệch tuổi thọ", loc="left")
for x in ax:
    x.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(OUT + "/chart1_chi_tieu_thu_nhap_tuoi_tho.png", dpi=150); plt.close()

# ---- Biểu đồ 2
sel = pd.concat([top.head(10), top.tail(10), df[df["Country Code"] == "VNM"]]).drop_duplicates("Country Code").sort_values("resid_gdp")
fig, a = plt.subplots(figsize=(8, 8.5))
colors = ["#d62728" if c == "VNM" else ("#2a7f62" if x > 0 else "#c97b1a") for c, x in zip(sel["Country Code"], sel.resid_gdp)]
a.barh(sel.name, sel.resid_gdp, color=colors); a.axvline(0, c="k", lw=.8)
for i, x in enumerate(sel.resid_gdp):
    a.text(x + (.2 if x > 0 else -.2), i, "%+.1f" % x, va="center", ha="left" if x > 0 else "right", fontsize=8)
a.set_xlabel("Tuổi thọ thực tế trừ tuổi thọ kỳ vọng theo GDP/người PPP (năm)")
a.set_title("10 nước vượt / dưới kỳ vọng nhiều nhất và Việt Nam (hạng %d/%d), 2023" % (v.rank_resid_gdp, len(df)), loc="left", fontsize=10)
a.spines[["top", "right"]].set_visible(False)
a.set_xlim(sel.resid_gdp.min() - 3, sel.resid_gdp.max() + 3)
plt.tight_layout(); plt.savefig(OUT + "/chart2_vuot_duoi_ky_vong.png", dpi=150); plt.close()
