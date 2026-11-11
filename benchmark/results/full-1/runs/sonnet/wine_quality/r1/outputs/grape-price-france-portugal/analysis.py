import pandas as pd
from scipy import stats
OUT = 'outputs/grape-price-france-portugal/'
r = pd.read_csv('data/winequality-red.csv', sep=';')
w = pd.read_csv('data/winequality-white.csv', sep=';')
print(list(r.columns))
s = pd.DataFrame({'n': [len(r), len(w)],
                  'mean': [r.quality.mean(), w.quality.mean()],
                  'median': [r.quality.median(), w.quality.median()],
                  'pct_ge7': [(r.quality >= 7).mean() * 100, (w.quality >= 7).mean() * 100]},
                 index=['red', 'white']).round(3)
print(s)
s.to_csv(OUT + 'red_vs_white.csv')
print(stats.mannwhitneyu(r.quality, w.quality))
a = pd.concat([r, w])
c = a.corr()['quality'].drop('quality').sort_values()
print(c.round(3))
c.to_csv(OUT + 'corr_quality.csv')
