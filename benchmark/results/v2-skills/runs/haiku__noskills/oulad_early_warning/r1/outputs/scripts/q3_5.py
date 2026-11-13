"""Q3-Q5: early-warning model using only day 0-28 information.
Time-based split from the data: train = 2013B,2013J ; validation = 2014B ; test = 2014J.
Target = target_noncompletion (Fail or Withdrawn = 1; Pass/Distinction = 0)."""
import json
import pandas as pd, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix

D = "data/"
OUT = "outputs/"
K = ['code_module', 'code_presentation', 'id_student']
TARGET = 'target_noncompletion'
RECALL_GOAL = 0.70
CAP = 200

m = pd.read_csv(D + "aq3_model_table.csv")
a = pd.read_csv(D + "aq3_audit_attributes.csv")
lab = pd.read_csv(D + "aq2_diagnostic_table.csv")[K + ['final_result', 'label3']]
m = m.merge(lab, on=K, how='left', validate='one_to_one')

# only columns known at or before day 28 (all in aq3_model_table, which has no outcome columns)
FEATS = [c for c in m.columns if c not in K + ['split', TARGET, 'final_result', 'label3']]
assert not any(c.startswith('final') or 'label' in c for c in FEATS)
# tma1 fields are missing when TMA1 not submitted. Filling with 0 would make "not submitted"
# look like a score of 0 (a huge artificial effect), so fill with the TRAINING mean (neutral z=0);
# the tma1_submitted_by_d28 flag carries the "not submitted" information.
for c in ['tma1_days_before_deadline', 'tma1_score']:
    fill = m.loc[m.split == 'train', c].mean()
    m[c] = m[c].fillna(fill)
X_all = m[FEATS].astype(float)

tr = m.split == 'train'; va = m.split == 'validation'; te = m.split == 'test'
y = m[TARGET].values

def fit_lr(Xtr, ytr):
    sc = StandardScaler().fit(Xtr)
    lr = LogisticRegression(C=0.5, max_iter=5000).fit(sc.transform(Xtr), ytr)
    return sc, lr

def score_lr(sc, lr, X):
    return lr.predict_proba(sc.transform(X))[:, 1]

def fit_gb(Xtr, ytr):
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                          l2_regularization=1.0, random_state=0).fit(Xtr, ytr)

def recall_at(yt, p, thr):
    pred = p >= thr
    tp = (pred & (yt == 1)).sum()
    return tp / max((yt == 1).sum(), 1), pred.sum(), tp / max(pred.sum(), 1)

def pick_threshold(yt, p, goal=RECALL_GOAL):
    # highest threshold that still reaches the recall goal (= fewest flags, precision as high as possible)
    cands = np.unique(np.round(p, 4))[::-1]
    for t in cands:
        r, _, _ = recall_at(yt, p, t)
        if r >= goal:
            return float(t)
    return float(cands[-1])

# ---- models ----
sc, lr = fit_lr(X_all[tr], y[tr])
p_lr_va = score_lr(sc, lr, X_all[va])
p_lr_te = score_lr(sc, lr, X_all[te])
gb = fit_gb(X_all[tr], y[tr])
p_gb_va = gb.predict_proba(X_all[va])[:, 1]
p_gb_te = gb.predict_proba(X_all[te])[:, 1]

rows = []
for name, pv, pt in [('Hồi quy logistic (chính)', p_lr_va, p_lr_te), ('Gradient boosting (so sánh)', p_gb_va, p_gb_te)]:
    thr = pick_threshold(y[va], pv)
    for split, yy, pp in [('validation', y[va], pv), ('test (2014J)', y[te], pt)]:
        r, nflag, prec = recall_at(yy, pp, thr)
        rows.append(dict(mô_hình=name, tập=split, AUC=round(roc_auc_score(yy, pp), 3),
                         PR_AUC=round(average_precision_score(yy, pp), 3), ngưỡng=round(thr, 3),
                         recall=round(r, 3), precision=round(prec, 3), số_bị_cảnh_báo=int(nflag),
                         tỷ_lệ_bị_cảnh_báo=round(nflag / len(yy), 3), tỷ_lệ_không_hoàn_thành=round(yy.mean(), 3),
                         n=len(yy)))
perf = pd.DataFrame(rows)
perf.to_csv(OUT + "q3_model_performance.csv", index=False)
print(perf.to_string())

# recall-vs-flag-share curve for the chosen LR model on test
order = np.argsort(-p_lr_te)
cum = np.cumsum(y[te][order]) / y[te].sum()
share = np.arange(1, len(order) + 1) / len(order)
curve = pd.DataFrame({'tỷ_lệ_bị_cảnh_báo': share, 'recall': cum})
curve.iloc[::20].to_csv(OUT + "q3_recall_curve_test.csv", index=False)
for s in [0.1, 0.2, 0.3, 0.4, 0.5]:
    k = int(round(s * len(order)))
    print(f"top {s:.0%} flagged -> recall {cum[k-1]:.3f}")

