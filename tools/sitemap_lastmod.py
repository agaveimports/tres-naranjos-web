"""Keep the <lastmod> dates in site/sitemap.xml honest.

For every address in the sitemap, this takes a fingerprint of its page (the HTML without scripts
and styles, so code-only changes don't count) and keeps the date the page last changed in
tools/sitemap_fechas.json. When a fingerprint changes, that page's date becomes today. Pages that
didn't change keep their date. Google trusts lastmod only when it's accurate, so never set dates by hand.

Safe to run any time. The recipes workflow (.github/workflows/recetas.yml) runs it on every pass,
so hand-made edits get their new date within about 15 minutes.

Usage: python3 tools/sitemap_lastmod.py
"""
import datetime, hashlib, json, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
SITEMAP = os.path.join(SITE, 'sitemap.xml')
DB = os.path.join(ROOT, 'tools', 'sitemap_fechas.json')
LINE = re.compile(r'  <url><loc>([^<]+)</loc>(?:<lastmod>[^<]*</lastmod>)?</url>')


def page_file(loc):
    """https://tresnaranjos.com/recetas/margarita -> site/recetas/margarita.html"""
    path = re.sub(r'^https?://[^/]+', '', loc) or '/'
    if path.endswith('/'):
        path += 'index.html'
    elif not path.endswith('.html'):
        path += '.html'
    return os.path.join(SITE, path.lstrip('/'))


def fingerprint(f):
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    s = re.sub(r'\s+', ' ', s)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


def git_date(f):
    """Date of the last commit that touched the file (only used the first time a page is seen)."""
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', f], cwd=ROOT,
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return out if re.fullmatch(r'\d{4}-\d{2}-\d{2}', out) else ''
    except Exception:
        return ''


def main():
    sm = open(SITEMAP, encoding='utf-8').read()
    db = json.load(open(DB, encoding='utf-8')) if os.path.exists(DB) else {}
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    seen = {}

    def fix(m):
        loc = m.group(1)
        f = page_file(loc)
        if not os.path.exists(f):
            return f'  <url><loc>{loc}</loc></url>'
        key = os.path.relpath(f, SITE).replace(os.sep, '/')
        h = fingerprint(f)
        e = db.get(key)
        if not e:
            e = {'hash': h, 'fecha': git_date(f) or today}
        elif e['hash'] != h:
            e = {'hash': h, 'fecha': today}
        seen[key] = e
        return f'  <url><loc>{loc}</loc><lastmod>{e["fecha"]}</lastmod></url>'

    new_sm = LINE.sub(fix, sm)
    new_db = json.dumps(dict(sorted(seen.items())), ensure_ascii=False, indent=1) + '\n'
    old_db = open(DB, encoding='utf-8').read() if os.path.exists(DB) else ''
    if new_sm != sm:
        open(SITEMAP, 'w', encoding='utf-8').write(new_sm)
    if new_db != old_db:
        open(DB, 'w', encoding='utf-8').write(new_db)
    changed = [k for k, e in seen.items() if db.get(k) != e]
    print('sitemap dates updated: ' + ', '.join(changed) if changed else 'sitemap dates: nothing changed')


if __name__ == '__main__':
    main()
