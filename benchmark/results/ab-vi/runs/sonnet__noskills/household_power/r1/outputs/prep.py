import pandas as pd, numpy as np
W='/root/.cache/skill-bench/runs/ab-vi/sonnet__noskills/household_power/r1/workspace/'
df=pd.read_csv(W+'data/household_power_consumption.txt',sep=';',na_values='?',low_memory=False)
df['dt']=pd.to_datetime(df.Date+' '+df.Time,format='%d/%m/%Y %H:%M:%S')
df=df.set_index('dt').drop(columns=['Date','Time']).astype(float)
print(len(df),df.isna().sum().iloc[0],df.index.min(),df.index.max())
full=pd.date_range(df.index.min(),df.index.max(),freq='min')
print('absent rows',len(full)-len(df))
df=df.reindex(full)
df['kwh']=df.Global_active_power/60
df.to_pickle('/tmp/df.pkl')
na=df.kwh.isna()
g=(na!=na.shift()).cumsum()
runs=na.groupby(g).agg(['first','size']);runs=runs[runs['first']]
runs['start']=na.index.to_series().groupby(g).first()[runs.index].values
runs['hours']=runs['size']/60
print(runs.sort_values('size',ascending=False).head(20)[['start','hours']])
print('total NaN min',na.sum(), na.mean(), 'n runs',len(runs), (runs['size']>=60).sum())
runs[runs['size']>=60][['start','hours']].to_csv(W+'outputs/gaps.csv')