# sensitivity: add demographics (static at registration, not day 0-28 behaviour)
aa = a[K + ['gender', 'age_band', 'disability', 'imd_band', 'highest_education']]
mm = m[K].merge(aa, on=K, how='left')
Xd = pd.concat([X_all, pd.get_dummies(mm[['gender', 'age_band', 'disability', 'imd_band', 'highest_education']].astype(str), drop_first=True).astype(float)], axis=1)
sc2, lr2 = fit_lr(Xd[tr], y[tr])
pv2 = score_lr(sc2, lr2, Xd[va]); pt2 = score_lr(sc2, lr2, Xd[te])
thr2 = pick_threshold(y[va], pv2)
r2, n2, pr2 = recall_at(y[te], pt2, thr2)
sens = dict(AUC_test=round(roc_auc_score(y[te], pt2), 3), recall_test=round(r2, 3), precision_test=round(pr2, 3))
print("sensitivity with demographics:", sens)
json.dump(sens, open(OUT + "q3_sensitivity_demographics.json", "w"), indent=2)

# ---- Q4: capacity 200 per module-presentation, test cohort 2014J ----
# final model for 2014J scoring: train on all earlier presentations (train + validation)
trv = tr | va
sc_f, lr_f = fit_lr(X_all[trv], y[trv])
m['risk_score'] = score_lr(sc_f, lr_f, X_all)
te_df = m[te].copy()
te_df['rank_in_mp'] = te_df.groupby(['code_module', 'code_presentation'])['risk_score'].rank(ascending=False, method='first')
te_df['priority'] = te_df.rank_in_mp <= CAP
# compare baselines inside same cohort
te_df['rank_clicks'] = te_df.groupby(['code_module', 'code_presentation'])['clicks_0_28'].rank(ascending=True, method='first')
te_df['priority_clicks_rule'] = te_df.rank_clicks <= CAP
q4 = []
for (mod, pres), g in te_df.groupby(['code_module', 'code_presentation']):
    tot = int(g[TARGET].sum())
    for rule in ['priority', 'priority_clicks_rule']:
        s = g[g[rule]]
        hit = int(s[TARGET].sum())
        q4.append(dict(module=mod, presentation=pres, quy_tắc={'priority': 'Điểm rủi ro mô hình (cao -> thấp)',
                                                              'priority_clicks_rule': 'Baseline: ít lượt nhấp 0-28 nhất'}[rule],
                       số_sinh_viên_cohort=len(g), số_không_hoàn_thành_thực_tế=tot,
                       số_ưu_tiên=len(s), trúng=hit, precision=round(hit / len(s), 3),
                       recall_trên_mp=round(hit / tot, 3)))
q4 = pd.DataFrame(q4)
q4.to_csv(OUT + "q4_capacity_hits.csv", index=False)
print(q4.to_string())
prio = te_df[te_df.priority][K + ['risk_score', 'rank_in_mp', TARGET, 'final_result']].sort_values(['code_module', 'rank_in_mp'])
prio.to_csv(OUT + "q4_priority_list_2014J.csv", index=False)
print("tổng ưu tiên:", len(prio), " trúng:", int(prio[TARGET].sum()))

# ---- Q5: per-student contributions (logit decomposition, standardized LR) ----
coef = lr_f.coef_[0]
Z = sc_f.transform(X_all)
contrib = Z * coef  # contribution to logit; sum + intercept = logit
c_df = pd.DataFrame(contrib, columns=FEATS, index=m.index)
pri_idx = te_df[te_df.priority].index
contrib_pri = c_df.loc[pri_idx]
top_feat = contrib_pri.idxmax(axis=1)
top_val = contrib_pri.max(axis=1)
vc = top_feat.value_counts()
print("top contributing feature in priority list:\n", vc.head(15).to_string())
contrib_pri.assign(**{'id_student': m.loc[pri_idx, 'id_student'], 'code_module': m.loc[pri_idx, 'code_module'],
                      'code_presentation': m.loc[pri_idx, 'code_presentation']}).to_csv(OUT + "q5_contributions_priority.csv", index=False)
pd.Series(coef, index=FEATS).sort_values().to_csv(OUT + "q3_lr_coefficients.csv")
pd.DataFrame({'feature': FEATS, 'coef_std': coef}).sort_values('coef_std').to_csv(OUT + "q3_lr_coefficients.csv", index=False)
pd.to_pickle(dict(FEATS=FEATS, coef=coef, mean=sc_f.mean_, scale=sc_f.scale_), OUT + "scripts/_lr_meta.pkl")
