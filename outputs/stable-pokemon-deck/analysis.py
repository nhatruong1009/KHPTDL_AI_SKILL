import json, collections as C, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
here=Path(__file__).resolve().parent
E=json.load(open(here/"episodes.json"))
cn={}
for e in E: cn.update({int(k):v for k,v in e["cardnames"].items()})
ids={}  # decklist -> short id
rows=[]
for e in sorted(E,key=lambda e:e["ep"]):
    if None in e["rewards"]: continue
    k=[tuple(sorted(d)) for d in e["decks"]]
    for s in (0,1):
        ids.setdefault(k[s],None)
        rows.append(dict(ep=e["ep"],deck=k[s],opp=k[1-s],agent=e["names"][s],win=int(e["rewards"][s]>0)))
df=pd.DataFrame(rows)
def lbl(d):  # label by most frequent non-energy Pokemon-ish names: use top 3 most-copied non-energy cards
    c=C.Counter(d); top=[cn.get(i,str(i)) for i,_ in sorted(c.items(),key=lambda x:-x[1]) if "Energy" not in cn.get(i,"")][:2]
    return " / ".join(top)
order=df.deck.value_counts().index.tolist()
D={d:f"D{i+1:02d}" for i,d in enumerate(order)}
df["D"]=df.deck.map(D); df["O"]=df.opp.map(D)
def wilson(w,n,z=1.96):
    p=w/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den; return c-h,c+h
out=[]
for d,g in df.groupby("D"):
    n=len(g); w=g.win.sum(); lo,hi=wilson(w,n)
    m=g.groupby("O").win.agg(["sum","count"]); m=m[m["count"]>=10]; mwr=m["sum"]/m["count"]
    h=g.ep<g.ep.median()
    # per-pilot WR spread (pilots with >=15 games)
    pa=g.groupby("agent").win.agg(["mean","count"]); pa=pa[pa["count"]>=15]
    out.append(dict(deck=d,games=n,winrate=w/n,ci_lo=lo,ci_hi=hi,pilots=g.agent.nunique(),
      opp_decks_ge10=len(m),worst_matchup_wr=mwr.min() if len(m) else np.nan,matchup_wr_sd=mwr.std() if len(m)>1 else np.nan,
      wr_first_half=g[h].win.mean() if h.sum() else np.nan,wr_second_half=g[~h].win.mean() if (~h).sum() else np.nan,
      pilot_wr_sd=pa["mean"].std() if len(pa)>1 else np.nan,key_cards=lbl(next(k for k,v in D.items() if v==d))))
T=pd.DataFrame(out).sort_values("games",ascending=False); T.to_csv(here/"deck_stability.csv",index=False)
pd.set_option("display.width",250); pd.set_option("display.max_columns",20)
print(len(df),"sides");print(T[T.games>=30].round(3).to_string(index=False))
print("small decks:",(T.games<30).sum(),T[T.games<30].games.sum())
# confound check: decks used by >1 pilot
print(T[T.pilots>1][["deck","games","pilots"]])
df.to_csv(here/"deck_games.csv",index=False)
# chart: win rate with CI, decks n>=30, sorted
t=T[T.games>=30].sort_values("winrate")
fig,ax=plt.subplots(figsize=(9,0.38*len(t)+1.5))
ax.hlines(range(len(t)),t.ci_lo,t.ci_hi,color="#9aa5b1",lw=3)
ax.scatter(t.winrate,range(len(t)),color="#1f6feb",zorder=3)
ax.axvline(.5,color="#e5484d",ls="--",lw=1); ax.set_yticks(range(len(t))); ax.set_yticklabels([f"{a} (n={b})" for a,b in zip(t.deck,t.games)])
ax.set_xlabel("Win rate per game (95% Wilson CI)"); ax.set_title("Win rate by deck list"); ax.spines[["top","right"]].set_visible(False)
plt.tight_layout(); plt.savefig(here/"deck_winrate.png",dpi=130)
# save best-candidate decklists
json.dump({v:{cn.get(i,str(i)):c for i,c in sorted(C.Counter(k).items())} for k,v in D.items()},open(here/"decklists.json","w"),ensure_ascii=False,indent=1)
