# Hotfix: East Meadow online ordering

Stops MyManager orders routing to East Meadow until its Toast link is ready.

`mad-for-chicken/parts/site.html` is the **Oct 26 (live) theme** with only this fix. Replace the file at the same path on the server; nothing else changes.

The MyManager link (`mfc.mymanager.com/online-shop/68cf2cd3…`) is removed from all three places it appeared:
- the Order button on the East Meadow card (Locations page)
- the homepage "Find the Madness" stops list
- the Order Now location picker

East Meadow now shows "Online ordering soon" in those spots; Directions stays. Carle Place's MyManager link is untouched.

When the Toast link is ready, add `"East Meadow, NY": "<toast url>",` back to the `ORDER` list in the page script and restore the card's Order button.

The same fix is in the Oct 28 revisions (`oct-28-mobile-revisions/`). Rebuild with `oct-28-mobile-revisions/_build/east_meadow.py`.
