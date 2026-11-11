"""Health spending, income and life expectancy (World Bank WDI). Run from project root: python -I outputs/health_spending_life_expectancy/analysis.py"""
import glob
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt



class _R:
    def __init__(self, y, X):
        Xv = np.asarray(X, float); yv = np.asarray(y, float)
        b, *_ = np.linalg.lstsq(Xv, yv, rcond=None)
        fv = Xv @ b; rs = yv - fv
        n, k = Xv.shape
        s2 = rs @ rs / (n - k)
        se = np.sqrt(np.diag(s2 * np.linalg.inv(Xv.T @ Xv)))
        names = list(X.columns)
        self.params = pd.Series(b, index=names)
        self.pvalues = pd.Series(2 * stats.t.sf(np.abs(b / se), n - k), index=names)
        self.fittedvalues = pd.Series(fv, index=y.index)
        self.resid = pd.Series(rs, index=y.index)
        self.rsquared = 1 - (rs @ rs) / ((yv - yv.mean()) @ (yv - yv.mean()))

    def predict(self, x):
        return [float(np.dot(self.params.values, x))]


class sm:
    @staticmethod
    def add_constant(X):
        X = pd.DataFrame(X).copy()
        X.insert(0, 'const', 1.0)
        return X

    @staticmethod
    def OLS(y, X):
        return type('M', (), {'fit': lambda self: _R(y, X)})()


OUT = 'outputs/health_spending_life_expectancy'
YEAR = '2023'


def load(d):
    f = glob.glob(f'data/{d}/API_*.csv')[0]
    return pd.read_csv(f, skiprows=4, encoding='utf-8-sig').dropna(axis=1, how='all')


meta = pd.read_csv(glob.glob('data/life_expectancy/Metadata_Country*.csv')[0], encoding='utf-8-sig')
meta = meta[meta['Region'].notna()][['Country Code', 'Region', 'IncomeGroup']]  # drops aggregates


def panel(year):
    le = load('life_expectancy')[['Country Code', 'Country Name', year]].rename(columns={year: 'lifeexp'})
    he = load('health_expenditure_per_capita')[['Country Code', year]].rename(columns={year: 'health'})
    gdp = load('gdp_per_capita_ppp')[['Country Code', year]].rename(columns={year: 'gdp'})
    d = le.merge(he, on='Country Code', how='left').merge(gdp, on='Country Code', how='left').merge(meta, on='Country Code')
    n0 = len(d)
    d = d.dropna(subset=['lifeexp', 'health', 'gdp'])
    d = d[(d.health > 0) & (d.gdp > 0)].copy()
    d['lh'] = np.log(d.health)
    d['lg'] = np.log(d.gdp)
    return d, n0


def fit(d, cols):
    return sm.OLS(d.lifeexp, sm.add_constant(d[cols])).fit()


log = []
def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    log.append(s)


d, n0 = panel(YEAR)
P(f'Year {YEAR}: {n0} economies (non-aggregate), complete cases {len(d)}')
P('Dropped (missing any var):', sorted(set(meta.merge(load("life_expectancy")[["Country Code", "Country Name"]], on="Country Code")["Country Name"]) - set(d["Country Name"]))[:60])

# 1. Raw association
r, p = stats.pearsonr(d.lh, d.lifeexp)
rho, _ = stats.spearmanr(d.health, d.lifeexp)
rg, _ = stats.pearsonr(d.lg, d.lifeexp)
rhg, _ = stats.pearsonr(d.lh, d.lg)
P(f'Pearson r(ln health, LE)={r:.3f} (p={p:.1e}); Spearman={rho:.3f}; r(ln GDP, LE)={rg:.3f}; r(ln health, ln GDP)={rhg:.3f}')
m1 = fit(d, ['lh'])
m2 = fit(d, ['lg'])
m3 = fit(d, ['lh', 'lg'])
for n, m in [('LE~lnHealth', m1), ('LE~lnGDP', m2), ('LE~lnHealth+lnGDP', m3)]:
    P(n, 'R2=%.3f' % m.rsquared, m.params.round(3).to_dict(), 'p=', {k: float('%.2g' % v) for k, v in m.pvalues.items()})
P('10pct more health spending -> LE +%.2f yrs (unadjusted); +%.2f yrs (adj. income)' % (m1.params['lh'] * np.log(1.1), m3.params['lh'] * np.log(1.1)))
P('Doubling health spending -> +%.1f yrs unadjusted; +%.1f adj.' % (m1.params['lh'] * np.log(2), m3.params['lh'] * np.log(2)))
# partial correlation of health with LE controlling for GDP
res_le = fit(d, ['lg']).resid
res_h = sm.OLS(d.lh, sm.add_constant(d[['lg']])).fit().resid
P('Partial r(health, LE | GDP)=%.3f' % stats.pearsonr(res_h, res_le)[0])
# by income group
rows = []
for g, s in d.groupby('IncomeGroup'):
    rr = stats.pearsonr(s.lh, s.lifeexp)[0]
    rows.append((g, len(s), rr, s.lifeexp.median(), s.health.median()))
