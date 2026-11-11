import pandas as pd, numpy as np
from scipy import stats
import numpy.linalg as la
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O = 'outputs/alcohol-vs-g3/'
pd.set_option('display.width', 250)
m = pd.read_csv('data/student-mat.csv', sep=';'); p = pd.read_csv('data/student-por.csv', sep=';')
keys = "school sex age address famsize Pstatus Medu Fedu Mjob Fjob reason nursery internet".split()
for d in (m, p):
    d['key'] = d[keys].astype(str).agg('|'.join, axis=1)
print('dup keys within file', m.key.duplicated().sum(), p.key.duplicated().sum())
# only keys unique in BOTH files are treated as the same student (ambiguous keys stay separate)
safe = set(m.key[~m.key.duplicated(keep=False)]) & set(p.key[~p.key.duplicated(keep=False)])
print('safe matched', len(safe), '| raw key overlap', len(set(m.key) & set(p.key)))
mm = m[m.key.isin(safe)].set_index('key'); pp = p[p.key.isin(safe)].set_index('key').loc[mm.index]
print('Dalc agree', (mm.Dalc == pp.Dalc).mean(), 'Walc agree', (mm.Walc == pp.Walc).mean())
print('corr G3 mat vs por among matched', stats.pearsonr(mm.G3, pp.G3)[0])
om = m[~m.key.isin(safe)]; op = p[~p.key.isin(safe)]
# one row per student; G3 = mean over courses taken; alcohol from math file (differs from por for some)
stu = pd.concat([
    pd.DataFrame({'key': mm.index, 'Dalc': mm.Dalc.values, 'Walc': mm.Walc.values,
                  'G3_mat': mm.G3.values, 'G3_por': pp.G3.values}),
    pd.DataFrame({'key': om.key.values, 'Dalc': om.Dalc.values, 'Walc': om.Walc.values, 'G3_mat': om.G3.values, 'G3_por': np.nan}),
    pd.DataFrame({'key': op.key.values, 'Dalc': op.Dalc.values, 'Walc': op.Walc.values, 'G3_mat': np.nan, 'G3_por': op.G3.values})],
    ignore_index=True)
stu['G3'] = stu[['G3_mat', 'G3_por']].mean(axis=1)
stu['any_zero'] = stu[['G3_mat', 'G3_por']].min(axis=1) == 0
stu['n_courses'] = stu[['G3_mat', 'G3_por']].notna().sum(axis=1)
print('students', len(stu), 'in both', (stu.n_courses == 2).sum(), 'any zero', stu.any_zero.sum())
stu.to_csv(O + 'student_level_table.csv', index=False)

for n, d in (('mat', m), ('por', p)):
    z = d[d.G3 == 0]
    print(n, 'G3=0 n=', len(z), '| G2 of those: min/median/max', z.G2.astype(int).min(), z.G2.astype(int).median(), z.G2.astype(int).max(),
          '| absences zero-group', round(z.absences.mean(), 2), 'vs rest', round(d[d.G3 > 0].absences.mean(), 2))
print('mat G3=0 & G2>0:', ((m.G3 == 0) & (m.G2.astype(int) > 0)).sum(), ' por:', ((p.G3 == 0) & (p.G2.astype(int) > 0)).sum())


def cohen_d(a, b):
    sp = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / sp


rows = []
def run(label, df, y='G3'):
    for a in ('Dalc', 'Walc'):
        x = df[a]; yy = df[y]
        rho, pr = stats.spearmanr(x, yy); sl = stats.linregress(x, yy)
        lo = df[x <= 2][y]; hi = df[x >= 3][y]
        rg = np.random.default_rng(1)
        bs = [stats.spearmanr(x.values[i], yy.values[i])[0] for i in (rg.integers(0, len(df), len(df)) for _ in range(1000))]
        rows.append(dict(sample=label, alcohol=a, n=len(df), spearman=rho, sp_lo=np.percentile(bs, 2.5), sp_hi=np.percentile(bs, 97.5),
                         sp_p=pr, pearson=sl.rvalue, slope_per_pt=sl.slope, slope_ci=1.96 * sl.stderr, slope_p=sl.pvalue,
                         n_low=len(lo), n_high=len(hi), mean_low=lo.mean(), mean_high=hi.mean(), diff=hi.mean() - lo.mean(),
                         cohen_d=cohen_d(hi, lo), welch_p=stats.ttest_ind(hi, lo, equal_var=False).pvalue,
                         mwu_p=stats.mannwhitneyu(hi, lo).pvalue))


