"""OULAD early warning (ngày 0-28). Chạy từ thư mục gốc: python -I outputs/oulad_early_warning/analysis.py"""
import os, json, warnings
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve
warnings.filterwarnings('ignore')
OUT = 'outputs/oulad_early_warning'
D = 'data'
os.makedirs(OUT, exist_ok=True)
K = ['code_module', 'code_presentation', 'id_student']
m = pd.read_csv(D + '/aq3_model_table.csv')
d = pd.read_csv(D + '/aq2_diagnostic_table.csv')
w = pd.read_csv(D + '/aq1_student_week.csv')
aud = pd.read_csv(D + '/aq3_audit_attributes.csv')
params = json.load(open(D + '/aq4_decision_params.json'))


def bh(p):
    p = np.asarray(p); n = len(p); o = np.argsort(p); r = np.empty(n)
    q = p[o] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    r[o] = np.minimum(q, 1)
    return r


def cliff(x, y):
    return 2 * stats.mannwhitneyu(x, y).statistic / (len(x) * len(y)) - 1


# ---------- Q1 ----------
order = ['Pass', 'Fail', 'Withdrawn']
g = w.groupby(['label3', 'week'])[['clicks', 'active_days']].agg(['mean', 'median']).round(2)
g.columns = ['_'.join(c) for c in g.columns]
g = g.reset_index()
g.to_csv(OUT + '/q1_weekly_by_outcome.csv', index=False)
print(g.to_string())
rows = []
for wk in range(1, 5):
    s = w[w.week == wk]
    for v in ['clicks', 'active_days']:
        grp = [s[s.label3 == o][v] for o in order]
        H, p = stats.kruskal(*grp)
        r = dict(week=wk, metric=v, kruskal_H=H, p=p)
        for a, b in [('Pass', 'Fail'), ('Pass', 'Withdrawn'), ('Fail', 'Withdrawn')]:
            r['cliffs_' + a + '_vs_' + b] = cliff(s[s.label3 == a][v], s[s.label3 == b][v])
        rows.append(r)
    zero = s.groupby('label3').clicks.apply(lambda x: (x == 0).mean())
    rows.append(dict(week=wk, metric='share_zero_clicks', **{o: zero[o] for o in order}))
q1t = pd.DataFrame(rows)
q1t.to_csv(OUT + '/q1_tests.csv', index=False)
print(q1t.round(4).to_string())
tot = d.groupby('label3')[['clicks_0_28', 'active_days_0_28', 'n_sites_0_28', 'tma1_submitted_by_d28', 'tma1_on_time',
                           'no_vle_activity_0_28', 'days_since_last_active_d28']].agg(['mean', 'median']).round(2)
tot.columns = ['_'.join(c) for c in tot.columns]
tot['n'] = d.groupby('label3').size()
tot.to_csv(OUT + '/q1_total_0_28_by_outcome.csv')
print(tot.T)

# ---------- Q2 ----------
d['nc'] = d.target_noncompletion
ind = ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'active_days_w1', 'active_days_w2', 'active_days_w3', 'active_days_w4',
       'clicks_pre_start', 'active_days_pre_start', 'clicks_0_28', 'active_days_0_28', 'n_sites_0_28', 'days_since_last_active_d28',
       'clicks_homepage_0_28', 'clicks_oucontent_0_28', 'clicks_resource_0_28', 'clicks_subpage_0_28', 'clicks_forumng_0_28',
       'clicks_quiz_0_28', 'clicks_url_0_28', 'tma1_submitted_by_d28', 'tma1_on_time', 'tma1_days_before_deadline', 'tma1_score',
       'clicks_change_w1_w4', 'num_of_prev_attempts', 'studied_credits', 'highest_education_ord', 'registration_lead_days']
rows = []
for v in ind:
    a, b = d[d.nc == 0][v].dropna(), d[d.nc == 1][v].dropna()
    U, p = stats.mannwhitneyu(a, b)
    per = []
    for _, s in d.groupby(['code_module', 'code_presentation']):
        per.append(cliff(s[s.nc == 0][v].dropna(), s[s.nc == 1][v].dropna()))
    rows.append(dict(indicator=v, median_complete=a.median(), median_noncomplete=b.median(), mean_complete=a.mean(),
                     mean_noncomplete=b.mean(), cliffs_delta=2 * U / (len(a) * len(b)) - 1, p=p,
                     delta_min_8_cohorts=min(per), delta_max_8_cohorts=max(per),
                     same_sign_all_cohorts=bool((np.sign(per) == np.sign(np.mean(per))).all())))
