"""Builds site/equipo/receta.html (served at /equipo/receta): private page for the team to publish a new recipe (password first, see team_gate.py).
Flow: 1) paste the recipe as text  2) "Así va a quedar": the recipe cleaned up, looking like the site, photo beside it,
one Editar that turns it into plain text  3) Publicar  4) ¡Publicada!
Cleanup: Claude (Apps Script accion=limpiar, when ANTHROPIC_API_KEY is set in the script) or the rules in this page.
Publishing goes to the same Apps Script (doPost accion=receta): photo to Drive, row in the Recetas tab, GitHub rebuild.
Not in the menu, the sitemap or Google (noindex)."""
from hoist_meta import hoist
import json, re, os
import team_gate
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS, SITE = ROOT + 'tools/', ROOT + 'site/'
SCRIPT_URL = re.search(r"SCRIPT_URL = '([^']+)'", open(TOOLS + 'build_anadir.py').read()).group(1)

s = open(TOOLS + 'tragos_base.html').read()
s = re.sub(r'<title>.*?</title>', '<title>Añadir una receta | Tres Naranjos</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Publicar una receta nueva en Tres Naranjos.">', s, count=1)
s = re.sub(r'<link rel="canonical"[^>]*>\n?', '', s)
s = s.replace('<a href="recetas/" aria-current="page">', '<a href="recetas/">')

