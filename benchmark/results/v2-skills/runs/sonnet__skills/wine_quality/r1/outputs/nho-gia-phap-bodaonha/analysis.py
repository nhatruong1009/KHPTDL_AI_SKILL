import pandas as pd
from scipy import stats

r = pd.read_csv('data/winequality-red.csv', sep=';')
w = pd.read_csv('data/winequality-white.csv', sep=';')
cols = list(r.columns) + list(w.columns)
rows = [dict(loai=n, n=len(d), mean=d.quality.mean(), median=d.quality.median(), sd=d.quality.std())
        for n, d in [('red', r), ('white', w)]]
t = pd.DataFrame(rows)
print(t)
t.to_csv('outputs/nho-gia-phap-bodaonha/quality_red_vs_white.csv', index=False)
print(stats.mannwhitneyu(r.quality, w.quality))
print('cot lien quan:', [c for c in cols if any(k in c.lower() for k in ['grape', 'price', 'country', 'variety'])])
