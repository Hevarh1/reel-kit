"""Render the scene page to two video files: colour (straight alpha) and alpha-as-gray.
   python3 render.py <first_frame> <last_frame_exclusive> <tag> [--fps 30000/1001] [--dur seconds]
   Output: work/<tag>_rgb.mp4 and work/<tag>_a.mp4. Run several frame ranges in parallel for long videos."""
import sys,subprocess,os,time,argparse,cv2,numpy as np
from fractions import Fraction
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser(); ap.add_argument('f0',type=int); ap.add_argument('f1',type=int); ap.add_argument('tag')
ap.add_argument('--fps',default='30000/1001'); ap.add_argument('--dur',type=float,default=None,help='timeline length for the warm-up pass (default: end of this range)')
a=ap.parse_args(); FPS=float(Fraction(a.fps)); W,H=1080,1920
HERE=os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(HERE,'work'),exist_ok=True)
def enc(name,pix):
    return subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt',pix,'-s',f'{W}x{H}','-r',a.fps,'-i','-','-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-preset','veryfast','-crf','15','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-g','30',name],stdin=subprocess.PIPE)
with sync_playwright() as p:
    kw=dict(args=['--no-sandbox','--allow-file-access-from-files'])
    if os.environ.get('CHROME'): kw['executable_path']=os.environ['CHROME']
    elif os.path.exists('/usr/bin/google-chrome'): kw['executable_path']='/usr/bin/google-chrome'
    b=p.chromium.launch(**kw)
    pg=b.new_page(viewport={'width':W,'height':H}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.join(HERE,'scene.html')); pg.wait_for_timeout(1500)
    if errs: sys.exit('page errors: '+repr(errs))
    # warm-up: show every element once so all font subsets and images are loaded before capture
    dur=a.dur or a.f1/FPS+1
    for _ in range(2):
        k=0.0
        while k<dur: pg.evaluate(f"renderAt({k})"); k+=0.2
        pg.evaluate("Promise.all([document.fonts.ready].concat(Array.from(document.images).map(i=>i.decode().catch(()=>0))))"); pg.wait_for_timeout(1000)
    print('fonts loaded:',pg.evaluate("Array.from(document.fonts).filter(f=>f.status==='loaded').length"),flush=True)
    rgb=os.path.join(HERE,'work',a.tag+'_rgb'); al=os.path.join(HERE,'work',a.tag+'_a')
    pr=enc(rgb+'.tmp.mp4','bgr24'); pa=enc(al+'.tmp.mp4','gray')
    zrgb=np.zeros((H,W,3),np.uint8).tobytes(); za=np.zeros((H,W),np.uint8).tobytes(); t0=time.time()
    for n in range(a.f0,a.f1):
        if pg.evaluate(f"renderAt({n/FPS})"):
            im=cv2.imdecode(np.frombuffer(pg.screenshot(type='png',omit_background=True),np.uint8),cv2.IMREAD_UNCHANGED)
            if im.shape[2]==3: im=np.dstack([im,np.full(im.shape[:2],255,np.uint8)])
            pr.stdin.write(np.ascontiguousarray(im[:,:,:3]).tobytes()); pa.stdin.write(np.ascontiguousarray(im[:,:,3]).tobytes())
        else: pr.stdin.write(zrgb); pa.stdin.write(za)
        if n%200==0: print(a.tag,n,round(time.time()-t0),'s',flush=True)
    pr.stdin.close(); pa.stdin.close(); pr.wait(); pa.wait()
    os.rename(rgb+'.tmp.mp4',rgb+'.mp4'); os.rename(al+'.tmp.mp4',al+'.mp4'); b.close()
print('DONE',a.tag,flush=True)
