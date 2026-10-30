# Builds animated HTML5 banner folders from the Figma-derived spec.
# usage: python3 build.py <spec.py> <out_dir> [align.json]
import json, os, re, shutil, sys
from PIL import Image

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(S, 'assets')
NAVY = '#1F3D7B'

spec = {}
exec(open(sys.argv[1]).read(), spec)
OUT = sys.argv[2]
# optional: per-line offsets measured by align.py against Figma's 2x render
ALIGN = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
vec = json.load(open(os.path.join(S, 'vec.json')))

LOOP = 8.0      # seconds per loop; loops forever, like a GIF
OUT_FADE = 0.4  # everything fades back to the bare background before the loop restarts

# Figma "auto" line heights: Playfair = ascent+descent (1.333em); DIN OT adds its 0.288em line gap.
# Figma places the whole DIN line gap above the first line, CSS splits it, hence DIN_TOP.
DIN_LH, DIN_TOP = 1.288, 0.144


def bg_path(node_id, widen=0):
    d = re.search(r'd="([^"]+)"', vec[node_id]['svg']).group(1)
    if not widen:
        return d
    # push the right-hand x coordinates outward (used for 150->160)
    out, cmd, idx = [], None, 0
    for t in re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d):
        if t.isalpha():
            cmd, idx = t, 0
            out.append(t)
            continue
        v = float(t)
        if ((cmd in 'MLC' and idx % 2 == 0) or cmd == 'H') and v > 75:
            v += widen
        idx += 1
        out.append('%g' % v)
    return ' '.join(out)


def keyframes(name, frames):
    """frames: list of (time_s, css)"""
    rows = ['  %.2f%% { %s }' % (min(100, t / LOOP * 100), css) for t, css in frames]
    return '@keyframes %s {\n%s\n}' % (name, '\n'.join(rows))


def build_in(name, t0, t1, hidden, shown):
    end = LOOP - OUT_FADE
    return keyframes(name, [(0, hidden), (t0, hidden + ';animation-timing-function:cubic-bezier(.2,.6,.3,1)'),
                            (t1, shown), (end, shown), (LOOP, 'opacity:0;transform:none')])


def lines_html(t):
    # one block per line; 'nudge' holds per-line px offsets measured against Figma's render (Figma snaps each line)
    n = t.get('nudge') or [0] * len(t['lines'])
    return ''.join('<span style="top:%gpx">%s</span>' % (dy, ln) if dy else '<span>%s</span>' % ln
                   for ln, dy in zip(t['lines'], n))


def anim(name):
    return 'animation:%s %gs linear infinite both' % (name, LOOP)


