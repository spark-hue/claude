# MFC website: Oct 28 mobile revisions

These are the revised files for the **WordPress Theme Oct 26** theme (`mad-for-chicken/`).
Every file here replaces the file at the same path in the theme. Files not listed here are unchanged.

```
mad-for-chicken/
  style.css                      version 1.0.3 -> 1.0.4
  parts/site.html                all layout / behaviour changes
  assets/*.jpg, assets/*.png     cooler colour grade + new cut-outs (list below)
```

The desktop layout is unchanged except for the notes marked *(also Desktop)*. All other
changes only apply at phone/tablet widths (999px and below, mostly 760px and below).

## Feedback → change

| # | Note | What changed |
|---|------|--------------|
| 1 | Hero video looks stretched on mobile | The full-height hero cropped the 16:9 film about 4×. On phones the hero now sits below the header and shows the film at a gentle crop (header + 92vw tall, full 16:9 on tablets). |
| 2 | Hero video doesn't autoplay; play button shows | Muted/inline playback is forced in JS and retried on load, first touch or scroll, and when the tab returns. The iOS play overlay is hidden, so a refused autoplay (for example Low Power Mode) shows the poster instead of a button. |
| 3 | Colour too yellow *(also Desktop)* | All food and lifestyle photos and cut-outs re-graded cooler (`_build/cool.py`: slight blue white balance plus less yellow saturation; reds/sauces kept). The hero video gets a soft cool tint layer. |
| 4 | Subway line animation missing on mobile | On phones/tablets the line now runs down the left margin from The Madness through each process step (a coloured stretch and a station per card) into the Made To Be Craved frame, drawing as you scroll. |
| 5 | ADA button *(also Desktop)* | Floating accessibility button (bottom-left) with larger text, high contrast, highlight links, pause motion, readable font, text spacing and reset. Choices are remembered per visitor. Also added: a skip-to-content link that shows on keyboard focus. It's included in the footer, so inner pages (Terms, Careers…) get it too. |
| 6 | "Order Now" unlabeled / out of proportion | On phones the header keeps just the logo and the menu button. "Order Now" becomes a labeled bottom CTA (Coqodaq-style) between the accessibility and back-to-top buttons, and steps aside while the "Get Mad. Order Now." section is on screen. |
| 7 | Hamburger instead of "Menu" | 3-line hamburger icon (X to close), with screen-reader labels. |
| 8 | Locations token blends into the sheet; add E / C / F | Every token in the menu sheet gets the white ring; Events **E**, Contact **C**, Franchise **F** tokens added. |
| 9.1 | Flip the process photos on scroll | On touch/small screens each card flips to its photo as it reaches the middle of the screen (tapping still works). |
| 9.2 | Photos off-centre / not filling | Photos now fill the card edge to edge, and the cards are taller on phones. |
| 9.3 | Clearer Served Hot photo *(also Desktop)* | `process-4.jpg` is now the tray shot of single glazed drumsticks and wings (shoot photo p22). |
| 10.1 | "Made To Be Craved" *(also Desktop)* | Capital T. |
| 11.1 | Each sauce pops up 3 photos | Bug fix: a tap fires hover, focus and click, and each one appended a photo while the image loaded. Now only one photo is ever shown. |
| 11.2 | Faint square behind sauce cut-outs *(also Desktop)* | The cut-out files are clean. The box comes from Safari drawing the CSS `drop-shadow` filter as a rectangle while the image animates. Replaced it with a soft shadow ellipse under the cup, with no filter. |
| 11.3 | Sauce bar should slide | When a line is wider than the screen, tapping a stop slides it to the front so the next stops come into view (Hickory BBQ → Buffalo / Blazin' Peach / Sweet & Spicy; Sweet & Spicy → Nashville Hot / Mango Habanero). Same on the Menu page. |
| 12.1 | Center "Get Mad. / Order Now." | Logo, headline and button centered; exactly two lines. |
| 13.1 | Single-piece cut-outs *(also Desktop)* | New single-piece **Wing** and **Drumstick** cut-outs (from the tray shot). Thighs, Tenders and Vegetarian are unchanged; we don't have single pieces of those yet (next quarterly shoot). |
| 13.2 | Swap the banners *(also Desktop)* | The band after The Specialties and the band after Kids are swapped; both re-graded. |
| 13.3 | Different sandwich cut-out | On mobile the Sandwiches cut-out is now the glazed crispy chicken sandwich (shoot photo p11, hand removed): `cut-sandwich-chicken.png`. Desktop keeps the current one. |
| 14.1 | Remove "What People Say" | Hidden on mobile. |
| 14.2 | Quote order *(also Desktop)* | Queens Post ("The first Korean…") first, NYC Tourism ("Fried to a shattering crunch") second. |
| 15.1 | Franchise photo *(also Desktop)* | Back to the previous photo (the brick storefront with the MAD FOR CHICKEN sign, `franchise-marquee.jpg`), cropped so the sign sits centered in the frame. |

## Also included

* **East Meadow hotfix:** the MyManager order link is removed until the Toast link is ready. East Meadow shows "Online ordering soon" (`_build/east_meadow.py`, run after `revise.py`).

## Still needed

* Single-piece cut-outs for **Thighs, Tenders and Vegetarian Chicken** (next shoot). Drop them in as
  `assets/cut-thighs.png`, `cut-tenders.png` and `cut-veg.png`; no code change needed.
* The hero **video file** wasn't re-encoded (it's over the Drive download limit for this tool), so it's
  cooled with a tint layer instead. A cooler, smaller mobile encode of `hero.mp4` would be better still.
* The ADA button covers common needs, but full ADA/WCAG compliance needs an audit
  (e.g. colour contrast on the red and spruce sections, form errors, and alt text across inner pages).

## Changed assets

Re-graded: `DSC6895.jpg DSC7127.jpg DSC7144.jpg DSC7209.jpg DSC7228.jpg craved.jpg process-1.jpg process-2.jpg
process-3.jpg franchise-storefront.jpg franchise-marquee.jpg chicken-cutout.png batterdrip.png cut-thighs.png
cut-tenders.png cut-veg.png cut-dumplings.png cut-sandwich.png`

New: `process-4.jpg` (Served Hot), `cut-wings.png`, `cut-drumsticks.png` (single pieces), `cut-sandwich-chicken.png` (mobile).

The asset cache key in `site.html` moves from `?v=202610231310` to `?v=202610281200`, so browsers pick up the new images.

## Rebuilding

`_build/revise.py` applies every page change to the Oct 26 `parts/site.html`, and checks that each edit
lands exactly once: `python3 _build/revise.py <oct26 site.html> <out site.html>`, then
`python3 _build/east_meadow.py <out site.html> <out site.html>`.
`_build/cool.py <in> <out>` applies the colour grade to one image.
