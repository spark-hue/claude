# Bulk-exports every layer the manifest needs from the Figma images API, plus a 2x render of each frame for QA.
# usage: python3 export.py <manifest.json> <cache_dir>
#   cache/svg/<id>.svg        vector layers and text (Figma outlines the glyphs)
#   cache/png<scale>/<id>.png  photo groups (2x; 2.2x on 150x600 frames, which are widened to 160) and image logos (4x)
#   cache/frame/<id>.png       the whole frame at 2x, the reference the build is checked against
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

KEY = 'kf0eIQHtVt2kHCWCHBXUHb'
API = 'https://api.figma.com/v1/images/' + KEY


def fname(i):
    return i.replace(':', '-').replace(';', '_')


def get(url, tries=6):
    for t in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or t == tries - 1:
                raise
            wait = int(e.headers.get('Retry-After') or 0) or 2 ** (t + 2)
            print('  HTTP %d, retry in %ds' % (e.code, wait), flush=True)
            time.sleep(min(wait, 120))
        except (urllib.error.URLError, TimeoutError):
            if t == tries - 1:
                raise
            time.sleep(2 ** (t + 1))


def export(ids, fmt, scale, out_dir, batch):
    os.makedirs(out_dir, exist_ok=True)
    todo = [i for i in sorted(set(ids)) if not os.path.exists(os.path.join(out_dir, fname(i) + '.' + fmt))]
    print('%s x%s -> %s: %d to export' % (fmt, scale, out_dir, len(todo)), flush=True)

    def one(chunk):
        q = '%s?ids=%s&format=%s' % (API, ','.join(urllib.request.quote(i, safe=':;') for i in chunk), fmt)
        if fmt == 'png':
            q += '&scale=%g' % scale
        res = json.loads(get(q))
        if res.get('err'):
            raise RuntimeError(res['err'])
        for i, u in res['images'].items():
            if not u:
                print('  no render for', i)
                continue
            data = get(u)
            p = os.path.join(out_dir, fname(i) + '.' + fmt)
            open(p + '.tmp', 'wb').write(data)
            os.replace(p + '.tmp', p)
        return len(chunk)

    chunks = [todo[k:k + batch] for k in range(0, len(todo), batch)]
    done = 0
    with ThreadPoolExecutor(4) as ex:
        for n in ex.map(one, chunks):
            done += n
            print('  %d/%d' % (done, len(todo)), flush=True)


if __name__ == '__main__':
    man = json.load(open(sys.argv[1]))
    cache = sys.argv[2]
    svg, png = [], {}
    for b in man:
        for l in b['layers']:
            if l['kind'] == 'svg':
                svg.append(l['id'])
            else:
                s = 4 if l['role'] == 'logo' else (2.2 if b['W'] == 150 else 2)
                png.setdefault(s, []).append(l['id'])
    export(svg, 'svg', 1, os.path.join(cache, 'svg'), 60)
    for s, ids in sorted(png.items()):
        export(ids, 'png', s, os.path.join(cache, 'png%g' % s), 15)
    export([b['id'] for b in man], 'png', 2, os.path.join(cache, 'frame'), 15)
