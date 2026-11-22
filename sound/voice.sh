#!/bin/sh
# Voice polish for a phone-recorded talking head, then the final mix with the SFX track.
#   sh voice.sh clean_cut_audio.wav voice_pro.wav
#   sh voice.sh mix video_only.mp4 voice_pro.wav sfx.wav final.mp4 <duration_seconds>
set -e
if [ "$1" = mix ]; then
  ST=$(python3 -c "print(max(0,$6-0.3))")
  ffmpeg -y -v error -i "$2" -i "$3" -i "$4" -filter_complex \
   "[1:a]afade=t=out:st=$ST:d=0.25[v];[v][2:a]amix=inputs=2:duration=first,volume=2,alimiter=limit=0.89:level=disabled,aresample=48000[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -movflags +faststart "$5"
else
  ffmpeg -y -v error -i "$1" -af \
   "highpass=f=80,equalizer=f=250:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=1:g=2.5,highshelf=f=9000:g=2,deesser,acompressor=ratio=3,loudnorm=I=-14:TP=-1.5:LRA=7,alimiter=limit=0.89:level=disabled" \
   -ar 48000 -c:a pcm_s16le "$2"
fi
