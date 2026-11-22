// Deterministic scene library: every element's style is a pure function of time t.
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const E={lin:x=>x,out:x=>1-Math.pow(1-x,3),out5:x=>1-Math.pow(1-x,5),inn:x=>x*x*x,sm:x=>x*x*(3-2*x),
  expo:x=>x>=1?1:1-Math.pow(2,-10*x), io:x=>x<.5?16*x*x*x*x*x:1-Math.pow(-2*x+2,5)/2};
const tw=(t,t0,d,e=E.out)=>e(clamp((t-t0)/d));
const lerp=(a,b,p)=>a+(b-a)*p;
const within=(t,a,b)=>t>=a&&t<b;
const items=[];
// add(html, css, fn(t,el), className, parent): fn returns false when the element is hidden at time t
function add(html,css,fn,cls,parent){const e=document.createElement('div');e.className='abs '+(cls||'');e.innerHTML=html;if(css)e.style.cssText=css;(parent||document.getElementById('front')).appendChild(e);items.push({e,fn});return e}
let _s=11;const rnd=()=>{_s=(_s*16807)%2147483647;return _s/2147483647};   // seeded: never use Math.random
const DIR=TEXT.dir==='ltr'?'ltr':'rtl', LTR=DIR==='ltr';
document.documentElement.style.setProperty('--dir',DIR); document.documentElement.style.setProperty('--font',TEXT.font);
// ---------------- designs ----------------
// flow : soft paper panels, drawn lines, text straight on the wall (no boxes)
// night: dark panels, neon accents with glow, notes on dark cards
// punch: white panels, heavy type, highlighter box behind key subtitle words
const THEMES={
 flow :{palette:{accent:'#1F8A8A',accent2:'#6FD6CF',ink:'#2B2C30',paper:'#F8F3EC'}, panelBg:p=>`linear-gradient(180deg,#fff,${p.paper})`, darkPanel:false, cards:false, glow:false, capHL:'color', takeBg:'linear-gradient(160deg,#26272B,#141416)'},
 night:{palette:{accent:'#C8FF2E',accent2:'#3FE0FF',ink:'#070A16',paper:'#0A0F24'}, panelBg:p=>`linear-gradient(180deg,${p.paper},${p.ink})`, darkPanel:true, cards:true, glow:true, capHL:'glow', takeBg:'linear-gradient(160deg,#0A0F24,#070A16)'},
 punch:{palette:{accent:'#FF4A1C',accent2:'#FFD21F',ink:'#111111',paper:'#FFFFFF'}, panelBg:p=>p.paper, darkPanel:false, cards:false, glow:false, capHL:'box', takeBg:'#111111'}};
const TH=THEMES[typeof THEME==='string'&&THEMES[THEME]?THEME:'flow'], PAL=Object.assign({},TH.palette,(typeof PALETTE==='object'&&PALETTE)||{});
const ACC=PAL.accent, ACC2=PAL.accent2, INK=PAL.ink, PAPER=PAL.paper;
const PINK=TH.darkPanel?'#fff':INK;                     // text colour inside panels
const PHALO=TH.darkPanel?PAL.ink:PAPER;                 // halo behind panel labels
const WINK=TH.cards?'#fff':INK;                         // text colour of notes/words on the wall
const WHALO=TH.cards?'none':'0 0 22px rgba(255,255,255,.95),0 0 8px rgba(255,255,255,.9)';
const CARD=TH.cards?`background:rgba(7,10,22,.82);border-radius:26px;padding:18px 14px 16px;box-shadow:0 0 0 2px ${ACC}55,0 12px 40px rgba(0,0,0,.45);`:'';
const GLOW=c=>TH.glow?`text-shadow:0 0 18px ${c}99,0 0 42px ${c}55;`:'';
// presence: smooth rise in, drift out. returns [opacity, y]
const pres=(t,a,b,din=.55,dout=.35,dy=44)=>{const p=tw(t,a,din,E.expo), q=tw(t,b-dout,dout,E.inn); return [clamp((t-a)/(din*.5))*(1-q),(1-p)*dy-q*dy*.7]};
// draw-on for svg strokes
function draw(svg,p){ svg.querySelectorAll('path,circle,line,rect,ellipse,polyline').forEach(s=>{ if(!s.dataset.d){s.dataset.d=1; s.setAttribute('pathLength','1'); s.style.strokeDasharray='1';} s.style.strokeDashoffset=1-clamp(p); }); }

