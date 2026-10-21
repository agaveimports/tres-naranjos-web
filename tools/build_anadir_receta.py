"""Builds site/anadir-receta.html: private page for the team to publish a new recipe (photo required).
Not in the menu, the sitemap or Google (noindex). Sends the recipe to the Apps Script of the sheet
"Tres Naranjos: sitio web" (same SCRIPT_URL as anadir-tienda), which saves the photo in Drive, adds a row to the
Recetas tab and tells GitHub to rebuild (tools/sync_recetas.py)."""
from hoist_meta import hoist
import team_gate
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
TOOLS, SITE = ROOT + 'tools/', ROOT + 'site/'
SCRIPT_URL = re.search(r"SCRIPT_URL = '([^']+)'", open(TOOLS + 'build_anadir.py').read()).group(1)
LISTO_MIN = 15   # dispatch + GitHub job + Cloudflare publish; usually 3 to 5 minutes

VASOS = ['Vaso corto', 'Vaso alto', 'Copa', 'Copa de vino', 'Copa o shot', 'Flauta', 'Jarra']
TAGS = ['Cítrico', 'Fresco', 'Frutal', 'Tropical', 'Ácido', 'Agridulce', 'Burbujeante', 'Ligero', 'Refrescante',
        'Ahumado', 'Picantito', 'Seco', 'Robusto', 'Intenso', 'Almendrado']
AMTS = ['', '1/4', '1/2', '3/4', '1', '1 1/4', '1 1/2', '1 3/4', '2', '2 1/2', '3', '4', '6', '8']

s = open(TOOLS + 'tragos_base.html').read()
s = re.sub(r'<title>.*?</title>', '<title>Añadir una receta | Tres Naranjos</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Publicar una receta nueva en Tres Naranjos.">', s, count=1)
s = re.sub(r'<link rel="canonical"[^>]*>\n?', '', s)
s = s.replace('<a href="recetas/" aria-current="page">', '<a href="recetas/">')

