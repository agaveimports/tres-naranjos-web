# Builds the WhatsApp preview cards in site/share/<slug>.jpg (1200x630) from the drink photos.
# Layout: the drink photo exactly as on the site (4:5, uncropped, rounded) on the left,
# a cream panel on the right with the drink name big, its vibe and glass, the two tags and the wordmark.
# share/home.jpg is hand-made and not touched here.
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageOps

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
for dr in json.load(open(TOOLS + 'drinks.json')):
    img = Image.new('RGB', (W, H), CREMA); d = ImageDraw.Draw(img)
    # photo: same 4:5 frame as the site, only resized
    ph_h = H - 2 * M; ph_w = int(ph_h * 4 / 5)
    ph = Image.open(SITE + 'assets/tragos/' + dr['photo'] + '.webp').convert('RGB')
    ph = ImageOps.fit(ph, (ph_w, ph_h), Image.LANCZOS, centering=(0.5, 0.5))
    mask = Image.new('L', (ph_w, ph_h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, ph_w - 1, ph_h - 1], R, fill=255)
    img.paste(ph, (M, M), mask)

    # right panel
    x0 = M + ph_w + 56; maxw = W - M - 20 - x0
    y = M + 26
    name = dr['name'].upper()
    size = 132
    while size > 70:
        lines = wrap(d, name, f('elc.ttf', size), maxw)
        if len(lines) <= 2 and all(d.textlength(l, font=f('elc.ttf', size)) <= maxw for l in lines): break
        size -= 4
    fo = f('elc.ttf', size); y += 4
    for l in lines:
        d.text((x0 - 4, y), l, font=fo, fill=NEGRO); y += int(size * 0.9)
    y += 14
    y += 8
    # tags
    tf = f('hk7.ttf', 26); tx = x0
    for (bg, fg), t in zip([(NAR, CREMA), (AMARILLO, LADRILLO)], dr['tags']):
        tt = t.upper(); tw = sum(d.textlength(ch, font=tf) + 1.5 for ch in tt) - 1.5; bw = int(tw + 48)
        d.rounded_rectangle([tx, y, tx + bw, y + 52], 26, fill=bg)
        spaced(d, tx + 24, y + 12, tt, tf, fg, 1.5); tx += bw + 12
    # wordmark, bottom right of the panel
    wordmark(img, x0, H - M - 20 - 46, 46, NAR)
    img.save(SITE + f"share/{dr['slug']}.jpg", quality=90, optimize=True, progressive=True, subsampling=0)
print('done')