q2 = pd.DataFrame(rows)
q2['p_fdr'] = bh(q2.p)
q2['meaningful'] = (q2.p_fdr < 0.01) & (q2.cliffs_delta.abs() >= 0.1)
q2 = q2.sort_values('cliffs_delta', key=abs, ascending=False)
q2.to_csv(OUT + '/q2_indicator_tests.csv', index=False)
print(q2[['indicator', 'median_complete', 'median_noncomplete', 'cliffs_delta', 'p_fdr', 'meaningful', 'same_sign_all_cohorts']].round(3).to_string())
wk = w.merge(d[K + ['nc']], on=K).sort_values(K + ['week'])
wk['cum_clicks'] = wk.groupby(K).clicks.cumsum()
wk['cum_days'] = wk.groupby(K).active_days.cumsum()
rows = []
for k in range(1, 5):
    s = wk[wk.week == k]
    for v in ['clicks', 'active_days', 'cum_clicks', 'cum_days']:
        a, b = s[s.nc == 0][v], s[s.nc == 1][v]
        U, p = stats.mannwhitneyu(a, b)
        rows.append(dict(week=k, metric=v, median_complete=a.median(), median_noncomplete=b.median(),
                         cliffs_delta=2 * U / (len(a) * len(b)) - 1, p=p))
q2w = pd.DataFrame(rows)
q2w.to_csv(OUT + '/q2_by_week.csv', index=False)
print(q2w.round(4).to_string())

# ---------- Q3 ----------
excl = set(K + ['split', 'target_noncompletion', 'flag_high_activity'])
feats = [c for c in m.columns if c not in excl]
m['tma1_days_before_deadline_na'] = m.tma1_days_before_deadline.isna().astype(int)
m['tma1_score_na'] = m.tma1_score.isna().astype(int)
cols = feats + ['tma1_days_before_deadline_na', 'tma1_score_na']
X = m[cols].copy()
tr, va, te = [(m.split == s).values for s in ['train', 'validation', 'test']]
X = X.fillna(X[tr].median())
y = m.target_noncompletion.values
sc = StandardScaler().fit(X[tr])
Xs = pd.DataFrame(sc.transform(X), columns=X.columns, index=X.index)
models = {'Logistic (L2)': LogisticRegression(C=0.1, max_iter=2000),
          'GradientBoosting': HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=250,
                                                              l2_regularization=1.0, random_state=0)}


def pick_thr(ys, ps, target=0.70):
    P, R, T = precision_recall_curve(ys, ps)
    ok = np.where(R[:-1] >= target)[0]
    return T[ok[-1]]


res = []
scores = {}
base = -m.log_clicks_0_28.values
for name in list(models) + ['Baseline: ít click 0-28']:
    if name in models:
        models[name].fit(Xs[tr], y[tr])
        s_ = models[name].predict_proba(Xs)[:, 1]
    else:
        s_ = base
    scores[name] = s_
    thr = pick_thr(y[va], s_[va])
    for sp, msk in [('validation', va), ('test', te)]:
        pred = s_[msk] >= thr
        yy = y[msk]
        res.append(dict(model=name, split=sp, auc=roc_auc_score(yy, s_[msk]), pr_auc=average_precision_score(yy, s_[msk]),
                        base_rate=yy.mean(), threshold_from_val=thr, flagged_share=pred.mean(),
                        recall=(pred & (yy == 1)).sum() / yy.sum(), precision=(pred & (yy == 1)).sum() / max(pred.sum(), 1)))
q3 = pd.DataFrame(res)
q3.to_csv(OUT + '/q3_model_metrics.csv', index=False)
print(q3.round(3).to_string())
cand = q3[(q3.split == 'validation') & (~q3.model.str.startswith('Baseline'))].sort_values('auc')
best = cand.iloc[-1].model
print('BEST', best)
rng = np.random.default_rng(0)
idx = np.where(te)[0]
bs = []
for _ in range(500):
    b = rng.choice(idx, len(idx))
    bs.append(roc_auc_score(y[b], scores[best][b]))