const PANEL_H=866, SHIFT=612;
const SFX=[]; const sfx=(k,t,o)=>SFX.push(o?[k,+t.toFixed(2),o]:[k,+t.toFixed(2)]);
const CAPDOWN=[], CAPHIDE=[];
HALF.forEach(p=>{sfx('whoosh',p.a+.22,{g:-23,d:.6,f0:250,f1:1800}); sfx('whoosh_dn',p.b-.22,{g:-25,d:.5});});
function halfK(t){ for(const p of HALF) if(t>=p.a&&t<p.b) return tw(t,p.a,.5,E.sm)*(1-tw(t,p.b-.5,.5,E.sm)); return 0; }
const tkIn=(t,k)=>tw(t,k.a,.55,E.io), tkOut=(t,k)=>tw(t,k.b-.5,.5,E.io);
const inTK=t=>TK.some(k=>t>=k.a+.3&&t<k.b-.25), inHalf=t=>halfK(t)>0.01||TK.some(k=>t>=k.a&&t<k.b);
function capY(t){
  if(inTK(t)) return CAP_Y.takeover;
  if(CAPDOWN.some(([a,b])=>t>=a-.05&&t<b)) return CAP_Y.low;
  return lerp(CAP_Y.normal,CAP_Y.split,halfK(t));
}
const wave=(h,t,amp=12)=>{let p='0px 0px,1080px 0px'; for(let x=1080;x>=0;x-=60) p+=`,${x}px ${(h+amp*Math.sin(x*.0105+t*2.1)+amp*.5*Math.sin(x*.021-t*1.3)).toFixed(1)}px`; return `polygon(${p})`};

// soft light dips on jump cuts
CUTS.forEach(c=>add('','left:0;top:0;width:1080px;height:1920px;background:#fff',(t,e)=>{
  if(!within(t,c-.1,c+.28)) return false; e.style.opacity=.42*(t<c?tw(t,c-.1,.1,E.lin):1-tw(t,c,.28,E.out));}));

// split-screen panel: paper sheet with a slowly waving bottom edge. Put content in it with sub(...)
// The inner stage is 1080x760 scaled to 76%, which keeps content inside Instagram's safe area.
const _shadow=add('', 'left:0;top:0;width:1080px;height:1100px;background:rgba(0,0,0,.22);filter:blur(14px)',(t,e)=>{const k=halfK(t); if(k<=0.002) return false; e.style.clipPath=wave(PANEL_H*k+10,t,12*k);});
const panel=add(`<div style="position:absolute;left:0;top:0;width:1080px;height:1100px;background:${TH.panelBg(PAL)}"></div>
  <div id="pc" style="position:absolute;left:129.6px;top:185px;width:1080px;height:760px;transform:scale(.76);transform-origin:0 0"></div>`,
 'left:0;top:0;width:1080px;height:1100px',(t,e)=>{const k=halfK(t); if(k<=0.002) return false; e.style.clipPath=wave(PANEL_H*k,t,12*k);});
const pc=panel.querySelector('#pc');
const sub=(html,css,fn,cls)=>add(html,css,fn,cls,pc);
// content block inside the panel that slides in at a and out at b; inner(t,el) animates its children
function slide(html,css,a,b,inner){ return sub(html,css,(t,e)=>{ if(!within(t,a,b)) return false; const p=tw(t,a,.6,E.expo), q=tw(t,b-.4,.4,E.inn);
  e.style.opacity=clamp((t-a)/.25)*(1-q); e.style.transform=`translateY(${(1-p)*60-q*50}px)`; e.style.filter=`blur(${(1-tw(t,a,.4))*6+q*5}px)`; if(inner) inner(t,e); }); }

