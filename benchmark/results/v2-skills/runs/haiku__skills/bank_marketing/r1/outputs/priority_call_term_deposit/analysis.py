"""Dự đoán khách hàng có đăng ký tiền gửi có kỳ hạn trước khi gọi điện.

Dữ liệu chính: data/bank-additional/bank-additional-full.csv (41.188 dòng, 21 cột, đầy đủ nhất).
Kiểm tra độ bền: data/bank-full.csv (45.211 dòng, không có chỉ số kinh tế vĩ mô).

Nguyên tắc:
- Thời điểm dự đoán = trước cuộc gọi. Loại `duration` (chỉ biết sau khi gọi) và
  `campaign` (số lần gọi trong chiến dịch, gồm cả cuộc gọi hiện tại) khỏi mô hình chính.
- Dữ liệu sắp xếp theo thời gian (theo tài liệu UCI) -> chia theo thứ tự thời gian:
  70% đầu train, 15% kế validation (chọn mô hình), 15% cuối test (chạm một lần).
- `age` và `marital` là thuộc tính cá nhân nhạy cảm: không dùng làm đầu vào; chỉ dùng để kiểm tra lỗi theo nhóm tuổi.
"""
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 0
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- dữ liệu
ADD = pd.read_csv(ROOT / "data/bank-additional/bank-additional-full.csv", sep=";")
FULL = pd.read_csv(ROOT / "data/bank-full.csv", sep=";")


def prep(d, kind):
    d = d.copy()
    contacted = (d["pdays"] != 999) if kind == "add" else (d["pdays"] != -1)
    d["pdays_contacted"] = contacted.astype(int)
    d["pdays_clean"] = d["pdays"].where(contacted, 0)
    d["target"] = (d["y"] == "yes").astype(int)
    return d


ADD = prep(ADD, "add")
FULL = prep(FULL, "full")

ADD_CAT = ["job", "education", "default", "housing", "loan", "contact", "month", "day_of_week", "poutcome"]
ADD_NUM = ["previous", "pdays_contacted", "pdays_clean"]
MACRO = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
FULL_CAT = ["job", "education", "default", "housing", "loan", "contact", "month", "poutcome"]
FULL_NUM = ["balance", "day", "previous", "pdays_contacted", "pdays_clean"]


def split(d):
    n = len(d)
    i1, i2 = int(0.70 * n), int(0.85 * n)
    return d.iloc[:i1].copy(), d.iloc[i1:i2].copy(), d.iloc[i2:].copy()


TR, VA, TE = split(ADD)
FTR, FVA, FTE = split(FULL)


# ---------------------------------------------------------------- mô hình
def make_pre(cat, num):
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
        ("num", StandardScaler(), num),
    ])


def lr_model(cat, num, C=1.0):
    return make_pipeline(make_pre(cat, num), LogisticRegression(C=C, max_iter=5000))


def hgb_model(cat, num, lr=0.05, leaves=31):
    return make_pipeline(
        make_pre(cat, num),
        HistGradientBoostingClassifier(
            learning_rate=lr, max_leaf_nodes=leaves, min_samples_leaf=50,
            l2_regularization=1.0, max_iter=500, early_stopping=True,
            validation_fraction=0.1, n_iter_no_change=20, random_state=SEED),
    )


# ---------------------------------------------------------------- chỉ số
def topk(y, s, ks=(0.05, 0.10, 0.20, 0.30)):
    order = np.argsort(-s, kind="stable")
    ys = y[order]
    P, base = y.sum(), y.mean()
    rows = []
    for k in ks:
        m = int(round(k * len(y)))
        tp = int(ys[:m].sum())
        rows.append({"top_pct": k, "so_khach_goi": m, "so_dang_ky_bat_duoc": tp,
                     "ty_le_dang_ky": tp / m, "recall": tp / P, "lift": (tp / m) / base})
    return rows


def metrics(y, s):
    t = {r["top_pct"]: r for r in topk(y, s)}
    return {
        "roc_auc": roc_auc_score(y, s),
        "pr_auc": average_precision_score(y, s),
        "brier": brier_score_loss(y, np.clip(s, 0, 1)),
        "precision_top20": t[0.20]["ty_le_dang_ky"],
        "recall_top20": t[0.20]["recall"],
        "lift_top20": t[0.20]["lift"],
    }


