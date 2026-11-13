import pandas as pd
from scipy import stats

d = 'data/'
out = 'outputs/giong-nho-gia-phap-vs-bodaonha/'
r = pd.read_csv(d + 'winequality-red.csv', sep=';')
w = pd.read_csv(d + 'winequality-white.csv', sep=';')
r['type'] = 'red'
w['type'] = 'white'
a = pd.concat([r, w])

s = a.groupby('type').quality.agg(['count', 'mean', 'median', 'std']).round(3)
s['pct_quality_ge7'] = a.groupby('type').quality.apply(lambda x: (x >= 7).mean() * 100).round(1)
s.to_csv(out + 'quality_by_type.csv')
print(s)
print(stats.mannwhitneyu(r.quality, w.quality))

dd = a.drop_duplicates()
print(dd.groupby('type').quality.agg(['count', 'mean']).round(3))
print(stats.mannwhitneyu(dd[dd.type == 'red'].quality, dd[dd.type == 'white'].quality))

a['hi'] = a.quality >= 7
p = a.groupby(['type', 'hi'])[['alcohol', 'volatile acidity', 'density', 'residual sugar']].mean().round(3)
p.to_csv(out + 'profile_high_quality.csv')
print(p)