// full-screen takeovers: a dark sheet wipes up with a wave edge. Content goes in TKC[i].
const TKC=TK.map(K=>{ sfx('whoosh',K.a+.2,{g:-20,d:.8,f0:200,f1:2400}); sfx('whoosh_dn',K.b-.35,{g:-23,d:.6});
  const tk=add(`<div style="position:absolute;inset:0;background:${TH.takeBg}"></div><div class="tkc" style="position:absolute;inset:0"></div>`,'left:0;top:0;width:1080px;height:1920px',(t,e)=>{
   if(!within(t,K.a,K.b)) return false; const yT=lerp(2010,-90,tkIn(t,K)), yB=lerp(2010,-90,tkOut(t,K));
   let p=''; for(let x=0;x<=1080;x+=60) p+=`${x}px ${(yT+34*Math.sin(x*.008+t*3)).toFixed(1)}px,`; for(let x=1080;x>=0;x-=60) p+=`${x}px ${(yB+34*Math.sin(x*.008+t*3+1)).toFixed(1)}px,`;
   e.style.clipPath=`polygon(${p.slice(0,-1)})`;});
  return tk.querySelector('.tkc'); });

// ---------------- components ----------------
// flowing ribbon across the frame at height y
function ribbon(y,a,b,o={}){ const amp=o.amp||40, w=o.w||10, c=o.c||ACC, len=o.len||.45, sp=o.sp||1.6;
  return add(`<svg class="ln" viewBox="0 0 1080 300" style="width:1080px;height:300px;overflow:visible"><path stroke="${c}" stroke-width="${w}" pathLength="1" stroke-dasharray="${len} 3"/></svg>`,`left:0;top:${y-150}px`,(t,e)=>{
    if(!within(t,a,b)) return false; let d=''; for(let x=1120;x>=-40;x-=40){const yy=150+amp*Math.sin(x*.006+t*1.1+y)+amp*.4*Math.sin(x*.013-t*.9); d+=(x===1120?'M':'L')+x+' '+yy.toFixed(1);}
    const pth=e.querySelector('path'); pth.setAttribute('d',d); const k=((t-a)*sp)%1;
    pth.style.strokeDashoffset=len-k*(1+len); e.style.opacity=(o.op||.9)*Math.min(1,(t-a)/.15,(b-t)/.25);}); }
// line icons (24x24 viewBox stroke paths). Add your own.
const ICON={
 brief:'<rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M9 7V5a2 2 0 012-2h2a2 2 0 012 2v2M3 13h18"/>',
 cap:'<path d="M2 9l10-5 10 5-10 5L2 9z"/><path d="M6 11.5V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.5M22 9v6"/>',
 home:'<path d="M3 11l9-8 9 8M5 9.5V20h5v-6h4v6h5V9.5"/>'};
