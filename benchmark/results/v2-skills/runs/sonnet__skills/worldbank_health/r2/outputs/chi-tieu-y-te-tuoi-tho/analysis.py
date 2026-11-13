import pandas as pd, numpy as np, glob, os
from scipy import stats

class _M:
    def __init__(s, y, X, names):
        b, *_ = np.linalg.lstsq(X, y.values, rcond=None); s.params = pd.Series(b, index=names)
        s.resid = pd.Series(y.values - X @ b, index=y.index); n, k = X.shape
        s.rsquared = 1 - (s.resid ** 2).sum() / ((y - y.mean()) ** 2).sum()
        se = np.sqrt(np.diag((s.resid ** 2).sum() / (n - k) * np.linalg.inv(X.T @ X)))
        s.pvalues = pd.Series(2 * stats.t.sf(np.abs(b / se), n - k), index=names)

class sm:  # OLS tối giản (không có statsmodels trong môi trường)
    @staticmethod
    def add_constant(X):
        X = X.copy(); X.insert(0, "const", 1.0); return X
    @staticmethod
    def OLS(y, X):
        class _F:
            def fit(self_): return _M(y, X.values, list(X.columns))
        return _F()
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid")
out = os.path.join("outputs", "chi-tieu-y-te-tuoi-tho")
YEARS = (2019, 2020, 2021, 2022, 2023)

def load(d, name):
    f = glob.glob("data/%s/API*.csv" % d)[0]
    df = pd.read_csv(f, skiprows=4)
    df = df.set_index("Country Code")[["Country Name"] + [str(y) for y in YEARS]]
    return df.rename(columns=lambda c: name + "_" + c if c.isdigit() else c)

le = load("life_expectancy", "le"); he = load("health_expenditure_per_capita", "he"); gd = load("gdp_per_capita_ppp", "gdp")
meta = pd.read_csv(glob.glob("data/life_expectancy/Metadata_Country*.csv")[0]).set_index("Country Code")

def build(y):
    d = pd.DataFrame({"country": le["Country Name"], "life": le["le_%d" % y], "he": he["he_%d" % y], "gdp": gd["gdp_%d" % y]})
    d = d.join(meta[["Region", "IncomeGroup"]])
    n0 = len(d); d = d[d.Region.notna()]  # bỏ nhóm tổng hợp (không có Region)
    n1 = len(d); d = d.dropna(subset=["life", "he", "gdp"])
    d["lhe"] = np.log(d.he); d["lgdp"] = np.log(d.gdp)
    print(y, "tong dong", n0, "quoc gia/vung", n1, "du 3 chi so", len(d))
    return d

def fit(d, cols):
    return sm.OLS(d["life"], sm.add_constant(d[cols])).fit()

res = {}
for y in (2023, 2022):
    d = build(y)
    r = stats.spearmanr(d.he, d["life"]); rp = stats.pearsonr(d.lhe, d["life"])
    mA = fit(d, ["lgdp"]); mB = fit(d, ["lgdp", "lhe"]); m0 = fit(d, ["lhe"])
    d["res_A"] = mA.resid; d["res_B"] = mB.resid
    rl = mA.resid
    rh = sm.OLS(d.lhe, sm.add_constant(d[["lgdp"]])).fit().resid
    pc = stats.pearsonr(rh, rl)
    grp = {g: stats.spearmanr(x.he, x["life"])[0] for g, x in d.groupby("IncomeGroup")}
    summ = dict(year=y, n=len(d), spearman_he_le=r[0], pearson_lhe_le=rp[0], r2_he=m0.rsquared, r2_gdp=mA.rsquared, r2_both=mB.rsquared,
                beta_lhe_alone=m0.params["lhe"], beta_lgdp=mA.params["lgdp"], beta_lhe_ctrl=mB.params["lhe"], p_lhe_ctrl=mB.pvalues["lhe"],
                partial_r=pc[0], partial_p=pc[1], resid_sd_A=mA.resid.std())
    summ.update({"sp_" + k: v for k, v in grp.items()})
    res[y] = (d, summ)
    pd.DataFrame([summ]).T.to_csv("%s/tom_tat_mo_hinh_%d.csv" % (out, y), header=["value"])

