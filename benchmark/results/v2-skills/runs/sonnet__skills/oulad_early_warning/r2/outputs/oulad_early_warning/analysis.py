import pandas as pd, numpy as np, json, warnings
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, confusion_matrix
warnings.filterwarnings('ignore')
O = 'outputs/oulad_early_warning/'
plt.rcParams.update({'figure.dpi': 130, 'axes.spines.top': False, 'axes.spines.right': False})
COL = {'Pass': '#2a9d8f', 'Fail': '#e9c46a', 'Withdrawn': '#d1495b'}
W = pd.read_csv('data/aq1_student_week.csv'); D = pd.read_csv('data/aq2_diagnostic_table.csv')
M = pd.read_csv('data/aq3_model_table.csv'); A = pd.read_csv('data/aq3_audit_attributes.csv')
P = json.load(open('data/aq4_decision_params.json'))
key = ['code_module', 'code_presentation', 'id_student']

# consistency aq1 vs aq2
chk = W.pivot_table(index=key, columns='week', values='clicks').reset_index().merge(
    D[key + ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4']], on=key)
print('aq1 vs aq2 weekly clicks mismatches:', sum((chk[i] != chk['clicks_w%d' % i]).sum() for i in range(1, 5)))

# ---------------- Q1 ----------------
q1 = []
for lab, x in D.groupby('label3'):
    r = {'label3': lab, 'n': len(x)}
    for w in range(1, 5):
        r['median_clicks_w%d' % w] = x['clicks_w%d' % w].median()
        r['mean_clicks_w%d' % w] = x['clicks_w%d' % w].mean()
        r['mean_active_days_w%d' % w] = x['active_days_w%d' % w].mean()
        r['pct_zero_clicks_w%d' % w] = (x['clicks_w%d' % w] == 0).mean() * 100
    r['median_clicks_0_28'] = x.clicks_0_28.median()
    r['pct_no_vle_0_28'] = x.no_vle_activity_0_28.mean() * 100
    r['pct_tma1_submitted'] = x.tma1_submitted_by_d28.mean() * 100
    r['median_days_since_last_active'] = x.days_since_last_active_d28.median()
    q1.append(r)
q1 = pd.DataFrame(q1).round(2); q1.to_csv(O + 'q1_group_profile.csv', index=False)
print(q1.T.to_string())
for v in ['clicks_0_28', 'active_days_0_28']:
    print(v, 'Kruskal', stats.kruskal(*[x[v] for _, x in D.groupby('label3')]))
# pairwise Fail vs Withdrawn and Pass vs each
for a, b in [('Pass', 'Fail'), ('Pass', 'Withdrawn'), ('Fail', 'Withdrawn')]:
    xa = D.loc[D.label3 == a, 'clicks_0_28']; xb = D.loc[D.label3 == b, 'clicks_0_28']
    u, p = stats.mannwhitneyu(xa, xb); print(a, 'vs', b, 'clicks_0_28 rbc=%.3f p=%.2g' % (2 * u / (len(xa) * len(xb)) - 1, p))

# ---------------- Q2 ----------------
D['nc'] = D.target_noncompletion
feats = ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'active_days_w1', 'active_days_w2', 'active_days_w3',
         'active_days_w4', 'clicks_0_28', 'active_days_0_28', 'n_sites_0_28', 'days_since_last_active_d28',
         'clicks_pre_start', 'active_days_pre_start', 'clicks_homepage_0_28', 'clicks_oucontent_0_28',
         'clicks_resource_0_28', 'clicks_subpage_0_28', 'clicks_forumng_0_28', 'clicks_quiz_0_28', 'clicks_url_0_28',
         'tma1_submitted_by_d28', 'tma1_on_time', 'tma1_days_before_deadline', 'registration_lead_days',
         'num_of_prev_attempts', 'studied_credits']
rows = []
for f in feats:
    a = D.loc[D.nc == 0, f].dropna(); b = D.loc[D.nc == 1, f].dropna()
    u, p = stats.mannwhitneyu(a, b); auc = u / (len(a) * len(b))
    rows.append({'feature': f, 'median_complete': a.median(), 'median_noncomplete': b.median(),
                 'mean_complete': a.mean(), 'mean_noncomplete': b.mean(), 'auc_complete_gt_non': auc,
                 'effect_rbc': 2 * auc - 1, 'p': p})
q2 = pd.DataFrame(rows); n = len(q2); o = q2.p.sort_values().index
q2['p_holm'] = np.nan; run = 0
for i, ix in enumerate(o):
    run = max(run, min(1, q2.p[ix] * (n - i))); q2.loc[ix, 'p_holm'] = run
q2['significant_holm'] = q2.p_holm < 0.05
q2 = q2.sort_values('effect_rbc', key=abs, ascending=False).round(4)
q2.to_csv(O + 'q2_noncompleter_vs_completer.csv', index=False); print(q2.to_string())

wk = []
for (m, pr), x in D.groupby(['code_module', 'code_presentation']):
    for w in range(1, 5):
        a = x.loc[x.nc == 0, 'clicks_w%d' % w]; b = x.loc[x.nc == 1, 'clicks_w%d' % w]
        u, p = stats.mannwhitneyu(a, b)
        wk.append({'module': m, 'presentation': pr, 'week': w, 'median_complete': a.median(), 'median_non': b.median(),
                   'rbc': round(2 * u / (len(a) * len(b)) - 1, 3), 'p': p})
wk = pd.DataFrame(wk); wk.to_csv(O + 'q2_weekly_by_module_presentation.csv', index=False)
print(wk.groupby('week').rbc.agg(['min', 'max']), (wk.p < 0.05).groupby(wk.week).mean())

bs = np.random.default_rng(42); wrow = []
def rbc(a, b): return 2 * stats.mannwhitneyu(a, b)[0] / (len(a) * len(b)) - 1
for w in range(1, 5):
    a = D.loc[D.nc == 0, 'clicks_w%d' % w].values; b = D.loc[D.nc == 1, 'clicks_w%d' % w].values
    bt = [rbc(bs.choice(a, len(a)), bs.choice(b, len(b))) for _ in range(200)]
    wrow.append({'week': w, 'rbc': rbc(a, b), 'ci_lo': np.percentile(bt, 2.5), 'ci_hi': np.percentile(bt, 97.5),
                 'median_complete': np.median(a), 'median_non': np.median(b),
                 'pct_zero_complete': (a == 0).mean() * 100, 'pct_zero_non': (b == 0).mean() * 100,
                 'mean_active_days_complete': D.loc[D.nc == 0, 'active_days_w%d' % w].mean(),
                 'mean_active_days_non': D.loc[D.nc == 1, 'active_days_w%d' % w].mean()})
wkp = pd.DataFrame(wrow).round(3); wkp.to_csv(O + 'q2_weekly_pooled.csv', index=False); print(wkp.to_string())

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for lab in ['Pass', 'Fail', 'Withdrawn']:
    x = D[D.label3 == lab]
    ax[0].plot(range(1, 5), [x['clicks_w%d' % w].median() for w in range(1, 5)], marker='o', color=COL[lab], label='%s (n=%s)' % (lab, format(len(x), ',')))
    ax[1].plot(range(1, 5), [(x['clicks_w%d' % w] == 0).mean() * 100 for w in range(1, 5)], marker='o', color=COL[lab], label=lab)
ax[0].set_title('Fail và Withdrawn đều ít click hơn Pass ngay từ tuần 1; Fail thấp nhất\n(trung vị clicks mỗi tuần)', fontsize=10)
ax[0].set_xlabel('Tuần'); ax[0].set_ylabel('Trung vị số clicks'); ax[0].legend(loc='center right', fontsize=8); ax[0].set_xticks(range(1, 5))
ax[1].set_title('Tỷ lệ sinh viên không có click nào trong tuần (%)', fontsize=10)
ax[1].set_xlabel('Tuần'); ax[1].set_ylabel('%'); ax[1].set_xticks(range(1, 5)); ax[1].legend()
plt.tight_layout(); plt.savefig(O + 'q1_tuong_tac_theo_nhom.png'); plt.close()
fig, ax = plt.subplots(figsize=(7, 4))
ax.errorbar(wkp.week, wkp.rbc, yerr=[wkp.rbc - wkp.ci_lo, wkp.ci_hi - wkp.rbc], marker='o', capsize=4, color='#d1495b')
ax.set_title('Khác biệt clicks giữa hoàn thành và không hoàn thành\nđã có từ tuần 1 (hiệu ứng rank-biserial, 95% CI)', fontsize=10)
ax.set_xlabel('Tuần'); ax.set_ylabel('Hiệu ứng'); ax.set_xticks(range(1, 5)); ax.set_ylim(0, None)
plt.tight_layout(); plt.savefig(O + 'q2_khac_biet_theo_tuan.png'); plt.close()

# ---------------- Q3 ----------------
# Feature timing audit: see answer.md. Dropped: tma1_score (release date unknown -> sensitivity only),
# flag_high_activity / days_observable_0_28 (derived flags with unclear definition), final_result/label3/audit flags (outcome-linked), sensitive attrs.
num = ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'active_days_w1', 'active_days_w2', 'active_days_w3',
       'active_days_w4', 'clicks_0_28', 'active_days_0_28', 'n_sites_0_28', 'days_since_last_active_d28',
       'clicks_pre_start', 'active_days_pre_start', 'clicks_homepage_0_28', 'clicks_oucontent_0_28',
       'clicks_resource_0_28', 'clicks_subpage_0_28', 'clicks_forumng_0_28', 'clicks_quiz_0_28', 'clicks_url_0_28',
       'tma1_submitted_by_d28', 'tma1_on_time', 'tma1_days_before_deadline', 'num_of_prev_attempts', 'studied_credits',
       'highest_education_ord', 'registration_lead_days', 'seen_in_earlier_presentation', 'late_registration_1_28',
       'no_vle_activity_0_28']
