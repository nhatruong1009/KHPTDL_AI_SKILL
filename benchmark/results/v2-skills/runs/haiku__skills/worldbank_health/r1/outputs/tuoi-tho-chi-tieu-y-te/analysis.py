"""
Câu hỏi: Các quốc gia chi tiêu y tế nhiều hơn có tuổi thọ cao hơn không?
Sau khi tính đến mức thu nhập (GDP/người PPP), quốc gia nào 'vượt kỳ vọng' / 'dưới kỳ vọng'
nhiều nhất, và Việt Nam đứng ở đâu?

Dữ liệu: World Bank WDI (đọc từ thư mục data/, chỉ đọc).
Năm chính: 2019 (trước đại dịch COVID-19). Kiểm tra độ nhạy: 2022.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = "/root/.cache/skill-bench/runs/v2-skills/haiku__skills/worldbank_health/r1/workspace"
DATA = os.path.join(PROJECT, "data")
OUT = os.path.join(PROJECT, "outputs", "tuoi-tho-chi-tieu-y-te")
os.makedirs(OUT, exist_ok=True)

F_LE = os.path.join(DATA, "life_expectancy", "API_SP.DYN.LE00.IN_DS2_en_csv_v2_70864.csv")
F_HX = os.path.join(DATA, "health_expenditure_per_capita", "API_SH.XPD.CHEX.PC.CD_DS2_en_csv_v2_57.csv")
F_GDP = os.path.join(DATA, "gdp_per_capita_ppp", "API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_60730.csv")
F_META = os.path.join(DATA, "life_expectancy", "Metadata_Country_API_SP.DYN.LE00.IN_DS2_en_csv_v2_70864.csv")

VN_CODE = "VNM"


def load_wb(path, year):
    """year: một năm (int) hoặc danh sách năm -> trung bình các năm có dữ liệu (ít nhất 2 năm)."""
    df = pd.read_csv(path, skiprows=4, encoding="utf-8-sig")
    years = [year] if isinstance(year, int) else list(year)
    cols = [str(y) for y in years]
    if len(cols) == 1:
        df = df[["Country Name", "Country Code", cols[0]]].rename(columns={cols[0]: "value"})
    else:
        sub = df[["Country Name", "Country Code"] + cols].copy()
        sub["value"] = sub[cols].mean(axis=1, skipna=True).where(sub[cols].notna().sum(axis=1) >= 2)
        df = sub[["Country Name", "Country Code", "value"]]
    return df


def build(year):
    le = load_wb(F_LE, year).rename(columns={"value": "life_exp"})
    hx = load_wb(F_HX, year).rename(columns={"value": "health_exp_pc"})
    gdp = load_wb(F_GDP, year).rename(columns={"value": "gdp_pc_ppp"})
    meta = pd.read_csv(F_META, encoding="utf-8-sig")[["Country Code", "Region", "IncomeGroup"]]

    m = le.merge(hx, on=["Country Name", "Country Code"], how="inner")
    m = m.merge(gdp, on=["Country Name", "Country Code"], how="inner")
    m = m.merge(meta, on="Country Code", how="left")
    # Loại các tổng hợp khu vực/nhóm thu nhập (không có Region trong metadata quốc gia)
    m = m[m["Region"].notna()].copy()
    m = m.dropna(subset=["life_exp", "health_exp_pc", "gdp_pc_ppp"]).copy()
    m = m[(m.health_exp_pc > 0) & (m.gdp_pc_ppp > 0)].copy()
    m["log_hx"] = np.log(m["health_exp_pc"])
    m["log_gdp"] = np.log(m["gdp_pc_ppp"])
    m["year"] = str(year)
    return m


def ols(X, y):
    """OLS với hệ số, SE, p-value, R^2."""
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    sigma2 = resid @ resid / (n - k)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * (1 - stats.t.cdf(np.abs(t), df=n - k))
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, p, r2, resid


def analyse(year, tag, save=True):
    m = build(year)
    n = len(m)
    res = {"year": year, "n_countries": n}

    # 1. Tương quan thô
    r_p, p_p = stats.pearsonr(m.log_hx, m.life_exp)
    r_s, p_s = stats.spearmanr(m.health_exp_pc, m.life_exp)
    res.update(raw_pearson_logHX_LE=r_p, raw_pearson_p=p_p,
               raw_spearman_HX_LE=r_s, raw_spearman_p=p_s)

    # 2. Tương quan thô với GDP (để biết thu nhập đóng vai trò lớn cỡ nào)
    r_g, _ = stats.pearsonr(m.log_gdp, m.life_exp)
    r_hg, _ = stats.pearsonr(m.log_hx, m.log_gdp)
    res.update(raw_pearson_logGDP_LE=r_g, pearson_logHX_logGDP=r_hg)

    # 3. Mô hình chỉ có thu nhập: LE ~ logGDP + logGDP^2 (quan hệ cong)
    X_inc = np.column_stack([m.log_gdp, m.log_gdp ** 2])
    b_inc, se_inc, p_inc, r2_inc, resid_inc = ols(X_inc, m.life_exp.values)
    res.update(r2_income_only=r2_inc)

    # 4. Mô hình có cả chi tiêu y tế sau khi kiểm soát thu nhập
    X_full = np.column_stack([m.log_hx, m.log_gdp, m.log_gdp ** 2])
    b_f, se_f, p_f, r2_f, resid_f = ols(X_full, m.life_exp.values)
    res.update(
        r2_full=r2_f,
        coef_logHX_adj=b_f[1], se_logHX_adj=se_f[1], p_logHX_adj=p_f[1],
        delta_r2_from_HX=r2_f - r2_inc,
    )
    # Ước lượng: +1 năm tuổi thọ tương ứng với bao nhiêu % chi tiêu y tế (theo log)
    res["pct_HX_increase_per_1yr_LE_adj"] = (np.exp(1.0 / b_f[1]) - 1) * 100 if b_f[1] != 0 else np.nan

    # Partial correlation: phần dư LE (sau thu nhập) vs phần dư logHX (sau thu nhập)
    hx_on_inc = ols(X_inc, m.log_hx.values)[4]
    r_partial, p_partial = stats.pearsonr(resid_inc, hx_on_inc)
    res.update(partial_r_HX_LE_given_income=r_partial, partial_p=p_partial)

    # 5. Kỳ vọng theo thu nhập (mô hình chỉ có thu nhập) -> chênh lệch thực tế - kỳ vọng
    m = m.assign(expected_le=m.life_exp - resid_inc, gap_years=resid_inc)
    m["rank_over"] = m["gap_years"].rank(ascending=False, method="min").astype(int)
    m = m.sort_values("gap_years", ascending=False).reset_index(drop=True)

    vn = m[m["Country Code"] == VN_CODE]
    if len(vn):
        r = vn.iloc[0]
        res.update(vn_life_exp=r.life_exp, vn_expected=r.expected_le, vn_gap=r.gap_years,
                   vn_rank=int(r.rank_over), vn_health_exp_pc=r.health_exp_pc,
                   vn_gdp_pc_ppp=r.gdp_pc_ppp, vn_income_group=r.IncomeGroup)
    else:
        res.update(vn_gap=np.nan)

    if save:
        cols = ["Country Name", "Country Code", "Region", "IncomeGroup", "gdp_pc_ppp",
                "health_exp_pc", "life_exp", "expected_le", "gap_years", "rank_over"]
        m[cols].to_csv(os.path.join(OUT, f"ranking_{tag}.csv"), index=False)
        pd.Series(res).to_csv(os.path.join(OUT, f"summary_{tag}.csv"), header=["value"])
    return m, res, (b_inc, b_f)


def charts(m, res, tag="2019"):
    # Chart 1: LE vs chi tiêu y tế (log), màu theo nhóm thu nhập
    fig, ax = plt.subplots(figsize=(9, 6))
    groups = m["IncomeGroup"].fillna("Khác")
    colors = {"High income": "#1f77b4", "Upper middle income": "#2ca02c",
              "Lower middle income": "#ff7f0e", "Low income": "#d62728"}
    for g, sub in m.groupby(groups):
        ax.scatter(sub.health_exp_pc, sub.life_exp, s=28, alpha=0.7,
                   color=colors.get(g, "grey"), label=g, edgecolor="none")
    ax.set_xscale("log")
    ax.set_xlabel("Chi tiêu y tế bình quân đầu người, 2019 (USD hiện hành, thang log)")
    ax.set_ylabel("Tuổi thọ trung bình, 2019 (năm)")
    ax.set_title(f"Chi tiêu y tế cao hơn đi kèm tuổi thọ cao hơn, phần lớn trùng với thu nhập (r = {res['raw_pearson_logHX_LE']:.2f})")
    vn = m[m["Country Code"] == VN_CODE]
    if len(vn):
        ax.scatter(vn.health_exp_pc, vn.life_exp, s=120, facecolor="none", edgecolor="black", linewidth=2)
        ax.annotate("Việt Nam", (vn.health_exp_pc.iloc[0], vn.life_exp.iloc[0]),
                    xytext=(10, -12), textcoords="offset points", fontsize=10, weight="bold")
    ax.legend(title="Nhóm thu nhập", frameon=False, fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"chart1_le_vs_chi_tieu_{tag}.png"), dpi=150)
    plt.close(fig)

    # Chart 2: LE vs GDP/người (log) với đường kỳ vọng và các nước ngoại lệ
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(m.gdp_pc_ppp, m.life_exp, s=28, alpha=0.5, color="grey", edgecolor="none")
    X = np.column_stack([m.log_gdp, m.log_gdp ** 2])
    b, *_ = ols(X, m.life_exp.values)
    xs = np.linspace(m.log_gdp.min(), m.log_gdp.max(), 200)
    ys = b[0] + b[1] * xs + b[2] * xs ** 2
    ax.plot(np.exp(xs), ys, color="black", lw=2, label="Kỳ vọng theo thu nhập")
    top_over = m.head(8)
    top_under = m.tail(8)
    ax.scatter(top_over.gdp_pc_ppp, top_over.life_exp, color="#2ca02c", s=50, label="Vượt kỳ vọng nhiều nhất")
    ax.scatter(top_under.gdp_pc_ppp, top_under.life_exp, color="#d62728", s=50, label="Dưới kỳ vọng nhiều nhất")
    for _, r in pd.concat([top_over, top_under]).iterrows():
        ax.annotate(r["Country Code"], (r.gdp_pc_ppp, r.life_exp), fontsize=7,
                    xytext=(3, 3), textcoords="offset points")
    vn = m[m["Country Code"] == VN_CODE]
    if len(vn):
        ax.scatter(vn.gdp_pc_ppp, vn.life_exp, s=140, facecolor="none", edgecolor="black", linewidth=2)
        ax.annotate("VNM", (vn.gdp_pc_ppp.iloc[0], vn.life_exp.iloc[0]),
                    xytext=(6, -10), textcoords="offset points", fontsize=9, weight="bold")
    ax.set_xscale("log")
    ax.set_xlabel("GDP bình quân đầu người theo PPP, 2019 (USD quốc tế, thang log)")
    ax.set_ylabel("Tuổi thọ trung bình, 2019 (năm)")
    ax.set_title("Sau khi tính thu nhập, một số nước có tuổi thọ cao/thấp hơn kỳ vọng rõ rệt")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"chart2_ky_vong_theo_thu_nhap_{tag}.png"), dpi=150)
    plt.close(fig)


def main():
    m19, r19, _ = analyse(2019, "2019")
    m22, r22, _ = analyse(2022, "2022_sensitivity")
    m3y, r3y, _ = analyse([2017, 2018, 2019], "tb3nam_2017_2019_sensitivity")
    charts(m19, r19, "2019")

    print("\n=== Độ nhạy: trung bình 2017-2019 ===")
    for k in ["n_countries", "raw_pearson_logHX_LE", "r2_income_only", "r2_full", "delta_r2_from_HX",
              "partial_r_HX_LE_given_income", "partial_p", "vn_gap", "vn_rank"]:
        print(f"{k}: {r3y.get(k)}")
    print("Top 5 vượt:", m3y.head(5)[["Country Code", "gap_years"]].round(2).values.tolist())
    print("Top 5 dưới:", m3y.tail(5).iloc[::-1][["Country Code", "gap_years"]].round(2).values.tolist())
    both3 = m19[["Country Code", "gap_years"]].merge(m3y[["Country Code", "gap_years"]],
               on="Country Code", suffixes=("_2019", "_3y"))
    print("Spearman hạng dư 2019 vs TB 2017-19:", round(stats.spearmanr(both3.gap_years_2019, both3.gap_years_3y)[0], 3))
    # Loại CAF (chuỗi tuổi thọ bất thường) để kiểm tra
    m19_xcaf = m19[m19["Country Code"] != "CAF"]
    print("Hệ số partial r (2019, bỏ CAF):", round(stats.pearsonr(
        *[np.array(v) for v in [ols(np.column_stack([m19_xcaf.log_gdp, m19_xcaf.log_gdp**2]), m19_xcaf.life_exp.values)[4],
                                ols(np.column_stack([m19_xcaf.log_gdp, m19_xcaf.log_gdp**2]), m19_xcaf.log_hx.values)[4]]])[0], 3))

    keys = ["n_countries", "raw_pearson_logHX_LE", "raw_spearman_HX_LE", "raw_pearson_logGDP_LE",
            "pearson_logHX_logGDP", "r2_income_only", "r2_full", "delta_r2_from_HX",
            "coef_logHX_adj", "p_logHX_adj", "partial_r_HX_LE_given_income", "partial_p",
            "vn_life_exp", "vn_expected", "vn_gap", "vn_rank", "vn_health_exp_pc", "vn_gdp_pc_ppp",
            "vn_income_group"]
    print("=== 2019 (chính) ===")
    for k in keys:
        print(f"{k}: {r19.get(k)}")
    print("\n=== 2022 (độ nhạy) ===")
    for k in keys:
        print(f"{k}: {r22.get(k)}")

    print("\n=== Top 10 vượt kỳ vọng (2019) ===")
    print(m19[["Country Name", "Country Code", "IncomeGroup", "gdp_pc_ppp", "health_exp_pc",
               "life_exp", "expected_le", "gap_years"]].head(10).round(2).to_string(index=False))
    print("\n=== Top 10 dưới kỳ vọng (2019) ===")
    print(m19[["Country Name", "Country Code", "IncomeGroup", "gdp_pc_ppp", "health_exp_pc",
               "life_exp", "expected_le", "gap_years"]].tail(10).iloc[::-1].round(2).to_string(index=False))
    print("\n=== Việt Nam (2019 / 2022) ===")
    print(m19[m19["Country Code"] == VN_CODE][["Country Name", "IncomeGroup", "gdp_pc_ppp",
          "health_exp_pc", "life_exp", "expected_le", "gap_years", "rank_over"]].round(2).to_string(index=False))
    print(m22[m22["Country Code"] == VN_CODE][["Country Name", "IncomeGroup", "gdp_pc_ppp",
          "health_exp_pc", "life_exp", "expected_le", "gap_years", "rank_over"]].round(2).to_string(index=False))
    # Ổn định xếp hạng giữa hai năm
    both = m19[["Country Code", "gap_years"]].merge(m22[["Country Code", "gap_years"]],
              on="Country Code", suffixes=("_2019", "_2022"))
    rho, _ = stats.spearmanr(both.gap_years_2019, both.gap_years_2022)
    print(f"\nTương quan hạng dư (2019 vs 2022), n={len(both)}: Spearman = {rho:.3f}")
    print(f"Tổng số nước 2022: {len(m22)}")


if __name__ == "__main__":
    main()
