"""Converts recipes between tools/drinks.json and the rows of the "Recetas" tab in the Google Sheet
"Tres Naranjos: sitio web". Used by sync_recetas.py (sheet -> site) and to fill the sheet the first time.

Sheet columns (row 1 headers, in this order):
  nombre | descripcion corta | vaso | etiquetas | porciones | tiempo | ingredientes | pasos | foto | publicada | consejo | codigo | slug
  ingredientes: one per line, "1 1/2 oz Tequila blanco" (lines without "oz" have no amount, e.g. "Sal y una rueda de lima").
                Any line that says Tres Naranjos is highlighted on the site.
  pasos: one per line.  etiquetas: up to 2, separated by commas.  publicada: TRUE/FALSE (checkbox).
  foto: the photo name already on the site (e.g. "margarita") or a Google Drive link to a new photo.
  codigo, slug: filled by the site, never changed by hand (the slug is the page address).
"""
import re, unicodedata

COLS = ['nombre', 'descripcion corta', 'vaso', 'etiquetas', 'porciones', 'tiempo', 'ingredientes', 'pasos',
        'foto', 'publicada', 'consejo', 'codigo', 'slug']
VASOS = {'Vaso corto': 'rocks', 'Vaso alto': 'highball', 'Copa': 'coupe', 'Copa o shot': 'coupe',
         'Flauta': 'flute', 'Copa de vino': 'wine', 'Jarra': 'pitcher'}
FR = {0: '', .25: '1/4', .5: '1/2', .75: '3/4'}


def norm(s):
    return unicodedata.normalize('NFD', str(s or '')).encode('ascii', 'ignore').decode().lower().strip()


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', norm(s)).strip('-')


def fmt_amount(a):
    w = int(a); f = round((a - w) * 4) / 4
    if f == 1: w, f = w + 1, 0
    fr = FR[f]
    return ((str(w) if w else '') + (' ' if w and fr else '') + fr) or '0'


def parse_amount(s):
    s = s.strip()
    m = re.fullmatch(r'(\d+)\s+(\d)/(\d)', s)
    if m: return int(m[1]) + int(m[2]) / int(m[3])
    m = re.fullmatch(r'(\d)/(\d)', s)
    if m: return int(m[1]) / int(m[2])
    m = re.fullmatch(r'\d+(?:[.,]\d+)?', s)
    if m: return float(s.replace(',', '.'))
    return None


def is_tn(name):
    return bool(re.search(r'\b(tres|3)\s*naranjos?\b', norm(name)))


def ing_line(i):
    amt, name = i[0], i[1]
    return (fmt_amount(amt) + ' oz ' + name) if amt is not None else name


def parse_ing(line):
    line = re.sub(r'\s+', ' ', line).strip(' -•\t')
    if not line: return None
    m = re.match(r'^(\d+\s+\d/\d|\d/\d|\d+(?:[.,]\d+)?)\s*oz\.?\s+(.+)$', line, re.I)
    amt, name = (parse_amount(m[1]), m[2].strip()) if m else (None, line)
    if amt is not None and amt == int(amt): amt = int(amt)
    if is_tn(name):
        name = 'Tres Naranjos' if norm(name) in ('tres naranjos', '3 naranjos', 'tres naranjo', 'tres naranjos triple sec') else name
        return [amt, name, 1]
    return [amt, name]


def drink_to_row(d):
    return {
        'nombre': d['name'], 'descripcion corta': d['sub'], 'vaso': d['vaso'],
        'etiquetas': ', '.join(d['tags']), 'porciones': d['serves'], 'tiempo': d['time'],
        'ingredientes': '\n'.join(ing_line(i) for i in d['ing']), 'pasos': '\n'.join(d['steps']),
        'foto': d['photo'], 'publicada': True, 'consejo': d.get('tip', ''), 'codigo': d['code'], 'slug': d['slug'],
    }


def next_code(used):
    for L in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        for n in range(1, 5):
            if L + str(n) not in used: return L + str(n)
    raise ValueError('no codes left')


def row_to_drink(r, prev, used_codes, used_slugs):
    """r: dict of sheet columns. prev: the existing drink with this code (keeps the fields the sheet doesn't show)."""
    name = str(r.get('nombre', '')).strip()
    code = str(r.get('codigo', '')).strip() or next_code(used_codes)
    slug = str(r.get('slug', '')).strip() or slugify(name)
    if not str(r.get('slug', '')).strip():
        base, k = slug, 2
        while slug in used_slugs: slug, k = f'{base}-{k}', k + 1
    tags = [t.strip() for t in re.split(r'[,;/]', str(r.get('etiquetas', ''))) if t.strip()][:2]
    try: serves = max(1, int(float(str(r.get('porciones') or 1).replace(',', '.'))))
    except ValueError: serves = 1
    vaso = str(r.get('vaso', '')).strip() or 'Vaso corto'
    d = dict(prev) if prev else {
        'level': 'Fácil', 'bg': 'var(--crema)', 'liq': '#F7B94A', 'rim': None, 'garnish': None, 'needs': []}
    d.update({
        'code': code, 'name': name, 'sub': str(r.get('descripcion corta', '')).strip(), 'vaso': vaso,
        'time': str(r.get('tiempo', '')).strip() or (prev or {}).get('time') or '3 min', 'serves': serves,
        'tags': tags, 'photo': str(r.get('foto', '')).strip(),
        'ing': [x for x in (parse_ing(l) for l in str(r.get('ingredientes', '')).splitlines()) if x],
        'steps': [s.strip(' -•\t') for s in str(r.get('pasos', '')).splitlines() if s.strip(' -•\t')],
        'tip': str(r.get('consejo', '')).strip(), 'slug': slug,
    })
    if not prev:
        d['taste'] = tags[:]; d['flavor'] = tags[0] if tags else 'Cítrico'; d['glass'] = VASOS.get(vaso, 'rocks')
    # keep the key order of drinks.json
    order = ['code', 'name', 'sub', 'vaso', 'time', 'level', 'serves', 'tags', 'photo', 'ing', 'steps', 'tip',
             'taste', 'bg', 'liq', 'glass', 'rim', 'garnish', 'flavor', 'needs', 'slug']
    return {k: d[k] for k in order if k in d} | {k: v for k, v in d.items() if k not in order}


def published(r):
    v = r.get('publicada', True)
    return v is True or norm(v) in ('true', 'si', 'sí', 'yes', '1', 'x', 'verdadero')


if __name__ == '__main__':
    import json, os
    D = json.load(open(os.path.join(os.path.dirname(__file__), 'drinks.json')))
    rows = [drink_to_row(d) for d in D]
    back = [row_to_drink(r, d, set(), set()) for r, d in zip(rows, D)]
    bad = [(a['name'], k) for a, b in zip(D, back) for k in a if a[k] != b.get(k)]
    print('round trip differences:', bad or 'none')