d, s = res[2023]
print(pd.DataFrame([res[2023][1], res[2022][1]]).T.to_string())
d["rank_A"] = d.res_A.rank(ascending=False).astype(int)
d["rank_B"] = d.res_B.rank(ascending=False).astype(int)
d["res_A_2022"] = res[2022][0].res_A.reindex(d.index)
cols = ["country", "IncomeGroup", "Region", "life", "he", "gdp", "res_A", "rank_A", "res_B", "rank_B", "res_A_2022"]
d.sort_values("res_A", ascending=False)[cols].to_csv(out + "/phan_du_theo_quoc_gia_2023.csv")
print("TOP vuot"); print(d.sort_values("res_A", ascending=False)[cols].head(12).round(2).to_string())
print("TOP duoi"); print(d.sort_values("res_A")[cols].head(12).round(2).to_string())
print("VNM"); print(d.loc[["VNM"]][cols].round(2).T)
v = d.loc["VNM"]
print("n", len(d), "VNM rank_A", v.rank_A, "z", v.res_A / s["resid_sd_A"])
print("VNM 2022 res", res[2022][0].loc["VNM", ["res_A", "res_B"]].tolist())
peer = d[(d.gdp.between(v.gdp * .75, v.gdp * 1.25)) & (d.index != "VNM")]
print("peers", len(peer), "median le", peer["life"].median(), "median he", peer.he.median(), "VNM he", v.he, "le", v["life"])
pc_ = peer.sort_values("life", ascending=False)[["country", "life", "he", "gdp", "res_A"]].round(1)
pc_.to_csv(out + "/nhom_tuong_dong_vn.csv"); print(pc_.to_string())
print("spearman res A 23 vs 22", stats.spearmanr(d.res_A, d.res_A_2022, nan_policy="omit")[0], "A vs B", stats.spearmanr(d.res_A, d.res_B)[0])
d22 = d.dropna(subset=["res_A_2022"])
for k in (15,):
    print("top15 A&B", len(set(d.nlargest(k, "res_A").index) & set(d.nlargest(k, "res_B").index)),
          "A&2022", len(set(d.nlargest(k, "res_A").index) & set(d22.nlargest(k, "res_A_2022").index)),
          "bot A&B", len(set(d.nsmallest(k, "res_A").index) & set(d.nsmallest(k, "res_B").index)),
          "A&2022", len(set(d.nsmallest(k, "res_A").index) & set(d22.nsmallest(k, "res_A_2022").index)))
print(d.groupby("IncomeGroup").agg(n=("life", "size"), le=("life", "median"), he=("he", "median")).round(1))
rng = np.random.default_rng(0); bs = []
for _ in range(1000):
    b = d.sample(len(d), replace=True, random_state=int(rng.integers(1e9)))
    m = sm.OLS(b["life"], sm.add_constant(b[["lgdp"]])).fit()
    bs.append(v["life"] - (m.params["const"] + m.params["lgdp"] * v.lgdp))
print("VN resid CI", np.percentile(bs, [2.5, 97.5]))
# quadratic check
dq = d.copy(); dq["lgdp2"] = dq.lgdp ** 2
print("R2 linear", fit(d, ["lgdp"]).rsquared, "quad", fit(dq, ["lgdp", "lgdp2"]).rsquared)
print("VN res B", v.res_B, "rank B", v.rank_B)

