# HTML5 banner build

Source: Figma `kf0eIQHtVt2kHCWCHBXUHb` (HTML5-TCS).

- `vec.json`: background shapes and the horizontal logo (SVG) exported from Figma.
- `assets/photos`: photo groups exported from Figma at 2x (named by node id). Figma's export flattens onto white, so the
  alpha comes from the clip-path mask SVGs in `assets/masks` (rasterized by `tools/masks.js`).
- Fonts: Playfair Display Bold (OFL, subset) and DIN OT Regular (client-supplied, subset).
- Text is live. Line breaks come from Figma; `align_<set>.json` holds per-line pixel offsets measured against
  Figma's 2x render of each frame (Figma snaps each line to the pixel grid).
- Animations loop forever (8s): logo intro -> zoom out -> core message -> supporting message -> CTA, soft fade, repeat.

    python3 tools/build.py tools/spec_<set>.py out/ [tools/align_<set>.json]
    node tools/textmask.js out/ qa/ && python3 tools/align.py qa/ figma2x/   # measure line offsets vs Figma 2x frame renders
    DSF=2 node tools/render.js out/<banner> qa/<banner>                       # QA: off-frame, line collisions, end frame
    python3 tools/overlap.py tools/spec_<set>.py qa/                          # text/logo on photo pixel check

Zip from inside each banner folder (`cd out/<banner> && zip -X -9 ../<banner>.zip *`) so the files sit at the root of the zip.

## Batch build (all sets, Figma REST API)

`batch/` builds every banner frame in the file straight from the Figma API (needs the api.figma.com token).
Each layer is Figma's own export placed at its Figma position: background, logo, text and CTA as SVG (glyph
outlines, so copy and line breaks match Figma exactly), photos as JPG flattened onto the background (or PNG
where they overlap other layers). Same 8s loop as the first set: logo intro -> zoom out -> photo -> headline ->
body / bullets -> CTA -> fade, repeat. 150x600 frames are delivered as 160x600 (background widened,
full-width photos scaled, everything else centred).

    curl -sS https://api.figma.com/v1/files/kf0eIQHtVt2kHCWCHBXUHb -o full.json
    python3 batch/manifest.py full.json manifest.json         # frames -> output names + layer roles
    python3 batch/export.py manifest.json cache                # bulk SVG/PNG exports + 2x frame renders (resumable)
    python3 batch/build.py manifest.json cache out ..          # banner folders + zips under html5-banners/<page>/<program>/<funnel>/
    node batch/qa.js manifest.json out qa && python3 batch/compare.py manifest.json cache qa   # end frame vs Figma render

`build.py` skips `Approved Not Live/M.A. Applied Psychology/TOFU` (the approved live-text set built with `tools/`).
