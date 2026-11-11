"""Tuổi thọ vs chi tiêu y tế bình quân đầu người, đã điều chỉnh theo thu nhập (GDP/người PPP).

Chạy: python outputs/tuoi-tho-chi-tieu-y-te/analysis.py   (từ thư mục workspace)
Đầu vào: data/ (World Bank WDI, chỉ đọc).
Đầu ra: CSV, PNG trong thư mục này.
"""
from pathlib import Path
import glob

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

LE_DIR, HE_DIR, GDP_DIR = "life_expectancy", "health_expenditure_per_capita", "gdp_per_capita_ppp"


def load_wide(folder):
    f = glob.glob(str(DATA / folder / "API_*.csv"))[0]
    d = pd.read_csv(f, skiprows=4)
    d.columns = [str(c) for c in d.columns]
    return d


def to_long(d, value_name):
    years = [c for c in d.columns if c.isdigit()]
    long = d.melt(id_vars=["Country Name", "Country Code"], value_vars=years,
                  var_name="year", value_name=value_name)
    long["year"] = long["year"].astype(int)
    return long


# ---- 1. Đọc dữ liệu & loại bỏ nhóm tổng hợp (aggregates) ----
meta = pd.read_csv(glob.glob(str(DATA / LE_DIR / "Metadata_Country_*.csv"))[0])
meta = meta[["Country Code", "Region", "IncomeGroup"]].dropna(subset=["Region"])  # nhóm tổng hợp không có Region
meta = meta[meta["Region"].astype(str).str.strip() != ""]

le = to_long(load_wide(LE_DIR), "life_exp")
he = to_long(load_wide(HE_DIR), "health_exp_pc")
gdp = to_long(load_wide(GDP_DIR), "gdp_pc_ppp")

panel = le.merge(he, on=["Country Code", "Country Name", "year"]).merge(
    gdp, on=["Country Code", "Country Name", "year"])
panel = panel[panel["Country Code"].isin(meta["Country Code"])].copy()
panel = panel.merge(meta, on="Country Code", how="left")
# Chuẩn hóa tên hiển thị (dữ liệu WB ghi "Naoero", "Viet Nam")
panel["Country Name"] = panel["Country Name"].replace({"Naoero": "Nauru", "Viet Nam": "Việt Nam"})

# ---- 2. Chọn năm phân tích: năm gần nhất có đủ 3 chỉ số cho ≥ 150 quốc gia ----
complete = panel.dropna(subset=["life_exp", "health_exp_pc", "gdp_pc_ppp"])
cov = complete.groupby("year")["Country Code"].nunique()
print("Số quốc gia đủ 3 chỉ số theo năm (2015–2024):")
print(cov.loc[2015:2024].to_string())
YEAR = int(cov[cov >= 150].index.max())
print(f"\n=> Năm phân tích chính: {YEAR}")
cov.loc[2000:2024].rename("n_countries_complete").to_csv(OUT / "coverage_by_year.csv")

df = complete[complete["year"] == YEAR].copy()
df["ln_he"] = np.log(df["health_exp_pc"])
df["ln_gdp"] = np.log(df["gdp_pc_ppp"])
df["ln_gdp2"] = df["ln_gdp"] ** 2
print(f"Số quốc gia trong mẫu {YEAR}: {len(df)}")
df.to_csv(OUT / "panel_year.csv", index=False)


def ols(y, X):
    """OLS bằng numpy; trả về hệ số, R², residual, fitted."""
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    fitted = X @ beta
    resid = y - fitted
    r2 = 1 - resid.var() / y.var()
    return beta, r2, resid, fitted


# ---- 3. Câu hỏi 1: chi tiêu nhiều hơn có tuổi thọ cao hơn không? (chưa điều chỉnh) ----
r_pearson_raw = stats.pearsonr(df["health_exp_pc"], df["life_exp"])
r_spearman_raw = stats.spearmanr(df["health_exp_pc"], df["life_exp"])
r_pearson_log = stats.pearsonr(df["ln_he"], df["life_exp"])
r_spearman_log = stats.spearmanr(df["health_exp_pc"], df["life_exp"])

