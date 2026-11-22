"""Composite one part: speaker video (with sub-pixel zoom/shift from xform.json) + transparent graphics layer.
   python3 comp.py --video clean.mp4 --rgb g0_rgb.mp4 --alpha g0_a.mp4 --xform xform.json --f0 0 --f1 773 --out e0.mp4 [--fps 30000/1001]
   The layer files must start exactly at frame f0 (render the same frame ranges you composite).
   Works with ffmpeg 4.4+. Then: ffmpeg -f concat -safe 0 -i list.txt -c copy video.mp4

   Two things this script does on purpose:
   * layer files are plain inputs with NO -ss and NO concat demuxer: seeking a concat-demuxer input can drop
     about the first second of the overlay.
   * zoom uses the perspective filter with per-frame expressions (variable `on` = output frame number) and cubic
     interpolation. scale/crop/overlay with integer positions moves in whole pixels and shimmers on slow zooms."""
import subprocess,sys,json,argparse
from fractions import Fraction
ap=argparse.ArgumentParser()
for k in ('video','rgb','alpha','xform','out'): ap.add_argument('--'+k,required=True)
ap.add_argument('--f0',type=int,required=True); ap.add_argument('--f1',type=int,required=True); ap.add_argument('--fps',default='30000/1001')
ap.add_argument('--size',default='1080x1920'); ap.add_argument('--centre',default='525,600',help='zoom centre, must match graphics/shot.py')
ap.add_argument('--crf',default='17'); ap.add_argument('--preset',default='medium')
a=ap.parse_args(); FPS=float(Fraction(a.fps)); W,H=map(int,a.size.split('x')); CX,CY=map(float,a.centre.split(','))
S=a.f0/FPS; D=(a.f1-a.f0)/FPS; X=json.load(open(a.xform)); T=f'({S:.6f}+on/{FPS:.6f})'
def ex(i0,i1,base):
    parts=[]
    for seg in X:
        s,e=seg[0],seg[1]; v0,v1=seg[i0],seg[i1]
        if e<=S-0.1 or s>=S+D+0.1 or (v0==base and v1==base): continue
        p=f"(({T}-{s})/({e}-{s}))"; sm=f"({p}*{p}*(3-2*{p}))"
        parts.append(f"between({T},{s},{e}-0.0001)*({v0-base}+({v1-v0})*{sm})")
    return str(base)+''.join('+'+q for q in parts)
Z=ex(2,3,1); Y=ex(4,5,0)
x0=f"{CX}-{CX}/({Z})"; x1=f"{CX}+{W-CX}/({Z})"; y0=f"{CY}-({CY}+({Y}))/({Z})"; y2=f"{CY}+({H-CY}-({Y}))/({Z})"
fc=(f"[0:v]fps={a.fps},format=yuv420p,perspective=x0='{x0}':y0='{y0}':x1='{x1}':y1='{y0}':x2='{x0}':y2='{y2}':x3='{x1}':y3='{y2}':sense=source:eval=frame:interpolation=cubic[v1];"
    f"[2:v]fps={a.fps},format=gray[fa];[1:v]fps={a.fps}[fr];[fr][fa]alphamerge[f];[v1][f]overlay=shortest=1,format=yuv420p[vo]")
cmd=['ffmpeg','-y','-v','error','-stats','-ss',f'{S:.5f}','-t',f'{D+0.3:.5f}','-i',a.video,'-i',a.rgb,'-i',a.alpha,
 '-filter_complex',fc,'-map','[vo]','-an','-frames:v',str(a.f1-a.f0),'-c:v','libx264','-preset',a.preset,'-crf',a.crf,'-g','30','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-video_track_timescale','30000',a.out]
sys.exit(subprocess.run(cmd).returncode)
