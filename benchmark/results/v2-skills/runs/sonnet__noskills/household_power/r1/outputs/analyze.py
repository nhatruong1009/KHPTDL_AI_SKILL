import pandas as pd, numpy as np
pd.set_option('display.width',200)
W='/root/.cache/skill-bench/runs/ab-vi/sonnet__noskills/household_power/r1/workspace/'
df=pd.read_pickle('/tmp/df.pkl')
k=df.kwh
# daily: sum observed, coverage
d=pd.DataFrame({'obs':k.groupby(k.index.floor('D')).sum(),'n':k.groupby(k.index.floor('D')).count()})
d['cov']=d.n/1440
d['kwh_day']=np.where(d['cov']>=0.9,d.obs/d['cov'],np.nan)  # gap-scaled; days <90% coverage dropped
d.to_csv(W+'outputs/daily.csv')
# monthly: mean daily rate of valid days * days in month
m=d.groupby(d.index.to_period('M')).agg(valid=('kwh_day','count'),mean_day=('kwh_day','mean'))
m['days']=m.index.days_in_month
m['kwh_month']=m.mean_day*m.days
m['kwh_month_raw']=d.obs.groupby(d.index.to_period('M')).sum()
m['cov']=d['cov'].groupby(d.index.to_period('M')).mean()
m.to_csv(W+'outputs/monthly.csv')
print(m.round(1))
# yearly (full years 2007-2009)
print(m.groupby(m.index.year).kwh_month.sum().round(0))
# hourly profile
h=k.groupby(k.index.hour).mean()*60
print('hour kW',h.round(2).to_dict())
dow=d.kwh_day.groupby(d.index.dayofweek).mean();print('dow',dow.round(2).to_dict())
mo=d.kwh_day.groupby(d.index.month).mean();print('month',mo.round(2).to_dict())
# weekday vs weekend hourly
wk=(k.index.dayofweek>=5)
print('weekend h',(k[wk].groupby(k[wk].index.hour).mean()*60).round(2).to_dict())
print('weekday h',(k[~wk].groupby(k[~wk].index.hour).mean()*60).round(2).to_dict())
# weekly anomalies
wkly=d.kwh_day.resample('W-SUN').agg(['mean','count'])
wkly=wkly[wkly['count']>=5]['mean']*7
wk_s=wkly.copy()
# deseasonalize: weekly-of-year median
woy=wk_s.index.isocalendar().week.values
doy=pd.Series(wk_s.values,index=wk_s.index)
# robust residual vs centered 9-wk rolling median
base=doy.rolling(9,center=True,min_periods=5).median()
res=np.log(doy/base)
z=(res-res.median())/(1.4826*(res-res.median()).abs().median())
an=pd.DataFrame({'kwh_week':doy,'base':base,'z':z}).round(2)
an.to_csv(W+'outputs/weekly.csv')
print(an[an.z.abs()>3].sort_values('z'))
print('trend slope: yearly means', d.kwh_day.groupby(d.index.year).mean().round(2).to_dict())
