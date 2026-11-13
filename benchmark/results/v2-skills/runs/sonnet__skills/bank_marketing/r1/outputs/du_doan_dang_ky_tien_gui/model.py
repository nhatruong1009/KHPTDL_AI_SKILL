import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.inspection import permutation_importance

OUT = "outputs/du_doan_dang_ky_tien_gui"
os.makedirs(OUT, exist_ok=True)
df = pd.read_csv("data/bank-additional/bank-additional-full.csv", sep=";")
n0 = len(df)
df = df.drop_duplicates().reset_index(drop=True)  # giữ thứ tự thời gian của file
df["y"] = (df["y"] == "yes").astype(int)
df["pdays_contacted"] = (df["pdays"] != 999).astype(int)
df["pdays_val"] = df["pdays"].where(df["pdays"] != 999, 0)

# Split theo thời gian (file sắp theo ngày, 05/2008 -> 11/2010): 60/20/20
n = len(df)
i1, i2 = int(n * .6), int(n * .8)
tr, va, te = df.iloc[:i1], df.iloc[i1:i2], df.iloc[i2:]
split_info = pd.DataFrame({
    "tap": ["train", "valid", "test"], "n": [len(tr), len(va), len(te)],
    "ty_le_dang_ky": [d.y.mean() for d in (tr, va, te)],
    "thang_dau": [d.month.iloc[0] for d in (tr, va, te)],
    "thang_cuoi": [d.month.iloc[-1] for d in (tr, va, te)],
    "euribor_tb": [d.euribor3m.mean() for d in (tr, va, te)],
    "ty_le_poutcome_success": [(d.poutcome == "success").mean() for d in (tr, va, te)]})
split_info.to_csv(OUT + "/split_drift.csv", index=False)
print(split_info, n0, n)

# Kiểm toán thời điểm (xem answer.md). Dự đoán TRƯỚC cuộc gọi.
cat_core = ["job", "marital", "education", "default", "housing", "loan", "contact", "day_of_week", "poutcome"]
num_core = ["previous", "pdays_val", "pdays_contacted"]
macro = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
# age: nhạy cảm -> chỉ audit; duration: biết sau cuộc gọi -> loại;
# campaign: đếm cả lần gọi hiện tại/cuối -> chỉ sensitivity; month: không tổng quát qua split thời gian -> loại


def make(cats, nums, model):
    pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats),
                             ("n", StandardScaler(), nums)])
    return Pipeline([("p", pre), ("m", model)])


def LR():
    return LogisticRegression(max_iter=2000, class_weight="balanced", C=0.5)


def HG():
    return HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300,
                                          l2_regularization=1.0, random_state=42)


def lift_k(y, s, frac):
    k = int(len(y) * frac)
    idx = np.argsort(-s)[:k]
    p = y[idx].mean()
    return p, p / y.mean(), y[idx].sum() / y.sum()


def row(name, split, y, s):
    r = dict(modelo=name, tap=split, roc_auc=roc_auc_score(y, s),
             pr_auc=average_precision_score(y, s), base_rate=y.mean())
    for f in (.1, .2, .3):
        p, l, rec = lift_k(y, s, f)
        pc = str(int(f * 100))
        r["precision@" + pc] = p
        r["lift@" + pc] = l
        r["recall@" + pc] = rec
    return r


rows = []


def evaluate(name, pipe, cats, nums):
    cols = cats + nums
    pipe.fit(tr[cols], tr.y)
    for nm, d in (("valid", va), ("test", te)):
        rows.append(row(name, nm, d.y.values, pipe.predict_proba(d[cols])[:, 1]))
    return pipe


for nm, d in (("valid", va), ("test", te)):
    y = d.y.values
    rs = np.random.RandomState(42).rand(len(d))
    r = row("Baseline 1: gọi ngẫu nhiên", nm, y, rs)
    r["roc_auc"], r["pr_auc"] = 0.5, y.mean()  # kỳ vọng của ngẫu nhiên
    rows.append(r)
    s = (d.poutcome == "success").astype(float).values * 10 - d.euribor3m.values + 1e-6 * rs
    rows.append(row("Baseline 2: luật đơn giản (poutcome=success, euribor thấp)", nm, y, s))