M['is_FFF'] = (M.code_module == 'FFF').astype(int)
base = num + ['is_FFF']
M['tma1_days_before_deadline'] = M.tma1_days_before_deadline.where(M.tma1_submitted_by_d28 == 1)
M['tma1_score_f'] = M.tma1_score
cnt = [c for c in base if c.startswith('clicks') or c.startswith('n_sites')]
def prep(df, cols):
    X = df[cols].copy()
    for c in cnt:
        if c in X: X[c] = np.log1p(X[c].clip(lower=0))
    return X
tr, va, te = [M[M.split == s].reset_index(drop=True) for s in ['train', 'validation', 'test']]
def lr(): return make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                               LogisticRegression(C=0.3, class_weight='balanced', max_iter=2000, random_state=42))
def hgb(): return make_pipeline(SimpleImputer(strategy='median'),
                                HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, random_state=42, class_weight='balanced'))
sets = {'main': base, 'sens_with_tma1_score': base + ['tma1_score_f']}
res = []; models = {}
for sname, cols in sets.items():
    for mname, mk in [('LogReg', lr), ('HistGB', hgb)]:
        m = mk().fit(prep(tr, cols), tr.target_noncompletion); models[(sname, mname)] = (m, cols)
        r = {'set': sname, 'model': mname}
        for nm, df in [('val', va), ('test', te)]:
            p = m.predict_proba(prep(df, cols))[:, 1]
            r['auc_' + nm] = roc_auc_score(df.target_noncompletion, p); r['prauc_' + nm] = average_precision_score(df.target_noncompletion, p)
        res.append(r)
