"""Find repeated takes without a transcript: MFCC features + subsequence DTW.
   python3 repeats.py audio16k.wav segments.json [--win 0.8] [--cost 0.36]
   segments.json: [[start,end], ...] speech stretches in seconds (from segments.py).
   For every 0.8 s window of speech it reports other stretches that contain nearly the same sound.
   A stretch whose opening matches the opening of a later stretch is usually an abandoned take: keep the later one.
   Needs numpy + scipy. Treat matches as hints and check them by ear or against the frames."""
import numpy as np,json,argparse
from scipy.io import wavfile
from scipy.fftpack import dct
ap=argparse.ArgumentParser(); ap.add_argument('wav'); ap.add_argument('segs'); ap.add_argument('--win',type=float,default=.8); ap.add_argument('--cost',type=float,default=.36)
a=ap.parse_args(); sr,x=wavfile.read(a.wav); assert sr==16000 and x.ndim==1,'need 16 kHz mono wav'
x=x.astype(np.float32)/32768; x=np.append(x[0],x[1:]-0.97*x[:-1]); N=400;H=160;nf=1+(len(x)-N)//H
fr=x[np.arange(N)[None,:]+H*np.arange(nf)[:,None]]*np.hamming(N); P=np.abs(np.fft.rfft(fr,512))**2
mel=lambda f:2595*np.log10(1+f/700); imel=lambda m:700*(10**(m/2595)-1)
nm=26; bins=np.floor(513*imel(np.linspace(mel(100),mel(7000),nm+2))/16000).astype(int); fb=np.zeros((nm,257))
for m in range(1,nm+1):
    p,q,r=bins[m-1],bins[m],bins[m+1]; fb[m-1,p:q]=(np.arange(p,q)-p)/max(1,q-p); fb[m-1,q:r]=(r-np.arange(q,r))/max(1,r-q)
M=dct(np.log(P@fb.T+1e-10),type=2,axis=1,norm='ortho')[:,1:13]
S=[tuple(s) for s in json.load(open(a.segs))]; speech=np.zeros(len(M),bool)
for s,e in S: speech[int(s*100):int(e*100)]=True
Z0=(M-M[speech].mean(0))/M[speech].std(0); Z=np.hstack([Z0,0.6*np.gradient(Z0,axis=0)]); Z/=np.linalg.norm(Z,axis=1,keepdims=True)+1e-9
def sdtw(q,r):
    C=1-q@r.T; n,m=C.shape; INF=1e9; D=np.full((n,m),INF); D[0]=C[0]
    for i in range(1,n):
        u=np.full(m,INF); u[1:]=D[i-1,:-1]; v=np.full(m,INF); v[2:]=D[i-1,:-2]; w=np.full(m,INF)
        if i>=2: w[1:]=D[i-2,:-1]+C[i-1,1:]
        D[i]=C[i]+np.minimum(np.minimum(u,v),w)
    j=int(np.argmin(D[n-1])); return D[n-1,j]/n,j
QL=int(a.win*100)
def sid(t): return next((k+1 for k,(s,e) in enumerate(S) if s-0.05<=t<=e+0.05),0)
print('window start | own stretch | matches as  stretch:cost@time')
for qs in range(0,len(M)-QL,10):
    if speech[qs:qs+QL].mean()<0.85: continue
    hits=[]
    for k,(s,e) in enumerate(S):
        r0,r1=int(s*100),int(e*100)
        if r1-r0<QL*0.6 or not (r1<qs-30 or r0>qs+QL+30): continue
        c,j=sdtw(Z[qs:qs+QL],Z[r0:r1])
        if c<a.cost: hits.append((c,k+1,(r0+j)/100-a.win))
    if hits: print(f"{qs/100:7.2f} S{sid(qs/100+a.win/2):02d} | "+'  '.join(f"S{k:02d}:{c:.2f}@{t:.1f}" for c,k,t in sorted(hits)))
