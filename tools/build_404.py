"""Builds site/404.html, the page Cloudflare shows for any address that doesn't exist
(wrangler.jsonc: "not_found_handling": "404-page"). Uses the shared header, footer and age gate."""
from hoist_meta import hoist
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS, SITE = ROOT + 'tools/', ROOT + 'site/'
s = open(TOOLS + 'tragos_base.html').read()
s = re.sub(r'<title>.*?</title>', '<title>Página no encontrada | Tres Naranjos</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Esta página no existe. Vuelve al inicio de Tres Naranjos o escoge un trago.">', s, count=1)
s = s.replace('<a href="tragos/" aria-current="page">', '<a href="tragos/">')
CSS = '''<style>
main#top.nf{min-height:calc(100svh - var(--navh,70px));box-sizing:border-box;display:grid;place-items:center;text-align:center;
  padding:calc(var(--navh,70px) + env(safe-area-inset-top,0px) + clamp(32px,6vw,72px)) var(--gutter,16px) clamp(56px,8vw,100px)}
.nf-in{max-width:560px}
.nf-ico{width:clamp(84px,12vw,120px);height:auto;margin:0 auto clamp(18px,2vw,26px);display:block;color:var(--negro)}
.nf-eye{font-family:var(--type);font-weight:700;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#E8561A}
.nf h1{font-family:var(--display);font-size:clamp(44px,6vw,80px);line-height:.95;margin:.2em 0 .35em;text-transform:uppercase}
.nf p{font-size:clamp(16px,1.3vw,18px);line-height:1.55;margin:0 auto 28px;max-width:40ch;color:var(--negro-60)}
.nf-ctas{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.nf-ctas a{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:.85em 1.6em .75em;border-radius:999px;font-weight:700;font-size:14px;letter-spacing:.06em;text-transform:uppercase;text-decoration:none}
.nf-ctas .a1{background:#EE5F1C;color:var(--crema)}
.nf-ctas .a1:hover{background:#F26F31}
.nf-ctas .a2{background:var(--negro);color:var(--crema)}
.nf-ctas .a2:hover{background:#433D39}
@media (max-width:700px){.nf-ctas{flex-direction:column}.nf-ctas a{width:100%;box-sizing:border-box}}
</style>'''
ICON = '<img class="nf-ico" src="assets/icon.webp" alt="">'
main = f'''<main id="top" class="nf"><div class="nf-in">
  {ICON}
  <span class="nf-eye">Error 404</span>
  <h1>Esta página no existe.</h1>
  <p>Se nos perdió esta naranja. Puede que el enlace esté mal escrito o que la página se haya movido.</p>
  <div class="nf-ctas"><a class="a1" href="./">Ir al inicio</a><a class="a2" href="tragos/">Ver los tragos</a></div>
</div></main>'''
a = s.index('<main id="top">'); b = s.index('</main>', a) + 7; s = s[:a] + main + s[b:]
# served at any address, so every link and asset is resolved from the site root
s = s.replace('<head>', '<head>\n<base href="/">', 1)
s = s.replace('</head>', CSS + '<meta name="robots" content="noindex">\n</head>', 1)
a = s.index('/* =====================================================================\n   RECETAS'); b = s.index('</script>', a)
s = s[:a] + "(function(){const n=document.getElementById('nav');if(n)document.documentElement.style.setProperty('--navh',n.offsetHeight+'px')})();\n" + s[b:]
s = re.sub(r'<style>\.t-page\{[^<]*</style>\n', '', s)
open(SITE + '404.html', 'w').write(hoist(s)); print('ok 404')
