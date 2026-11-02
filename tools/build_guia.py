#!/usr/bin/env python3
"""Builds the guide pages site/guia/<slug>.html from tools/guia.json.

One page per question people ask AI and Google ("¿Dónde comprar triple sec en Puerto Rico?"), with the
question as the title and the answer in the first paragraph. Same header, footer, age gate and type as
the FAQ page (tools/tragos_base.html). Not in the menu; linked from the FAQ, the sitemap and each other.
Placeholders {{TIENDAS_LEAD}} / {{TIENDAS_LISTA}} are filled from the live store list.
Run after editing guia.json or when the stores change (the recipes workflow runs it every 15 min).
"""
from hoist_meta import hoist
import json, html, re, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS = ROOT + 'tools/'; SITE = ROOT + 'site/'
sys.path.insert(0, TOOLS)
from build_llms import stores
B = json.load(open(TOOLS + 'config.json'))['site_url'].rstrip('/')
GUIA = json.load(open(TOOLS + 'guia.json', encoding='utf8'))
esc = lambda t: html.escape(t, quote=True)
ZONA = {'condado / miramar': 'San Juan', 'santurce': 'San Juan', 'viejo san juan': 'San Juan', 'hato rey': 'San Juan', 'río piedras': 'San Juan'}


def isla():
    """Puerto Rico outline with one dot per store, from the sheet's coordinates (same projection as the Tres Santos map)."""
    import re as _re
    I = json.load(open(TOOLS + 'isla.json'))
    dots = ''
    for r in stores():
        ll = _re.search(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', getattr(r, 'll', ''))
        if not ll: continue
        lat, lng = float(ll.group(1)), float(ll.group(2))
        x = 20.1 + 481.2 * (lng + 67.24819); y = 101.5 - 506.1 * (lat - 18.32943)
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8"><title>{esc(r[0])} · {esc(r[3])}</title></circle>'
    return ('<svg class="gu-isla" viewBox="-6 -2 846 324" role="img" aria-label="Mapa de Puerto Rico con los lugares donde comprar Tres Naranjos">'
            f'<path class="coast" d="{I["coast"]}"/><g class="dots">{dots}</g></svg>')


def tiendas():
    rows = stores()
    towns = []
    for n, t, d, p in rows:
        tw = ZONA.get(p.strip().lower(), p)
        if tw not in towns: towns.append(tw)
    lead_en = (f'Tres Naranjos Triple Sec is sold at {len(rows)} places in {len(towns)} towns across Puerto Rico, from {towns[0]} to {towns[-1]}: liquor stores, supermarkets and cash and carries. '
               f'It is a triple sec sweetened with agave honey, 25% ABV, 750 ml, made in Mexico and imported to Puerto Rico.')
    lead = (f'Hoy Tres Naranjos Triple Sec, un licor de naranja con miel de agave, está en {len(rows)} lugares de {len(towns)} pueblos de Puerto Rico, entre licorerías, supermercados y cash and carry, '
            f'de {towns[0]} a {towns[-1]}. Si no te queda ninguno cerca, <a href="https://puertoricoproduce.com/product/tres-naranjos" target="_blank" rel="noopener">PRoduce</a> lo entrega a domicilio en el área metro.')
    g = {}
    for n, t, d, p in rows: g.setdefault(p, []).append((n, t, d))
    lista = ''.join(f'<h3>{esc(p)}</h3><ul>' + ''.join(f'<li><b>{esc(n)}</b> ({esc(t)}){", " + esc(d) if d else ""}</li>' for n, t, d in g[p]) + '</ul>'
                    for p in sorted(g, key=lambda x: x.lower()))
    return lead, lista, lead_en


LOGOS = ('<div class="gu-logos" aria-label="Algunos lugares donde lo encuentras"><img src="assets/tiendas/the-house.webp" alt="The House" width="480" height="121" loading="lazy" style="height:clamp(20px,1.9vw,28px)">'
         '<img src="assets/tiendas/produce.webp" alt="PRoduce" width="310" height="200" loading="lazy" style="height:clamp(28px,2.6vw,38px)">'
         '<img src="assets/tiendas/club-mezcal.webp" alt="Club Mezcal" width="322" height="200" loading="lazy" style="height:clamp(30px,2.8vw,40px)"></div>')
SPECS_UL = ('<ul class="gu-specs"><li><span>Alcohol</span><b>25% vol.</b></li><li><span>Contenido</span><b>750 ml</b></li><li><span>Hecho con</span><b>Miel de agave</b></li>'
         '<li><span>Hecho en</span><b>México</b></li><li><span>Se vende en</span><b>Puerto Rico</b></li></ul>')
SPECS = ('<div class="gu-specwrap">' + SPECS_UL + '<img class="gu-back" src="assets/prod-back.webp" alt="Etiqueta trasera de Tres Naranjos Triple Sec con la receta para margaritas" width="1000" height="1250" loading="lazy"></div>')
MARGARITA = ('<div class="gu-rec"><p class="gu-rec-t">La margarita, con Tres Naranjos</p><ul class="rp-ing">'
             '<li><span>Tequila blanco o mezcal</span><span class="a">1 1/2 oz</span></li>'
             '<li class="tn"><span>Tres Naranjos Triple Sec</span><span class="a">1/2 oz</span></li>'
             '<li><span>Jugo de lima</span><span class="a">1/2 oz</span></li>'
             '<li><span>Miel de agave o sirope simple</span><span class="a">1/2 oz</span></li>'
             '<li><span>Sal y una rueda de lima</span><span class="a"></span></li></ul>'
             '<p class="gu-rec-n">Agita con hielo de 10 a 15 segundos, cuela sobre hielo fresco. <a href="recetas/margarita">La receta completa →</a></p></div>')

TRAGOS = ('<div class="gu-tragos">' + ''.join(f'<a href="recetas/{slug}"><img src="assets/tragos/sm/{ph}.webp" alt="{n}" width="560" height="560" loading="lazy"><span>{n}</span></a>'
          for slug, ph, n in [('margarita','margarita','Margarita'),('mezcalita','mezcalita','Mezcalita'),('cosmo','cosmo','Cosmo'),('spritz-de-china','spritz','Spritz de china')]) + '</div>')

SPECS_EN = ('<ul class="gu-specs"><li><span>Alcohol</span><b>25% ABV</b></li><li><span>Size</span><b>750 ml</b></li><li><span>Sweetened with</span><b>Agave honey</b></li>'
            '<li><span>Made in</span><b>Mexico</b></li><li><span>Sold in</span><b>Puerto Rico</b></li></ul>')
MARGARITA_EN = ('<div class="gu-rec"><p class="gu-rec-t">The margarita, with Tres Naranjos</p><ul class="rp-ing">'
                '<li><span>Blanco tequila or mezcal</span><span class="a">1 1/2 oz</span></li>'
                '<li class="tn"><span>Tres Naranjos Triple Sec</span><span class="a">1/2 oz</span></li>'
                '<li><span>Lime juice</span><span class="a">1/2 oz</span></li>'
                '<li><span>Agave honey or simple syrup</span><span class="a">1/2 oz</span></li>'
                '<li><span>Salt rim and a lime wheel</span><span class="a"></span></li></ul>'
                '<p class="gu-rec-n">Shake with ice for 10 to 15 seconds, strain over fresh ice. <a href="recetas/margarita">Full recipe (Spanish) →</a></p></div>')

CSS = '''<style>
main#top.gu{padding-top:calc(var(--fqnav,77px) + clamp(36px,4.5vw,64px))!important;padding-bottom:clamp(64px,8vw,110px);max-width:1040px;margin-inline:auto}
.gu-top{display:grid;grid-template-columns:minmax(0,1fr) clamp(220px,24vw,300px);gap:clamp(28px,4vw,64px);align-items:start;margin-bottom:clamp(28px,3vw,40px);padding-bottom:clamp(24px,2.5vw,32px);border-bottom:1.5px dashed var(--negro)}
.gu-top img{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;border-radius:16px;display:block}
.gu-body{max-width:720px}
@media (max-width:760px){.gu-top{grid-template-columns:1fr;gap:20px}.gu-top img{aspect-ratio:5/4;order:-1}}
.gu-top--map{grid-template-columns:1fr}.gu-top--map .gu-isla{width:170px;margin:0 0 18px -4px}
.gu-isla{width:100%;height:auto;overflow:visible}
.gu-isla .muni path{fill:#FFF;stroke:rgba(45,41,38,.14);stroke-width:.8}
.gu-isla .coast{fill:#FFF;stroke:#2D2926;stroke-width:3;stroke-linejoin:round}
.gu-isla .dots circle{r:13;fill:#E8561A;stroke:#FFF;stroke-width:4}
@media (max-width:760px){.gu-top--map .gu-isla{width:150px;margin-bottom:14px}}
.gu-photo{width:100%;max-width:520px;height:auto;aspect-ratio:5/4;object-fit:cover;border-radius:16px;display:block;margin:24px 0 8px}
.gu-logos{display:flex;align-items:center;gap:clamp(22px,3.4vw,44px);flex-wrap:wrap;margin:24px 0 0}.gu-logos img,.gu-top .gu-logos img{width:auto;max-width:100%;aspect-ratio:auto;border-radius:0;object-fit:contain;display:block;filter:brightness(0);opacity:.78}
.gu-specwrap{display:grid;grid-template-columns:minmax(0,460px) clamp(180px,20vw,240px);gap:clamp(24px,4vw,56px);align-items:center;margin-top:28px}
.gu-back{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;border-radius:16px;display:block}
@media (max-width:640px){.gu-specwrap{grid-template-columns:1fr}.gu-back{max-width:260px}}
.gu .gu-specs{list-style:none;margin:0;padding:0;max-width:460px;border-top:1.5px dashed var(--negro)}
.gu .gu-specs li{margin:0;display:flex;justify-content:space-between;gap:16px;padding-block:12px;border-bottom:1.5px dashed var(--negro);font-family:var(--type);font-size:15.5px;-webkit-text-stroke:.4px currentColor}
.gu-specs b{font-weight:700}
.gu-cmp-wrap{margin:18px 0 4px}
.gu .gu-cmp{width:100%;border-collapse:collapse;border-top:1.5px dashed var(--negro);font-size:15.5px}
.gu-cmp th{font-family:var(--type);font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;text-align:left;font-weight:700;padding:10px 14px 10px 0;border-bottom:1.5px dashed var(--negro);white-space:nowrap}
.gu-cmp td{padding:13px 14px 13px 0;border-bottom:1px dotted rgba(45,41,38,.45);vertical-align:top;line-height:1.45}
.gu-cmp tbody tr:last-child td{border-bottom:1.5px dashed var(--negro)}
.gu-cmp td b{display:block;font-size:16.5px}
.gu-cmp tr.tn td b{color:#C2410C}
.gu-cmp .gu-cmp-where{display:block;font-size:13.5px;color:var(--negro-60);margin-top:2px}
.gu .gu-cmp .gu-cmp-where a{font-weight:400;text-underline-offset:3px;text-decoration-thickness:1px}
.gu-cmp td.n{font-family:var(--type);font-weight:700;-webkit-text-stroke:.4px currentColor;white-space:nowrap}
.gu .gu-cmp-src{font-size:13.5px;line-height:1.5;color:var(--negro-60);margin:10px 0 0}
.gu .gu-cmp-src a{font-weight:400}
@media (max-width:640px){.gu-cmp thead{display:none}.gu-cmp,.gu-cmp tbody,.gu-cmp tr,.gu-cmp td{display:block;width:100%}.gu-cmp tr{padding:12px 0;border-bottom:1px dotted rgba(45,41,38,.45)}.gu-cmp tbody tr:last-child{border-bottom:1.5px dashed var(--negro)}.gu-cmp td,.gu-cmp tbody tr:last-child td{border:0;padding:3px 0}.gu-cmp td[data-label]:not(:first-child){display:flex;gap:10px}.gu-cmp td[data-label]:not(:first-child)::before{content:attr(data-label);flex:0 0 92px;font-family:var(--type);font-size:12px;letter-spacing:.05em;text-transform:uppercase;font-weight:700;padding-top:3px}.gu-cmp td:first-child{padding-bottom:6px}}
.gu-rec{margin:28px 0 8px;padding:18px 0 0;border-top:1.5px dashed var(--negro);max-width:520px}
.gu-rec-t{font-family:var(--display);font-size:clamp(22px,2vw,28px);line-height:1;text-transform:uppercase;margin:0 0 10px}
.gu .gu-rec .rp-ing{list-style:none;margin:0;padding:0;font-family:var(--type);font-size:15.5px;-webkit-text-stroke:.4px currentColor}
.gu .gu-rec .rp-ing li{margin:0;display:flex;justify-content:space-between;gap:16px;padding:10px 0;border-bottom:1px dotted rgba(45,41,38,.45)}.gu-rec .rp-ing li:last-child{border-bottom:1.5px dashed var(--negro)}
.gu-rec .rp-ing li.tn{font-weight:700;color:#C2410C}.gu-rec .rp-ing .a{white-space:nowrap;font-weight:700}
.gu-rec-n{font-size:15px;margin:12px 0 0;color:var(--negro-60)}
.gu-tragos{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:clamp(10px,1.6vw,18px);margin:24px 0 8px}
.gu-tragos a{text-decoration:none;font-weight:700;font-size:14px;color:var(--negro)}
.gu-tragos img{width:100%;height:auto;aspect-ratio:1;object-fit:cover;border-radius:12px;display:block;margin-bottom:8px}
.gu-tragos a:hover{color:#E04F12}
@media (max-width:600px){.gu-tragos{grid-template-columns:repeat(2,minmax(0,1fr))}}
.gu h1{font-family:var(--display);font-size:clamp(34px,3.8vw,52px);line-height:.95;margin:.2em 0 .4em;text-transform:uppercase}
.gu .lead{font-size:clamp(18px,1.5vw,21px);line-height:1.5;margin:0}
.gu h2{font-family:var(--display);font-size:clamp(24px,2.2vw,32px);line-height:1;margin:clamp(32px,3.5vw,44px) 0 12px;text-transform:uppercase}
.gu h3{font-size:17px;margin:22px 0 6px}
.gu p,.gu li{font-size:17px;line-height:1.6}
.gu ul{padding-left:1.2em;margin:0 0 8px}
.gu li{margin:4px 0}
.gu a{color:var(--negro);font-weight:700;text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:4px}
.gu a:hover{color:#E04F12}
.gu-links{margin-top:clamp(36px,4vw,52px);padding-top:20px;border-top:1.5px dashed var(--negro);display:flex;flex-wrap:wrap;gap:10px 24px;font-size:16px}
.gu-more{margin-top:14px;font-size:15px;color:var(--negro-60)}
.gu-more a{font-weight:700}
@media (min-width:1800px){.gu{zoom:1.2}}
</style>'''

os.makedirs(SITE + 'guia', exist_ok=True)
base = open(TOOLS + 'tragos_base.html', encoding='utf8').read()
t_lead, t_lista, t_lead_en = tiendas()
for g in GUIA:
    s = base
    lead = g['lead'].replace('{{TIENDAS_LEAD}}', t_lead).replace('{{TIENDAS_LEAD_EN}}', t_lead_en)
    has_logos = '{{LOGOS}}' in g['body']
    lead_logos = LOGOS if has_logos else ''
    body = '\n'.join(x for x in g['body'] if x != '{{LOGOS}}').replace('{{TIENDAS_LISTA}}', t_lista).replace('{{ISLA}}', isla()).replace('{{LOGOS}}', LOGOS).replace('{{SPECS}}', SPECS).replace('{{MARGARITA}}', MARGARITA).replace('{{TRAGOS}}', TRAGOS).replace('{{MARGARITA_EN}}', MARGARITA_EN).replace('{{SPECS_EN}}', SPECS_EN)
    others = [o for o in GUIA if o['slug'] != g['slug'] and o.get('lang', 'es') == g.get('lang', 'es')]
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(g["title"])} | Tres Naranjos Triple Sec</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(g["desc"])}">', s, count=1)
    s = s.replace('<a href="recetas/" aria-current="page">', '<a href="recetas/">', 1)
    top_media = isla() if g.get('map') else f'<img src="{g["photo"]}" alt="{esc(g["photo_alt"])}" width="960" height="1200" fetchpriority="high">'
    main = f'''<main id="top" class="gu wrap">
  {'<div class="gu-top gu-top--map"><div>' + top_media + '<h1>' + esc(g["title"]) + '</h1><p class="lead">' + lead + '</p>' + lead_logos + '</div></div>' if g.get('map') else '<div class="gu-top"><div><h1>' + esc(g["title"]) + '</h1><p class="lead">' + lead + '</p>' + lead_logos + '</div>' + top_media + '</div>'}
  <div class="gu-body">
  {body}
  <nav class="gu-links" aria-label="Enlaces">{''.join(f'<a href="{h}">{esc(t)} →</a>' for t, h in g.get("links", []))}</nav>
  {('<p class="gu-more">' + ('More' if g.get('lang') == 'en' else 'Más preguntas') + ': ' + ' · '.join(f'<a href="guia/{o["slug"]}">{esc(o["q"])}</a>' for o in others) + ('' if g.get('lang') == 'en' else ' · <a href="guias">Todas las guías</a>') + '</p>') if others else ''}
  </div>
</main>
<script>(function(){{const n=document.getElementById('nav');const f=()=>{{if(n)document.documentElement.style.setProperty('--fqnav',n.getBoundingClientRect().bottom+'px')}};f();addEventListener('resize',f);addEventListener('load',f)}})();</script>'''
    a = s.index('<main id="top">'); b = s.index('</main>', a) + 7; s = s[:a] + main + s[b:]
    s = re.sub(r'(<head[^>]*>)', r'\1<base href="../">', s, count=1)
    LD = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"], "inLanguage": "es-PR",
          "mainEntityOfPage": f"{B}/guia/{g['slug']}", "image": f"{B}/{g['photo']}",
          "publisher": {"@type": "Organization", "name": "Tres Naranjos", "url": B + "/"},
          "about": {"@type": "Product", "name": "Tres Naranjos Triple Sec", "@id": B + "/#producto"}}
    s = s.replace('</head>', f'<script type="application/ld+json">{json.dumps(LD, ensure_ascii=False)}</script>\n</head>', 1)
    s = s.replace('</head>', CSS + f'<meta property="og:type" content="article"><meta property="og:site_name" content="Tres Naranjos"><meta property="og:title" content="{esc(g["title"])}"><meta property="og:description" content="{esc(g["desc"])}"><meta property="og:image" content="{B}/share/home.jpg?v=2"><link rel="canonical" href="{B}/guia/{g["slug"]}">\n</head>', 1)
    a = s.index('/* =====================================================================\n   RECETAS'); b = s.index('</script>', a)
    s = s[:a] + "(function(){const n=document.getElementById('nav');if(n)document.documentElement.style.setProperty('--navh',n.offsetHeight+'px')})();\n" + s[b:]
    s = re.sub(r'<style>\.t-page\{[^<]*</style>\n', '', s)
    if g.get('lang') == 'en':
        s = s.replace('<html lang="es"', '<html lang="en"', 1)
        s = s.replace('<meta property="og:locale" content="es_PR">', '<meta property="og:locale" content="en_US">')
        s = s.replace('"inLanguage": "es-PR"', '"inLanguage": "en"')
    open(SITE + f'guia/{g["slug"]}.html', 'w', encoding='utf8').write(hoist(s))
