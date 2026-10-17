# Tres Naranjos website

Marketing site for Tres Naranjos Triple Sec (Agave Imports LLC, Puerto Rico). Plain static HTML, CSS and JS, no framework and no build server. Everything in `site/` is published as is by Netlify.

The people asking for changes are usually not developers. They write in Spanish or English and describe what they want to see. Make the change, check it, and explain what changed in plain words.

## Layout

```
site/                    published folder (Netlify "publish" directory)
  index.html             home page
  tragos.html            drinks grid      (GENERATED, do not edit by hand)
  donde-comprar.html     store finder with the map
  preguntas.html         FAQ page (GENERATED from tools/faq.json)
  r/A1.html ... C4.html  one page per drink (GENERATED, do not edit by hand)
  r/img/*.jpg            WhatsApp share cards, 1200x630 (GENERATED)
  assets/                photos (.webp), video, fonts
  assets/tragos/         drink photos 960x1200; assets/tragos/sm/ = 560x560 thumbnails
  sitemap.xml, robots.txt, _headers (cache rules), favicons
tools/
  drinks.json            ALL drink data: name, vibe, glass, tags, photo, ingredients, steps, tip
  config.json            site_url, whatsapp, email (current values, used by the helper scripts)
  tragos_base.html       shared header, footer, age gate and styles for generated pages
  build_recipes.py       builds site/r/*.html from drinks.json
  build_tragos.py        builds site/tragos.html from drinks.json
  build_faq.py           builds site/preguntas.html from faq.json (questions + answers, FAQPage schema)
  build_cards.py         builds site/r/img/*.jpg share cards (needs Pillow)
  set_contact.py         change WhatsApp number or email everywhere
  set_domain.py          change the site address everywhere (links, share cards, sitemap)
```

## Common tasks

**Edit a drink or add one**
1. Edit `tools/drinks.json`. Codes go A1..C4; a new drink gets the next code (D1...). Amounts are in oz as numbers (1.5, 0.75); `null` for things like "Hielo". Mark the Tres Naranjos line with a third value `1`, for example `[0.5, "Tres Naranjos", 1]`.
2. New drink photo: 960x1200 WebP in `site/assets/tragos/<photo>.webp` plus a 560x560 crop in `site/assets/tragos/sm/<photo>.webp`. Match the existing look: one glass, flat colored backdrop, hard warm sunlight, leaf shadows, film grain.
3. Run, from the repo root:
   `python3 tools/build_recipes.py && python3 tools/build_tragos.py && python3 tools/build_faq.py && python3 tools/build_cards.py`
4. Add the new page to `site/sitemap.xml`.

The home page section "Una naranja, mil maneras" shows 6 featured drinks from its own `const RECIPES` block in `site/index.html` (plus `SHARE_CODE` and `SHARE_TAGS` next to it). Keep it in sync with drinks.json when you change one of those 6.

**Change the WhatsApp number or email**
`python3 tools/set_contact.py --whatsapp 1787XXXXXXX` (digits only, starting with 1)
`python3 tools/set_contact.py --email nuevo@correo.com`

**Change the domain** (for example when tresnaranjos.com goes live)
`python3 tools/set_domain.py https://tresnaranjos.com`, then run the four build scripts. Also lock the Mapbox token to the new domain in the Mapbox account.

**Stores on Dónde comprar**
The list is the `const TIENDAS = [...]` array in `site/donde-comprar.html`: name, type, address, town, phone, "lat, lng" (start with `~` when approximate). It can instead read a published Google Sheet CSV: paste the link into `STORES_CSV_URL` in the same file (instructions are in the comment above it). The home page closing section ("81 lugares en 18 pueblos", its town list and its small map pins) is hand-written in `site/index.html`; update it when the store list changes a lot. The "Disponible en" strip under the hero is also in `site/index.html`.

**Edit the FAQ**
Edit `tools/faq.json` (answers may contain simple HTML links), then run `python3 tools/build_faq.py`.

## Brand rules (keep the site consistent)

- Spanish (Puerto Rico). Orange is "china" in ingredients; "lima" is the green one, "limón" the yellow one. Amounts written "1 1/2 oz", "3/4 oz".
- No em dashes in copy.
- Colors: brand orange #E8561A, buttons #EE5F1C (hover #E04F12), cream #FFF4E6, ink #2D2926, yellow #F7C45A, WhatsApp green #1E8E4F.
- Fonts: El Camino (display and logo), Hanken Grotesk (body and buttons), Courier Prime (small labels, ingredient lists). All self-hosted in `site/assets/fonts/`.
- Buttons are flat pills: no outlines, no hard drop shadows. Animation is minimal (section headlines fade up once).
- Never invent reviews, testimonials or ratings.
- Keep the age gate, "Disfruta con responsabilidad" and the GOVERNMENT WARNING on every page.

## Before finishing any change

- Open the changed pages in a browser at phone width (390px) and laptop width (1440px) and check nothing overlaps or spills sideways.
- Check there are no broken images or console errors.
- Images: new photos as WebP, around 80 quality, no wider than 1600px.
- Commit with a short message describing the change. Pushing to `main` deploys to Netlify automatically in about a minute.
