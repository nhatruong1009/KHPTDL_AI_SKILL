"""Rượu (Dalc, Walc) vs G3 - dữ liệu Toán + Bồ Đào Nha, loại trùng học sinh, xử lý G3=0.
Chạy:  python -I outputs/alcohol_vs_g3/analysis.py   (từ thư mục gốc dự án)
"""
import os
import numpy as np, pandas as pd
from scipy import stats
from scipy.optimize import linear_sum_assignment
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "outputs/alcohol_vs_g3"
rng = np.random.default_rng(42)
m = pd.read_csv("data/student-mat.csv", sep=";")
p = pd.read_csv("data/student-por.csv", sep=";")

# ---------------------------------------------------------------- 1. Khớp học sinh
KEYS = "school sex age address famsize Pstatus Medu Fedu Mjob Fjob reason nursery internet".split()  # khóa của student-merge.R
SOFT = "guardian traveltime studytime schoolsup famsup activities higher romantic famrel freetime goout health".split()
# SOFT: thuộc tính ổn định giữa 2 file (khớp ~97-99%) dùng để phân giải khóa trùng. KHÔNG dùng Dalc/Walc/G*.
m["rid_m"] = np.arange(len(m)); p["rid_p"] = np.arange(len(p))
pairs, ambiguous_groups = [], 0
gm = m.groupby(KEYS); gp = p.groupby(KEYS)
common = set(gm.groups) & set(gp.groups)
for k in common:
    a = m.loc[gm.groups[k]]; b = p.loc[gp.groups[k]]
    amb = len(a) > 1 or len(b) > 1
    ambiguous_groups += amb
    cost = np.array([[sum(ra[c] != rb[c] for c in SOFT) for _, rb in b.iterrows()] for _, ra in a.iterrows()])
    r, c = linear_sum_assignment(cost)
    for i, j in zip(r, c):
        pairs.append((a.iloc[i].rid_m, b.iloc[j].rid_p, amb, cost[i, j]))
pairs = pd.DataFrame(pairs, columns=["rid_m", "rid_p", "ambiguous", "soft_mismatch"])
print("cặp khớp:", len(pairs), "| nhóm khóa mơ hồ:", ambiguous_groups, "| cặp trong nhóm mơ hồ:", int(pairs.ambiguous.sum()))
print("mismatch mềm trung bình:", pairs.soft_mismatch.mean().round(2), "max", pairs.soft_mismatch.max())

# ---------------------------------------------------------------- 2. Bảng cấp học sinh
mm = m.set_index("rid_m"); pp = p.set_index("rid_p")
rows = []
linked_m, linked_p = set(pairs.rid_m), set(pairs.rid_p)
for _, r in pairs.iterrows():
    a, b = mm.loc[r.rid_m], pp.loc[r.rid_p]
    rows.append(dict(sid=f"L{len(rows)}", linked=1, amb=int(r.ambiguous), Dalc=(a.Dalc + b.Dalc) / 2, Walc=(a.Walc + b.Walc) / 2,
                     G3_mat=a.G3, G3_por=b.G3, **{c: b[c] for c in ["sex", "age", "school", "address", "Medu", "Fedu", "studytime", "goout", "famrel", "failures", "absences"]}))
for i, a in mm.iterrows():
    if i not in linked_m:
        rows.append(dict(sid=f"M{i}", linked=0, amb=0, Dalc=a.Dalc, Walc=a.Walc, G3_mat=a.G3, G3_por=np.nan,
                         **{c: a[c] for c in ["sex", "age", "school", "address", "Medu", "Fedu", "studytime", "goout", "famrel", "failures", "absences"]}))
for i, b in pp.iterrows():
    if i not in linked_p:
        rows.append(dict(sid=f"P{i}", linked=0, amb=0, Dalc=b.Dalc, Walc=b.Walc, G3_mat=np.nan, G3_por=b.G3,
                         **{c: b[c] for c in ["sex", "age", "school", "address", "Medu", "Fedu", "studytime", "goout", "famrel", "failures", "absences"]}))
S = pd.DataFrame(rows)
S["both"] = S.G3_mat.notna() & S.G3_por.notna()
print("số học sinh duy nhất:", len(S), "| có cả 2 môn:", int(S.both.sum()), "| chỉ Toán:", int((S.G3_mat.notna() & ~S.both).sum()), "| chỉ Bồ:", int((S.G3_por.notna() & ~S.both).sum()))
print("Dalc lệch giữa 2 file ở cặp khớp:", (pairs.merge(m[["rid_m", "Dalc"]], on="rid_m").merge(p[["rid_p", "Dalc"]], on="rid_p").pipe(lambda d: d.Dalc_x != d.Dalc_y)).mean().round(3))

