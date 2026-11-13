import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from scipy import stats
OUT = 'outputs/oulad-early-warning/'
d = pd.read_csv('data/aq2_diagnostic_table.csv')
d['grp'] = d.label3          # Pass (gồm Distinction) / Fail / Withdrawn
d['nc'] = d.target_noncompletion
sns.set_theme(style='whitegrid')

# ---------------- Q1: profile theo nhóm kết quả x tuần
rows = []
for g, x in d.groupby('grp'):
    r = {'nhom': g, 'n': len(x)}
    for w in range(1, 5):
        r[f'clicks_median_w{w}'] = x[f'clicks_w{w}'].median()
        r[f'clicks_mean_w{w}'] = x[f'clicks_w{w}'].mean()
        r[f'days_mean_w{w}'] = x[f'active_days_w{w}'].mean()
        r[f'zero_clicks_pct_w{w}'] = (x[f'clicks_w{w}'] == 0).mean() * 100
    r['clicks_0_28_median'] = x.clicks_0_28.median()
    r['active_days_0_28_median'] = x.active_days_0_28.median()
    r['tma1_submitted_pct'] = x.tma1_submitted_by_d28.mean() * 100
    r['no_vle_pct'] = x.no_vle_activity_0_28.mean() * 100
    rows.append(r)
q1 = pd.DataFrame(rows)
q1.to_csv(OUT + 'q1_profile_by_outcome.csv', index=False)
print(q1.set_index('nhom').T.round(2))
kw = []
for v in ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'active_days_w1', 'active_days_w2',
          'active_days_w3', 'active_days_w4', 'clicks_0_28', 'active_days_0_28', 'tma1_submitted_by_d28']:
    H, p = stats.kruskal(*[x[v] for _, x in d.groupby('grp')])
    kw.append({'var': v, 'H': H, 'p': p, 'eta2_H': (H - 2) / (len(d) - 3)})
kw = pd.DataFrame(kw)
kw.to_csv(OUT + 'q1_kruskal.csv', index=False)
print(kw)
pw = []
for a, b in [('Pass', 'Fail'), ('Pass', 'Withdrawn'), ('Fail', 'Withdrawn')]:
    for v in ['clicks_0_28', 'active_days_0_28']:
        xa, xb = d[d.grp == a][v], d[d.grp == b][v]
        u, p = stats.mannwhitneyu(xa, xb)
        pw.append({'A': a, 'B': b, 'var': v, 'AUC_A_higher': u / (len(xa) * len(xb)), 'p': p})
pw = pd.DataFrame(pw)
pw.to_csv(OUT + 'q1_pairwise.csv', index=False)
print(pw)


# ---------------- Q2: chỉ báo hoàn thành vs không hoàn thành
def auc_ci(x, y, B=300, seed=0):
    rng = np.random.default_rng(seed)
    a = stats.mannwhitneyu(x[y == 1], x[y == 0])
    au = a.statistic / ((y == 1).sum() * (y == 0).sum())
    idx = np.arange(len(x))
    bs = []
    for _ in range(B):
        s = rng.choice(idx, len(idx))
        xs, ys = x[s], y[s]
        bs.append(stats.mannwhitneyu(xs[ys == 1], xs[ys == 0]).statistic / ((ys == 1).sum() * (ys == 0).sum()))
    return au, np.percentile(bs, 2.5), np.percentile(bs, 97.5), a.pvalue


inds = ['clicks_pre_start', 'active_days_pre_start', 'clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4',
        'active_days_w1', 'active_days_w2', 'active_days_w3', 'active_days_w4', 'clicks_0_28',
        'active_days_0_28', 'n_sites_0_28', 'days_since_last_active_d28', 'clicks_change_w1_w4',
        'clicks_homepage_0_28', 'clicks_oucontent_0_28', 'clicks_resource_0_28', 'clicks_subpage_0_28',
        'clicks_forumng_0_28', 'clicks_quiz_0_28', 'clicks_url_0_28', 'tma1_submitted_by_d28',
        'tma1_on_time', 'tma1_days_before_deadline', 'registration_lead_days', 'num_of_prev_attempts',
        'studied_credits']
y = d.nc.values
res = []
for v in inds:
    x = d[v].fillna(d[v].median()).values.astype(float)
    au, lo, hi, p = auc_ci(x, y)
    res.append({'indicator': v, 'median_complete': np.median(x[y == 0]), 'median_noncomplete': np.median(x[y == 1]),
                'AUC_noncomplete_higher': au, 'ci_lo': lo, 'ci_hi': hi, 'p': p})