res.append({'set': 'baseline', 'model': 'Dummy (tỷ lệ nền)', 'auc_val': 0.5, 'prauc_val': va.target_noncompletion.mean(), 'auc_test': 0.5, 'prauc_test': te.target_noncompletion.mean()})
s1 = -np.log1p(va.clicks_0_28); s2 = -np.log1p(te.clicks_0_28)
res.append({'set': 'baseline', 'model': 'Quy tắc: ít click 0-28', 'auc_val': roc_auc_score(va.target_noncompletion, s1),
            'prauc_val': average_precision_score(va.target_noncompletion, s1), 'auc_test': roc_auc_score(te.target_noncompletion, s2),
            'prauc_test': average_precision_score(te.target_noncompletion, s2)})
res = pd.DataFrame(res).round(4); res.to_csv(O + 'q3_model_comparison.csv', index=False); print(res.to_string())
mm = res[res.set == 'main'].sort_values('auc_val', ascending=False).iloc[0].model; print('chosen on validation:', mm)
model, cols = models[('main', mm)]
pv = model.predict_proba(prep(va, cols))[:, 1]; pt = model.predict_proba(prep(te, cols))[:, 1]
yv = va.target_noncompletion.values; yt = te.target_noncompletion.values
thr = None
for t in np.sort(np.unique(pv))[::-1]:
    if (pv[yv == 1] >= t).mean() >= 0.70: thr = t; break
