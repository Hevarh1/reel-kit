"""Cut the audio with the same frame cuts (8 ms fades at each joint so joins never click).
   python3 cut_audio.py audio48k.wav cuts.json out.wav [--fps 30000/1001] [--filter "loudnorm=I=-16:TP=-1.5:LRA=11"]"""
import json,subprocess,argparse
from fractions import Fraction
ap=argparse.ArgumentParser(); [ap.add_argument(x) for x in ('wav','cuts','out')]; ap.add_argument('--fps',default='30000/1001'); ap.add_argument('--filter',default='anull')
a=ap.parse_args(); FPS=float(Fraction(a.fps)); parts=[];labs=''
C=json.load(open(a.cuts))
for n,(x,y) in enumerate(C):
    s,e=x/FPS,y/FPS; d=e-s
    parts.append(f"[0:a]atrim={s:.4f}:{e:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={d-0.008:.4f}:d=0.008[a{n}]"); labs+=f'[a{n}]'
fc=';'.join(parts)+f';{labs}concat=n={len(C)}:v=0:a=1,{a.filter}[o]'
subprocess.run(['ffmpeg','-y','-v','error','-i',a.wav,'-filter_complex',fc,'-map','[o]','-c:a','pcm_s16le',a.out],check=True)
