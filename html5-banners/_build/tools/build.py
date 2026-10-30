# Builds animated HTML5 banner folders from the Figma-derived spec.
# usage: python3 build.py <spec.py> <out_dir>
import json, os, re, shutil, sys
from PIL import Image

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(S, 'assets')
NAVY = '#1F3D7B'

spec = {}
exec(open(sys.argv[1]).read(), spec)
OUT = sys.argv[2]
vec = json.load(open(os.path.join(S, 'vec.json')))
body = json.load(open(os.path.join(S, 'body.json')))

LOOP = 8.0          # seconds per loop
PLAYS = 3           # IAB: stop on end frame after 3 loops (24s < 30s)


def bg_path(node_id, widen=0):
    svg = vec[node_id]['svg']
    d = re.search(r'd="([^"]+)"', svg).group(1)
    if widen:
        # push the right-hand x coordinates outward (used for 150->160)
        toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
        out, cmd, idx = [], None, 0
        for t in toks:
            if re.match(r'[A-Za-z]', t):
                cmd, idx = t, 0
                out.append(t)
                continue
            v = float(t)
            is_x = (cmd in 'MLC' and idx % 2 == 0) or cmd == 'H'
            if is_x and v > 75:
                v += widen
            idx += 1
            out.append(('%g' % v))
        d = ' '.join(out)
    return d


def keyframes(name, frames):
    """frames: list of (time_s, css)"""
    rows = []
    for t, css in frames:
        rows.append('  %.2f%% { %s }' % (min(100, t / LOOP * 100), css))
    return '@keyframes %s {\n%s\n}' % (name, '\n'.join(rows))


def ease_in(name, t0, t1, from_css, to_css):
    return keyframes(name, [(0, from_css), (t0, from_css), (t1, to_css), (LOOP, to_css)])


