import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
here=Path(__file__).resolve().parent; root=here.parents[1]
d=pd.read_csv(root/"sales_data_sample.csv",encoding="latin1")
d["date"]=pd.to_datetime(d.ORDERDATE); end=d.date.max()
print("end",end)
o=d.groupby("ORDERNUMBER").agg(date=("date","first"),cust=("CUSTOMERNAME","first"),status=("STATUS","first"),sales=("SALES","sum"),country=("COUNTRY","first"),yr=("YEAR_ID","first"),m=("MONTH_ID","first")).reset_index()
ok=o[o.status!="Cancelled"]
# 1 stuck cash
stuck=o[o.status.isin(["On Hold","Disputed"])]
print("STUCK",stuck.groupby("status").sales.agg(["count","sum"]), stuck.sales.sum())
# 2 seasonality: share of annual revenue by month (2003,2004 full years)
s=ok[ok.yr.isin([2003,2004])].pivot_table(index="m",columns="yr",values="sales",aggfunc="sum")
sh=(s/s.sum()*100).round(1); print(sh); sh.to_csv(here/"monthly_share.csv")
print("Sep-Dec share",sh.loc[9:12].sum().round(1).to_dict())
# 3 customer recency
last=ok.groupby("cust").agg(last=("date","max"),n=("sales","size"),rev=("sales","sum"),first=("date","min")).reset_index()
last["days"]=(end-last["last"]).dt.days
def b(x): return "0-90" if x<=90 else "91-180" if x<=180 else "181-365" if x<=365 else ">365"
last["rec"]=last.days.map(b)
r=last.groupby("rec").agg(customers=("cust","size"),lifetime_rev=("rev","sum"),avg_rev=("rev","mean"));print(r)
# win-back list: lapsed >180d with lifetime rev, ranked
w=last[last.days>180].sort_values("rev",ascending=False); w.to_csv(here/"winback_candidates.csv",index=False)
print("lapsed>180",len(w),w.rev.sum(),"top15 rev",w.head(15).rev.sum()); print(w.head(10)[["cust","last","n","rev","days"]])
# annual revenue per customer repeat
act=ok[ok.yr==2004].groupby("cust").sales.sum(); print("2004 custs",len(act),"avg",act.mean())
bought05=set(ok[ok.yr==2005].cust); lost=[c for c in act.index if c not in bought05]
print("2004 custs not yet bought 2005",len(lost),act[lost].sum(), act[lost].sum()/act.sum())
# 4 concentration lifetime
t=ok.groupby("cust").sales.sum().sort_values(ascending=False); print("top1,top5 share",t.iloc[0]/t.sum(),t.iloc[:5].sum()/t.sum())
# 5 frequency: customers with 1 order only
print("1-order custs",(last.n==1).sum(),"of",len(last))
# 6 country/product concentration & gaps
c=ok.groupby("country").sales.sum().sort_values(ascending=False); print((c/c.sum()*100).round(1).head(8)); 
# 7 deal size
ds=d[d.STATUS!="Cancelled"].groupby("DEALSIZE").SALES.agg(["count","sum"]);print(ds,(ds["sum"]/ds["sum"].sum()).round(3))
# 8 product x year mix
p=ok.pivot_table(index=ok.yr,values="sales",aggfunc="sum");print(p)
# chart: seasonality + 2005 YTD
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
for y,col in zip([2003,2004],["#9aa5b1","#1f6feb"]): ax[0].plot(sh.index,sh[y],marker="o",color=col,label=str(y))
ax[0].axvspan(9,12,color="#fde68a",alpha=.4); ax[0].set_title("Share of annual revenue by month\n(Sep-Dec = peak season)"); ax[0].set_xlabel("Month"); ax[0].set_ylabel("% of year"); ax[0].legend()
ax[0].spines[["top","right"]].set_visible(False)
rr=r.reindex(["0-90","91-180","181-365",">365"]); ax[1].bar(rr.index,rr.customers,color=["#1f6feb","#1f6feb","#e5484d","#e5484d"])
for i,(v,rv) in enumerate(zip(rr.customers,rr.lifetime_rev)): ax[1].text(i,v+.5,f"{v}\n{rv/1e3:.0f}K USD",ha="center",fontsize=9)
ax[1].set_title("Customers by days since last order\n(as of 2005-05-31; label = lifetime revenue)"); ax[1].set_xlabel("Days since last order"); ax[1].set_ylim(0,rr.customers.max()*1.25)
ax[1].spines[["top","right"]].set_visible(False)
plt.tight_layout(); plt.savefig(here/"rescue_levers.png",dpi=130)