ig = pd.DataFrame(rows, columns=['income_group', 'n', 'r_lnhealth_le', 'median_le', 'median_health_usd'])
P(ig.round(2).to_string())
ig.to_csv(f'{OUT}/by_income_group.csv', index=False)

# 2. Over/under performance: residual of LE vs income (primary), with CI-like standardisation
d['pred_le'] = m2.fittedvalues
d['resid'] = m2.resid
sd = m2.resid.std()
d['z'] = d.resid / sd
d['rank_resid'] = d.resid.rank(ascending=False).astype(int)
# secondary: resid after income AND health
d['resid_inc_health'] = m3.resid
# robustness: quadratic in lnGDP
d['resid_quad'] = sm.OLS(d.lifeexp, sm.add_constant(pd.DataFrame({'lg': d.lg, 'lg2': d.lg ** 2}))).fit().resid
d.to_csv(f'{OUT}/country_residuals_{YEAR}.csv', index=False)
P('resid SD=%.2f yrs' % sd)
cols = ['Country Name', 'lifeexp', 'pred_le', 'resid', 'z', 'health', 'gdp', 'IncomeGroup']
top = d.sort_values('resid', ascending=False)
P('TOP 10 over-performers\n', top[cols].head(10).round(1).to_string())
P('BOTTOM 10 under-performers\n', top[cols].tail(10).round(1).to_string())
top[cols].head(10).to_csv(f'{OUT}/top10_over.csv', index=False)
top[cols].tail(10).to_csv(f'{OUT}/top10_under.csv', index=False)

# robustness: other years and spec
sets = {}
for y in ['2019', '2022', '2023']:
    dy, _ = panel(y)
    dy['resid'] = fit(dy, ['lg']).resid
    sets[y] = dy.set_index('Country Name').resid
dq = d.set_index('Country Name')
over = set(top['Country Name'].head(10))
under = set(top['Country Name'].tail(10))
rob = pd.DataFrame(sets)
rob['quad'] = dq.resid_quad
rob['inc+health'] = dq.resid_inc_health
rob['rank2023'] = rob['2023'].rank(ascending=False)
P('Rank corr of residuals 2023 vs 2019: %.2f, vs 2022: %.2f, vs quadratic: %.2f' % (
    rob['2023'].corr(rob['2019'], method='spearman'), rob['2023'].corr(rob['2022'], method='spearman'),
    rob['2023'].corr(rob['quad'], method='spearman')))
rob.loc[sorted(over | under | {'Viet Nam'})].round(1).to_csv(f'{OUT}/robustness_residuals.csv')
P('Robustness for top/bottom\n', rob.loc[sorted(over | under | {"Viet Nam"})].round(1).to_string())

# 3. Vietnam
v = d[d['Country Code'] == 'VNM'].iloc[0]
P('VIETNAM', v[['lifeexp', 'pred_le', 'resid', 'z', 'health', 'gdp', 'rank_resid']].to_dict(), 'of', len(d))
pred_h = m1.predict([1, v.lh])[0]
P('Vietnam predicted by health spend alone: %.1f; by income+health: %.1f' % (pred_h, m3.fittedvalues[v.name]))
# peers: countries within +-25% GDP
peers = d[(d.gdp.between(v.gdp * 0.75, v.gdp * 1.33)) & (d['Country Code'] != 'VNM')].sort_values('resid', ascending=False)
P('Peers GDP within -25%/+33%:', len(peers), 'Vietnam resid rank among peers incl. itself:',
  int((peers.resid > v.resid).sum() + 1), '/', len(peers) + 1)
