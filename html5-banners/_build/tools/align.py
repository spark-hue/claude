# usage: align.py <qa_dir> <figma2x_dir>  -> per-line (dx,dy) offsets in CSS px that best match Figma's render
import json, sys, os
import numpy as np
from PIL import Image
qa, fg = sys.argv[1:3]
info = json.load(open(os.path.join(qa, 'lines.json')))
FIG = {'160x600': ('150x600', -5)}  # size -> (figma frame, css x offset of figma relative to live)
res = {}
for size, blocks in sorted(info.items()):
    fname, xo = FIG.get(size, (size, 0))
    live = np.asarray(Image.open(os.path.join(qa, size + '_text.png')).convert('RGBA'))[:, :, 3].astype(float) / 255
    f = np.asarray(Image.open(os.path.join(fg, fname + '.png')).convert('RGB')).astype(float)
    white = np.clip((f.min(axis=2) - 120) / 135, 0, 1)  # white text on navy
    fw = white.shape[1]
    res[size] = {}
    for blk, lines in blocks.items():
        out = []
        for (l, t, r, b) in lines:
            y0, y1, x0, x1 = int(t * 2) - 2, int(b * 2) + 2, int(l * 2) - 2, int(r * 2) + 2
            m = live[y0:y1, x0:x1]
            best = None
            for dy in range(-12, 13):
                for dx in range(-6, 7):
                    fx0 = x0 + dx + xo * 2
                    if fx0 < 0 or fx0 + m.shape[1] > fw or y0 + dy < 0: continue
                    w = white[y0 + dy:y1 + dy, fx0:fx0 + m.shape[1]]
                    if w.shape != m.shape: continue
                    sc = (m * w).sum() - 0.5 * (m * (1 - w)).sum()
                    if best is None or sc > best[0]: best = (sc, dx, dy, (m * w).sum() / max(m.sum(), 1))
            out.append((best[1] / 2, best[2] / 2, round(best[3], 3)))
        res[size][blk] = out
        print(size, blk, [(dx, dy) for dx, dy, _ in out], 'match', [c for _, _, c in out])
json.dump(res, open(os.path.join(qa, 'align.json'), 'w'))