def conf(y, p, t):
    f = p >= t; tn, fp, fn, tp = confusion_matrix(y, f).ravel()
    return dict(threshold=round(float(t), 4), flagged=int(f.sum()), flagged_pct=round(f.mean() * 100, 1), tp=tp, fp=fp, fn=fn, tn=tn,
                recall=round(tp / (tp + fn), 3), precision=round(tp / (tp + fp), 3), specificity=round(tn / (tn + fp), 3), base_rate=round(y.mean(), 3))
c3 = pd.DataFrame([{'split': 'validation', **conf(yv, pv, thr)}, {'split': 'test', **conf(yt, pt, thr)}])
c3.to_csv(O + 'q3_threshold_recall70.csv', index=False); print(c3.to_string())
te['p'] = pt; te['y'] = yt
lab = te.merge(D[key + ['label3']], on=key)
print('flag rate by label (test):', lab.assign(f=lab.p >= thr).groupby('label3').f.mean().round(3).to_dict())
rs = np.random.default_rng(42); bt = []; ba = []
for _ in range(500):
    i = rs.integers(0, len(yt), len(yt)); bt.append((pt[i][yt[i] == 1] >= thr).mean()); ba.append(roc_auc_score(yt[i], pt[i]))
print('test recall 95%% CI', np.percentile(bt, [2.5, 97.5]), 'AUC CI', np.percentile(ba, [2.5, 97.5]))
# sensitivity: with tma1_score
ms, cs = models[('sens_with_tma1_score', mm)]
pvs = ms.predict_proba(prep(va, cs))[:, 1]; pts = ms.predict_proba(prep(te, cs))[:, 1]
print('sens (tma1_score) AUC val/test', roc_auc_score(yv, pvs), roc_auc_score(yt, pts))
# audit by group
aud = te.merge(A, on=key); rows = []
for a in ['gender', 'age_band', 'disability', 'imd_band', 'region', 'highest_education']:
    for lvl, x in aud.groupby(a):
        if len(x) < 30: continue
        pos = x.y == 1
        rows.append({'attribute': a, 'level': lvl, 'n': len(x), 'n_noncompleters': int(pos.sum()), 'base_rate': round(x.y.mean(), 3),
                     'flag_rate': round((x.p >= thr).mean(), 3), 'recall': round((x.p[pos] >= thr).mean(), 3), 'fpr': round((x.p[~pos] >= thr).mean(), 3)})
aud_df = pd.DataFrame(rows); aud_df.to_csv(O + 'q3_audit_by_group.csv', index=False); print(aud_df.to_string())

# ---------------- Q4 ----------------
te2 = te.copy(); conv = P['assumed_conversion_rate']; rows = []
te2['low_click'] = -te2.clicks_0_28
for k in P['capacity_k_per_module_presentation']:
    for rule, col in [('Mô hình (điểm rủi ro)', 'p'), ('Ít click nhất 0-28', 'low_click'), ('Ngẫu nhiên (TB 20 lần)', 'rand')]:
        for (m, pr), x in te2.groupby(['code_module', 'code_presentation']):
            kk = min(k, len(x))
            if col == 'rand':
                hits = np.mean([x.y.values[np.random.default_rng(s).permutation(len(x))[:kk]].sum() for s in range(20)])
            else:
                hits = x.sort_values(col, ascending=False, kind='mergesort').head(kk).y.sum()
            rows.append({'k': k, 'rule': rule, 'module': m, 'presentation': pr, 'n_students': len(x), 'n_noncompleters': int(x.y.sum()),
                         'contacted': kk, 'hits': hits, 'precision': hits / kk, 'recall': hits / x.y.sum(), 'base_rate': x.y.mean()})
q4 = pd.DataFrame(rows); q4['lift'] = q4.precision / q4.base_rate
q4.round(3).to_csv(O + 'q4_topk_by_module_presentation.csv', index=False)
s = q4.groupby(['k', 'rule']).agg(contacted=('contacted', 'sum'), hits=('hits', 'sum'), n_non=('n_noncompleters', 'sum'), n_students=('n_students', 'sum')).reset_index()
s['precision'] = s.hits / s.contacted; s['recall'] = s.hits / s.n_non; s['base_rate'] = s.n_non / s.n_students
s['lift'] = s.precision / s.base_rate; s['expected_helped_at_14pct'] = s.hits * conv
s.round(3).to_csv(O + 'q4_topk_summary.csv', index=False); print(s.round(3).to_string())
print(q4[(q4.k == 200) & q4.rule.str.startswith('Mô')].round(3).to_string())
need = []
for (m, pr), x in te2.groupby(['code_module', 'code_presentation']):
    xs = x.sort_values('p', ascending=False); cum = xs.y.cumsum().values / xs.y.sum()
    need.append({'module': m, 'presentation': pr, 'n_students': len(x), 'n_noncompleters': int(x.y.sum()), 'contacts_for_70pct_recall': int(np.argmax(cum >= 0.7) + 1)})
