"""Cảnh báo sớm OULAD, mốc quyết định cuối ngày 28.

Chạy từ thư mục workspace:  python -I outputs/canh_bao_som_d28/analysis.py
Quy ước:
- Nhãn y = target_noncompletion (1 = Fail hoặc Withdrawn; 0 = Pass/Distinction).
- Tuần k = ngày 7(k-1) .. 7k-1; clicks_0_28 gồm cả ngày 28.
- Đặc trưng mô hình chỉ dùng dữ liệu đến ngày 28 (và hồ sơ đăng ký lúc đầu khóa).
  Không dùng giới tính, khuyết tật, vùng, IMD, độ tuổi trong mô hình chính.
- Phân chia train / validation / test lấy từ cột split có sẵn.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(WS, "data")
K = ["code_module", "code_presentation", "id_student"]
MODULE_PRES = ["code_module", "code_presentation"]
RES = {}  # gom số liệu chính để viết answer.md


def holm(p):
    p = np.asarray(p, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(running, 1.0)
    return adj


# ---------------------------------------------------------------- nạp dữ liệu
aq1 = pd.read_csv(os.path.join(DATA, "aq1_student_week.csv"))
aq2 = pd.read_csv(os.path.join(DATA, "aq2_diagnostic_table.csv"))
aq3m = pd.read_csv(os.path.join(DATA, "aq3_model_table.csv"))
params = json.load(open(os.path.join(DATA, "aq4_decision_params.json"), encoding="utf-8"))

chk = aq2.merge(aq3m[K + ["target_noncompletion", "split"]], on=K, suffixes=("", "_m"))
assert len(chk) == len(aq2) == len(aq3m), "khóa không khớp"
assert (chk.target_noncompletion == chk.target_noncompletion_m).all()
assert (chk.split == chk.split_m).all()
assert not aq2.duplicated(K).any()

df = aq2.copy()
df["y"] = df["target_noncompletion"].astype(int)
df["label3"] = df["label3"]
df["tma1_score_missing"] = df.tma1_score.isna().astype(int)
df["tma1_deadline_missing"] = df.tma1_days_before_deadline.isna().astype(int)
for k in range(1, 5):
    df[f"tich_luy_clicks_den_tuan{k}"] = df[[f"clicks_w{j}" for j in range(1, k + 1)]].sum(axis=1)
    df[f"tich_luy_ngay_hd_den_tuan{k}"] = df[[f"active_days_w{j}" for j in range(1, k + 1)]].sum(axis=1)
df["clicks_4tuan"] = df["tich_luy_clicks_den_tuan4"]
df["ngay_hd_4tuan"] = df["tich_luy_ngay_hd_den_tuan4"]

RES["n_total"] = len(df)
RES["base_rate"] = df.y.mean()
RES["n_by_label3"] = df.label3.value_counts().to_dict()
RES["n_by_split"] = df.split.value_counts().to_dict()
RES["n_by_mp"] = {f"{a} {b}": int(n) for (a, b), n in df.groupby(MODULE_PRES).size().items()}

# ---------------------------------------------------------------- Câu 1
G3 = ["Pass", "Fail", "Withdrawn"]
ind1 = [f"clicks_w{k}" for k in range(1, 5)] + [f"active_days_w{k}" for k in range(1, 5)] + ["clicks_4tuan", "ngay_hd_4tuan"]
rows, pair_rows = [], []
for c in ind1:
    arrs = {g: df.loc[df.label3 == g, c] for g in G3}
    H, p = stats.kruskal(*arrs.values())
    n, k = len(df), 3
    row = {"chi_bao": c, "KW_H": H, "p_KW": p, "eta2": (H - k + 1) / (n - k)}
    for g in G3:
        row[f"trung_vi_{g}"] = arrs[g].median()
        row[f"tb_{g}"] = arrs[g].mean()
        row[f"ti_le_bang_0_{g}"] = (arrs[g] == 0).mean()
    rows.append(row)
    for a, b in [("Fail", "Pass"), ("Withdrawn", "Pass"), ("Withdrawn", "Fail")]:
        U, pu = stats.mannwhitneyu(arrs[a], arrs[b], alternative="two-sided")
        pair_rows.append({"chi_bao": c, "so_sanh": f"{a} vs {b}", "p_raw": pu,
                          "P(a>b)": U / (len(arrs[a]) * len(arrs[b]))})
q1_kw = pd.DataFrame(rows)
q1_kw["p_KW_holm"] = holm(q1_kw.p_KW)
q1_pair = pd.DataFrame(pair_rows)
q1_pair["p_holm"] = holm(q1_pair.p_raw)
q1_kw.to_csv(os.path.join(HERE, "cau1_so_sanh_3_nhom.csv"), index=False)
q1_pair.to_csv(os.path.join(HERE, "cau1_cap_nhom.csv"), index=False)
weekly_grp = pd.DataFrame({
    f"{m}_tuan{k}_{g}": df.loc[df.label3 == g, f"{m}_w{k}"].median()
    for g in G3 for m in ["clicks", "active_days"] for k in range(1, 5)
}, index=[0]).T.rename(columns={0: "trung_vi"})
weekly_grp.to_csv(os.path.join(HERE, "cau1_trung_vi_theo_tuan.csv"))
RES["q1_kw"] = q1_kw[["chi_bao", "KW_H", "p_KW_holm", "eta2"] + [c for c in q1_kw.columns if c.startswith("trung_vi_")]].round(4).to_dict("records")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, m, title in [(axes[0], "clicks", "Số lượt nhấp trung vị mỗi tuần"),
                     (axes[1], "active_days", "Số ngày hoạt động trung vị mỗi tuần")]:
    for g, col in zip(G3, ["#2a9d8f", "#e9c46a", "#e76f51"]):
        vals = [df.loc[df.label3 == g, f"{m}_w{k}"].median() for k in range(1, 5)]
        ax.plot(range(1, 5), vals, marker="o", label=g, color=col, lw=2)
    ax.set_xticks(range(1, 5))
    ax.set_xticklabels([f"Tuần {k}" for k in range(1, 5)])
    ax.set_title(title)
    ax.grid(alpha=0.3)
axes[0].set_ylabel("Lượt nhấp")
axes[1].set_ylabel("Số ngày")
axes[1].legend(title="Kết quả")
fig.suptitle("Tương tác 4 tuần đầu theo nhóm kết quả (Pass / Fail / Withdrawn)")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "cau1_tuong_tac_4_tuan.png"), dpi=140)
plt.close(fig)

# ---------------------------------------------------------------- Câu 2
y = df.y
cand = []
for k in range(1, 5):
    cand += [f"clicks_w{k}", f"active_days_w{k}", f"tich_luy_clicks_den_tuan{k}", f"tich_luy_ngay_hd_den_tuan{k}"]
cand += ["days_since_last_active_d28", "n_sites_0_28", "no_vle_activity_0_28", "clicks_pre_start",
         "active_days_pre_start", "clicks_homepage_0_28", "clicks_oucontent_0_28", "clicks_resource_0_28",
         "clicks_subpage_0_28", "clicks_forumng_0_28", "clicks_quiz_0_28", "clicks_url_0_28",
         "tma1_score", "tma1_days_before_deadline", "num_of_prev_attempts", "studied_credits",
         "highest_education_ord", "registration_lead_days", "clicks_change_w1_w4"]
binary = ["tma1_submitted_by_d28", "tma1_on_time"]
rows = []
for c in cand:
    x = df[c]
    m = x.notna()
    xx, yy = x[m], y[m]
    a0, a1 = xx[yy == 0], xx[yy == 1]
    U, p = stats.mannwhitneyu(a1, a0, alternative="two-sided")
    direction = 1 if a1.median() > a0.median() else -1
    auc_rủi_ro = roc_auc_score(yy, direction * xx)
    rows.append({"chi_bao": c, "loai": "liên tục", "trung_vi_hoan_thanh": a0.median(),
                 "trung_vi_khong_hoan_thanh": a1.median(), "p_raw": p,
                 "AUC_don_bien_theo_huong_rui_ro": auc_rủi_ro,
                 "huong": "cao hơn = rủi ro" if direction > 0 else "thấp hơn = rủi ro"})
for c in binary:
    tab = pd.crosstab(df[c], df.y)
    chi2, p, _, _ = stats.chi2_contingency(tab)
    p0 = df.loc[df.y == 0, c].mean()
    p1 = df.loc[df.y == 1, c].mean()
    rows.append({"chi_bao": c, "loai": "nhị phân (tỉ lệ)", "trung_vi_hoan_thanh": p0,
                 "trung_vi_khong_hoan_thanh": p1, "p_raw": p,
                 "AUC_don_bien_theo_huong_rui_ro": np.nan,
                 "huong": "tỉ lệ 1 (hoàn thành / không)"})
q2 = pd.DataFrame(rows)
q2["p_holm"] = holm(q2.p_raw)
q2["co_y_nghia_holm_5pct"] = q2.p_holm < 0.05
q2 = q2.sort_values("AUC_don_bien_theo_huong_rui_ro", ascending=False, na_position="last")
q2.to_csv(os.path.join(HERE, "cau2_chi_bao_hoan_thanh_vs_khong.csv"), index=False)
RES["q2_sig"] = q2[q2.co_y_nghia_holm_5pct][["chi_bao", "trung_vi_hoan_thanh", "trung_vi_khong_hoan_thanh",
                                                 "AUC_don_bien_theo_huong_rui_ro", "p_holm"]].round(4).to_dict("records")
RES["q2_nonsig"] = q2[~q2.co_y_nghia_holm_5pct].chi_bao.tolist()

# từ tuần nào: AUC theo tuần cho lượt nhấp và ngày hoạt động (theo tuần & tích lũy)
week_rows = []
q2i = q2.set_index("chi_bao")
for k in range(1, 5):
    for lab, c in [("lượt nhấp trong tuần", f"clicks_w{k}"), ("ngày hoạt động trong tuần", f"active_days_w{k}"),
                   ("lượt nhấp tích lũy đến tuần", f"tich_luy_clicks_den_tuan{k}"),
                   ("ngày hoạt động tích lũy đến tuần", f"tich_luy_ngay_hd_den_tuan{k}")]:
        r = q2i.loc[c]
        week_rows.append({"tuan": k, "chi_bao": lab, "cot_goc": c,
                          "AUC_don_bien_theo_huong_rui_ro": r.AUC_don_bien_theo_huong_rui_ro,
                          "p_holm": r.p_holm, "co_y_nghia_holm_5pct": bool(r.co_y_nghia_holm_5pct)})
q2_week = pd.DataFrame(week_rows)
q2_week.to_csv(os.path.join(HERE, "cau2_auc_theo_tuan.csv"), index=False)
RES["q2_week"] = q2_week.round(4).to_dict("records")

fig, ax = plt.subplots(figsize=(8.5, 4.6))
series = [("clicks_w{k}", "Lượt nhấp trong tuần", "#2a9d8f", "-"),
          ("active_days_w{k}", "Số ngày hoạt động trong tuần", "#264653", "--"),
          ("tich_luy_clicks_den_tuan{k}", "Lượt nhấp tích lũy đến tuần", "#e76f51", "-"),
          ("tich_luy_ngay_hd_den_tuan{k}", "Ngày hoạt động tích lũy đến tuần", "#e9c46a", "--")]
for pat, lab, col, ls in series:
    vals, sig = [], []
    for k in range(1, 5):
        c = pat.format(k=k)
        r = q2.set_index("chi_bao").loc[c]
        vals.append(r.AUC_don_bien_theo_huong_rui_ro)
        sig.append(bool(r.co_y_nghia_holm_5pct))
    ax.plot(range(1, 5), vals, marker="o", color=col, ls=ls, label=lab, lw=2)
    for xk, v, s in zip(range(1, 5), vals, sig):
        if s:
            ax.scatter([xk], [v], s=160, facecolors="none", edgecolors=col, lw=1.2)
ax.axhline(0.5, color="grey", lw=1, ls=":")
ax.set_xticks(range(1, 5))
ax.set_xticklabels([f"Tuần {k}" for k in range(1, 5)])
ax.set_ylabel("AUC đơn biến (0,5 = không phân biệt)")
ax.set_title("Chỉ báo hoạt động phân biệt Hoàn thành / Không hoàn thành từ tuần nào\n(vòng tròn = có ý nghĩa sau hiệu chỉnh Holm 5%)")
ax.legend(fontsize=8, loc="lower right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "cau2_khac_biet_theo_tuan.png"), dpi=140)
plt.close(fig)

# ---------------------------------------------------------------- Câu 3
FEATS = [
    "clicks_w1", "clicks_w2", "clicks_w3", "clicks_w4",
    "active_days_w1", "active_days_w2", "active_days_w3", "active_days_w4",
    "clicks_0_28", "active_days_0_28", "n_sites_0_28",
    "days_since_last_active_d28", "clicks_pre_start", "active_days_pre_start", "no_vle_activity_0_28",
    "tma1_submitted_by_d28", "tma1_score",
    "num_of_prev_attempts", "studied_credits", "highest_education_ord", "registration_lead_days",
]
# Đã bỏ: đếm lượt nhấp theo loại (cộng tuyến với clicks_0_28), cờ thiếu TMA1 và tma1_on_time /
# tma1_days_before_deadline (trùng với tma1_submitted_by_d28 — đều là "chưa nộp" khi thiếu).
RES["n_features"] = len(FEATS)
tr = df.split == "train"
va = df.split == "validation"
te = df.split == "test"
med = df.loc[tr, FEATS].median()
X = df[FEATS].fillna(med)
scaler = StandardScaler().fit(X[tr])
Xs = pd.DataFrame(scaler.transform(X), columns=FEATS, index=X.index)


def fit_model(name, Xtr, ytr):
    if name == "logistic":
        return LogisticRegression(C=1.0, max_iter=5000).fit(Xtr, ytr)
    return HistGradientBoostingClassifier(max_iter=400, learning_rate=0.03, max_leaf_nodes=15,
                                          min_samples_leaf=40, l2_regularization=1.0,
                                          random_state=0).fit(Xtr, ytr)


def score(name, model, idx):
    Xi = Xs.loc[idx] if name == "logistic" else X.loc[idx]
    return model.predict_proba(Xi)[:, 1]


models, val_rows = {}, []
for name in ["logistic", "hist_gbm"]:
    mdl = fit_model(name, Xs[tr] if name == "logistic" else X[tr], y[tr])
    models[name] = mdl
    p = score(name, mdl, df.index[va])
    val_rows.append({"mo_hinh": name, "AUC_validation": roc_auc_score(y[va], p),
                     "PR_AUC_validation": average_precision_score(y[va], p)})
base_val = -df.loc[va, "clicks_0_28"]
val_rows.append({"mo_hinh": "baseline: ít lượt nhấp đến ngày 28",
                 "AUC_validation": roc_auc_score(y[va], base_val),
                 "PR_AUC_validation": average_precision_score(y[va], base_val)})
val_tbl = pd.DataFrame(val_rows)
val_tbl.to_csv(os.path.join(HERE, "cau3_so_sanh_mo_hinh_validation.csv"), index=False)
RES["val_models"] = val_tbl.round(4).to_dict("records")

auc_lr = val_tbl.set_index("mo_hinh").loc["logistic", "AUC_validation"]
auc_gb = val_tbl.set_index("mo_hinh").loc["hist_gbm", "AUC_validation"]
# Chọn GBM chỉ khi vượt logistic ít nhất 0,01 AUC; nếu không, dùng logistic (dễ giải thích)
chosen = "hist_gbm" if auc_gb - auc_lr >= 0.01 else "logistic"
RES["chosen_model"] = chosen
mdl = models[chosen]

# ngưỡng: điểm cắt lớn nhất trên validation đạt recall >= 0.70
p_va = score(chosen, mdl, df.index[va])
target_recall = 0.70
grid = np.unique(np.quantile(p_va, np.linspace(0, 1, 4001)))
best_thr, best_rec = None, -1
for t in sorted(grid, reverse=True):
    rec = ((p_va >= t) & (y[va].values == 1)).sum() / y[va].sum()
    if rec >= target_recall:
        best_thr = t
        best_rec = rec
        break
if best_thr is None:
    best_thr = grid.min()
RES["threshold"] = float(best_thr)

p_te = score(chosen, mdl, df.index[te])
yt = y[te].values
pred = (p_te >= best_thr).astype(int)
tn, fp, fn, tp = confusion_matrix(yt, pred).ravel()
test_metrics = {
    "mo_hinh": chosen,
    "AUC_test": roc_auc_score(yt, p_te),
    "PR_AUC_test": average_precision_score(yt, p_te),
    "n_test": int(len(yt)),
    "ti_le_khong_hoan_thanh_test": yt.mean(),
    "recall_test": tp / (tp + fn),
    "precision_test": tp / (tp + fp),
    "ti_le_bi_gan_co": pred.mean(),
    "so_bat_duoc": int(tp),
    "tong_khong_hoan_thanh": int(tp + fn),
    "so_gan_co_khong_hoan_thanh": int(fp),
    "so_bo_sot": int(fn),
    "nguong": float(best_thr),
}
RES["test"] = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in test_metrics.items()}
pd.DataFrame([test_metrics]).to_csv(os.path.join(HERE, "cau3_ket_qua_test.csv"), index=False)

# đường cong recall theo tỉ lệ được gắn cờ (trên test)
order = np.argsort(-p_te)
cum_hit = np.cumsum(yt[order])
share = np.arange(1, len(yt) + 1) / len(yt)
recall_curve = cum_hit / yt.sum()
k70 = int(np.argmax(recall_curve >= 0.70)) + 1
RES["test_share_for_recall70"] = float(k70 / len(yt))
RES["test_precision_at_recall70"] = float(cum_hit[k70 - 1] / k70)
curve = pd.DataFrame({"ti_le_gan_co": share, "recall": recall_curve,
                      "precision": cum_hit / np.arange(1, len(yt) + 1)})
curve.iloc[::20].to_csv(os.path.join(HERE, "cau3_duong_cong_recall_test.csv"), index=False)

fig, ax = plt.subplots(figsize=(8, 4.6))
ax.plot(share * 100, recall_curve * 100, color="#264653", lw=2, label="Recall (tỉ lệ không hoàn thành được bắt)")
ax.plot(share * 100, cum_hit / np.arange(1, len(yt) + 1) * 100, color="#e76f51", lw=2,
        label="Precision (tỉ lệ bị gắn cờ thực sự không hoàn thành)")
ax.axhline(70, color="grey", ls=":", lw=1)
ax.axvline(k70 / len(yt) * 100, color="grey", ls=":", lw=1)
ax.text(k70 / len(yt) * 100 + 1, 5, f"70% recall cần gắn cờ {k70 / len(yt) * 100:.0f}% sinh viên", fontsize=9)
ax.set_xlabel("Tỉ lệ sinh viên được gắn cờ rủi ro (%) — xếp theo điểm rủi ro")
ax.set_ylabel("%")
ax.set_title(f"Dự báo dùng dữ liệu đến ngày 28 — tập test (AUC = {test_metrics['AUC_test']:.2f})")
ax.legend(fontsize=8, loc="center right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "cau3_recall_theo_ti_le_gan_co.png"), dpi=140)
plt.close(fig)

# ---------------------------------------------------------------- Câu 4
# Điểm rủi ro ngoài mẫu (5-fold, phân tầng theo nhãn) cho toàn bộ 13.020 sinh viên
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
risk = np.zeros(len(df))
for tr_i, te_i in skf.split(X, y):
    tr_idx = df.index[tr_i]
    te_idx = df.index[te_i]
    if chosen == "logistic":
        sc = StandardScaler().fit(X.loc[tr_idx])
        m_ = LogisticRegression(C=1.0, max_iter=5000).fit(sc.transform(X.loc[tr_idx]), y[tr_idx])
        risk[te_i] = m_.predict_proba(sc.transform(X.loc[te_idx]))[:, 1]
    else:
        m_ = fit_model("hist_gbm", X.loc[tr_idx], y[tr_idx])
        risk[te_i] = m_.predict_proba(X.loc[te_idx])[:, 1]
df["risk_oof"] = risk
RES["oof_auc"] = float(roc_auc_score(y, risk))

CAP = int(params["default_k"])
rank_rows, prio = [], []
for (mod, pres), g in df.groupby(MODULE_PRES):
    g = g.sort_values("risk_oof", ascending=False)
    top = g.head(CAP)
    total_nc = int(g.y.sum())
    hits = int(top.y.sum())
    cum = np.cumsum(g.y.values)
    need = 0.70 * total_nc
    k70_mp = int(np.argmax(cum >= need)) + 1
    rank_rows.append({
        "module": mod, "presentation": pres, "so_sv": len(g), "so_khong_hoan_thanh": total_nc,
        "ti_le_khong_hoan_thanh": total_nc / len(g), "cap_lien_he": CAP, "trung_trong_danh_sach": hits,
        "precision_trong_danh_sach": hits / CAP, "recall_trong_danh_sach": hits / total_nc,
        "so_sv_can_gan_co_de_bat_70pct": k70_mp,
        "ti_le_cohort_can_gan_co_70pct": k70_mp / len(g),
    })
    top = top.assign(thu_tu=range(1, len(top) + 1), module=mod, presentation=pres)
    prio.append(top)
rank_tbl = pd.DataFrame(rank_rows)
prio_df = pd.concat(prio)
rank_tbl.to_csv(os.path.join(HERE, "cau4_hieu_qua_danh_sach_200.csv"), index=False)
RES["q4"] = rank_tbl.round(4).to_dict("records")
RES["q4_total"] = {
    "so_sv_trong_danh_sach": int(len(prio_df)),
    "trung": int(prio_df.y.sum()),
    "tong_khong_hoan_thanh": int(df.y.sum()),
    "recall": float(prio_df.y.sum() / df.y.sum()),
    "precision": float(prio_df.y.mean()),
}

fig, ax = plt.subplots(figsize=(9, 4.6))
labels = [f"{m}\n{p}" for m, p in zip(rank_tbl.module, rank_tbl.presentation)]
xx = np.arange(len(rank_tbl))
ax.bar(xx, rank_tbl.trung_trong_danh_sach, color="#2a9d8f", label="Không hoàn thành trong danh sách 200")
ax.bar(xx, rank_tbl.so_khong_hoan_thanh - rank_tbl.trung_trong_danh_sach, bottom=rank_tbl.trung_trong_danh_sach,
       color="#e9c46a", label="Không hoàn thành ngoài danh sách")
for i, r in rank_tbl.reset_index(drop=True).iterrows():
    ax.text(i, r.so_khong_hoan_thanh + 8, f"{r.recall_trong_danh_sach * 100:.0f}%", ha="center", fontsize=8)
ax.set_xticks(xx)
ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel("Số sinh viên không hoàn thành")
ax.set_title("Danh sách 200 sinh viên mỗi module-kỳ: bắt được bao nhiêu trên tổng số không hoàn thành")
ax.legend(fontsize=8, loc="upper right")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "cau4_trung_theo_module_ky.png"), dpi=140)
plt.close(fig)

# ---------------------------------------------------------------- Câu 5
# Đóng góp theo log-odds = hệ số × (giá trị chuẩn hóa), từ logistic fit trên toàn bộ dữ liệu.
# Dùng cùng bộ đặc trưng; chỉ để giải thích, điểm xếp hạng vẫn là điểm ngoài mẫu.
sc_all = StandardScaler().fit(X)
Z = pd.DataFrame(sc_all.transform(X), columns=FEATS, index=X.index)
lr_exp = LogisticRegression(C=1.0, max_iter=5000).fit(Z, y)
coef = pd.Series(lr_exp.coef_[0], index=FEATS)
RES["coef_top"] = coef.sort_values(key=abs, ascending=False).head(10).round(3).to_dict()
contrib = Z.mul(coef, axis=1)
RES["corr_oof_vs_lr_full"] = float(np.corrcoef(df.risk_oof, lr_exp.predict_proba(Z)[:, 1])[0, 1])

LABEL = {
    "clicks_w1": "số lượt nhấp tuần 1", "clicks_w2": "số lượt nhấp tuần 2",
    "clicks_w3": "số lượt nhấp tuần 3", "clicks_w4": "số lượt nhấp tuần 4",
    "active_days_w1": "số ngày hoạt động tuần 1", "active_days_w2": "số ngày hoạt động tuần 2",
    "active_days_w3": "số ngày hoạt động tuần 3", "active_days_w4": "số ngày hoạt động tuần 4",
    "clicks_0_28": "tổng lượt nhấp đến ngày 28", "active_days_0_28": "tổng số ngày hoạt động đến ngày 28",
    "n_sites_0_28": "số loại học liệu đã truy cập", "clicks_change_w1_w4": "xu hướng lượt nhấp từ tuần 1 đến tuần 4",
    "days_since_last_active_d28": "số ngày kể từ lần hoạt động cuối",
    "clicks_pre_start": "lượt nhấp trước khai giảng", "active_days_pre_start": "số ngày hoạt động trước khai giảng",
    "no_vle_activity_0_28": "số ngày không có hoạt động trên hệ thống học trực tuyến",
    "clicks_homepage_0_28": "lượt nhấp trang chủ khóa học", "clicks_oucontent_0_28": "lượt nhấp nội dung khóa học",
    "clicks_resource_0_28": "lượt nhấp tài liệu học", "clicks_subpage_0_28": "lượt nhấp trang con",
    "clicks_forumng_0_28": "lượt nhấp diễn đàn thảo luận", "clicks_quiz_0_28": "lượt nhấp bài trắc nghiệm",
    "clicks_url_0_28": "lượt nhấp liên kết ngoài",
    "tma1_days_before_deadline": "số ngày nộp TMA1 trước hạn", "tma1_score": "điểm TMA1",
    "num_of_prev_attempts": "số lần học lại trước đó", "studied_credits": "số tín chỉ đang theo học",
    "highest_education_ord": "trình độ học vấn trước khi vào khóa", "registration_lead_days": "số ngày đăng ký trước khai giảng",
}
BIN = {
    "tma1_submitted_by_d28": ("đã nộp TMA1 đến ngày 28", "chưa nộp TMA1 đến ngày 28"),
    "tma1_on_time": ("nộp TMA1 đúng hạn", "chưa nộp TMA1 đúng hạn"),
    "tma1_score_missing": ("chưa có điểm TMA1", "đã có điểm TMA1"),
    "tma1_deadline_missing": ("thiếu thông tin hạn nộp TMA1", "có thông tin hạn nộp TMA1"),
}
ENGAGE = {"clicks", "active_days", "n_sites", "days_since", "no_vle", "clicks_"}


def phrase(f, i):
    v = X.loc[i, f]
    z = Z.loc[i, f]
    if f in BIN:
        return BIN[f][0] if v == 1 else BIN[f][1]
    lab = LABEL.get(f, f)
    return f"{lab} {'thấp' if z < 0 else 'cao'} hơn mức trung bình"


def advice(f):
    if f.startswith("tma1"):
        return "hỗ trợ lập kế hoạch nộp bài đánh giá TMA1 đúng hạn"
    if f.startswith(("num_of", "studied", "highest", "registration")):
        return "xem lại khối lượng học và hỗ trợ kỹ năng nền trước khi học"
    return "trao đổi về nhịp học và cách sử dụng tài liệu, diễn đàn trên hệ thống học trực tuyến"


explain_rows = []
raw_missing = df[FEATS].isna()  # giá trị đã điền median: không dùng để nói về sinh viên
for idx, r in prio_df.iterrows():
    c = contrib.loc[idx].copy()
    c = c[~raw_missing.loc[idx]]
    top = c.sort_values(ascending=False).head(3)
    top = top[top > 0]
    if len(top) == 0:
        top = c.sort_values(ascending=False).head(2)
    f1 = top.index[0]
    parts = [phrase(f, idx) for f in top.index[:2]]
    s1 = (f"Sinh viên {r.id_student} ({r.code_module} {r.code_presentation}) nằm trong nhóm {CAP} "
          f"sinh viên có điểm rủi ro cao nhất của module-kỳ này.")
    s2 = f"Yếu tố đóng góp nhiều nhất là {parts[0]}" + (f", tiếp theo là {parts[1]}." if len(parts) > 1 else ".")
    s3 = f"Cố vấn nên {advice(f1)}."
    row = {"code_module": r.code_module, "code_presentation": r.code_presentation, "id_student": r.id_student,
           "thu_tu": r.thu_tu, "risk_oof": round(r.risk_oof, 4), "nhan_thuc_te": r.label3,
           "dac_trung_1": f1, "dac_trung_1_dong_gop_logodds": round(top.iloc[0], 3)}
    if len(top) > 1:
        row["dac_trung_2"] = top.index[1]
    row["giai_thich_cho_co_van"] = " ".join([s1, s2, s3])
    explain_rows.append(row)
exp_df = pd.DataFrame(explain_rows)
exp_df.to_csv(os.path.join(HERE, "cau5_giai_thich_tung_sinh_vien.csv"), index=False)

top1_counts = exp_df.dac_trung_1.map(lambda f: LABEL.get(f, f)).value_counts()
top1_counts.to_csv(os.path.join(HERE, "cau5_dac_trung_hang_dau.csv"), header=["so_sv"])
RES["q5_top1"] = top1_counts.head(10).to_dict()
RES["q5_top1_by_group"] = {f"{a} {b}": s.map(lambda f: LABEL.get(f, f)).value_counts().index[0]
                           for (a, b), s in exp_df.groupby(["code_module", "code_presentation"]).dac_trung_1}
RES["q5_sample"] = exp_df.head(3).giai_thich_cho_co_van.tolist()
RES["q5_top1_fail_rate"] = exp_df.groupby("dac_trung_1").nhan_thuc_te.apply(
    lambda s: (s != "Pass").mean()).round(3).to_dict()

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, ensure_ascii=False, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps(RES, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))[:20000])
