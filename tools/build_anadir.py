"""Builds site/equipo/tienda.html (served at /equipo/tienda): private page for the team to add a store to the Dónde comprar map.
Not in the menu, the sitemap or Google (noindex). Paste a Google Maps link, see the store and its pin, pick the type, confirm.
Talks to the Apps Script web app of the sheet "Tres Naranjos: tiendas del mapa" (SCRIPT_URL below)."""
from hoist_meta import hoist
import team_gate
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS, SITE = ROOT + 'tools/', ROOT + 'site/'

# Apps Script web app (Deploy > New deployment > Web app) of the stores sheet
SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbw8qShm5ziNHJrTbTOZC8eJ7ItsOH2Nw0Vz4nIYQ-AQcaH_YDvtSutR0_-YEDz1yPmw/exec'
MAPBOX_TOKEN = re.search(r"MAPBOX_TOKEN = '([^']+)'", open(SITE + 'donde-comprar.html').read()).group(1)

s = open(TOOLS + 'tragos_base.html').read()
s = re.sub(r'<title>.*?</title>', '<title>Añadir una tienda | Tres Naranjos</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Añadir una tienda al mapa de Dónde comprar.">', s, count=1)
s = re.sub(r'<link rel="canonical"[^>]*>\n?', '', s)
s = s.replace('<a href="recetas/" aria-current="page">', '<a href="recetas/">')

CSS = '''<style>
.eq-back{display:inline-flex;align-items:center;gap:6px;margin:0 0 18px;font-weight:700;font-size:15px;color:var(--negro);text-decoration:none}.eq-back:hover{color:#E04F12}
main#top.at{box-sizing:border-box;padding:calc(var(--navh,70px) + env(safe-area-inset-top,0px) + clamp(32px,3.2vw,44px)) var(--gutter,16px) clamp(40px,6vw,72px)}
.at-in{max-width:760px;margin:0 auto}
.at-eye{font-weight:700;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#E8561A}
.at h1{font-family:var(--display);font-size:clamp(34px,4.2vw,54px);line-height:.95;margin:0 0 .25em;text-transform:uppercase;text-wrap:balance}
.at-lead{font-size:clamp(15px,1.2vw,17px);line-height:1.5;margin:0 0 18px;color:var(--negro-60)}
.at-lead b{color:var(--negro)}
.at label.l{display:block;font-weight:700;font-size:15px;margin:0 0 8px}
.at-field{display:flex;gap:8px}
.at-field input{flex:1;min-width:0;font:500 16px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro);background:#fff;border:1.5px solid var(--negro);border-radius:999px;padding:.85em 1.2em;outline:none}
.at-field input:focus{border-color:#E8561A}
.at-btn{display:inline-flex;align-items:center;justify-content:center;gap:.5em;min-height:50px;padding:.8em 1.5em .7em;border:0;border-radius:999px;font:700 14px "Hanken Grotesk",system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;text-decoration:none}
.at-btn.go{background:#EE5F1C;color:var(--crema)}
.at-btn.go:hover{background:#F26F31}
.at-btn.dark{background:var(--negro);color:var(--crema)}
.at-btn.dark:hover{background:#433D39}
.at-btn.soft{background:#F1D5B2;color:var(--negro)}
.at-btn.soft:hover{background:#F6E2C8}
.at-btn[disabled]{opacity:.45;cursor:default}
.at-btn:focus{outline:none}.at-btn:focus-visible{outline:2px solid #E8561A;outline-offset:3px}
.at-btn.go[disabled]:hover{background:#EE5F1C}
.at-msg{margin:10px 0 0;font-size:15px;line-height:1.5}.at-msg:empty{display:none}
.at-msg.err{color:#B3361A;font-weight:600}
.at-wait{display:flex;align-items:center;gap:10px;color:var(--negro-60)}
.at-wait i{width:16px;height:16px;border-radius:50%;border:2px solid #F1D5B2;border-top-color:#E8561A;animation:atspin .8s linear infinite}
@keyframes atspin{to{transform:rotate(360deg)}}
.at-card{margin-top:16px;border:1.5px solid var(--negro);border-radius:18px;overflow:hidden;background:#fff;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr)}
.at-mapbox{position:relative;min-height:260px;background:#F6E2C8;border-right:1.5px solid var(--negro)}.at-mapbox img{position:absolute;inset:0;display:block;width:100%;height:100%;object-fit:cover}
.at-info{padding:18px 20px 20px;min-width:0}
.at-info .q{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--negro-60);margin:0 0 6px}
.at-info .n{font-weight:700;font-size:21px;line-height:1.25;margin:0}
.at-info .a{font-size:15px;line-height:1.45;margin:4px 0 0;color:var(--negro-60)}
.at-tipos{margin:16px 0 0}
.at-tipos legend{font-weight:700;font-size:14px;margin:0 0 8px;padding:0}
.at-tipos fieldset{border:0;margin:0;padding:0;min-width:0}
.at-tipos label{margin:0 6px 8px 0;display:inline-flex;align-items:center;min-height:38px;padding:0 1em;border-radius:999px;background:#F6E2C8;font-weight:600;font-size:15px;cursor:pointer;user-select:none}
.at-tipos label:hover{background:#F9EAD6}
.at-tipos input{position:absolute;opacity:0;pointer-events:none}
.at-tipos label:has(input:checked){background:var(--negro);color:var(--crema)}
.at-tipos input:focus-visible+span{outline:2px solid #E8561A;outline-offset:4px;border-radius:4px}
.at-acts{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
.at-done{margin-top:16px;padding:22px 20px;border-radius:18px;background:#F6E2C8}
.at-done h2{font-family:var(--display);font-size:clamp(30px,4vw,42px);line-height:1;margin:0 0 .3em;text-transform:uppercase}
.at-done p{margin:0 0 16px;line-height:1.5}
.at-help{margin-top:28px;padding-top:16px;border-top:1.5px dashed var(--negro);font-size:15px;line-height:1.55;color:var(--negro-60)}
.at-help b{color:var(--negro)}
.at-help ol{margin:8px 0 0;padding-left:1.2em}
.at-add{width:100%;margin-top:8px}
@media (max-width:640px){.at-card{grid-template-columns:1fr}.at-mapbox{min-height:0;aspect-ratio:5/2;border-right:0;border-bottom:1.5px solid var(--negro)}.at-info{padding:14px 16px 16px}.at-info .n{font-size:19px}.at-field .at-btn,.at-acts .at-btn{width:auto}}
@media (max-width:420px){.at-acts .at-btn{width:100%}}
</style>'''

