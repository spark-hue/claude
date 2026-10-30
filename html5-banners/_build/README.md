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
