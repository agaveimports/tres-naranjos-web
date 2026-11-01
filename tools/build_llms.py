#!/usr/bin/env python3
"""Builds site/llms.txt: a plain-text summary of the site for AI assistants.

Facts come from the same places the site uses: tools/drinks.json (recipes),
the stores sheet (CSV in STORES_CSV_URL inside site/donde-comprar.html; if it can't
be reached, the TIENDAS backup list in that same file) and tools/config.json.
Run after recipes or stores change (the recipes workflow runs it every 15 min).
"""
import csv, io, json, os, re, urllib.request, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, 'tools/config.json'), encoding='utf8'))
BASE = CFG['site_url'].rstrip('/')
DC = open(os.path.join(ROOT, 'site/donde-comprar.html'), encoding='utf8').read()


def stores():
    m = re.search(r"STORES_CSV_URL\s*=\s*'([^']+)'", DC)
    rows = []
    if m:
        try:
            with urllib.request.urlopen(m.group(1), timeout=15) as r:
                for row in csv.DictReader(io.StringIO(r.read().decode('utf8'))):
                    if row.get('nombre', '').strip():
                        rows.append((row['nombre'].strip(), row.get('tipo', '').strip(),
                                     row.get('direccion', '').strip(), row.get('pueblo', '').strip()))
        except Exception:
            rows = []
    if not rows:  # backup list in the page
        m = re.search(r'const TIENDAS\s*=\s*\[(.*?)\];', DC, re.S)
        for row in json.loads('[' + m.group(1) + ']'):
            rows.append((row[0], row[1], row[2], row[3]))
    return rows


def main():
    drinks = json.load(open(os.path.join(ROOT, 'tools/drinks.json'), encoding='utf8'))
    tiendas = stores()
    pueblos = []
    for _, _, _, p in tiendas:
        if p not in pueblos:
            pueblos.append(p)
    wa = CFG['whatsapp']; wa_fmt = f"{wa[1:4]}-{wa[4:7]}-{wa[7:]}"
    hoy = dt.date.today().strftime('%-d de %B de %Y')
    meses = {'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril', 'May': 'mayo', 'June': 'junio',
             'July': 'julio', 'August': 'agosto', 'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'}
    for en, es in meses.items():
        hoy = hoy.replace(en, es)

    L = ["# Tres Naranjos Triple Sec", "",
         "> Tres Naranjos es un triple sec (licor de naranja) endulzado con miel de agave, 25% alc. vol., botella de 750 ml, "
         "que se vende en Puerto Rico. Lo produce y embotella Bodegas Collado en Ciudad de México y lo importa Agave Imports LLC "
         "(San Juan, Puerto Rico). Hecho para margaritas, mezcalitas, cosmos y otros cócteles con tequila o mezcal.", "",
         "## Datos",
         "- Tipo: triple sec / licor de naranja, transparente",
         "- Endulzante: miel de agave (no azúcar refinada)",
         "- Alcohol: 25% vol.",
         "- Tamaño: 750 ml",
         "- Productor: Bodegas Collado, S.A. de C.V., Ciudad de México",
         "- Importador y distribuidor en Puerto Rico: Agave Imports LLC, PO Box 190029, San Juan, PR 00919",
         "- Distribución a supermercados y tiendas: Insular Trading",
         "- Se usa en la misma cantidad que cualquier triple sec, Cointreau o licor de naranja en una receta", "",
         f"## Dónde comprar en Puerto Rico ({len(tiendas)} lugares en {len(pueblos)} pueblos, lista actualizada el {hoy})",
         f"Lista completa con mapa: {BASE}/donde-comprar"]
    for n, t, d, p in tiendas:
        L.append(f"- {n} ({t}), {d + ', ' if d else ''}{p}")
    L += ["", f"## Recetas ({len(drinks)}, con cantidades en oz y ml que se ajustan por persona)", f"Todas: {BASE}/recetas/"]
    for d in drinks:
        ing = ', '.join(i[1] for i in d.get('ingredients', []) if isinstance(i, list) and len(i) > 1)
        L.append(f"- {d['name']}: {BASE}/recetas/{d['slug']}" + (f" ({ing})" if ing else ''))
    L += ["", "## Páginas",
          f"- Inicio: {BASE}/",
          f"- Dónde comprar: {BASE}/donde-comprar",
          f"- Recetas: {BASE}/recetas/",
          f"- Sobre nosotros y preguntas frecuentes: {BASE}/sobre-nosotros", "",
          "## Contacto",
          f"- Restaurantes y barras (pedidos): Agave Imports LLC, {wa_fmt} (WhatsApp), {CFG['email']}",
          "- Supermercados y tiendas: Insular Trading, 787-270-7272, info@insulartradingpr.com",
          "- Instagram: https://instagram.com/tresnaranjosoficial", ""]
    out = os.path.join(ROOT, 'site/llms.txt')
    txt = '\n'.join(L)
    old = open(out, encoding='utf8').read() if os.path.exists(out) else ''
    if re.sub(r'actualizada el .*?\)', '', old) != re.sub(r'actualizada el .*?\)', '', txt):
        open(out, 'w', encoding='utf8').write(txt)
        print('llms.txt actualizado:', len(tiendas), 'tiendas,', len(drinks), 'recetas')
    else:
        print('llms.txt sin cambios')


if __name__ == '__main__':
    main()