# Quintile: chi tiêu theo nhóm 5 bậc
df["he_quintile"] = pd.qcut(df["health_exp_pc"], 5, labels=["Q1 thấp nhất", "Q2", "Q3", "Q4", "Q5 cao nhất"])
quint = df.groupby("he_quintile", observed=True).agg(
    n=("life_exp", "size"),
    chi_tieu_tb_usd=("health_exp_pc", "mean"),
    tuoi_tho_tb=("life_exp", "mean"),
    gdp_pc_tb=("gdp_pc_ppp", "mean"),
).reset_index()
quint.round(2).to_csv(OUT / "quintile_health_exp.csv", index=False)

# ---- 4. Câu hỏi 2: điều chỉnh theo thu nhập ----
# 4a. Mô hình chỉ có thu nhập (ln GDP + ln GDP²) -> "kỳ vọng theo thu nhập"
X_inc = np.column_stack([df["ln_gdp"], df["ln_gdp2"]])
b_inc, r2_inc, resid_inc, fit_inc = ols(df["life_exp"].values, X_inc)
df["expected_le_income"] = fit_inc
df["gap_vs_income"] = resid_inc  # + = vượt kỳ vọng, - = dưới kỳ vọng

# 4b. Mô hình thu nhập + chi tiêu: hệ số riêng của chi tiêu sau khi giữ thu nhập
X_both = np.column_stack([df["ln_gdp"], df["ln_gdp2"], df["ln_he"]])
b_both, r2_both, _, _ = ols(df["life_exp"].values, X_both)

# 4c. Mô hình chỉ có chi tiêu (ln HE) để so sánh
b_he_only, r2_he_only, _, _ = ols(df["life_exp"].values, df["ln_he"].values)

# Bootstrap CI cho hệ số ln_he trong mô hình 4b (1000 lần)
rng = np.random.default_rng(42)
boot = []
y_all = df["life_exp"].values
for _ in range(1000):
    idx = rng.integers(0, len(df), len(df))
    b, *_ = ols(y_all[idx], X_both[idx])
    boot.append(b[-1])
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])

# Kiểm định partial: tương quan giữa chi tiêu (đã bỏ thu nhập) và residual tuổi thọ
_, _, res_he_on_inc, _ = ols(df["ln_he"].values, X_inc)
partial_r = stats.pearsonr(res_he_on_inc, resid_inc)

# Tương quan chi tiêu với thu nhập (để giải thích vì sao phải điều chỉnh)
r_he_gdp = stats.pearsonr(df["ln_he"], df["ln_gdp"])

model_summary = pd.DataFrame([
    dict(mo_hinh="(1) Chỉ chi tiêu y tế (ln)", R2=r2_he_only, he_coef_ln=b_he_only[1], n=len(df)),
    dict(mo_hinh="(2) Chỉ thu nhập (ln GDP, ln GDP²)", R2=r2_inc, he_coef_ln=np.nan, n=len(df)),
    dict(mo_hinh="(3) Thu nhập + chi tiêu (ln)", R2=r2_both, he_coef_ln=b_both[-1], n=len(df)),
])
model_summary["ci95_he_low"] = [np.nan, np.nan, ci_lo]
model_summary["ci95_he_high"] = [np.nan, np.nan, ci_hi]
model_summary.round(4).to_csv(OUT / "model_summary.csv", index=False)

corr_summary = pd.DataFrame([
    dict(thong_ke="Pearson r: chi tiêu (USD) vs tuổi thọ", value=r_pearson_raw[0], p=r_pearson_raw[1]),
    dict(thong_ke="Spearman rho: chi tiêu (USD) vs tuổi thọ", value=r_spearman_raw[0], p=r_spearman_raw[1]),
    dict(thong_ke="Pearson r: ln chi tiêu vs tuổi thọ", value=r_pearson_log[0], p=r_pearson_log[1]),
    dict(thong_ke="Pearson r: ln chi tiêu vs ln GDP (đa cộng tuyến)", value=r_he_gdp[0], p=r_he_gdp[1]),
    dict(thong_ke="Partial r: chi tiêu vs tuổi thọ | thu nhập", value=partial_r[0], p=partial_r[1]),
])
corr_summary.to_csv(OUT / "correlations.csv", index=False)

