import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.inspection import permutation_importance

OUT = "outputs/du_doan_dang_ky"
os.makedirs(OUT, exist_ok=True)
df = pd.read_csv("data/bank-additional/bank-additional-full.csv", sep=";")
print(df.shape, "dup rows:", df.duplicated().sum(), df.y.value_counts(normalize=True).to_dict())
df["target"] = (df.y == "yes").astype(int)
df["pdays_contacted"] = (df.pdays != 999).astype(int)
df["pdays"] = df.pdays.replace(999, np.nan)

# file is ordered by date -> temporal split 70/30
n = len(df)
cut = int(n * 0.7)
tr, te = df.iloc[:cut], df.iloc[cut:]
yte = te.target.values
base = yte.mean()
print("train rate", tr.target.mean(), "test rate", base)

client = ["age", "job", "marital", "education", "default", "housing", "loan"]
contact = ["contact", "month", "day_of_week"]
hist = ["pdays", "previous", "poutcome", "pdays_contacted"]
macro = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
A = "A. Khách hàng + lịch sử"
B = "B. A + kênh/tháng/thứ"
C = "C. B + vĩ mô"
sets = {A: client + hist, B: client + hist + contact, C: client + hist + contact + macro}


def prep(cols, scale):
    cat = [c for c in cols if not pd.api.types.is_numeric_dtype(df[c])]
    num = [c for c in cols if c not in cat]
    nt = make_pipeline(SimpleImputer(strategy="median"), StandardScaler()) if scale else "passthrough"
    return ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat), ("n", nt, num)])


def gb(cols):
    return make_pipeline(prep(cols, False), HistGradientBoostingClassifier(
        max_depth=4, learning_rate=0.05, max_iter=250, l2_regularization=1.0, random_state=0))


def lg(cols):
    return make_pipeline(prep(cols, True), LogisticRegression(max_iter=2000, C=0.3))


def topk(y, s, k):
    m = int(len(y) * k)
    idx = np.argsort(-s)[:m]
    return y[idx].sum() / y.sum(), y[idx].mean() / y.mean()


def row(name, feats, s):
    return dict(mo_hinh=name, bo_bien=feats, auc=roc_auc_score(yte, s), pr_auc=average_precision_score(yte, s),
                thu_hoi_top10=topk(yte, s, .1)[0], lift_top10=topk(yte, s, .1)[1],
                thu_hoi_top20=topk(yte, s, .2)[0], lift_top20=topk(yte, s, .2)[1])


rows = [dict(mo_hinh="Baseline 1: ngẫu nhiên (tỷ lệ chung)", bo_bien="-", auc=0.5, pr_auc=base,
             thu_hoi_top10=.1, lift_top10=1.0, thu_hoi_top20=.2, lift_top20=1.0)]
rule = (te.poutcome == "success").astype(float).values + np.random.RandomState(0).rand(len(te)) * 1e-6
rows.append(row("Baseline 2: quy tắc poutcome=success", "poutcome", rule))
scores = {}
for name, cols in sets.items():
    for mn, f in [("Logistic", lg), ("Gradient Boosting", gb)]:
        m = f(cols).fit(tr[cols], tr.target)
        p = m.predict_proba(te[cols])[:, 1]
        scores[(name, mn)] = p
        rows.append(row(mn, name, p))
for extra, label in [("campaign", "C + campaign (độ nhạy)"), ("duration", "C + duration (RÒ RỈ - chỉ minh họa)")]:
    cols = sets[C] + [extra]
    p = gb(cols).fit(tr[cols], tr.target).predict_proba(te[cols])[:, 1]
    rows.append(row("Gradient Boosting", label, p))
res = pd.DataFrame(rows).round(4)
res.to_csv(f"{OUT}/ket_qua_mo_hinh.csv", index=False)
print(res.to_string())

pm = scores[(C, "Gradient Boosting")]
rs = np.random.RandomState(1)
a, d = [], []
for _ in range(300):
    i = rs.randint(0, len(yte), len(yte))
    a.append(roc_auc_score(yte[i], pm[i]))
    d.append(roc_auc_score(yte[i], pm[i]) - roc_auc_score(yte[i], rule[i]))
print("AUC CI", np.percentile(a, [2.5, 97.5]), "diff vs rule CI", np.percentile(d, [2.5, 97.5]))

