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


def grain(img, seed=7, size=2.2, amount=11):
    """film grain, same as build_cards.grain (the house look on every drink photo)"""
    import numpy as np
    from PIL import Image, ImageFilter
    a = np.asarray(img).astype(np.float32); h, w = a.shape[:2]
    gh, gw = max(1, int(h / size)), max(1, int(w / size))
    g = np.random.default_rng(seed).normal(0, 1, (gh, gw)).astype(np.float32)
    g = np.asarray(Image.fromarray(((g * 40) + 128).clip(0, 255).astype('uint8')).resize((w, h), Image.BICUBIC)
                   .filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) - 128
    lum = a.mean(2, keepdims=True) / 255
    a += (g[..., None] / 40) * (amount + 5 * (1 - lum))
    return Image.fromarray(a.clip(0, 255).astype('uint8'))


def house_look(img):
    """The look of the original drink photos: a little faded (softer blacks), slightly warm, slightly less saturated."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img).astype(np.float32)
    g = a.mean(2, keepdims=True); a = g + (a - g) * 0.88          # a touch less saturated
    a = a * 0.9 + 255 * 0.06                                       # lifted blacks, softer contrast
    a *= np.array([1.03, 1.0, 0.95], dtype=np.float32)             # warm
    return Image.fromarray(a.clip(0, 255).astype('uint8'))


def glass_x(im):
    """Where the glass is in a wide AI photo, as a fraction of the width (same logic as the /equipo/receta preview).
    Backdrop colour = right quarter (always empty); the glass is the widest run of columns, in the lower-middle band,
    whose colour differs from it. Chromaticity only, so light and leaf shadows on the backdrop don't count."""
    import numpy as np
    w = 160; h = max(1, round(im.height * w / im.width))
    a = np.asarray(im.convert('RGB').resize((w, h))).astype(float)
    c = a / (a.sum(2, keepdims=True) + 1)
    bg = np.median(c[:, int(w * .75):].reshape(-1, 3), 0)
    d = np.sqrt(((c - bg) ** 2).sum(2)) * 100
    score = (d[int(h * .28):int(h * .62), :int(w * .75)] > 6).mean(0)  # upper glass only: shadows on the table stay out
    if score.max() < .15: return .25
    on = score >= score.max() * .5
    best, start = (0, 0, 0), None
    for i, v in enumerate(list(on) + [False]):
        if v and start is None: start = i
        if not v and start is not None:
            if i - start > best[0]: best = (i - start, start, i)
            start = None
    _, s, e = best
    return ((s + e) / 2) / w if e > s else .25


def save_photo(img_bytes, name, slug=None):
    """A wide photo (the AI photos from /equipo/receta are 16:9, glass in the left third) becomes:
    the recipe photo cropped 4:5 from the glass side, and tools/share-src/<slug>.jpg so its WhatsApp card is the full wide photo."""
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(img_bytes))).convert('RGB')
    W, H = im.size
    if slug and W / H > 1.3:
        house_look(im.resize((1600, round(1600 * H / W)), Image.LANCZOS)).save(TOOLS + f'share-src/{slug}.jpg', quality=92)  # card gets its grain in build_cards
        cw = round(H * 0.8); x0 = max(0, min(W - cw, round(W * glass_x(im) - cw / 2)))  # glass in the middle of the recipe photo
        im = im.crop((x0, 0, x0 + cw, H))
        im = grain(house_look(ImageOps.fit(im, (960, 1200), Image.LANCZOS)), amount=7)  # faded warm look + film grain, like the original drink photos
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
                save_photo(base64.b64decode(f['b64']), d['photo'], d['slug'])
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