need = pd.DataFrame(need); need.to_csv(O + 'q4_contacts_needed_for_70pct.csv', index=False); print(need.to_string())

fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
pr_, rc_, _ = precision_recall_curve(yt, pt)
ax[0].plot(rc_, pr_, color='#d1495b'); ax[0].axvline(0.7, ls='--', color='gray'); ax[0].axhline(yt.mean(), ls=':', color='gray')
ax[0].plot([c3.iloc[1].recall], [c3.iloc[1].precision], 'ko')
ax[0].annotate('ngưỡng chọn trên validation\nrecall test %.1f%%, precision %.0f%%' % (c3.iloc[1].recall * 100, c3.iloc[1].precision * 100), (c3.iloc[1].recall, c3.iloc[1].precision), xytext=(0.05, 0.5), fontsize=8, arrowprops=dict(arrowstyle='->'))
ax[0].set_title('Ngưỡng cho recall 70%% ở validation chỉ đạt %.1f%% trên test\n(đường nét đứt = mục tiêu 70%%; nét chấm = tỷ lệ nền %.0f%%)' % (c3.iloc[1].recall * 100, yt.mean() * 100), fontsize=10)
ax[0].set_xlabel('Recall'); ax[0].set_ylabel('Precision')
for rule, c in [('Mô hình (điểm rủi ro)', '#d1495b'), ('Ít click nhất 0-28', '#e9c46a'), ('Ngẫu nhiên (TB 20 lần)', '#9aa5b1')]:
    x = s[s.rule == rule]; ax[1].plot(x.k, x.recall * 100, marker='o', color=c, label=rule)
ax[1].axhline(70, ls='--', color='gray'); ax[1].set_xticks(P['capacity_k_per_module_presentation']); ax[1].set_ylim(0, 100)
ax[1].set_title('Với 200 liên hệ/module-kỳ chỉ bắt được ~%.0f%% SV không hoàn thành' % (s[(s.k == 200) & s.rule.str.startswith('Mô')].recall.iloc[0] * 100), fontsize=10)
ax[1].set_xlabel('Sức chứa k mỗi module-kỳ'); ax[1].set_ylabel('Recall (%)'); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig(O + 'q3_q4_recall_precision.png'); plt.close()

# ---------------- Q5 ----------------
lrm = models[('main', 'LogReg')][0]; cols = base
Z = lrm[1].transform(lrm[0].transform(prep(te, cols))); clf = lrm[2]
C = pd.DataFrame(Z * clf.coef_[0], columns=cols)   # log-odds contribution vs average training student
theme = {'Mức tương tác tổng 4 tuần đầu': ['clicks_0_28', 'active_days_0_28', 'n_sites_0_28', 'clicks_homepage_0_28', 'clicks_oucontent_0_28', 'clicks_resource_0_28', 'clicks_subpage_0_28', 'clicks_forumng_0_28', 'clicks_quiz_0_28', 'clicks_url_0_28', 'no_vle_activity_0_28'],
         'Tương tác tuần 1': ['clicks_w1', 'active_days_w1'], 'Tương tác tuần 2': ['clicks_w2', 'active_days_w2'],
         'Tương tác tuần 3': ['clicks_w3', 'active_days_w3'], 'Tương tác tuần 4': ['clicks_w4', 'active_days_w4'],
         'Số ngày từ lần hoạt động cuối': ['days_since_last_active_d28'], 'Hoạt động trước khi khóa bắt đầu': ['clicks_pre_start', 'active_days_pre_start'],
         'Bài TMA1': ['tma1_submitted_by_d28', 'tma1_on_time', 'tma1_days_before_deadline'],
         'Học lại / từng đăng ký trước': ['num_of_prev_attempts', 'seen_in_earlier_presentation'],
         'Số tín chỉ': ['studied_credits'], 'Học vấn đầu vào': ['highest_education_ord'],
         'Thời điểm đăng ký': ['registration_lead_days', 'late_registration_1_28'], 'Module': ['is_FFF']}
