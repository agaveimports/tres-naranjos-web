# Builds the WhatsApp preview cards in site/share/<slug>.jpg (1200x630) from the drink photos.
# Layout: the drink photo exactly as on the site (4:5, uncropped, rounded) on the left,
# the two tags on the photo (like the Tragos grid), and only the drink name on the right, vertically centered.
# If tools/share-src/<slug>.jpg exists (a wide version of the drink photo, glass in the left third),
# the card is that photo full-bleed with film grain and only the drink name, centered in the empty space.
# Names are always cream, no shadow, as big as fits in up to 2 lines.
# Krea prompt used for the wide photos (Nano Banana Pro, 16:9, 2K, the site photo attached):
#   Extend this exact photograph into a wide landscape image. Keep the same glass, the same drink, the same garnish,
#   the same hard warm sunlight, the same backdrop color, the same soft leaf shadows and the same fine film grain.
#   Do not redraw or change the glass or the drink. Place the glass in the left third of the frame. The right two
#   thirds is the same continuous seamless backdrop with soft dappled leaf shadows, plain and empty, with room for a
#   title. No text, no logos, no extra objects. share/home.jpg (home share card) is the hand-made photo in tools/share-src/home-clean.jpg plus the hero headline in cream; it is not built here. Bump its ?v= when it changes.
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS, SITE = ROOT + 'tools/', ROOT + 'site/'
FONTS = TOOLS + 'fonts/'
CREMA, NEGRO, NAR, LADRILLO, AMARILLO = (255, 244, 230), (45, 41, 38), (232, 86, 26), (138, 47, 12), (247, 196, 90)
GRIS = (122, 112, 104)
W, H, M, R = 1200, 630, 30, 34
f = lambda n, s: ImageFont.truetype(FONTS + n, s)

def spaced(d, x, y, t, fo, fill, ls):
    for ch in t:
        d.text((x, y), ch, font=fo, fill=fill); x += d.textlength(ch, font=fo) + ls
    return x

def wordmark(img, x, y, size, fill):
    """TRES NARANJOS with the mirrored E, like the logo."""
    d = ImageDraw.Draw(img); fo = f('elcaps.ttf', size)
    d.text((x, y), 'TR', font=fo, fill=fill); x += d.textlength('TR', font=fo)
    ew = int(d.textlength('E', font=fo)) + 2
    e = Image.new('RGBA', (ew, int(size * 1.5)), (0, 0, 0, 0)); ImageDraw.Draw(e).text((0, 0), 'E', font=fo, fill=fill)
    e = ImageOps.mirror(e); img.paste(e, (int(x), int(y)), e); x += d.textlength('E', font=fo)
    d.text((x, y), 'S NARANJOS', font=fo, fill=fill)

def wrap(d, text, fo, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fo) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

os.makedirs(SITE + 'share', exist_ok=True)

WIDE = TOOLS + 'share-src/'
def grain(img, seed=7, size=2.2, amount=11):
    """film grain like the home page hero: coarse (about 2px) clumps, a bit stronger in the shadows"""
    a = np.asarray(img).astype(np.float32); h, w = a.shape[:2]
    gh, gw = max(1, int(h / size)), max(1, int(w / size))
    g = np.random.default_rng(seed).normal(0, 1, (gh, gw)).astype(np.float32)
    g = np.asarray(Image.fromarray(((g * 40) + 128).clip(0, 255).astype('uint8')).resize((w, h), Image.BICUBIC)
                   .filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) - 128
    lum = a.mean(2, keepdims=True) / 255
    a += (g[..., None] / 40) * (amount + 5 * (1 - lum))
    return Image.fromarray(a.clip(0, 255).astype('uint8'))

def balanced(d, text, fo, maxw):
    """One line if it fits, otherwise the two-line split with the narrowest widest line."""
    if d.textlength(text, font=fo) <= maxw: return [text]
    w = text.split(); best = None
    if len(w) == 1: return [text]
    for i in range(1, len(w)):
        a, b = ' '.join(w[:i]), ' '.join(w[i:]); m = max(d.textlength(a, font=fo), d.textlength(b, font=fo))
        if best is None or m < best[0]: best = (m, [a, b])
    return best[1]