CSS = '''<style>
.eq-back{display:inline-flex;align-items:center;gap:6px;margin:0 0 18px;font-weight:700;font-size:15px;color:var(--negro);text-decoration:none}.eq-back:hover{color:#E04F12}
main#top.ar{box-sizing:border-box;padding:calc(var(--navh,70px) + env(safe-area-inset-top,0px) + clamp(32px,3.2vw,44px)) var(--gutter,16px) clamp(40px,6vw,72px)}
.ar-in{max-width:1060px;margin:0 auto}
.ar h1{font-family:var(--display);font-size:clamp(34px,4.2vw,54px);line-height:.95;margin:0 0 .25em;text-transform:uppercase}
.ar-lead{font-size:clamp(15px,1.2vw,17px);line-height:1.5;margin:0 0 20px;color:var(--negro-60);max-width:62ch}
.ar .l{display:block;font-weight:700;font-size:15px;margin:0 0 8px}
.ar textarea{box-sizing:border-box;width:100%;resize:vertical;font:400 15px/1.6 "Courier Prime",monospace;color:var(--negro);background:#fff;border:1.5px solid var(--negro);border-radius:18px;padding:16px 18px;outline:none}
.ar textarea:focus{border-color:#E8561A}
#pega{min-height:clamp(260px,42vh,420px)}
.hint{margin:8px 0 0;font-size:14px;color:var(--negro-60)}
.btn-a{display:inline-flex;align-items:center;justify-content:center;gap:.5em;min-height:50px;padding:.8em 1.7em .7em;border:0;border-radius:999px;font:700 14px "Hanken Grotesk",system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;text-decoration:none}
.btn-a.go{background:#EE5F1C;color:var(--crema)}.btn-a.go:hover{background:#F26F31}
.btn-a.dark{background:var(--negro);color:var(--crema)}.btn-a.dark:hover{background:#433D39}
.btn-a.soft{background:#F1D5B2;color:var(--negro)}.btn-a.soft:hover{background:#F6E2C8}
.btn-a.sm{min-height:40px;padding:0 1.2em;font-size:13px}
.btn-a[disabled]{opacity:.45;cursor:default}.btn-a.go[disabled]:hover{background:#EE5F1C}
.btn-a:focus{outline:none}.btn-a:focus-visible{outline:2px solid #E8561A;outline-offset:3px}
.btn-a svg{width:15px;height:15px}
.link{font:600 15px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro);background:none;border:0;padding:0;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.link:hover{color:#E04F12}
.acts{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-top:18px}
.msg{margin:12px 0 0;font-size:15px;line-height:1.5}.msg:empty{display:none}.msg.err{color:#B3361A;font-weight:600}
.wait{display:inline-flex;align-items:center;gap:10px;color:var(--negro-60)}
.wait i{width:16px;height:16px;border-radius:50%;border:2px solid #F1D5B2;border-top-color:#E8561A;animation:arspin .8s linear infinite}
@keyframes arspin{to{transform:rotate(360deg)}}
.pv-top{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin:0 0 14px}
.pv-top .eye{display:block;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--negro-60);margin:0 0 4px}
.pv-top p{margin:0;font-size:15px;color:var(--negro-60);line-height:1.45}
.rx-card{border:1.5px solid var(--negro);border-radius:22px;background:#fff;padding:clamp(16px,2.2vw,28px);display:grid;grid-template-columns:minmax(0,380px) minmax(0,1fr);gap:clamp(20px,4vw,52px);align-items:start}
.ph{position:relative;aspect-ratio:4/5;border-radius:16px;overflow:hidden}
.ph-col{display:grid;gap:10px;min-width:0;align-content:start}
.ai-wait,.ai-err{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;text-align:center;padding:20px;border-radius:16px}
.ai-wait{background:linear-gradient(110deg,#F6E2C8 20%,#FBEEDC 40%,#F6E2C8 60%) 0 0/250% 100%;animation:aishim 1.6s linear infinite}
.ai-wait b,.ai-err b{font-size:17px}.ai-wait span{font-size:14px;color:var(--negro-60);max-width:24ch;line-height:1.4}
.ai-err{background:#FFFBF5;border:1.5px dashed #E8561A}
.ai-spin{width:30px;height:30px;border-radius:50%;border:3px solid rgba(45,41,38,.15);border-top-color:#E8561A;animation:arspin .9s linear infinite}
@keyframes aishim{to{background-position:-250% 0}}
@media (prefers-reduced-motion:reduce){.ai-wait{animation:none}.ai-spin{animation-duration:2.4s}}
.ai-tools{display:flex;gap:8px}
.ai-tools input{flex:1;min-width:0;box-sizing:border-box;font:500 15px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro);background:#fff;border:1.5px solid rgba(45,41,38,.35);border-radius:999px;padding:.7em 1em;outline:none}
.ai-tools input:focus{border-color:#E8561A}
.ai-tools .btn-a{white-space:nowrap}
.ai-up{justify-self:center;background:none;border:0;padding:4px;font:600 14px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro-60);text-decoration:underline;text-underline-offset:3px;cursor:pointer}
.ai-up:hover{color:#E04F12}

.rx-drop{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;text-align:center;padding:16px;border:1.5px dashed #E8561A;border-radius:16px;background:#FFFBF5;cursor:pointer}
.rx-drop:hover{background:#FFF6EA}
.rx-drop b{font-size:17px}.rx-drop span{font-size:14px;color:var(--negro-60)}
.rx-drop svg{width:38px;height:38px;color:#E8561A}
.rx-drop input{position:absolute;opacity:0;pointer-events:none;width:1px;height:1px}
.ph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ph-btns{position:absolute;left:12px;right:12px;bottom:12px;display:flex;gap:8px;justify-content:center}
.ph-btns .btn-a.soft{background:var(--crema)}
.ct{min-width:0;display:flex;flex-direction:column;gap:20px}
.ct h2{font-family:var(--display);font-size:clamp(34px,4vw,56px);line-height:.95;margin:0;text-transform:uppercase;text-wrap:balance;overflow-wrap:anywhere}
.ct .desc{margin:6px 0 0;font-size:17px;color:var(--negro-60)}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.tags span{padding:6px 12px;border-radius:999px;background:#F6E2C8;font-size:13px;font-weight:600}
.ct .sec{font-weight:700;font-size:15px;margin:0 0 6px}
.rx-ing{list-style:none;margin:0;padding:0;font-family:"Courier Prime",monospace;font-size:17px}
.rx-ing li{display:flex;justify-content:space-between;gap:14px;padding:10px 0;border-bottom:1px dotted rgba(45,41,38,.45);-webkit-text-stroke:.4px currentColor}
.rx-ing li.tn{color:#C2410C;font-weight:700;-webkit-text-stroke:0}
.rx-ing li b{white-space:nowrap}
.steps{margin:0;padding-left:1.4em;list-style:decimal;display:flex;flex-direction:column;gap:6px;font-size:16px;line-height:1.5}
.steps li{display:list-item}
#ed{min-height:470px;font-size:16px;line-height:1.6}
.ed-acts{display:flex;align-items:center;gap:16px;margin-top:10px}
.miss{font-size:14px;color:#B3361A;font-weight:600}
.done{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:clamp(20px,4vw,48px);align-items:start}
.done img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:16px;display:block}
.done-box{padding:clamp(20px,2.4vw,28px);border-radius:20px;background:#F6E2C8}
.done-box h2{font-family:var(--display);font-size:clamp(38px,4.4vw,52px);line-height:1;margin:0 0 .3em;text-transform:uppercase}
.done-box p{margin:0 0 10px;font-size:17px;line-height:1.5}
.done-box p.s{font-size:15px;color:rgba(45,41,38,.7);margin-bottom:18px}
@media (max-width:760px){
  .rx-card,.done{grid-template-columns:1fr}
  .ph-col,.done img{width:min(340px,100%);justify-self:center;margin:0}
  .ai-tools{flex-wrap:wrap}.ai-tools input,.ai-tools .btn-a{flex:1 1 100%}
  .pv-top{flex-direction:column;align-items:flex-start}
  #ed{min-height:380px}
  .acts .btn-a.go{flex:1}
}
</style>'''

CAM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg>'
PEN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16z"/></svg>'

