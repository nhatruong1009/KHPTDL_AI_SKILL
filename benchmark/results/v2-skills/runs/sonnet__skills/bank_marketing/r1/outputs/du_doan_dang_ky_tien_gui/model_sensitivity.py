"""Kiểm tra độ nhạy: (A) huấn luyện lại trên train+valid -> test; (B) CV theo khối thời gian liên tục.
(B) KHÔNG phải kiểm tra 'dự đoán tương lai' - nó cho biết mô hình học được gì khi các giai đoạn đã có trong dữ liệu."""
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
from sklearn.model_selection import GroupKFold
from sklearn.inspection import permutation_importance

OUT = "outputs/du_doan_dang_ky_tien_gui"
df = pd.read_csv("data/bank-additional/bank-additional-full.csv", sep=";").drop_duplicates().reset_index(drop=True)
df["y"] = (df["y"] == "yes").astype(int)
df["pdays_contacted"] = (df["pdays"] != 999).astype(int)
df["pdays_val"] = df["pdays"].where(df["pdays"] != 999, 0)
cat_core = ["job", "marital", "education", "default", "housing", "loan", "contact", "day_of_week", "poutcome"]
num_core = ["previous", "pdays_val", "pdays_contacted"]
macro = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]


def make(cats, nums, kind):
    pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats),
                             ("n", StandardScaler(), nums)])
    if kind == "lr":
        m = LogisticRegression(max_iter=2000, class_weight="balanced", C=0.5)
    else:
        m = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=200,
                                           l2_regularization=1.0, random_state=42)
    return Pipeline([("p", pre), ("m", m)])


def metrics(y, s):
    k = int(len(y) * .2)
    idx = np.argsort(-s)[:k]
    p = y[idx].mean()
    return dict(roc_auc=roc_auc_score(y, s), pr_auc=average_precision_score(y, s),
                precision20=p, lift20=p / y.mean(), recall20=y[idx].sum() / y.sum(), base=y.mean())


def baseline2(d):
    return (d.poutcome == "success").astype(float).values * 10 - d.euribor3m.values


configs = {"LogReg + vĩ mô": ("lr", cat_core, num_core + macro), "HistGB + vĩ mô": ("hgb", cat_core, num_core + macro),
           "LogReg không vĩ mô": ("lr", cat_core, num_core), "HistGB không vĩ mô": ("hgb", cat_core, num_core)}
rows = []
# (A) refit train+valid -> test (cấu hình đã cố định trước, test chạm 1 lần cho mỗi cấu hình)
n = len(df)
i2 = int(n * .8)
trv, te = df.iloc[:i2], df.iloc[i2:]
for name, (kind, c, nu) in configs.items():
    p = make(c, nu, kind).fit(trv[c + nu], trv.y)
    r = metrics(te.y.values, p.predict_proba(te[c + nu])[:, 1])
    rows.append(dict(kiem_tra="A: train+valid -> test (tuyến tính theo thời gian)", modelo=name, **r))
rows.append(dict(kiem_tra="A: train+valid -> test (tuyến tính theo thời gian)", modelo="Baseline 2 (luật đơn giản)",
                 **metrics(te.y.values, baseline2(te))))

# (B) CV theo khối liên tục (mỗi khối ~300 dòng liên tiếp), 5 fold
blk = (np.arange(n) // 300)
oof = {k: np.zeros(n) for k in configs}
gkf = GroupKFold(n_splits=5)
folds = list(gkf.split(df, df.y, blk))
for name, (kind, c, nu) in configs.items():
    for a, b in folds:
        p = make(c, nu, kind).fit(df.iloc[a][c + nu], df.y.iloc[a])
        oof[name][b] = p.predict_proba(df.iloc[b][c + nu])[:, 1]
    rows.append(dict(kiem_tra="B: CV theo khối thời gian (không phải dự báo tương lai)", modelo=name,
                     **metrics(df.y.values, oof[name])))
rows.append(dict(kiem_tra="B: CV theo khối thời gian (không phải dự báo tương lai)", modelo="Baseline 2 (luật đơn giản)",
                 **metrics(df.y.values, baseline2(df))))
rows.append(dict(kiem_tra="B: CV theo khối thời gian (không phải dự báo tương lai)", modelo="Baseline 1: ngẫu nhiên",
                 **{**metrics(df.y.values, np.random.RandomState(42).rand(n)), "roc_auc": .5, "lift20": 1.0}))
res = pd.DataFrame(rows)
res.to_csv(OUT + "/metrics_sensitivity.csv", index=False)
pd.set_option("display.width", 220)
print(res.round(3).to_string())

# Tầm quan trọng (permutation, ROC-AUC) cho HistGB+vĩ mô, trên fold B (mỗi fold fit riêng, trung bình)
feats = cat_core + num_core + macro
imps = []
for a, b in folds:
    p = make(cat_core, num_core + macro, "hgb").fit(df.iloc[a][feats], df.y.iloc[a])
    pi = permutation_importance(p, df.iloc[b][feats], df.y.iloc[b], scoring="roc_auc", n_repeats=5, random_state=42)
    imps.append(pi.importances_mean)
imp = pd.DataFrame({"feature": feats, "giam_roc_auc": np.mean(imps, 0), "sd_giua_fold": np.std(imps, 0)}
                   ).sort_values("giam_roc_auc", ascending=False)
imp.to_csv(OUT + "/feature_importance_blockCV.csv", index=False)
print(imp.round(4))

# Lift theo decile (OOF, mô hình HistGB + vĩ mô)
s = oof["HistGB + vĩ mô"]
dd = pd.DataFrame({"y": df.y.values, "s": s})
dd["decile"] = pd.qcut(dd.s.rank(method="first", ascending=False), 10, labels=range(1, 11))
dec = dd.groupby("decile", observed=True).agg(n=("y", "size"), ty_le=("y", "mean")).reset_index()
dec["lift"] = dec.ty_le / df.y.mean()
dec.to_csv(OUT + "/decile_blockCV.csv", index=False)
print(dec.round(3))

# Biểu đồ so sánh hai cách kiểm tra
sub = res[res.modelo.isin(["Baseline 2 (luật đơn giản)", "HistGB + vĩ mô", "HistGB không vĩ mô", "LogReg không vĩ mô"])]
piv = sub.pivot(index="modelo", columns="kiem_tra", values="roc_auc")
fig, ax = plt.subplots(figsize=(9, 4.8))
piv.plot.barh(ax=ax, color=["#2a6f97", "#e08e45"])
ax.axvline(.5, color="grey", ls="--")
ax.set_title("Mô hình chỉ vượt baseline khi kiểm tra trong cùng giai đoạn; dự báo giai đoạn sau thì không")
ax.set_xlabel("ROC-AUC")
ax.set_ylabel("")
ax.legend(fontsize=8, loc="lower right")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(OUT + "/so_sanh_kiem_tra.png", dpi=150)
plt.close()
