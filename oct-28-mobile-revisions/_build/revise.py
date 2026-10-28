"""Oct 28 revisions to parts/site.html. Every replacement must match exactly the expected number of times."""
import re, sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f'expected {count} match(es), found {n}: {old[:90]!r}')
    s = s.replace(old, new)

OLDV, NEWV = '?v=202610231310', '?v=202610281200'
s = s.replace(OLDV, NEWV)
V = NEWV

# ---------- header: hamburger (mobile/tablet nav) ----------
BURGER = '<span class="burger" aria-hidden="true"><i></i><i></i><i></i></span>'
rep('<button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="sheet">Menu</button>',
    '<button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="sheet" aria-label="Open menu">' + BURGER + '</button>')
rep('<button class="menu-btn" id="menuClose" style="display:inline-block">Close</button>',
    '<button class="menu-btn" id="menuClose" style="display:inline-grid" aria-label="Close menu"><span class="burger burger--x" aria-hidden="true"><i></i><i></i><i></i></span></button>')

# ---------- sheet: ringed bullets on every stop, E / C / F tokens ----------
rep('<li><a href="#events">Events</a></li>\n    <li><a href="#contact">Contact</a></li>\n    <li><a href="#franchise">Franchise</a></li>',
    '<li><a href="#events"><span class="bullet bullet--ink">E</span>Events</a></li>\n'
    '    <li><a href="#contact"><span class="bullet bullet--sage">C</span>Contact</a></li>\n'
    '    <li><a href="#franchise"><span class="bullet bullet--red">F</span>Franchise</a></li>')

# ---------- skip link visible on keyboard focus ----------
rep('<a href="#main" style="position:absolute;left:-999px">Skip to content</a>',
    '<a class="skip" href="#main">Skip to content</a>')

# ---------- hero video: inline playback hints ----------
rep('<video id="heroVid" autoplay muted loop playsinline preload="auto"',
    '<video id="heroVid" autoplay muted loop playsinline webkit-playsinline disablepictureinpicture disableremoteplayback preload="auto"')

# ---------- Made To Be Craved ----------
rep('<h2 class="display h2"><i>M</i>ade to <i>B</i>e <i>C</i>raved.</h2>',
    '<h2 class="display h2"><i>M</i>ade <i>T</i>o <i>B</i>e <i>C</i>raved.</h2>')

# ---------- Get Mad. / Order Now. as two lines ----------
rep('<h2 class="display"><i>G</i>et <i>M</i>ad.<br><i>O</i>rder <i>N</i>ow.</h2>',
    '<h2 class="display"><span class="ln"><i>G</i>et <i>M</i>ad.</span> <span class="ln"><i>O</i>rder <i>N</i>ow.</span></h2>')

# ---------- menu: swap the band after The Specialties with the band after Kids ----------
A = f'<div class="mband" role="img" aria-label="Mad For Chicken food" style="background-image:url(assets/DSC7144.jpg{V})"></div>'
B = f'<div class="mband" role="img" aria-label="Mad For Chicken food" style="background-image:url(assets/DSC6895.jpg{V})"></div>'
rep(A, '@@BAND_A@@'); rep(B, '@@BAND_B@@')
rep('@@BAND_A@@', B); rep('@@BAND_B@@', A)

# ---------- menu: different sandwich cutout on mobile ----------
rep(f'<span class="mcut-wrap" tabindex="0"><img class="mcut" src="assets/cut-sandwich.png{V}" alt="Spicy chicken sandwich" loading="lazy"></span>',
    f'<span class="mcut-wrap" tabindex="0"><picture><source media="(max-width:820px)" srcset="assets/cut-sandwich-chicken.png{V}"><img class="mcut" src="assets/cut-sandwich.png{V}" alt="Spicy chicken sandwich" loading="lazy"></picture></span>')