CSS = '''<style>
main#top.ar{box-sizing:border-box;padding:calc(var(--navh,70px) + env(safe-area-inset-top,0px) + clamp(32px,3.2vw,44px)) var(--gutter,16px) clamp(40px,6vw,72px)}
.ar-in{max-width:980px;margin:0 auto}
.ar h1{font-family:var(--display);font-size:clamp(34px,4.2vw,54px);line-height:.95;margin:0 0 .25em;text-transform:uppercase}
.ar-lead{font-size:clamp(15px,1.2vw,17px);line-height:1.5;margin:0 0 20px;color:var(--negro-60)}
.ar-grid{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr);gap:clamp(20px,3vw,40px);align-items:start}
.ar-photo{position:sticky;top:calc(var(--navh,70px) + 16px)}
.ar-drop{display:grid;place-items:center;aspect-ratio:4/5;border:1.5px dashed var(--negro);border-radius:18px;background:#fff;cursor:pointer;overflow:hidden;position:relative;text-align:center;padding:16px}
.ar-drop:hover{background:#FFFBF5}
.ar-drop img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ar-drop .ph b{display:block;font-size:17px;margin:10px 0 4px}
.ar-drop .ph span{font-size:14px;color:var(--negro-60);line-height:1.45}
.ar-drop svg{width:38px;height:38px;color:#E8561A}
.ar-drop input{position:absolute;opacity:0;pointer-events:none}
.ar-change{display:block;margin:10px auto 0;font:600 14px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro);background:none;border:0;text-decoration:underline;text-underline-offset:3px;cursor:pointer}
.ar-f{display:grid;gap:16px;min-width:0}
.ar label.l,.ar .l{display:block;font-weight:700;font-size:15px;margin:0 0 7px}
.ar .l small{font-weight:400;color:var(--negro-60)}
.ar input[type=text],.ar input[type=password],.ar textarea,.ar select{box-sizing:border-box;width:100%;min-width:0;font:500 16px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro);background:#fff;border:1.5px solid var(--negro);border-radius:14px;padding:.7em .9em;outline:none}
.ar input[type=text]:focus,.ar input[type=password]:focus,.ar textarea:focus,.ar select:focus{border-color:#E8561A}
.ar textarea{resize:vertical;min-height:52px;line-height:1.45}
.ar-two{display:grid;grid-template-columns:minmax(0,1fr) 120px;gap:12px}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.chips label{display:inline-flex;align-items:center;min-height:36px;padding:0 .95em;border-radius:999px;background:#F6E2C8;font-weight:600;font-size:14px;cursor:pointer;user-select:none}
.chips label:hover{background:#F9EAD6}
.chips input{position:absolute;opacity:0;pointer-events:none}
.chips label:has(input:checked){background:var(--negro);color:var(--crema)}
.chips label:has(input:focus-visible){outline:2px solid #E8561A;outline-offset:2px}
.rows{display:grid;gap:8px}
.row{display:grid;grid-template-columns:118px minmax(0,1fr) 40px;gap:8px;align-items:center}
.row.step{grid-template-columns:28px minmax(0,1fr) 40px;align-items:start}
.row .n{font:700 15px "Courier Prime",monospace;padding-top:.8em;text-align:center}
.row.tn input[type=text]{border-color:#E8561A;color:#C2410C;font-weight:700}
.row select{padding-left:.6em;padding-right:.3em;font-size:15px}
.x{width:40px;height:40px;border:0!important;box-shadow:none!important;border-radius:50%;background:transparent!important;color:var(--negro-60);font-size:20px;cursor:pointer}
.x:hover{background:#F6E2C8;color:var(--negro)}
.add{justify-self:start;font:700 14px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro);background:none;border:0;padding:4px 0;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.btn-a{display:inline-flex;align-items:center;justify-content:center;min-height:50px;padding:.8em 1.6em .7em;border:0;border-radius:999px;font:700 14px "Hanken Grotesk",system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;text-decoration:none}
.btn-a.go{background:#EE5F1C;color:var(--crema)}.btn-a.go:hover{background:#F26F31}
.btn-a.soft{background:#F1D5B2;color:var(--negro)}.btn-a.soft:hover{background:#F6E2C8}
.btn-a[disabled]{opacity:.45;cursor:default}.btn-a.go[disabled]:hover{background:#EE5F1C}
.btn-a:focus{outline:none}.btn-a:focus-visible{outline:2px solid #E8561A;outline-offset:3px}
.acts{display:flex;gap:8px;flex-wrap:wrap}
.msg{margin:0;font-size:15px;line-height:1.5}.msg:empty{display:none}.msg.err{color:#B3361A;font-weight:600}
.wait{display:flex;align-items:center;gap:10px;color:var(--negro-60)}
.wait i{width:16px;height:16px;border-radius:50%;border:2px solid #F1D5B2;border-top-color:#E8561A;animation:arspin .8s linear infinite}
@keyframes arspin{to{transform:rotate(360deg)}}
.pv{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:clamp(18px,3vw,36px);align-items:start;border:1.5px solid var(--negro);border-radius:18px;background:#fff;padding:clamp(14px,2vw,22px)}
.pv img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:12px;display:block}
.pv .q{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--negro-60);margin:0 0 6px}
.pv h2{font-family:var(--display);font-size:clamp(30px,3.4vw,44px);line-height:.95;margin:0 0 6px;text-transform:uppercase}
.pv .meta{margin:0 0 14px;color:var(--negro-60)}
.pv ul{list-style:none;margin:0 0 14px;padding:0;font-family:"Courier Prime",monospace;font-size:16px}
.pv li{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px dotted rgba(45,41,38,.45);-webkit-text-stroke:.4px currentColor}
.pv li.tn{font-weight:700;color:#C2410C;-webkit-text-stroke:0}
.pv li .a{white-space:nowrap;font-weight:700}
.pv ol{margin:0 0 16px;padding-left:1.4em;line-height:1.5;list-style:decimal}.pv ol li{display:list-item;border:0;padding:4px 0;font-family:inherit;-webkit-text-stroke:0}
.done{padding:22px 20px;border-radius:18px;background:#F6E2C8;max-width:640px}
.done h2{font-family:var(--display);font-size:clamp(30px,4vw,42px);line-height:1;margin:0 0 .3em;text-transform:uppercase}
.done p{margin:0 0 16px;line-height:1.5}
@media (max-width:760px){.ar-grid,.pv{grid-template-columns:1fr}.ar-photo{position:static;max-width:300px;width:100%;margin:0 auto}.pv img{max-width:300px;margin:0 auto}.acts .btn-a{flex:1}}
@media (max-width:420px){.row{grid-template-columns:108px minmax(0,1fr) 34px;gap:6px}.x{width:36px;height:36px}}
</style>'''

