#!/usr/bin/env bash
# Build the complete, uploadable theme zip: Oct 26 theme + Oct 28 revisions + East Meadow hotfix.
# Usage: make_theme_zip.sh <oct26-theme-zip-or-folder> <out.zip>
set -euo pipefail
SRC=$1; OUT=$(realpath -m "$2")
HERE=$(cd "$(dirname "$0")/.." && pwd)          # oct-28-mobile-revisions/
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
if [[ -f $SRC ]]; then unzip -q "$SRC" -d "$T/in"; else cp -r "$SRC" "$T/in"; fi
BASE=$(dirname "$(find "$T/in" -name functions.php -path '*/mad-for-chicken*' | head -1)")
[[ -f $BASE/style.css && -f $BASE/assets/hero.mp4 ]] || { echo "Oct 26 theme not found / incomplete in $SRC"; exit 1; }
mkdir -p "$T/out" && cp -r "$BASE" "$T/out/mad-for-chicken"
rm -rf "$T/out/mad-for-chicken/__MACOSX"; find "$T/out" -name '.DS_Store' -delete
cp -r "$HERE/mad-for-chicken/." "$T/out/mad-for-chicken/"     # revised site.html, style.css, assets
grep -q 'Online ordering soon' "$T/out/mad-for-chicken/parts/site.html"
! grep -q '68cf2cd3eacacf55537e615c' "$T/out/mad-for-chicken/parts/site.html"
for f in "$T"/out/mad-for-chicken/*.php; do php -l "$f" >/dev/null; done
(cd "$T/out" && rm -f "$OUT" && zip -qr -X "$OUT" mad-for-chicken)
echo "built $OUT"; unzip -l "$OUT" | tail -1
