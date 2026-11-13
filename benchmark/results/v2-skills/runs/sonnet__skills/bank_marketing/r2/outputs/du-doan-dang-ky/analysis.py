import os
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.inspection import permutation_importance

O = "outputs/du-doan-dang-ky/"
os.makedirs(O, exist_ok=True)
F = "data/bank-additional/bank-additional-full.csv"
df = pd.read_csv(F, sep=";")
if df.shape[1] == 1:
    df = pd.read_csv(F)
df["y"] = (df["y"] == "yes").astype(int)
df["pdays_contacted"] = (df.pdays != 999).astype(int)
df["pdays_val"] = df.pdays.where(df.pdays != 999, 0)
df["log_previous"] = np.log1p(df.previous)
df["log_campaign"] = np.log1p(df.campaign)
df["log_duration"] = np.log1p(df.duration)

# file is ordered by date (May 2008 - Nov 2010): time-based split 60/20/20
n = len(df); a, b = int(n * .6), int(n * .8)
tr, va, te = df.iloc[:a], df.iloc[a:b], df.iloc[b:]
pd.DataFrame({"set": ["train", "valid", "test"], "rows": [len(tr), len(va), len(te)],
              "base_rate": [d.y.mean() for d in (tr, va, te)]}).to_csv(O + "split_base_rate.csv", index=False)

pd.DataFrame([
 ("age, marital", "trước cuộc gọi", "loại khỏi mô hình", "thuộc tính nhạy cảm: chỉ dùng kiểm tra sai số theo nhóm"),
 ("duration", "SAU cuộc gọi", "LOẠI", "tài liệu nêu rõ không biết trước khi gọi; chỉ chạy sensitivity"),
 ("campaign", "đếm cả cuộc gọi cuối", "LOẠI khỏi mô hình chính", "không kiểm chứng được trước cuộc gọi; chạy sensitivity"),
 ("job, education, default, housing, loan", "trước", "giữ", "hồ sơ khách hàng"),
 ("contact, month, day_of_week", "lúc lên lịch gọi", "giữ", "biết khi lên lịch"),
 ("pdays, previous, poutcome", "trước (chiến dịch cũ)", "giữ", "lịch sử"),
 ("5 chỉ số vĩ mô", "công bố tại thời điểm gọi", "giữ (+ chạy bản không có)", "trôi theo thời gian"),
], columns=["feature", "known_when", "decision", "why"]).to_csv(O + "feature_audit.csv", index=False)

cat = ["job", "education", "default", "housing", "loan", "contact", "month", "day_of_week", "poutcome"]
macro = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
num = ["pdays_val", "pdays_contacted", "log_previous"] + macro


def mk(model, cat, num):
    pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore"), cat),
                             ("n", StandardScaler(), num)], sparse_threshold=0)
    return Pipeline([("p", pre), ("m", model)])


def metrics(name, yv, s, d):
    r = {"model": name, "set": d, "auc": roc_auc_score(yv, s), "pr_auc": average_precision_score(yv, s)}
    for fr in (.1, .2):
        k = int(len(yv) * fr); idx = np.argsort(-s, kind="stable")[:k]
        r[f"precision@{int(fr*100)}%"] = yv[idx].mean()
        r[f"lift@{int(fr*100)}%"] = yv[idx].mean() / yv.mean()
        r[f"recall@{int(fr*100)}%"] = yv[idx].sum() / yv.sum()
    return r


rows = []; fitted = {}
def run(name, model, c, nu):
    p = mk(model, c, nu).fit(tr[c + nu], tr.y); fitted[name] = (p, c + nu)
    for dn, d in (("valid", va), ("test", te)):
        rows.append(metrics(name, d.y.values, p.predict_proba(d[c + nu])[:, 1], dn))

for dn, d in (("valid", va), ("test", te)):
    rows.append(metrics("Baseline: gọi ngẫu nhiên", d.y.values, np.random.RandomState(0).rand(len(d)), dn))
for dn, d in (("valid", va), ("test", te)):
    s = (d.poutcome == "success").astype(float).values + np.random.RandomState(42).rand(len(d)) * 1e-3
    rows.append(metrics("Baseline: luật poutcome=success", d.y.values, s, dn))
