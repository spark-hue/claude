# HTML5 banner batch: prompt for a new Claude Code session

Copy everything below the line into a new Claude Code session (claude.ai/code) on the `spark-hue/claude` repository.
Fill in the **[brackets]** first. Before you start, do the one-time setup in "Before you paste".

## Before you paste (one-time setup, about 5 minutes)

1. **Figma token.** In Figma: Settings › Security › Personal access tokens › create one with read-only access
   to file content. Copy it.
2. **Add it to the Claude Code cloud environment as a network secret, not in the chat.**
   At the top of a session, click the environment name › Edit › **Network secrets** (older versions:
   "API credentials").
   - Allowed websites: `api.figma.com`
   - Path prefixes: `/v1/` (or leave empty)
   - Header name: `X-Figma-Token`. Replace "Authorization", and leave the prefix empty (delete "Bearer").
   - Value: the token. Click **Add**, then save.
3. **Start a new session** after saving, because secrets only load when a session starts. Pick the
   `spark-hue/claude` repo.
4. Have ready: the Figma file link, which pages and sections to build, and any sets that are already
   approved and must not be rebuilt.

---

You're continuing an HTML5 display-banner production pipeline for The Chicago School. It already exists in
this repo, was used to deliver 1,152 banners from the Figma file `kf0eIQHtVt2kHCWCHBXUHb`, and the client
approved the output. Your job is to run the **same process on a new Figma file** and produce the same
deliverables. Don't redesign the approach; reuse the scripts and adapt only the file-specific settings.

## Inputs

- Figma file: **[paste Figma URL]** (the file key is the part after `/design/`)
- Pages and sections to build: **[e.g. all banner sections on pages "X" and "Y"]**
- Skip: any section whose name contains META, Social, or components (already the default), plus
  **[anything else]**
- Already approved sets, do not rebuild: **[none / list]**
- Deliver to: **[e.g. the "2026 HTML5 Banners" Google Drive folder; I will drag the bundles in myself]**

## Setup

1. Work on a new branch, created from `claude/zealous-pascal-2pyc4v`, which holds the pipeline:
   `git fetch origin claude/zealous-pascal-2pyc4v && git checkout -b <new-branch> origin/claude/zealous-pascal-2pyc4v`.
   Commit and push your work to that branch as you go, because the container is temporary.
2. Read `html5-banners/_build/README.md` (the "Batch build" section) and every script in
   `html5-banners/_build/batch/`: `manifest.py`, `export.py`, `build.py`, `qa.js`, `compare.py`, `backup.js`.
3. Check the token works:
   `curl -sS -o /dev/null -w '%{http_code}' "https://api.figma.com/v1/files/<KEY>?depth=1"` should print 200.
   If you get 403 or 404, stop and tell me; the network secret isn't set up (see "Before you paste").
4. Keep large intermediate files (the file JSON, the export cache, QA renders) in your scratchpad directory,
   not in the repo.

## Step 1: Pull the file and survey it

- `curl -sS https://api.figma.com/v1/files/<KEY> -o full.json`. One request returns the whole file tree.
- List every page › section › frame. Report the number of sets and banners per page, the frame sizes, and
  any sizes outside the standard 10 (970x250, 300x600, 336x280, 728x90, 300x250, 300x50, 320x50,
  150x600 or 160x600, 1024x768, 768x1024). Odd sizes like 387x225 were skipped last time; ask me before
  including any.
- Survey the layer structure of the frames: types of top-level children, fonts, and anything new compared
  with what `manifest.py` already classifies.

## Step 2: Manifest (`batch/manifest.py`)

`manifest.py` classifies each frame's top-level layers into animation roles and works out output names.

- **Roles:** `bg` (large solid vector), `logo` (white vector at a 3.8–5.8 aspect ratio, or anything named
  "logo"), `photo` (anything containing an image fill), `head` (largest Playfair text), `head2`, `body`
  (first DIN text block), `extra` (bullets, divider lines, other DIN blocks), `cta` (named "cta", or a
  rectangle plus one short text).
- Layers that are hidden, or parked fully outside the artboard, are skipped.
- Update the file-specific settings at the top: `PROGRAM_BY_SECTION`, `FUNNEL_BY_SECTION`, `PROGRAM_RENAME`
  (keyed by Figma section ids and names from the old file; replace them for the new file) and `SIZES`.
- **Naming** (keep it identical):
  - Folder: `<Page>/<Program>/<TOFU|MOFU|BOFU>[ (Text A|B)]/`
  - File: `TCS_<Program-slug>_<FUNNEL>[_Text-A]_<WxH>.zip`. The slug drops `.`, `:`, `(` and `)`, and
    turns spaces into `-`, e.g. "M.A. Applied Psychology" becomes `MA-Applied-Psychology`.
  - TOF/MOF/BOF map to TOFU/MOFU/BOFU.
  - A repeated program, funnel and size gets a `_v2` suffix.
  - 150x600 frames are named 160x600.
- Run it and print the role combinations per frame and the folder list. **Show me any section where the
  program or funnel name looks wrong or ambiguous before building.** Last time these needed a decision:
  - Two sections had the same name.
  - Sections were named only "TOFU (Text A)".
  - A "Banners" section had no funnel in its name.

## Step 3: Export from Figma (`batch/export.py`)

`FIGMA_FILE_KEY=<KEY> python3 batch/export.py manifest.json cache`

