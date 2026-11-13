import json
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.inspection import permutation_importance

BASE = "/root/.cache/skill-bench/runs/ab-vi/haiku__noskills/bank_marketing/r1/workspace"
OUT = BASE + "/outputs"
df = pd.read_csv(BASE + "/data/bank-full.csv", sep=";")
df["target"] = (df["y"] == "yes").astype(int)
print("rows", len(df), "base rate", round(df.target.mean(), 4))

CAT = ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome"]
NUM = ["age", "balance", "day", "pdays", "previous"]
# Loại duration (rò rỉ: chỉ biết sau cuộc gọi) và campaign (gồm chính cuộc gọi kết quả)
FEATS = CAT + NUM
X = df[FEATS]
y = df["target"].values


def pre(cat, num, scale=True):
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
        ("num", StandardScaler() if scale else "passthrough", num),
    ])


def make_logreg(cat, num):
    return make_pipeline(pre(cat, num), LogisticRegression(max_iter=2000, C=1.0))


def make_gbm(cat, num):
    return make_pipeline(
        ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
                           ("num", "passthrough", num)]),
        HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31,
                                       l2_regularization=1.0, random_state=0))


def top_k_metrics(y_true, score, frac):
    n = int(round(frac * len(y_true)))
    idx = np.argsort(-score)[:n]
    prec = y_true[idx].mean()
    recall = y_true[idx].sum() / y_true.sum()
    return prec, recall, prec / y_true.mean()


# Baseline 1: ngẫu nhiên (không có mô hình)
# Baseline 2: quy tắc đơn giản: xếp hạng theo tỷ lệ đăng ký của nhóm poutcome
def baseline_poutcome_fit(Xtr, ytr):
    return pd.Series(ytr, index=Xtr.index).groupby(Xtr["poutcome"]).mean()


def baseline_poutcome_score(rate, Xte):
    return Xte["poutcome"].map(rate).fillna(rate.mean()).values


def all_scores(Xtr, ytr, Xte, seed=0):
    rate = baseline_poutcome_fit(Xtr, ytr)
    lr = make_logreg(CAT, NUM).fit(Xtr, ytr)
    gb = make_gbm(CAT, NUM).fit(Xtr, ytr)
    return {
        "Ngẫu nhiên (baseline 1)": np.random.RandomState(seed).rand(len(Xte)),
        "Quy tắc poutcome (baseline 2)": baseline_poutcome_score(rate, Xte),
        "Hồi quy logistic": lr.predict_proba(Xte)[:, 1],
        "Gradient boosting (HistGB)": gb.predict_proba(Xte)[:, 1],
    }, gb, lr


skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
names = ["Ngẫu nhiên (baseline 1)", "Quy tắc poutcome (baseline 2)", "Hồi quy logistic", "Gradient boosting (HistGB)"]
rows = {k: {"auc": [], "pr_auc": [], "prec10": [], "prec20": [], "recall20": [], "lift20": []} for k in names}

for tr, te in skf.split(X, y):
    Xtr, Xte, ytr, yte = X.iloc[tr], X.iloc[te], y[tr], y[te]
    scores, _, _ = all_scores(Xtr, ytr, Xte)
    for k, s in scores.items():
        p10, _, _ = top_k_metrics(yte, s, 0.10)
        p20, r20, l20 = top_k_metrics(yte, s, 0.20)
        rows[k]["auc"].append(roc_auc_score(yte, s))
        rows[k]["pr_auc"].append(average_precision_score(yte, s))
        rows[k]["prec10"].append(p10)
        rows[k]["prec20"].append(p20)
        rows[k]["recall20"].append(r20)
        rows[k]["lift20"].append(l20)

summary = []
for k, v in rows.items():
    rec = {"mo_hinh": k}
    for m, vals in v.items():
        rec[m] = round(float(np.mean(vals)), 4)
        rec[m + "_sd"] = round(float(np.std(vals)), 4)
    summary.append(rec)
cv = pd.DataFrame(summary)
cv.to_csv(OUT + "/ket_qua_cv5.csv", index=False)
print(cv.to_string())

# Holdout theo thời gian: dữ liệu sắp xếp theo ngày (2008-2010); train 80% đầu, test 20% cuối
cut = int(len(df) * 0.8)
Xtr, Xte, ytr, yte = X.iloc[:cut], X.iloc[cut:], y[:cut], y[cut:]
tscores, gb, lr = all_scores(Xtr, ytr, Xte)
trows = []
for k, s in tscores.items():
    p10, _, _ = top_k_metrics(yte, s, 0.10)
    p20, r20, l20 = top_k_metrics(yte, s, 0.20)
    trows.append({"mo_hinh": k, "auc": round(roc_auc_score(yte, s), 4),
                  "pr_auc": round(average_precision_score(yte, s), 4),
                  "prec10": round(p10, 4), "prec20": round(p20, 4),
                  "recall20": round(r20, 4), "lift20": round(l20, 3)})