def gains(y, s):
    order = np.argsort(-s, kind="stable")
    cum = np.cumsum(y[order]) / y.sum()
    x = np.arange(1, len(y) + 1) / len(y)
    return x, cum


# ---------------------------------------------------------------- 1) EDA nhanh
eda = {
    "so_dong": len(ADD), "so_cot": ADD.shape[1] - 2,
    "ty_le_dang_ky": ADD.target.mean(), "so_dong_trung_lap": int(ADD.duplicated().sum()),
    "ty_le_pdays_999": (ADD.pdays == 999).mean(),
    "ty_le_dang_ky_train": TR.target.mean(), "ty_le_dang_ky_valid": VA.target.mean(),
    "ty_le_dang_ky_test": TE.target.mean(),
}
rates = []
for col in ["poutcome", "contact", "month"]:
    g = ADD.groupby(col)["target"].agg(["size", "mean"]).reset_index()
    g.columns = ["gia_tri", "so_khach", "ty_le_dang_ky"]
    g.insert(0, "bien", col)
    rates.append(g)
pd.concat(rates).to_csv(HERE / "ty_le_dang_ky_theo_bien.csv", index=False)

# tỷ lệ đăng ký theo từng phần thời gian (10 khối theo thứ tự dòng) - để thấy trôi dạt
blk = ADD.assign(khoi=np.arange(len(ADD)) * 10 // len(ADD))
drift = blk.groupby("khoi").agg(ty_le_dang_ky=("target", "mean"), euribor3m_tb=("euribor3m", "mean"),
                                nr_employed_tb=("nr.employed", "mean"), so_khach=("target", "size")).reset_index()
drift.to_csv(HERE / "troi_dat_theo_thoi_gian.csv", index=False)

# ---------------------------------------------------------------- 2) chọn mô hình trên validation
CANDIDATES = {
    "Logistic (đầy đủ, có macro)": (lr_model, ADD_CAT, ADD_NUM + MACRO),
    "Logistic (không macro)": (lr_model, ADD_CAT, ADD_NUM),
    "GBM lr0.03 leaves15": (lambda c, n: hgb_model(c, n, 0.03, 15), ADD_CAT, ADD_NUM + MACRO),
    "GBM lr0.05 leaves31": (lambda c, n: hgb_model(c, n, 0.05, 31), ADD_CAT, ADD_NUM + MACRO),
    "GBM lr0.10 leaves15": (lambda c, n: hgb_model(c, n, 0.10, 15), ADD_CAT, ADD_NUM + MACRO),
}
val_rows, fitted = [], {}
for name, (factory, cat, num) in CANDIDATES.items():
    m = factory(cat, num).fit(TR[cat + num], TR.target)
    s = m.predict_proba(VA[cat + num])[:, 1]
    val_rows.append({"mo_hinh": name, "roc_auc_validation": roc_auc_score(VA.target, s),
                     "pr_auc_validation": average_precision_score(VA.target, s)})
    fitted[name] = (m, cat + num)
# baseline đơn giản, đánh giá trên validation để đối chiếu
simple = lr_model(["poutcome"], []).fit(TR[["poutcome"]], TR.target)
s_va_simple = simple.predict_proba(VA[["poutcome"]])[:, 1]
val_rows.append({"mo_hinh": "Baseline: chỉ poutcome", "roc_auc_validation": roc_auc_score(VA.target, s_va_simple),
                 "pr_auc_validation": average_precision_score(VA.target, s_va_simple)})
val_df = pd.DataFrame(val_rows).sort_values("roc_auc_validation", ascending=False)
val_df.to_csv(HERE / "chon_mo_hinh_validation.csv", index=False)

# mô hình được chọn: cao nhất trên validation, trong số các ứng viên (không tính baseline)
cand_only = val_df[val_df.mo_hinh != "Baseline: chỉ poutcome"]
best_name = cand_only.iloc[0]["mo_hinh"]
best, best_cols = fitted[best_name]
best_is_lr = best_name.startswith("Logistic")

# ---------------------------------------------------------------- 3) đánh giá trên test (chạm một lần)
s_best = best.predict_proba(TE[best_cols])[:, 1]
y_te = TE.target.values
s_simple = simple.predict_proba(TE[["poutcome"]])[:, 1]
s_lr_macro = fitted["Logistic (đầy đủ, có macro)"][0].predict_proba(TE[ADD_CAT + ADD_NUM + MACRO])[:, 1]
s_rand = rng.random(len(TE))  # xếp hạng ngẫu nhiên

rows = []
for name, s in [("Ngẫu nhiên (baseline 0)", s_rand),
                ("Chỉ poutcome (baseline đơn giản)", s_simple),
                ("Logistic (đầy đủ, có macro)", s_lr_macro),
                (f"Mô hình chọn: {best_name}", s_best)]:
    r = metrics(y_te, s)
    r["mo_hinh"] = name
    rows.append(r)
test_df = pd.DataFrame(rows)[["mo_hinh", "roc_auc", "pr_auc", "brier", "precision_top20", "recall_top20", "lift_top20"]]
test_df.to_csv(HERE / "ket_qua_test.csv", index=False)

# khoảng tin cậy bootstrap cho chênh lệch AUC (mô hình chọn - baseline poutcome)
diffs = []
for _ in range(500):
    idx = rng.integers(0, len(y_te), len(y_te))
    yb = y_te[idx]
    if yb.sum() == 0 or yb.sum() == len(yb):
        continue
    diffs.append(roc_auc_score(yb, s_best[idx]) - roc_auc_score(yb, s_simple[idx]))
ci = {"auc_chenh_lech_trung_binh": float(np.mean(diffs)),
      "auc_chenh_lech_2.5": float(np.percentile(diffs, 2.5)),
      "auc_chenh_lech_97.5": float(np.percentile(diffs, 97.5))}
pd.DataFrame([ci]).to_csv(HERE / "chenh_lech_auc_bootstrap.csv", index=False)

# top-k chi tiết
tk = pd.DataFrame(topk(y_te, s_best))
tk_b = pd.DataFrame(topk(y_te, s_simple))
tk["baseline_ty_le_dang_ky"] = tk_b["ty_le_dang_ky"]
tk["baseline_recall"] = tk_b["recall"]
tk.to_csv(HERE / "top_k_test.csv", index=False)

gx, gy = gains(y_te, s_best)
bx, by = gains(y_te, s_simple)

# ---------------------------------------------------------------- 4) yếu tố quan trọng (permutation trên test)
pi = permutation_importance(best, TE[best_cols], y_te, scoring="roc_auc",
                            n_repeats=10, random_state=SEED, n_jobs=1)
imp = pd.DataFrame({"bien": best_cols, "giam_auc_trung_binh": pi.importances_mean,
                    "do_lech_chuan": pi.importances_std}).sort_values("giam_auc_trung_binh", ascending=False)
imp.to_csv(HERE / "quan_trong_bien_permutation.csv", index=False)


# ---------------------------------------------------------------- 5) độ nhạy (cùng họ mô hình với mô hình chọn)
def fit_eval(cat, num, tr=TR, te=TE):
    if best_is_lr:
        m = lr_model(cat, num).fit(tr[cat + num], tr.target)
    else:
        m = hgb_model(cat, num, 0.05, 31).fit(tr[cat + num], tr.target)
    s = m.predict_proba(te[cat + num])[:, 1]
    return metrics(te.target.values, s)


scen = [
    ("Chính: chỉ thông tin biết trước khi gọi (có macro)", ADD_CAT, ADD_NUM + MACRO),
    ("Bỏ chỉ số kinh tế vĩ mô", ADD_CAT, ADD_NUM),
    ("Thêm campaign (số lần gọi, gồm cuộc hiện tại) - không dùng được trước khi gọi", ADD_CAT, ADD_NUM + MACRO + ["campaign"]),
    ("Thêm duration (thời lượng cuộc gọi) - RÒ RỈ, chỉ biết sau khi gọi", ADD_CAT, ADD_NUM + MACRO + ["duration"]),
    ("Thêm age + marital (nhạy cảm, chỉ để đối chiếu)", ADD_CAT + ["marital"], ADD_NUM + MACRO + ["age"]),
]
sens_rows = []
for label, cat, num in scen:
    r = fit_eval(cat, num)
    r["kich_ban"] = label
    sens_rows.append(r)
sens = pd.DataFrame(sens_rows)[["kich_ban", "roc_auc", "pr_auc", "precision_top20", "recall_top20", "lift_top20"]]
sens.to_csv(HERE / "do_nhay_kich_ban.csv", index=False)

# kiểm tra trên bank-full.csv (phiên bản khác của cùng dữ liệu, không có macro, có balance/day)
fm_model = lr_model(FULL_CAT, FULL_NUM).fit(FTR[FULL_CAT + FULL_NUM], FTR.target)
fs = fm_model.predict_proba(FTE[FULL_CAT + FULL_NUM])[:, 1]
fsimp = lr_model(["poutcome"], []).fit(FTR[["poutcome"]], FTR.target).predict_proba(FTE[["poutcome"]])[:, 1]
robust = pd.DataFrame([
    {"du_lieu": "bank-full.csv", "mo_hinh": "Logistic (balance, day, không macro)",
     **metrics(FTE.target.values, fs)},
    {"du_lieu": "bank-full.csv", "mo_hinh": "Chỉ poutcome (baseline)",
     **metrics(FTE.target.values, fsimp)},
])[["du_lieu", "mo_hinh", "roc_auc", "pr_auc", "precision_top20", "recall_top20", "lift_top20"]]
robust.to_csv(HERE / "kiem_tra_bank_full.csv", index=False)

# ---------------------------------------------------------------- 6) kiểm tra lỗi theo nhóm tuổi (chỉ để audit)
thr = np.quantile(s_best, 0.80)
flag = s_best >= thr
bins = [0, 29, 39, 49, 59, 120]
labels = ["<30", "30-39", "40-49", "50-59", "60+"]
ag = TE.assign(nhom_tuoi=pd.cut(TE.age, bins=bins, labels=labels), flagged=flag, s=s_best)
audit = []
for g, d in ag.groupby("nhom_tuoi", observed=True):
    yy = d.target.values
    audit.append({"nhom_tuoi": str(g), "so_khach": len(d), "ty_le_dang_ky_thuc_te": yy.mean(),
                  "ty_le_duoc_danh_dau_top20": d.flagged.mean(),
                  "recall_top20_trong_nhom": (d.flagged & (d.target == 1)).sum() / max((d.target == 1).sum(), 1),
                  "auc_trong_nhom": roc_auc_score(yy, d.s) if 0 < yy.sum() < len(yy) else np.nan})
audit = pd.DataFrame(audit)
audit.to_csv(HERE / "kiem_tra_nhom_tuoi.csv", index=False)

pd.DataFrame({"row_goc_trong_file": TE.index, "target": y_te, "diem_mo_hinh_chon": s_best,
              "diem_baseline_poutcome": s_simple}).to_csv(HERE / "diem_test.csv", index=False)

# ---------------------------------------------------------------- 7) biểu đồ (tiêu đề nêu kết quả)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
r_m = test_df.iloc[3]
r_b = test_df.iloc[1]
r20_m = tk.loc[tk.top_pct == 0.2, "recall"].item()
r20_b = tk.loc[tk.top_pct == 0.2, "baseline_recall"].item()

# Biểu đồ 1: đường tích lũy trên test
fig, ax = plt.subplots(figsize=(7, 5.5))
ax.plot(gx, gy, lw=2.4, color="#1f5aa6", label=f"Mô hình chọn (AUC {r_m.roc_auc:.3f})")
ax.plot(bx, by, lw=2, color="#e08a1e", label=f"Baseline chỉ poutcome (AUC {r_b.roc_auc:.3f})")
ax.plot([0, 1], [0, 1], ls="--", color="grey", label="Ngẫu nhiên")
ax.axvline(0.2, color="black", lw=0.8, ls=":")
ax.set_xlabel("Tỷ lệ khách được gọi (xếp theo điểm, từ cao xuống)")
ax.set_ylabel("Tỷ lệ người đăng ký được bắt")
ax.set_title(f"Test cuối: gọi 20% đầu danh sách bắt {r20_m:.0%} người đăng ký,\nbaseline poutcome bắt {r20_b:.0%}",
             loc="left", fontsize=11)
ax.legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(HERE / "bieu_do_1_duong_tich_luy.png", dpi=150); plt.close(fig)

# Biểu đồ 2: yếu tố quan trọng
top = imp.head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(7.5, 5.5))
ax.barh(top.bien, top.giam_auc_trung_binh, xerr=top.do_lech_chuan, color="#1f5aa6")
ax.set_xlabel("Mức giảm AUC khi xáo trộn biến (trên test)")
client_imp = imp[imp.bien.isin(["job", "education", "default", "housing", "loan"])].giam_auc_trung_binh.max()
ax.set_title(f"Mạnh nhất là {imp.bien.iloc[0]}, {imp.bien.iloc[1]}, {imp.bien.iloc[2]} (thời điểm/kinh tế),\n"
             f"đặc điểm khách hàng chỉ đóng góp tối đa {client_imp:.3f} AUC",
             loc="left", fontsize=10)
