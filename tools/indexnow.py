#!/usr/bin/env python3
"""Tells Bing (and through it ChatGPT search and Copilot) which pages changed, using IndexNow.

Reads site/sitemap.xml and sends every URL whose <lastmod> is different from the last time it was sent
(remembered in tools/indexnow_enviado.json). The key file site/<KEY>.txt proves we own the domain.
The recipes workflow runs it every 15 minutes, after publishing; it sends nothing when nothing changed.
"""
import json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = '5286298b28425ac8dbbe004d0601e227'
HOST = 'tresnaranjos.com'
STATE = os.path.join(ROOT, 'tools/indexnow_enviado.json')


def main():
    sm = open(os.path.join(ROOT, 'site/sitemap.xml'), encoding='utf8').read()
    pages = dict(re.findall(r'<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]*)</lastmod>)?', sm))
    sent = json.load(open(STATE, encoding='utf8')) if os.path.exists(STATE) else {}
    changed = [u for u, d in pages.items() if sent.get(u) != d and HOST in u]
    if not changed:
        print('IndexNow: nada nuevo'); return
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': changed}).encode()
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    print(f'IndexNow: {len(changed)} páginas enviadas, respuesta {code}')
    if code in (200, 202):  # 202 = key not checked yet (first time), still accepted
        sent.update({u: pages[u] for u in changed})
        json.dump(sent, open(STATE, 'w', encoding='utf8'), indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
