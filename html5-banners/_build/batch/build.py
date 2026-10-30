# Builds the animated HTML5 banner folders (and zips) for every manifest entry from the cached Figma exports.
# usage: python3 build.py <manifest.json> <cache_dir> <out_dir> <zip_root> [filter-substring]
#
# Every layer is Figma's own export, placed at its Figma position: vectors and text as SVG (glyph outlines, so the
# copy matches Figma exactly), photos as JPG. 150x600 frames are delivered as 160x600: the background shape is
# widened 10px on its right side, full-width photos are scaled to the new width (anchored bottom-left), and
# everything else moves 5px right so it stays centred.
import json, os, re, shutil, subprocess, sys
import numpy as np
from PIL import Image

LOOP = 8.0      # seconds per loop; loops forever, like a GIF
OUT_FADE = 0.4  # everything fades back to the bare background before the loop restarts
NUM = re.compile(r'-?\d*\.\d+(?:e-?\d+)?|-?\d+')

man_path, CACHE, OUT, ZIPS = sys.argv[1:5]
FILTER = sys.argv[5] if len(sys.argv) > 5 else ''
# Already delivered and approved with live text; leave those zips alone.
SKIP_FOLDERS = {'Approved Not Live/M.A. Applied Psychology/TOFU'}


def fname(i):
    return i.replace(':', '-').replace(';', '_')


def svg_min(s):
    s = re.sub(r'>\s+<', '><', s.strip())
    return re.sub(r'(\d+\.\d{2})\d+', r'\1', s)  # 0.01px is plenty


def widen_bg(svg, x0, add):
    """Push every x coordinate right of the frame centre (75px) outward by `add`px (150 -> 160 wide)."""
    def path(m):
        out, cmd, idx = [], None, 0
        for t in re.findall(r'[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?', m.group(1)):
            if t.isalpha():
                cmd, idx = t, 0
                out.append(t)
                continue
            v = float(t)
            if ((cmd in 'MLCQST' and idx % 2 == 0) or cmd == 'H') and v + x0 > 75:
                v += add
            idx += 1
            out.append('%g' % v)
        return 'd="%s"' % ' '.join(out)
    svg = re.sub(r'd="([^"]+)"', path, svg)
    w = float(re.search(r'width="([\d.]+)"', svg).group(1))
    vb = re.search(r'viewBox="([\d.\- ]+)"', svg).group(1).split()
    svg = svg.replace('width="%s"' % re.search(r'width="([\d.]+)"', svg).group(1), 'width="%g"' % (w + add), 1)
    return svg.replace('viewBox="%s"' % ' '.join(vb), 'viewBox="%s %s %g %s"' % (vb[0], vb[1], float(vb[2]) + add, vb[3]), 1)


def keyframes(name, frames):
    rows = ['%.2f%%{%s}' % (min(100, t / LOOP * 100), css) for t, css in frames]
    return '@keyframes %s{%s}' % (name, ''.join(rows))


def build_in(name, t0, t1, hidden, shown):
    end = LOOP - OUT_FADE
    return keyframes(name, [(0, hidden), (t0, hidden + ';animation-timing-function:cubic-bezier(.2,.6,.3,1)'),
                            (t1, shown), (end, shown), (LOOP, 'opacity:0;transform:none')])


def backdrop_colour(frame_png, x, y, w, h, alpha, k):
    """Colour behind a photo's transparent pixels in Figma's frame render, if it is one flat colour."""
    fr = np.asarray(frame_png.convert('RGB')).astype(int)
    a = np.asarray(alpha.resize((max(1, round(w * 2)), max(1, round(h * 2))))) if k != 2 else np.asarray(alpha)
    X, Y = round(x * 2), round(y * 2)
    hh, ww = a.shape
    ys, xs = np.nonzero(a == 0)
    ys, xs = ys + Y, xs + X
    ok = (ys >= 0) & (xs >= 0) & (ys < fr.shape[0]) & (xs < fr.shape[1])
    if ok.sum() == 0:
        return None
    px = fr[ys[ok], xs[ok]]
    med = np.median(px, axis=0)
    if (np.abs(px - med).max(axis=1) <= 10).mean() > 0.995:
        return tuple(int(v) for v in med)
    return False