m_lr = evaluate("LogReg (chính)", make(cat_core, num_core + macro, LR()), cat_core, num_core + macro)
m_hg = evaluate("HistGB (chính)", make(cat_core, num_core + macro, HG()), cat_core, num_core + macro)
evaluate("[Nhạy cảm] HistGB không có biến vĩ mô", make(cat_core, num_core, HG()), cat_core, num_core)
evaluate("[Nhạy cảm] HistGB + campaign", make(cat_core, num_core + macro + ["campaign"], HG()),
         cat_core, num_core + macro + ["campaign"])
evaluate("[Nhạy cảm] LogReg không có biến vĩ mô", make(cat_core, num_core, LR()), cat_core, num_core)
res = pd.DataFrame(rows)
res.to_csv(OUT + "/metrics.csv", index=False)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
print(res.round(3).to_string())

v = res[(res.tap == "valid") & res.modelo.str.contains("chính")].set_index("modelo").pr_auc
print(v)
best_name = v.idxmax()
best = m_lr if best_name.startswith("LogReg") else m_hg
print("Chọn (theo PR-AUC valid):", best_name)
feats = cat_core + num_core + macro
s_te = best.predict_proba(te[feats])[:, 1]

pi = permutation_importance(best, te[feats], te.y, scoring="roc_auc", n_repeats=10, random_state=42)
imp = pd.DataFrame({"feature": feats, "giam_roc_auc": pi.importances_mean, "sd": pi.importances_std}
                   ).sort_values("giam_roc_auc", ascending=False)
imp.to_csv(OUT + "/feature_importance.csv", index=False)
print(imp.round(4))

dd = pd.DataFrame({"y": te.y.values, "s": s_te})
dd["decile"] = pd.qcut(dd.s.rank(method="first", ascending=False), 10, labels=range(1, 11))
dec = dd.groupby("decile", observed=True).agg(n=("y", "size"), ty_le=("y", "mean")).reset_index()
dec["lift"] = dec.ty_le / te.y.mean()
dec.to_csv(OUT + "/decile_test.csv", index=False)
print(dec.round(3))

# Audit theo nhóm tuổi (age không là predictor)
te2 = te.assign(s=s_te, nhom_tuoi=pd.cut(te.age, [0, 29, 39, 49, 59, 120],
                                         labels=["<30", "30-39", "40-49", "50-59", "60+"]))
thr = np.quantile(s_te, .8)
ra = []
for g, d in te2.groupby("nhom_tuoi", observed=True):
    sel = d[d.s >= thr]
    ra.append(dict(nhom_tuoi=g, n=len(d), ty_le_thuc=d.y.mean(), ty_le_duoc_chon_top20=len(sel) / len(d),
                   precision_trong_nhom_chon=sel.y.mean() if len(sel) else np.nan,
                   auc=roc_auc_score(d.y, d.s) if d.y.nunique() > 1 else np.nan))
aud = pd.DataFrame(ra)
aud.to_csv(OUT + "/audit_nhom_tuoi.csv", index=False)
print(aud.round(3))

# Bootstrap: chênh ROC-AUC mô hình - baseline 2 trên test
rs = np.random.RandomState(42)
y = te.y.values
s_b2 = (te.poutcome == "success").astype(float).values * 10 - te.euribor3m.values
dif = []
for _ in range(500):
    i = rs.randint(0, len(y), len(y))
    dif.append(roc_auc_score(y[i], s_te[i]) - roc_auc_score(y[i], s_b2[i]))
print("AUC diff vs baseline2 CI95", np.percentile(dif, [2.5, 50, 97.5]))

# Charts
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(dec.decile.astype(str), dec.ty_le * 100, color="#2a6f97")
ax.axhline(te.y.mean() * 100, color="#c0392b", ls="--")
ax.text(9.4, te.y.mean() * 100 + 1, "Trung bình %.1f%%" % (te.y.mean() * 100), ha="right", color="#c0392b")
ax.set_title("10%% khách điểm cao nhất đăng ký %.0f%%, gấp %.1f lần gọi ngẫu nhiên" % (dec.ty_le[0] * 100, dec.lift[0]))
ax.set_xlabel("Decile điểm dự đoán (1 = cao nhất), tập test")
ax.set_ylabel("Tỷ lệ đăng ký (%)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(OUT + "/lift_decile.png", dpi=150)
plt.close()
top = imp.head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(top.feature, top.giam_roc_auc, xerr=top.sd, color="#2a6f97")
ax.set_title("Top 10 yếu tố giúp dự đoán đăng ký (trước cuộc gọi)")
ax.set_xlabel("Mức giảm ROC-AUC khi xáo trộn biến (test)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(OUT + "/feature_importance.png", dpi=150)
plt.close()
