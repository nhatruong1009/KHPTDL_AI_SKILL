import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "..", "data")
OUT = BASE

red = pd.read_csv(os.path.join(DATA, "winequality-red.csv"), sep=";")
white = pd.read_csv(os.path.join(DATA, "winequality-white.csv"), sep=";")
red["type"] = "Đỏ"
white["type"] = "Trắng"
df = pd.concat([red, white], ignore_index=True)
feat_cols = [c for c in df.columns if c != "type"]
df_dedup = df.drop_duplicates(subset=feat_cols + ["type"]).copy()


def mean_ci(x):
    x = np.asarray(x, float)
    m = x.mean()
    se = x.std(ddof=1) / np.sqrt(len(x))
    h = stats.t.ppf(0.975, len(x) - 1) * se
    return m, m - h, m + h


PALETTE = {"Đỏ": "#8B0000", "Trắng": "#D4AF37"}
lines = []


def log(s=""):
    print(s)
    lines.append(s)


for label, d in [("TOÀN BỘ (có trùng lặp)", df), ("SAU KHI LOẠI TRÙNG LẶP", df_dedup)]:
    log(f"\n=== {label} ===")
    log("Số dòng: " + ", ".join(f"{t}={n}" for t, n in d["type"].value_counts().items()))
    rows = []
    for t, g in d.groupby("type"):
        m, lo, hi = mean_ci(g["quality"])
        rows.append({
            "loại": t, "n": len(g), "điểm TB": round(m, 3),
            "CI 95% thấp": round(lo, 3), "CI 95% cao": round(hi, 3),
            "trung vị": g["quality"].median(),
            "tỉ lệ quality>=7 (%)": round((g["quality"] >= 7).mean() * 100, 1),
        })
    log(pd.DataFrame(rows).to_string(index=False))
    w = d.loc[d.type == "Trắng", "quality"]
    r = d.loc[d.type == "Đỏ", "quality"]
    _, p_mw = stats.mannwhitneyu(w, r, alternative="two-sided")
    _, p_t = stats.ttest_ind(w, r, equal_var=False)
    log(f"Chênh lệch điểm TB (Trắng - Đỏ) = {w.mean() - r.mean():.3f}; "
        f"Mann-Whitney p = {p_mw:.2e}; Welch t p = {p_t:.2e}")
    ct = pd.crosstab(d["type"], d["quality"] >= 7)
    _, p_c, _, _ = stats.chi2_contingency(ct)
    log(f"Tỉ lệ quality>=7 theo loại: chi2 p = {p_c:.2e}")

log("\n=== Phân bố điểm chất lượng (sau khi loại trùng lặp) ===")
dist = pd.crosstab(df_dedup["quality"], df_dedup["type"])
log(dist.to_string())

log("\n=== Độ cồn (alcohol) và điểm chất lượng, theo loại (sau khi loại trùng lặp) ===")
for t, g in df_dedup.groupby("type"):
    rho, p_rho = stats.spearmanr(g["alcohol"], g["quality"])
    log(f"{t}: Spearman rho(alcohol, quality) = {rho:.3f}, p = {p_rho:.2e}, n = {len(g)}")

df_dedup["nhom_con"] = pd.qcut(df_dedup["alcohol"], 4, labels=["Q1 thấp", "Q2", "Q3", "Q4 cao"])
tab_alc = (df_dedup.groupby(["type", "nhom_con"], observed=True)["quality"]
           .agg(n="size", diem_tb="mean", ti_le_q7_pct=lambda x: (x >= 7).mean() * 100)
           .round(2).reset_index())
log(tab_alc.to_string(index=False))

tab_alc.to_csv(os.path.join(OUT, "alcohol_quartile_quality.csv"), index=False)
dist.to_csv(os.path.join(OUT, "quality_distribution_dedup.csv"))

# Chart 1: phân bố điểm theo loại
fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(data=df_dedup, x="quality", hue="type", hue_order=["Đỏ", "Trắng"], palette=PALETTE, ax=ax)
ax.set_title("Vang trắng được chấm điểm TB cao hơn vang đỏ (5,86 so với 5,62 trên thang 0–10)")
ax.set_xlabel("Điểm chất lượng (0–10)")
ax.set_ylabel("Số mẫu (đã loại trùng lặp)")
ax.legend(title="Loại vang")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "phan_bo_diem_theo_loai.png"), dpi=150)
plt.close(fig)

# Chart 2: tỉ lệ điểm >=7 theo nhóm cồn
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=tab_alc, x="nhom_con", y="ti_le_q7_pct", hue="type",
            hue_order=["Đỏ", "Trắng"], palette=PALETTE, ax=ax)
ax.set_title("Vang có độ cồn cao hơn đạt điểm 7+ thường xuyên hơn ở cả hai loại")
ax.set_xlabel("Nhóm độ cồn (quartile)")
ax.set_ylabel("Tỉ lệ điểm chất lượng ≥ 7 (%)")
ax.legend(title="Loại vang")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "ti_le_diem7_theo_con.png"), dpi=150)
plt.close(fig)

with open(os.path.join(OUT, "analysis_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