# ---- 5. Bảng xếp hạng vượt / dưới kỳ vọng ----
df["gap_rank_desc"] = df["gap_vs_income"].rank(ascending=False, method="first")
cols = ["Country Name", "Country Code", "Region", "IncomeGroup", "life_exp", "expected_le_income",
        "gap_vs_income", "health_exp_pc", "gdp_pc_ppp"]
ranked = df[cols].sort_values("gap_vs_income", ascending=False)
ranked.round(2).to_csv(OUT / "gap_all_countries.csv", index=False)
top_over = ranked.head(15).round(2)
top_under = ranked.tail(15).sort_values("gap_vs_income").round(2)
top_over.to_csv(OUT / "top15_vuot_ky_vong.csv", index=False)
top_under.to_csv(OUT / "top15_duoi_ky_vong.csv", index=False)

# Việt Nam
vn = ranked[ranked["Country Code"] == "VNM"].copy()
vn_rank = int(ranked.reset_index(drop=True).index[ranked.reset_index(drop=True)["Country Code"] == "VNM"][0]) + 1
n_total = len(ranked)
vn_row = vn.iloc[0]
# So sánh với các nước cùng nhóm thu nhập và nước láng giềng ASEAN
asean = ["THA", "MYS", "IDN", "PHL", "KHM", "LAO", "MMR", "SGP"]
peers = ranked[ranked["Country Code"].isin(asean + ["VNM"])].sort_values("gap_vs_income", ascending=False)
peers.round(2).to_csv(OUT / "vietnam_asean_peers.csv", index=False)

# Phân bố gap theo nhóm thu nhập
by_inc = df.groupby("IncomeGroup").agg(
    n=("gap_vs_income", "size"),
    gap_tb=("gap_vs_income", "mean"),
    le_tb=("life_exp", "mean"),
    he_tb=("health_exp_pc", "mean"),
).round(2)
by_inc.to_csv(OUT / "gap_by_income_group.csv")

# Độ nhạy: đổi năm (năm trước) để kiểm tra kết quả có ổn định không
sens_rows = []
for yr in sorted({YEAR - 2, YEAR - 1, YEAR}):
    s = complete[complete["year"] == yr].copy()
    if len(s) < 100:
        continue
    s["ln_he"] = np.log(s["health_exp_pc"])
    s["ln_gdp"] = np.log(s["gdp_pc_ppp"])
    s["ln_gdp2"] = s["ln_gdp"] ** 2
    b_i, _, r_i, _ = ols(s["life_exp"].values, np.column_stack([s["ln_gdp"], s["ln_gdp2"]]))
    b_b, r2_b, _, _ = ols(s["life_exp"].values, np.column_stack([s["ln_gdp"], s["ln_gdp2"], s["ln_he"]]))
    s["gap"] = r_i
    vn_s = s[s["Country Code"] == "VNM"]
    sens_rows.append(dict(
        year=yr, n=len(s),
        spearman_he_le=stats.spearmanr(s["health_exp_pc"], s["life_exp"])[0],
        he_coef_ln_adj=b_b[-1], r2_adj=r2_b,
        vn_gap=float(vn_s["gap"].iloc[0]) if len(vn_s) else np.nan,
        vn_gap_rank=int((s["gap"] > float(vn_s["gap"].iloc[0])).sum() + 1) if len(vn_s) else np.nan,
    ))
sens = pd.DataFrame(sens_rows)
sens.round(3).to_csv(OUT / "sensitivity_years.csv", index=False)

