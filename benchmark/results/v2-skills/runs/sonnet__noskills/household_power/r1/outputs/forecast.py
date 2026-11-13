import pandas as pd, numpy as np
W='/root/.cache/skill-bench/runs/ab-vi/sonnet__noskills/household_power/r1/workspace/'
m=pd.read_csv(W+'outputs/monthly.csv',index_col=0)
m.index=pd.PeriodIndex(m.index,freq='M')
y=m.kwh_month.copy()
y['2006-12']=np.nan            # nửa tháng đầu, không đại diện
y['2008-08']=np.nan            # tháng vắng nhà bất thường
y=y.drop(pd.Period('2006-12'))
ly=np.log(y)

def fc(ly,t):
    """seasonal-naive điều chỉnh mức: trung bình log cùng tháng các năm trước + lệch mức 12 tháng gần nhất"""
    hist=ly[ly.index<t]
    same=hist[hist.index.month==t.month].dropna()
    last12=hist.iloc[-12:]
    # lệch mức: 12 tháng gần nhất so với giá trị trung bình mùa vụ của chính các tháng đó
    seas=hist.groupby(hist.index.month).mean()
    dev=(last12.dropna()-seas.reindex(last12.dropna().index.month).values).mean()
    return same.mean()+dev if len(same) else np.nan, len(same)
errs=[]
for t in y.index:
    if t<pd.Period('2008-10') or t==pd.Period('2008-08') or np.isnan(ly[t]): continue
    p,n=fc(ly,t)
    if t.month==8 and t.year==2009: pass
    errs.append((str(t),np.exp(p),y[t],ly[t]-p))
e=pd.DataFrame(errs,columns=['month','pred','actual','logerr']).set_index('month')
print(e.round(3))
print('MAPE',(np.exp(e.logerr)-1).abs().mean(),'sd logerr',e.logerr.std(),'n',len(e))
# bỏ tháng có độ phủ thấp khi tính sai số? giữ nguyên, báo cáo
t=pd.Period('2010-12')
p,n=fc(ly,t)
sd=e.logerr.std(ddof=1)
from scipy import stats
tq=stats.t.ppf([0.025,0.1,0.9,0.975],df=len(e)-1)
print('point',np.exp(p),'same-month n',n)
for q,a in zip([2.5,10,90,97.5],tq): print(q,np.exp(p+a*sd*np.sqrt(1+1/len(e))))
# kiểm tra chéo: ước lượng thô
dec=y[y.index.month==12];print(dec)
print('dev', p-ly[ly.index.month==12].mean())
# kiểm tra: tỷ lệ YoY 12 tháng gần nhất
l12=y['2009-12':'2010-11'].sum(); p12=y['2008-12':'2009-11'].sum();print('YoY 12m',l12/p12,l12,p12)
# hệ số mức: 2010 vs 2009 cùng tháng Jan-Nov
print('Jan-Nov 2010/2009',y['2010-01':'2010-11'].sum()/y['2009-01':'2009-11'].sum())
# nov 2010 corrected: dữ liệu đến 26/11
