"""Builds site/privacidad.html (plain-language privacy notice). Edit the TEXT below, then run this script.
Update FECHA whenever the text changes, and mention new tools (analytics, forms) when they are added."""
from hoist_meta import hoist
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS, SITE = ROOT + 'tools/', ROOT + 'site/'
B = json.load(open(TOOLS + 'config.json'))['site_url'].rstrip('/')
EMAIL = json.load(open(TOOLS + 'config.json')).get('email', 'info@agaveimportspr.com')
FECHA = '17 de octubre de 2026'
TEXT = [
  ('Lo corto', f'Este sitio no tiene cuentas, formularios ni tienda. No te pedimos tu nombre, tu correo ni tu teléfono, y no vendemos información de nadie.'),
  ('Lo que se guarda en tu teléfono o computadora', 'Cuando confirmas que tienes la edad legal, guardamos esa respuesta en tu navegador para no preguntarte cada vez que entras. Se queda en tu equipo y la puedes borrar cuando quieras borrando los datos del sitio en tu navegador.'),
  ('Tu ubicación', 'Si tocas "Cerca de mí" en Dónde comprar, tu navegador te pide permiso para usar tu ubicación. La usamos solo en tu pantalla para mostrarte los lugares más cercanos. No la guardamos ni la enviamos a nadie.'),
  ('El mapa', 'El mapa de Dónde comprar lo provee Mapbox. Para mostrarlo, tu navegador le pide las imágenes del mapa a Mapbox, que recibe datos técnicos como tu dirección IP y el tipo de navegador, igual que cualquier sitio que visitas.'),
  ('El hosting', 'El sitio está alojado en Cloudflare. Como cualquier servidor, Cloudflare recibe datos técnicos de cada visita (dirección IP, navegador, página visitada) para entregar el sitio y protegerlo.'),
  ('Estadísticas', 'Usamos Microsoft Clarity y Cloudflare Web Analytics para entender cómo se usa el sitio: qué páginas se visitan, dónde se toca y hasta dónde se baja. Esa información es anónima y no la usamos para identificarte.'),
  ('Enlaces a otros sitios', 'Los botones de WhatsApp, Instagram y Google Maps te llevan a esos servicios, que tienen sus propias políticas de privacidad.'),
  ('Edad', 'Este sitio es para personas con la edad legal para consumir alcohol en su país.'),
  ('Preguntas', f'Si tienes alguna pregunta sobre tu privacidad, escríbenos a <button type="button" class="copy-mail" data-mail="{EMAIL}" aria-label="Copiar {EMAIL}"><span>{EMAIL}</span></button>.'),
]
s = open(TOOLS + 'tragos_base.html').read()
s = re.sub(r'<title>.*?</title>', '<title>Privacidad | Tres Naranjos</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Cómo Tres Naranjos maneja tu información en este sitio: qué se guarda, qué no y con quién se comparte.">', s, count=1)
s = s.replace('<a href="recetas/" aria-current="page">', '<a href="recetas/">')
CSS = '''<style>
main#top.pv{padding-top:calc(var(--navh,70px) + env(safe-area-inset-top,0px) + clamp(36px,6vw,80px));padding-bottom:clamp(64px,8vw,110px);max-width:720px;margin-inline:auto}
.pv-eye{font-family:var(--type);font-weight:700;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#E8561A}
.pv h1{font-family:var(--display);font-size:clamp(36px,4vw,56px);line-height:.95;margin:.2em 0 .3em;text-transform:uppercase}
.pv-date{font-size:14px;color:var(--negro-60);margin:0 0 clamp(24px,3vw,36px)}
.pv h2{font-size:clamp(17px,1.3vw,19px);font-weight:700;margin:28px 0 6px}
.pv p{font-size:16px;line-height:1.6;margin:0;max-width:62ch}
@media (min-width:1800px){.pv{zoom:1.2}}
</style>'''
body = ''.join(f'<h2>{h}</h2><p>{t}</p>' for h, t in TEXT)
main = f'''<main id="top" class="pv wrap">
  <span class="pv-eye">Privacidad</span><h1>Tu privacidad</h1><p class="pv-date">Última actualización: {FECHA}</p>
  {body}
</main>'''
a = s.index('<main id="top">'); b = s.index('</main>', a) + 7; s = s[:a] + main + s[b:]
s = s.replace('</head>', CSS + f'<link rel="canonical" href="{B}/privacidad">\n</head>', 1)
a = s.index('/* =====================================================================\n   RECETAS'); b = s.index('</script>', a)
s = s[:a] + "(function(){const n=document.getElementById('nav');if(n)document.documentElement.style.setProperty('--navh',n.offsetHeight+'px')})();\n" + s[b:]
s = re.sub(r'<style>\.t-page\{[^<]*</style>\n', '', s)
open(SITE + 'privacidad.html', 'w').write(hoist(s)); print('ok privacidad')
