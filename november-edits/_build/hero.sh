#!/usr/bin/env bash
# Swap in a new hero video: web-size H.264 encode (muted, 1080p, fast start), a matching poster frame,
# and fresh cache keys for both in parts/site.html.
# Usage: hero.sh <new-video> <theme-folder (mad-for-chicken)>
set -euo pipefail
IN=$1; T=$2; KEY=$(date +%Y%m%d%H%M)
ffmpeg -loglevel error -y -i "$IN" -an -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p \
  -vf "scale='min(1920,iw)':-2" -movflags +faststart "$T/assets/hero.mp4"
ffmpeg -loglevel error -y -ss 1 -i "$T/assets/hero.mp4" -frames:v 1 -q:v 3 "$T/assets/hero-poster.jpg"
python3 -I - "$T/parts/site.html" "$KEY" <<'PY'
import re, sys
p, key = sys.argv[1], sys.argv[2]
s = open(p, encoding='utf-8').read()
for f in ('hero.mp4', 'hero-poster.jpg'):
    s, n = re.subn(r'assets/' + re.escape(f) + r'\?v=\d+', f'assets/{f}?v={key}', s)
    assert n == 1, (f, n)
open(p, 'w', encoding='utf-8').write(s)
PY
ls -la "$T/assets/hero.mp4" "$T/assets/hero-poster.jpg"