tdf = pd.DataFrame(trows)
tdf.to_csv(OUT + "/ket_qua_holdout_thoi_gian.csv", index=False)
print(tdf.to_string())

# Độ quan trọng biến: permutation importance trên holdout thời gian (giảm AUC)
pi = permutation_importance(gb, Xte, yte, scoring="roc_auc", n_repeats=5, random_state=0, n_jobs=1)
imp = pd.DataFrame({"bien": FEATS, "giam_auc": pi.importances_mean, "sd": pi.importances_std})
imp = imp.sort_values("giam_auc", ascending=False)
imp.to_csv(OUT + "/do_quan_trong_bien.csv", index=False)
print(imp.to_string())

# Hệ số logistic chuẩn hóa để xem hướng tác động
ohe = lr.named_steps["columntransformer"].named_transformers_["cat"]
fn = list(ohe.get_feature_names_out(CAT)) + NUM
coef = pd.Series(lr.named_steps["logisticregression"].coef_[0], index=fn)
coef.sort_values().to_csv(OUT + "/he_so_logistic.csv", header=["he_so"])

# Tỷ lệ đăng ký theo nhóm (mô tả)
for c in ["poutcome", "contact", "month", "job", "education", "housing", "loan"]:
    g = df.groupby(c)["target"].agg(["mean", "size"]).sort_values("mean", ascending=False).round(4)
    g.to_csv(OUT + "/ty_le_theo_" + c + ".csv")
df["nhom_tuoi"] = pd.cut(df.age, [0, 30, 40, 50, 60, 120], labels=["<=30", "31-40", "41-50", "51-60", ">60"])
g = df.groupby("nhom_tuoi", observed=True)["target"].agg(["mean", "size"]).round(4)
g.to_csv(OUT + "/ty_le_theo_tuoi.csv")
print(g)

# Độ nhạy: thêm campaign (chỉ để kiểm tra; không dùng cho dự đoán trước cuộc gọi)
Xc = df[FEATS + ["campaign"]]
gb2 = make_gbm(CAT, NUM + ["campaign"])
aucs = []
for tr, te in skf.split(Xc, y):
    gb2.fit(Xc.iloc[tr], y[tr])
    aucs.append(roc_auc_score(y[te], gb2.predict_proba(Xc.iloc[te])[:, 1]))
print("Do nhay + campaign, AUC CV:", round(np.mean(aucs), 4))

# Tham khảo: thêm duration (rò rỉ, không khả thi trước cuộc gọi)
Xd = df[FEATS + ["duration"]]
gb3 = make_gbm(CAT, NUM + ["duration"])
aucs = []
for tr, te in skf.split(Xd, y):
    gb3.fit(Xd.iloc[tr], y[tr])
    aucs.append(roc_auc_score(y[te], gb3.predict_proba(Xd.iloc[te])[:, 1]))
print("Tham khao + duration (ro ri), AUC CV:", round(np.mean(aucs), 4))

# Độ nhạy: bộ bank-additional-full (có chỉ số kinh tế, không có balance/day)
da = pd.read_csv(BASE + "/data/bank-additional/bank-additional-full.csv", sep=";")
da["target"] = (da["y"] == "yes").astype(int)
CAT_A = ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "day_of_week", "poutcome"]
NUM_A = ["age", "pdays", "previous", "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
Xa, ya = da[CAT_A + NUM_A], da["target"].values
res = {}
for name in ["Ngẫu nhiên", "Hồi quy logistic", "Gradient boosting"]:
    aucs, lifts = [], []
    for tr, te in skf.split(Xa, ya):
        if name == "Ngẫu nhiên":
            s = np.random.RandomState(0).rand(len(te))
        elif name == "Hồi quy logistic":
            m = make_logreg(CAT_A, NUM_A).fit(Xa.iloc[tr], ya[tr])
            s = m.predict_proba(Xa.iloc[te])[:, 1]
        else:
            m = make_gbm(CAT_A, NUM_A).fit(Xa.iloc[tr], ya[tr])
            s = m.predict_proba(Xa.iloc[te])[:, 1]
        aucs.append(roc_auc_score(ya[te], s))
        lifts.append(top_k_metrics(ya[te], s, 0.20)[2])
    res[name] = {"auc": round(float(np.mean(aucs)), 4), "lift20": round(float(np.mean(lifts)), 3)}
print("bank-additional-full:", res)

with open(OUT + "/ket_qua.json", "w", encoding="utf-8") as f:
    json.dump({"cv": summary, "holdout": trows, "bank_additional_full": res,
               "base_rate": round(float(df.target.mean()), 4), "n": int(len(df))},
              f, ensure_ascii=False, indent=2, default=float)
