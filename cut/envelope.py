"""Loudness envelope of a 16-bit mono WAV in 10 ms steps (dB). Pure standard library.
   ffmpeg -i video.mov -vn -ac 1 -ar 16000 -c:a pcm_s16le a.wav
   python3 envelope.py a.wav env.json"""
import wave,math,array,json,sys
w=wave.open(sys.argv[1]); assert w.getsampwidth()==2 and w.getnchannels()==1,'need 16-bit mono wav'
sr=w.getframerate(); a=array.array('h'); a.frombytes(w.readframes(w.getnframes())); hop=int(sr*0.01); db=[]
for i in range(0,len(a)-hop,hop):
    s=0
    for v in a[i:i+hop]: s+=v*v
    db.append(round(20*math.log10(max(math.sqrt(s/hop),1)/32768),2))
json.dump(db,open(sys.argv[2],'w')); sd=sorted(db); n=len(db)
print('10ms frames',n,'| p5',sd[n//20],'p25',sd[n//4],'p50',sd[n//2],'p90',sd[n*9//10],'max',sd[-1])
