import pandas as pd, numpy as np
df = pd.read_csv('data/household_power_consumption.txt', sep=';', na_values='?', low_memory=False)
df['ts'] = pd.to_datetime(df.Date + ' ' + df.Time, format='%d/%m/%Y %H:%M:%S')
df = df.set_index('ts').drop(columns=['Date', 'Time']).astype(float)
print(df.shape, df.index.min(), df.index.max(), df.index.is_unique)
print(df.isna().sum())
full = pd.date_range(df.index.min(), df.index.max(), freq='min')
print('missing minutes in index', len(full) - len(df))
df = df.reindex(full)
df['kwh'] = df.Global_active_power / 60  # kW * 1/60 h
df[['kwh', 'Global_active_power']].to_pickle('outputs/dien_nang/minute.pkl')
print(df.describe().T)
