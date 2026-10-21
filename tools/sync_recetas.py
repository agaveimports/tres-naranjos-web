"""Brings the recipes from the Google Sheet "Tres Naranjos: sitio web" (tab Recetas) into the site.
Runs on GitHub (.github/workflows/recetas.yml) when the sheet changes, and every 15 minutes as a backup.
Can also be run by hand from the repo root:  python3 tools/sync_recetas.py  [--from file.json] [--force]

1. Reads the rows from the sheet's Apps Script web app (?accion=recetas).
2. Rows with "publicada" checked become drinks.json (fields the sheet doesn't show are kept per recipe code).
3. New photos (Google Drive links in the "foto" column) are downloaded and saved as WebP:
   site/assets/tragos/<name>.webp (960x1200) and site/assets/tragos/sm/<name>.webp (560x560).
   The file name includes part of the Drive id, so a new photo gets a new name (assets are cached for a year).
4. Rebuilds the recipe pages, the Recetas grid, the WhatsApp cards and the sitemap. Removes pages of
   recipes that are no longer published.
"""
import base64, io, json, os, re, subprocess, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recetas_sheet import row_to_drink, published

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS, SITE = ROOT + 'tools/', ROOT + 'site/'
SCRIPT_URL = re.search(r"SCRIPT_URL = '([^']+)'", open(TOOLS + 'build_anadir.py').read()).group(1)
VERSION_FILE = TOOLS + 'recetas_version.txt'


def get(params):
    url = SCRIPT_URL + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'tres-naranjos-sync'}), timeout=120) as r:
        return json.loads(r.read().decode())


def drive_id(foto):
    m = re.search(r'(?:/d/|[?&]id=)([A-Za-z0-9_-]{20,})', str(foto))
    return m.group(1) if m else None


def save_photo(img_bytes, name):
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(img_bytes))).convert('RGB')
    ImageOps.fit(im, (960, 1200), Image.LANCZOS, centering=(0.5, 0.5)).save(SITE + f'assets/tragos/{name}.webp', 'WEBP', quality=80)
    ImageOps.fit(im, (560, 560), Image.LANCZOS, centering=(0.5, 0.45)).save(SITE + f'assets/tragos/sm/{name}.webp', 'WEBP', quality=80)


def main():
    force = '--force' in sys.argv
    if '--from' in sys.argv:
        data = json.load(open(sys.argv[sys.argv.index('--from') + 1]))
    else:
        data = get({'accion': 'recetas'})
    if not data.get('ok') or not data.get('recetas'):
        print('sheet did not answer or is empty; nothing changed'); return 0
    old_version = open(VERSION_FILE).read().strip() if os.path.exists(VERSION_FILE) else ''
    if data['version'] == old_version and not force:
        print('no changes in the sheet'); return 0

    old = json.load(open(TOOLS + 'drinks.json'))
    by_code = {d['code']: d for d in old}
    used_codes = {str(r.get('codigo', '')).strip() for r in data['recetas']} | set(by_code)
    used_slugs = {str(r.get('slug', '')).strip() for r in data['recetas']} | {d['slug'] for d in old}
    new, skipped = [], []
    for r in data['recetas']:
        if not published(r) or not str(r.get('nombre', '')).strip():
            continue
        d = row_to_drink(r, by_code.get(str(r.get('codigo', '')).strip()), used_codes, used_slugs)
        used_codes.add(d['code']); used_slugs.add(d['slug'])
        fid = drive_id(d['photo'])
        if fid:
            d['photo'] = (d['slug'] + '-' + re.sub(r'[^a-z0-9]', '', fid.lower())[:6])
            if not os.path.exists(SITE + f"assets/tragos/{d['photo']}.webp"):
                f = get({'accion': 'foto', 'id': fid})
                if not f.get('ok'):
                    skipped.append((d['name'], 'foto no disponible')); continue
                save_photo(base64.b64decode(f['b64']), d['photo'])
        if not os.path.exists(SITE + f"assets/tragos/{d['photo']}.webp"):
            skipped.append((d['name'], 'sin foto')); continue
        if not d['ing'] or not d['steps']:
            skipped.append((d['name'], 'faltan ingredientes o pasos')); continue
        new.append(d)
    if not new:
        print('no published recipes; keeping the site as is'); return 0

    json.dump(new, open(TOOLS + 'drinks.json', 'w'), ensure_ascii=False, indent=1)
    keep = {d['slug'] for d in new}
    for d in old:
        if d['slug'] not in keep:
            for p in (SITE + f"recetas/{d['slug']}.html", SITE + f"share/{d['slug']}.jpg"):
                if os.path.exists(p): os.remove(p)

    for b in ('build_recipes.py', 'build_tragos.py', 'build_cards.py'):
        subprocess.run([sys.executable, TOOLS + b], check=True, cwd=ROOT)

    sm = open(SITE + 'sitemap.xml').read()
    base = re.search(r'<loc>(https?://[^/<]+)/</loc>', sm).group(1)
    lines = ''.join(f'  <url><loc>{base}/recetas/{d["slug"]}</loc></url>\n' for d in new)
    sm = re.sub(r'(?:  <url><loc>[^<]*/recetas/[^<]+</loc></url>\n)+', lambda m: lines, sm, count=1)
    open(SITE + 'sitemap.xml', 'w').write(sm)

    open(VERSION_FILE, 'w').write(data['version'] + '\n')
    print(f'{len(new)} recipes published', ('| skipped: ' + str(skipped)) if skipped else '')
    return 0


if __name__ == '__main__':
    sys.exit(main())