# rolling-origin check: 10 consecutive blocks, train on all earlier blocks, test on the next
from sklearn.model_selection import StratifiedKFold
blk = pd.cut(np.arange(n), 10, labels=False)
out = []
for k in range(6, 10):
    trk, tek = df[blk < k], df[blk == k]
    r = dict(khoi_test=k + 1, ty_le_dang_ky=tek.target.mean())
    ru = (tek.poutcome == "success").astype(float).values + np.random.RandomState(0).rand(len(tek)) * 1e-6
    r["auc_quy_tac"] = roc_auc_score(tek.target, ru)
    for nm, cols in [("A", sets[A]), ("B", sets[B]), ("C", sets[C])]:
        m = gb(cols).fit(trk[cols], trk.target)
        r["auc_GB_" + nm] = roc_auc_score(tek.target, m.predict_proba(tek[cols])[:, 1])
    out.append(r)
roll = pd.DataFrame(out).round(4)
roll.to_csv(f"{OUT}/kiem_tra_theo_thoi_gian.csv", index=False)
print(roll.to_string()); print(roll.mean().round(4))

# random stratified 5-fold CV (optimistic: mixes periods) for comparison
cvr = []
for nm, cols in [("A", sets[A]), ("B", sets[B]), ("C", sets[C])]:
    for mn, f in [("Logistic", lg), ("Gradient Boosting", gb)]:
        au, pr = [], []
        for t_, v_ in StratifiedKFold(5, shuffle=True, random_state=0).split(df, df.target):
            m = f(cols).fit(df.iloc[t_][cols], df.iloc[t_].target)
            pp = m.predict_proba(df.iloc[v_][cols])[:, 1]
            au.append(roc_auc_score(df.iloc[v_].target, pp)); pr.append(average_precision_score(df.iloc[v_].target, pp))
        cvr.append(dict(mo_hinh=mn, bo_bien=nm, auc=np.mean(au), auc_sd=np.std(au), pr_auc=np.mean(pr)))
rule_all = (df.poutcome == "success").astype(float).values
cvr.append(dict(mo_hinh="Quy tắc poutcome=success", bo_bien="-", auc=roc_auc_score(df.target, rule_all), auc_sd=np.nan, pr_auc=average_precision_score(df.target, rule_all)))
cvr.append(dict(mo_hinh="Ngẫu nhiên", bo_bien="-", auc=.5, auc_sd=np.nan, pr_auc=df.target.mean()))
cvr = pd.DataFrame(cvr).round(4); cvr.to_csv(f"{OUT}/ket_qua_cv_ngau_nhien.csv", index=False); print(cvr.to_string())


def imp(cols, fn):
    m = gb(cols).fit(tr[cols], tr.target)
    r = permutation_importance(m, te[cols], te.target, scoring="roc_auc", n_repeats=8, random_state=0)
    t = pd.DataFrame({"bien": cols, "giam_auc": r.importances_mean, "sd": r.importances_std}).sort_values("giam_auc", ascending=False)
    t.round(4).to_csv(fn, index=False)
    return t


iC = imp(sets[C], f"{OUT}/do_quan_trong_C.csv")
iB = imp(sets[B], f"{OUT}/do_quan_trong_B_khong_vi_mo.csv")
print(iC.round(4).to_string())
print(iB.round(4).to_string())

te2 = te.copy()
te2["p"] = pm
te2["decile"] = pd.qcut(te2.p.rank(method="first", ascending=False), 10, labels=range(1, 11))
dt = te2.groupby("decile", observed=True).agg(so_kh=("target", "size"), dang_ky=("target", "sum"), ty_le=("target", "mean")).reset_index()
dt["lift"] = dt.ty_le / base
dt["thu_hoi_luy_ke"] = dt.dang_ky.cumsum() / dt.dang_ky.sum()
dt.round(4).to_csv(f"{OUT}/bang_decile.csv", index=False)
print(dt.round(3).to_string())

for c in ["poutcome", "contact", "month"]:
    print(df.groupby(c).target.agg(["mean", "size"]).sort_values("mean", ascending=False).round(3).to_string())
print(df.groupby(pd.cut(np.arange(n), 5)).target.mean())

C1, C2 = "#1f77b4", "#9aa5b1"
fig, ax = plt.subplots(figsize=(8.5, 4.8))
lab = ["Ngẫu nhiên", "Quy tắc\n'lần trước thành công'", "Logistic\n(A)", "Gradient Boosting\n(C: đầy đủ)"]
vals = [.5, res.auc[1], res[(res.mo_hinh == "Logistic") & (res.bo_bien == A)].auc.iloc[0],
        res[(res.mo_hinh == "Gradient Boosting") & (res.bo_bien == C)].auc.iloc[0]]