fig.tight_layout(); fig.savefig(HERE / "bieu_do_2_yeu_to_quan_trong.png", dpi=150); plt.close(fig)

# Biểu đồ 3: độ nhạy
fig, ax = plt.subplots(figsize=(9, 5.5))
short = ["Chính", "Bỏ macro", "Thêm campaign", "Thêm duration (rò rỉ)", "Thêm age+marital"]
colors = ["#1f5aa6", "#7fa7d9", "#7fa7d9", "#c0392b", "#9b9b9b"]
ax.barh(short[::-1], sens.roc_auc.values[::-1], color=colors[::-1])
for i, v in enumerate(sens.roc_auc.values[::-1]):
    ax.text(v + 0.003, i, f"{v:.3f}", va="center")
ax.axvline(r_b.roc_auc, color="#e08a1e", ls="--", lw=1.2)
ax.text(r_b.roc_auc + 0.01, 4.45, f"baseline poutcome {r_b.roc_auc:.3f}", color="#e08a1e", va="bottom")
ax.set_xlim(0, 0.8)
ax.set_xlabel("AUC trên test (0,5 = đoán ngẫu nhiên)")
ax.set_title(f"Thêm duration đẩy AUC lên {sens.roc_auc.iloc[3]:.2f} nhưng là rò rỉ; các biến hợp lệ đều dưới baseline",
             loc="left", fontsize=11)
