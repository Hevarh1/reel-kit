// ---- EDIT ME: text direction, palette + layout timeline (all times are seconds in the clean cut) ----
// dir 'rtl' for Kurdish/Arabic/Persian, 'ltr' for English etc. font = CSS font-family list (must be linked in scene.html)
const TEXT={dir:'ltr', font:"'Inter'"};
// design: 'flow' (soft, drawn lines) | 'night' (dark, neon, cards) | 'punch' (heavy type, highlighter)
const THEME='night';
// optional colour override, e.g. {accent:'#EC5A5C', accent2:'#FF7C74'}; null = the design's own colours
const PALETTE=null;
// split screen: a paper panel covers the top, the speaker video shifts down
const HALF=[];
// full-screen takeover (use sparingly)
const TK=[{a:0.6,b:3.1}];
// slow push-ins on the speaker video: [start, end, zoomFrom, zoomTo]. Change zoom at every jump cut.
const ZOOMS=[[3.1,9.4,1.0,1.06],[9.4,12.2,1.0,1.05]];
// jump-cut times that get a soft light dip
const CUTS=[9.4];
// subtitle vertical centre: normal / split mode / lowered while a graphic sits on the chest area
const CAP_Y={normal:1330, split:800, low:1450, takeover:1400};