# ---------------------------------------------------------------- 3. G3 đáng ngờ
z = lambda s: (s - s.mean()) / s.std()
zeros = pd.DataFrame({"mon": ["Toán", "Bồ Đào Nha"], "n": [len(m), len(p)],
                      "G3_bang_0": [(m.G3 == 0).sum(), (p.G3 == 0).sum()],
                      "G3_0_va_G2_lon_hon_0": [((m.G3 == 0) & (m.G2 > 0)).sum(), ((p.G3 == 0) & (p.G2 > 0)).sum()],
                      "G3_0_va_absences_0": [((m.G3 == 0) & (m.absences == 0)).sum(), ((p.G3 == 0) & (p.absences == 0)).sum()],
                      "absences_0_trong_G3_duong": [(m[m.G3 > 0].absences == 0).mean().round(3), (p[p.G3 > 0].absences == 0).mean().round(3)]})
print(zeros.to_string()); zeros.to_csv(f"{OUT}/g3_dang_ngo.csv", index=False)
# G3 = 0: coi là không có điểm thi cuối (bỏ thi/bỏ học), không phải điểm thật -> loại trong phân tích chính
valid = lambda s: s.where(s > 0)
S["G3m_v"], S["G3p_v"] = valid(S.G3_mat), valid(S.G3_por)
S["zero_any"] = ((S.G3_mat == 0) | (S.G3_por == 0)).astype(int)
# z-score theo môn (trên điểm hợp lệ), rồi trung bình qua các môn của học sinh
zm = (S.G3m_v - m.G3[m.G3 > 0].mean()) / m.G3[m.G3 > 0].std()
zp = (S.G3p_v - p.G3[p.G3 > 0].mean()) / p.G3[p.G3 > 0].std()
S["Zvalid"] = pd.concat([zm, zp], axis=1).mean(axis=1, skipna=True)         # chính: bỏ G3=0
S["Gvalid"] = S[["G3m_v", "G3p_v"]].mean(axis=1, skipna=True)                  # điểm thô trung bình
mz = (S.G3_mat - m.G3.mean()) / m.G3.std(); pz = (S.G3_por - p.G3.mean()) / p.G3.std()
S["Zall"] = pd.concat([mz, pz], axis=1).mean(axis=1, skipna=True)              # nhạy: giữ G3=0
S["alc_idx"] = (5 * S.Dalc + 2 * S.Walc) / 7                                     # chỉ số tuần (5 ngày thường + 2 cuối tuần)
S.to_csv(f"{OUT}/student_level.csv", index=False)

# ---------------------------------------------------------------- 4. Hàm thống kê
def cohen_d(x, y):
    nx, ny = len(x), len(y); sp = np.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
    return (x.mean() - y.mean()) / sp
def boot(fn, *arrs, B=2000):
    n = len(arrs[0]); out = []
    for _ in range(B):
        i = rng.integers(0, n, n); out.append(fn(*[a[i] for a in arrs]))
    return np.percentile(out, [2.5, 97.5])
def spear(df, x, y):
    d = df[[x, y]].dropna(); r, pv = stats.spearmanr(d[x], d[y])
    lo, hi = boot(lambda a, b: stats.spearmanr(a, b)[0], d[x].values, d[y].values)
    return dict(n=len(d), rho=r, ci_lo=lo, ci_hi=hi, p=pv)
def twogroup(df, x, y, cut):
    d = df[[x, y]].dropna(); hi = d[d[x] >= cut][y].values; lo = d[d[x] < cut][y].values
    dd = cohen_d(pd.Series(hi), pd.Series(lo)); a, b = boot(lambda u, v: cohen_d(pd.Series(u), pd.Series(v)), hi, lo, B=1500) if False else (np.nan, np.nan)
    bs = [cohen_d(pd.Series(rng.choice(hi, len(hi))), pd.Series(rng.choice(lo, len(lo)))) for _ in range(1500)]
    a, b = np.percentile(bs, [2.5, 97.5])
    return dict(n_thap=len(lo), n_cao=len(hi), tb_thap=lo.mean(), tb_cao=hi.mean(), chenh=hi.mean() - lo.mean(), d=dd, d_lo=a, d_hi=b,
                p_welch=stats.ttest_ind(hi, lo, equal_var=False)[1], p_mwu=stats.mannwhitneyu(hi, lo)[1])
