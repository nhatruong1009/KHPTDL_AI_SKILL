import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

O = 'outputs/everest-safety/'


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


m = pd.read_csv('data/members.csv')
m = m[m.peak_id == 'EVER'].copy()
m['group'] = np.where(m.hired, 'Hired staff', 'Expedition member')
m['decade'] = m.year // 10 * 10
m['era'] = np.where(m.year < 1990, '1950-1989', '1990-2019')
m['p5'] = m.year // 5 * 5


def tab(df, by):
    g = df.groupby(by + ['group']).agg(n=('died', 'size'), deaths=('died', 'sum'), summits=('success', 'sum')).reset_index()
    g['deaths_per_1000'] = g.deaths / g.n * 1000
    lo, hi = wilson(g.deaths.values, g.n.values)
    g['lo'] = lo * 1000
    g['hi'] = hi * 1000
    g['deaths_per_1000_summits'] = np.where(g.summits > 0, g.deaths / g.summits.replace(0, np.nan) * 1000, np.nan)
    return g


pd.set_option('display.width', 200)
d = tab(m[m.year >= 1950], ['decade']); d.to_csv(O + 'by_decade.csv', index=False)
e = tab(m[m.year >= 1950], ['era']); e.to_csv(O + 'by_era.csv', index=False)
p = tab(m[m.year >= 1990], ['p5']); p.to_csv(O + 'by_5yr_1990plus.csv', index=False)
print(d.round(1).to_string()); print(e.round(1).to_string()); print(p.round(1).to_string())

for g in ['Expedition member', 'Hired staff']:
    s = m[(m.group == g) & (m.year >= 1950)]
    print(g, 'pre vs post Fisher', stats.fisher_exact(pd.crosstab(s.era, s.died).values))
s = m[m.year >= 1990]
print('1990+ hired vs member Fisher', stats.fisher_exact(pd.crosstab(s.group, s.died).values))

y = m[m.year >= 1990].groupby(['year', 'group']).agg(n=('died', 'size'), deaths=('died', 'sum')).reset_index()
y['r'] = y.deaths / y.n * 1000
y.to_csv(O + 'by_year_1990plus.csv', index=False)
for g, x in y.groupby('group'):
    print(g, 'Spearman year vs rate 1990+', stats.spearmanr(x.year, x.r))

x = m[(m.year >= 1990) & (~m.year.isin([2014, 2015]))]
print('1990+ excluding 2014/2015'); print(tab(x, ['era']).round(1).to_string())
print(m[m.year.isin([2014, 2015])].groupby(['year', 'group']).died.agg(['sum', 'size']))

c = m[m.died & (m.year >= 1990)].groupby(['group', 'death_cause']).size().unstack(0).fillna(0).sort_values('Hired staff', ascending=False)
c.to_csv(O + 'causes_1990plus.csv'); print(c.head(8))

mm = m[(m.group == 'Expedition member') & (m.year >= 1950)]
print(mm.groupby('decade').agg(oxygen=('oxygen_used', 'mean'), success=('success', 'mean'), n=('died', 'size')).round(3))
print(m[m.year >= 1990].groupby(['group', 'success']).died.agg(['sum', 'size']))

fig, ax = plt.subplots(figsize=(9, 5))
col = {'Expedition member': '#1f77b4', 'Hired staff': '#d95f02'}
for g, x in d.groupby('group'):
    off = 1.5 if g == 'Hired staff' else -1.5
    ax.errorbar(x.decade + off, x.deaths_per_1000, yerr=[x.deaths_per_1000 - x.lo, x.hi - x.deaths_per_1000],
                marker='o', capsize=3, label=g, color=col[g])
ax.axvline(1990, ls='--', color='grey')
ax.text(1991, ax.get_ylim()[1] * .92, 'commercial era', color='grey')
ax.set_xlabel('Decade of expedition')
ax.set_ylabel('Deaths per 1,000 people on Everest teams')
ax.set_title('Everest death rate by decade (95% CI)')
ax.legend()
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); plt.savefig(O + 'death_rate_by_decade.png', dpi=150)
