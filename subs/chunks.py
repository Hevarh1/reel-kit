"""Word-level transcript JSON -> subtitle chunks.
   python3 chunks.py transcript.json OUTDIR [--fixes fixes.json] [--sizes 2,3,3,1,...] [--max 3]
   Input : {"segments":[{"words":[{"text":..,"start_time":..,"end_time":..}, ...]}]}  (ElevenLabs Speech to Text export)
           or {"words":[{"text"|"word":..,"start"|"start_time":..,"end"|"end_time":..}]}
   Output: OUTDIR/words.js (CHUNKS, WORDS for the scene page) and OUTDIR/subs.txt (numbered lines to proof-read).
   --sizes  hand-picked words per chunk (best result); otherwise chunks break at punctuation, pauses and --max words."""
import json,sys,os,argparse
ap=argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--fixes'); ap.add_argument('--sizes'); ap.add_argument('--max',type=int,default=3)
a=ap.parse_args(); J=json.load(open(a.src,encoding='utf-8'))
raw=[w for s in J['segments'] for w in s['words']] if 'segments' in J else J['words']
g=lambda w,*ks: next(w[k] for k in ks if k in w)
W=[dict(w=g(w,'text','word').strip(),t0=float(g(w,'start_time','start')),t1=float(g(w,'end_time','end'))) for w in raw if g(w,'text','word').strip()]
F=json.load(open(a.fixes,encoding='utf-8')) if a.fixes else {}
PUNCT='،؛؟!.,;:?…'
def is_latin(s): return any(ord(c)<0x250 and c.isalpha() for c in s)
MIXED=sum(is_latin(w['w']) for w in W)<len(W)/2      # Latin words are the minority: loanwords inside e.g. Sorani text
for i,w in enumerate(W):
    t=w['w']
    for k,v in F.get('chars',{}).items(): t=t.replace(k,v)
    core=t.rstrip(PUNCT); tail=t[len(core):]
    core=F.get('words',{}).get(core,core)
    w['brk']=bool(tail)
    if MIXED and is_latin(core): tail=''            # no commas / full stops stuck to Latin loanwords in RTL text
    w['w']=core+tail
for first,nxt,rep in F.get('before',[]):               # context fix: replace `first` when the next word starts with `nxt`
    for i in range(len(W)-1):
        if W[i]['w']==first and W[i+1]['w'].startswith(nxt): W[i]['w']=rep
HL=F.get('highlight',[]); HERO=F.get('hero',[])
if a.sizes:
    sizes=[int(x) for x in a.sizes.split(',')]; assert sum(sizes)==len(W),f'sizes sum {sum(sizes)} != {len(W)} words'
else:
    sizes=[];n=0
    for i,w in enumerate(W):
        n+=1; gap=W[i+1]['t0']-w['t1'] if i+1<len(W) else 9
        if n>=a.max or w['brk'] or gap>0.35: sizes.append(n); n=0
    if n: sizes.append(n)
chunks=[];i=0
for s in sizes:
    seg=W[i:i+s]; i+=s; tx=' '.join(x['w'] for x in seg)
    chunks.append(dict(words=[dict(w=x['w'],t0=x['t0'],hl=1 if any(k in x['w'] for k in HL) else 0) for x in seg],t0=seg[0]['t0'],last=seg[-1]['t1'],hero=1 if any(k in tx for k in HERO) else 0))
for c,n in zip(chunks,chunks[1:]): c['end']=min(n['t0']-0.06,c['last']+0.45)
chunks[-1]['end']=chunks[-1]['last']+0.25
os.makedirs(a.out,exist_ok=True)
open(os.path.join(a.out,'words.js'),'w',encoding='utf-8').write('const CHUNKS='+json.dumps(chunks,ensure_ascii=False)+';\nconst WORDS='+json.dumps([dict(w=x['w'],t0=x['t0'],t1=x['t1']) for x in W],ensure_ascii=False)+';')
L=[f"{k:03d} | {int(c['t0']//60)}:{c['t0']%60:04.1f} | "+' '.join(w['w'] for w in c['words']) for k,c in enumerate(chunks,1)]
open(os.path.join(a.out,'subs.txt'),'w',encoding='utf-8').write('\n'.join(L)+'\n'); print('\n'.join(L)); print(len(W),'words ->',len(chunks),'chunks')