ci = list(np.percentile(bs, [2.5, 97.5]))
print('AUC test 95% CI', ci)
json.dump(dict(best=best, auc_ci=ci), open(OUT + '/q3_best.json', 'w'))
P, R, T = precision_recall_curve(y[te], scores[best][te])
pd.DataFrame(dict(recall=R[:-1], precision=P[:-1], threshold=T)).to_csv(OUT + '/q3_pr_curve_test.csv', index=False)
thr = pick_thr(y[va], scores[best][va])
t = m[te][K].copy()
t['y'] = y[te]
t['flag'] = scores[best][te] >= thr
t = t.merge(aud, on=K)
rows = []
for col in ['gender', 'age_band', 'disability', 'highest_education', 'code_module']:
    for lv, s in t.groupby(col):
        rows.append(dict(attr=col, level=lv, n=len(s), noncompl_rate=s.y.mean(),
                         recall=(s.flag & (s.y == 1)).sum() / max((s.y == 1).sum(), 1), flagged_share=s.flag.mean()))
au = pd.DataFrame(rows)
au.to_csv(OUT + '/q3_group_audit.csv', index=False)
print(au.round(3).to_string())

# ---------- Q4 ----------
tt = m[te][K].copy()
tt['y'] = y[te]
tt['score'] = scores[best][te]
tt['rule_low_clicks'] = base[te]
tt['rule_no_tma1'] = (1 - m[te].tma1_submitted_by_d28.values) * 1e6 + base[te]
rows = []
for (mod, pres), s in tt.groupby(['code_module', 'code_presentation']):
    P_ = s.y.sum()
    for kk in params['capacity_k_per_module_presentation']:
        for rname, col in [('Mô hình (điểm rủi ro)', 'score'), ('Quy tắc: ít click nhất', 'rule_low_clicks'),
                           ('Quy tắc: chưa nộp TMA1 rồi ít click', 'rule_no_tma1')]:
            h = s.nlargest(kk, col).y.sum()
            rows.append(dict(module=mod, presentation=pres, K=kk, rule=rname, n_students=len(s), n_noncompleters=P_, hits=h,
                             precision=h / kk, recall=h / P_, lift=(h / kk) / (P_ / len(s)),
                             expected_helped=h * params['assumed_conversion_rate']))
        rs = np.mean([s.sample(kk, random_state=i).y.sum() for i in range(200)])
        rows.append(dict(module=mod, presentation=pres, K=kk, rule='Ngẫu nhiên (TB 200 lần)', n_students=len(s), n_noncompleters=P_,
                         hits=rs, precision=rs / kk, recall=rs / P_, lift=1.0, expected_helped=rs * params['assumed_conversion_rate']))
    ss = s.sort_values('score', ascending=False)
    cum = ss.y.cumsum().values
    need = int(np.argmax(cum >= 0.7 * P_)) + 1
    rows.append(dict(module=mod, presentation=pres, K=need, rule='K cần để recall 70% (mô hình)', n_students=len(s),
                     n_noncompleters=P_, hits=cum[need - 1], precision=cum[need - 1] / need, recall=cum[need - 1] / P_))
q4 = pd.DataFrame(rows)
q4.to_csv(OUT + '/q4_topk.csv', index=False)
print(q4.round(3).to_string())

# ---------- Q5 ----------
mdl = models[best]
coef = pd.Series(models['Logistic (L2)'].coef_[0], index=Xs.columns)
sel = pd.concat([s_.nlargest(200, 'score') for _, s_ in tt.groupby(['code_module', 'code_presentation'])])
tong = ['clicks_0_28', 'log_clicks_0_28', 'active_days_0_28', 'n_sites_0_28', 'no_vle_activity_0_28']
tuan = [c for c in cols if c.startswith('clicks_w') or c.startswith('active_days_w') or c == 'clicks_change_w1_w4']
kenh = [c for c in cols if c.startswith('clicks_') and c.endswith('_0_28') and c not in tong]
tru = ['clicks_pre_start', 'active_days_pre_start']


