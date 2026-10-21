"""Builds site/equipo/index.html, served at /equipo: the ONE private link the team gets.
Asks for the password (team_gate.py), then lets you pick what to do: add a recipe (/equipo/receta),
add a store (/equipo/tienda), or open the Google Sheet to edit or remove. Not in the menu, sitemap or Google (noindex)."""
from hoist_meta import hoist
import team_gate
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS, SITE = ROOT + 'tools/', ROOT + 'site/'
SCRIPT_URL = re.search(r"SCRIPT_URL = '([^']+)'", open(TOOLS + 'build_anadir.py').read()).group(1)
SHEET_URL = 'https://docs.google.com/spreadsheets/d/15rUOE9lmcXHpuN0paVIG2eGAeZwaiGeAVqqqK9mEvdA/edit'

s = open(TOOLS + 'tragos_base.html').read()
s = re.sub(r'<title>.*?</title>', '<title>Equipo | Tres Naranjos</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Página del equipo de Tres Naranjos.">', s, count=1)
s = re.sub(r'<link rel="canonical"[^>]*>\n?', '', s)
s = s.replace('<a href="recetas/" aria-current="page">', '<a href="recetas/">')

CSS = '''<style>
main#top.eq{box-sizing:border-box;padding:calc(var(--navh,70px) + env(safe-area-inset-top,0px) + clamp(32px,3.2vw,44px)) var(--gutter,16px) clamp(40px,6vw,72px)}
.eq-in{max-width:880px;margin:0 auto}
.eq h1{font-family:var(--display);font-size:clamp(34px,4.2vw,54px);line-height:.95;margin:0 0 .3em;text-transform:uppercase;text-wrap:balance}
.eq-lead{font-size:clamp(15px,1.2vw,17px);line-height:1.5;margin:0 0 22px;color:var(--negro-60)}
.eq-pick{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.eq-card{display:grid;align-content:start;gap:10px;padding:clamp(20px,2.4vw,30px);border-radius:22px;background:#fff;border:1.5px solid var(--negro);color:var(--negro);text-decoration:none;min-height:190px;transition:background .15s}
.eq-card:hover{background:#FFFBF5}
.eq-card:focus{outline:none}.eq-card:focus-visible{outline:2px solid #E8561A;outline-offset:3px}
.eq-ico{width:52px;height:52px;border-radius:50%;background:#EE5F1C;color:var(--crema);display:grid;place-items:center}
.eq-ico svg{width:26px;height:26px}
.eq-card h2{font-family:var(--display);font-size:clamp(28px,2.8vw,38px);line-height:.95;margin:6px 0 0;text-transform:uppercase}
.eq-card p{margin:0;font-size:16px;line-height:1.45;color:var(--negro-60)}
.eq-go{margin-top:auto;padding-top:8px;font-weight:700;font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:#C2410C}
.eq-sheet{margin:22px 0 0;font-size:16px;line-height:1.5;color:var(--negro-60)}
.eq-sheet a{color:var(--negro);font-weight:700;text-underline-offset:3px}.eq-sheet a:hover{color:#E04F12}
.eq-wide{margin-top:14px;display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:18px;padding:clamp(18px,2vw,24px) clamp(20px,2.4vw,30px);border-radius:22px;background:#F6E2C8;color:var(--negro);text-decoration:none;transition:background .15s}
.eq-wide:hover{background:#F9EAD6}
.eq-wide:focus{outline:none}.eq-wide:focus-visible{outline:2px solid #E8561A;outline-offset:3px}
.eq-ico.soft{background:#188038}
.eq-wide h2{font-family:var(--display);font-size:clamp(24px,2.2vw,30px);line-height:.95;margin:0 0 4px;text-transform:uppercase}
.eq-wide p{margin:0;font-size:16px;line-height:1.45;color:var(--negro-60)}
.eq-open{display:inline-flex;align-items:center;min-height:46px;padding:0 22px;border-radius:999px;background:#188038;color:#fff;font-weight:700;font-size:14px;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap}
.eq-wide:hover .eq-open{background:#1E9445}
@media (max-width:640px){.eq-wide{grid-template-columns:auto minmax(0,1fr);align-items:start}.eq-open{grid-column:1/-1;justify-content:center}}
@media (max-width:640px){.eq-pick{grid-template-columns:1fr}.eq-card{min-height:0}}
</style>'''

GLASS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h14l-7 8z"/><path d="M12 12v8M8 20h8"/></svg>'
SHEET = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><rect x="8.5" y="11" width="7" height="6.5" rx=".5"/><path d="M8.5 14.2h7M12 11v6.5"/></svg>'
PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'

main = f'''<main id="top" class="eq"><div class="eq-in">
{team_gate.html('Equipo Tres Naranjos')}
<div id="eq-app" hidden>
  <h1>¿Qué quieres hacer?</h1>
  <p class="eq-lead">Todo lo que añadas aquí sale en tresnaranjos.com.</p>
  <div class="eq-pick">
    <a class="eq-card" href="equipo/receta"><span class="eq-ico">{GLASS}</span><h2>Añadir una receta</h2><p>Pega la receta, sube la foto, revisa cómo va a quedar y publica.</p><span class="eq-go">Empezar →</span></a>
    <a class="eq-card" href="equipo/tienda"><span class="eq-ico">{PIN}</span><h2>Añadir una tienda</h2><p>Pega el link de Google Maps de la tienda y escoge el tipo.</p><span class="eq-go">Empezar →</span></a>
  </div>
  <a class="eq-wide" href="{SHEET_URL}" target="_blank" rel="noopener"><span class="eq-ico soft">{SHEET}</span><span class="eq-wt"><h2>Editar o quitar en Google Sheet</h2><p>Cambia o esconde una receta, o borra una tienda. Todo está en el Google Sheet.</p></span><span class="eq-open">Abrir Google Sheet ↗</span></a>
</div>
</div></main>'''

a = s.index('<main id="top">'); b = s.index('</main>', a) + 7; s = s[:a] + main + s[b:]
s = s.replace('<head>', '<head>\n<base href="/">\n' + team_gate.HEAD, 1)
s = s.replace('</head>', CSS + team_gate.CSS + '<meta name="robots" content="noindex, nofollow">\n</head>', 1)
a = s.index('/* =====================================================================\n   RECETAS'); b = s.index('</script>', a)
s = s[:a] + "(function(){const n=document.getElementById('nav');if(!n)return;const f=()=>document.documentElement.style.setProperty('--navh',n.offsetHeight+'px');f();addEventListener('load',f);addEventListener('resize',f);if(document.fonts)document.fonts.ready.then(f)})();\n" + s[b:]
s = re.sub(r'<style>\.t-page\{[^<]*</style>\n', '', s)
s = s.replace('</body>', team_gate.js(SCRIPT_URL, 'eq-app', hub=True) + '\n</body>', 1)
os.makedirs(SITE + 'equipo', exist_ok=True)
open(SITE + 'equipo/index.html', 'w').write(hoist(team_gate.no_footer(s))); print('ok equipo')
