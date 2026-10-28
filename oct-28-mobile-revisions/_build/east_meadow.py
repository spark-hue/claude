"""Hotfix: stop MyManager orders routing to East Meadow until its Toast link is ready.
Removes the link everywhere it appears; locations without an order link show "Online ordering soon"."""
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()

def rep(old, new):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'expected 1 match, found {n}: {old[:90]!r}')
    s = s.replace(old, new)

LINK = 'https://mfc.mymanager.com/online-shop/68cf2cd3eacacf55537e615c'
SOON = '<span class="osoon">Online ordering soon</span>'

# Locations page card
rep(f'<a class="btn" href="{LINK}" target="_blank" rel="noopener">Order <span class="arr">→</span></a>', SOON)
# order links used by the homepage stops list and the Order Now picker
rep(f' "East Meadow, NY": "{LINK}",', '')
# no order link -> no Order button (was a fallback to #locations)
rep("""</p></div><a class="btn" href="'+esc(ORDER[l.title]||'#locations')+'" target="_blank" rel="noopener">Order Now</a></li>';""",
    """</p></div>'+(ORDER[l.title]?'<a class="btn" href="'+esc(ORDER[l.title])+'" target="_blank" rel="noopener">Order Now</a>':'""" + SOON + """')+'</li>';""")
rep("""</p></div><a class="btn" href="'+esc(ORDER[l.title]||'#locations')+'" target="_blank" rel="noopener">Order <span class="arr">→</span></a></div>'""",
    """</p></div>'+(ORDER[l.title]?'<a class="btn" href="'+esc(ORDER[l.title])+'" target="_blank" rel="noopener">Order <span class="arr">→</span></a>':'""" + SOON + """')+'</div>'""")
rep('</style>\n</head>',
    '.osoon{font:13px/1.2 var(--f-label);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);align-self:center}\n</style>\n</head>')

if s.count('68cf2cd3eacacf55537e615c'):
    raise SystemExit('East Meadow MyManager link still present')
open(dst, 'w', encoding='utf-8').write(s)
print('ok')
