import pandas as pd, numpy as np
from scipy import stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng = np.random.default_rng(1)
m = pd.read_csv('data/student-mat.csv', sep=';'); p = pd.read_csv('data/student-por.csv', sep=';')
# khoá nhận diện cùng một học sinh (13 thuộc tính của R script + 12 thuộc tính nền khác); Dalc/Walc khớp 100% ở cặp trùng
k = ("school sex age address famsize Pstatus Medu Fedu Mjob Fjob reason nursery internet guardian traveltime "
     "studytime schoolsup famsup activities higher romantic famrel freetime goout health").split()
m['sub'] = 'mat'; p['sub'] = 'por'
a = pd.concat([m, p], ignore_index=True)
a['sid'] = a.groupby(k, sort=False).ngroup()
n_both = (a.groupby('sid')['sub'].nunique() == 2).sum()
print('rows', len(a), 'unique students', a.sid.nunique(), 'in both', n_both)
a['zero'] = (a.G3 == 0)
a['G3v'] = a.G3.where(~a.zero)

def stud(col):
    g = a.groupby('sid')
    s = g.agg(Dalc=('Dalc', 'mean'), Walc=('Walc', 'mean'), G3=(col, 'mean'), sex=('sex', 'first'), age=('age', 'first'),
              studytime=('studytime', 'mean'), failures=('failures', 'max'), higher=('higher', 'first'),
              school=('school', 'first'), Medu=('Medu', 'first'), Fedu=('Fedu', 'first'), goout=('goout', 'first'),
              nsub=('sub', 'nunique'), zero=('zero', 'max'))
    s['alc'] = (5 * s.Dalc + 2 * s.Walc) / 7
    return s

S = stud('G3v'); Sall = stud('G3')
S = S.dropna(subset=['G3'])
print('students analysed', len(S), 'excluded (only zeros)', a.sid.nunique() - len(S))
print('students with any G3=0:', Sall.zero.sum())

def cohen_d(x, y):
    nx, ny = len(x), len(y)
    sp = np.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
    return (x.mean() - y.mean()) / sp

def boot_rho(x, y, n=1000):
    r = []
    for _ in range(n):
        i = rng.integers(0, len(x), len(x)); r.append(stats.spearmanr(x[i], y[i])[0])
    return np.percentile(r, [2.5, 97.5])

def ols(X, y, names):
    X = np.column_stack([np.ones(len(y)), X]); b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b
    H = np.linalg.inv(X.T @ X); h = np.einsum('ij,jk,ik->i', X, H, X)
    V = H @ (X.T * (e / (1 - h)) ** 2) @ X @ H   # HC3
    se = np.sqrt(np.diag(V)); df = len(y) - X.shape[1]; t = b / se; pv = 2 * stats.t.sf(abs(t), df)
    return pd.DataFrame({'b': b, 'se': se, 'p': pv}, index=['const'] + names)

rows = []
def analyse(D, label):
    for v in ['Dalc', 'Walc', 'alc']:
        x, y = D[v].values, D.G3.values
        rho, pr = stats.spearmanr(x, y); r, pp = stats.pearsonr(x, y)
        ci = boot_rho(x, y)
        hi = D[D[v] >= 3].G3; lo = D[D[v] < 3].G3
        d = cohen_d(hi, lo); tw = stats.ttest_ind(hi, lo, equal_var=False); mw = stats.mannwhitneyu(hi, lo)
        bs = [cohen_d(pd.Series(rng.choice(hi.values, len(hi))), pd.Series(rng.choice(lo.values, len(lo)))) for _ in range(1000)]
        dci = np.percentile(bs, [2.5, 97.5])
        Xc = D[['sex', 'age', 'studytime', 'failures', 'higher', 'school', 'Medu', 'Fedu', 'goout']].copy()
        Xc['sex'] = (Xc.sex == 'M') * 1.; Xc['higher'] = (Xc.higher == 'yes') * 1.; Xc['school'] = (Xc.school == 'MS') * 1.
        o = ols(np.column_stack([x, Xc.values]), y, [v] + list(Xc.columns)).loc[v]
        rows.append(dict(sample=label, var=v, n=len(D), pearson_r=r, p_pearson=pp, spearman_rho=rho, rho_lo=ci[0], rho_hi=ci[1],
                         p_spearman=pr, n_hi=len(hi), mean_hi=hi.mean(), mean_lo=lo.mean(), diff=hi.mean() - lo.mean(),
                         cohen_d=d, d_lo=dci[0], d_hi=dci[1], p_welch=tw.pvalue, p_mw=mw.pvalue,
                         adj_b=o.b, adj_p=o.p, adj_std_b=o.b / D.G3.std()))

analyse(S, 'primary: zero=missing, student-level')
analyse(Sall.dropna(subset=['G3']), 'sens: zeros kept, student-level')
for sub in ['mat', 'por']:
    for keep in [False, True]:
        D = a[a['sub'] == sub].copy()
        D['G3'] = D.G3 if keep else D.G3v
        D = D.dropna(subset=['G3']); D['alc'] = (5 * D.Dalc + 2 * D.Walc) / 7
        analyse(D.set_index('sid'), 'subject=%s, zeros %s' % (sub, 'kept' if keep else 'missing'))
R = pd.DataFrame(rows); R.to_csv('outputs/results.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
print(R.round(4).to_string())

S['Walc_g'] = S.Walc.round().astype(int); S['Dalc_g'] = S.Dalc.round().astype(int)
gd = S.groupby('Dalc_g').G3.agg(['count', 'mean', 'std']).round(2); gw = S.groupby('Walc_g').G3.agg(['count', 'mean', 'std']).round(2)
print(gd); print(gw)
pd.concat({'Dalc': gd, 'Walc': gw}).to_csv('outputs/group_means.csv')

Z = Sall
for v in ['Dalc', 'Walc']:
    h = Z[Z[v] >= 3]; l = Z[Z[v] < 3]
    print(v, 'ti le co G3=0: cao', round(h.zero.mean(), 3), 'thap', round(l.zero.mean(), 3),
          stats.fisher_exact([[h.zero.sum(), len(h) - h.zero.sum()], [l.zero.sum(), len(l) - l.zero.sum()]]))
a2 = a[~a.zero]
print('naive (nhan doi hoc sinh)', len(a2), stats.spearmanr(a2.Walc, a2.G3), stats.spearmanr(a2.Dalc, a2.G3))

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
for x, (v, t) in zip(ax, [('Dalc_g', 'Ngày thường (Dalc)'), ('Walc_g', 'Cuối tuần (Walc)')]):
    g = S.groupby(v).G3; mu = g.mean(); se = g.std() / np.sqrt(g.count())
    x.errorbar(mu.index, mu, yerr=1.96 * se, fmt='o-', color='#1f77b4', capsize=4)
    for xx, yy, c in zip(mu.index, mu, g.count()):
        x.annotate('n=%d' % c, (xx, yy), textcoords='offset points', xytext=(0, -16), ha='center', fontsize=8)
    x.set_title(t); x.set_xlabel('Mức uống rượu (1=rất thấp, 5=rất cao)'); x.set_xticks(range(1, 6)); x.grid(alpha=.3)
ax[0].set_ylabel('G3 trung bình (±95% CI)')
fig.suptitle('Điểm cuối kỳ G3 theo mức uống rượu (%d học sinh, G3=0 coi là thiếu dữ liệu)' % len(S))
plt.tight_layout(); plt.savefig('outputs/g3_theo_muc_uong.png', dpi=150)