def build(b):
    W, H, OW = b['W'], b['H'], b['OW']
    widen = OW - W
    d = os.path.join(OUT, b['folder'], b['name'])
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    frame_png = Image.open(os.path.join(CACHE, 'frame', fname(b['id']) + '.png'))
    roles = {l['role'] for l in b['layers']}
    has_body = bool(roles & {'body', 'extra'})

    T = dict(logo_in=(0.0, 0.6), logo_move=(1.3, 2.0), photo=(1.8, 2.6), head=(2.2, 2.9),
             body=(3.6, 4.3), extra=(4.1, 4.8), cta=(5.1, 5.6))
    if not has_body:
        T.update(head=(2.0, 2.7), cta=(3.4, 3.9))
    if 'body' not in roles:
        T['extra'] = T['body']
    hidden = dict(photo='opacity:0;transform:translateX(-24px)', head='opacity:0;transform:translateY(10px)',
                  body='opacity:0;transform:translateY(10px)', extra='opacity:0;transform:translateY(8px)',
                  cta='opacity:0;transform:scale(.85)')
    hidden['head2'] = hidden['head']
    T['head2'] = T['head']

    css, html, anims, used = [], [], [], set()
    for n, l in enumerate(b['layers']):
        role, x, y = l['role'], l['x'], l['y']
        cls = 'l%d' % n
        if l['kind'] == 'svg':
            svg = open(os.path.join(CACHE, 'svg', fname(l['id']) + '.svg')).read()
            if role == 'bg' and widen:
                svg = widen_bg(svg, x, widen)
            elif widen:
                x += widen / 2
            svg = svg_min(svg)
            w = float(re.search(r'width="([\d.]+)"', svg).group(1))
            h = float(re.search(r'height="([\d.]+)"', svg).group(1))
            src = '%s.svg' % cls
            open(os.path.join(d, src), 'w').write(svg)
        else:
            k = 4 if role == 'logo' else (2.2 if W == 150 else 2)
            im = Image.open(os.path.join(CACHE, 'png%g' % k, fname(l['id']) + '.png')).convert('RGBA')
            w, h = im.width / k, im.height / k
            fx, fy = x, y
            if widen and role == 'photo' and x <= 2 and x + w >= W - 2:
                s = OW / W  # full-width photo: scale to the wider frame, keep the bottom edge where it was
                y, w, h = y + h - h * s, w * s, h * s
                x = x * s
            elif widen:
                x += widen / 2
            if role == 'logo':
                src = '%s.png' % cls
                tw = round(w * 4)
                im.resize((tw, round(tw * im.height / im.width)), Image.LANCZOS).save(os.path.join(d, src), optimize=True)
            else:
                alpha = im.split()[3]
                lo = alpha.getextrema()[0]
                bgc = (255, 255, 255) if lo == 255 else backdrop_colour(frame_png, fx, fy, im.width / k, im.height / k, alpha, k)
                if bgc:  # flatten onto the flat colour it sits on -> plain JPG
                    flat = Image.new('RGB', im.size, bgc)
                    flat.paste(im, mask=alpha)
                    src = '%s.jpg' % cls
                    flat.save(os.path.join(d, src), quality=82, subsampling=0, optimize=True, progressive=True)
                else:    # sits over mixed content: JPG plus an alpha mask
                    src = '%s.jpg' % cls
                    flat = Image.new('RGB', im.size, (0, 0, 0))
                    flat.paste(im, mask=alpha)
                    flat.save(os.path.join(d, src), quality=82, subsampling=0, optimize=True, progressive=True)
                    m = Image.new('LA', im.size, (0, 0))
                    m.putalpha(alpha)
                    m.save(os.path.join(d, '%sm.png' % cls), optimize=True)
                    css.append('.%s{-webkit-mask-image:url(%sm.png);mask-image:url(%sm.png);'
                               '-webkit-mask-size:100%% 100%%;mask-size:100%% 100%%}' % (cls, cls, cls))
        html.append('<img class="%s" src="%s" alt="">' % (cls, src))
        geo = 'left:%.2fpx;top:%.2fpx;width:%.2fpx;height:%.2fpx' % (x, y, w, h)

        if role == 'bg':
            css.append('.%s{%s}' % (cls, geo))
        elif role == 'logo':
            s = max(min(0.62 * OW / w, 0.62 * H / h, 2.6), 1.0)
            s = min(s, 0.9 * OW / w, 0.85 * H / h) if s > 1 else s
            start = 'transform:translate(%.2fpx,%.2fpx) scale(%.3f)' % (OW / 2 - (x + w / 2), H / 2 - (y + h / 2), s)
            ease = ';animation-timing-function:cubic-bezier(.6,0,.2,1)'
            css.append('.%s{%s;animation:%s %gs linear infinite both}' % (cls, geo, cls, LOOP))
            anims.append(keyframes(cls, [
                (0, 'opacity:0;' + start + ';animation-timing-function:ease-out'), (T['logo_in'][1], 'opacity:1;' + start + ease),
                (T['logo_move'][0], 'opacity:1;' + start + ease), (T['logo_move'][1], 'opacity:1;transform:none'),
                (LOOP - OUT_FADE, 'opacity:1;transform:none'), (LOOP, 'opacity:0;transform:none')]))
        else:
            r = role if role in T else 'extra'
            css.append('.%s{%s;animation:a_%s %gs linear infinite both}' % (cls, geo, r, LOOP))
            if r not in used:
                used.add(r)
                anims.append(build_in('a_' + r, *T[r], hidden[r], 'opacity:1;transform:none'))

    head = next(l for l in b['layers'] if l['role'] == 'head')['text']
    cta = next((l['text'] for l in b['layers'] if l['role'] == 'cta'), 'Learn More')
    label = ('The Chicago School: %s - %s' % (head, cta)).replace('"', '&quot;')
    page = TEMPLATE.format(W=OW, H=H, css='\n'.join(css), anims='\n'.join(anims), html='\n'.join(html),
                           title='The Chicago School %dx%d' % (OW, H), label=label,
                           bgc=fmt_colour(b.get('bg'))).replace('@@CLICKTAG@@', CLICKTAG)
    open(os.path.join(d, 'index.html'), 'w').write(page)
    os.makedirs(os.path.join(ZIPS, b['folder']), exist_ok=True)
    z = os.path.abspath(os.path.join(ZIPS, b['folder'], b['name'] + '.zip'))
    if os.path.exists(z):
        os.remove(z)
    subprocess.run('zip -q -X -9 "%s" *' % z, shell=True, cwd=d, check=True)
    return d