# ---- 6. Các số liệu tóm tắt in ra để kiểm chứng ----
print("\n=== TƯƠNG QUAN (chưa điều chỉnh) ===")
print(corr_summary.round(3).to_string(index=False))
print("\n=== MÔ HÌNH ===")
print(model_summary.round(3).to_string(index=False))
print("\n=== CHI TIÊU THEO QUINTILE ===")
print(quint.round(2).to_string(index=False))
print("\n=== TOP 15 VƯỢT KỲ VỌNG (theo thu nhập) ===")
print(top_over[["Country Name", "IncomeGroup", "life_exp", "expected_le_income", "gap_vs_income", "health_exp_pc"]].to_string(index=False))
print("\n=== TOP 15 DƯỚI KỲ VỌNG ===")
print(top_under[["Country Name", "IncomeGroup", "life_exp", "expected_le_income", "gap_vs_income", "health_exp_pc"]].to_string(index=False))
print(f"\n=== VIỆT NAM === hạng {vn_rank}/{n_total}")
print(vn_row[["life_exp", "expected_le_income", "gap_vs_income", "health_exp_pc", "gdp_pc_ppp", "IncomeGroup"]].to_string())
print("\n=== ASEAN peers ===")
print(peers[["Country Name", "life_exp", "expected_le_income", "gap_vs_income", "health_exp_pc", "gdp_pc_ppp"]].round(2).to_string(index=False))
print("\n=== GAP THEO NHÓM THU NHẬP ===")
print(by_inc.to_string())
print("\n=== ĐỘ NHẠY THEO NĂM ===")
print(sens.round(3).to_string(index=False))

# ---- 7. Biểu đồ ----
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
inc_order = ["Low income", "Lower middle income", "Upper middle income", "High income"]
inc_label = {"Low income": "Thu nhập thấp", "Lower middle income": "Trung bình thấp",
             "Upper middle income": "Trung bình cao", "High income": "Thu nhập cao"}
colors = {"Low income": "#9ecae1", "Lower middle income": "#4292c6",
          "Upper middle income": "#2171b5", "High income": "#08306b"}

# Chart 1: scatter tuổi thọ vs chi tiêu (log), màu theo nhóm thu nhập
fig, ax = plt.subplots(figsize=(9, 6))
for g in inc_order:
    s = df[df["IncomeGroup"] == g]
    ax.scatter(s["health_exp_pc"], s["life_exp"], s=28, alpha=0.8, color=colors[g], label=inc_label[g], edgecolor="none")
vn_pt = df[df["Country Code"] == "VNM"]
ax.scatter(vn_pt["health_exp_pc"], vn_pt["life_exp"], s=120, color="#e6550d", edgecolor="black", zorder=5, label="Việt Nam")
ax.annotate("Việt Nam", (float(vn_pt["health_exp_pc"].iloc[0]), float(vn_pt["life_exp"].iloc[0])),
            xytext=(10, -12), textcoords="offset points", fontsize=10, color="#e6550d", weight="bold")
