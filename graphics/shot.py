"""Still-sheet checker: composite the graphics over the speaker video at given times.
   python3 shot.py sheet.jpg 1.0 4.2 7.5 ... [--video proxy.mp4] [--fps 30000/1001]
   Also writes work/xform.json (for compose/comp.py) and work/sfx_events.json (for sound/sfx.py).
   Without --video a grey background is used."""
import sys,os,json,argparse,cv2,numpy as np
from fractions import Fraction
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('times',type=float,nargs='*'); ap.add_argument('--video'); ap.add_argument('--fps',default='30000/1001')
a=ap.parse_args(); FPS=float(Fraction(a.fps)); HERE=os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(HERE,'work'),exist_ok=True)
CX,CY=525,600   # zoom centre, must match compose/comp.py
cap=cv2.VideoCapture(a.video) if a.video else None; tiles=[]
with sync_playwright() as p:
    kw=dict(args=['--no-sandbox','--allow-file-access-from-files'])
    if os.environ.get('CHROME'): kw['executable_path']=os.environ['CHROME']
    elif os.path.exists('/usr/bin/google-chrome'): kw['executable_path']='/usr/bin/google-chrome'
    b=p.chromium.launch(**kw)
    pg=b.new_page(viewport={'width':1080,'height':1920}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.join(HERE,'scene.html')); pg.wait_for_timeout(1500); pg.evaluate("document.fonts.ready")
    if errs: sys.exit('page errors: '+repr(errs))
    XF=pg.evaluate('XFORM'); json.dump(XF,open(os.path.join(HERE,'work/xform.json'),'w')); json.dump(pg.evaluate('SFXEV'),open(os.path.join(HERE,'work/sfx_events.json'),'w'))
    def xf(t):
        z=1.0;y=0.0
        for s,e,z0,z1,y0,y1 in XF:
            if s<=t<e: pp=(t-s)/(e-s); pp=pp*pp*(3-2*pp); z+=z0-1+(z1-z0)*pp; y+=y0+(y1-y0)*pp
        return z,y
    for t in a.times:
        pg.evaluate(f"renderAt({t})"); pg.wait_for_timeout(250)   # let lazy font subsets arrive
        fr=np.full((1920,1080,3),120,np.float32)
        if cap is not None:
            cap.set(1,int(round(t*FPS))); ok,f=cap.read()
            if ok: fr=cv2.resize(f,(1080,1920),interpolation=cv2.INTER_CUBIC).astype(np.float32)
        z,y=xf(t); M=np.float32([[z,0,CX-z*CX],[0,z,CY-z*CY+y]]); comp=cv2.warpAffine(fr,M,(1080,1920))
        if pg.evaluate(f"renderAt({t})"):
            im=cv2.imdecode(np.frombuffer(pg.screenshot(type='png',omit_background=True),np.uint8),cv2.IMREAD_UNCHANGED).astype(np.float32)
            if im.shape[2]==3: im=np.dstack([im,np.full(im.shape[:2],255,np.float32)])
            al=im[:,:,3:]/255; comp=comp*(1-al)+im[:,:,:3]*al
        c=cv2.resize(comp.astype(np.uint8),(378,672),interpolation=cv2.INTER_AREA); cv2.putText(c,f'{t:.2f}',(8,664),0,.7,(0,255,255),2); tiles.append(c)
    b.close()
if tiles: cv2.imwrite(a.out,np.hstack(tiles))
print('wrote',a.out,'+ work/xform.json, work/sfx_events.json')