def fmt_colour(c):
    if not c:
        return '#fff'
    return '#%02x%02x%02x' % tuple(round(c[k] * 255) for k in 'rgb')


# Ad-server clickTAG, taken verbatim from the coworker's working The Trade Desk banner.
CLICKTAG = r"""<script type="text/javascript">
  // The Trade Desk clickTAG (case-sensitive). TTD appends ?clickTAG=... to the creative URL;
  // if it is absent (local preview) we fall back to the default landing page below.
  function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  }
  var clickTAG = getParameterByName("clickTAG") || getParameterByName("clickTag") || "https://www.thechicagoschool.edu/";
</script>"""

TEMPLATE = '''<!DOCTYPE html>
<html lang="en" class="paused">
<head>
<meta charset="utf-8">
<meta name="ad.size" content="width={W},height={H}">
<meta name="viewport" content="width={W},height={H}">
<title>{title}</title>
@@CLICKTAG@@
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#fff}}
#ad{{position:relative;display:block;width:{W}px;height:{H}px;overflow:hidden;background:{bgc};cursor:pointer;text-decoration:none}}
#ad>img{{position:absolute;display:block;border:0;max-width:none}}
{css}
.paused #ad *{{animation-play-state:paused!important}}
{anims}
</style>
</head>
<body>
<a id="ad" href="javascript:window.open(window.clickTAG);void(0);" aria-label="{label}">
{html}
</a>
<script>
// Hold the animation until every layer image has loaded so nothing pops in late.
(function(){{var r=document.documentElement,go=function(){{r.className='';}};
if(document.readyState==='complete')go();else{{window.addEventListener('load',go);setTimeout(go,2500);}}}})();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    man = [b for b in json.load(open(man_path)) if b['folder'] not in SKIP_FOLDERS and FILTER in b['folder'] + '/' + b['name']]
    for b in man:
        print(build(b), flush=True)