// small note beside the speaker's head: {side:'L'|'R', y, a, b, label, icon?, num?, fs?, tintAt?}
function note(o){ const cx=o.side==='R'?925:155, y=o.y; sfx('tick',o.a+.05,{f:1500+rnd()*500,g:-29,pan:o.side==='R'?.5:-.5});
  add(`${o.num?`<div class="ku" style="font-weight:900;font-size:150px;line-height:1;color:${ACC}">${o.num}</div>`:''}
   ${o.icon?`<svg class="ln ic" viewBox="0 0 24 24" style="width:104px;height:104px;stroke:${WINK};stroke-width:1.5">${ICON[o.icon]}</svg>`:''}
   <div class="ku lb" style="font-weight:${o.w||800};font-size:${o.fs||44}px;line-height:1.25;color:${WINK};margin-top:4px;text-shadow:${WHALO}">${o.label}</div>
   <svg class="ln ul" viewBox="0 0 200 20" style="width:${o.uw||150}px;height:15px;margin-top:2px"><path d="M4 12 C 50 2, 120 18, 196 7" stroke="${ACC}" stroke-width="5"/></svg>`,
   `left:${cx-150}px;top:${y}px;width:300px;text-align:center;box-sizing:border-box;${CARD}`,(t,e)=>{
    if(t<o.a||t>o.b||inHalf(t)) return false; const [op,dy]=pres(t,o.a,o.b);
    e.style.opacity=op; e.style.transform=`translateY(${dy+Math.sin(t*1.3+cx)*4}px)`; e.style.filter=`blur(${(1-tw(t,o.a,.4))*6}px)`;
    const ic=e.querySelector('.ic'); if(ic){ draw(ic,tw(t,o.a+.05,.8,E.sm)); if(o.tintAt) ic.style.stroke=t>=o.tintAt?ACC:WINK; }
    draw(e.querySelector('.ul'),tw(t,o.a+.35,.6,E.sm)); if(o.tintAt) e.querySelector('.lb').style.color=t>=o.tintAt+.05?ACC:WINK;});
}
// single emphasised word beside the head, rising out of a mask with a drawn underline
function word(txt,side,y,a,b,fs=84){ sfx('tick',a,{f:1400+rnd()*600,g:-29,pan:side==='R'?.5:-.5});
  const cx=side==='R'?915:170;
  add(`<div class="ku" style="font-weight:900;font-size:${fs}px;line-height:1.35;color:${WINK};white-space:nowrap;text-shadow:${WHALO}"><span class="mask"><span class="w">${txt}</span></span></div>
    <svg class="ln ul" viewBox="0 0 200 20" style="width:150px;height:15px"><path d="M4 12 C 50 2, 120 18, 196 7" stroke="${ACC}" stroke-width="6"/></svg>`,
   `left:${cx-170}px;top:${y}px;width:340px;text-align:center;box-sizing:border-box;${CARD}`,(t,e)=>{
    if(t<a||t>b||inHalf(t)) return false; const q=tw(t,b-.3,.3,E.inn); e.style.opacity=1-q; e.style.transform=`translateY(${-q*26+Math.sin(t*1.2+y)*3}px)`;
    e.querySelector('.w').style.transform=`translateY(${(1-tw(t,a,.6,E.expo))*110}%)`; draw(e.querySelector('.ul'),tw(t,a+.3,.55,E.sm));});
}
// an image (e.g. a logo file YOU supply) on a soft white glow above the head
function image(src,a,b,y=150,w=560){ add(`<div style="position:absolute;left:-90px;top:-70px;right:-90px;bottom:-70px;background:radial-gradient(50% 50% at 50% 50%,rgba(255,255,255,.96) 45%,rgba(255,255,255,0) 100%)"></div><img src="${src}" style="position:relative;width:${w}px;display:block">`,
  `left:${540-w/2}px;top:${y}px;width:${w}px`,(t,e)=>{ if(t<a||t>b||inHalf(t)) return false; const [op,dy]=pres(t,a,b,.7,.4,-36); e.style.opacity=op; e.style.transform=`translateY(${dy}px) scale(${.94+.06*tw(t,a,.8,E.expo)})`; e.style.filter=`blur(${(1-tw(t,a,.45))*8}px)`;}); }