def ols_hc3(df, y, xs):
    d = df[[y] + xs].dropna(); X = pd.get_dummies(d[xs], drop_first=True).astype(float); X.insert(0, "const", 1.0)
    Y = d[y].values; Xv = X.values; XtXi = np.linalg.inv(Xv.T @ Xv); b = XtXi @ Xv.T @ Y
    e = Y - Xv @ b; h = np.einsum("ij,jk,ik->i", Xv, XtXi, Xv)
    V = XtXi @ (Xv.T * (e / (1 - h)) ** 2) @ Xv @ XtXi; se = np.sqrt(np.diag(V))
    t = b / se; pv = 2 * stats.t.sf(abs(t), len(d) - len(b))
    return pd.DataFrame(dict(coef=b, se=se, lo=b - 1.96 * se, hi=b + 1.96 * se, p=pv), index=X.columns), len(d), 1 - e.var() / Y.var()

# ---------------------------------------------------------------- 5. Phân tích chính (cấp học sinh, G3=0 loại)
main = S[S.Zvalid.notna()]
print("\nPhân tích chính: n =", len(main))
res = []
for ex in ["Dalc", "Walc", "alc_idx"]:
    r = spear(main, ex, "Zvalid"); r["exposure"] = ex; res.append(r)
main_sp = pd.DataFrame(res); print(main_sp.round(4).to_string()); main_sp.to_csv(f"{OUT}/chinh_spearman.csv", index=False)

tg = []
for ex, cut, lab in [("Dalc", 2, "Dalc>=2 vs Dalc=1"), ("Walc", 3, "Walc>=3 vs Walc<=2"), ("Walc", 4, "Walc>=4 vs Walc<=3")]:
    r = twogroup(main, ex, "Zvalid", cut); r["so_sanh"] = lab; tg.append(r)
    r2 = twogroup(main, ex, "Gvalid", cut); r2["so_sanh"] = lab + " (điểm G3 thô)"; tg.append(r2)
tg = pd.DataFrame(tg); print(tg.round(4).to_string()); tg.to_csv(f"{OUT}/chinh_hai_nhom.csv", index=False)

# Kruskal-Wallis + eta^2 theo 5 mức
kw = []
for ex in ["Dalc", "Walc"]:
    d = main.assign(lv=main[ex].round().astype(int)); groups = [g.Zvalid.values for _, g in d.groupby("lv")]
    H, pv = stats.kruskal(*groups); k, n = len(groups), len(d); eta = (H - k + 1) / (n - k)
    kw.append(dict(exposure=ex, k=k, n=n, H=H, p=pv, eta2=eta))
kw = pd.DataFrame(kw); print(kw.round(4).to_string()); kw.to_csv(f"{OUT}/chinh_kruskal.csv", index=False)

lv = []
for ex in ["Dalc", "Walc"]:
    d = main.assign(lv=main[ex].round().astype(int))
    for l, g in d.groupby("lv"):
        s = g.Gvalid; lv.append(dict(exposure=ex, muc=l, n=len(g), G3_tb=s.mean(), G3_ci_lo=s.mean() - 1.96 * s.sem(), G3_ci_hi=s.mean() + 1.96 * s.sem(), z_tb=g.Zvalid.mean(), ti_le_G3_0=np.nan))
lv = pd.DataFrame(lv)
for ex in ["Dalc", "Walc"]:  # tỉ lệ G3=0 theo mức (toàn bộ học sinh)
    d = S.assign(lv=S[ex].round().astype(int))
    for l, g in d.groupby("lv"):
        lv.loc[(lv.exposure == ex) & (lv.muc == l), "ti_le_G3_0"] = g.zero_any.mean()
lv.to_csv(f"{OUT}/theo_muc.csv", index=False); print(lv.round(3).to_string())

# Hồi quy hiệu chỉnh
base = ["sex", "age", "school", "address", "Medu", "Fedu", "studytime", "goout"]
adj_rows = []
for name, xs, dfu in [("thô", [], main), ("hiệu chỉnh nền (giới, tuổi, trường, địa chỉ, học vấn bố mẹ, studytime, goout)", base, main),
                      ("+failures, absences", base + ["failures", "absences"], main)]:
    for ex in [["Dalc", "Walc"]]:
        co, n, r2 = ols_hc3(dfu, "Zvalid", ex + [x for x in xs])
        for v in ex:
            adj_rows.append(dict(mo_hinh=name, n=n, R2=r2, bien=v, **co.loc[v].to_dict()))
adj = pd.DataFrame(adj_rows); print(adj.round(4).to_string()); adj.to_csv(f"{OUT}/hoi_quy_hieu_chinh.csv", index=False)

# ---------------------------------------------------------------- 6. Nhạy cảm
sens = []
def add(name, df, y):
    for ex in ["Dalc", "Walc"]:
        r = spear(df, ex, y); r.update(spec=name, exposure=ex); sens.append(r)
