"""Phân tích: chi tiêu y tế bình quân đầu người có gắn với tuổi thọ không,
và sau khi kiểm soát thu nhập (GDP/người PPP), nước nào vượt/dưới kỳ vọng.

Chạy từ thư mục workspace:  python3 -I outputs/code/analysis.py
"""
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import panel  # noqa: E402

OUT = "outputs/"
os.makedirs(OUT + "tables", exist_ok=True)
YEAR = "2019"  # năm trước đại dịch; độ phủ đầy đủ nhất (186 nước)


def build(year):
    meta, le, he, gd, codes = panel()
    rows = []
    for c in codes:
        l = le[c]["vals"].get(year)
        h = he.get(c, {}).get("vals", {}).get(year)
        g = gd.get(c, {}).get("vals", {}).get(year)
        if None in (l, h, g):
            continue
        rows.append({
            "code": c,
            "country": le[c]["name"],
            "region": meta[c]["Region"],
            "income": meta[c]["IncomeGroup"],
            "life_exp": l,
            "che_pc": h,
            "gdp_pc_ppp": g,
        })
    df = pd.DataFrame(rows)
    df["ln_che"] = np.log(df.che_pc)
    df["ln_gdp"] = np.log(df.gdp_pc_ppp)
    return df


def ols(X, y):
    X = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    ss_res = (resid ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    return beta, resid, 1 - ss_res / ss_tot


def main():
    df = build(YEAR)
    n = len(df)
    print(f"Năm {YEAR}: n = {n} nước")

    # 1) Tương quan thô
    r_raw = np.corrcoef(df.ln_che, df.life_exp)[0, 1]
    r_gdp = np.corrcoef(df.ln_gdp, df.life_exp)[0, 1]
    r_che_gdp = np.corrcoef(df.ln_che, df.ln_gdp)[0, 1]
    print(f"r(LE, ln CHE) thô      = {r_raw:.3f}")
    print(f"r(LE, ln GDP)          = {r_gdp:.3f}")
    print(f"r(ln CHE, ln GDP)      = {r_che_gdp:.3f}")

    # 2) Kỳ vọng theo thu nhập: LE ~ ln GDP + (ln GDP)^2 (cong, bão hòa ở mức giàu)
    X_inc = np.column_stack([df.ln_gdp, df.ln_gdp ** 2])
    b_inc, res_inc, r2_inc = ols(X_inc, df.life_exp.values)
    print(f"R² chỉ thu nhập        = {r2_inc:.3f}")

    # 3) Thêm chi tiêu: có còn đóng góp sau khi kiểm soát thu nhập?
    X_both = np.column_stack([df.ln_gdp, df.ln_gdp ** 2, df.ln_che])
    b_both, res_both, r2_both = ols(X_both, df.life_exp.values)
    print(f"R² thu nhập + chi tiêu = {r2_both:.3f}")
    print(f"Hệ số ln CHE (đã kiểm soát thu nhập) = {b_both[3]:.3f} năm / đơn vị ln")

    # Partial correlation của ln CHE với LE khi kiểm soát ln GDP (bậc 2)
    _, res_le_on_inc, _ = ols(X_inc, df.life_exp.values)
    _, res_che_on_inc, _ = ols(X_inc, df.ln_che.values)
    r_partial = np.corrcoef(res_le_on_inc, res_che_on_inc)[0, 1]
    print(f"Tương quan riêng (partial r) LE–ln CHE | thu nhập = {r_partial:.3f}")

    # 4) Khoảng cách so với kỳ vọng theo thu nhập
    df["expected_le"] = df.life_exp.values - res_inc
    df["gap_years"] = res_inc
    df["rank_over"] = df.gap_years.rank(ascending=False, method="min").astype(int)
    df["residual_che"] = res_both  # phần LE chưa giải thích sau khi có cả thu nhập + chi tiêu

    df = df.sort_values("gap_years", ascending=False).reset_index(drop=True)
    df.to_csv(OUT + "tables/ty_le_ky_vong_2019.csv", index=False, encoding="utf-8-sig")

    cols = ["country", "income", "life_exp", "expected_le", "gap_years", "che_pc", "gdp_pc_ppp"]
    print("\nTop 10 VƯỢT kỳ vọng (sau khi kiểm soát thu nhập):")
    print(df[cols].head(10).round(2).to_string(index=False))
    print("\nTop 10 DƯỚI kỳ vọng:")
    print(df[cols].tail(10).iloc[::-1].round(2).to_string(index=False))

    vn = df[df.code == "VNM"].iloc[0]
    vn_rank = int(df.index[df.code == "VNM"][0]) + 1
    print(f"\nViệt Nam: LE {vn.life_exp:.2f}, kỳ vọng {vn.expected_le:.2f}, "
          f"chênh {vn.gap_years:+.2f} năm, hạng {vn_rank}/{n} (1 = vượt kỳ vọng nhất)")
    print(f"  CHE/người {vn.che_pc:.0f} USD, GDP/người PPP {vn.gdp_pc_ppp:.0f} USD")

    # 5) Chỉ số hóa theo nhóm thu nhập
    g = df.groupby("income").agg(
        so_nuoc=("code", "count"),
        LE_tb=("life_exp", "mean"),
        CHE_trung_vi=("che_pc", "median"),
        chenh_tb=("gap_years", "mean"),
    ).round(2)
    print("\nTheo nhóm thu nhập:")
    print(g.to_string())
    g.to_csv(OUT + "tables/theo_nhom_thu_nhap_2019.csv", encoding="utf-8-sig")

    # 6) Độ bền vững: năm khác và năm 2015 để so sánh
    for yr in ["2015", "2023"]:
        d = build(yr)
        Xi = np.column_stack([d.ln_gdp, d.ln_gdp ** 2])
        bi, ri, _ = ols(Xi, d.life_exp.values)
        d["gap"] = ri
        top = d.sort_values("gap", ascending=False).country.head(10).tolist()
        bot = d.sort_values("gap").country.head(10).tolist()
        vn_g = d.loc[d.code == "VNM", "gap"].values
        print(f"\n[Bền vững {yr}] n={len(d)}, r(LE, ln CHE)={np.corrcoef(d.ln_che, d.life_exp)[0,1]:.3f}")
        print("  Top vượt:", ", ".join(top))
        print("  Top dưới:", ", ".join(bot))
        if len(vn_g):
            print(f"  Việt Nam chênh: {vn_g[0]:+.2f} năm")

    # Lưu tóm tắt số liệu cho story
    summary = {
        "year": YEAR, "n": n,
        "r_raw": r_raw, "r_gdp": r_gdp, "r2_inc": r2_inc, "r2_both": r2_both,
        "b_che": b_both[3], "r_partial": r_partial,
        "vn_le": float(vn.life_exp), "vn_exp": float(vn.expected_le),
        "vn_gap": float(vn.gap_years), "vn_rank": vn_rank,
        "vn_che": float(vn.che_pc), "vn_gdp": float(vn.gdp_pc_ppp),
    }
    pd.Series(summary).to_csv(OUT + "tables/tom_tat_2019.csv", encoding="utf-8-sig")


if __name__ == "__main__":
    main()