# ---------- locations: no pre-header on mobile; Queens Post quote first ----------
rep('<p class="kicker label">What people say</p>', '<p class="kicker label kicker--say">What people say</p>')
Q1 = '<figure><blockquote>“Fried to a shattering crunch.”</blockquote><figcaption>NYC Tourism</figcaption></figure>'
Q2 = '<figure><blockquote>“The first Korean fried chicken restaurant in New York.”</blockquote><figcaption>Queens Post</figcaption></figure>'
rep(Q1 + '\n        ' + Q2, Q2 + '\n        ' + Q1)

# ---------- franchise: previous (marquee) photo, sign centred in the frame ----------
rep(f'<img src="assets/franchise-storefront.jpg{V}" alt="A Mad For Chicken storefront lit up at night" loading="lazy">',
    f'<img src="assets/franchise-marquee.jpg{V}" alt="The Mad For Chicken sign over a brick storefront" loading="lazy" style="object-position:86% 50%">')

# ---------- floating controls: accessibility + mobile Order Now CTA (inside the footer so inner pages get them too) ----------
A11Y = f'''
  <a class="mcta btn btn--doodle" href="#locations" data-order><span class="dood"><img src="assets/logo-trace.png{V}" alt=""></span><span>Order Now</span></a>
  <button class="a11y-btn" id="a11yBtn" type="button" aria-label="Accessibility options" aria-expanded="false" aria-controls="a11yPanel"><svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><circle cx="12" cy="3.6" r="2.2"/><path d="M20.3 7.6c-2.6.7-5.4 1.1-8.3 1.1s-5.7-.4-8.3-1.1l-.6 2.1c2 .6 4.2.9 6.4 1.1v3.1L7.3 21.7l2.1.6 2.6-7.4 2.6 7.4 2.1-.6-2.2-7.8v-3.1c2.2-.2 4.4-.5 6.4-1.1z"/></svg></button>
  <div class="a11y-panel" id="a11yPanel" role="dialog" aria-modal="false" aria-labelledby="a11yTitle" hidden>
    <div class="a11y-panel__head"><h2 class="label" id="a11yTitle">Accessibility</h2><button class="omodal__x" type="button" id="a11yClose" aria-label="Close accessibility options">×</button></div>
    <div class="a11y-opts">
      <button type="button" data-a11y="text" aria-pressed="false"><b aria-hidden="true">A+</b>Larger text</button>
      <button type="button" data-a11y="contrast" aria-pressed="false"><b aria-hidden="true">◐</b>High contrast</button>
      <button type="button" data-a11y="links" aria-pressed="false"><b aria-hidden="true">⎁</b>Highlight links</button>
      <button type="button" data-a11y="motion" aria-pressed="false"><b aria-hidden="true">❚❚</b>Pause motion</button>
      <button type="button" data-a11y="font" aria-pressed="false"><b aria-hidden="true">Aa</b>Readable font</button>
      <button type="button" data-a11y="spacing" aria-pressed="false"><b aria-hidden="true">↕</b>Text spacing</button>
    </div>
    <button type="button" class="a11y-reset" id="a11yReset">Reset all</button>
    <p class="a11y-note">Need help using this site? Email <a href="mailto:support@madforchickenusa.com">support@madforchickenusa.com</a>.</p>
  </div>
  <script>
  (function(){{var K='mfc-a11y',root=document.documentElement,btn=document.getElementById('a11yBtn'),panel=document.getElementById('a11yPanel');if(!btn||!panel)return;
  var opts=[].slice.call(panel.querySelectorAll('[data-a11y]')),on={{}};
  try{{on=JSON.parse(localStorage.getItem(K)||'{{}}')||{{}}}}catch(e){{on={{}}}}
  function apply(){{opts.forEach(function(o){{var k=o.dataset.a11y,v=!!on[k];root.classList.toggle('a11y-'+k,v);o.setAttribute('aria-pressed',v)}});
    var hv=document.getElementById('heroVid');if(hv){{if(on.motion)hv.pause();else if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){{var p=hv.play();if(p&&p.catch)p.catch(function(){{}})}}}}
    try{{localStorage.setItem(K,JSON.stringify(on))}}catch(e){{}}}}
  function open(v){{panel.hidden=!v;btn.setAttribute('aria-expanded',v);if(v)opts[0].focus();else btn.focus()}}
  btn.addEventListener('click',function(){{open(panel.hidden)}});
  document.getElementById('a11yClose').addEventListener('click',function(){{open(false)}});
  document.getElementById('a11yReset').addEventListener('click',function(){{on={{}};apply()}});
  opts.forEach(function(o){{o.addEventListener('click',function(){{on[o.dataset.a11y]=!on[o.dataset.a11y];apply()}})}});
  document.addEventListener('keydown',function(e){{if(e.key==='Escape'&&!panel.hidden)open(false)}});
  document.addEventListener('click',function(e){{if(!panel.hidden&&!panel.contains(e.target)&&!btn.contains(e.target))open(false)}});
  apply();}})();
  </script>
</footer>'''
rep('    <div class="ftr__bot">© 2026 Mad For Chicken. All Rights Reserved.</div>\n  </div>\n</footer>',
    '    <div class="ftr__bot">© 2026 Mad For Chicken. All Rights Reserved.</div>\n  </div>' + A11Y)

