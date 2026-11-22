"""Synthesized, royalty-free sound effects from an event list. Needs numpy + scipy.
   python3 sfx.py events.json out.wav <duration_seconds>
   events.json: [[kind, time, {options}], ...]  (graphics/shot.py writes work/sfx_events.json)
   kinds: whoosh, whoosh_dn, pop, tick, impact, ding, err, drone{d}, keys{end}, data{end}; option g = gain in dB, pan = -1..1
   Keep it quiet: whooshes around -22..-25 dB, ticks -27..-31, at most one impact."""
import numpy as np, json, sys
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
SR=48000
rng=np.random.default_rng(3)
def env_exp(n,tau): return np.exp(-np.arange(n)/(tau*SR))
def bp(x,lo,hi): return sosfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),x)
def lp(x,f): return sosfilt(butter(2,f,btype='low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,btype='high',fs=SR,output='sos'),x)
def whoosh(d=.45,f0=400,f1=3000,peak=.6):
    n=int(d*SR); x=rng.standard_normal(n); out=np.zeros(n); nb=24
    for i in range(nb):  # sweep by crossfading bands
        a=i/nb; fc=f0*(f1/f0)**a; band=bp(x,fc*.7,min(fc*1.4,20000))
        w=np.exp(-((np.arange(n)/n-a)/(1.5/nb))**2); out+=band*w
    e=np.exp(-((np.arange(n)/n-peak)/.28)**2); out*=e
    return out/np.abs(out).max()
def pop(f=620,d=.09):
    n=int(d*SR); t=np.arange(n)/SR; fr=f*np.exp(-t*14); ph=2*np.pi*np.cumsum(fr)/SR
    y=np.sin(ph)*env_exp(n,.022); y[:48]*=np.linspace(0,1,48); return y
def tick(f=2400,d=.03):
    n=int(d*SR); t=np.arange(n)/SR; y=np.sin(2*np.pi*f*t)*env_exp(n,.005)+.4*hp(rng.standard_normal(n),5000)*env_exp(n,.002); return y/np.abs(y).max()
def impact(d=.6):
    n=int(d*SR); t=np.arange(n)/SR; fr=38+50*np.exp(-t*18); y=np.sin(2*np.pi*np.cumsum(fr)/SR)*env_exp(n,.13)
    nz=lp(rng.standard_normal(n),900)*env_exp(n,.03); y=y+.35*nz/np.abs(nz).max(); y[:96]*=np.linspace(0,1,96); return y/np.abs(y).max()
def ding(f=1318.5,d=.9):
    n=int(d*SR); t=np.arange(n)/SR; y=sum(a*np.sin(2*np.pi*f*m*t)*env_exp(n,tau) for m,a,tau in [(1,1,.22),(1.5,.5,.16),(2,.25,.1)]); y[:96]*=np.linspace(0,1,96); return y/np.abs(y).max()
def err(d=.22):
    n=int(d*SR); t=np.arange(n)/SR; f=np.where(t<d/2,233,185); y=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)); y=lp(y,1400)*np.minimum(1,np.minimum(t/.01,(d-t)/.03)); return y/np.abs(y).max()
def drone(d):
    n=int(d*SR); t=np.arange(n)/SR; y=np.sin(2*np.pi*49*t)+.6*np.sin(2*np.pi*73.5*t+1)+.25*lp(rng.standard_normal(n),180)
    e=np.minimum(1,t/1.5)*np.minimum(1,(d-t)/.6); return y*e/np.abs(y).max()
def db(x): return 10**(x/20)
def build(events,dur):
    L=np.zeros(int(dur*SR)+SR); R=L.copy()
    def put(t,y,g,pan=0):
        i=int(t*SR); j=min(len(L),i+len(y)); y=y[:j-i]*db(g); L[i:j]+=y*(1-max(0,pan)*.6); R[i:j]+=y*(1+min(0,pan)*.6)
    for ev in events:
        k,t=ev[0],ev[1]; a=ev[2] if len(ev)>2 else {}
        if k=='whoosh': put(t-.2,whoosh(a.get('d',.45),a.get('f0',350),a.get('f1',2600)),a.get('g',-22),a.get('pan',0))
        elif k=='whoosh_dn': put(t-.15,whoosh(a.get('d',.4),2600,350),a.get('g',-23))
        elif k=='pop': put(t,pop(a.get('f',620)),a.get('g',-19),a.get('pan',0))
        elif k=='tick': put(t,tick(a.get('f',2400)),a.get('g',-27),a.get('pan',0))
        elif k=='impact': put(t,impact(),a.get('g',-13))
        elif k=='ding': put(t,ding(a.get('f',1318.5)),a.get('g',-22))
        elif k=='err': put(t,err(),a.get('g',-25))
        elif k=='drone': put(t,drone(a['d']),a.get('g',-24))
        elif k=='keys':
            tt=t
            while tt<a['end']: put(tt,tick(1500+rng.uniform(-300,500),.02),-31+rng.uniform(-2,2),rng.uniform(-.4,.4)); tt+=rng.uniform(.055,.11)
        elif k=='data':
            tt=t
            while tt<a['end']: p=(tt-t)/(a['end']-t); put(tt,tick(1800+1800*p,.015),-33+4*p,rng.uniform(-.8,.8)); tt+=.075-.045*p
    x=np.stack([L,R],1)[:int(dur*SR)]; x=np.tanh(x*1.2)/1.2
    return x
if __name__=='__main__':
    ev=json.load(open(sys.argv[1])); dur=float(sys.argv[3]); x=build(ev,dur)
    print('sfx peak dBFS',20*np.log10(np.abs(x).max()))
    wavfile.write(sys.argv[2],SR,(x*32767).astype(np.int16))
