"""Moves the title, description, share-preview (og/twitter), canonical and JSON-LD tags
to the top of <head>. WhatsApp, Facebook and Google read only the start of a page,
so these must come before the big inline styles. The build scripts call this
automatically; run it by hand on a hand-edited page:  python3 tools/hoist_meta.py site/index.html
"""
import re, sys
PAT = re.compile(
    r'<title>.*?</title>'
    r'|<meta\s+(?:name="(?:description|twitter:[^"]*)"|property="og:[^"]*")[^>]*>'
    r'|<link\s+rel="canonical"[^>]*>'
    r'|<script type="application/ld\+json">.*?</script>', re.S)
VIEWPORT = re.compile(r'<meta\s+name=("?)viewport\1[^>]*>')

def hoist(s):
    h = s.index('</head>')
    head, rest = s[:h], s[h:]
    tags = PAT.findall(head)
    if not tags:
        return s
    head = PAT.sub('', head)
    m = VIEWPORT.search(head)
    at = m.end() if m else head.index('<head>') + 6
    return head[:at] + '\n' + ''.join(tags) + '\n' + head[at:] + rest

if __name__ == '__main__':
    for p in sys.argv[1:]:
        s = open(p, encoding='utf-8').read()
        open(p, 'w', encoding='utf-8').write(hoist(s))
        print('hoisted', p)
