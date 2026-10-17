# Builds the WhatsApp preview cards in site/share/<slug>.jpg (1200x630) from the drink photos.
# Layout: the drink photo exactly as on the site (4:5, uncropped, rounded) on the left,
# the two tags on the photo (like the Tragos grid), and only the drink name on the right, vertically centered.
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