main = f'''<main id="top" class="ar"><div class="ar-in">
{team_gate.html('Añadir una receta')}
<a class="eq-back" href="equipo/"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>Equipo</a>
<div id="team-app" hidden>

  <section id="s-pega">
    <h1>Añadir una receta</h1>
    <p class="ar-lead">Pega la receta y la arreglamos por ti. Antes de publicar, ves cómo va a quedar.</p>
    <label class="l" for="pega">Pega la receta</label>
    <textarea id="pega" spellcheck="false" placeholder="Paloma de toronja&#10;Fresca y fácil, para el calor.&#10;&#10;Ingredientes:&#10;- 2 oz tequila blanco&#10;- 15 ml Tres Naranjos&#10;- 3 oz jugo de toronja&#10;&#10;Preparación:&#10;1. Llena un vaso alto con hielo.&#10;2. Añade todo y completa con soda."></textarea>
    <p class="hint">De Claude, ChatGPT, una nota o WhatsApp. Las medidas en ml se pasan a oz.</p>
    <p class="msg" id="m1" role="status" aria-live="polite"></p>
    <div class="acts"><button type="button" class="btn-a go" id="llenar">Llenar la receta</button><button type="button" class="link" id="amano">Prefiero llenarla a mano</button></div>
  </section>

  <section id="s-prev" hidden>
    <div class="pv-top">
      <div><span class="eye">Así va a quedar</span><p id="nota"></p></div>
      <button type="button" class="btn-a soft sm" id="editar">{PEN}Editar</button>
    </div>
    <div class="rx-card">
      <div class="ph-col">
      <div class="ph" id="ph">
        <label class="rx-drop" id="drop"><input type="file" id="file" accept="image/*">{CAM}<b>Sube la foto</b><span>o arrástrala aquí · vertical, el trago en el centro</span></label>
        <img id="foto" alt="Foto del trago" hidden>
        <div class="ai-wait" id="ai-wait" hidden><span class="ai-spin" aria-hidden="true"></span><b>Creando la foto…</b><span>Unos 30 segundos. Mientras, revisa la receta.</span></div>
        <div class="ai-err" id="ai-err" hidden><b id="ai-err-t">No se pudo crear la foto.</b><button type="button" class="btn-a dark sm" id="ai-retry">Intentar otra vez</button></div>
        <div class="ph-btns" id="ph-btns" hidden><button type="button" class="btn-a soft sm" id="cambiar">Cambiar</button><button type="button" class="btn-a dark sm" id="quitar">Quitar</button></div>
      </div>
      <form class="ai-tools" id="ai-tools" autocomplete="off" hidden><input id="ai-cambio" maxlength="200" placeholder="¿Qué le cambiarías? (opcional)" aria-label="Qué le cambiarías a la foto"><button type="submit" class="btn-a soft sm" id="ai-otra">Otra versión</button></form>
      <button type="button" class="ai-up" id="ai-subir" hidden>o sube tu foto</button>
      </div>
      <div class="ct" id="view">
        <div>
          <h2 id="v-name"></h2>
          <p class="desc" id="v-desc"></p>
          <div class="tags" id="v-tags"></div>
        </div>
        <div><p class="sec">Ingredientes</p><ul class="rx-ing" id="v-ing"></ul></div>
        <div><p class="sec">Pasos</p><ol class="steps" id="v-steps"></ol></div>
      </div>
      <div class="ct" id="edit" hidden>
        <div>
          <label class="l" for="ed">Editar la receta</label>
          <textarea id="ed" spellcheck="false"></textarea>
          <div class="ed-acts"><button type="button" class="btn-a dark sm" id="listo">Listo</button><button type="button" class="link" id="cancelar">Cancelar</button></div>
        </div>
      </div>
    </div>
    <div class="acts"><button type="button" class="btn-a go" id="publicar">Publicar</button><span class="miss" id="miss"></span></div>
    <p class="msg" id="m2" role="status" aria-live="polite"></p>
  </section>

  <section id="s-done" hidden>
    <div class="done">
      <img id="d-foto" alt="">
      <div class="done-box">
        <h2>¡Publicada!</h2>
        <p id="d-txt"></p>
        <p class="s">Para cambiarla o quitarla después, se hace en la hoja de recetas.</p>
        <button type="button" class="btn-a go" id="otra">Añadir otra</button>
      </div>
    </div>
  </section>

</div>
</div></main>'''

