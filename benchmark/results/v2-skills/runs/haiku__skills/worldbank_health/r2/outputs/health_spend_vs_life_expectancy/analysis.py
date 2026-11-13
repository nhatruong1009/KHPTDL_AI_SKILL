"""Chi tieu y te va tuoi tho sau khi kiem soat thu nhap (World Bank WDI).

Chay: python analysis.py   (doc du lieu tu ../../data, ghi ket qua vao thu muc nay)
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data"))

FILES = {
    "le": os.path.join(DATA, "life_expectancy", "API_SP.DYN.LE00.IN_DS2_en_csv_v2_70864.csv"),
    "hexp": os.path.join(DATA, "health_expenditure_per_capita", "API_SH.XPD.CHEX.PC.CD_DS2_en_csv_v2_57.csv"),
    "gdp": os.path.join(DATA, "gdp_per_capita_ppp", "API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_60730.csv"),
}
META = os.path.join(DATA, "life_expectancy", "Metadata_Country_API_SP.DYN.LE00.IN_DS2_en_csv_v2_70864.csv")


def load_wb(path):
    """WB API csv: 4 dong metadata truoc header; cot cuoi la rong."""
    df = pd.read_csv(path, skiprows=4, encoding="utf-8-sig")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    years = [c for c in df.columns if c.isdigit()]
    long = df.melt(id_vars=["Country Name", "Country Code"], value_vars=years,
                   var_name="year", value_name="value")
    long["year"] = long["year"].astype(int)
    return long.dropna(subset=["value"])


meta = pd.read_csv(META, encoding="utf-8-sig")
meta = meta[["Country Code", "Region", "IncomeGroup"]]
# Cac dong tong hop (khu vuc, nhom thu nhap) co Region/IncomeGroup rong -> loai
meta = meta.dropna(subset=["Region", "IncomeGroup"])

frames = {}
for k, p in FILES.items():
    l = load_wb(p)
    frames[k] = l.rename(columns={"value": k})
    print(f"{k}: {len(l)} quan sat khac rong, {l['Country Code'].nunique()} ma, nam {l.year.min()}-{l.year.max()}")

panel = frames["le"].merge(frames["hexp"], on=["Country Code", "Country Name", "year"], how="inner")
panel = panel.merge(frames["gdp"][["Country Code", "year", "gdp"]], on=["Country Code", "year"], how="inner")
panel = panel.merge(meta, on="Country Code", how="inner")  # chi giu quoc gia that (co nhom thu nhap)
panel["log_hexp"] = np.log(panel["hexp"])
panel["log_gdp"] = np.log(panel["gdp"])
panel.to_csv(os.path.join(HERE, "panel_complete_cases.csv"), index=False)

# Chon nam: nam gan nhat co nhieu quoc gia du 3 chi so nhat
cov = panel.groupby("year")["Country Code"].nunique()
print("\nSo quoc gia co du 3 chi so theo nam (5 nam gan nhat):")
print(cov.tail(8).to_string())


def ols(y, X):
    X1 = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    resid = y - X1 @ beta
    n, k = X1.shape
    s2 = resid @ resid / (n - k)
    cov_b = s2 * np.linalg.inv(X1.T @ X1)
    se = np.sqrt(np.diag(cov_b))
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, r2, resid


def analyse(year):
    d = panel[panel.year == year].copy().reset_index(drop=True)
    n = len(d)
    out = {"year": year, "n": n}
    # 1) Tuong quan thuan (chua kiem soat thu nhap)
    rho, p = stats.spearmanr(d["hexp"], d["le"])
    out["spearman_hexp_le"] = rho
    out["spearman_p"] = p
    # 2) Thu nhap, LE ~ log(GDP)
    b, se, r2_inc, res_inc = ols(d["le"].values, d[["log_gdp"]].values)
    out["r2_income_only"] = r2_inc
    out["b_loggdp"] = b[1]
    # 3) LE ~ log(GDP) + log(chi tieu y te): chi tieu y te co them gia tri sau khi kiem soat thu nhap?
    b2, se2, r2_both, _ = ols(d["le"].values, d[["log_gdp", "log_hexp"]].values)
    out["b_loghexp_adj"] = b2[2]
    out["se_loghexp_adj"] = se2[2]
    out["t_loghexp_adj"] = b2[2] / se2[2]
    out["r2_both"] = r2_both
    # 4) Ky vong theo thu nhap (mo hinh bac 2 trong log GDP) -> do chech lech
    X2 = np.column_stack([d["log_gdp"], d["log_gdp"] ** 2])
    b3, _, r2_quad, res_quad = ols(d["le"].values, X2)
    out["r2_income_quad"] = r2_quad
    d["expected_le"] = d["le"] - res_inc            # mo hinh tuyen tinh theo log GDP
    d["gap_le"] = res_inc                           # > 0: vuot ky vong
    d["gap_le_quad"] = res_quad                     # mo hinh bac 2 (kiem tra do nhay)
    # Ky vong tu mo hinh tuyen tinh
    X1 = np.column_stack([np.ones(n), d["log_gdp"].values])
    d["expected_le"] = X1 @ b
    d["gap_le"] = d["le"] - d["expected_le"]
    d["rank_gap"] = d["gap_le"].rank(ascending=False).astype(int)
    d["rank_gap_quad"] = d["gap_le_quad"].rank(ascending=False).astype(int)
    d["hexp_quartile_rank"] = d["hexp"].rank(pct=True)
    return d, out


if __name__ == "__main__":
    year_main = int(cov[cov.index <= 2023].tail(1).index[0]) if cov.index.max() > 2023 else cov.index.max()
    # Dung nam 2022 hoac 2021 neu co du do phu (do phu tot hon nam moi nhat)
    candidates = cov[(cov.index >= 2019) & (cov.index <= 2023)]
    year_main = int(candidates.idxmax())
    print(f"\nNam chinh (phu nhieu nhat trong 2019-2023): {year_main}")

    d, out = analyse(year_main)
    for k, v in out.items():
        print(f"{k}: {v}")

    d.sort_values("gap_le", ascending=False).to_csv(os.path.join(HERE, "gap_ranking.csv"), index=False)

    # Do nhay: cac nam khac
    sens = []
    for y in sorted(candidates.index):
        _, o = analyse(int(y))
        sens.append({k: o[k] for k in ["year", "n", "spearman_hexp_le", "b_loghexp_adj",
                                        "t_loghexp_adj", "r2_income_only", "r2_both", "r2_income_quad"]})
    pd.DataFrame(sens).to_csv(os.path.join(HERE, "sensitivity_by_year.csv"), index=False)
    print("\nDo nhay theo nam:")
    print(pd.DataFrame(sens).round(3).to_string(index=False))

    pd.Series(out).to_csv(os.path.join(HERE, "model_summary.csv"), header=["value"])