# ---------- biểu đồ
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(d.he, d["life"], s=22, c="#bbbbbb", alpha=.8)
m0 = fit(d, ["lhe"]); xs = np.linspace(d.lhe.min(), d.lhe.max(), 100)
ax.plot(np.exp(xs), m0.params["const"] + m0.params["lhe"] * xs, c="#444", lw=1.5)
ax.scatter(v.he, v["life"], s=90, c="#d62728", zorder=5)
ax.annotate("Việt Nam", (v.he, v["life"]), xytext=(8, -14), textcoords="offset points", color="#d62728", fontweight="bold")
ax.set_xscale("log"); ax.set_xlabel("Chi tiêu y tế bình quân đầu người, 2023 (US$ hiện hành, thang log)"); ax.set_ylabel("Tuổi thọ khi sinh, 2023 (năm)")
ax.set_title("Nước chi tiêu y tế cao hơn có tuổi thọ cao hơn (Spearman = %.2f)" % s["spearman_he_le"], fontsize=11, loc="left")
fig.text(.01, -.01, "Nguồn: World Bank WDI (WHO GHED, UN WPP); n = %d quốc gia/vùng lãnh thổ." % len(d), fontsize=8)
fig.savefig(out + "/01_chi_tieu_vs_tuoi_tho.png", dpi=150, bbox_inches="tight"); plt.close()

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(d.gdp, d["life"], s=22, c="#bbbbbb", alpha=.8)
mA = fit(d, ["lgdp"]); xs = np.linspace(d.lgdp.min(), d.lgdp.max(), 100)
ax.plot(np.exp(xs), mA.params["const"] + mA.params["lgdp"] * xs, c="#444")
top = d.nlargest(6, "res_A"); bot = d.nsmallest(6, "res_A")
ax.scatter(top.gdp, top["life"], c="#1f77b4", s=45); ax.scatter(bot.gdp, bot["life"], c="#ff7f0e", s=45)
ax.scatter(v.gdp, v["life"], c="#d62728", s=90, zorder=5)
for n_, r in pd.concat([top, bot, d.loc[["VNM"]]]).iterrows():
    ax.annotate(r.country if n_ != "VNM" else "Việt Nam", (r.gdp, r["life"]), xytext=(4, 4), textcoords="offset points", fontsize=8, color="#d62728" if n_ == "VNM" else "k")
ax.set_xscale("log"); ax.set_xlabel("GDP bình quân đầu người PPP, 2023 (int-$ hiện hành, thang log)"); ax.set_ylabel("Tuổi thọ khi sinh (năm)")
ax.set_title("Việt Nam sống thọ hơn mức kỳ vọng theo thu nhập khoảng %.1f năm" % v.res_A, fontsize=12, loc="left")
fig.text(.01, -.01, "Xanh: 6 nước vượt kỳ vọng nhất; cam: 6 nước dưới kỳ vọng nhất (hồi quy tuổi thọ ~ ln GDP PPP).", fontsize=8)
fig.savefig(out + "/02_phan_du_theo_thu_nhap.png", dpi=150, bbox_inches="tight"); plt.close()

t = pd.concat([d.nlargest(10, "res_A"), d.nsmallest(10, "res_A")])
if "VNM" not in t.index: t = pd.concat([t, d.loc[["VNM"]]])
t = t.sort_values("res_A")
fig, ax = plt.subplots(figsize=(9, 8))
cl = ["#d62728" if i == "VNM" else ("#1f77b4" if r > 0 else "#ff7f0e") for i, r in zip(t.index, t.res_A)]
ax.barh([c if i != "VNM" else "Việt Nam" for i, c in zip(t.index, t.country)], t.res_A, color=cl)
for y_, r in enumerate(t.res_A):
    ax.text(r + (.15 if r > 0 else -.15), y_, "%+.1f" % r, va="center", ha="left" if r > 0 else "right", fontsize=8)
ax.axvline(0, c="k", lw=.8); ax.set_xlabel("Chênh lệch tuổi thọ so với kỳ vọng theo GDP PPP (năm)")
ax.set_title("Nước vượt và dưới kỳ vọng tuổi thọ nhiều nhất, sau khi tính đến thu nhập", fontsize=11, loc="left")
fig.text(.01, .0, "Phần dư của hồi quy tuổi thọ ~ ln(GDP PPP), 2023.", fontsize=8)
fig.savefig(out + "/03_vuot_duoi_ky_vong.png", dpi=150, bbox_inches="tight"); plt.close()