chip = lambda name, typ, v: f'<label><input type="{typ}" name="{name}" value="{v}"><span>{v}</span></label>'
amt_opts = ''.join(f'<option value="{a}">{a + " oz" if a else "Sin medida"}</option>' for a in AMTS)

main = f'''<main id="top" class="ar"><div class="ar-in">
{team_gate.html('Añadir una receta')}
<div id="team-app" hidden>
  <h1>Añadir una receta</h1>
  <p class="ar-lead">Llena la receta y sube la foto. Antes de publicar, ves cómo va a quedar.</p>

  <form id="ar-form" novalidate>
  <div class="ar-grid" id="ar-edit">
    <div class="ar-photo">
      <label class="ar-drop" id="ar-drop">
        <input type="file" id="ar-file" accept="image/*">
        <span class="ph" id="ar-ph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg>
          <b>Sube la foto</b><span>Vertical, con el trago en el centro. Se recorta a 4:5.</span></span>
        <img id="ar-img" alt="" hidden>
      </label>
      <button type="button" class="ar-change" id="ar-change" hidden>Cambiar foto</button>
    </div>

    <div class="ar-f">
      <div class="ar-two">
        <div><label class="l" for="ar-name">Nombre</label><input type="text" id="ar-name" maxlength="60" placeholder="Paloma de toronja" autocomplete="off"></div>
        <div><label class="l" for="ar-serves">Porciones</label><select id="ar-serves">{''.join(f'<option>{n}</option>' for n in (1, 2, 4, 6, 8, 10))}</select></div>
      </div>
      <div><label class="l" for="ar-sub">Descripción corta <small>(2 o 3 palabras)</small></label><input type="text" id="ar-sub" maxlength="40" placeholder="Para el calor" autocomplete="off"></div>
      <div><span class="l">Vaso</span><div class="chips">{''.join(chip('vaso', 'radio', v) for v in VASOS)}</div></div>
      <div><span class="l">Sabor <small>(escoge 2)</small></span><div class="chips" id="ar-tags">{''.join(chip('tag', 'checkbox', t) for t in TAGS)}</div></div>
      <div><span class="l">Ingredientes</span><div class="rows" id="ar-ing"></div><button type="button" class="add" id="ar-add-ing">+ Añadir ingrediente</button></div>
      <div><span class="l">Pasos</span><div class="rows" id="ar-steps"></div><button type="button" class="add" id="ar-add-step">+ Añadir paso</button></div>
      <p class="msg" id="ar-msg" role="status" aria-live="polite"></p>
      <div class="acts"><button type="submit" class="btn-a go" id="ar-review">Revisar receta</button></div>
    </div>
  </div>
  </form>

  <div id="ar-pv" hidden>
    <div class="pv">
      <img id="pv-img" alt="">
      <div>
        <p class="q">Así va a quedar</p>
        <h2 id="pv-name"></h2>
        <p class="meta" id="pv-meta"></p>
        <ul id="pv-ing"></ul>
        <ol id="pv-steps"></ol>
        <div class="acts"><button type="button" class="btn-a go" id="ar-pub">Publicar</button><button type="button" class="btn-a soft" id="ar-back">Editar</button></div>
        <p class="msg" id="pv-msg" role="status" aria-live="polite" style="margin-top:12px"></p>
      </div>
    </div>
  </div>

  <div class="done" id="ar-done" hidden>
    <h2>¡Publicada!</h2>
    <p id="ar-done-txt"></p>
    <button type="button" class="btn-a go" id="ar-otra">Añadir otra</button>
  </div>
</div>
</div></main>'''

