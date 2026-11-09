import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path
here=Path(__file__).resolve().parent; src=here.parents[1]/"gun_violence"
p=pd.read_csv(src/"country_gun_profile.csv")
print(p.shape); print(p[["firearms_per_100_people","avg_2013_2022_firearm_homicide_rate","gdp_per_capita_usd_2017","gini_index_2017"]].describe().round(2).to_string())
d=p.dropna(subset=["firearms_per_100_people","avg_2013_2022_firearm_homicide_rate"]).copy()
print("countries with both:",len(d))
d["lf"]=np.log(d.avg_2013_2022_firearm_homicide_rate.clip(lower=0.01)); 
d["lg"]=np.log(d.gdp_per_capita_usd_2017)
x,y="firearms_per_100_people","avg_2013_2022_firearm_homicide_rate"
rho,pv=stats.spearmanr(d[x],d[y]); print("Spearman guns vs firearm homicide",round(rho,3),pv)
# bootstrap CI
rng=np.random.default_rng(0); bs=[stats.spearmanr(*d[[x,y]].sample(len(d),replace=True,random_state=int(s)).values.T)[0] for s in rng.integers(0,1e6,2000)]
print("CI",np.percentile(bs,[2.5,97.5]).round(3))
print("w/o USA:",stats.spearmanr(d[d.iso3!="USA"][x],d[d.iso3!="USA"][y])[0].round(3))
# by income group
rows=[]
for g,s in d.groupby("income_group"):
    r=stats.spearmanr(s[x],s[y])[0] if len(s)>=8 else np.nan
    rows.append(dict(income_group=g,n=len(s),median_guns=s[x].median(),median_fhr=s[y].median(),spearman=r))
I=pd.DataFrame(rows).round(3); print(I.to_string(index=False)); I.to_csv(here/"by_income_group.csv",index=False)
# by region
rows=[]
for g,s in d.groupby("region"):
    rows.append(dict(region=g,n=len(s),median_guns=s[x].median(),median_fhr=s[y].median(),spearman=stats.spearmanr(s[x],s[y])[0] if len(s)>=8 else np.nan))
R=pd.DataFrame(rows).round(3); print(R.to_string(index=False)); R.to_csv(here/"by_region.csv",index=False)
# adjusted: OLS log(fhr) ~ guns + log gdp + gini
m=d.dropna(subset=["gini_index_2017","lg"])
print("n with gini:",len(m))
def ols(cols,df):
    X=np.column_stack([np.ones(len(df))]+[(df[c]-df[c].mean())/df[c].std() for c in cols]); return np.linalg.lstsq(X,df["lf"].values,rcond=None)[0]
print("unadj std coef guns:",ols([x],m)[1].round(3))
print("adj coefs [const,guns,logGDP,gini]:",ols([x,"lg","gini_index_2017"],m).round(3))
bs=[ols([x,"lg","gini_index_2017"],m.sample(len(m),replace=True,random_state=int(s)))[1] for s in rng.integers(0,1e6,2000)]
print("adj guns CI",np.percentile(bs,[2.5,97.5]).round(3))
print(m[[x,"lg","gini_index_2017","lf"]].corr(method="spearman").round(2))
# top
print(d.sort_values(y,ascending=False)[["country","firearms_per_100_people",y,"income_group"]].head(8).to_string(index=False))
print(d[d.firearms_per_100_people>=30][["country",x,y]].sort_values(y).to_string(index=False))
# charts
fig,ax=plt.subplots(figsize=(9,6)); cols={"High income":"#1f6feb","Upper middle income":"#2da44e","Lower middle income":"#d29922","Low income":"#e5484d"}
for g,s in d.groupby("income_group"): ax.scatter(s[x],s[y],s=30,alpha=.8,label=g,color=cols.get(g,"gray"))
ax.set_yscale("log"); ax.set_xlabel("Civilian firearms per 100 people (2017)"); ax.set_ylabel("Firearm homicide rate per 100k (avg 2013-2022, log)")
for iso in ["USA","BRA","VEN","HND","SLV","JAM","FIN","CHE","CAN"]:
    r=d[d.iso3==iso]
    if len(r): ax.annotate(iso,(r[x].iloc[0],r[y].iloc[0]),fontsize=8,xytext=(3,3),textcoords="offset points")
ax.set_title(f"Gun ownership vs firearm homicide ({len(d)} countries, Spearman {rho:.2f})"); ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False)
plt.tight_layout(); plt.savefig(here/"guns_vs_firearm_homicide.png",dpi=130)