bars = ax.bar(lab, vals, color=[C2, C2, C2, C1])
for r, v in zip(bars, vals):
    ax.text(r.get_x() + r.get_width() / 2, v + .01, f"{v:.3f}", ha="center")
ax.set_ylim(.4, .85)
ax.set_ylabel("ROC AUC (tập kiểm tra theo thời gian)")
ax.set_title("Mô hình xếp hạng khách hàng tốt hơn rõ rệt so với baseline")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/so_sanh_baseline.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(8, 4.8))
x = np.r_[0, dt.index.values + 1] / 10
y = np.r_[0, dt.thu_hoi_luy_ke.values]
ax.plot(x, y, color=C1, marker="o", label="Mô hình (Gradient Boosting)")
ax.plot([0, 1], [0, 1], color=C2, ls="--", label="Gọi ngẫu nhiên")
t20 = dt.thu_hoi_luy_ke.iloc[1]
ax.annotate(f"Top 20%: bắt {t20:.0%}", (.2, t20), xytext=(.3, t20 - .15), arrowprops=dict(arrowstyle="->"))
ax.set_xlabel("Tỷ lệ khách hàng được gọi (xếp theo điểm giảm dần)")
ax.set_ylabel("Tỷ lệ người đăng ký bắt được")
ax.set_title("Gọi theo thứ tự điểm số bắt được nhiều người đăng ký hơn")
ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/duong_thu_hoi.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(8, 5.2))
t = iC.head(10)[::-1]
ax.barh(t.bien, t.giam_auc, xerr=t.sd, color=C1)
ax.set_xlabel("Mức giảm AUC khi xáo trộn biến (tập kiểm tra)")
ax.set_title("Các yếu tố quan trọng nhất (mô hình đầy đủ)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/do_quan_trong.png", dpi=150); plt.close()

# ===== Random stratified hold-out (75/25): within-period estimate =====
from sklearn.model_selection import train_test_split
itr, ite = train_test_split(np.arange(n), test_size=.25, stratify=df.target, random_state=42)
R_tr, R_te = df.iloc[itr], df.iloc[ite]
yr = R_te.target.values
baser = yr.mean()
rr = (R_te.poutcome == "success").astype(float).values + np.random.RandomState(0).rand(len(R_te)) * 1e-6


def row2(nm, ft, s):
    return dict(mo_hinh=nm, bo_bien=ft, auc=roc_auc_score(yr, s), pr_auc=average_precision_score(yr, s),
                thu_hoi_top10=topk(yr, s, .1)[0], lift_top10=topk(yr, s, .1)[1],
                thu_hoi_top20=topk(yr, s, .2)[0], lift_top20=topk(yr, s, .2)[1])


rr_rows = [dict(mo_hinh="Ngẫu nhiên", bo_bien="-", auc=.5, pr_auc=baser, thu_hoi_top10=.1, lift_top10=1,
                thu_hoi_top20=.2, lift_top20=1), row2("Quy tắc poutcome=success", "poutcome", rr)]
rp = {}
for nm, cols in [(A, sets[A]), (B, sets[B]), (C, sets[C])]:
    for mn, f in [("Logistic", lg), ("Gradient Boosting", gb)]:
        p = f(cols).fit(R_tr[cols], R_tr.target).predict_proba(R_te[cols])[:, 1]
        rp[(nm, mn)] = p
        rr_rows.append(row2(mn, nm, p))
rr_df = pd.DataFrame(rr_rows).round(4)
rr_df.to_csv(f"{OUT}/ket_qua_holdout_ngau_nhien.csv", index=False)
print(rr_df.to_string())
pb = rp[(C, "Gradient Boosting")]
bs = []
rs = np.random.RandomState(3)
for _ in range(300):
    i = rs.randint(0, len(yr), len(yr))
    bs.append((roc_auc_score(yr[i], pb[i]), roc_auc_score(yr[i], rr[i])))
bs = np.array(bs)
print("holdout AUC CI", np.percentile(bs[:, 0], [2.5, 97.5]), "rule CI", np.percentile(bs[:, 1], [2.5, 97.5]))


def imp2(cols, fn):
    m = gb(cols).fit(R_tr[cols], R_tr.target)
    r = permutation_importance(m, R_te[cols], R_te.target, scoring="roc_auc", n_repeats=8, random_state=0)
    t = pd.DataFrame({"bien": cols, "giam_auc": r.importances_mean, "sd": r.importances_std}).sort_values("giam_auc", ascending=False)
    t.round(4).to_csv(fn, index=False)
    return t