def wide_card(dr, size):
    src = Image.open(WIDE + dr['slug'] + '.jpg').convert('RGB')
    sw, sh = src.size; th = int(sw * H / W); top = int((sh - th) * 0.55)
    img = grain(src.crop((0, top, sw, top + th)).resize((W, H), Image.LANCZOS))
    d = ImageDraw.Draw(img)
    zx0, zx1 = int(W * 0.36), W - 40          # empty zone to the right of the glass
    # each card gets the biggest name that fits the zone in up to 2 lines (capped so short names don't shout)
    size = WMAX
    while size > 70:
        fo = f('elc.ttf', size); lines = balanced(d, dr['name'].upper(), fo, zx1 - zx0 - 24)
        if len(lines) <= 2 and all(d.textlength(l, font=fo) <= zx1 - zx0 - 24 for l in lines): break
        size -= 4
    fo = f('elc.ttf', size)
    lh = int(size * 0.92); bb = fo.getbbox('M'); cap = bb[3] - bb[1]
    block = lh * (len(lines) - 1) + cap; y0 = (H - block) // 2 - bb[1]
    widest = max(d.textlength(l, font=fo) for l in lines); x0 = int((zx0 + zx1 - widest) / 2)
    # names are always cream, no shadow (the WhatsApp title and description sit below the card)
    y = y0
    for l in lines:
        d.text((x0, y), l, font=fo, fill=CREMA); y += lh
    return img

DR = json.load(open(TOOLS + 'drinks.json'))
WMAX = 200   # largest drink name on a wide share card
# one name size for every wide card: the largest that keeps every name to 2 lines in the empty zone
_d = ImageDraw.Draw(Image.new('RGB', (W, H))); WSIZE = 132
while WSIZE > 70 and any(_d.textlength(l, font=f('elc.ttf', WSIZE)) > int(W * 0.60) - 80
        for x in DR for l in balanced(_d, x['name'].upper(), f('elc.ttf', WSIZE), int(W * 0.60) - 80)):
    WSIZE -= 4
for dr in DR:
    if os.path.exists(WIDE + dr['slug'] + '.jpg'):
        wide_card(dr, 0).save(SITE + f"share/{dr['slug']}.jpg", quality=90, optimize=True, progressive=True, subsampling=0); continue
    img = Image.new('RGB', (W, H), CREMA); d = ImageDraw.Draw(img)
    # photo: same 4:5 frame as the site, only resized
    ph_h = H - 2 * M; ph_w = int(ph_h * 4 / 5)
    ph = Image.open(SITE + 'assets/tragos/' + dr['photo'] + '.webp').convert('RGB')
    ph = ImageOps.fit(ph, (ph_w, ph_h), Image.LANCZOS, centering=(0.5, 0.5))
    mask = Image.new('L', (ph_w, ph_h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, ph_w - 1, ph_h - 1], R, fill=255)
    img.paste(ph, (M, M), mask)

    # tags on the photo, bottom-left, like the Tragos grid
    tf = f('hk7.ttf', 24); tx = M + 22; ty = M + ph_h - 22 - 48
    for (bg, fg), t in zip([(NAR, CREMA), (AMARILLO, LADRILLO)], dr['tags']):
        tt = t.upper(); tw = sum(d.textlength(ch, font=tf) + 1.5 for ch in tt) - 1.5; bw = int(tw + 44)
        d.rounded_rectangle([tx, ty, tx + bw, ty + 48], 24, fill=bg)
        spaced(d, tx + 22, ty + 11, tt, tf, fg, 1.5); tx += bw + 10
    # right panel: only the drink name, vertically centered on the photo, max 2 lines
    x0 = M + ph_w + 64; maxw = W - M - 24 - x0
    name = dr['name'].upper(); size = 140
    while size > 64:
        lines = wrap(d, name, f('elc.ttf', size), maxw)
        if len(lines) <= 2 and all(d.textlength(l, font=f('elc.ttf', size)) <= maxw for l in lines): break
        size -= 4
    fo = f('elc.ttf', size); lh = int(size * 0.92)
    bb = fo.getbbox('M'); cap = bb[3] - bb[1]
    block = lh * (len(lines) - 1) + cap
    y = M + (ph_h - block) // 2 - bb[1]
    for l in lines:
        d.text((x0 - 4, y), l, font=fo, fill=NEGRO); y += lh
    img.save(SITE + f"share/{dr['slug']}.jpg", quality=90, optimize=True, progressive=True, subsampling=0)
print('done')