// title on the chest area: two-part headline (second part accent) + small line. T = time the headline lands.
function lowerThird(a,b,T,big1,big2,small){ CAPDOWN.push([a,b]); sfx('whoosh',a+.1,{g:-24,d:.5}); sfx('ding',T+.05,{g:-25});
  add(`<div class="ku" style="font-weight:900;font-size:84px;line-height:1.35;color:#fff;white-space:nowrap;text-shadow:0 0 30px rgba(0,0,0,.65),0 3px 8px rgba(0,0,0,.5)"><span class="mask"><span class="b1">${big1}</span></span> <span class="mask"><span class="b2" style="color:${ACC2}">${big2}</span></span></div>
    <svg class="ln l" viewBox="0 0 800 16" style="width:800px;height:16px;display:block;margin:6px auto 10px"><path d="M796 8 C 600 2, 300 14, 4 8" stroke="${ACC}" stroke-width="7"/></svg>
    <div class="ku s" style="font-weight:500;font-size:46px;color:#fff;white-space:nowrap;text-shadow:0 0 24px rgba(0,0,0,.7),0 2px 6px rgba(0,0,0,.5)">${small||''}</div>`,
   'left:90px;top:1015px;width:860px;text-align:center',(t,e)=>{
    if(t<a||t>b) return false; const q=tw(t,b-.3,.3,E.inn); e.style.opacity=1-q; e.style.transform=`translateY(${-q*30}px)`;
    draw(e.querySelector('.l'),tw(t,a,.7,E.sm));
    e.querySelector('.b1').style.transform=`translateY(${(1-tw(t,T-.06,.6,E.expo))*110}%)`; e.querySelector('.b2').style.transform=`translateY(${(1-tw(t,T+.5,.6,E.expo))*110}%)`;
    const s=e.querySelector('.s'), sp=tw(t,a+.3,.6,E.expo); s.style.opacity=clamp((t-a-.3)/.3); s.style.transform=`translateY(${(1-sp)*24}px)`;});
}
// inside the split panel: a curved path with up to three numbered steps. steps=[[time,numeral,label],...]; b = end
function steps(b,list){ const mx=x=>LTR?1080-x:x;   // the path runs in reading direction
  const P=[[930,680,850,548],[540,480,540,348],[150,290,250,158]].map(([x,y,lx,ly])=>[mx(x),y,mx(lx),ly]), T=list.map(s=>s[0]);
  sub(`<svg class="ln" viewBox="0 0 1080 760" style="width:1080px;height:760px;overflow:visible;${LTR?'transform:scaleX(-1)':''}"><path d="M930 680 C 740 680, 720 480, 540 480 S 340 290, 150 290" stroke="${ACC}" stroke-width="11"/></svg>`,'left:0;top:0',(t,e)=>{
    if(!within(t,T[0]-.1,b)) return false; let p=0; if(T[1]!==undefined){ p=t<T[1]?lerp(0,.5,tw(t,T[0],T[1]-T[0],E.sm)):lerp(.5,T[2]!==undefined?1:.5,tw(t,T[1],(T[2]||T[1]+1)-T[1],E.sm)); } draw(e,p);});
  list.forEach(([t0,n,lab],i)=>{ const [x,y,lx,ly]=P[i]; sfx('tick',t0,{f:1500+i*250,g:-27});
    sub('',`left:${x-22}px;top:${y-22}px;width:44px;height:44px;border-radius:50%;background:${ACC};box-shadow:0 0 0 9px ${PHALO},0 0 0 12px ${ACC}`,(t,e)=>{
      if(!within(t,t0,b)) return false; e.style.transform=`scale(${tw(t,t0,.5,E.expo)})`; e.style.opacity=clamp((t-t0)/.1);});
    sub(`<span class="ku" style="font-weight:900;font-size:72px;color:${ACC};margin-inline-end:16px">${n}</span><span class="ku" style="font-weight:900;font-size:68px;color:${PINK};white-space:nowrap;text-shadow:0 0 14px ${PHALO},0 0 14px ${PHALO},0 0 8px ${PHALO},0 0 8px ${PHALO}">${lab}</span>`,
     `left:${lx-320}px;top:${ly}px;width:640px;text-align:center;direction:${DIR}`,(t,e)=>{
      if(!within(t,t0+.05,b)) return false; const [op,dy]=pres(t,t0+.05,b+1); e.style.opacity=op; e.style.transform=`translateY(${dy}px)`; e.style.filter=`blur(${(1-tw(t,t0+.05,.4))*6}px)`;}); });
}
// inside the split panel: two-part headline at the top of the stage
function panelHeadline(a,b,t1,t2){ sfx('whoosh',a,{g:-24,d:.5});
  sub(`<div class="ku" style="font-weight:900;font-size:88px;line-height:1.3;color:${PINK};white-space:nowrap"><span class="mask"><span class="h1">${t1}</span></span> <span class="mask"><span class="h2" style="color:${ACC};${GLOW(ACC)}">${t2}</span></span></div>
   <svg class="ln ul" viewBox="0 0 600 24" style="width:600px;height:24px;display:block;margin:0 auto"><path d="M6 14 C 150 2, 400 24, 594 8" stroke="${ACC}" stroke-width="7"/></svg>`,
  'left:0;top:6px;width:1080px;text-align:center',(t,e)=>{
   if(!within(t,a-.05,b)) return false; e.querySelector('.h1').style.transform=`translateY(${(1-tw(t,a-.05,.6,E.expo))*110}%)`; e.querySelector('.h2').style.transform=`translateY(${(1-tw(t,a+.12,.6,E.expo))*110}%)`;
   draw(e.querySelector('.ul'),tw(t,a+.35,.6,E.sm));}); }

