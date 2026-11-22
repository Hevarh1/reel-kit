"""Full-quality export of the approved cut, one file per clip, resumable (re-run until it prints ALLDONE).
   python3 export_clips.py source.mov cuts.json OUTDIR [--fps 30000/1001] [--vf "..."]
   Default --vf makes 1080x1920 limited-range video from a full-range phone clip; check yours with ffprobe.
   Afterwards:  ffmpeg -f concat -safe 0 -i OUTDIR/list.txt -c copy video_only.mp4   and mux the audio."""
import json,subprocess,os,argparse
from fractions import Fraction
ap=argparse.ArgumentParser(); [ap.add_argument(x) for x in ('src','cuts','outdir')]; ap.add_argument('--fps',default='30000/1001')
ap.add_argument('--vf',default='scale=1080:1920:flags=lanczos:in_range=pc:out_range=tv,format=yuv420p')
a=ap.parse_args(); FPS=float(Fraction(a.fps)); F=json.load(open(a.cuts)); os.makedirs(a.outdir,exist_ok=True)
for n,(s,e) in enumerate(F):
    out=os.path.join(a.outdir,f'c{n+1:02d}.mp4')
    if os.path.exists(out+'.done'): continue
    subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{s/FPS:.5f}','-i',a.src,'-an','-vf',a.vf,'-frames:v',str(e-s),'-c:v','libx264','-preset','slow','-crf','15','-g','30','-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-video_track_timescale','30000',out],check=True)
    open(out+'.done','w').write('ok'); print('done',n+1,flush=True)
open(os.path.join(a.outdir,'list.txt'),'w').write(''.join(f"file 'c{n+1:02d}.mp4'\n" for n in range(len(F)))); print('ALLDONE')
