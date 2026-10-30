# Reads the Figma file JSON and writes manifest.json: one entry per banner frame with its output path and
# layers (Figma node ids) tagged with an animation role.
# usage: python3 manifest.py <file.json> <manifest.json>
import json, re, sys
from collections import Counter

SKIP_SECTION = re.compile(r'META|Social|components', re.I)
SIZES = {'970x250', '300x600', '336x280', '728x90', '300x250', '300x50', '320x50', '150x600', '1024x768', '768x1024'}

# Section ids whose program / funnel can't be read from the section names
PROGRAM_BY_SECTION = {'1:20734': 'M.A. Industrial Organizational Psychology', '1:20938': 'M.A. Industrial Organizational Psychology',
                      '1:21137': 'M.A. Industrial Organizational Psychology'}
FUNNEL_BY_SECTION = {'1:4497': 'MOFU 2', '1:13025': 'BOFU'}
PROGRAM_RENAME = {'OTD': 'OTD', 'Fall October': 'FY27 Fall October', 'FY27 Fall Start': 'FY27 Fall Start',
                  'TOFU Applied Clinical Psychology Licensure': 'Applied Clinical Psychology Licensure'}


def walk(n, pred):
    if n.get('visible', True) is False:
        return
    if pred(n):
        yield n
    for c in n.get('children', []):
        yield from walk(c, pred)


def texts(n):
    return list(walk(n, lambda x: x['type'] == 'TEXT'))


def has_image(n):
    return any(True for _ in walk(n, lambda x: any(f.get('type') == 'IMAGE' and f.get('visible', True) for f in x.get('fills', []))))


def white_fill(n):
    return any(f.get('type') == 'SOLID' and f.get('visible', True) and min(f['color'][k] for k in 'rgb') > 0.95 for f in n.get('fills', []))


def solid_fill(n):
    return any(f.get('type') == 'SOLID' and f.get('visible', True) for f in n.get('fills', []))


def visible_box(n):
    """Bounds of what a node actually draws: a mask child clips the siblings after it (x0, y0, x1, y1)."""
    kids = [c for c in n.get('children', []) if c.get('visible', True)]
    if not kids:
        b = n['absoluteBoundingBox']
        return [b['x'], b['y'], b['x'] + b['width'], b['y'] + b['height']]
    box, mask = None, None
    for c in kids:
        if c.get('isMask'):
            mask = visible_box(c)
            continue
        v = visible_box(c)
        if mask:
            v = [max(v[0], mask[0]), max(v[1], mask[1]), min(v[2], mask[2]), min(v[3], mask[3])]
            if v[2] <= v[0] or v[3] <= v[1]:
                continue
        box = v if box is None else [min(box[0], v[0]), min(box[1], v[1]), max(box[2], v[2]), max(box[3], v[3])]
    return box or [0, 0, 0, 0]


def classify(frame):
    fb = frame['absoluteBoundingBox']
    W, H = round(fb['width']), round(fb['height'])
    layers = []
    for c in frame.get('children', []):
        if c.get('visible', True) is False or c.get('opacity', 1) == 0:
            continue
        b = c['absoluteBoundingBox']
        x, y, w, h = b['x'] - fb['x'], b['y'] - fb['y'], b['width'], b['height']
        if x >= W or y >= H or x + w <= 0 or y + h <= 0:
            continue  # parked off the artboard
        L = dict(id=c['id'], name=c['name'], x=x, y=y, w=w, h=h)
        if has_image(c):  # Figma's PNG export covers the visibly drawn area (mask applied, frame not)
            v = visible_box(c)
            L['v'] = [v[0] - fb['x'], v[1] - fb['y'], v[2] - v[0], v[3] - v[1]]
        rb = c.get('absoluteRenderBounds')
        if rb:  # Figma sizes exports to the rendered bounds, which can overrun the box (e.g. text wider than its component)
            L['r'] = [rb['x'] - fb['x'], rb['y'] - fb['y'], rb['width'], rb['height']]
        tx = texts(c)
        names = ' '.join(n['name'] for n in walk(c, lambda _: True))
        if tx:
            fams = {t['style']['fontFamily'] for t in tx}
            L['text'] = ' '.join(t['characters'].strip() for t in tx)
            rect = any(n['type'] == 'RECTANGLE' and solid_fill(n) for n in walk(c, lambda _: True))
            if re.search(r'\bcta\b', c['name'], re.I) or (rect and len(tx) == 1 and len(L['text']) <= 30):
                L['role'] = 'cta'
            elif 'Playfair Display' in fams and 'DIN OT' not in fams:
                L['role'] = 'head'
                L['fs'] = max(t['style']['fontSize'] for t in tx)
            else:
                L['role'] = 'din'
        elif c['type'] in ('VECTOR', 'RECTANGLE', 'BOOLEAN_OPERATION') and solid_fill(c) and not white_fill(c) and w * h > 0.5 * W * H:
            L['role'] = 'bg'
        elif re.search(r'logo', names, re.I) or (white_fill(c) and 3.8 < w / max(h, .01) < 5.8 and not has_image(c)) \
                or (c['type'] == 'GROUP' and not has_image(c) and y < H * 0.3 and 3.8 < w / max(h, .01) < 5.8):
            L['role'] = 'logo'
        elif has_image(c):
            L['role'] = 'photo'
        else:
            L['role'] = 'extra'
        L['kind'] = 'png' if has_image(c) else 'svg'
        layers.append(L)

    # one headline (largest Playfair), any other Playfair blocks travel with it; first DIN block is the body
    heads = sorted([l for l in layers if l['role'] == 'head'], key=lambda l: -l['fs'])
    for l in heads[1:]:
        l['role'] = 'head2'
    dins = sorted([l for l in layers if l['role'] == 'din'], key=lambda l: (l['y'], l['x']))
    for i, l in enumerate(dins):
        l['role'] = 'body' if i == 0 else 'extra'
    logos = [l for l in layers if l['role'] == 'logo']
    for l in logos[1:]:
        l['role'] = 'extra'
    return W, H, layers


