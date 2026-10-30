# usage: overlap.py spec.py qa_dir  -> counts text/logo pixels sitting on real (alpha) photo pixels
import sys, os
from PIL import Image, ImageChops
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec={}; exec(open(sys.argv[1]).read(), spec)
for b in spec['BANNERS']:
    if 'photo' not in b: continue
    p=b['photo']; W,H=b['w'],b['h']
    src=Image.open(os.path.join(S,'assets','photos',p['src'])).split()[3].resize((round(p['w']),round(p['h'])),Image.LANCZOS)
    mask=Image.new('L',(W,H),0); mask.paste(src,(round(p['x']),round(p['y'])))
    mask=mask.point(lambda v:255 if v>40 else 0)
    t=Image.open(os.path.join(sys.argv[2],b['name']+'_m_text.png')).split()[3].point(lambda v:255 if v>40 else 0)
    hit=ImageChops.multiply(mask,t); n=sum(1 for v in hit.get_flattened_data() if v)
    print(b['name'],'text/logo pixels on photo:',n, hit.getbbox())
