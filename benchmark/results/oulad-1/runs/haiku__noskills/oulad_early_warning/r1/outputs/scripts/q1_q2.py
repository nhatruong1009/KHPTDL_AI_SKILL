"""Q1 & Q2: interaction in weeks 1-4 by outcome group, and which indicators
separate completers (Pass) from non-completers (Fail + Withdrawn), by week."""
import pandas as pd, numpy as np
from scipy import stats

D = "data/"
OUT = "outputs/"
K = ['code_module', 'code_presentation', 'id_student']

w = pd.read_csv(D + "aq1_student_week.csv")
d = pd.read_csv(D + "aq2_diagnostic_table.csv")

# ---------- Q1: weekly interaction by label3 ----------
wide = w.pivot_table(index=K, columns='week', values=['clicks', 'active_days'], aggfunc='sum')
wide.columns = [f"{v}_w{k}" for v, k in wide.columns]
wide = wide.reset_index()
base = d[K + ['label3', 'target_noncompletion', 'tma1_submitted_by_d28', 'tma1_score',
              'clicks_pre_start', 'active_days_pre_start', 'days_since_last_active_d28',
              'no_vle_activity_0_28', 'n_sites_0_28', 'clicks_0_28', 'active_days_0_28']]
df = base.merge(wide, on=K, how='left')
for k in range(1, 5):
    df[f'cum_clicks_w{k}'] = df[[f'clicks_w{i}' for i in range(1, k + 1)]].sum(axis=1)
    df[f'cum_active_w{k}'] = df[[f'active_days_w{i}' for i in range(1, k + 1)]].sum(axis=1)
    df[f'zero_click_w{k}'] = (df[f'clicks_w{k}'] == 0).astype(int)

groups = ['Pass', 'Fail', 'Withdrawn']
rows = []
for k in range(1, 5):
    r = {'tuần': k}
    for g in groups:
        s = df.loc[df.label3 == g, f'clicks_w{k}']
        r[f'{g}_median_clicks'] = s.median()
        r[f'{g}_mean_clicks'] = round(s.mean(), 1)
        r[f'{g}_median_active_days'] = df.loc[df.label3 == g, f'active_days_w{k}'].median()
        r[f'{g}_pct_zero_click'] = round(100 * df.loc[df.label3 == g, f'zero_click_w{k}'].mean(), 1)
    r['kruskal_p'] = stats.kruskal(*[df.loc[df.label3 == g, f'clicks_w{k}'] for g in groups]).pvalue
    rows.append(r)
q1 = pd.DataFrame(rows)
q1.to_csv(OUT + "q1_weekly_by_outcome.csv", index=False)
print(q1.T.to_string())

# group sizes
print(df.label3.value_counts())

# ---------- Q2: completer (Pass) vs non-completer (Fail/Withdrawn) ----------
df['noncomp'] = df.target_noncompletion
ind = []
for k in range(1, 5):
    ind += [(f'clicks_w{k}', f'Số lượt nhấp tuần {k}', k),
            (f'active_days_w{k}', f'Số ngày hoạt động tuần {k}', k),
            (f'cum_clicks_w{k}', f'Lũy kế lượt nhấp đến tuần {k}', k),
            (f'cum_active_w{k}', f'Lũy kế ngày hoạt động đến tuần {k}', k),
            (f'zero_click_w{k}', f'Tỷ lệ tuần {k} không có lượt nhấp', k)]
ind += [('clicks_pre_start', 'Lượt nhấp trước khi khóa bắt đầu', 0),
        ('active_days_pre_start', 'Ngày hoạt động trước khi khóa bắt đầu', 0),
        ('tma1_submitted_by_d28', 'Đã nộp TMA1 đến ngày 28', 'd28'),
        ('tma1_score', 'Điểm TMA1 (nếu đã nộp)', 'd28'),
        ('days_since_last_active_d28', 'Số ngày từ lần hoạt động cuối đến ngày 28', 'd28'),
        ('n_sites_0_28', 'Số trang/nguồn VLE đã truy cập 0-28', 'd28')]

res = []
g1 = df[df.noncomp == 0]
g2 = df[df.noncomp == 1]
for col, label, wk in ind:
    a = g1[col].dropna(); b = g2[col].dropna()
    u = stats.mannwhitneyu(a, b, alternative='two-sided')
    auc = u.statistic / (len(a) * len(b))  # P(completer > non-completer)
    res.append(dict(chỉ_báo=label, column=col, tuần=wk, n_pass=len(a), n_noncomp=len(b),
                    median_pass=a.median(), median_noncomp=b.median(),
                    AUC_pass_vs_noncomp=round(auc, 3), p_value=u.pvalue))
r2 = pd.DataFrame(res)
# Benjamini-Hochberg over all tests
p = r2.p_value.values
order = np.argsort(p); m = len(p)
q = np.empty(m); cur = 1.0
for rank, idx in reversed(list(enumerate(order, start=1))):
    cur = min(cur, p[idx] * m / rank); q[idx] = cur
r2['q_BH'] = q
r2['significant_BH05'] = r2.q_BH < 0.05
r2.to_csv(OUT + "q2_indicator_tests.csv", index=False)
pd.set_option('display.width', 250)
print(r2.drop(columns=['column']).to_string())
