"""Rough keep-ranges (seconds) -> exact frame cuts that never clip a word ending.
   python3 bounds.py env.json clips.json cuts.json [--fps 30000/1001] [--pre 0.12] [--post 0.22] [--floor -72] [--loud -48]
   clips.json: [[start,end], ...] rough times of the speech you keep, in source seconds.
               An item may be {"s":..,"e":..,"hard_start":t,"hard_end":t} to force an exact edge
               (needed when two takes sit closer together than the pads).
   Rule: the sound ends where the level stays below --floor for 100 ms; the cut is onset-pre .. soundend+post,
   snapped outward to whole frames. Speakers who let sentence endings trail off need this."""
import json,argparse,math
from fractions import Fraction
ap=argparse.ArgumentParser(); ap.add_argument('env'); ap.add_argument('clips'); ap.add_argument('out')
ap.add_argument('--fps',default='30000/1001'); ap.add_argument('--pre',type=float,default=.12); ap.add_argument('--post',type=float,default=.22); ap.add_argument('--floor',type=float,default=-72); ap.add_argument('--loud',type=float,default=-48)
a=ap.parse_args(); FPS=float(Fraction(a.fps)); db=json.load(open(a.env)); N=len(db); out=[]
def onset(s):
    i=min(N-1,int(round(s*100)))
    while i<N-1 and db[i]<a.loud: i+=1
    j=i
    while j>5 and not all(v<a.floor for v in db[j-5:j]): j-=1
    return j/100
def soundend(e):
    k=min(N-1,int(round(e*100)))
    while k>0 and db[k]<a.loud: k-=1
    m=k
    while m+11<N and not all(v<a.floor for v in db[m+1:m+11]): m+=1
    return (m+1)/100
for n,c in enumerate(json.load(open(a.clips)),1):
    if isinstance(c,dict): s,e,hs,he=c['s'],c['e'],c.get('hard_start'),c.get('hard_end')
    else: (s,e),hs,he=c,None,None
    on,off=onset(s),soundend(e); S=hs if hs is not None else max(0,on-a.pre); En=he if he is not None else min(N/100,off+a.post)
    fs=int(S*FPS); fe=math.ceil(En*FPS); out.append([fs,fe])
    print(f"{n:2d} onset {on:7.2f} soundend {off:7.2f} | cut {fs/FPS:8.3f}-{fe/FPS:8.3f}  frames {fs}-{fe}  dur {(fe-fs)/FPS:6.2f}")
json.dump(out,open(a.out,'w')); print('total %.2f s'%(sum(b-x for x,b in out)/FPS))