P(peers[['Country Name', 'lifeexp', 'resid', 'health', 'gdp']].round(1).to_string())
sea = d[d['Country Code'].isin(['VNM', 'THA', 'IDN', 'PHL', 'MYS', 'KHM', 'LAO', 'MMR', 'CHN', 'SGP', 'KOR', 'JPN', 'IND'])]
P(sea[['Country Name', 'lifeexp', 'resid', 'health', 'gdp']].round(1).to_string())
sea[['Country Name', 'lifeexp', 'pred_le', 'resid', 'health', 'gdp']].to_csv(f'{OUT}/vietnam_and_neighbours.csv', index=False)
# share of countries with higher LE yet lower health spend than Vietnam
P('Countries with lower health spend than VN:', int((d.health < v.health).sum()), '; of those with higher LE:', int(((d.health < v.health) & (d.lifeexp > v.lifeexp)).sum()))
P('Countries with higher LE than VN:', int((d.lifeexp > v.lifeexp).sum()), '; their median health spend: %.0f vs VN %.0f' % (d[d.lifeexp > v.lifeexp].health.median(), v.health))
# Vietnam trend in residual 2000-2023
tr = []
for y in ['2000', '2005', '2010', '2015', '2019', '2023']:
    dy, _ = panel(y)
    mm = fit(dy, ['lg'])
    vv = dy[dy['Country Code'] == 'VNM']
    if len(vv):
        tr.append((y, len(dy), float(vv.lifeexp.iloc[0]), float(mm.resid[vv.index[0]]), int((mm.resid > mm.resid[vv.index[0]]).sum() + 1)))
trd = pd.DataFrame(tr, columns=['year', 'n', 'vn_le', 'vn_resid', 'vn_rank'])
P(trd.round(2).to_string())
trd.to_csv(f'{OUT}/vietnam_trend.csv', index=False)

# Charts
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
a = ax[0]
a.scatter(d.health, d.lifeexp, s=18, c='#b0b7bf', alpha=.8)
xs = np.linspace(d.lh.min(), d.lh.max(), 100)
a.plot(np.exp(xs), m1.params['const'] + m1.params['lh'] * xs, c='#444', lw=1.5)
a.scatter(v.health, v.lifeexp, s=70, c='#d62728', zorder=5)
a.annotate('Việt Nam', (v.health, v.lifeexp), xytext=(8, -16), textcoords='offset points', color='#d62728', fontweight='bold')
a.set_xscale('log')
a.set_xlabel('Chi y tế bình quân đầu người, US$ (thang log), 2023')
a.set_ylabel('Tuổi thọ (năm)')
a.set_title('Chi y tế cao hơn đi cùng tuổi thọ cao hơn (r = %.2f)' % r, loc='left', fontsize=11, fontweight='bold')
b = ax[1]
b.scatter(d.gdp, d.lifeexp, s=18, c='#b0b7bf', alpha=.8)
xs = np.linspace(d.lg.min(), d.lg.max(), 100)
b.plot(np.exp(xs), m2.params['const'] + m2.params['lg'] * xs, c='#444', lw=1.5)
for _, rw in pd.concat([top.head(5), top.tail(5)]).iterrows():
    c = '#1f77b4' if rw.resid > 0 else '#ff7f0e'
    b.scatter(rw.gdp, rw.lifeexp, s=40, c=c, zorder=4)
    b.annotate(rw['Country Name'], (rw.gdp, rw.lifeexp), xytext=(4, 3), textcoords='offset points', fontsize=8, color=c)
b.scatter(v.gdp, v.lifeexp, s=70, c='#d62728', zorder=5)
b.annotate('Việt Nam', (v.gdp, v.lifeexp), xytext=(8, -16), textcoords='offset points', color='#d62728', fontweight='bold')
b.set_xscale('log')
b.set_xlabel('GDP bình quân đầu người, PPP (int. $, thang log), 2023')
b.set_ylabel('Tuổi thọ (năm)')
b.set_title('Cùng mức thu nhập, tuổi thọ lệch tới ±%.0f năm' % top.resid.abs().max(), loc='left', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT}/scatter_health_income_le.png', dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(8, 6))
sel = pd.concat([top.head(8), top[top['Country Code'] == 'VNM'], top.tail(8)]).drop_duplicates('Country Code').sort_values('resid')
colors = ['#d62728' if c == 'VNM' else ('#1f77b4' if x > 0 else '#ff7f0e') for c, x in zip(sel['Country Code'], sel.resid)]
ax.barh(sel['Country Name'], sel.resid, color=colors)
for i, x in enumerate(sel.resid):
    ax.text(x + (.15 if x > 0 else -.15), i, f'{x:+.1f}', va='center', ha='left' if x > 0 else 'right', fontsize=8)
ax.axvline(0, c='#444', lw=.8)
ax.set_xlabel('Tuổi thọ thực tế − dự kiến theo mức thu nhập (năm)')
ax.set_title('Vượt / dưới kỳ vọng so với mức thu nhập, 2023', loc='left', fontweight='bold')
ax.set_xlim(sel.resid.min() - 2, sel.resid.max() + 2)
plt.tight_layout()
plt.savefig(f'{OUT}/over_under_performers.png', dpi=150)
plt.close()

open(f'{OUT}/analysis_log.txt', 'w').write('\n'.join(log))
