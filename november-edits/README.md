# November edits

Built on the team's **November Edits / NOVEMBER-mad-for-chicken** code (Drive), not on the Oct 28 package.

Changed vs. that folder:
* `assets/cut-drumsticks.png`, `cut-thighs.png`, `cut-tenders.png`: new single-piece cut-outs (from Images/), resized for the web (≈0.4–0.6 MB each). Vegetarian unchanged (no image yet).
* `parts/site.html`: cache keys on those three images only (`?v=202611111930`).
* `functions.php`: unchanged from the November folder (included because the build needs it).

Pending: the November hero video (`hero_NOVEMBEREDIT.mp4`, 37 MB, over the Drive connector's 10 MB limit).
`_build/hero.sh <video> <theme folder>` re-encodes it for the web, makes a matching poster and bumps both cache keys.