def gname(f):
    if f.startswith('tma1'): return 'tma1'
    if f in tong: return 'tong'
    if f in tuan: return 'tuan'
    if f in kenh: return 'kenh'
    if f in tru: return 'truoc'
    if f == 'days_since_last_active_d28': return 'cuoi'
    return f


Xte = Xs.loc[sel.index]
med_s = Xs[tr].median()
base_logit = mdl.decision_function(Xte)
gmap = {}
for f in Xs.columns:
    gmap.setdefault(gname(f), []).append(f)
contrib = pd.DataFrame(index=sel.index)
for gn, fs in gmap.items():
    Xo = Xte.copy()
    Xo[fs] = med_s[fs].values
    contrib[gn] = base_logit - mdl.decision_function(Xo)  # >0: nhóm này đẩy rủi ro lên so với sinh viên điển hình
contrib.to_csv(OUT + '/q5_group_contributions_priority.csv')
out = []
for i, r in sel.iterrows():
    grp = contrib.loc[i].to_dict()
    top = [(a, b) for a, b in sorted(grp.items(), key=lambda x: -x[1]) if b > 0][:3]
    xr = m.loc[i]

    def phrase(gn):
        if gn == 'tma1':
            if xr.tma1_submitted_by_d28 == 0: return 'chưa nộp bài kiểm tra TMA1 đầu tiên'
            if xr.tma1_score < 60: return 'điểm TMA1 chỉ ' + str(int(xr.tma1_score))
            return 'nộp TMA1 sát hạn hoặc muộn'
        if gn == 'tong': return 'tổng hoạt động trên hệ thống học tập thấp (%d lượt click, %d ngày vào học trong 28 ngày)' % (xr.clicks_0_28, xr.active_days_0_28)
        if gn == 'tuan': return 'hoạt động từng tuần thấp hoặc giảm dần (tuần 1-4: %d/%d/%d/%d lượt click)' % (xr.clicks_w1, xr.clicks_w2, xr.clicks_w3, xr.clicks_w4)
        if gn == 'cuoi': return 'đã %d ngày chưa vào học tính đến ngày 28' % xr.days_since_last_active_d28
        if gn == 'kenh': return 'ít dùng nội dung học chính (oucontent/quiz/forum)'
        if gn == 'truoc': return 'ít hoạt động trước khi khóa bắt đầu'
        if gn == 'num_of_prev_attempts': return 'đã từng học module này %d lần trước' % xr.num_of_prev_attempts
        if gn == 'studied_credits': return 'đang học nhiều tín chỉ cùng lúc (%d)' % xr.studied_credits
        if gn == 'highest_education_ord': return 'trình độ học vấn đầu vào thấp'
        if gn == 'registration_lead_days': return 'đăng ký sát ngày bắt đầu khóa'
        if gn == 'seen_in_earlier_presentation': return 'đã xuất hiện ở kỳ học trước'
        return gn
    ph = [phrase(a) for a, _ in top]
    txt = ('Sinh viên này được ưu tiên chủ yếu vì ' + '; '.join(ph) + '. Nên liên hệ sớm để hỏi về khó khăn và giúp bắt kịp tiến độ.')
    out.append(dict(code_module=r.code_module, code_presentation=r.code_presentation, id_student=r.id_student,
                    risk_score=round(r.score, 4), actual_noncompletion=r.y,
                    top1=top[0][0] if top else '', top2=top[1][0] if len(top) > 1 else '', top3=top[2][0] if len(top) > 2 else '',
                    contrib_top1=round(top[0][1], 3) if top else 0, explanation_vi=txt))
q5 = pd.DataFrame(out)
q5['rank_in_group'] = q5.groupby(['code_module', 'code_presentation']).risk_score.rank(ascending=False, method='first').astype(int)
q5 = q5.sort_values(['code_module', 'code_presentation', 'rank_in_group'])
q5.to_csv(OUT + '/q5_priority_list_with_explanations.csv', index=False)
print(q5.top1.value_counts())
print(q5.groupby('top1').size() / len(q5))
for t_ in q5.head(3).explanation_vi: print(t_)
tt.to_csv(OUT + '/_test_scores.csv', index=False)
coef.sort_values().to_csv(OUT + '/q3_lr_coefficients.csv')