def clean_program(name):
    n = re.sub(r'\((Text [AB])\)|\bText [AB]\b|\b(TOFU|MOFU|BOFU|TOF|MOF|BOF)\b|\bBanners\b|\bFY 27\b', ' ', name)
    n = re.sub(r'\s+', ' ', n).strip(' -/')
    return n


def meta(path_names, path_ids):
    joined = ' '.join(path_names)
    funnel = None
    for sid in path_ids:
        funnel = FUNNEL_BY_SECTION.get(sid, funnel)
    if not funnel:
        m = re.search(r'\b(TOFU|MOFU|BOFU|TOF|MOF|BOF)\b', joined)
        funnel = {'TOF': 'TOFU', 'MOF': 'MOFU', 'BOF': 'BOFU'}.get(m.group(1), m.group(1)) if m else None
    text = re.search(r'Text ([AB])', joined)
    program = None
    for sid in path_ids:
        program = PROGRAM_BY_SECTION.get(sid, program)
    if not program:
        program = clean_program(path_names[0])
        program = PROGRAM_RENAME.get(program, program)
    return program, funnel, ('Text ' + text.group(1)) if text else None


def slug(s):
    s = s.replace('&', 'and').replace('.', '').replace(':', '').replace('(', '').replace(')', '')
    return re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-')


def main():
    d = json.load(open(sys.argv[1]))
    out = []
    for page in d['document']['children']:
        def sections(sec, names, ids):
            for c in sec.get('children', []):
                if c['type'] == 'SECTION':
                    if not SKIP_SECTION.search(c['name']):
                        yield from sections(c, names + [c['name']], ids + [c['id']])
                elif c['type'] in ('FRAME', 'COMPONENT', 'INSTANCE'):
                    yield names, ids, c
        for names, ids, f in sections(page, [], []):
            W, H, layers = classify(f)
            if '%dx%d' % (W, H) not in SIZES:
                continue
            program, funnel, text = meta(names, ids)
            ow = 160 if (W, H) == (150, 600) else W
            folder = funnel + (' (%s)' % text if text else '')
            base = 'TCS_%s_%s%s_%dx%d' % (slug(program), funnel.replace(' ', ''), '_' + text.replace(' ', '-') if text else '', ow, H)
            out.append(dict(id=f['id'], page=page['name'], program=program, funnel=funnel, variant=text, section=names,
                            folder='%s/%s/%s' % (page['name'], program.replace(':', ''), folder), name=base,
                            W=W, H=H, OW=ow, bg=f.get('backgroundColor'), layers=layers))
    # same program/funnel/size more than once (e.g. two 300x50 versions): number the later ones
    seen = Counter()
    for b in out:
        k = (b['folder'], b['name'])
        seen[k] += 1
        if seen[k] > 1:
            b['name'] += '_v%d' % seen[k]
    json.dump(out, open(sys.argv[2], 'w'), indent=1)
    print(len(out), 'banners;', Counter(r for b in out for r in [l['role'] for l in b['layers']]))
    roles = Counter(tuple(sorted(Counter(l['role'] for l in b['layers']).items())) for b in out)
    for k, v in roles.most_common():
        print(v, k)


main()
