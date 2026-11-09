import pandas as pd, numpy as np, json, glob, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
here=Path(__file__).resolve().parent; src=here.parents[1]/"youtube_trending"
fr=[]
for f in sorted(src.glob("*videos.csv")):
    try: d=pd.read_csv(f,encoding="utf-8")
    except UnicodeDecodeError: d=pd.read_csv(f,encoding="latin1")
    d["region"]=f.name[:2]; fr.append(d)
d=pd.concat(fr,ignore_index=True)
print("rows",len(d)); print(d.groupby("region").size())
for c in ["comments_disabled","ratings_disabled","video_error_or_removed"]: d[c]=d[c].astype(str).str.lower().eq("true")
d["pub"]=pd.to_datetime(d.publish_time,errors="coerce",utc=True)
d["td"]=pd.to_datetime(d.trending_date,format="%y.%d.%m",errors="coerce")
print("bad dates",d.pub.isna().sum(),d.td.isna().sum()); 
d["lag_days"]=(d.td-d.pub.dt.tz_localize(None).dt.normalize()).dt.days
d["hour"]=d.pub.dt.hour
# unique video per region (peak views)
u=d.sort_values("views").groupby(["region","video_id"],as_index=False).tail(1).copy()
u["days_trending"]=u.set_index(["region","video_id"]).index.map(d.groupby(["region","video_id"]).size())
print("unique videos",len(u))
cats={}
for f in src.glob("*_category_id.json"):
    j=json.load(open(f,encoding="utf-8")); cats[f.name[:2]]={int(i["id"]):i["snippet"]["title"] for i in j["items"]}
u["cat"]=[cats.get(r,{}).get(c,str(c)) for r,c in zip(u.region,u.category_id)]
ok=u[(~u.ratings_disabled)&(u.views>0)]
g=u.groupby("region")
R=pd.DataFrame({"videos":g.size(),"median_views":g.views.median(),
 "like_per_100_views":ok.groupby("region").apply(lambda x:100*x.likes.sum()/x.views.sum()),
 "dislike_per_100_views":ok.groupby("region").apply(lambda x:100*x.dislikes.sum()/x.views.sum()),
 "comments_per_1000_views":u[~u.comments_disabled].groupby("region").apply(lambda x:1000*x.comment_count.sum()/x.views.sum()),
 "pct_comments_disabled":100*g.comments_disabled.mean(),"pct_ratings_disabled":100*g.ratings_disabled.mean(),
 "median_lag_days":g.lag_days.median(),"median_days_trending":g.days_trending.median()}).round(2)
R.to_csv(here/"region_metrics.csv"); print(R.to_string())
# category mix
cm=pd.crosstab(u.region,u.cat,normalize="index")*100
top=cm.mean().sort_values(ascending=False).head(8).index; cm[top].round(1).to_csv(here/"category_mix.csv"); print(cm[top].round(1).to_string())
print("top cat per region:",cm.idxmax(axis=1).to_dict())
# hour of publish (UTC) share 'peak hour'
hp=pd.crosstab(u.region,u.hour,normalize="index")*100; print("peak UTC hour",hp.idxmax(axis=1).to_dict())
# language note: music category share
# charts
fig,ax=plt.subplots(2,2,figsize=(12,8))
for a,(c,t) in zip(ax.ravel(),[("like_per_100_views","Likes per 100 views"),("comments_per_1000_views","Comments per 1,000 views"),("median_views","Median views per trending video"),("median_lag_days","Median days from publish to first trending date row")]):
    s=R[c].sort_values(); a.barh(s.index,s.values,color="#1f6feb"); a.set_title(t); a.spines[["top","right"]].set_visible(False)
plt.tight_layout(); plt.savefig(here/"region_engagement.png",dpi=130)
fig,ax=plt.subplots(figsize=(10,5)); cm2=cm[top].loc[R.index]; im=ax.imshow(cm2.values,cmap="Blues",aspect="auto")
ax.set_xticks(range(len(top)));ax.set_xticklabels(top,rotation=35,ha="right");ax.set_yticks(range(len(cm2)));ax.set_yticklabels(cm2.index)
for i in range(cm2.shape[0]):
    for j in range(cm2.shape[1]): ax.text(j,i,f"{cm2.values[i,j]:.0f}",ha="center",va="center",fontsize=8)
ax.set_title("Category mix of trending videos by region (% of unique videos)"); plt.tight_layout(); plt.savefig(here/"category_mix.png",dpi=130)