print('ok', len(GUIA), 'guías')
# ---------- /guias (Nov 2): hub of the guides, linked from the footer on every page ----------
ES = [g for g in GUIA if g.get('lang', 'es') == 'es']
s = base
H_T = 'Guías de triple sec: qué es, cuál usar y dónde comprar | Tres Naranjos'
H_D = 'Guías claras sobre el triple sec: qué es, triple sec o Cointreau, cuál usar para margarita y dónde comprarlo en Puerto Rico.'
s = re.sub(r'<title>.*?</title>', f'<title>{esc(H_T)}</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(H_D)}">', s, count=1)
s = s.replace('<a href="recetas/" aria-current="page">', '<a href="recetas/">', 1)
s = s.replace('<li><a href="guias">Guías</a></li>', '<li><a href="guias" aria-current="page">Guías</a></li>', 1)
main = f'''<main id="top" class="gu wrap gu-hub">
  <h1>Guías de triple sec</h1>
  <p class="lead">Respuestas claras a lo que más se pregunta del triple sec: qué es, cuál usar y dónde comprarlo en Puerto Rico.</p>
  <ul class="gu-hub-l">{''.join(f'<li><a href="guia/{g["slug"]}"><b>{esc(g["q"])}</b><span>{esc(g["desc"])}</span></a></li>' for g in ES)}</ul>
</main>
<script>(function(){{const n=document.getElementById('nav');const f=()=>{{if(n)document.documentElement.style.setProperty('--fqnav',n.getBoundingClientRect().bottom+'px')}};f();addEventListener('resize',f);addEventListener('load',f)}})();</script>'''
a = s.index('<main id="top">'); b = s.index('</main>', a) + 7; s = s[:a] + main + s[b:]
LD = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Guías de triple sec", "description": H_D, "inLanguage": "es-PR", "url": f"{B}/guias",
      "hasPart": [{"@type": "Article", "headline": g["title"], "url": f"{B}/guia/{g['slug']}"} for g in ES]}