ax.set_xscale("log")
ax.set_xticks([25, 100, 500, 2000, 8000])
ax.set_xticklabels(["25", "100", "500", "2.000", "8.000"])
ax.set_xlabel("Chi tiêu y tế bình quân đầu người (USD hiện hành, thang log)")
ax.set_ylabel("Tuổi thọ trung bình (năm)")
ax.set_title(f"Chi tiêu y tế nhiều hơn đi kèm tuổi thọ cao hơn, nhưng thu nhập là yếu tố chính ({YEAR})")
ax.legend(frameon=False, loc="lower right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "chart1_scatter_chi_tieu_tuoi_tho.png", dpi=150)
plt.close(fig)

# Chart 2: đường kỳ vọng theo thu nhập + điểm quốc gia
fig, ax = plt.subplots(figsize=(9, 6))
for g in inc_order:
    s = df[df["IncomeGroup"] == g]
    ax.scatter(s["gdp_pc_ppp"], s["life_exp"], s=28, alpha=0.8, color=colors[g], label=inc_label[g], edgecolor="none")
xs = np.linspace(df["gdp_pc_ppp"].min(), df["gdp_pc_ppp"].max(), 300)
lx = np.log(xs)
ys = b_inc[0] + b_inc[1] * lx + b_inc[2] * lx ** 2
order = np.argsort(xs)
ax.plot(xs[order], ys[order], color="black", lw=2, label="Kỳ vọng theo thu nhập")
ax.scatter(vn_pt["gdp_pc_ppp"], vn_pt["life_exp"], s=120, color="#e6550d", edgecolor="black", zorder=5)
ax.annotate("Việt Nam", (float(vn_pt["gdp_pc_ppp"].iloc[0]), float(vn_pt["life_exp"].iloc[0])),
            xytext=(10, -12), textcoords="offset points", fontsize=10, color="#e6550d", weight="bold")
ax.set_xscale("log")
ax.set_xlabel("GDP bình quân đầu người theo PPP (USD quốc tế hiện hành, thang log)")
ax.set_ylabel("Tuổi thọ trung bình (năm)")
ax.set_title(f"Sau khi tính thu nhập, tuổi thọ vẫn chênh nhau đáng kể quanh đường kỳ vọng ({YEAR})")
ax.legend(frameon=False, loc="lower right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "chart2_ky_vong_theo_thu_nhap.png", dpi=150)
plt.close(fig)

# Chart 3: top 10 vượt / dưới kỳ vọng
t = pd.concat([top_over.head(10).assign(nhom="Vượt kỳ vọng"),
               top_under.head(10).assign(nhom="Dưới kỳ vọng")])
t = t.sort_values("gap_vs_income")
fig, ax = plt.subplots(figsize=(9, 7))
bar_colors = ["#d95f02" if v < 0 else "#1b7837" for v in t["gap_vs_income"]]
ax.barh(t["Country Name"], t["gap_vs_income"], color=bar_colors)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Chênh lệch tuổi thọ so với kỳ vọng theo thu nhập (năm)")
ax.set_title(f"10 quốc gia vượt và 10 quốc gia dưới kỳ vọng nhất theo thu nhập ({YEAR})")
for y, v in enumerate(t["gap_vs_income"]):
    ax.text(v + (0.2 if v >= 0 else -0.2), y, f"{v:+.1f}", va="center",
            ha="left" if v >= 0 else "right", fontsize=8)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "chart3_top10_vuot_duoi_ky_vong.png", dpi=150)
plt.close(fig)

# Chart 4: Việt Nam so với ASEAN
pe = peers.sort_values("gap_vs_income")
fig, ax = plt.subplots(figsize=(8, 5))
cc = ["#e6550d" if c == "VNM" else "#7f7f7f" for c in pe["Country Code"]]
ax.barh(pe["Country Name"], pe["gap_vs_income"], color=cc)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Chênh lệch tuổi thọ so với kỳ vọng theo thu nhập (năm)")
ax.set_title(f"Việt Nam so với các nước ASEAN có dữ liệu ({YEAR})")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "chart4_viet_nam_asean.png", dpi=150)
plt.close(fig)

# Chart 5: quintile chi tiêu
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(quint["he_quintile"].astype(str), quint["tuoi_tho_tb"], color="#2171b5")
for i, v in enumerate(quint["tuoi_tho_tb"]):
    ax.text(i, v + 0.3, f"{v:.1f}", ha="center", fontsize=9)
ax.set_ylabel("Tuổi thọ trung bình (năm)")
ax.set_xlabel("Nhóm chi tiêu y tế bình quân đầu người (ngũ phân vị)")
ax.set_title(f"Tuổi thọ tăng theo nhóm chi tiêu y tế ({YEAR})")
ax.set_ylim(0, quint["tuoi_tho_tb"].max() + 5)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "chart5_quintile_chi_tieu.png", dpi=150)
plt.close(fig)

print("\nDone. Outputs in", OUT)