fig.tight_layout(); fig.savefig(HERE / "bieu_do_3_do_nhay.png", dpi=150); plt.close(fig)

# Biểu đồ 4: tỷ lệ đăng ký theo poutcome
pr = ADD.groupby("poutcome")["target"].mean().reindex(["success", "failure", "nonexistent"])
fig, ax = plt.subplots(figsize=(6.5, 5))
ax.bar(["Thành công", "Thất bại", "Chưa từng gọi"], pr.values, color=["#1f5aa6", "#9b9b9b", "#cfd8e3"])
for i, v in enumerate(pr.values):
    ax.text(i, v + 0.01, f"{v:.1%}", ha="center")
ax.set_ylabel("Tỷ lệ đăng ký")
ax.set_title(f"Khách thành công ở chiến dịch trước đăng ký {pr.iloc[0]:.0%}, so với {ADD.target.mean():.0%} chung",
             loc="left", fontsize=11)
fig.tight_layout(); fig.savefig(HERE / "bieu_do_4_poutcome.png", dpi=150); plt.close(fig)

# Biểu đồ 5: trôi dạt theo thời gian
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.bar(drift.khoi + 1, drift.ty_le_dang_ky, color="#9bb7dc")
ax.set_xlabel("Khối thời gian (10 khối theo thứ tự dòng, 1 = sớm nhất)")
ax.set_ylabel("Tỷ lệ đăng ký")
ax.set_title(f"Tỷ lệ đăng ký tăng từ {drift.ty_le_dang_ky.iloc[0]:.0%} lên {drift.ty_le_dang_ky.iloc[-1]:.0%} "
             "qua thời gian: mô hình học trên giai đoạn thấp, test ở giai đoạn cao",
             loc="left", fontsize=10)
fig.tight_layout(); fig.savefig(HERE / "bieu_do_5_troi_dat.png", dpi=150); plt.close(fig)

# ---------------------------------------------------------------- tóm tắt
print("EDA:", {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v) for k, v in eda.items()})
print("Drift:\n", drift.round(3).to_string(index=False))
print("Validation:\n", val_df.round(4).to_string(index=False))
print("Chọn:", best_name)
print("Test:\n", test_df.round(4).to_string(index=False))
print("Bootstrap chênh lệch AUC (chọn - poutcome):", {k: round(v, 4) for k, v in ci.items()})
print("Top-k (mô hình chọn vs baseline):\n", tk.round(4).to_string(index=False))
print("Quan trọng:\n", imp.round(4).to_string(index=False))
print("Độ nhạy:\n", sens.round(4).to_string(index=False))
print("bank-full:\n", robust.round(4).to_string(index=False))
print("Nhóm tuổi (audit):\n", audit.round(3).to_string(index=False))