i2C = imp2(sets[C], f"{OUT}/do_quan_trong_holdout_C.csv")
i2B = imp2(sets[B], f"{OUT}/do_quan_trong_holdout_B_khong_vi_mo.csv")
print(i2C.round(4).to_string())
print(i2B.round(4).to_string())

R2 = R_te.copy()
R2["p"] = pb
R2["decile"] = pd.qcut(R2.p.rank(method="first", ascending=False), 10, labels=range(1, 11))
d2 = R2.groupby("decile", observed=True).agg(so_kh=("target", "size"), dang_ky=("target", "sum"), ty_le=("target", "mean")).reset_index()
d2["lift"] = d2.ty_le / baser
d2["thu_hoi_luy_ke"] = d2.dang_ky.cumsum() / d2.dang_ky.sum()
d2.round(4).to_csv(f"{OUT}/bang_decile_holdout.csv", index=False)
print(d2.round(3).to_string())

# charts (overwrite earlier ones)
fig, ax = plt.subplots(figsize=(9.5, 4.8))
labs = ["Ngẫu nhiên", "Quy tắc\n'lần trước thành công'", "Logistic\n(C)", "Gradient Boosting\n(C)"]
g = lambda mn: rr_df[(rr_df.mo_hinh == mn) & (rr_df.bo_bien == C)].auc.iloc[0]
v1 = [.5, rr_df.auc[1], g("Logistic"), g("Gradient Boosting")]
v2 = [.5, roll.auc_quy_tac.mean(), np.nan, roll.auc_GB_C.mean()]
x = np.arange(4)
w = .38
b1 = ax.bar(x - w / 2, v1, w, color=C1, label="Kiểm tra ngẫu nhiên (cùng giai đoạn)")
b2 = ax.bar(x + w / 2, v2, w, color=C2, label="Kiểm tra theo thời gian (train quá khứ, test giai đoạn sau)")
for bars in (b1, b2):
    for r_ in bars:
        h = r_.get_height()
        if not np.isnan(h):
            ax.text(r_.get_x() + r_.get_width() / 2, h + .008, f"{h:.2f}", ha="center")
ax.set_xticks(x)
ax.set_xticklabels(labs)
ax.set_ylim(.4, .95)
ax.set_ylabel("ROC AUC")
ax.set_title("Mô hình vượt baseline, nhưng lợi thế co lại khi dự báo giai đoạn sau")
ax.legend(frameon=False, loc="upper left", fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/so_sanh_baseline.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(8, 4.8))
x = np.r_[0, d2.index.values + 1] / 10
y = np.r_[0, d2.thu_hoi_luy_ke.values]
ax.plot(x, y, color=C1, marker="o", label="Mô hình (Gradient Boosting)")
ax.plot([0, 1], [0, 1], color=C2, ls="--", label="Gọi ngẫu nhiên")
t20 = d2.thu_hoi_luy_ke.iloc[1]
ax.annotate(f"Gọi 20% đầu bảng: bắt {t20:.0%} người đăng ký", (.2, t20), xytext=(.3, t20 - .18), arrowprops=dict(arrowstyle="->"))
ax.set_xlabel("Tỷ lệ khách hàng được gọi (xếp theo điểm giảm dần)")
ax.set_ylabel("Tỷ lệ người đăng ký bắt được")
ax.set_title("Xếp hạng theo điểm số giúp bắt nhiều người đăng ký hơn")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/duong_thu_hoi.png", dpi=150); plt.close()

fig, axs = plt.subplots(1, 2, figsize=(12, 5.2))
for ax, t, ttl in [(axs[0], i2C, "Mô hình đầy đủ (có vĩ mô)"), (axs[1], i2B, "Không có chỉ số vĩ mô")]:
    t = t.head(8)[::-1]
    ax.barh(t.bien, t.giam_auc, xerr=t.sd, color=C1)
    ax.set_title(ttl)
    ax.set_xlabel("Mức giảm AUC khi xáo trộn biến")
    ax.spines[["top", "right"]].set_visible(False)
plt.suptitle("Yếu tố quan trọng nhất (hold-out ngẫu nhiên)")
plt.tight_layout(); plt.savefig(f"{OUT}/do_quan_trong.png", dpi=150); plt.close()