JS = '''<script>
(function(){
  const SCRIPT_URL = %s, LISTO_MIN = %d, AMTS = %s;
  const $ = id => document.getElementById(id);
  const esc = s => String(s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const norm = s => String(s || '').normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase();
  const isTN = s => /\\b(tres|3)\\s*naranjos?\\b/.test(norm(s));
  let photo = null, busy = false;

  /* ---- photo: shrink on the phone before sending ---- */
  function loadPhoto(file){
    if (!file || !/^image\\//.test(file.type)) return;
    const img = new Image(), url = URL.createObjectURL(file);
    img.onload = () => {
      const k = Math.min(1, 1600 / Math.max(img.naturalWidth, img.naturalHeight));
      const c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * k); c.height = Math.round(img.naturalHeight * k);
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
      photo = c.toDataURL('image/jpeg', .86);
      $('ar-img').src = photo; $('ar-img').hidden = false; $('ar-ph').hidden = true; $('ar-change').hidden = false;
      URL.revokeObjectURL(url); say('');
    };
    img.src = url;
  }
  $('ar-file').addEventListener('change', e => loadPhoto(e.target.files[0]));
  $('ar-change').addEventListener('click', () => $('ar-file').click());
  const drop = $('ar-drop');
  drop.addEventListener('dragover', e => { e.preventDefault(); });
  drop.addEventListener('drop', e => { e.preventDefault(); loadPhoto(e.dataTransfer.files[0]); });

  /* ---- rows ---- */
  function ingRow(amt, name){
    const r = document.createElement('div'); r.className = 'row';
    r.innerHTML = '<select aria-label="Cantidad">' + AMTS.map(a => '<option value="' + a + '">' + (a ? a + ' oz' : 'Sin medida') + '</option>').join('') + '</select>' +
      '<input type="text" aria-label="Ingrediente" placeholder="Ingrediente" maxlength="70"><button type="button" class="x" aria-label="Quitar">×</button>';
    r.querySelector('select').value = amt || ''; const inp = r.querySelector('input'); inp.value = name || '';
    const mark = () => r.classList.toggle('tn', isTN(inp.value)); inp.addEventListener('input', mark); mark();
    r.querySelector('.x').addEventListener('click', () => { r.remove(); });
    $('ar-ing').appendChild(r); return inp;
  }
  function stepRow(text){
    const r = document.createElement('div'); r.className = 'row step';
    r.innerHTML = '<span class="n"></span><textarea rows="1" aria-label="Paso" placeholder="Qué hacer" maxlength="240"></textarea><button type="button" class="x" aria-label="Quitar">×</button>';
    const t = r.querySelector('textarea'); t.value = text || '';
    const fit = () => { t.style.height = 'auto'; t.style.height = t.scrollHeight + 3 + 'px'; }; t.addEventListener('input', fit);
    r.querySelector('.x').addEventListener('click', () => { r.remove(); number(); });
    $('ar-steps').appendChild(r); number(); return t;
  }
  function number(){ [...$('ar-steps').children].forEach((r, i) => r.querySelector('.n').textContent = (i + 1) + '.'); }
  function fresh(){
    $('ar-ing').innerHTML = ''; $('ar-steps').innerHTML = '';
    ingRow('1 1/2', ''); ingRow('1/2', 'Tres Naranjos'); ingRow('1/2', ''); stepRow(''); stepRow('');
  }
  fresh();
  $('ar-add-ing').addEventListener('click', () => ingRow('', '').focus());
  $('ar-add-step').addEventListener('click', () => stepRow('').focus());
  $('ar-tags').addEventListener('change', e => { const on = $('ar-tags').querySelectorAll('input:checked'); if (on.length > 2) e.target.checked = false; });

  /* ---- collect + check ---- */
  const say = (h, err) => { const m = $('ar-msg'); m.className = 'msg' + (err ? ' err' : ''); m.innerHTML = h; };
  const say2 = (h, err) => { const m = $('pv-msg'); m.className = 'msg' + (err ? ' err' : ''); m.innerHTML = h; };
  function collect(){
    const ing = [...$('ar-ing').children].map(r => ({a: r.querySelector('select').value, n: r.querySelector('input').value.trim()})).filter(x => x.n);
    return {
      nombre: $('ar-name').value.trim(), descripcion: $('ar-sub').value.trim(),
      vaso: (document.querySelector('input[name=vaso]:checked') || {}).value || '',
      etiquetas: [...document.querySelectorAll('input[name=tag]:checked')].map(x => x.value),
      porciones: +$('ar-serves').value, ing,
      pasos: [...$('ar-steps').querySelectorAll('textarea')].map(t => t.value.trim()).filter(Boolean)
    };
  }
  function problem(d){
    if (!photo) return 'Sube la foto del trago.';
    if (!d.nombre) return 'Escribe el nombre de la receta.';
    if (!d.vaso) return 'Escoge el vaso.';
    if (d.etiquetas.length < 1) return 'Escoge el sabor (1 o 2).';
    if (d.ing.length < 2) return 'Añade por lo menos 2 ingredientes.';
    if (!d.ing.some(x => isTN(x.n))) return 'Esta receta no lleva Tres Naranjos. Añádelo a los ingredientes.';
    if (!d.pasos.length) return 'Añade los pasos.';
    return '';
  }

  $('ar-form').addEventListener('submit', e => {
    e.preventDefault();
    const d = collect(), p = problem(d);
    if (p) return say(p, true);
    say('');
    $('pv-img').src = photo; $('pv-name').textContent = d.nombre;
    $('pv-meta').textContent = [d.descripcion, d.vaso, d.porciones > 1 ? d.porciones + ' porciones' : ''].filter(Boolean).join(' · ');
    $('pv-ing').innerHTML = d.ing.map(x => '<li class="' + (isTN(x.n) ? 'tn' : '') + '"><span>' + esc(x.n) + '</span><span class="a">' + (x.a ? esc(x.a) + ' oz' : '') + '</span></li>').join('');
    $('pv-steps').innerHTML = d.pasos.map(s => '<li>' + esc(s) + '</li>').join('');
    say2(''); $('ar-pub').disabled = false;
    $('ar-form').hidden = true; $('ar-pv').hidden = false; scrollTo({top: 0});
  });
  $('ar-back').addEventListener('click', () => { $('ar-pv').hidden = true; $('ar-form').hidden = false; scrollTo({top: 0}); });

  $('ar-pub').addEventListener('click', () => {
    if (busy) return;
    const d = collect();
    busy = true; $('ar-pub').disabled = true; $('ar-back').disabled = true;
    say2('<span class="wait"><i></i>Publicando… puede tardar unos segundos.</span>');
    const body = {accion: 'receta', clave: window.tnClave(), nombre: d.nombre, descripcion: d.descripcion, vaso: d.vaso,
      etiquetas: d.etiquetas, porciones: d.porciones, pasos: d.pasos,
      ingredientes: d.ing.map(x => (x.a ? x.a + ' oz ' : '') + x.n), foto: photo.split(',')[1]};
    fetch(SCRIPT_URL, {method: 'POST', body: JSON.stringify(body)}).then(r => r.json()).then(r => {
      if (r.ok) {
        const t = new Date(Date.now() + LISTO_MIN * 60000).toLocaleTimeString('es-PR', {hour: 'numeric', minute: '2-digit'});
        $('ar-done-txt').innerHTML = '<b>' + esc(r.nombre) + '</b> sale en Recetas no más tarde de las <b>' + t + '</b>.';
        $('ar-pv').hidden = true; $('ar-done').hidden = false; scrollTo({top: 0}); return;
      }
      if (r.error === 'clave') return window.tnLock();
      const m = { sin_tn: 'La receta tiene que llevar Tres Naranjos.',
        ya_esta: 'Ya hay una receta con ese nombre.', faltan: 'Faltan datos. Vuelve a Editar y revisa.'}[r.error] || 'No se pudo publicar. Vuelve a intentar en un momento.';
      say2(m, true);
    }).catch(() => say2('No pudimos conectarnos. Revisa tu internet y vuelve a intentar.', true))
      .finally(() => { busy = false; $('ar-pub').disabled = false; $('ar-back').disabled = false; });
  });

  $('ar-otra').addEventListener('click', () => {
    photo = null; $('ar-img').hidden = true; $('ar-ph').hidden = false; $('ar-change').hidden = true; $('ar-file').value = '';
    $('ar-form').reset();
    fresh(); $('ar-done').hidden = true; $('ar-form').hidden = false; scrollTo({top: 0});
  });
})();
</script>''' % (repr(SCRIPT_URL), LISTO_MIN, json.dumps(AMTS))

a = s.index('<main id="top">'); b = s.index('</main>', a) + 7; s = s[:a] + main + s[b:]
s = s.replace('<head>', '<head>\n<base href="/">\n' + team_gate.HEAD, 1)
s = s.replace('</head>', CSS + team_gate.CSS + '<meta name="robots" content="noindex, nofollow">\n</head>', 1)
a = s.index('/* =====================================================================\n   RECETAS'); b = s.index('</script>', a)
s = s[:a] + "(function(){const n=document.getElementById('nav');if(!n)return;const f=()=>document.documentElement.style.setProperty('--navh',n.offsetHeight+'px');f();addEventListener('load',f);addEventListener('resize',f);if(document.fonts)document.fonts.ready.then(f)})();\n" + s[b:]
s = re.sub(r'<style>\.t-page\{[^<]*</style>\n', '', s)
s = s.replace('</body>', team_gate.js(SCRIPT_URL, 'team-app') + JS + '\n</body>', 1)
open(SITE + 'anadir-receta.html', 'w').write(hoist(s)); print('ok anadir-receta')