# ---------- JS: hero autoplay ----------
rep("  var hv=document.getElementById('heroVid');\n  if(hv&&reduce){hv.removeAttribute('autoplay');hv.pause()}",
    "  var hv=document.getElementById('heroVid');\n"
    "  if(hv&&reduce){hv.removeAttribute('autoplay');hv.pause()}\n"
    "  /* phones: make sure the muted hero starts on its own (iOS shows a play button when a first attempt is refused) */\n"
    "  if(hv&&!reduce){\n"
    "    hv.muted=true;hv.defaultMuted=true;hv.setAttribute('muted','');hv.playsInline=true;\n"
    "    var heroPlay=function(){if(!hv.paused||document.getElementById('view-home').hidden||document.documentElement.classList.contains('a11y-motion'))return;var p=hv.play();if(p&&p.catch)p.catch(function(){})};\n"
    "    ['loadeddata','canplay'].forEach(function(ev){hv.addEventListener(ev,heroPlay)});\n"
    "    ['touchstart','scroll','pointerdown'].forEach(function(ev){window.addEventListener(ev,heroPlay,{passive:true,once:true})});\n"
    "    document.addEventListener('visibilitychange',function(){if(!document.hidden)heroPlay()});\n"
    "    heroPlay();\n"
    "  }")

# ---------- JS: sauces — one photo per pick, and the line slides to the next stops ----------
rep("""    var old=cupVis.querySelector('img');if(old)old.remove();
    cupDish.hidden=false;
    var src='assets/sauces/'+li.dataset.slug+'.png';
    function usePhoto(){var im=new Image();im.src=src;im.alt=li.dataset.name+' sauce cup';cupVis.appendChild(im);cupDish.hidden=true}
    if(photoCache[src]===true)usePhoto();
    else if(photoCache[src]===undefined){var t=new Image();t.onload=function(){photoCache[src]=true;if(li.classList.contains('on'))usePhoto()};t.onerror=function(){photoCache[src]=false};t.src=src}""",
"""    [].forEach.call(cupVis.querySelectorAll('img'),function(o){o.remove()});
    cupDish.hidden=false;
    var src='assets/sauces/'+li.dataset.slug+'.png';
    function usePhoto(){if(!li.classList.contains('on'))return;[].forEach.call(cupVis.querySelectorAll('img'),function(o){o.remove()});var im=new Image();im.src=src;im.alt=li.dataset.name+' sauce cup';cupVis.appendChild(im);cupDish.hidden=true}
    if(photoCache[src]===true)usePhoto();
    else if(photoCache[src]===undefined){photoCache[src]='loading';var t=new Image();t.onload=function(){photoCache[src]=true;usePhoto()};t.onerror=function(){photoCache[src]=false};t.src=src}""")