add("Chính: cấp HS, bỏ G3=0", main, "Zvalid")
add("Giữ G3=0 (cấp HS)", S, "Zall")
# Toán / Bồ riêng (mỗi file vốn 1 dòng/HS)
mm_ = m.assign(Dalc=m.Dalc, Walc=m.Walc); pm_ = p
add("Chỉ Toán, bỏ G3=0", m[m.G3 > 0], "G3"); add("Chỉ Bồ Đào Nha, bỏ G3=0", p[p.G3 > 0], "G3")
add("Chỉ Toán, giữ G3=0", m, "G3"); add("Chỉ Bồ Đào Nha, giữ G3=0", p, "G3")
# Gộp 2 file ngây thơ (đếm đôi 382 HS)
naive = pd.concat([m.assign(c="m"), p.assign(c="p")]); add("Gộp dòng ngây thơ (đếm đôi), bỏ G3=0", naive[naive.G3 > 0], "G3")
add("Chỉ cặp khớp không mơ hồ + HS 1 môn", main[main.amb == 0], "Zvalid")
add("Chỉ HS ở cả 2 môn", main[main.both], "Zvalid")
sens = pd.DataFrame(sens)[["spec", "exposure", "n", "rho", "ci_lo", "ci_hi", "p"]]
print(sens.round(4).to_string()); sens.to_csv(f"{OUT}/nhay_cam.csv", index=False)

# G3=0 như kết cục nhị phân
zb = []
for ex in ["Dalc", "Walc"]:
    r = stats.spearmanr(S[ex], S.zero_any); zb.append(dict(exposure=ex, n=len(S), ti_le_zero=S.zero_any.mean(), rho=r[0], p=r[1]))
zb = pd.DataFrame(zb); print(zb.round(4).to_string()); zb.to_csv(f"{OUT}/g3_zero_va_ruou.csv", index=False)
# Holm trên 2 kiểm định chính (Dalc, Walc)
pv = main_sp.set_index("exposure").loc[["Dalc", "Walc"], "p"].sort_values(); holm = {k: min(1, v * (2 - i)) for i, (k, v) in enumerate(pv.items())}
print("Holm:", holm)

# ---------------------------------------------------------------- 7. Biểu đồ
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
for a, ex, lab in zip(ax, ["Dalc", "Walc"], ["Rượu ngày thường (Dalc)", "Rượu cuối tuần (Walc)"]):
    d = lv[lv.exposure == ex]
    a.errorbar(d.muc, d.G3_tb, yerr=[d.G3_tb - d.G3_ci_lo, d.G3_ci_hi - d.G3_tb], fmt="o-", color="#1f77b4", capsize=4)
    for x, y, n in zip(d.muc, d.G3_ci_hi, d.n): a.annotate(f"n={n}", (x, y), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=9, color="#555")
    r = main_sp.set_index("exposure").loc[ex]
    a.set_xlabel(f"{lab}: 1 = rất thấp … 5 = rất cao"); a.set_title(f"Spearman ρ = {r.rho:.2f} (KTC95% {r.ci_lo:.2f}…{r.ci_hi:.2f}), p = {r.p:.3g}", fontsize=10)
    a.set_xticks([1, 2, 3, 4, 5])
ax[0].set_ylabel("G3 trung bình / học sinh (thang 0-20, bỏ G3=0)")
fig.suptitle("Uống nhiều hơn đi kèm điểm G3 thấp hơn nhẹ; mối liên hệ yếu (|ρ| ≈ 0,1)", fontweight="bold")
fig.tight_layout(); fig.savefig(f"{OUT}/g3_theo_muc_ruou.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5.6))
sp = sens.copy(); sp["y"] = np.arange(len(sp))[::-1]
for ex, col, off in [("Dalc", "#d62728", 0.15), ("Walc", "#1f77b4", -0.15)]:
    d = sp[sp.exposure == ex]
    ax.errorbar(d.rho, d.y + off, xerr=[d.rho - d.ci_lo, d.ci_hi - d.rho], fmt="o", color=col, capsize=3, label={"Dalc": "Ngày thường (Dalc)", "Walc": "Cuối tuần (Walc)"}[ex])
specs = sp[sp.exposure == "Dalc"].sort_values("y")
ax.set_yticks(specs.y); ax.set_yticklabels(specs.spec, fontsize=9); ax.axvline(0, color="k", lw=.8)
ax.set_xlabel("Hệ số Spearman ρ với G3 (KTC 95% bootstrap)"); ax.legend(loc="lower left")
ax.set_title("Kết luận bền vững: ρ âm nhỏ ở mọi cách xử lý trùng lặp và G3=0", fontweight="bold", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/do_ben_vung.png", dpi=150); plt.close(fig)
print("xong")
