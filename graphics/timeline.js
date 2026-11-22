// ---- EDIT ME: what appears when. Demo content for the example transcript (12 s). ----
// 0 - 3 s: ribbons flow past while the hook is spoken
ribbon(250,0.9,3.0,{sp:.9,w:8,amp:30});
ribbon(1090,1.3,3.0,{sp:1.25,w:14,amp:46,op:.85});
ribbon(1560,1.7,3.0,{sp:1.5,w:6,c:'#fff',amp:34});

// 3.1 - 9.4 s: split screen, three steps drawn along a path, then a headline
steps(9.42,[[4.90,'١','دەست پێبکە'],[6.20,'٢','بەردەوام بە'],[7.50,'٣','هەڵەکانت چاک بکە']]);
panelHeadline(3.75,9.42,'سێ هەنگاوی','سادە');

// 9.4 - 12 s: back on the speaker, words beside the head and a closing title on the chest
word('ئەمڕۆ','R',320,9.90,11.9);
note({icon:'cap',label:'فێربوون',side:'L',y:330,a:10.3,b:11.9});
lowerThird(10.5,12.2,10.7,'هەر ئێستا','دەست پێبکە','یەک هەنگاو لە ڕۆژێکدا');