// ---------------- more components ----------------
// big word in front of the speaker (chest area). kind:'yes' | 'no' | undefined colours it and picks the sound.
function bigWord(txt,a,b,o={}){ const c=o.color||(o.kind==='yes'?'#3DDC84':o.kind==='no'?'#FF4257':ACC2), y=o.y||1080, fs=o.fs||230;
  CAPDOWN.push([a,b]); sfx(o.kind==='no'?'err':o.kind==='yes'?'ding':'impact',a,o.kind?{g:-24}:{g:-16});
  add(`<div class="ku" style="font-weight:900;font-size:${fs}px;line-height:1.25;color:${c};white-space:nowrap;text-shadow:0 0 34px rgba(0,0,0,.55),0 6px 14px rgba(0,0,0,.5)${TH.glow?`,0 0 60px ${c}88`:''}"><span class="mask"><span class="w">${txt}</span></span></div>
    <svg class="ln ul" viewBox="0 0 600 30" style="width:520px;height:26px;display:block;margin:-8px auto 0"><path d="M8 18 C 150 4, 420 28, 592 10" stroke="${c}" stroke-width="10"/></svg>`,
   `left:0;top:${y-fs*.7}px;width:1080px;text-align:center`,(t,e)=>{
    if(t<a||t>b) return false; const q=tw(t,b-.25,.25,E.inn), p=tw(t,a,.5,E.expo); e.style.opacity=1-q; e.style.transform=`scale(${1.12-.12*p+q*.06}) rotate(${o.tilt===undefined?-3:o.tilt}deg)`;
    e.querySelector('.w').style.transform=`translateY(${(1-p)*110}%)`; draw(e.querySelector('.ul'),tw(t,a+.2,.45,E.sm));}); }
// numbered marker above the speaker's head: stepMarker('1','Start small',a,b)
function stepMarker(n,label,a,b,o={}){ const y=o.y||250; sfx('pop',a,{g:-21,f:520+60*(parseInt(n)||0)});
  add(`<span style="display:inline-flex;align-items:center;gap:22px;direction:${DIR};${TH.cards?`background:rgba(7,10,22,.82);border-radius:999px;padding:12px 34px 12px 34px;box-shadow:0 0 0 2px ${ACC}55,0 12px 40px rgba(0,0,0,.45)`:''}">
     <span class="num" style="display:inline-flex;align-items:center;justify-content:center;width:112px;height:112px;border-radius:50%;background:${ACC};color:${TH.darkPanel?INK:'#fff'};font-family:var(--font);font-weight:900;font-size:76px;line-height:1;box-shadow:0 8px 24px rgba(0,0,0,.3)">${n}</span>
     <span class="ku" style="font-weight:900;font-size:${o.fs||70}px;line-height:1.3;color:${TH.cards?'#fff':'#fff'};white-space:nowrap;text-shadow:0 0 26px rgba(0,0,0,.65),0 3px 8px rgba(0,0,0,.55)"><span class="mask"><span class="w">${label}</span></span></span></span>`,
   `left:0;top:${y}px;width:1080px;text-align:center`,(t,e)=>{
    if(t<a||t>b||inHalf(t)) return false; const q=tw(t,b-.3,.3,E.inn); e.style.opacity=clamp((t-a)/.12)*(1-q); e.style.transform=`translateY(${-q*30+Math.sin(t*1.2)*3}px)`;
    const nm=e.querySelector('.num'), p=tw(t,a,.5,E.expo); nm.style.transform=`scale(${.3+.7*p}) rotate(${(1-p)*-40}deg)`;
    e.querySelector('.w').style.transform=`translateY(${(1-tw(t,a+.12,.55,E.expo))*110}%)`;}); }
