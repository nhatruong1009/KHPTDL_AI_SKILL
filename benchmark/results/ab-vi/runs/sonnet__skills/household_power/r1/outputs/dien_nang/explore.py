import pandas as pd, numpy as np
m=pd.read_pickle('outputs/dien_nang/minute.pkl')
na=m.kwh.isna()
# gaps
g=(na!=na.shift()).cumsum()
runs=m[na].groupby(g[na]).apply(lambda x:(x.index[0],x.index[-1],len(x)))
runs=pd.DataFrame(runs.tolist(),columns=['start','end','minutes']).sort_values('minutes',ascending=False)
runs.to_csv('outputs/dien_nang/gaps.csv',index=False)
print(runs.head(15).to_string()); print(len(runs),(runs.minutes>=60).sum())
mo=m.kwh.resample('MS').agg(['sum','count'])
mo['days']=m.kwh.resample('MS').size()/1440
mo['cover']=mo['count']/m.kwh.resample('MS').size()
mo['kwh_per_day_obs']=mo['sum']/(mo['count']/1440)
print(mo.round(3).to_string())
