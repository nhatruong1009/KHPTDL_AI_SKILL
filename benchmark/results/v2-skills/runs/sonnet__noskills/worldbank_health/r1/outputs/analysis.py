import pandas as pd, numpy as np, glob
from math import erfc, sqrt


class _M:
    pass


class sm:
    @staticmethod
    def add_constant(X):
        X = X.copy()
        X.insert(0, 'const', 1.0)
        return X

    @staticmethod
    def OLS(y, X):
        class F:
            def fit(self_):
                Xv = X.values
                yv = np.asarray(y, float)
                b = np.linalg.lstsq(Xv, yv, rcond=None)[0]
                m = _M()
                m.params = pd.Series(b, index=X.columns)
                m.fittedvalues = pd.Series(Xv @ b, index=X.index)
                m.resid = pd.Series(yv - Xv @ b, index=X.index)
                n, k = Xv.shape
                s2 = (m.resid ** 2).sum() / (n - k)
                se = np.sqrt(np.diag(s2 * np.linalg.inv(Xv.T @ Xv)))
                m.pvalues = pd.Series([erfc(abs(t) / sqrt(2)) for t in b / se], index=X.columns)
                m.rsquared = 1 - (m.resid ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
                return m
        return F()
W = '/root/.cache/skill-bench/runs/ab-vi/sonnet__noskills/worldbank_health/r1/workspace/'

def load(d, name, y):
    f = glob.glob(W + 'data/' + d + '/API*')[0]
    x = pd.read_csv(f, skiprows=4)
    return x[['Country Name', 'Country Code', y]].rename(columns={y: name})

meta = pd.read_csv(glob.glob(W + 'data/life_expectancy/Metadata_Country*')[0])

def run(y):
    d = load('life_expectancy', 'LE', y)
    d = d.merge(load('health_expenditure_per_capita', 'he', y)[['Country Code', 'he']], on='Country Code')
    d = d.merge(load('gdp_per_capita_ppp', 'gdp', y)[['Country Code', 'gdp']], on='Country Code')
    d = d.merge(meta[['Country Code', 'Region', 'IncomeGroup']], on='Country Code')
    d = d[d.Region.notna()].dropna(subset=['LE', 'he', 'gdp'])  # bỏ nhóm tổng hợp
    d = d[(d.he > 0) & (d.gdp > 0)].copy()
    d['lhe'] = np.log(d.he)
    d['lgdp'] = np.log(d.gdp)
    return d

res = {}
for y in ['2023', '2022']:
    d = run(y)
    n = len(d)
    print(y, 'n=', n)
    print('corr le~lhe', round(d['LE'].corr(d.lhe), 3), 'le~he linear', round(d['LE'].corr(d.he), 3),
          'spearman', round(d['LE'].corr(d.he, method='spearman'), 3))
    m1 = sm.OLS(d['LE'], sm.add_constant(d[['lhe']])).fit()
    m2 = sm.OLS(d['LE'], sm.add_constant(d[['lgdp']])).fit()
    m3 = sm.OLS(d['LE'], sm.add_constant(d[['lgdp', 'lhe']])).fit()
    for nm, m in [('lhe', m1), ('lgdp', m2), ('both', m3)]:
        print(nm, m.params.round(3).to_dict(), 'R2', round(m.rsquared, 3), 'p', m.pvalues.round(4).to_dict())
    d['pred3'] = m3.fittedvalues
    d['resid'] = m3.resid
    rng = np.random.default_rng(0)
    b = []
    for _ in range(1000):
        s = d.sample(n, replace=True, random_state=int(rng.integers(1e9)))
        b.append(sm.OLS(s['LE'], sm.add_constant(s[['lgdp', 'lhe']])).fit().params['lhe'])
    print('boot CI lhe', np.percentile(b, [2.5, 97.5]).round(3))
    res[y] = (d, m3, m1)
    d.to_csv(W + 'outputs/data_%s.csv' % y, index=False)

d, m3, m1 = res['2023']
cols = ['Country Name', 'LE', 'he', 'gdp', 'pred3', 'resid']
print(d.sort_values('resid', ascending=False)[cols].head(12).round(1).to_string())
print(d.sort_values('resid')[cols].head(12).round(1).to_string())
vn = d[d['Country Code'] == 'VNM']
print(vn[cols + ['IncomeGroup']].round(2).to_string())
r = d.resid.rank(ascending=False)
print('VN rank', int(r[vn.index[0]]), 'of', len(d), 'resid sd', round(d.resid.std(), 2))
nb = d[(d.gdp > vn.gdp.iloc[0] * 0.7) & (d.gdp < vn.gdp.iloc[0] * 1.4)].sort_values('resid', ascending=False)
print(nb[cols].round(1).to_string())
d2 = res['2022'][0]
j = d.merge(d2[['Country Code', 'resid']], on='Country Code', suffixes=('', '_22'))
print('stab corr', round(j.resid.corr(j.resid_22), 3))
print(d2.loc[d2['Country Code'] == 'VNM', ['LE', 'he', 'gdp', 'resid']])
print('x2 effect both', np.log(2) * m3.params['lhe'], 'alone', np.log(2) * m1.params['lhe'])
for g, s in d.groupby('IncomeGroup'):
    print(g, len(s), round(s['LE'].corr(s.lhe), 2))