nz = stu[~stu.any_zero]
run('A student-level, zeros kept', stu)
run('B student-level, excl any G3=0', nz)
run('C math rows only, all', m); run('D por rows only, all', p)
run('E math, G3>0', m[m.G3 > 0]); run('F por, G3>0', p[p.G3 > 0])
R = pd.DataFrame(rows); R.to_csv(O + 'results.csv', index=False)
print(R.round(4).to_string())

zr = []
for a in ('Dalc', 'Walc'):
    hi = stu[stu[a] >= 3].any_zero; lo = stu[stu[a] <= 2].any_zero
    orr, pf = stats.fisher_exact([[hi.sum(), (~hi).sum()], [lo.sum(), (~lo).sum()]])
    zr.append(dict(alcohol=a, n_high=len(hi), zero_rate_high=hi.mean(), n_low=len(lo), zero_rate_low=lo.mean(), odds_ratio=orr, fisher_p=pf))
zr = pd.DataFrame(zr); zr.to_csv(O + 'zero_rate.csv', index=False); print(zr.round(4).to_string())

# adjusted OLS with covariates
cov = pd.concat([m, p]).drop_duplicates('key').set_index('key')
cov['male'] = (cov.sex == 'M').astype(int); cov['higher'] = (cov.higher == 'yes').astype(int); cov['ms'] = (cov.school == 'MS').astype(int)
cv = ['male', 'studytime', 'failures', 'higher', 'ms', 'age']


def ols(df, cols, y='G3'):
    X = np.column_stack([np.ones(len(df))] + [df[c] for c in cols]); b = la.lstsq(X, df[y], rcond=None)[0]
    res = df[y] - X @ b; dof = len(df) - X.shape[1]
    se = np.sqrt(np.diag(res @ res / dof * la.inv(X.T @ X)))
    return pd.DataFrame({'term': ['const'] + cols, 'coef': b, 'ci95': 1.96 * se, 'p': 2 * stats.t.sf(abs(b / se), dof), 'n': len(df)})


ad = []
for lab, sub in (('A zeros kept', stu), ('B excl zeros', nz)):
    s = sub.join(cov[cv], on='key')
    for nm, cols in (('Dalc', ['Dalc']), ('Walc', ['Walc']), ('both', ['Dalc', 'Walc'])):
        t = ols(s, cols + cv); t['model'] = lab + ' / ' + nm; ad.append(t)
AD = pd.concat(ad); AD.to_csv(O + 'adjusted_ols.csv', index=False)
print(AD[AD.term.isin(['Dalc', 'Walc'])].round(4).to_string())

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
for a_, al, xl in zip(ax, ('Dalc', 'Walc'), ('Workday alcohol (1=very low, 5=very high)', 'Weekend alcohol (1-5)')):
    for d, lab, c in ((stu, 'All students (zeros kept)', '#888888'), (nz, 'Excluding G3=0', '#1f77b4')):
        g = d.groupby(al).G3.agg(['mean', 'std', 'count'])
        a_.errorbar(g.index, g['mean'], 1.96 * g['std'] / np.sqrt(g['count']), marker='o', label=lab, color=c, capsize=3)
    a_.set_xlabel(xl); a_.grid(alpha=.3)
ax[0].set_ylabel('Mean G3 (0-20), 95% CI'); ax[0].legend()
fig.suptitle('Final grade by alcohol consumption (one row per student)')
plt.tight_layout(); plt.savefig(O + 'g3_by_alcohol.png', dpi=130)
