"""Low-res preview of a cut with the clip number and source time burned in, plus the table to send for approval.
   python3 preview.py proxy.mp4 audio48k.wav cuts.json preview.mp4 [--fps 30000/1001]
   proxy.mp4: small copy of the source with identical frame timing, e.g.
     ffmpeg -i source.mov -an -vf scale=540:-2 -c:v libx264 -crf 28 -preset veryfast proxy.mp4"""
import json,subprocess,argparse,os
from fractions import Fraction
ap=argparse.ArgumentParser(); [ap.add_argument(x) for x in ('proxy','wav','cuts','out')]; ap.add_argument('--fps',default='30000/1001'); ap.add_argument('--font',default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
a=ap.parse_args(); FPS=float(Fraction(a.fps)); cl=json.load(open(a.cuts)); t=0; vp=[];apx=[];dts=[];rows=[]
for n,(fs,fe) in enumerate(cl):
    s,e=fs/FPS,fe/FPS; d=e-s
    vp.append(f"[0:v]trim=start_frame={fs}:end_frame={fe},setpts=PTS-STARTPTS[v{n}]")
    apx.append(f"[1:a]atrim={s:.4f}:{e:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={d-0.008:.4f}:d=0.008[a{n}]")
    lab=f"{n+1}  |  {int(s//60)}\\:{s%60:04.1f}"
    dts.append(f"drawtext=fontfile={a.font}:text='{lab}':x=10:y=10:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=5:enable='between(t,{t:.3f},{t+d-0.001:.3f})'")
    rows.append((n+1,s,e,t)); t+=d
n=len(cl); fc=';'.join(vp+apx)+';'+''.join(f'[v{i}]' for i in range(n))+f"concat=n={n}:v=1:a=0,"+','.join(dts)+"[vo];"+''.join(f'[a{i}]' for i in range(n))+f"concat=n={n}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[ao]"
open(a.out+'.fc.txt','w').write(fc)
r=subprocess.run(['ffmpeg','-y','-v','error','-i',a.proxy,'-i',a.wav,'-filter_complex_script',a.out+'.fc.txt','-map','[vo]','-map','[ao]','-c:v','libx264','-preset','veryfast','-crf','28','-c:a','aac','-b:a','96k','-movflags','+faststart',a.out])
os.remove(a.out+'.fc.txt'); print('rc',r.returncode,'duration %.1f s'%t)
for i,s,e,o in rows: print(f"clip {i:2d}: source {s:7.2f}-{e:7.2f}  ({e-s:5.2f}s)  at {o:6.1f}")