main = '''<main id="top" class="at"><div class="at-in">
''' + team_gate.html('Añadir una tienda') + '''
<a class="eq-back" href="equipo/"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>Equipo</a>
<div id="team-app" hidden>
  <h1>Añadir una tienda</h1>
  <p class="at-lead">Pega el link de Google Maps de la tienda para añadirla al mapa de <b>Dónde comprar</b>.</p>

  <form id="at-form" autocomplete="off" novalidate>
    <label class="l" for="at-link">Link de Google Maps</label>
    <div class="at-field">
      <input id="at-link" type="url" inputmode="url" placeholder="https://maps.app.goo.gl/..." required>
      <button class="at-btn dark" id="at-buscar" type="submit">Buscar</button>
    </div>
  </form>
  <p class="at-msg" id="at-msg" role="status" aria-live="polite"></p>

  <div id="at-res" hidden>
    <div class="at-card">
      <div class="at-mapbox"><img id="at-map" alt=""></div>
      <div class="at-info">
        <p class="q">¿Es esta la tienda?</p>
        <p class="n" id="at-name"></p>
        <p class="a" id="at-addr"></p>
        <div class="at-tipos"><fieldset><legend>Tipo de tienda</legend>
          <label><input type="radio" name="tipo" value="Licorería"><span>Licorería</span></label>
          <label><input type="radio" name="tipo" value="Supermercado"><span>Supermercado</span></label>
          <label><input type="radio" name="tipo" value="Cash &amp; Carry"><span>Cash &amp; Carry</span></label>
          <label><input type="radio" name="tipo" value="Tienda"><span>Tienda</span></label>
        </fieldset></div>
        <button class="at-btn go at-add" id="at-si" type="button">Sí, añadir al mapa</button>
        <p class="at-msg" id="at-msg2" role="status" aria-live="polite"></p>
      </div>
    </div>
  </div>

  <div class="at-done" id="at-done" hidden>
    <h2>¡Listo!</h2>
    <p id="at-done-txt"></p>
    <div class="at-acts" style="margin-top:0">
      <button class="at-btn go" id="at-otra" type="button">Añadir otra</button>
    </div>
  </div>

  <div class="at-help">
    <b>¿Cómo copio el link?</b>
    <ol>
      <li>Busca la tienda en Google Maps y ábrela (que salga su nombre y su foto).</li>
      <li>Toca <b>Compartir</b> y luego <b>Copiar enlace</b>.</li>
      <li>Pégalo aquí arriba.</li>
    </ol>
    <p style="margin:12px 0 0">Solo tiendas donde se compra la botella (licorerías, supermercados, cash &amp; carry). Para quitar una tienda, borra su fila en el <a href="https://docs.google.com/spreadsheets/d/15rUOE9lmcXHpuN0paVIG2eGAeZwaiGeAVqqqK9mEvdA/edit" target="_blank" rel="noopener" style="color:inherit;font-weight:700;text-underline-offset:3px">Google Sheet</a>.</p>
  </div>
</div>
</div></main>'''