T = pd.DataFrame({k: C[v].sum(axis=1) for k, v in theme.items()})
te['rank_in_module_presentation'] = te.groupby(['code_module', 'code_presentation']).p.rank(ascending=False, method='first').astype(int)
idx = te.index[te.rank_in_module_presentation <= P['default_k']]
out = te.loc[idx, key + ['rank_in_module_presentation', 'p', 'y', 'clicks_0_28', 'active_days_0_28', 'days_since_last_active_d28', 'tma1_submitted_by_d28']].rename(columns={'p': 'risk_score', 'y': 'actual_noncompletion'})
for j in (1, 2, 3): out['reason%d' % j] = ''
notes = []
for i in idx:
    r = T.loc[i].sort_values(ascending=False); r = r[r > 0].head(3); facts = []
    for j, nm in enumerate(r.index): out.loc[i, 'reason%d' % (j + 1)] = nm
    # advisor text: only behavioural, actionable drivers (context such as module / prior education stays in reason columns)
    rb = T.loc[i].drop(['Module', 'Học vấn đầu vào', 'Số tín chỉ', 'Thời điểm đăng ký']).sort_values(ascending=False)
    names = list(rb[rb > 0].head(3).index)
    t = te.loc[i]
    for nm in names:
        if nm == 'Mức tương tác tổng 4 tuần đầu': facts.append('chỉ có %d lượt click trong %d ngày học ở 4 tuần đầu' % (t.clicks_0_28, t.active_days_0_28))
        elif nm == 'Số ngày từ lần hoạt động cuối': facts.append('đã %d ngày chưa vào học tính đến ngày 28' % t.days_since_last_active_d28)
        elif nm == 'Bài TMA1': facts.append('chưa nộp bài TMA1' if t.tma1_submitted_by_d28 == 0 else 'nộp bài TMA1 muộn hoặc sát hạn')
        elif nm.startswith('Tương tác tuần'): w = nm[-1]; facts.append('tuần %s chỉ có %d lượt click' % (w, t['clicks_w' + w]))
        elif nm == 'Học lại / từng đăng ký trước': facts.append('đã từng đăng ký/học lại trước đây')
        elif nm == 'Hoạt động trước khi khóa bắt đầu': facts.append('hầu như chưa làm quen hệ thống trước khi khóa bắt đầu')
        elif nm == 'Số tín chỉ': facts.append('đang học nhiều tín chỉ cùng lúc')
        elif nm == 'Học vấn đầu vào': facts.append('trình độ học vấn đầu vào thấp hơn mức trung bình')
        elif nm == 'Thời điểm đăng ký': facts.append('thời điểm đăng ký khác thường')
        else: facts.append('thuộc module có mức rủi ro nền cao hơn')
    notes.append('Sinh viên này được ưu tiên (điểm rủi ro %.2f) chủ yếu vì ' % t.p + '; '.join(facts) + '. Nên liên hệ sớm để hỏi về khó khăn khi vào học và nhắc bài tiếp theo.')
out['advisor_note'] = notes
out.sort_values(['code_module', 'code_presentation', 'rank_in_module_presentation']).to_csv(O + 'q5_priority_list_with_reasons.csv', index=False)
print(out.reason1.value_counts().to_string()); print(out.advisor_note.head(4).to_string())
tm = T.loc[idx].clip(lower=0).mean().sort_values(ascending=False).round(3); tm.to_csv(O + 'q5_theme_mean_positive_contribution.csv'); print(tm)
coef = pd.Series(clf.coef_[0], index=cols).sort_values(key=abs, ascending=False); coef.round(3).to_csv(O + 'q3_logreg_coefficients.csv'); print(coef.head(12))
fig, ax = plt.subplots(figsize=(7.5, 4.5)); m_ = tm.sort_values().tail(8)
ax.barh(m_.index, m_.values, color='#d1495b')
ax.set_title('Bài TMA1 chưa nộp/nộp muộn là yếu tố đẩy rủi ro mạnh nhất\ntrong danh sách ưu tiên (đóng góp trung bình, phần làm tăng rủi ro)', fontsize=10)
ax.set_xlabel('Đóng góp (log-odds)'); plt.tight_layout(); plt.savefig(O + 'q5_dong_gop_rui_ro.png'); plt.close()
