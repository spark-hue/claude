# HTML5 banner build

Source: Figma `kf0eIQHtVt2kHCWCHBXUHb` (HTML5-TCS). Layer data was exported from Figma into `vec.json` (background shapes, logo) and `body.json` (DIN OT body copy as vector outlines). Photos are in `assets/photos` (2x, named by Figma node id).

    python3 tools/build.py tools/spec_<set>.py out/        # banner folders
    node tools/render.js out/<banner> qa/<banner> gif       # QA checks + 15fps frames
    python3 tools/overlap.py tools/spec_<set>.py qa/        # text/logo on photo pixel check
    python3 tools/gif.py qa/<banner>_frames <banner>.gif    # looping GIF

Zip from inside each banner folder (`cd out/<banner> && zip -X -9 ../<banner>.zip *`) so the files sit at the root of the zip.