JS = '''<script>
(function(){
  const SCRIPT_URL = %s, TOKEN = %s;
  const $ = id => document.getElementById(id);
  const LISTO_MIN = 5; /* measured Oct 2026: the published sheet updates in seconds; Google promises within 5 minutes */
  const form = $('at-form'), input = $('at-link'), msg = $('at-msg'), res = $('at-res'), done = $('at-done');
  let current = null, busy = false;
  const say = (html, err) => { msg.className = 'at-msg' + (err ? ' err' : ''); msg.innerHTML = html; };
  const wait = t => say('<span class="at-wait"><i></i>' + t + '</span>');
  const say2 = (html, err) => { const m = $('at-msg2'); m.className = 'at-msg' + (err ? ' err' : ''); m.innerHTML = html; };
  const esc = s => String(s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const linkOf = v => (String(v).match(/https?:\\/\\/\\S+/) || [''])[0];
  const call = p => fetch(SCRIPT_URL + '?' + new URLSearchParams(p)).then(r => r.json());

  function reset(keepLink){ current = null; res.hidden = true; done.hidden = true; say(''); say2(''); if(!keepLink){ input.value = ''; }
    document.querySelectorAll('input[name=tipo]').forEach(r => r.checked = false); $('at-si').disabled = true; }

  function buscar(){
    const link = linkOf(input.value);
    reset(true);
    if (!link) return say('Pega el link que copiaste de Google Maps (empieza con https://).', true);
    if (!SCRIPT_URL) return say('Esta página todavía no está conectada a la hoja.', true);
    busy = true; $('at-buscar').disabled = true; wait('Buscando la tienda… puede tardar unos segundos.');
    call({accion:'ver', link}).then(d => {
      if (!d.ok) return say('No pudimos encontrar esa tienda con ese link. Ábrela en Google Maps (que salga su nombre), toca Compartir y copia el link otra vez.', true);
      const t = d.tienda, ll = t.ll.split(',').map(Number);
      current = {link, t};
      $('at-name').textContent = t.nombre;
      $('at-addr').textContent = [t.dir, t.pueblo].filter(Boolean).join(', ');
      $('at-map').src = 'https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/pin-l+e8561a(' + ll[1] + ',' + ll[0] + ')/' + ll[1] + ',' + ll[0] + ',15.5/600x520@2x?logo=false&access_token=' + TOKEN;
      $('at-map').alt = 'Mapa de ' + t.nombre;
      res.hidden = false;
      if (res.getBoundingClientRect().top > innerHeight * .6) res.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion:reduce)').matches ? 'auto' : 'smooth', block: 'start'});
      say(''); say2(d.ya ? 'Esta tienda ya está en el mapa (<b>' + esc(d.ya) + '</b>).' : '', !!d.ya);
      current.ya = !!d.ya; syncAdd();
    }).catch(() => say('No pudimos conectarnos. Revisa tu internet y vuelve a intentar.', true))
      .finally(() => { busy = false; $('at-buscar').disabled = false; });
  }

  const tipoSel = () => (document.querySelector('input[name=tipo]:checked') || {}).value;
  function syncAdd(){ $('at-si').disabled = busy || !current || current.ya || !tipoSel(); }
  document.querySelectorAll('input[name=tipo]').forEach(r => r.addEventListener('change', () => { say2(''); syncAdd(); }));
  /* clearing or changing the link hides the old store */
  input.addEventListener('input', () => { if (!current && done.hidden) return; if (linkOf(input.value) !== (current && current.link)) { reset(true); } });
  form.addEventListener('submit', e => { e.preventDefault(); if (!busy) buscar(); });
  input.addEventListener('paste', () => setTimeout(() => { if (!busy && linkOf(input.value)) buscar(); }, 0));
  $('at-otra').addEventListener('click', () => { reset(false); input.focus(); });
  $('at-si').addEventListener('click', () => {
    if (!current || busy) return;
    const tipo = tipoSel();
    if (!tipo) return;
    busy = true; $('at-si').disabled = true; say2('<span class="at-wait"><i></i>Añadiendo…</span>');
    call({accion:'anadir', link: current.link, tipo, clave: window.tnClave()}).then(d => {
      if (d.ok) { res.hidden = true; say2(''); input.value = ''; const listo = new Date(Date.now() + LISTO_MIN * 60000);
        $('at-done-txt').innerHTML = '<b>' + esc(d.tienda.nombre) + '</b> sale en el mapa no más tarde de las <b>' + listo.toLocaleTimeString('es-PR', {hour: 'numeric', minute: '2-digit'}) + '</b>.'; done.hidden = false; return; }
      if (d.error === 'clave') return window.tnLock();
      if (d.error === 'ya_esta') return say2('Esa tienda ya está en el mapa (' + esc(d.ya) + ').', true);
      say2('No se pudo añadir. Vuelve a intentar en un momento.', true);
    }).catch(() => say2('No pudimos conectarnos. Revisa tu internet y vuelve a intentar.', true))
      .finally(() => { busy = false; if (done.hidden) syncAdd(); });
  });
})();
</script>''' % (repr(SCRIPT_URL), repr(MAPBOX_TOKEN))

a = s.index('<main id="top">'); b = s.index('</main>', a) + 7; s = s[:a] + main + s[b:]
s = s.replace('<head>', '<head>\n<base href="/">\n' + team_gate.HEAD, 1)
s = s.replace('</head>', CSS + team_gate.CSS + '<meta name="robots" content="noindex, nofollow">\n</head>', 1)
a = s.index('/* =====================================================================\n   RECETAS'); b = s.index('</script>', a)
s = s[:a] + "(function(){const n=document.getElementById('nav');if(!n)return;const f=()=>document.documentElement.style.setProperty('--navh',n.offsetHeight+'px');f();addEventListener('load',f);addEventListener('resize',f);if(document.fonts)document.fonts.ready.then(f)})();\n" + s[b:]
s = re.sub(r'<style>\.t-page\{[^<]*</style>\n', '', s)
s = s.replace('</body>', team_gate.js(SCRIPT_URL, 'team-app') + JS + '\n</body>', 1)
os.makedirs(SITE + 'equipo', exist_ok=True); open(SITE + 'equipo/tienda.html', 'w').write(hoist(team_gate.admin_header(team_gate.no_footer(s)))); print('ok equipo/tienda')