s = s.replace('</head>', f'<script type="application/ld+json">{json.dumps(LD, ensure_ascii=False)}</script>\n</head>', 1)
HUB_CSS = '''<style>
.gu-hub{max-width:860px;padding-block:clamp(40px,6vw,80px)}
.gu-hub-l{list-style:none;padding:0!important;margin:clamp(24px,3vw,36px) 0 0!important;border-top:1.5px dashed var(--negro)}
.gu-hub-l li{margin:0!important;border-bottom:1.5px dashed var(--negro)}
.gu-hub-l a{display:block;padding:18px 0;text-decoration:none!important;color:var(--negro)}
.gu-hub-l b{display:block;font-size:clamp(19px,1.6vw,22px);line-height:1.3}
.gu-hub-l span{display:block;margin-top:4px;font-size:15px;line-height:1.45;font-weight:400;color:#7a706a}
.gu-hub-l a:hover b{color:#E04F12}
</style>'''
s = s.replace('</head>', CSS + HUB_CSS + f'<meta property="og:type" content="website"><meta property="og:site_name" content="Tres Naranjos"><meta property="og:title" content="{esc(H_T)}"><meta property="og:description" content="{esc(H_D)}"><meta property="og:image" content="{B}/share/home.jpg?v=2"><link rel="canonical" href="{B}/guias">\n</head>', 1)
a = s.index('/* =====================================================================\n   RECETAS'); b = s.index('</script>', a)
s = s[:a] + "(function(){const n=document.getElementById('nav');if(n)document.documentElement.style.setProperty('--navh',n.offsetHeight+'px')})();\n" + s[b:]
s = re.sub(r'<style>\.t-page\{[^<]*</style>\n', '', s)
open(SITE + 'guias.html', 'w', encoding='utf8').write(hoist(s))
print('ok guias hub')