rep("""  sauceLis.forEach(function(li){
    li.addEventListener('mouseenter',function(){showSauce(li)});
    li.addEventListener('focus',function(){showSauce(li)});
    li.addEventListener('click',function(){showSauce(li)});
  });""",
"""  /* when a line runs wider than the screen, slide it so the picked stop leads and the next ones come into view */
  window.mfcSlide=function(li){
    var tr=li.closest('.track');if(!tr||tr.scrollWidth<=tr.clientWidth+2)return;
    var max=tr.scrollWidth-tr.clientWidth,x=Math.max(0,Math.min(max,li.offsetLeft-12));
    if(tr.scrollTo)tr.scrollTo({left:x,behavior:reduce?'auto':'smooth'});else tr.scrollLeft=x;
  };
  sauceLis.forEach(function(li){
    li.addEventListener('mouseenter',function(){if(!li.classList.contains('on'))showSauce(li)});
    li.addEventListener('focus',function(){if(!li.classList.contains('on'))showSauce(li)});
    li.addEventListener('click',function(){if(!li.classList.contains('on'))showSauce(li);window.mfcSlide(li)});
  });""")
rep("    lis.forEach(function(li){['mouseenter','focus','click'].forEach(function(ev){li.addEventListener(ev,function(){show(li)})})});",
    "    lis.forEach(function(li){['mouseenter','focus','click'].forEach(function(ev){li.addEventListener(ev,function(){if(!li.classList.contains('on'))show(li);if(ev==='click'&&window.mfcSlide)window.mfcSlide(li)})})});")

# ---------- JS: process cards flip by themselves as you scroll (touch / small screens) ----------
rep("""  [].forEach.call(document.querySelectorAll('.step'),function(s){
    s.addEventListener('click',function(){if(window.matchMedia('(hover: none)').matches)s.classList.toggle('tapped')});
  });""",
"""  [].forEach.call(document.querySelectorAll('.step'),function(s){
    s.addEventListener('click',function(){if(window.matchMedia('(hover: none)').matches)s.classList.toggle('tapped')});
  });
  if('IntersectionObserver' in window&&window.matchMedia('(hover: none), (max-width: 999px)').matches){
    var flipIO=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('tapped');flipIO.unobserve(e.target)}})},{rootMargin:'-38% 0px -38% 0px'});
    [].forEach.call(document.querySelectorAll('.step'),function(s){flipIO.observe(s)});
  }""")

# ---------- JS: subway line on small screens ----------
rep("""    svg.innerHTML='';lines=[];
    if(window.innerWidth<1000||document.getElementById('view-home').hidden)return;
    var rb=route.getBoundingClientRect(),W=rb.width,H=rb.height;
    svg.setAttribute('viewBox','0 0 '+W+' '+H);""",
"""    svg.innerHTML='';lines=[];
    if(document.getElementById('view-home').hidden)return;
    var rb=route.getBoundingClientRect(),W=rb.width,H=rb.height;
    svg.setAttribute('viewBox','0 0 '+W+' '+H);
    if(window.innerWidth<1000){buildMobile(rb);draw();return}""")