def build(b):
    W, H = b['w'], b['h']
    d = os.path.join(OUT, b['name'])
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    css, html, anims = [], [], []
    single = 'body' not in b  # one-message units: logo -> zoom out -> core message

    T = dict(logo_in=(0.0, 0.6), logo_move=(1.3, 2.0), photo=(1.8, 2.6),
             head=(2.2, 2.9), body=(3.6, 4.3), cta=(5.1, 5.6))
    if single:
        T['head'] = (2.0, 2.7)

    # background
    html.append('<svg class="bg" width="%d" height="%d" viewBox="0 0 %d %d" aria-hidden="true">'
                '<path d="%s" fill="%s"/></svg>' % (W, H, W, H, bg_path(b['bg'], b.get('widen', 0)), NAVY))

    # photo: flattened onto navy (it only ever sits over the navy shape) -> small jpg, 2x density
    if 'photo' in b:
        p = b['photo']
        im = Image.open(os.path.join(ASSETS, 'photos', p['src']))
        flat = Image.new('RGB', im.size, NAVY)
        flat.paste(im, mask=im.split()[3])
        flat.save(os.path.join(d, 'photo.jpg'), quality=p.get('q', 82), subsampling=0, optimize=True, progressive=True)
        html.append('<img class="photo" src="photo.jpg" alt="">')
        css.append('.photo{left:%gpx;top:%gpx;width:%gpx;height:%gpx;%s}' % (p['x'], p['y'], p['w'], p['h'], anim('photo')))
        anims.append(build_in('photo', *T['photo'], 'opacity:0;transform:translateX(-24px)', 'opacity:1;transform:none'))

    # logo
    L = b['logo']
    if L['kind'] == 'svg':
        open(os.path.join(d, 'logo.svg'), 'w').write(vec['1:3380']['svg'])
        html.append('<img class="logo" src="logo.svg" alt="The Chicago School">')
    else:
        im = Image.open(os.path.join(ASSETS, 'logo-stacked.png'))
        tw = int(round(L['w'] * 4))  # 4x: still sharp while it is zoomed up during the intro
        im = im.resize((tw, int(round(tw * im.height / im.width))), Image.LANCZOS)
        im.save(os.path.join(d, 'logo.png'), optimize=True)
        html.append('<img class="logo" src="logo.png" alt="The Chicago School">')
    lx, ly, lw, lh = L['x'], L['y'], L['w'], L['h']
    s = max(min(0.62 * W / lw, 0.62 * H / lh, 2.6), 1.0)
    s = min(s, 0.9 * W / lw, 0.85 * H / lh) if s > 1 else s
    start = 'transform:translate(%.2fpx,%.2fpx) scale(%.3f)' % (W / 2 - (lx + lw / 2), H / 2 - (ly + lh / 2), s)
    ease = ';animation-timing-function:cubic-bezier(.6,0,.2,1)'
    css.append('.logo{left:%gpx;top:%gpx;width:%gpx;height:%gpx;transform-origin:50%% 50%%;%s}' % (lx, ly, lw, lh, anim('logo')))
    anims.append(keyframes('logo', [
        (0, 'opacity:0;' + start + ';animation-timing-function:ease-out'), (T['logo_in'][1], 'opacity:1;' + start + ease),
        (T['logo_move'][0], 'opacity:1;' + start + ease), (T['logo_move'][1], 'opacity:1;transform:none'),
        (LOOP - OUT_FADE, 'opacity:1;transform:none'), (LOOP, 'opacity:0;transform:none')]))

    # core message: live Playfair Display
    meas = ALIGN.get('%dx%d' % (W, H), {})
    for key in ('head', 'body'):
        if key in b and key in meas:
            b[key]['nudge'] = [dy for _, dy, _ in meas[key]]
    hd = b['head']
    html.append('<div class="head">%s</div>' % lines_html(hd))
    css.append('.head{left:%gpx;top:%gpx;width:%gpx;font-size:%.3fpx;text-align:%s;%s}'
               % (hd['x'], hd['y'], hd['w'], hd['fs'], hd['align'], anim('head')))
    anims.append(build_in('head', *T['head'], 'opacity:0;transform:translateY(10px)', 'opacity:1;transform:none'))

    # supporting message: live DIN OT, Figma's line breaks
    if not single:
        bd = b['body']
        html.append('<div class="body">%s</div>' % lines_html(bd))
        css.append('.body{left:%gpx;top:%gpx;width:%gpx;font-size:%.3fpx;text-align:%s;%s}'
                   % (bd['x'], bd['y'], bd['w'], bd['fs'], bd['align'], anim('body')))
        anims.append(build_in('body', *T['body'], 'opacity:0;transform:translateY(10px)', 'opacity:1;transform:none'))

    # CTA
    if 'cta' in b:
        c = b['cta']
        html.append('<div class="cta">Learn More</div>')
        css.append('.cta{left:%gpx;top:%gpx;width:%gpx;height:%gpx;line-height:%gpx;font-size:%.3fpx;%s}'
                   % (c['x'], c['y'], c['w'], c['h'], c['h'], c['fs'], anim('cta')))
        anims.append(build_in('cta', *T['cta'], 'opacity:0;transform:scale(.85)', 'opacity:1;transform:none'))

    page = TEMPLATE.format(W=W, H=H, css='\n'.join(css), anims='\n'.join(anims), html='\n'.join(html),
                           title=b['title'], navy=NAVY, din_lh=DIN_LH, din_top=DIN_TOP)
    open(os.path.join(d, 'index.html'), 'w').write(page)
    shutil.copy(os.path.join(ASSETS, 'pfd700.woff2'), d)
    if not single:
        shutil.copy(os.path.join(ASSETS, 'dinot400.woff2'), d)
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
@font-face{{font-family:"DIN OT";font-weight:400;font-style:normal;src:url(dinot400.woff2) format("woff2");font-display:block}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#fff}}
#ad{{position:relative;display:block;width:{W}px;height:{H}px;overflow:hidden;background:#fff;cursor:pointer;text-decoration:none;
-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;text-rendering:geometricPrecision}}
#ad>*{{position:absolute;display:block}}
.bg{{left:0;top:0}}
.head{{font-family:"Playfair Display",Georgia,serif;font-weight:700;line-height:1.3333;color:#fff;white-space:nowrap}}
.body{{font-family:"DIN OT",Arial,sans-serif;font-weight:400;line-height:{din_lh};padding-top:{din_top}em;color:#fff;white-space:nowrap}}
#ad .head span,#ad .body span{{display:block;position:relative}}
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
// Hold the animation until the web fonts are ready so text never flashes in a fallback face.
(function(){{var r=document.documentElement;r.className='paused';
var go=function(){{r.className='';}};
if(document.fonts&&document.fonts.load){{Promise.all([document.fonts.load('700 20px "Playfair Display"'),document.fonts.load('400 20px "DIN OT"')]).then(go,go);setTimeout(go,1500);}}else go();}})();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for b in spec['BANNERS']:
        print(build(b))
