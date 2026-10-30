# Scores each built banner's end frame against Figma's 2x render of the same frame.
# usage: python3 compare.py <manifest.json> <cache_dir> <qa_dir> [filter]
# Writes <qa>/scores.json; prints the worst matches. 160x600 builds are compared over the original 150px
# (live x 5..155 vs Figma 0..150), since the extra 10px has no Figma counterpart.
import json, os, sys
import numpy as np
from PIL import Image

man, cache, qa = sys.argv[1:4]
flt = sys.argv[4] if len(sys.argv) > 4 else ''
info = json.load(open(os.path.join(qa, 'qa.json')))
scores = {}
for b in json.load(open(man)):
    if (b['folder'] + '/' + b['name']).find(flt) < 0 or b['id'] not in info:
        continue
    f = b['id'].replace(':', '-')
    live = np.asarray(Image.open(os.path.join(qa, f + '.png')).convert('RGB')).astype(int)
    fig = np.asarray(Image.open(os.path.join(cache, 'frame', f + '.png')).convert('RGB')).astype(int)
    if b['OW'] != b['W']:
        live = live[:, 10:310]
    h, w = min(live.shape[0], fig.shape[0]), min(live.shape[1], fig.shape[1])
    diff = np.abs(live[:h, :w] - fig[:h, :w]).max(axis=2)
    bad = diff > 48
    scores[b['id']] = dict(name=b['name'], folder=b['folder'], mean=round(float(diff.mean()), 2), bad=round(float(bad.mean()) * 100, 3),
                           iterations=info[b['id']]['iterations'], broken=info[b['id']]['broken'])
json.dump(scores, open(os.path.join(qa, 'scores.json'), 'w'), indent=1)
worst = sorted(scores.items(), key=lambda kv: -kv[1]['bad'])
for k, s in worst[:25]:
    print('%-8s bad=%6.3f%% mean=%5.2f %s/%s %s' % (k, s['bad'], s['mean'], s['folder'], s['name'], '' if s['iterations'] == ['Infinity'] or s['iterations'] == [None] else s['iterations']))
print('banners:', len(scores), ' >1%% bad px:', sum(s['bad'] > 1 for s in scores.values()),
      ' broken images:', sum(bool(s['broken']) for s in scores.values()))