rep("""  function draw(){
    if(!lines.length)return;""",
"""  /* phones/tablets: one line down the left margin, a coloured stretch per step and a station at each card */
  function buildMobile(rb){
    var ref=document.querySelector('#home-process .wrap'),x=Math.max(9,parseFloat(getComputedStyle(ref).paddingLeft)/2);
    var top=document.getElementById('home-madness').getBoundingClientRect().top-rb.top;
    var ys=[].map.call(document.querySelectorAll('#steps .step__top'),function(t){var b=t.getBoundingClientRect();return b.top+b.height/2-rb.top});
    var fr=document.querySelector('#menuFrame .tframe');
    if(fr)ys.push(fr.getBoundingClientRect().top-rb.top+40);
    var prev=top;
    ys.forEach(function(y,i){
      var path='M'+x.toFixed(1)+' '+prev.toFixed(1)+' L'+x.toFixed(1)+' '+y.toFixed(1);
      var cas=document.createElementNS(NS,'path');cas.setAttribute('class','cas');cas.setAttribute('d',path);
      var ln=document.createElementNS(NS,'path');ln.setAttribute('class','ln');ln.setAttribute('d',path);ln.style.stroke=COLORS[Math.min(i,3)];
      svg.appendChild(cas);svg.appendChild(ln);
      var stn=null;
      if(i<4){stn=document.createElementNS(NS,'circle');stn.setAttribute('class','stn');stn.setAttribute('cx',x);stn.setAttribute('cy',y);stn.setAttribute('r',6);}
      var len=Math.max(1,y-prev);
      [cas,ln].forEach(function(p){p.style.strokeDasharray=len+' '+len});
      lines.push({cas:cas,ln:ln,stn:stn,cum:[0,len],trig:[prev,y],total:len});
      prev=y;
    });
    lines.forEach(function(L){if(L.stn)svg.appendChild(L.stn)});
  }
  function draw(){
    if(!lines.length)return;""")

rep('''  /* ---------- reveals ---------- */''', '''  /* phones: the floating Order Now steps aside while the Get Mad / Order Now section is on screen */
  var mcta=document.querySelector('.mcta'),homeOrder=document.getElementById('home-order');
  if(mcta&&homeOrder&&'IntersectionObserver' in window){new IntersectionObserver(function(es){es.forEach(function(e){mcta.classList.toggle('is-off',e.isIntersecting)})},{threshold:.2}).observe(homeOrder)}

  /* ---------- reveals ---------- */''')