cat_nm = [c for c in cat if c != "month"]
base = ["pdays_val", "pdays_contacted", "log_previous"]
LR = lambda: LogisticRegression(max_iter=3000, C=0.5)
HG = lambda: HistGradientBoostingClassifier(max_depth=3, learning_rate=.05, max_iter=150, random_state=42)
run("A Logistic: đầy đủ (có tháng+vĩ mô)", LR(), cat, num)
run("A HistGB: đầy đủ (có tháng+vĩ mô)", HG(), cat, num)
run("B Logistic: bỏ vĩ mô", LR(), cat, base)
run("B HistGB: bỏ vĩ mô", HG(), cat, base)
run("C Logistic: bỏ vĩ mô + tháng", LR(), cat_nm, base)
run("C HistGB: bỏ vĩ mô + tháng", HG(), cat_nm, base)
run("[Sens] C Logistic + campaign", LR(), cat_nm, base + ["log_campaign"])
run("[Sens] C Logistic + campaign + duration (RÒ RỈ)", LR(), cat_nm, base + ["log_campaign", "log_duration"])
R = pd.DataFrame(rows); R.to_csv(O + "metrics.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(R.round(3).to_string())

# permutation importance on test, main model (grouped by original column)
best = "B Logistic: bỏ vĩ mô"
p, X = fitted[best]
pi = permutation_importance(p, te[X], te.y, scoring="roc_auc", n_repeats=10, random_state=42)
imp = pd.DataFrame({"feature": X, "auc_drop": pi.importances_mean, "sd": pi.importances_std}).sort_values("auc_drop", ascending=False)
imp.to_csv(O + "feature_importance.csv", index=False); print(imp.head(12).round(4))
p2, X2 = fitted["B HistGB: bỏ vĩ mô"]
pi2 = permutation_importance(p2, te[X2], te.y, scoring="roc_auc", n_repeats=10, random_state=42)
imp2 = pd.DataFrame({"feature": X2, "auc_drop": pi2.importances_mean}).sort_values("auc_drop", ascending=False)
imp2.to_csv(O + "feature_importance_hgb.csv", index=False); print(imp2.head(8).round(4))

# audit by group (test, Logistic): lift@20% per age band / marital
s = p.predict_proba(te[X])[:, 1]; t = te.assign(score=s)
t["age_band"] = pd.cut(t.age, [0, 29, 39, 49, 59, 120], labels=["<30", "30-39", "40-49", "50-59", "60+"])
t["called"] = t.score >= np.quantile(t.score, .8)
aud = []
for g in ("age_band", "marital"):
    for k, d in t.groupby(g, observed=True):
        aud.append({"group": g, "level": k, "n": len(d), "base_rate": d.y.mean(), "share_in_top20": d.called.mean(),
                    "precision_top20": d[d.called].y.mean() if d.called.any() else np.nan,
                    "recall_top20": d[d.called].y.sum() / max(d.y.sum(), 1), "auc": roc_auc_score(d.y, d.score) if d.y.nunique() > 1 else np.nan})
pd.DataFrame(aud).to_csv(O + "audit_by_group.csv", index=False); print(pd.DataFrame(aud).round(3))

# charts
T = R[R.set == "test"].set_index("model")
names = ["Baseline: gọi ngẫu nhiên", "Baseline: luật poutcome=success", "B Logistic: bỏ vĩ mô", "B HistGB: bỏ vĩ mô"]
fig, ax = plt.subplots(figsize=(9, 5))
v = [T.loc[m, "precision@20%"] * 100 for m in names]
bars = ax.bar(["Gọi ngẫu nhiên", "Luật: từng đăng ký\nở chiến dịch trước", "Logistic\n(chọn trên validation)", "Gradient\nBoosting"], v,
              color=["#b0b0b0", "#b0b0b0", "#1f77b4", "#1f77b4"])
for b_, x in zip(bars, v): ax.text(b_.get_x() + b_.get_width() / 2, x + .5, f"{x:.1f}%", ha="center")
ax.set_ylabel("% khách đăng ký trong 20% khách được gọi trước (tập test)")
ax.set_title(f"Logistic: top 20% đạt {v[2]:.0f}% đăng ký (ngẫu nhiên {v[0]:.0f}%), nhưng luật đơn giản còn nhỉnh hơn {v[1]:.0f}%", fontsize=11)
plt.tight_layout(); plt.savefig(O + "precision_top20.png", dpi=130); plt.close()

groups = {"Lịch sử chiến dịch trước (pdays, previous, poutcome)": ["pdays_val", "pdays_contacted", "log_previous", "poutcome"],
          "Loại liên lạc (contact)": ["contact"], "Nghề nghiệp (job)": ["job"], "Học vấn (education)": ["education"],
          "Tín dụng (default, housing, loan)": ["default", "housing", "loan"], "Ngày trong tuần": ["day_of_week"]}
rng = np.random.RandomState(42); base_auc = roc_auc_score(te.y, p.predict_proba(te[X])[:, 1]); gi = []
for g, cols in groups.items():
    drops = []
    for _ in range(20):
        Xp = te[X].copy(); perm = rng.permutation(len(Xp)); Xp[cols] = Xp[cols].values[perm]
        drops.append(base_auc - roc_auc_score(te.y, p.predict_proba(Xp)[:, 1]))
    gi.append({"group": g, "auc_drop": np.mean(drops), "sd": np.std(drops)})
gi = pd.DataFrame(gi).sort_values("auc_drop", ascending=False); gi.to_csv(O + "feature_group_importance.csv", index=False); print(gi.round(4))
top = gi.iloc[::-1]
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.barh(top.group, top.auc_drop, xerr=top.sd, color="#1f77b4")
ax.set_xlabel("Mức giảm ROC-AUC khi xáo trộn nhóm biến (tập test)")
ax.set_title("Lịch sử chiến dịch trước là nhóm yếu tố dự báo quan trọng nhất")
plt.tight_layout(); plt.savefig(O + "feature_importance.png", dpi=130); plt.close()

# reference only: random stratified 5-fold CV (NOT a future-looking estimate)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
cv = StratifiedKFold(5, shuffle=True, random_state=42)
cvr = []
for nm, c, nu in (("A Logistic đầy đủ", cat, num), ("C Logistic bỏ vĩ mô+tháng", cat_nm, base)):
    sc = cross_val_predict(mk(LR(), c, nu), df[c + nu], df.y, cv=cv, method="predict_proba")[:, 1]
    cvr.append(metrics(nm, df.y.values, sc, "random-CV"))
pd.DataFrame(cvr).to_csv(O + "metrics_random_cv_reference.csv", index=False)
print(pd.DataFrame(cvr).round(3).to_string())
