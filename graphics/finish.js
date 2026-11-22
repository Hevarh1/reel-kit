// captions (from work/words.js built by subs/chunks.py) + data for the compositor + the driver
CHUNKS.forEach((c,ci)=>{
  if(ci===0){ c.words[0].t0=-1; c.t0=-1; }   // first words are on screen from the very first frame (cover frame)
  const html=c.words.map(w=>`<span>${w.w}</span>`).join('');
  add(html,'',(t,e)=>{
    if(t<c.t0-.06||t>c.end||CAPHIDE.some(([a,b])=>c.t0>=a&&c.t0<b)) return false;
    const onl=halfK(t)>.5; e.classList.toggle('onlight',onl&&!TH.darkPanel); e.classList.toggle('onpanel',onl); e.style.top=capY(t)+'px';
    e.style.fontSize=onl?(c.hero?'82px':'68px'):''; e.style.left=onl?'30px':''; e.style.width=onl?'1020px':'';
    // fade out while the split panel is moving so the caption never travels across the face
    const hk=halfK(t), mv=clamp(Math.abs(hk-.5)*3.2-.55); const q=clamp((t-(c.end-.1))/.1); e.style.opacity=(1-q)*mv; e.style.transform=`translateY(-50%) translateY(${-q*10}px)`;
    const sp=e.children;
    c.words.forEach((w,i)=>{const a=w.t0-.07, p=tw(t,a,.34,E.expo); sp[i].style.opacity=clamp((t-a)/.14); sp[i].style.transform=`translateY(${(1-p)*24}px)`; 
      if(w.hl){ const s=sp[i].style;
        if(TH.capHL==='box'){ s.background=ACC2; s.color=INK; s.textShadow='none'; s.padding='0 18px'; s.borderRadius='14px'; s.transform+=' rotate(-2deg)'; }
        else { const col=(onl&&!TH.darkPanel)?ACC:ACC2; s.color=col; if(TH.capHL==='glow') s.textShadow=`0 0 22px ${col}aa,0 0 50px ${col}66,0 3px 8px rgba(0,0,0,.55)`; } }});
  },'cap'+(c.hero?' hero':''));
});
// XFORM rows: [start, end, zoomFrom, zoomTo, shiftYFrom, shiftYTo] for the speaker video
window.XFORM=(()=>{const X=ZOOMS.map(([a,b,z0,z1])=>[a,b,z0,z1,0,0]);
  for(const p of HALF){X.push([p.a,p.a+.5,1,1,0,SHIFT],[p.a+.5,p.b-.5,1,1,SHIFT,SHIFT],[p.b-.5,p.b,1,1,SHIFT,0]);} return X.sort((a,b)=>a[0]-b[0]);})();
window.SFXEV=SFX;
window.renderAt=(t)=>{ let any=false;
  for(const it of items){ if(it.disp===undefined) it.disp=it.e.style.display; const r=it.fn(t,it.e); if(r===false){it.e.style.display='none'} else {it.e.style.display=it.disp;any=true} }
  return any; };