q2 = pd.DataFrame(res)
o = q2.p.argsort().values
m = len(q2)
adj = np.empty(m)
run = 0
for i, j in enumerate(o):
    run = max(run, min(1, q2.p.values[j] * (m - i)))
    adj[j] = run
q2['p_holm'] = adj
q2['effect_abs'] = (q2.AUC_noncomplete_higher - 0.5).abs()
q2.to_csv(OUT + 'q2_indicators.csv', index=False)
print(q2.round(4).to_string())

cons = []
for (m_, p_), x in d.groupby(['code_module', 'code_presentation']):
    for v in ['clicks_pre_start', 'clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'active_days_w1', 'tma1_submitted_by_d28']:
        a = stats.mannwhitneyu(x[x.nc == 1][v], x[x.nc == 0][v])
        cons.append({'mod_pres': m_ + p_, 'var': v, 'AUC': a.statistic / ((x.nc == 1).sum() * (x.nc == 0).sum()), 'p': a.pvalue})
cons = pd.DataFrame(cons)
cons.to_csv(OUT + 'q2_consistency_by_module_presentation.csv', index=False)
print(cons.pivot(index='var', columns='mod_pres', values='AUC').round(3))

wk = []
for w in range(1, 5):
    wk.append({'week': w,
               'noncomplete_rate_if_zero_clicks': d[d[f'clicks_w{w}'] == 0].nc.mean(),
               'n_zero': (d[f'clicks_w{w}'] == 0).sum(),
               'noncomplete_rate_if_active': d[d[f'clicks_w{w}'] > 0].nc.mean()})
wk = pd.DataFrame(wk)
wk.to_csv(OUT + 'q2_zero_activity_by_week.csv', index=False)
print(wk)
print('base rate', d.nc.mean())

# ---------------- charts
cols = {'Pass': '#2a9d8f', 'Fail': '#e76f51', 'Withdrawn': '#6d6875'}
fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
for g in ['Pass', 'Fail', 'Withdrawn']:
    x = d[d.grp == g]
    ax[0].plot(range(1, 5), [x[f'clicks_w{w}'].median() for w in range(1, 5)], marker='o', color=cols[g],
               label=f'{g} (n={len(x):,})', lw=2.5)
    ax[1].plot(range(1, 5), [x[f'active_days_w{w}'].mean() for w in range(1, 5)], marker='o', color=cols[g], lw=2.5)
for a, l in [(ax[0], 'Số click trung vị / tuần'), (ax[1], 'Số ngày hoạt động trung bình / tuần')]:
    a.set_xticks(range(1, 5))
    a.set_xlabel('Tuần của khóa học')
    a.set_ylabel(l)
    a.spines[['top', 'right']].set_visible(False)
ax[0].legend()
ax[0].set_title('Pass có click cao nhất, Fail thấp nhất ngay từ tuần 1', fontsize=11)
ax[1].set_title('Pass vào học nhiều ngày hơn hẳn Fail và Withdrawn', fontsize=11)
fig.text(0.01, -0.02, 'Nguồn: aq2_diagnostic_table.csv (13.020 lượt đăng ký còn học đến ngày 28; Pass gồm cả Distinction)', fontsize=8)
plt.tight_layout()
plt.savefig(OUT + 'q1_weekly_by_outcome.png', dpi=150, bbox_inches='tight')
plt.close()

keep = ['clicks_pre_start', 'clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'active_days_w1', 'active_days_w2',
        'active_days_w3', 'active_days_w4', 'clicks_0_28', 'active_days_0_28', 'tma1_submitted_by_d28',
        'tma1_on_time', 'days_since_last_active_d28', 'n_sites_0_28', 'clicks_forumng_0_28']
s = q2[q2.indicator.isin(keep)].copy()
s['es'] = s.AUC_noncomplete_higher - 0.5
s = s.sort_values('es')
fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(s.indicator, s.es, color=['#e76f51' if v > 0 else '#2a9d8f' for v in s.es])
ax.axvline(0, color='k', lw=.8)
ax.set_xlabel('AUC − 0,5 (âm: nhóm không hoàn thành có giá trị thấp hơn)')
ax.set_title('Số ngày hoạt động và việc nộp TMA1 phân biệt rõ nhất\nhoàn thành / không hoàn thành', fontsize=11)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(OUT + 'q2_indicator_effects.png', dpi=150, bbox_inches='tight')
plt.close()
