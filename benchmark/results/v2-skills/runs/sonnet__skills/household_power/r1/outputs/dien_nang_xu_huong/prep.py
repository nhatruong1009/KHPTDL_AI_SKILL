import pandas as pd, numpy as np
df = pd.read_csv('data/household_power_consumption.txt', sep=';', na_values='?', low_memory=False)
df['ts'] = pd.to_datetime(df.Date + ' ' + df.Time, format='%d/%m/%Y %H:%M:%S')
df = df.drop(columns=['Date', 'Time']).set_index('ts').sort_index()
print(len(df), df.index.is_unique, df.index.min(), df.index.max())
full = pd.date_range(df.index.min(), df.index.max(), freq='min')
print('expected', len(full), 'present', len(df), 'missing rows', len(full) - len(df),
      'NaN in present', df.Global_active_power.isna().sum())
df = df.reindex(full)
df['kwh'] = df.Global_active_power / 60  # kW * 1/60 h
m = df.kwh.isna()
g = (m != m.shift()).cumsum()
r = pd.DataFrame(dict(start=m.index.to_series().groupby(g.values).first(),
                      len=m.groupby(g.values).size(),
                      miss=m.groupby(g.values).first()))
r = r[r.miss].sort_values('len', ascending=False)
print(r.head(15))
print((r.len >= 60).sum(), 'gaps >=1h; total missing min', m.sum())
df.to_pickle('/tmp/min.pkl')
