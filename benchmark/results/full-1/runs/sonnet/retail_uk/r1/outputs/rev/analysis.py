import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
O='outputs/rev/'
a=pd.read_pickle(O+'Year_2009-2010.pkl');b=pd.read_pickle(O+'Year_2010-2011.pkl')
b=b[b.InvoiceDate>='2010-12-10']            # overlap 1-9/12/2010 identical in both sheets
d=pd.concat([a,b],ignore_index=True)
d['Invoice']=d.Invoice.astype(str); d['StockCode']=d.StockCode.astype(str)
n0=len(d)
nonprod=['POST','DOT','M','D','C2','S','BANK CHARGES','ADJUST','ADJUST2','AMAZONFEE','PADS','CRUK','B','TEST001','TEST002']
d=d[~d.StockCode.isin(nonprod)&(d.Price>0)].copy()
print('rows kept',len(d),'of',n0)
d['rev']=d.Quantity*d.Price
d['cust']=d['Customer ID']
d['year']=d.InvoiceDate.dt.year
d['md']=d.InvoiceDate.dt.strftime('%m-%d')
# fair window: 1 Jan - 9 Dec (data ends 9 Dec 2011)
w=d[(d.md<='12-09')&(d.year.isin([2010,2011]))].copy()
tot=w.groupby('year').rev.sum(); print(tot, tot[2011]/tot[2010]-1)
full=d.groupby('year').rev.sum(); print('naive full-year',full.to_dict())
# gross vs returns
w['ret']=w.Invoice.str.startswith('C')
print(w.groupby(['year','ret']).rev.sum().unstack())
# customer status: identified customers only
first=d.dropna(subset=['cust']).groupby('cust').InvoiceDate.min()
w['first']=w.cust.map(first)
def seg(r):
    if pd.isna(r.cust): return 'Unidentified (no ID)'
    return 'New (1st purchase in year)' if r['first'].year==r.year else 'Existing (bought before 1 Jan)'
w['seg']=w.apply(seg,axis=1)
s=w.groupby(['seg','year']).rev.sum().unstack(); s['chg']=s[2011]-s[2010]; s['share_of_chg']=s.chg/s.chg.sum()
print(s); s.to_csv(O+'segment.csv')
# existing detail: customers retained (active both yrs)
cnt=w.dropna(subset=['cust']).groupby(['seg','year']).cust.nunique().unstack(); print(cnt); cnt.to_csv(O+'segment_customers.csv')
# existing 2011: those who bought in 2010 (retained) vs reactivated
act10=set(w[(w.year==2010)].cust.dropna())
e=w[(w.year==2011)&(w.seg.str.startswith('Existing'))]
print('existing 2011 rev from 2010-active',e[e.cust.isin(act10)].rev.sum(),'reactivated(dormant)',e[~e.cust.isin(act10)].rev.sum())
# 2010 left-censoring: "existing" in 2010 only sees Dec 2009 history
ex10=w[(w.year==2010)&w.seg.str.startswith('Existing')].cust.nunique(); print('exist 2010 custs',ex10)
# 2010 new customers retention to 2011 vs 2009-cohort
c09=set(first[first<'2010-01-01'].index); c10=set(first[(first>='2010-01-01')&(first<'2011-01-01')].index)
r=w[w.year==2011].groupby('cust').rev.sum()
for n,c in [('first bought Dec2009',c09),('first bought 2010',c10)]:
    print(n,len(c),'active 2011:',len(c&set(r.index)),'rev2011',r[r.index.isin(c)].sum())
# country
cy=w.groupby(['Country','year']).rev.sum().unstack().fillna(0); cy['chg']=cy[2011]-cy[2010]
cy['pct']=cy.chg/cy[2010]; cy['share_of_total_chg']=cy.chg/cy.chg.sum()
cy=cy.sort_values('chg'); print(cy.head(6)); print(cy.tail(8)); cy.to_csv(O+'country.csv')
# UK vs export, new/existing by UK
w['uk']=np.where(w.Country=='United Kingdom','UK','Non-UK')
x=w.groupby(['uk','seg','year']).rev.sum().unstack(); x['chg']=x[2011]-x[2010]; print(x); x.to_csv(O+'uk_seg.csv')
# monthly
m=w.groupby(['year',w.InvoiceDate.dt.month]).rev.sum().unstack(0); m['pct']=m[2011]/m[2010]-1; print(m); m.to_csv(O+'monthly.csv')
# charts
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
v=s.chg.drop('Unidentified (no ID)',errors='ignore')
s2=s.chg/1e3
cols=['#2a7ab0' if x>=0 else '#c0504d' for x in s2]
ax[0].barh(s2.index,s2.values,color=cols); ax[0].set_title('Revenue change 2011 vs 2010 by customer type (£k, 1 Jan–9 Dec)'); ax[0].axvline(0,c='k',lw=.8)
for i,v_ in enumerate(s2): ax[0].text(v_,i,f' {v_:,.0f}',va='center')
top=pd.concat([cy.head(4),cy.tail(4)]).chg/1e3
ax[1].barh(top.index,top.values,color=['#2a7ab0' if x>=0 else '#c0504d' for x in top]); ax[1].set_title('Top movers by country (£k)'); ax[1].axvline(0,c='k',lw=.8)
plt.tight_layout(); plt.savefig(O+'chart.png',dpi=130)

# --- like-for-like sensitivity: 2011 "new" = no purchase in Dec 2010 lookback only? (2010 has only Dec-2009 history)
# Use identical 1-month lookback: customer is "existing" in year Y if bought in Dec of Y-1 ... too narrow; instead
# use 12-month lookback for 2011 vs the only available (1 month) for 2010 and report both.
dd=d.dropna(subset=['cust'])
def newrev(year,lookback_start):
    ww=w[(w.year==year)&w.cust.notna()]
    prior=set(dd[(dd.InvoiceDate>=lookback_start)&(dd.InvoiceDate<f'{year}-01-01')].cust)
    return ww[~ww.cust.isin(prior)].rev.sum(), ww[ww.cust.isin(prior)].rev.sum()
print('2010 new/exist (lookback Dec09)',newrev(2010,'2009-12-01'))
print('2011 new/exist (lookback Dec10 only)',newrev(2011,'2010-12-01'))
print('2011 new/exist (lookback all)',newrev(2011,'2009-12-01'))

# new customers per month (first-ever purchase) and their first-month revenue
f=dd.groupby('cust').InvoiceDate.min().dt.to_period('M')
nm=f.value_counts().sort_index(); print(nm.to_string()); nm.to_csv(O+'new_cust_by_month.csv')
# like-for-like: Sep-Nov (>=9 months of history for 2010)
for y in (2010,2011):
    print(y,'new cust Jul-Nov',sum(nm[pd.Period(f'{y}-{m:02d}')] for m in range(7,12)))
# 2011 revenue by acquisition vintage
dv=w[w.year==2011].dropna(subset=['cust']).copy(); dv['vint']=dv['first'].dt.year
print(dv.groupby('vint').rev.sum())
# 2010 revenue by vintage 
dv0=w[w.year==2010].dropna(subset=['cust']).copy(); dv0['vint']=dv0['first'].dt.year; print(dv0.groupby('vint').rev.sum())
