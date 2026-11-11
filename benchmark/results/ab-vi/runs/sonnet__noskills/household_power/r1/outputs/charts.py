import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W='/root/.cache/skill-bench/runs/ab-vi/sonnet__noskills/household_power/r1/workspace/'
df=pd.read_pickle('/tmp/df.pkl'); d=pd.read_csv(W+'outputs/daily.csv',index_col=0,parse_dates=True)
m=pd.read_csv(W+'outputs/monthly.csv',index_col=0); m.index=pd.PeriodIndex(m.index,freq='M')
wk=pd.read_csv(W+'outputs/weekly.csv',index_col=0,parse_dates=True)
gaps=pd.read_csv(W+'outputs/gaps.csv',parse_dates=['start'])
C='#2a6fb0';R='#d1495b';G='#888888'
plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False,'font.size':10})
# 1 xu hướng + bất thường
fig,ax=plt.subplots(figsize=(11,4.5))
ax.plot(wk.index,wk.kwh_week,color=C,lw=1,label='Điện năng theo tuần (kWh)')
an=wk[wk.z.abs()>3]
ax.scatter(an.index,an.kwh_week,color=R,s=18,zorder=3,label='Tuần bất thường (|z|>3)')
for _,r in gaps.iterrows():
    ax.axvspan(r.start,r.start+pd.Timedelta(hours=r.hours),color=G,alpha=.35,lw=0)
ax.axvspan(pd.Timestamp('2010-01-01'),pd.Timestamp('2010-01-01'),color=G,alpha=.35,label='Khoảng trống dữ liệu ≥1 giờ')
ax.set_title('Điện năng tiêu thụ theo tuần, 12/2006–11/2010: mùa vụ ổn định, không có xu hướng dài hạn')
ax.set_ylabel('kWh / tuần');ax.legend(frameon=False,loc='upper right',fontsize=9)
fig.tight_layout();fig.savefig(W+'outputs/chart1_xuhuong_batthuong.png',dpi=130);plt.close()
# 2 chu kỳ ngày, tuần, năm
k=df.kwh; wkend=k.index.dayofweek>=5
fig,axs=plt.subplots(1,3,figsize=(13,4))
for msk,lab,c in [(~wkend,'Ngày thường',C),(wkend,'Cuối tuần',R)]:
    s=k[msk].groupby(k[msk].index.hour).mean()*60; axs[0].plot(s.index,s.values,color=c,label=lab)
axs[0].set_title('Theo giờ trong ngày');axs[0].set_xlabel('Giờ');axs[0].set_ylabel('Công suất TB (kW)');axs[0].legend(frameon=False)
dow=d.kwh_day.groupby(d.index.dayofweek).mean()
axs[1].bar(['T2','T3','T4','T5','T6','T7','CN'],dow.values,color=[C]*5+[R]*2);axs[1].set_title('Theo thứ trong tuần');axs[1].set_ylabel('kWh / ngày')
dd=d[~((d.index>='2008-07-25')&(d.index<'2008-09-01'))]
mo=dd.kwh_day.groupby(dd.index.month).mean()
axs[2].bar(range(1,13),mo.values,color=C);axs[2].set_xticks(range(1,13));axs[2].set_title('Theo tháng trong năm');axs[2].set_xlabel('Tháng');axs[2].set_ylabel('kWh / ngày')
fig.tight_layout();fig.savefig(W+'outputs/chart2_mua_vu.png',dpi=130);plt.close()
# 3 dự báo
y=m.kwh_month.drop(pd.Period('2006-12')).copy()
fig,ax=plt.subplots(figsize=(11,4.5))
x=y.index.to_timestamp()
ax.plot(x,y.values,color=C,marker='o',ms=3,label='Tổng tháng (đã hiệu chỉnh theo độ phủ dữ liệu)')
t=pd.Timestamp('2010-12-01')
ax.errorbar([t],[1040],yerr=[[1040-849],[1274-1040]],color=R,capsize=5,marker='D',label='Dự báo 12/2010: 1.040 kWh (KTC 95%: 849–1.274)')
ax.errorbar([t],[1040],yerr=[[1040-914],[1184-1040]],color=R,capsize=0,lw=5,alpha=.5)
ax.annotate('Tháng 8/2008: vắng nhà',(pd.Timestamp('2008-08-01'),206),xytext=(pd.Timestamp('2008-09-15'),150),fontsize=9)
ax.set_title('Tổng điện năng theo tháng và dự báo tháng 12/2010');ax.set_ylabel('kWh / tháng');ax.legend(frameon=False,loc='upper right',fontsize=9)
fig.tight_layout();fig.savefig(W+'outputs/chart3_dubao.png',dpi=130);plt.close()