JS = r'''<script>
(function(){
  const SCRIPT_URL = %s;
  const $ = id => document.getElementById(id);
  const esc = s => String(s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const norm = s => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
  const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
  const isTN = s => /\b(tres|3)\s*naranjos?\b/.test(norm(s));
  const VASOS = ['Vaso corto','Vaso alto','Copa','Copa de vino','Copa o shot','Flauta','Jarra'];
  const SHORT = {'Vaso corto':'corto','Vaso alto':'alto'};
  let R = null, photo = null, photoUrl = null, aiGen = 0, aiBusy = false, busy = false, fixes = [];

  function fmtA(x){ let w = Math.floor(x), f = Math.round((x - w) * 4) / 4; if (f === 1) { w++; f = 0; }
    const fr = {0:'', .25:'1/4', .5:'1/2', .75:'3/4'}[f]; return ((w ? w : '') + (w && fr ? ' ' : '') + fr) || '1/4'; }
  function num(t){ t = t.trim().replace(',', '.'); let m;
    if ((m = t.match(/^(\d+)\s+(\d)\/(\d)$/))) return +m[1] + m[2] / m[3];
    if ((m = t.match(/^(\d)\/(\d)$/))) return m[1] / m[2];
    if (/^\d+(\.\d+)?$/.test(t)) return +t; return null; }
  const N = '(\\d+\\s+\\d\\/\\d|\\d\\/\\d|\\d+(?:[.,]\\d+)?)';
  const U = '(oz|onzas?|ml|mililitros?|cl)\\.?';
  const PRE = new RegExp('^' + N + '\\s*' + U + '\\s+(?:de\\s+)?(.+)$', 'i');
  const POST = new RegExp('^(.+?)\\s*[:\\-,]?\\s*' + N + '\\s*' + U + '$', 'i');
  const BARE = new RegExp('^' + N + '\\s+(.+)$');

  function ingLine(line, inSection){
    let a = '', n = line, m, unit = 'oz', q = null;
    if ((m = line.match(PRE))) { q = num(m[1]); unit = m[2].toLowerCase(); n = m[3]; }
    else if ((m = line.match(POST))) { n = m[1]; q = num(m[2]); unit = m[3].toLowerCase(); }
    else if (inSection && (m = line.match(BARE)) && num(m[1]) !== null && num(m[1]) <= 8) { q = num(m[1]); n = m[2]; }
    if (q !== null) {
      if (/^ml|^mili/.test(unit)) { q = q / 30; fixes.push('ml'); } else if (unit === 'cl') { q = q / 3; fixes.push('ml'); }
      a = fmtA(Math.max(.25, Math.round(q * 4) / 4));
    }
    n = n.replace(/\b(tres naranjos(\s+triple\s+sec)?|triple\s*sec|cointreau|licor de naranja)\b/ig, 'Tres Naranjos')
         .replace(/\bnaranjas\b/ig, 'chinas').replace(/\bnaranja\b/ig, 'china').replace(/\s+/g, ' ').trim();
    return {a, n: cap(n)};
  }

  function clean(raw){
    fixes = [];
    const lines = String(raw || '').replace(/\r/g, '').replace(/\s*[—–]\s*/g, ', ')
      .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, '').split('\n')
      .map(l => l.replace(/\*\*|__|`/g, '').replace(/^\s*(#+|[-*•·>]+)\s*/, '').replace(/\s+/g, ' ').trim());
    const ING = /^(ingredientes?|lo que necesitas|necesitas)\s*:?\s*(.*)$/i;
    const PAS = /^(pasos?|preparaci[oó]n|instrucciones|modo de preparaci[oó]n|elaboraci[oó]n|c[oó]mo (se )?(hace|prepara)(lo)?)\s*:?\s*(.*)$/i;
    const META = /^vaso\s*:/i;
    const VERB = /^(llena|añade|anade|agrega|agita|cuela|sirve|mezcla|echa|echale|pon|decora|revuelve|vierte|corta|escarcha|exprime|licua|licúa|completa|termina|enfria|enfría|bate|refrigera|pica|machaca|frota|pasa|usa|deja|tapa|sacude)\b/i;
    // one-line message ("paloma: 2oz tequila, 15ml triple sec, ... echale hielo ...") -> split it
    const filled = lines.filter(Boolean);
    if (filled.length === 1 && /[:,]/.test(filled[0])) {
      const one = filled[0], c = one.indexOf(':'), nm = c > 0 && c < 40 ? one.slice(0, c) : '';
      const rest = nm ? one.slice(c + 1) : one, sent = rest.split(/\.\s+|\.$/).map(x => x.trim()).filter(Boolean);
      lines.length = 0; if (nm) lines.push(nm);
      lines.push('Ingredientes'); (sent[0] || '').split(/,|\s+y\s+/).forEach(x => x.trim() && lines.push(x.trim()));
      if (sent.length > 1) { lines.push('Pasos'); sent.slice(1).forEach(x => lines.push(x)); }
    }
    const head = [], ing = [], steps = []; let mode = 'head', meta = '';
    for (const l of lines) {
      if (!l) continue; let m;
      if (META.test(l)) { meta = l; continue; }
      if ((m = l.match(ING))) { mode = 'ing'; if (m[2]) m[2].split(/[,;]/).forEach(x => x.trim() && ing.push(x.trim())); continue; }
      if ((m = l.match(PAS))) { mode = 'pas'; const rest = m[m.length - 1]; if (rest) steps.push(rest); continue; }
      if (mode === 'head') {
        if (head.length >= 1 && (PRE.test(l) || POST.test(l))) { mode = 'ing'; ing.push(l); }
        else if ((/^(paso\s*)?\d+\s*[.)]\s+\D/i.test(l) || VERB.test(l)) && head.length >= 1) { mode = 'pas'; steps.push(l); }
        else head.push(l);
      } else if (mode === 'ing') {
        if ((/^(paso\s*)?\d+\s*[.)]\s+\D/i.test(l) && !PRE.test(l)) || (VERB.test(l) && !PRE.test(l) && !POST.test(l))) { mode = 'pas'; steps.push(l); }
        else ing.push(l);
      } else steps.push(l);
    }
    const name = cap((head[0] || '').replace(/[.:]$/, '').trim());
    const desc = head[1] && head[1].length <= 90 ? cap(head[1].replace(/\.$/, '')) + '.' : '';
    if (head.length > 2 && !steps.length) steps.push(...head.slice(2));
    if (steps.some(x => /^(paso\s*)?\d+\s*[.)]/i.test(x))) fixes.push('num');
    const pasos = steps.map(x => x.replace(/^(paso\s*)?\d+\s*[.):\-]\s*/i, '').trim()).filter(Boolean)
      .map(x => { x = cap(x); return /[.!?]$/.test(x) ? x : x + '.'; });
    const ingr = ing.map(l => ingLine(l, true)).filter(x => x.n);

    const all = norm(raw); let vaso = '', tags = [], serves = 1, m2;
    if (meta) {
      const v = (meta.match(/vaso\s*:\s*([^·|]+)/i) || [])[1]; if (v) { const t = norm(v); vaso = VASOS.find(x => norm(x) === t || norm(SHORT[x] || '') === t) || ''; }
      const sb = (meta.match(/sabor\s*:\s*([^·|]+)/i) || [])[1]; if (sb) tags = sb.split(/,|\by\b/).map(x => cap(x.trim())).filter(Boolean).slice(0, 2);
      const pr = (meta.match(/porciones\s*:\s*(\d+)/i) || [])[1]; if (pr) serves = Math.min(20, +pr);
    }
    if (!vaso) vaso = /vaso alto|highball|collins/.test(all) ? 'Vaso alto' : /copa de vino|wine/.test(all) ? 'Copa de vino' : /flauta|champ|mimosa/.test(all) ? 'Flauta'
      : /jarra|pitcher|ponchera/.test(all) ? 'Jarra' : /shot/.test(all) ? 'Copa o shot' : /\bcopa\b|coupe|martini/.test(all) ? 'Copa' : 'Vaso corto';
    if (!tags.length) {
      const score = [['Cítrico',/lima|limon|toronja|china/],['Burbujeante',/soda|prosecco|cava|champ|espumoso|tonica|ginger/],['Tropical',/parcha|pina|coco|mango|guayaba|tamarindo/],
        ['Frutal',/fresa|frambuesa|arandano|fruta|sangria|melocoton/],['Ahumado',/mezcal|ahumad/],['Picantito',/tajin|picante|jalapeno|chile/],['Fresco',/hierbabuena|menta|pepino|albahaca/]];
      tags = score.filter(([, re]) => re.test(all)).map(([t]) => t).slice(0, 2);
      if (tags.length < 2) tags.push(...['Refrescante', 'Cítrico'].filter(t => !tags.includes(t)).slice(0, 2 - tags.length));
    }
    if (!meta && (m2 = all.match(/(\d+)\s*(porciones|personas)/))) serves = Math.min(20, +m2[1]);
    return {nombre: name, descripcion: desc, vaso, etiquetas: tags, porciones: serves, ing: ingr, pasos};
  }

  function toText(r){
    const meta = 'Vaso: ' + (SHORT[r.vaso] || r.vaso) + ' · Sabor: ' + r.etiquetas.join(', ') + (r.porciones > 1 ? ' · Porciones: ' + r.porciones : '');
    return [r.nombre, r.descripcion, meta, '', 'Ingredientes', ...r.ing.map(x => (x.a ? x.a + ' oz ' : '') + x.n), '', 'Pasos', ...r.pasos.map((p, i) => (i + 1) + '. ' + p)].join('\n');
  }
  function fromAI(a){
    const r = {nombre: a.nombre || '', descripcion: a.descripcion || '', vaso: a.vaso || 'Vaso corto', etiquetas: (a.etiquetas || []).slice(0, 2), porciones: a.porciones || 1,
      ing: (a.ingredientes || []).map(x => ({a: x.cantidad || '', n: x.ingrediente || ''})), pasos: a.pasos || []};
    const out = clean(toText(r)); fixes = []; return out;
  }

  const show = id => { ['s-pega','s-prev','s-done'].forEach(x => $(x).hidden = x !== id); scrollTo({top: 0}); };
  function render(){
    $('v-name').textContent = R.nombre || 'Sin nombre';
    $('v-desc').textContent = R.descripcion; $('v-desc').hidden = !R.descripcion;
    $('v-tags').innerHTML = [R.vaso, ...R.etiquetas, R.porciones > 1 ? R.porciones + ' porciones' : ''].filter(Boolean).map(t => '<span>' + esc(t) + '</span>').join('');
    $('v-ing').innerHTML = R.ing.map(x => '<li class="' + (isTN(x.n) ? 'tn' : '') + '"><span>' + esc(x.n) + '</span><b>' + (x.a ? esc(x.a) + ' oz' : '') + '</b></li>').join('');
    $('v-steps').innerHTML = R.pasos.map(p => '<li>' + esc(p) + '</li>').join('');
    check();
  }
  function problems(){
    const p = [];
    if (!photo && !photoUrl) p.push(aiBusy ? 'La foto se está creando.' : 'Falta la foto.');
    if (!R.nombre) p.push('Falta el nombre.');
    if (R.ing.length < 2) p.push('Faltan ingredientes.');
    else if (!R.ing.some(x => isTN(x.n))) p.push('La receta no lleva Tres Naranjos. Toca Editar y añádelo.');
    if (!R.pasos.length) p.push('Faltan los pasos.');
    return p;
  }
  function check(){ const p = problems(); $('miss').textContent = p.join(' '); $('publicar').disabled = !!p.length || busy; }
  function note(){
    const n = fixes.filter(x => x === 'ml').length, parts = [];
    if (n) parts.push(n === 1 ? 'una medida en ml pasó a oz' : n + ' medidas en ml pasaron a oz');
    if (R.pasos.length) parts.push('pasos numerados');
    return (parts.length ? 'Lo arreglamos: ' + parts.join(', ') + '. ' : '') + 'Si algo no quedó bien, toca Editar.';
  }
  const say = (id, h, err) => { const m = $(id); m.className = 'msg' + (err ? ' err' : ''); m.innerHTML = h; };

  $('llenar').addEventListener('click', async () => {
    const raw = $('pega').value.trim();
    if (!raw) return say('m1', 'Pega la receta primero.', true);
    if (busy) return; busy = true; $('llenar').disabled = true;
    let r = null, by = '';
    if (window.tnIA) {
      say('m1', '<span class="wait"><i></i>Claude está arreglando la receta…</span>');
      try {
        const ctl = new AbortController(), t = setTimeout(() => ctl.abort(), 25000);
        const res = await fetch(SCRIPT_URL, {method: 'POST', body: JSON.stringify({accion: 'limpiar', clave: window.tnClave(), texto: raw}), signal: ctl.signal}).then(x => x.json());
        clearTimeout(t);
        if (res.error === 'clave') { busy = false; $('llenar').disabled = false; say('m1', ''); return window.tnLock(); }
        if (res.ok) { r = fromAI(res.receta); by = 'ia'; }
      } catch (e) {}
    }
    if (!r) r = clean(raw);
    busy = false; $('llenar').disabled = false; say('m1', '');
    R = r; render();
    $('nota').textContent = by === 'ia' ? 'Claude la arregló y la puso en el formato del site. Si algo no quedó bien, toca Editar.' : note();
    view(); show('s-prev');
    if (window.tnFoto && !photo && !photoUrl) genPhoto('');
  });
  $('amano').addEventListener('click', () => {
    R = {nombre: '', descripcion: '', vaso: 'Vaso corto', etiquetas: ['Cítrico', 'Fresco'], porciones: 1, ing: [], pasos: []};
    render(); $('nota').textContent = 'Escribe la receta. Al tocar Listo la ponemos en el formato del site.';
    show('s-prev'); edit('Nombre del trago\nDescripción corta\nVaso: corto · Sabor: Cítrico, Fresco\n\nIngredientes\n1 1/2 oz \n1/2 oz Tres Naranjos\n\nPasos\n1. ');
  });

  function edit(text){ $('ed').value = text != null ? text : toText(R); $('view').hidden = true; $('edit').hidden = false; $('editar').hidden = true; $('ed').focus({preventScroll: true}); }
  function view(){ $('view').hidden = false; $('edit').hidden = true; $('editar').hidden = false; }
  $('editar').addEventListener('click', () => edit());
  $('cancelar').addEventListener('click', view);
  $('listo').addEventListener('click', () => { R = clean($('ed').value); fixes = []; render(); view();
    if (window.tnFoto && !photo && !photoUrl && !aiBusy && R.nombre) genPhoto(''); });

  let gx = .25;
  /* where the glass is in a wide AI photo (fraction of the width); same logic as glass_x() in tools/sync_recetas.py */
  function glassX(img){
    try {
      const w = 160, h = Math.max(1, Math.round(img.naturalHeight * w / img.naturalWidth)), c = document.createElement('canvas');
      c.width = w; c.height = h; const g = c.getContext('2d'); g.drawImage(img, 0, 0, w, h); const d = g.getImageData(0, 0, w, h).data;
      const ch = (x, y) => { const i = (y * w + x) * 4, t = d[i] + d[i + 1] + d[i + 2] + 1; return [d[i] / t, d[i + 1] / t, d[i + 2] / t]; };
      const bgs = [[], [], []];
      for (let y = 0; y < h; y++) for (let x = Math.floor(w * .75); x < w; x++) { const v = ch(x, y); bgs[0].push(v[0]); bgs[1].push(v[1]); bgs[2].push(v[2]); }
      const bg = bgs.map(a => a.sort((p, q) => p - q)[a.length >> 1]);
      const y0 = Math.floor(h * .4), y1 = Math.floor(h * .8), xs = Math.floor(w * .75), sc = [];
      for (let x = 0; x < xs; x++) { let n = 0; for (let y = y0; y < y1; y++) { const v = ch(x, y); if (Math.hypot(v[0] - bg[0], v[1] - bg[1], v[2] - bg[2]) * 100 > 6) n++; } sc.push(n / (y1 - y0)); }
      const mx = Math.max(...sc); if (mx < .15) return .25;
      let best = [0, 0, 0], st = -1;
      sc.concat([0]).forEach((v, i) => { const on = i < sc.length && v >= mx * .5; if (on && st < 0) st = i; if (!on && st >= 0) { if (i - st > best[0]) best = [i - st, st, i]; st = -1; } });
      return best[2] > best[1] ? ((best[1] + best[2]) / 2) / w : .25;
    } catch (e) { return .25; }
  }
  const ingList = () => R.ing.map(x => (x.a ? x.a + ' oz ' : '') + x.n);
  function fit(img){ const r = img.naturalWidth / img.naturalHeight; if (r <= 1.2) { img.style.objectPosition = '50%% 50%%'; return; }
    const f = .8 / r, x = Math.min(1, Math.max(0, (gx - f / 2) / (1 - f))); img.style.objectPosition = (x * 100).toFixed(1) + '%% 50%%'; } /* wide AI photo: crop centred on the glass (a quarter in), same as sync_recetas.py */
  $('foto').addEventListener('load', () => fit($('foto')));
  function photoState(st, msg){
    $('ai-wait').hidden = st !== 'wait'; $('ai-err').hidden = st !== 'err';
    if (st === 'err') $('ai-err-t').textContent = msg || 'No se pudo crear la foto.';
    const has = !!(photo || photoUrl); $('foto').hidden = !has;
    $('drop').hidden = has || !!window.tnFoto || st === 'wait';
    $('ph-btns').hidden = !photo;
    $('ai-tools').hidden = !photoUrl || st === 'wait';
    $('ai-subir').hidden = !window.tnFoto || !!photo || st === 'wait';
    $('ai-otra').disabled = aiBusy; if (R) check();
  }
  async function genPhoto(cambio){
    if (!R) return;
    const my = ++aiGen; aiBusy = true; $('ai-retry').textContent = 'Intentar otra vez'; photoState('wait');
    const fail = m => { if (my !== aiGen) return; aiBusy = false; photoState(photoUrl ? '' : 'err', m); if (photoUrl) say('m2', m || 'No se pudo crear otra versión.', true); };
    try {
      const r = await fetch(SCRIPT_URL, {method: 'POST', body: JSON.stringify({accion: 'fotoia', clave: window.tnClave(), nombre: R.nombre, vaso: R.vaso, ingredientes: ingList(), cambio: cambio || ''})}).then(x => x.json());
      if (r.error === 'clave') return window.tnLock();
      if (!r.ok) return fail(r.error === 'sin_saldo' ? 'Se acabó el saldo de Krea para fotos.' : '');
      for (let i = 0; i < 45; i++) {
        await new Promise(ok => setTimeout(ok, 3500));
        if (my !== aiGen) return;
        const e = await fetch(SCRIPT_URL + '?' + new URLSearchParams({accion: 'fotoestado', clave: window.tnClave(), job: r.job})).then(x => x.json()).catch(() => ({ok: true}));
        if (my !== aiGen) return;
        if (!e.ok) return fail('');
        if (e.listo) {
          const fd = await fetch(SCRIPT_URL + '?' + new URLSearchParams({accion: 'fotodatos', clave: window.tnClave(), url: e.url})).then(x => x.json()).catch(() => ({}));
          if (my !== aiGen) return;
          const src = fd.ok ? 'data:' + fd.mime + ';base64,' + fd.b64 : e.url;
          const im = new Image();
          im.onload = () => { if (my !== aiGen) return; gx = fd.ok ? glassX(im) : .25; photoUrl = e.url; photo = null; $('foto').src = src; aiBusy = false; say('m2', ''); photoState(''); };
          im.onerror = () => fail('');
          im.src = src; return;
        }
      }
      fail('La foto está tardando mucho.');
    } catch (err) { fail(''); }
  }
  $('ai-retry').addEventListener('click', () => genPhoto(''));
  $('ai-tools').addEventListener('submit', e => { e.preventDefault(); if (aiBusy) return; const c = $('ai-cambio').value.trim(); genPhoto(c); $('ai-cambio').value = ''; });
  $('ai-subir').addEventListener('click', () => $('file').click());
  function loadPhoto(file){
    if (!file || !/^image\//.test(file.type)) return;
    const img = new Image(), url = URL.createObjectURL(file);
    img.onload = () => {
      const k = Math.min(1, 1600 / Math.max(img.naturalWidth, img.naturalHeight));
      const c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * k); c.height = Math.round(img.naturalHeight * k);
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
      photo = c.toDataURL('image/jpeg', .86); URL.revokeObjectURL(url);
      aiGen++; aiBusy = false; photoUrl = null; $('foto').src = photo; photoState('');
    };
    img.src = url;
  }
  $('file').addEventListener('change', e => { loadPhoto(e.target.files[0]); e.target.value = ''; });
  $('cambiar').addEventListener('click', () => $('file').click());
  $('quitar').addEventListener('click', () => { photo = null; if (window.tnFoto) photoState('err', 'Sin foto.'), $('ai-retry').textContent = 'Crear foto con IA'; else photoState(''); });
  $('ph').addEventListener('dragover', e => e.preventDefault());
  $('ph').addEventListener('drop', e => { e.preventDefault(); loadPhoto(e.dataTransfer.files[0]); });

  $('publicar').addEventListener('click', () => {
    if (!$('edit').hidden) { R = clean($('ed').value); fixes = []; render(); view(); }
    if (problems().length || busy) return check();
    busy = true; check(); say('m2', '<span class="wait"><i></i>Publicando… puede tardar unos segundos.</span>');
    const body = {accion: 'receta', clave: window.tnClave(), nombre: R.nombre, descripcion: R.descripcion, vaso: R.vaso, etiquetas: R.etiquetas,
      porciones: R.porciones, pasos: R.pasos, ingredientes: ingList()};
    if (photoUrl) body.foto_url = photoUrl; else body.foto = photo.split(',')[1];
    fetch(SCRIPT_URL, {method: 'POST', body: JSON.stringify(body)}).then(r => r.json()).then(r => {
      if (r.ok) {
        const t = new Date(Date.now() + (r.rapido ? 10 : 35) * 60000).toLocaleTimeString('es-PR', {hour: 'numeric', minute: '2-digit'});
        $('d-foto').src = $('foto').src; fit($('d-foto')); $('d-txt').innerHTML = '<b>' + esc(r.nombre) + '</b> sale en Recetas no más tarde de las <b>' + t + '</b>' + (/\.$/.test(t) ? '' : '.');
        say('m2', ''); show('s-done'); return;
      }
      if (r.error === 'clave') return window.tnLock();
      say('m2', {sin_tn: 'La receta tiene que llevar Tres Naranjos.', ya_esta: 'Ya hay una receta con ese nombre. Cámbialo en Editar.', faltan: 'Faltan datos. Revisa la receta.'}[r.error] || 'No se pudo publicar. Vuelve a intentar en un momento.', true);
    }).catch(() => say('m2', 'No pudimos conectarnos. Revisa tu internet y vuelve a intentar.', true))
      .finally(() => { busy = false; check(); });
  });
  $('otra').addEventListener('click', () => {
    R = null; photo = null; photoUrl = null; aiGen++; aiBusy = false; $('ai-retry').textContent = 'Intentar otra vez'; $('pega').value = ''; photoState(''); view(); show('s-pega');
  });

  window.__tnClean = clean; window.__tnToText = toText;
})();
</script>''' % repr(SCRIPT_URL)

a = s.index('<main id="top">'); b = s.index('</main>', a) + 7; s = s[:a] + main + s[b:]
s = s.replace('<head>', '<head>\n<base href="/">\n' + team_gate.HEAD, 1)
s = s.replace('</head>', CSS + team_gate.CSS + '<meta name="robots" content="noindex, nofollow">\n</head>', 1)
a = s.index('/* =====================================================================\n   RECETAS'); b = s.index('</script>', a)
s = s[:a] + "(function(){const n=document.getElementById('nav');if(!n)return;const f=()=>document.documentElement.style.setProperty('--navh',n.offsetHeight+'px');f();addEventListener('load',f);addEventListener('resize',f);if(document.fonts)document.fonts.ready.then(f)})();\n" + s[b:]
s = re.sub(r'<style>\.t-page\{[^<]*</style>\n', '', s)
s = s.replace('</body>', team_gate.js(SCRIPT_URL, 'team-app') + JS + '\n</body>', 1)
os.makedirs(SITE + 'equipo', exist_ok=True); open(SITE + 'equipo/receta.html', 'w').write(hoist(team_gate.admin_header(team_gate.no_footer(s)))); print('ok equipo/receta')