# ---------- CSS ----------
CSS = r'''
/* ================= Oct 28 revisions ================= */
.skip{position:absolute;left:-999px;top:12px;z-index:100;background:var(--linen-hi);color:var(--ink);border:3px solid var(--red);border-radius:999px;padding:12px 20px 10px;font:15px/1 var(--f-label);letter-spacing:.08em;text-transform:uppercase}
.skip:focus{left:16px}
.order h2 .ln{display:block}
/* hero: cooler grade over the video (all sizes) */
.hero video{z-index:0}
.hero::before{content:"";position:absolute;inset:0;z-index:1;background:#2b5f92;mix-blend-mode:soft-light;opacity:.42;pointer-events:none}
.hero::after{z-index:2}
.hero video::-webkit-media-controls,.hero video::-webkit-media-controls-panel,.hero video::-webkit-media-controls-overlay-play-button,.hero video::-webkit-media-controls-start-playback-button{display:none!important;-webkit-appearance:none;opacity:0}
/* nav: hamburger */
.burger{display:block;position:relative;width:22px;height:16px}
.burger i{position:absolute;left:0;right:0;height:2.5px;border-radius:2px;background:currentColor;transition:transform .25s var(--ease),opacity .2s}
.burger i:nth-child(1){top:0}.burger i:nth-child(2){top:6.75px}.burger i:nth-child(3){top:13.5px}
.burger--x i:nth-child(1){transform:translateY(6.75px) rotate(45deg)}.burger--x i:nth-child(2){opacity:0}.burger--x i:nth-child(3){transform:translateY(-6.75px) rotate(-45deg)}
@media (max-width:1180px){.menu-btn{display:inline-grid;place-items:center;width:48px;height:48px;padding:0}}
/* menu sheet: every stop gets the same ringed token */
.sheet .bullet{box-shadow:inset 0 0 0 3px var(--linen-hi)}
.bullet--ink{--b:var(--ink)}.bullet--sage{--b:var(--sage)}
/* floating controls */
.a11y-btn{position:fixed;left:calc(18px + env(safe-area-inset-left,0px));bottom:calc(18px + env(safe-area-inset-bottom,0px));z-index:47;width:58px;height:58px;border-radius:50%;background:var(--spruce);color:var(--linen-hi);border:3px solid var(--linen-hi);box-shadow:0 0 0 3px var(--spruce),0 8px 20px rgba(0,0,0,.22);display:grid;place-items:center;cursor:pointer;padding:0}
.a11y-btn:hover{background:var(--spruce-deep)}
.a11y-panel{position:fixed;left:calc(18px + env(safe-area-inset-left,0px));bottom:calc(88px + env(safe-area-inset-bottom,0px));z-index:85;width:min(340px,calc(100vw - 36px));background:var(--linen);color:var(--ink);border:3px solid var(--ink);border-radius:8px;box-shadow:0 0 0 4px var(--spruce),0 24px 60px rgba(0,0,0,.35);padding:16px 16px 18px;display:grid;gap:12px}
.a11y-panel__head{display:flex;justify-content:space-between;align-items:center}
.a11y-panel h2{margin:0;font-size:20px;color:var(--spruce)}
.a11y-panel .omodal__x{width:40px;height:40px;font-size:20px}
.a11y-opts{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.a11y-opts button{display:grid;justify-items:center;gap:6px;padding:12px 8px 10px;border:2px solid var(--ink);border-radius:6px;background:var(--linen-hi);color:var(--ink);font:13px/1.1 var(--f-label);letter-spacing:.08em;text-transform:uppercase;cursor:pointer}
.a11y-opts button b{font:700 18px/1 Arial,sans-serif;letter-spacing:0}
.a11y-opts button[aria-pressed="true"]{background:var(--spruce);border-color:var(--spruce);color:var(--linen-hi)}
.a11y-reset{justify-self:start;background:none;border:0;padding:4px 0;font:14px/1 var(--f-label);letter-spacing:.08em;text-transform:uppercase;color:var(--red);text-decoration:underline;text-underline-offset:3px;cursor:pointer}
.a11y-note{margin:0;font-size:14px;line-height:1.4;color:var(--ink-soft)}
.a11y-note a{color:var(--red);text-decoration:underline}
html.a11y-text :is(p,li,label,input,select,textarea,blockquote,figcaption,.prose,.item p,.ev p,.station p,.lcard p){font-size:max(1.18em,20px)!important;line-height:1.55!important}
html.a11y-text :is(.navl,.btn,.label,.track li span,.mnav a,.snav button){font-size:max(1.12em,17px)!important}
html.a11y-contrast{--ink-soft:#000;--rule:rgba(0,0,0,.55)}
html.a11y-contrast body{color:#000}
html.a11y-contrast :is(.prose,.item p,.mcat__head p,.station p,.lcard p,.step__txt p,.note,.fine,.stops__count){color:inherit!important;opacity:1!important}
html.a11y-contrast :is(.sec--red,.sec--ink,.sec--spruce,.ph,.queens,.madness,.order,.ftr,.fhero,.formats) :is(p,li,.prose,a){color:#fff!important;opacity:1!important}
html.a11y-contrast .btn{border-color:#000;color:#000}
html.a11y-links a:not(.btn):not(.brand):not(.mcta){text-decoration:underline!important;text-underline-offset:4px!important;text-decoration-thickness:2px!important}
html.a11y-links a.btn,html.a11y-links button.btn{outline:2px dashed currentColor;outline-offset:3px}
html.a11y-motion *,html.a11y-motion *::before,html.a11y-motion *::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}
html.a11y-font :is(body,.display,.label,.btn,.navl,.fx-h,h1,h2,h3,h4,p,li,a,button,input,select,textarea,blockquote){font-family:Verdana,Arial,Helvetica,sans-serif!important;font-style:normal!important}
html.a11y-font .display i{font-style:normal!important}
html.a11y-spacing :is(p,li,blockquote,label){line-height:1.9!important;letter-spacing:.03em!important;word-spacing:.12em!important}
.mcta{display:none}
@media (max-width:760px){
  /* Order Now becomes a bottom CTA; the header keeps just the logo and the menu */
  .hdr nav.r .btn--doodle{display:none}
  .mcta{display:inline-flex;position:fixed;left:50%;transform:translateX(-50%);bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:46;width:calc(100% - 2*(52px + 28px));max-width:300px;justify-content:center;padding:4px 20px 4px 4px;font-size:17px;box-shadow:0 10px 26px rgba(0,0,0,.28)}
  .mcta:hover{transform:translateX(-50%) translateY(-2px)}
  .mcta .dood{width:44px;height:44px}
  .mcta .dood img{width:38px;height:42px}
  .a11y-btn,.totop{width:52px;height:52px;bottom:calc(16px + env(safe-area-inset-bottom,0px))}
  .a11y-btn{left:calc(14px + env(safe-area-inset-left,0px))}
  .totop{right:calc(14px + env(safe-area-inset-right,0px));opacity:1;transform:none;pointer-events:auto;visibility:hidden}
  .totop.show{visibility:visible}
  .a11y-panel{left:14px;bottom:calc(80px + env(safe-area-inset-bottom,0px))}
  .ftr{padding-bottom:110px}
}
@media (max-width:999px){
  /* hero: show more of the 16:9 film instead of a 4x crop; keep it clear of the header */
  .hero{height:calc(var(--hdr) + 56.25vw);min-height:0}
  .hero video{top:var(--hdr);height:calc(100% - var(--hdr));object-position:50% 50%}
  .hero::before{top:var(--hdr)}
  /* subway line runs down the left margin */
  .route__svg{display:block}
  .route__svg .cas{stroke-width:9}
  .route__svg .ln{stroke-width:5}
  .route__svg .stn{stroke-width:2.5}
  /* process photos fill their cards */
  .flip__b{display:block}
  .flip__b img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
  /* sauces line slides */
  .track{scroll-behavior:smooth}
  /* franchise photo sits centred in its frame */
  .fhero__photo{margin-inline:auto;width:100%}
}
@media (max-width:640px){
  .hero{height:calc(var(--hdr) + 92vw)}
  .step__art{height:min(58vw,260px)}
}
@media (max-width:760px){
  /* Get Mad. / Order Now. centred, two lines */
  .order__in{justify-items:center;text-align:center}
  .order__in>.rv{display:flex;flex-direction:column;align-items:center}
  .order__neon{justify-self:center;width:min(220px,60vw)}
  .order h2{font-size:clamp(44px,13vw,68px)}
  .order h2 .ln{white-space:nowrap}
  .order .btn{margin-top:36px}
  /* locations: no pre-header above Everyone's Talking */
  .kicker--say{display:none}
  /* menu: bigger cut / sauce pop-ups */
  .mpop__vis{width:min(62vw,250px)}
}
.mcut-wrap picture{display:block}
/* sauce / cut pop-ups: soft shadow underneath instead of a CSS drop-shadow filter,
   which Safari draws as a faint square around the cut-out while it animates */
.cup__vis img,.mpop__vis img{filter:none;position:relative;z-index:1}
.cup__vis::after,.mpop__vis::after{content:"";position:absolute;left:14%;right:14%;bottom:-5%;height:14%;border-radius:50%;background:radial-gradient(closest-side,rgba(25,18,10,.32),rgba(25,18,10,0));pointer-events:none}
.mpop:not(.has-img) .mpop__vis::after{display:none}
.mcta{transition:opacity .25s var(--ease)}
.mcta.is-off{opacity:0;pointer-events:none}
'''
rep('</style>\n</head>', CSS + '</style>\n</head>')

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