// an image YOU supply (app icon, logo, screenshot) on a rounded card with a label, beside the head
function logoCard(src,label,side,y,a,b,o={}){ const cx=side==='R'?885:195, w=o.w||250; sfx('pop',a,{g:-22,pan:side==='R'?.5:-.5});
  add(`<div style="width:${w}px;box-sizing:border-box;padding:26px;border-radius:44px;background:${TH.cards?'rgba(7,10,22,.86)':'#fff'};box-shadow:${TH.cards?`0 0 0 2px ${ACC}66,`:''}0 18px 50px rgba(0,0,0,.35)"><img src="${src}" style="width:100%;display:block;border-radius:22px"></div>
    ${label?`<div class="ku" style="margin-top:14px;font-weight:800;font-size:${o.fs||44}px;color:#fff;white-space:nowrap;text-shadow:0 0 22px rgba(0,0,0,.7),0 2px 6px rgba(0,0,0,.6)">${label}</div>`:''}`,
   `left:${cx-w/2}px;top:${y}px;width:${w}px;text-align:center`,(t,e)=>{
    if(t<a||t>b||inHalf(t)) return false; const p=tw(t,a,.6,E.expo), q=tw(t,b-.3,.3,E.inn); e.style.opacity=clamp((t-a)/.15)*(1-q);
    e.style.transform=`translateY(${(1-p)*70-q*40+Math.sin(t*1.1+cx)*5}px) rotate(${(1-p)*(side==='R'?10:-10)+(side==='R'?3:-3)}deg) scale(${.8+.2*p})`;}); }
// full-screen code wall inside takeover i: lines type themselves. lines=['const x = 1', ...]
function codeWall(i,lines,o={}){ const K=TK[i], A=K.a+.35, B=K.b, cps=o.cps||((lines.join('').length+2*lines.length)/Math.max(.6,(B-A-.9))); sfx('keys',A,{end:B-.5});
  const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;'); let off=0; const starts=lines.map(l=>{const s=off; off+=l.length+2; return s;});
  if(o.title) add(`<div class="ku" style="font-weight:900;font-size:84px;color:#fff;white-space:nowrap;${GLOW(ACC)}"><span class="mask"><span class="w">${o.title}</span></span></div>`,'left:0;top:300px;width:1080px;text-align:center',(t,e)=>{
    if(!within(t,K.a,B)) return false; e.querySelector('.w').style.transform=`translateY(${(1-tw(t,A,.6,E.expo))*110}%)`;},'',TKC[i]);
  add(lines.map((l,n)=>`<div style="white-space:pre;height:1.55em"><span style="display:inline-block;width:70px;color:#5A5C63;text-align:right;margin-right:26px">${n+1}</span><span class="cl"></span></div>`).join('')+`<div class="cur" style="position:absolute;width:16px;height:40px;background:${ACC}"></div>`,
   `left:70px;top:${o.title?470:380}px;width:900px;direction:ltr;text-align:left;font-family:'JetBrains Mono',monospace;font-weight:500;font-size:${o.fs||34}px;line-height:1.55;color:#E6E8EE`,(t,e)=>{
    if(!within(t,K.a,B)) return false; const n=(t-A)*cps, rows=e.querySelectorAll('.cl'); let cr=0, cc=0;
    lines.forEach((l,k)=>{ const m=Math.round(clamp(n-starts[k],0,l.length)); if(rows[k].dataset.m!=m){ rows[k].dataset.m=m; rows[k].innerHTML=esc(l.slice(0,m)).replace(/(\/\/.*)$/,`<span style="color:#6B7280">$1</span>`).replace(/\b(const|let|function|return|if|else|for|import|from|def|class|await|async)\b/g,`<span style="color:${ACC2}">$1</span>`); } if(n>=starts[k]){cr=k;cc=m;} });
    const cu=e.querySelector('.cur'); cu.style.left=(96+cc*(o.fs||34)*.6)+'px'; cu.style.top=(cr*1.55*(o.fs||34)+6)+'px'; cu.style.opacity=(Math.floor(t*2.5)%2||n<off)?1:0;
    e.style.transform=`translateY(${-Math.max(0,cr-14)*1.55*(o.fs||34)}px)`;},'',TKC[i]); }
