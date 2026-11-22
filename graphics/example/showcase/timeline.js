// Showcase of the other components (English, 12 s): code wall, step markers, big word, image card.
// Copy this file and config.js into graphics/ and try THEME 'night', 'punch' and 'flow'.
codeWall(0,["// learning.js","const steps = ['start small',","               'keep going',","               'fix your mistakes']","","for (const step of steps) {","  await practise(step)","}","return 'not hard'"],{title:'Not hard'});

stepMarker('1','Start small',4.90,6.15);
stepMarker('2','Keep going',6.20,7.45);
stepMarker('3','Fix your mistakes',7.50,9.35,{fs:60});

bigWord('YES',9.9,10.65,{kind:'yes'});
// replace PLACEHOLDER with your own image file, e.g. logoCard('assets/my_app.png','My app','R',330,10.7,12.1)
const PLACEHOLDER="data:image/svg+xml,"+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="28" fill="#D9DCE3"/><text x="100" y="94" text-anchor="middle" font-family="sans-serif" font-size="26" font-weight="700" fill="#6B7280">YOUR</text><text x="100" y="128" text-anchor="middle" font-family="sans-serif" font-size="26" font-weight="700" fill="#6B7280">IMAGE</text></svg>');
logoCard(PLACEHOLDER,'Your app','R',330,10.75,12.1);
word('Today','L',340,10.9,12.1);