This bulk-exports, through the Figma images API:
- every vector, text and CTA layer as SVG (text comes out as outlined glyphs);
- photos as PNG at 2x (2.2x on 150x600 frames) and image logos at 4x;
- a 2x render of every whole frame, used for QA.

It caches, retries and resumes, so if a batch fails just rerun it until it says "0 to export". About 1,150
banners took around 30 minutes. Never use `sleep` to wait; run it in the background.

## Step 4: Build (`batch/build.py`)

`python3 batch/build.py manifest.json cache out ../..` (the last argument is the zip root, the
`html5-banners/` folder). Add every approved set to `SKIP_FOLDERS` first so it is never overwritten.

How it works. Keep all of this as-is; it's what the client approved:
- **Layers:** each layer is Figma's own export, placed at its Figma position.
  - Placement uses whichever box matches the export's size: the layer box, Figma's render bounds (text that
    overflows its component), or the masked visible box (clipped photo groups).
- **Text:** outlined SVG from Figma, not live fonts. The DIN OT and Playfair files we have are subsets
  missing glyphs (’ + |) and the DIN Medium and Italic weights. Outlines guarantee exact copy and line
  breaks.
- **Photos:** JPG flattened onto the background colour, with these rules:
  - If another layer underneath overlaps the photo but the photo is fully transparent there, the photo is
    moved down to sit just above the background.
  - Only if the photo truly overlaps other content does it stay a transparent PNG.
  - No CSS masks: Chrome blocks them for local files, and they're risky in ad servers.
- **150x600 → 160x600:** the background shape's right side is widened by 10px, full-width photos are
  scaled to the new width (kept anchored at the bottom), and everything else moves 5px right.
- **Animation:** an 8s loop, forever. Logo intro, centred and scaled up (0–0.6s), then it zooms to its spot
  (1.3–2.0s). Photo slides in (1.8–2.6s), then headline (2.2–2.9s), body (3.6–4.3s), extras (4.1–4.8s) and
  CTA (5.1–5.6s). Everything fades out at 7.6–8.0s. Units without body copy bring the headline in at
  2.0s. Playback waits for all images to load.
- **ClickTAG:** the whole banner is the click area. The clickTAG script block was copied verbatim from a
  coworker's working The Trade Desk creative. Don't change it: it reads `?clickTAG=`, then `?clickTag=`,
  then falls back to `https://www.thechicagoschool.edu/`. The link is
  `href="javascript:window.open(window.clickTAG);void(0);"` with **no** `target="_blank"`.
- **Zips:** each banner zip has its files at the root (index.html plus layers), made with
  `zip -X -9 ../<name>.zip *` from inside the folder.

## Step 5: QA (do not skip)

`node batch/qa.js manifest.json out qa && python3 batch/compare.py manifest.json cache qa`

- This renders every banner's end frame (t = 7.4s) at 2x and compares it pixel by pixel with Figma's render.
- **Expected noise:**
  - Up to about 2% "bad pixels" on most sizes, and up to about 10% on 300x50 and 320x50. These are
    sub-pixel anti-aliasing differences on small text.
  - Up to about 18% on 160x600, because the photo is scaled on purpose and only the original 150px is
    compared.
- **Real bugs found last time, so check for these patterns:**
  - Headlines shifted right and cropped: text wider than its component, fixed by render-bounds placement.
  - Photos 3px off: clip-mask export bounds, fixed by the visible-box calculation.
  - A photo's flattened corner painting over the logo, fixed by moving the photo down.
  - Missing photos: CSS masks, removed.
- **Look at the results yourself.** Build side-by-side sheets (live | Figma) of:
  - the worst 25 by score, leaving out 160x600, 300x50 and 320x50, which are expected to be noisy;
  - a random sample of 8–10 from the 1–5% range.
  Investigate anything that isn't sub-pixel noise.
- Also confirm: no broken images, every animation is infinite, and zip sizes (median about 70 KB last
  time; flag anything over about 400 KB).
- Render one banner at several time points (`tools/strip.js`) to check the animation sequence.

## Step 6: Static backup images

`node batch/backup.js <html5-banners dir> <tmp dir>` renders the end frame of every zip at 1x as
`<same name>.jpg`, aiming for 150 KB or less. Then **move** the JPGs into a separate tree
`static-backups/<Page>/<Program>/<Funnel>/` that mirrors the HTML5 folders; the user wants backups kept
separate from the HTML5 zips. Check that every JPG is exactly its banner's pixel size.

## Step 7: Deliver

- Commit the scripts, the zips under `html5-banners/` and the JPGs under `static-backups/`, then push.
- Make bundles in the scratchpad, one per Figma page for the HTML5 zips, plus one for the backups:
  `zip -r -0 TCS_HTML5_Banners_<Page>.zip "<Page>"` and `TCS_Static_Backups.zip`. Send them with the
  send-file tool so I can unzip once and drag the folders into Drive. (The Drive connector can't upload
  binaries in bulk, so don't try.)
- Report back:
  - counts per page;
  - QA numbers and anything you couldn't fix;
  - naming decisions you made;
  - sections skipped and why.

## Rules

- Don't rebuild or overwrite sets I list as approved.
- Ask me before including odd sizes, renaming programs beyond what the Figma names say, or changing the
  animation, clickTAG or text approach.
- Never paste or echo the Figma token. It's injected automatically for api.figma.com.
