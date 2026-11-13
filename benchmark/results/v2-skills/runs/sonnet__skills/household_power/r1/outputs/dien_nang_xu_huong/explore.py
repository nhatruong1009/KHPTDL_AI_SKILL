import pandas as pd, numpy as np
df = pd.read_pickle('/tmp/min.pkl')
k = df.kwh
mo = pd.DataFrame(dict(obs_kwh=k.resample('MS').sum(min_count=1), cov=k.notna().resample('MS').mean()))
mo['days_in'] = mo.index.days_in_month
# month window clipped to data range
mo['adj_kwh'] = k.resample('MS').mean() * 60 * 0 + k.resample('MS').mean() * mo.days_in * 24 * 60
print(mo.round(3).to_string())
wk = pd.DataFrame(dict(kwh=k.resample('W-SUN').sum(), cov=k.notna().resample('W-SUN').mean()))
wk['adj'] = k.resample('W-SUN').mean() * 7 * 1440
print(wk.tail(8))
h = k.groupby(k.index.hour).mean() * 60
print(h.round(2).to_string())
d = k.resample('D').sum(min_count=1)
print(d.groupby(d.index.dayofweek).mean().round(2))
