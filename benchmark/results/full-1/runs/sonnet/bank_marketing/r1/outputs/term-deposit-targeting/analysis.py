import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.inspection import permutation_importance
from sklearn.model_selection import StratifiedKFold, cross_val_predict

O = "outputs/term-deposit-targeting/"
df = pd.read_csv("data/bank-additional/bank-additional-full.csv", sep=";")
print(df.shape, df.duplicated().sum(), "duplicate rows")
df["y"] = (df.y == "yes").astype(int)
df["prev_contacted"] = (df.pdays != 999).astype(int)
df.loc[df.pdays == 999, "pdays"] = -1
# Excluded: duration (unknown before call), campaign (counts the current call)
X = df.drop(columns=["duration", "campaign", "y"]); y = df.y
cat = X.select_dtypes("object").columns.tolist()
macro = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
num = [c for c in X if c not in cat]
Xc = X.copy()
for c in cat: Xc[c] = Xc[c].astype("category")

def gb(cols):
    return HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300,
        categorical_features=[cols.index(c) for c in cat if c in cols], random_state=0)

# temporal split (file is ordered by date): train first 70%, test last 30%
n = len(df); k = int(n * .7)
ytr, yte = y.iloc[:k], y.iloc[k:]
print("train rate", ytr.mean(), "test rate", yte.mean())
preds = {}
m = gb(list(Xc.columns)).fit(Xc.iloc[:k], ytr); preds["Gradient boosting"] = m.predict_proba(Xc.iloc[k:])[:, 1]
l = make_pipeline(ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore"), cat), ("n", StandardScaler(), num)]),
                  LogisticRegression(max_iter=2000)).fit(X.iloc[:k], ytr)
preds["Logistic regression"] = l.predict_proba(X.iloc[k:])[:, 1]
Xn = Xc.drop(columns=macro)
m2 = gb(list(Xn.columns)).fit(Xn.iloc[:k], ytr); preds["GB without macro indicators"] = m2.predict_proba(Xn.iloc[k:])[:, 1]
preds["Naive (constant)"] = np.full(len(yte), ytr.mean())

def topk(p, frac):
    idx = np.argsort(-p, kind="stable")[:int(len(p) * frac)]; return yte.values[idx].mean()
res = []
for nme, p in preds.items():
    row = dict(model=nme, roc_auc=roc_auc_score(yte, p), pr_auc=average_precision_score(yte, p))
    naive = nme.startswith("Naive")
    for f in (.1, .2): row[f"conv_top{int(f*100)}pct"] = yte.mean() if naive else topk(p, f)
    row["lift_top10"] = row["conv_top10pct"] / yte.mean(); res.append(row)
R = pd.DataFrame(res); R.to_csv(O + "model_comparison_temporal.csv", index=False); print(R.round(3).to_string())

rng = np.random.default_rng(0); p = preds["Gradient boosting"]; b = []
for _ in range(200):
    i = rng.integers(0, len(yte), len(yte)); b.append((roc_auc_score(yte.values[i], p[i]), average_precision_score(yte.values[i], p[i])))
print("GB AUC 95% CI", np.percentile([x[0] for x in b], [2.5, 97.5]), "PR-AUC CI", np.percentile([x[1] for x in b], [2.5, 97.5]))

cv = cross_val_predict(gb(list(Xc.columns)), Xc, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
print("random 5-fold CV AUC", roc_auc_score(y, cv), "PR", average_precision_score(y, cv))

d = pd.DataFrame({"p": p, "y": yte.values}); d["decile"] = pd.qcut(d.p.rank(method="first", ascending=False), 10, labels=range(1, 11))
dt = d.groupby("decile", observed=True).agg(clients=("y", "size"), rate=("y", "mean"), mean_pred=("p", "mean"))
dt["lift"] = dt.rate / yte.mean(); dt["cum_capture"] = dt.rate.mul(dt.clients).cumsum() / d.y.sum()
dt.to_csv(O + "decile_lift.csv"); print(dt.round(3))

pi = permutation_importance(m, Xc.iloc[k:], yte, scoring="roc_auc", n_repeats=5, random_state=0)
imp = pd.Series(pi.importances_mean, index=X.columns).sort_values(ascending=False)
imp.to_csv(O + "permutation_importance.csv", header=["auc_drop"]); print(imp.round(4))

rows = []
for c in ["poutcome", "month", "contact", "job", "education", "prev_contacted"]:
    t = df.groupby(c).y.agg(["size", "mean"]); t["feature"] = c; rows.append(t.reset_index().rename(columns={c: "level"}))
cr = pd.concat(rows); cr.to_csv(O + "conversion_by_factor.csv", index=False); print(cr.round(3).to_string())

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].bar(dt.index.astype(str), dt.rate * 100, color="#2a6fb0"); ax[0].axhline(yte.mean() * 100, color="k", ls="--")
ax[0].text(9, yte.mean() * 100 + 1, f"naive {yte.mean()*100:.1f}%", ha="right")
ax[0].set_xlabel("Score decile (1 = highest)"); ax[0].set_ylabel("Subscription rate (%)"); ax[0].set_title("Held-out later period: rate by score decile")
t = imp.head(10)[::-1]; ax[1].barh(t.index, t.values, color="#2a6fb0"); ax[1].set_xlabel("Drop in AUC when shuffled"); ax[1].set_title("Top factors (permutation importance)")
plt.tight_layout(); plt.savefig(O + "model_summary.png", dpi=130)
