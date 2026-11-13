"""Mức uống rượu (Dalc ngày thường, Walc cuối tuần) và điểm cuối kỳ G3.
Dữ liệu: student-mat.csv (Toán) + student-por.csv (Tiếng Bồ Đào Nha).
Học sinh xuất hiện ở cả hai file được ghép bằng đúng 13 khóa trong student-merge.R.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
        "Mjob", "Fjob", "reason", "nursery", "internet"]
CHECK_COLS = ["guardian", "traveltime", "studytime", "failures", "schoolsup", "famsup",
              "paid", "activities", "higher", "romantic", "famrel", "freetime", "goout",
              "Dalc", "Walc", "health"]
CONTROLS = ["G1", "G2", "is_por", "male", "age", "studytime", "failures"]
EXTRA = ["goout", "health", "absences"]


# ---------- helpers ----------
def cluster_ols(data, y, xcols, cluster="student_id"):
    """OLS với sai số chuẩn cluster-robust (CR1) theo học sinh."""
    X = np.column_stack([np.ones(len(data))] + [data[c].to_numpy(float) for c in xcols])
    yv = data[y].to_numpy(float)
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ yv
    e = yv - X @ b
    g = pd.factorize(data[cluster])[0]
    G = g.max() + 1
    meat = np.zeros((k, k))
    for gi in range(G):
        idx = g == gi
        s = X[idx].T @ e[idx]
        meat += np.outer(s, s)
    V = (G / (G - 1)) * ((n - 1) / (n - k)) * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    dfree = G - 1
    tcrit = stats.t.ppf(0.975, dfree)
    ss_tot = ((yv - yv.mean()) ** 2).sum()
    r2 = 1 - (e @ e) / ss_tot
    res = pd.DataFrame({"term": ["const"] + list(xcols), "coef": b, "se": se,
                        "p": 2 * stats.t.sf(np.abs(b / se), dfree),
                        "ci_lo": b - tcrit * se, "ci_hi": b + tcrit * se})
    return res, r2, n, G


def std_beta(data, y, x):
    return data[x].std() / data[y].std()


def boot_spearman(d, x, y, B=500, seed=1):
    """Bootstrap theo cụm học sinh (resample học sinh, giữ cả các bản ghi của họ)."""
    rng = np.random.default_rng(seed)
    codes = pd.factorize(d["student_id"])[0]
    G = codes.max() + 1
    idx_by = [np.where(codes == g)[0] for g in range(G)]
    xv = d[x].to_numpy(float)
    yv = d[y].to_numpy(float)
    rhos = []
    for _ in range(B):
        pick = rng.integers(0, G, G)
        ii = np.concatenate([idx_by[p] for p in pick])
        rhos.append(stats.spearmanr(xv[ii], yv[ii])[0])
    return np.nanpercentile(rhos, [2.5, 97.5])


def cliffs_and_d(d, x, lo, hi, y="G3"):
    a = d.loc[d[x] <= lo, y].to_numpy(float)
    b = d.loc[d[x] >= hi, y].to_numpy(float)
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    cohen_d = (b.mean() - a.mean()) / sp
    U = stats.mannwhitneyu(b, a, alternative="two-sided")
    cliff = 2 * U.statistic / (len(a) * len(b)) - 1
    return {"n_low": len(a), "n_high": len(b), "mean_low": a.mean(), "mean_high": b.mean(),
            "cohen_d_high_minus_low": cohen_d, "cliffs_delta_high_vs_low": cliff,
            "mwu_p": U.pvalue}


# ---------- 1. Ghép học sinh ở cả hai file ----------
mat = pd.read_csv(DATA / "student-mat.csv", sep=";")
por = pd.read_csv(DATA / "student-por.csv", sep=";")
mat["row"] = np.arange(len(mat))
por["row"] = np.arange(len(por))

pairs = mat.merge(por, on=KEYS, suffixes=("_mat", "_por"))
print(f"Số cặp khớp theo 13 khóa: {len(pairs)}")
dup_mat = pairs["row_mat"].duplicated().sum()
dup_por = pairs["row_por"].duplicated().sum()
print(f"Trùng trong cặp: mat={dup_mat}, por={dup_por}")
pairs = pairs.drop_duplicates("row_mat").drop_duplicates("row_por")
print(f"Cặp 1-1 sau khi bỏ trùng: {len(pairs)}")

agree = pd.DataFrame({
    "column": CHECK_COLS,
    "agree_share": [float((pairs[c + "_mat"] == pairs[c + "_por"]).mean()) for c in CHECK_COLS],
})
agree.to_csv(OUT / "match_agreement.csv", index=False)
print("\nTỷ lệ trùng giá trị của cặp khớp trên các cột không dùng làm khóa:")
print(agree.round(3).to_string(index=False))

mat["student_id"] = "M" + mat["row"].astype(str)
por["student_id"] = "P" + por["row"].astype(str)
for k, (rm, rp) in enumerate(zip(pairs["row_mat"], pairs["row_por"])):
    sid = f"B{k}"
    mat.loc[mat["row"] == rm, "student_id"] = sid
    por.loc[por["row"] == rp, "student_id"] = sid

mat["subject"] = "Toán"
por["subject"] = "Tiếng Bồ Đào Nha"
mat["is_por"] = 0
por["is_por"] = 1
df = pd.concat([mat, por], ignore_index=True)
df["male"] = (df["sex"] == "M").astype(int)
df["both_files"] = df["student_id"].str.startswith("B").astype(int)

n_records = len(df)
n_students = df["student_id"].nunique()
print(f"\nBản ghi (học sinh x môn): {n_records}; học sinh duy nhất: {n_students}; "
      f"học sinh ở cả hai môn: {df.loc[df.both_files == 1, 'student_id'].nunique()}")

# ---------- 2. Kiểm tra chất lượng G3 và điểm trước ----------
dq = []
for name, d in [("Toán", df[df.is_por == 0]), ("Tiếng Bồ Đào Nha", df[df.is_por == 1])]:
    dq.append({"subject": name, "rows": len(d),
               "G3_eq_0": int((d.G3 == 0).sum()),
               "G3_eq_0_but_G2_gt_0": int(((d.G3 == 0) & (d.G2 > 0)).sum()),
               "G2_eq_0": int((d.G2 == 0).sum()),
               "G1_eq_0": int((d.G1 == 0).sum())})
dq = pd.DataFrame(dq)
dq.to_csv(OUT / "data_quality.csv", index=False)
print("\nKiểm tra G3/G1/G2 = 0:")
print(dq.to_string(index=False))

# Mẫu chính: loại G3=0 (không có điểm cuối kỳ thật, nhiều khả năng bỏ học/không thi)
# và loại G1/G2=0 (điểm trước bằng 0 khi G3>0 là mâu thuẫn, dùng làm biến kiểm soát).
prim = df[(df.G3 > 0) & (df.G1 > 0) & (df.G2 > 0)].copy()
print(f"\nMẫu chính: {len(prim)} bản ghi, {prim.student_id.nunique()} học sinh")

# ---------- 3. Mô tả theo mức uống rượu ----------
desc_rows = []
for x in ["Dalc", "Walc"]:
    for lvl, g in prim.groupby(x):
        m_ = g.G3.mean()
        se_ = g.G3.std(ddof=1) / np.sqrt(len(g))
        desc_rows.append({"measure": x, "level": int(lvl), "n": len(g),
                          "mean_G3": m_, "ci_lo": m_ - 1.96 * se_, "ci_hi": m_ + 1.96 * se_,
                          "sd_G3": g.G3.std(ddof=1)})
desc = pd.DataFrame(desc_rows)
desc.to_csv(OUT / "descriptives_by_level.csv", index=False)
print("\nĐiểm G3 trung bình theo mức uống rượu (mẫu chính):")
print(desc.round(2).to_string(index=False))

# ---------- 4. Các kịch bản: effect size + thống kê ----------
scenarios = {
    "A. Chính (G3>0, G1,G2>0; mỗi bản ghi học sinh x môn)": prim,
    "B. Không loại bản ghi nào (gồm G3=0, G1/G2=0)": df,
    "C. Mỗi học sinh 1 bản ghi (giữ Toán khi ở cả hai)": prim[(prim.is_por == 0) | (prim.both_files == 0)],
    "D. Mỗi học sinh 1 bản ghi (giữ Tiếng BĐN khi ở cả hai)": prim[(prim.is_por == 1) | (prim.both_files == 0)],
}
rows = []
for name, d in scenarios.items():
    for x in ["Dalc", "Walc"]:
        rho, rho_p = stats.spearmanr(d[x], d["G3"])
        rho_lo, rho_hi = boot_spearman(d, x, "G3", B=1000)
        raw, _, n_raw, G_raw = cluster_ols(d, "G3", [x])
        adj_cols = [x] + CONTROLS
        adj, r2_full, n_adj, G_adj = cluster_ols(d, "G3", adj_cols)
        red_cols = [c for c in CONTROLS]
        _, r2_red, _, _ = cluster_ols(d, "G3", red_cols)
        sb = adj.loc[adj.term == x].iloc[0]
        lo = cliffs_and_d(d, x, 1, 4)
        rows.append({
            "scenario": name, "measure": x, "records": len(d),
            "students": d.student_id.nunique(),
            "spearman_rho": rho, "rho_ci_lo": rho_lo, "rho_ci_hi": rho_hi, "spearman_p": rho_p,
            "raw_slope_per_level": raw.loc[raw.term == x, "coef"].iloc[0],
            "raw_ci_lo": raw.loc[raw.term == x, "ci_lo"].iloc[0],
            "raw_ci_hi": raw.loc[raw.term == x, "ci_hi"].iloc[0],
            "raw_p": raw.loc[raw.term == x, "p"].iloc[0],
            "adj_slope_per_level": sb.coef, "adj_ci_lo": sb.ci_lo, "adj_ci_hi": sb.ci_hi,
            "adj_p": sb.p,
            "adj_std_beta": sb.coef * std_beta(d, "G3", x),
            "partial_R2_increment": r2_full - r2_red,
            "n_low_group(level1)": lo["n_low"], "n_high_group(level4-5)": lo["n_high"],
            "mean_G3_level1": lo["mean_low"], "mean_G3_level4_5": lo["mean_high"],
            "cohen_d_high_minus_low": lo["cohen_d_high_minus_low"],
            "cliffs_delta_high_vs_low": lo["cliffs_delta_high_vs_low"],
            "mwu_p_high_vs_low": lo["mwu_p"],
        })
scen_df = pd.DataFrame(rows)
scen_df.to_csv(OUT / "results_scenarios.csv", index=False)
pd.set_option("display.width", 250)
print("\nKết quả các kịch bản:")
print(scen_df[["scenario", "measure", "records", "students", "spearman_rho", "rho_ci_lo", "rho_ci_hi",
               "raw_slope_per_level", "raw_p", "adj_slope_per_level", "adj_ci_lo", "adj_ci_hi", "adj_p",
               "adj_std_beta", "partial_R2_increment", "cohen_d_high_minus_low", "cliffs_delta_high_vs_low",
               "mwu_p_high_vs_low"]].round(4).to_string(index=False))

# ---------- 5. Mô hình gộp: Dalc và Walc cùng lúc; mô hình thêm biến xã hội/sức khỏe ----------
joint, r2j, nj, Gj = cluster_ols(prim, "G3", ["Dalc", "Walc"] + CONTROLS)
joint["model"] = "Dalc+Walc+kiểm soát"
extra, r2e, ne, Ge = cluster_ols(prim, "G3", ["Dalc", "Walc"] + CONTROLS + EXTRA)
extra["model"] = "Dalc+Walc+kiểm soát+goout,health,absences"
models = pd.concat([joint, extra], ignore_index=True)
models["R2"] = np.where(models.model.str.contains("absences"), r2e, r2j)
models.to_csv(OUT / "joint_models.csv", index=False)
print(f"\nMô hình gộp (n={nj}, cụm={Gj}; R2={r2j:.3f}):")
print(joint.round(4).to_string(index=False))
print(f"\nMô hình gộp + goout, health, absences (n={ne}, R2={r2e:.3f}):")
print(extra.round(4).to_string(index=False))

# ---------- 6. Theo từng môn (mẫu chính) ----------
sub_rows = []
for subj, d in prim.groupby("subject"):
    for x in ["Dalc", "Walc"]:
        ctrl = [c for c in CONTROLS if c != "is_por"]
        res, r2, n, G = cluster_ols(d, "G3", [x] + ctrl)
        sb = res.loc[res.term == x].iloc[0]
        sub_rows.append({"subject": subj, "measure": x, "records": n, "students": G,
                         "adj_slope_per_level": sb.coef, "adj_ci_lo": sb.ci_lo,
                         "adj_ci_hi": sb.ci_hi, "adj_p": sb.p})
sub_df = pd.DataFrame(sub_rows)
sub_df.to_csv(OUT / "subject_models.csv", index=False)
print("\nTheo từng môn (mô hình điều chỉnh):")
print(sub_df.round(4).to_string(index=False))

prim.to_csv(OUT / "analysis_sample.csv", index=False)
