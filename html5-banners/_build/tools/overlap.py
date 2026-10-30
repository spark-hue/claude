# usage: overlap.py spec.py qa_dir  -> counts text/logo pixels sitting on real (alpha) photo pixels
import sys, os
from PIL import Image, ImageChops
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = {}; exec(open(sys.argv[1]).read(), spec)
for b in spec['BANNERS']:
    if 'photo' not in b: continue
    p = b['photo']
    t = Image.open(os.path.join(sys.argv[2], b['name'] + '_m_text.png')).split()[3].point(lambda v: 255 if v > 40 else 0)
    k = t.width / b['w']  # render scale
    src = Image.open(os.path.join(S, 'assets', 'photos', p['src'])).split()[3].resize((round(p['w'] * k), round(p['h'] * k)), Image.LANCZOS)
    mask = Image.new('L', t.size, 0); mask.paste(src, (round(p['x'] * k), round(p['y'] * k)))
    hit = ImageChops.multiply(mask.point(lambda v: 255 if v > 40 else 0), t)
    print(b['name'], 'text/logo pixels on photo:', sum(1 for v in hit.get_flattened_data() if v), hit.getbbox())
