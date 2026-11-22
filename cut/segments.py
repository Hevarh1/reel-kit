"""List speech stretches from env.json.
   python3 segments.py env.json [threshold_db=-48] [min_gap_s=0.25] [from-to ...]
   Prints start, end, duration, peak for every stretch louder than the threshold. Optional ranges (seconds) zoom in."""
import json,sys
db=json.load(open(sys.argv[1])); th=float(sys.argv[2]) if len(sys.argv)>2 else -48; gap=float(sys.argv[3]) if len(sys.argv)>3 else 0.25
rngs=[tuple(int(float(x)*100) for x in r.split('-')) for r in sys.argv[4:]] or [(0,len(db))]
for a,b in rngs:
    on=None; k=0
    def out():
        global k; k+=1; print(f"{k:3d}  {on/100:7.2f} {(last+1)/100:7.2f}  dur {(last+1-on)/100:5.2f}  peak {max(db[on:last+1]):6.1f}")
    for i in range(a,min(b,len(db))):
        if db[i]>th:
            if on is None: on=i
            last=i
        elif on is not None and i-last>gap*100: out(); on=None
    if on is not None: out()
