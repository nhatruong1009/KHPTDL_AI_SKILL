import pandas as pd, numpy as np
df = pd.read_csv('../../data/household_power_consumption.txt', sep=';', na_values='?', low_memory=False)
df['ts'] = pd.to_datetime(df.Date + ' ' + df.Time, format='%d/%m/%Y %H:%M:%S')
df = df.set_index('ts').drop(columns=['Date', 'Time'])
print(df.index.is_unique, df.index.is_monotonic_increasing, len(df), df.index.min(), df.index.max())
full = pd.date_range(df.index.min(), df.index.max(), freq='min')
print('absent minutes:', len(full) - len(df), ' NaN rows:', df.Global_active_power.isna().sum())
df = df.reindex(full)
df['kwh'] = df.Global_active_power / 60  # kW trung binh/phut -> kWh/phut
na = df.Global_active_power.isna()
r = (na != na.shift()).cumsum()
runs = pd.DataFrame({'start': na.index.to_series().groupby(r).first(),
                     'minutes': na.groupby(r).size(), 'isn': na.groupby(r).first()})
runs = runs[runs['isn']].drop(columns='isn').sort_values('minutes', ascending=False)
runs['end'] = runs.start + pd.to_timedelta(runs.minutes - 1, unit='min')
print(runs.head(15).to_string())
runs.to_csv('gap_runs.csv', index=False)
d = df.kwh.groupby(df.index.normalize()).agg(kwh='sum', n='count')
d['coverage'] = d.n / 1440
d.to_csv('daily.csv')
print(d.coverage.describe())
print('days cov<1:', (d.coverage < 1).sum(), ' cov==0:', (d.coverage == 0).sum())
h = df.kwh.resample('h').agg(['sum', 'count'])
h.to_csv('hourly.csv')
