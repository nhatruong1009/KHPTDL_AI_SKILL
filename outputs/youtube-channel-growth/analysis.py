import pandas as pd, numpy as np, json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
here=Path(__file__).resolve().parent; src=here.parents[1]/"youtube_trending"
fr=[]
for f in sorted(src.glob("*videos.csv")):
    try: d=pd.read_csv(f,encoding="utf-8")
    except UnicodeDecodeError: d=pd.read_csv(f,encoding="latin1")
    d["region"]=f.name[:2]; fr.append(d)
d=pd.concat(fr,ignore_index=True)
u=d.sort_values("views").groupby(["region","video_id"],as_index=False).tail(1).copy()
cats={}
for f in src.glob("*_category_id.json"):
    j=json.load(open(f,encoding="utf-8")); cats[f.name[:2]]={int(i["id"]):i["snippet"]["title"] for i in j["items"]}
u["cat"]=[cats[r].get(c,str(c)) for r,c in zip(u.region,u.category_id)]
u["pub"]=pd.to_datetime(u.publish_time,utc=True); u["hour"]=u.pub.dt.hour; u["dow"]=u.pub.dt.day_name()
u["ntags"]=u.tags.fillna("").map(lambda s:0 if s in("","[none]") else s.count("|")+1)
u["tlen"]=u.title.str.len()
# channel counts: share of trending videos from channels with >=5 trending videos
cc=u.groupby(["region","channel_title"]).size()
print("channels",cc.groupby("region").size().to_dict())
print("unique channels total",u.channel_title.nunique())
sh=u.merge(cc.rename("n").reset_index(),on=["region","channel_title"]).groupby("region").apply(lambda x:100*(x.n>=5).mean()).round(1)
print("% of videos from channels with >=5 trending videos:\n",sh.to_dict())
one=(cc==1).groupby("region").mean().mul(100).round(1); print("% channels with exactly 1 trending video:",one.to_dict())
# category: channels & median views (pooled, per-region median then average)
c=u.groupby(["region","cat"]).agg(videos=("video_id","size"),channels=("channel_title","nunique"),med_views=("views","median")).reset_index()
c["videos_per_channel"]=c.videos/c.channels
P=c.groupby("cat").agg(regions=("region","nunique"),videos=("videos","sum"),med_views=("med_views","median"),videos_per_channel=("videos_per_channel","mean")).sort_values("videos",ascending=False)
P.round(2).to_csv(here/"category_summary.csv"); print(P.head(12).round(2).to_string())
# title/tags
u["tag_bin"]=pd.cut(u.ntags,[-1,0,5,10,20,100],labels=["0","1-5","6-10","11-20","21+"])
print(u[u.region.isin(["US","CA","GB"])==False].groupby("tag_bin").views.median().round(0).to_dict())
u["tl_bin"]=pd.cut(u.tlen,[0,30,50,70,100],labels=["<=30","31-50","51-70","71-100"]); print(u.groupby("tl_bin").views.median().round(0).to_dict())
h=u.groupby("hour").size()/len(u)*100; print("share by UTC hour:",h.round(1).to_dict())
u.groupby("dow").size().div(len(u)).mul(100).round(1).to_csv(here/"publish_dow.csv")
print(u.groupby("dow").size().div(len(u)).mul(100).round(1).to_dict())
fig,ax=plt.subplots(figsize=(8,5)); p=P.head(10).sort_values("videos_per_channel")
ax.barh(p.index,p.videos_per_channel,color="#1f6feb"); ax.set_xlabel("Avg trending videos per channel (mean over regions)"); ax.set_title("Category: how concentrated are trending videos in a few channels?")
ax.spines[["top","right"]].set_visible(False); plt.tight_layout(); plt.savefig(here/"category_concentration.png",dpi=130)
