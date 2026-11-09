import json, re, sys, glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
root=Path(__file__).resolve().parents[2]/"pokemon"
HEAD=4_000_000
DECK=re.compile(r'"action": \[\[([\d, ]+)\], \[([\d, ]+)\]\]')
NAME=re.compile('\{"id": (\d+), "name": "([^"]*)"')
def one(p):
    ep=int(Path(p).stem)
    try:
        s=open(p,"rb").read(HEAD).decode("utf8","ignore")
        rw=json.loads(re.search(r'"rewards": (\[[^\]]*\])',s).group(1))
        bo=int(re.search(r'"bo": (\d+)',s).group(1))
        t=re.search(r'"TeamNames": (\[[^\]]*\])',s)
        names=json.loads(t.group(1)) if t else [None,None]
        i=s.index('"steps": [[')
        m=DECK.search(s,i)
        decks=[[int(x) for x in m.group(k).split(",")] for k in (1,2)]
        nm={int(a):b for a,b in NAME.findall(s,i)}
        return dict(ep=ep,bo=bo,rewards=rw,names=names,decks=decks,cardnames=nm)
    except Exception as e:
        return dict(ep=ep,err=repr(e))
if __name__=="__main__":
    fs=sorted(glob.glob(str(root/"*.json")))
    if len(sys.argv)>1: fs=fs[:int(sys.argv[1])]
    with ProcessPoolExecutor(6) as ex: res=list(ex.map(one,fs,chunksize=8))
    json.dump(res,open(Path(__file__).parent/"episodes.json","w"))
    bad=[r for r in res if 'err' in r]
    print(len(res),"errors",len(bad),bad[:3])
    ok=[r for r in res if 'err' not in r]
    print(ok[0]['rewards'],ok[0]['names'],[len(x) for x in ok[0]['decks']],len(ok[0]['cardnames']))
