"""Mức độ uống rượu (Dalc ngày thường, Walc cuối tuần) và điểm cuối kỳ G3.

Dữ liệu: data/student-mat.csv (Toán) và data/student-por.csv (Bồ Đào Nha).
Chạy: python outputs/ruou-g3/analysis.py  (từ thư mục gốc dự án)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data"
OUT = HERE
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
        "Mjob", "Fjob", "reason", "nursery", "internet"]  # khóa gộp theo student-merge.R
# Thuộc tính gần như không đổi giữa hai môn của cùng một học sinh (dùng để chọn cặp khi khóa gộp bị trùng)
TIEBREAK = ["guardian", "traveltime", "studytime", "famrel", "freetime", "goout", "Dalc",
            "Walc", "health", "romantic", "higher", "schoolsup", "famsup", "activities"]


# ---------------------------------------------------------------- 1. Đọc dữ liệu
m = pd.read_csv(DATA / "student-mat.csv", sep=";")
p = pd.read_csv(DATA / "student-por.csv", sep=";")
m["mon"] = "Toán"
p["mon"] = "Bồ Đào Nha"
m["sid"] = [f"M{i:03d}" for i in range(len(m))]
p["sid"] = [f"P{i:03d}" for i in range(len(p))]

# ---------------------------------------------------------------- 2. Ghép học sinh xuất hiện ở cả hai file
# Khóa gộp 13 cột của R gây ghép nhiều-nhiều (12 khóa trùng bên Toán, 8 bên Bồ Đào Nha),
# nên chọn cặp 1-1: ưu tiên cặp có nhiều thuộc tính khớp nhất (trong TIEBREAK), tham lam theo điểm.
cand = m.reset_index().merge(p.reset_index(), on=KEYS, suffixes=("_m", "_p"))
cand["score"] = sum((cand[f"{c}_m"] == cand[f"{c}_p"]).astype(int) for c in TIEBREAK)
cand = cand.sort_values(["score", "index_m", "index_p"], ascending=[False, True, True])
used_m, used_p, pairs = set(), set(), []
for r in cand.itertuples(index=False):
    if r.index_m in used_m or r.index_p in used_p:
        continue
    used_m.add(r.index_m)
    used_p.add(r.index_p)
    pairs.append((r.index_m, r.index_p, r.score))
pairs = pd.DataFrame(pairs, columns=["idx_m", "idx_p", "score"])
for _, row in pairs.iterrows():
    p.loc[int(row.idx_p), "sid"] = m.loc[int(row.idx_m), "sid"]
pairs.to_csv(OUT / "ghep_hoc_sinh_2_mon.csv", index=False)

n_pairs = len(pairs)
score_summary = pairs["score"].describe()
n_unique = pd.concat([m, p])["sid"].nunique()

# ---------------------------------------------------------------- 3. Gộp thành bảng học sinh-môn
df = pd.concat([m, p], ignore_index=True)
df["is_toan"] = (df["mon"] == "Toán").astype(int)
df["nam"] = (df["sex"] == "M").astype(int)
df["G3_0"] = (df["G3"] == 0)  # nghi ngờ: điểm 0 (không có dữ liệu vắng, bỏ thi/bỏ học?)
df["G3_hop_le"] = df["G3"].where(~df["G3_0"])

zero_stats = {
    "tong_so_ban_ghi": len(df),
    "G3_bang_0_toan": int(m["G3"].eq(0).sum()),
    "G3_bang_0_bdn": int(p["G3"].eq(0).sum()),
    "G3_0_ma_G2_>0_toan": int((m.G3.eq(0) & m.G2.gt(0)).sum()),
    "G3_0_ma_G2_>0_bdn": int((p.G3.eq(0) & p.G2.gt(0)).sum()),
    "G3_0_co_vang_>0_toan": int((m.G3.eq(0) & m.absences.gt(0)).sum()),
    "G3_0_co_vang_>0_bdn": int((p.G3.eq(0) & p.absences.gt(0)).sum()),
}
pd.Series(zero_stats).to_csv(OUT / "kiem_tra_G3_0.csv", header=["gia_tri"])

# Bảng phân tích chính: bỏ G3 = 0 (ghi chú: mọi G3 = 0 đều có absences = 0)
main = df[~df["G3_0"]].copy()
main = main.dropna(subset=["Dalc", "Walc", "G3"])


# ---------------------------------------------------------------- 4. Hàm thống kê
def spearman_ci(x, y, n):
    r, p_val = stats.spearmanr(x, y)
    z = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
    return r, p_val, lo, hi


def group_effect(d, exposure, cut=3):
    """Nhóm thấp (1-2) và cao (3-5). Trả về d Cohen, rank-biserial, MWU p, hiệu trung bình."""
    low = d.loc[d[exposure] < cut, "G3"]
    high = d.loc[d[exposure] >= cut, "G3"]
    n1, n2 = len(low), len(high)
    sp = np.sqrt(((n1 - 1) * low.var(ddof=1) + (n2 - 1) * high.var(ddof=1)) / (n1 + n2 - 2))
    dcoh = (low.mean() - high.mean()) / sp  # dương = nhóm uống nhiều có điểm thấp hơn
    u, p_mwu = stats.mannwhitneyu(low, high, alternative="two-sided")
    rb = 2 * u / (n1 * n2) - 1  # dương = nhóm thấp có xu hướng điểm cao hơn
    return dict(n_thap=n1, n_cao=n2, TB_thap=low.mean(), TB_cao=high.mean(),
                hieu_TB=low.mean() - high.mean(), d_Cohen=dcoh,
                rank_biserial=rb, p_MWU=p_mwu)


def ols_cluster(d, y, xcols, cluster):
    """OLS với sai số chuẩn cụm (cluster-robust) theo học sinh."""
    d = d.reset_index(drop=True)
    X = np.column_stack([np.ones(len(d))] + [d[c].astype(float).values for c in xcols])
    Y = d[y].astype(float).values
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ Y
    e = Y - X @ b
    meat = np.zeros((X.shape[1], X.shape[1]))
    groups = d.groupby(cluster).indices
    for idx in groups.values():
        s = X[idx].T @ e[idx]
        meat += np.outer(s, s)
    n, k = X.shape
    G = len(groups)
    c = G / (G - 1) * (n - 1) / (n - k)
    V = c * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    dfree = G - 1
    t = b / se
    pv = 2 * stats.t.sf(np.abs(t), dfree)
    tcrit = stats.t.ppf(0.975, dfree)
    return pd.DataFrame({"term": ["const"] + xcols, "coef": b, "se": se, "p": pv,
                         "ci_lo": b - tcrit * se, "ci_hi": b + tcrit * se,
                         "n": n, "n_hoc_sinh": G})


COV = ["nam", "age", "studytime", "failures", "absences"]
PRIOR = ["G1", "G2"]


def models(d, exposure_list, subject_term=True):
    """Model A: thô (có môn); B: + nhân khẩu/học tập; C: + điểm kỳ trước G1, G2.
    Với phân tích một môn (subject_term=False) không đưa biến môn vào mô hình."""
    out = []
    sub_t = ["is_toan"] if subject_term else []
    for name, cols in [("A_tho", exposure_list + sub_t),
                       ("B_hieu_chinh_nen", exposure_list + sub_t + COV),
                       ("C_them_G1_G2", exposure_list + sub_t + COV + PRIOR)]:
        res = ols_cluster(d, "G3", cols, "sid")
        res = res[res["term"].isin(exposure_list)].copy()
        res["ten_bien"] = res["term"]
        res["mo_hinh"] = name
        out.append(res)
    return pd.concat(out, ignore_index=True)


# ---------------------------------------------------------------- 5. Phân tích theo từng môn (mỗi học sinh 1 lần/môn)
rows, reg_rows, group_rows = [], [], []
for mon, sub in main.groupby("mon"):
    for exp in ["Dalc", "Walc"]:
        r, pv, lo, hi = spearman_ci(sub[exp], sub["G3"], len(sub))
        rows.append(dict(mon=mon, ten_bien=exp, n=len(sub), spearman_rho=r,
                         rho_CI_lo=lo, rho_CI_hi=hi, p_spearman=pv))
        g = group_effect(sub, exp)
        g.update(mon=mon, ten_bien=exp)
        group_rows.append(g)
        reg = models(sub, [exp], subject_term=False)
        reg["mon"] = mon
        reg_rows.append(reg)

# ---------------------------------------------------------------- 6. Phân tích gộp (cả hai môn, mỗi học sinh-môn 1 dòng, SE theo học sinh)
pooled_rows, pooled_group = [], []
for exp in ["Dalc", "Walc"]:
    r, pv, lo, hi = spearman_ci(main[exp], main["G3"], len(main))
    pooled_rows.append(dict(mon="Gộp (2 môn)", ten_bien=exp, n=len(main), spearman_rho=r,
                            rho_CI_lo=lo, rho_CI_hi=hi, p_spearman=pv))
    g = group_effect(main, exp)
    g.update(mon="Gộp (2 môn)", ten_bien=exp)
    pooled_group.append(g)
pooled_reg = pd.concat([models(main, ["Dalc", "Walc"]).assign(mon="Gộp (2 môn)")], ignore_index=True)

# ---------------------------------------------------------------- 7. Độ nhạy
# 7a. Đưa G3 = 0 trở lại
sens_rows = []
for mon, sub in df.groupby("mon"):
    sub = sub.dropna(subset=["Dalc", "Walc", "G3"])
    for exp in ["Dalc", "Walc"]:
        r, pv, lo, hi = spearman_ci(sub[exp], sub["G3"], len(sub))
        sens_rows.append(dict(kich_ban=f"Giữ G3=0 ({mon})", mon=mon, ten_bien=exp,
                              n=len(sub), spearman_rho=r, p=pv))
# 7b. Mỗi học sinh 1 dòng (662 học sinh duy nhất): G3 và Dalc/Walc lấy trung bình giữa các môn
stud = (main.groupby("sid")
        .agg(G3=("G3", "mean"), Dalc=("Dalc", "mean"), Walc=("Walc", "mean"), n_mon=("G3", "size"))
        .reset_index())
for exp in ["Dalc", "Walc"]:
    r, pv, lo, hi = spearman_ci(stud[exp], stud["G3"], len(stud))
    sens_rows.append(dict(kich_ban="1 dòng/học sinh (trung bình 2 môn)", mon="Gộp",
                          ten_bien=exp, n=len(stud), spearman_rho=r, p=pv))
# 7c. Chỉ lấy học sinh chỉ có một môn (không trùng) để so sánh
counts = df["sid"].value_counts()
single = df[df["sid"].map(counts) == 1]
for exp in ["Dalc", "Walc"]:
    sub = single.dropna(subset=[exp, "G3"]).query("G3 > 0")
    r, pv, lo, hi = spearman_ci(sub[exp], sub["G3"], len(sub))
    sens_rows.append(dict(kich_ban="Chỉ học sinh không trùng (1 môn)", mon="Gộp",
                          ten_bien=exp, n=len(sub), spearman_rho=r, p=pv))
sens = pd.DataFrame(sens_rows)

# ---------------------------------------------------------------- 8. Lưu kết quả
corr_tab = pd.DataFrame(rows + pooled_rows)
corr_tab.to_csv(OUT / "tuong_quan_spearman.csv", index=False)
group_tab = pd.DataFrame(group_rows + pooled_group)
group_tab.to_csv(OUT / "so_sanh_nhom_thap_cao.csv", index=False)
reg_tab = pd.concat(reg_rows + [pooled_reg], ignore_index=True)
reg_tab.to_csv(OUT / "hoi_quy_he_so.csv", index=False)
sens.to_csv(OUT / "do_nhay.csv", index=False)
main.to_csv(OUT / "du_lieu_phan_tich_hoc_sinh_mon.csv", index=False)
stud.to_csv(OUT / "du_lieu_hoc_sinh_duy_nhat.csv", index=False)

summary = {
    "so_hoc_sinh_ghep_2_mon": n_pairs,
    "so_hoc_sinh_duy_nhat": n_unique,
    "so_ban_ghi_toan": len(m),
    "so_ban_ghi_bdn": len(p),
    "diem_tuong_dong_cap_ghep_TB": round(score_summary["mean"], 2),
    "diem_tuong_dong_cap_ghep_min": int(score_summary["min"]),
    "so_ban_ghi_phan_tich": len(main),
    "so_ban_ghi_bi_loai_G3_0": int(df.G3_0.sum()),
}
pd.Series(summary).to_csv(OUT / "tom_tat_du_lieu.csv", header=["gia_tri"])
print(pd.Series(summary).to_string())
print(pd.Series(zero_stats).to_string())
print("\n== Spearman ==")
print(corr_tab.round(4).to_string(index=False))
print("\n== So sánh nhóm (thấp 1-2 vs cao 3-5) ==")
print(group_tab.round(4).to_string(index=False))
print("\n== Hồi quy (mỗi bậc tăng) ==")
print(reg_tab.round(4).to_string(index=False))
print("\n== Độ nhạy ==")
print(sens.round(4).to_string(index=False))

# ---------------------------------------------------------------- 9. Biểu đồ
sns.set_theme(style="whitegrid", context="notebook")
fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharey=True)
for i, exp in enumerate(["Dalc", "Walc"]):
    label = "ngày thường" if exp == "Dalc" else "cuối tuần"
    for j, mon in enumerate(["Toán", "Bồ Đào Nha"]):
        ax = axes[i, j]
        sub = main[main.mon == mon]
        sns.boxplot(data=sub, x=exp, y="G3", ax=ax, color="#9ecae1", fliersize=2)
        sns.stripplot(data=sub, x=exp, y="G3", ax=ax, color="#08519c", size=2.5, alpha=0.35, jitter=0.2)
        n_grp = sub.groupby(exp)["G3"].size()
        ax.set_title(f"{mon}: rượu {label}")
        ax.set_xlabel(f"Mức uống rượu {label} (1 = rất ít, 5 = rất nhiều)")
        ax.set_ylabel("Điểm cuối kỳ G3 (0-20)")
        r = corr_tab[(corr_tab.mon == mon) & (corr_tab.ten_bien == exp)].iloc[0]
        ax.text(0.02, 0.03, f"Spearman rho = {r.spearman_rho:.2f}, p = {r.p_spearman:.3g}",
                transform=ax.transAxes, fontsize=9, color="#333")
fig.suptitle("Điểm cuối kỳ G3 theo mức uống rượu (đã bỏ G3 = 0)", fontsize=13)
fig.tight_layout()
fig.savefig(OUT / "bieu_do_hop_G3_theo_ruou.png", dpi=150)
plt.close(fig)

# Forest plot: hệ số hồi quy (điểm G3 thay đổi mỗi bậc tăng)
fp = reg_tab.copy()
fp["nhan"] = fp["mon"] + " | " + fp["ten_bien"].map({"Dalc": "ngày thường", "Walc": "cuối tuần"}) + " | " + fp["mo_hinh"]
fp = fp.iloc[::-1].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(9, 9))
colors = fp["mo_hinh"].map({"A_tho": "#9ecae1", "B_hieu_chinh_nen": "#4292c6", "C_them_G1_G2": "#08306b"})
ax.errorbar(fp["coef"], range(len(fp)), xerr=[fp["coef"] - fp["ci_lo"], fp["ci_hi"] - fp["coef"]],
            fmt="none", ecolor="#666", capsize=3)
ax.scatter(fp["coef"], range(len(fp)), c=colors, s=40, zorder=3)
ax.axvline(0, color="red", lw=1, ls="--")
ax.set_yticks(range(len(fp)))
ax.set_yticklabels(fp["nhan"], fontsize=8)
ax.set_xlabel("Thay đổi G3 (0-20) khi mức rượu tăng 1 bậc (KTC 95%)")
ax.set_title("Ước lượng hiệu ứng uống rượu lên G3 (sai số chuẩn theo học sinh)")
fig.tight_layout()
fig.savefig(OUT / "bieu_do_forest_he_so.png", dpi=150)
plt.close(fig)
print("\nSaved outputs to", OUT)