def build(b):
    W, H = b['w'], b['h']
    d = os.path.join(OUT, b['name'])
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    css, html, anims = [], [], []
    has_body = 'body' in b
    has_cta = 'cta' in b
    single = not has_body  # one-message units: logo -> zoom out -> core message

    # --- timeline -------------------------------------------------------
    T = dict(logo_in=(0.0, 0.6), logo_move=(1.3, 2.0), photo=(1.8, 2.6),
             head=(2.2, 2.9), body=(3.6, 4.3), cta=(5.1, 5.6))
    if single:
        T['head'] = (2.0, 2.7)

    # --- background -----------------------------------------------------
    html.append('<svg class="bg" width="%d" height="%d" viewBox="0 0 %d %d" aria-hidden="true">'
                '<path d="%s" fill="%s"/></svg>' % (W, H, W, H, bg_path(b['bg'], b.get('widen', 0)), NAVY))

    # --- photo (flattened on navy -> jpg, sits on navy bg) ---------------
    if 'photo' in b:
        p = b['photo']
        im = Image.open(os.path.join(ASSETS, 'photos', p['src']))
        flat = Image.new('RGB', im.size, NAVY)
        flat.paste(im, mask=im.split()[3])
        flat.save(os.path.join(d, 'photo.jpg'), quality=p.get('q', 82), optimize=True, progressive=True)
        html.append('<img class="photo" src="photo.jpg" alt="">')
        css.append('.photo{left:%gpx;top:%gpx;width:%gpx;height:%gpx;animation:photo %gs linear %d both}'
                   % (p['x'], p['y'], p['w'], p['h'], LOOP, PLAYS))
        anims.append(ease_in('photo', *T['photo'], 'opacity:0;transform:translateX(-24px)', 'opacity:1;transform:none'))

    # --- logo -----------------------------------------------------------
    L = b['logo']
    if L['kind'] == 'svg':
        svg = vec['1:3380']['svg']
        open(os.path.join(d, 'logo.svg'), 'w').write(svg)
        html.append('<img class="logo" src="logo.svg" alt="The Chicago School">')
    else:
        im = Image.open(os.path.join(ASSETS, 'logo-stacked@4x.png'))
        tw = int(round(L['w'] * 3))
        th = int(round(tw * im.height / im.width))
        if tw < im.width:
            im = im.resize((tw, th), Image.LANCZOS)
        im.save(os.path.join(d, 'logo.png'), optimize=True)
        html.append('<img class="logo" src="logo.png" alt="The Chicago School">')
    lx, ly, lw, lh = L['x'], L['y'], L['w'], L['h']
    s = min(0.62 * W / lw, 0.62 * H / lh, 2.6)
    s = max(s, 1.0)
    s = min(s, 0.9 * W / lw, 0.85 * H / lh) if s > 1 else s
    dx = W / 2 - (lx + lw / 2)
    dy = H / 2 - (ly + lh / 2)
    start = 'transform:translate(%.2fpx,%.2fpx) scale(%.3f)' % (dx, dy, s)
    css.append('.logo{left:%gpx;top:%gpx;width:%gpx;height:%gpx;transform-origin:50%% 50%%;'
               'animation:logo %gs linear %d both}' % (lx, ly, lw, lh, LOOP, PLAYS))
    a0, a1 = T['logo_in']
    m0, m1 = T['logo_move']
    anims.append(keyframes('logo', [
        (0, 'opacity:0;' + start), (a1, 'opacity:1;' + start + ';animation-timing-function:cubic-bezier(.6,0,.2,1)'),
        (m0, 'opacity:1;' + start + ';animation-timing-function:cubic-bezier(.6,0,.2,1)'),
        (m1, 'opacity:1;transform:none'), (LOOP, 'opacity:1;transform:none')]))
    # first keyframe easing
    anims[-1] = anims[-1].replace('0.00% { opacity:0;', '0.00% { animation-timing-function:ease-out;opacity:0;')

    # --- headline (live Playfair Display text) ---------------------------
    hd = b['head']
    lines = '<br>'.join(hd['lines'])
    html.append('<div class="head">%s</div>' % lines)
    css.append('.head{left:%gpx;top:%gpx;width:%gpx;font-size:%.3fpx;text-align:%s;animation:head %gs linear %d both}'
               % (hd['x'], hd['y'], hd['w'], hd['fs'], hd['align'], LOOP, PLAYS))
    anims.append(ease_in('head', *T['head'], 'opacity:0;transform:translateY(10px)', 'opacity:1;transform:none'))

    # --- supporting message (DIN OT, vector outlines from Figma) ---------
    if has_body:
        bd = body[b['body']]
        svg = bd['svg']
        open(os.path.join(d, 'body.svg'), 'w').write(svg)
        x = bd['x'] + b.get('shift', 0)
        html.append('<img class="body" src="body.svg" alt="%s">' % b['body_alt'])
        css.append('.body{left:%gpx;top:%gpx;width:%gpx;height:%gpx;animation:body %gs linear %d both}'
                   % (x, bd['y'], bd['w'], bd['h'], LOOP, PLAYS))
        anims.append(ease_in('body', *T['body'], 'opacity:0;transform:translateY(10px)', 'opacity:1;transform:none'))

    # --- CTA --------------------------------------------------------------
    if has_cta:
        c = b['cta']
        html.append('<div class="cta">Learn More</div>')
        css.append('.cta{left:%gpx;top:%gpx;width:%gpx;height:%gpx;line-height:%gpx;font-size:%.3fpx;'
                   'animation:cta %gs linear %d both}'
                   % (c['x'], c['y'], c['w'], c['h'], c['h'], c['fs'], LOOP, PLAYS))
        anims.append(ease_in('cta', *T['cta'], 'opacity:0;transform:scale(.85)', 'opacity:1;transform:none'))

    page = TEMPLATE.format(W=W, H=H, css='\n'.join(css), anims='\n'.join(anims), html='\n'.join(html),
                           title=b['title'], navy=NAVY)
    open(os.path.join(d, 'index.html'), 'w').write(page)
    shutil.copy(os.path.join(ASSETS, 'pfd700.woff2'), os.path.join(d, 'pfd700.woff2'))
    return d


TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="ad.size" content="width={W},height={H}">
<meta name="viewport" content="width={W},height={H}">
<title>{title}</title>
<script>var clickTag = "https://www.thechicagoschool.edu/";</script>
<style>
@font-face{{font-family:"Playfair Display";font-weight:700;font-style:normal;src:url(pfd700.woff2) format("woff2");font-display:block}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#fff}}
#ad{{position:relative;display:block;width:{W}px;height:{H}px;overflow:hidden;background:#fff;cursor:pointer;
-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}
#ad>*{{position:absolute;display:block}}
.bg{{left:0;top:0}}
.head{{font-family:"Playfair Display",Georgia,serif;font-weight:700;line-height:1.3333;color:#fff;white-space:nowrap}}
.cta{{background:#fff;color:{navy};font-family:"Playfair Display",Georgia,serif;font-weight:700;text-align:center;white-space:nowrap}}
{css}
.paused #ad *{{animation-play-state:paused!important}}
{anims}
</style>
</head>
<body>
<a id="ad" href="javascript:window.open(window.clickTag)" aria-label="The Chicago School - Learn More">
{html}
</a>
<script>
// Hold animations until the web font is ready so the headline never flashes in a fallback face.
(function(){{var r=document.documentElement;r.className='paused';
var go=function(){{r.className='';}};
if(document.fonts&&document.fonts.load){{document.fonts.load('700 20px "Playfair Display"').then(go,go);setTimeout(go,1500);}}else go();}})();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for b in spec['BANNERS']:
        print(build(b))
