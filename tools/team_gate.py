"""Shared password screen for the private team pages: /equipo (the one link the team gets, asks for the password)
and its tools /equipo/receta and /equipo/tienda (no password screen of their own: without a saved password they send you to /equipo).
The page content stays hidden until the code is checked against the sheet's Apps Script (?accion=clave).
The code is remembered on that phone or computer (localStorage 'tn-clave'); if it stops working, the page asks again."""

# skip the age check on these private team pages (they are tools, not public pages)
HEAD = "<script>document.documentElement.classList.add('age-ok')</script>"

CSS = '''<style>
.pw{max-width:560px}
.pw h1{font-family:var(--display);font-size:clamp(34px,4.2vw,54px);line-height:.95;margin:0 0 .25em;text-transform:uppercase}
.pw .pw-lead{font-size:clamp(15px,1.2vw,17px);line-height:1.5;margin:0 0 18px;color:var(--negro-60)}
.pw form{display:flex;gap:8px}
.pw input{flex:1;min-width:0;box-sizing:border-box;font:500 16px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro);background:#fff;border:1.5px solid var(--negro);border-radius:999px;padding:.85em 1.2em;outline:none}
.pw input:focus{border-color:#E8561A}
.pw button{min-height:50px;padding:.8em 1.5em .7em;border:0;border-radius:999px;font:700 14px "Hanken Grotesk",system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;background:var(--negro);color:var(--crema)}
.pw button:hover{background:#433D39}.pw button[disabled]{opacity:.5;cursor:default}
.pw button:focus{outline:none}.pw button:focus-visible{outline:2px solid #E8561A;outline-offset:3px}
.pw .pw-msg{margin:10px 0 0;font-size:15px;line-height:1.5}.pw .pw-msg:empty{display:none}.pw .pw-msg.err{color:#B3361A;font-weight:600}
</style>'''


def html(title):
    return f'''<div class="pw" id="pw-team" hidden>
  <h1>{title}</h1>
  <p class="pw-lead">Escribe la contraseña para entrar. Solo se pide una vez en este teléfono o computadora.</p>
  <form id="pw-form" autocomplete="off"><input type="password" id="pw-key" placeholder="Contraseña" aria-label="Contraseña"><button type="submit" id="pw-go">Entrar</button></form>
  <p class="pw-msg" id="pw-msg" role="status" aria-live="polite"></p>
</div>'''


def js(script_url, app_id, hub=False):
    return ('''<script>
(function(){
  const URL_ = %r, app = document.getElementById(%r), pw = document.getElementById('pw-team');
  const get = () => { try { return localStorage.getItem('tn-clave') || ''; } catch (e) { return window.__tnKey || ''; } };
  const set = v => { window.__tnKey = v; try { v ? localStorage.setItem('tn-clave', v) : localStorage.removeItem('tn-clave'); } catch (e) {} };
  const open = () => { pw.hidden = true; app.hidden = false; };
  const HUB = %s;
  const toHub = m => location.replace('/equipo/?' + new URLSearchParams(Object.assign({ir: location.pathname}, m ? {m: 1} : {})));
  const lock = msg => { if (!HUB) { set(''); return toHub(msg); } set(''); app.hidden = true; pw.hidden = false; document.getElementById('pw-msg').textContent = msg || ''; document.getElementById('pw-msg').className = 'pw-msg' + (msg ? ' err' : ''); if (matchMedia('(hover:hover) and (pointer:fine)').matches) document.getElementById('pw-key').focus({preventScroll: true}); };
  window.tnClave = get;
  window.tnLock = () => lock('La contraseña cambió. Escribe la nueva.');
  window.tnIA = false;
  const check = k => fetch(URL_ + '?' + new URLSearchParams({accion: 'clave', clave: k})).then(r => r.json());
  if (get()) { open(); check(get()).then(r => { if (!r.ok) lock('La contraseña cambió. Escribe la nueva.'); else window.tnIA = !!r.ia; }).catch(() => {}); }
  else lock(HUB && new URLSearchParams(location.search).get('m') ? 'La contraseña cambió. Escribe la nueva.' : '');
  document.getElementById('pw-form').addEventListener('submit', e => {
    e.preventDefault();
    const k = document.getElementById('pw-key').value.trim(), btn = document.getElementById('pw-go'), m = document.getElementById('pw-msg');
    if (!k) return;
    btn.disabled = true; m.className = 'pw-msg'; m.textContent = 'Revisando…';
    check(k).then(r => {
      if (r.ok) { set(k); window.tnIA = !!r.ia; m.textContent = ''; const ir = new URLSearchParams(location.search).get('ir') || ''; if (ir.indexOf('/equipo/') === 0 && /^[a-z/-]+$/.test(ir) && ir.length > 8) return location.replace(ir); open(); } else { m.className = 'pw-msg err'; m.textContent = 'Contraseña incorrecta.'; }
    }).catch(() => { m.className = 'pw-msg err'; m.textContent = 'No pudimos conectarnos. Vuelve a intentar.'; })
      .finally(() => { btn.disabled = false; });
  });
})();
</script>''' % (script_url, app_id, 'true' if hub else 'false'))


def no_footer(page):
    """Team pages are tools, not public pages: no footer, wordmark or credit line (Alfonso, Oct 2026)."""
    import re
    page = re.sub(r'<footer[\s\S]*?</footer>\n?', '', page, count=1)
    page = re.sub(r'<div class="credit">.*?</div>\n?', '', page, count=1)
    return page


def admin_header(page):
    """Team pages get a slim header instead of the public menu: logo + EQUIPO tag, and one 'Ver el sitio' link."""
    import re
    hdr = ('<header class="nav solid adm" id="nav">\n'
           '  <a class="logo" href="equipo/" aria-label="Equipo Tres Naranjos">TR<span class="rev">E</span>S NARANJOS</a>\n'
           '  <span class="adm-tag">Equipo</span>\n'
           '  <a class="adm-site" href="./" target="_blank" rel="noopener">Ver el sitio <span aria-hidden="true">↗</span></a>\n'
           '</header>')
    page = re.sub(r'<header class="nav[^"]*" id="nav">[\s\S]*?</header>', hdr, page, count=1)
    css = ('<style>.nav.adm{display:flex;align-items:center;gap:14px}'
           '.adm-tag{font:700 12px var(--mono,monospace);letter-spacing:.14em;text-transform:uppercase;padding:6px 10px 5px;border-radius:999px;background:var(--negro);color:var(--crema)}'
           '.adm-site{margin-left:auto;font-weight:700;font-size:15px;color:var(--negro);text-decoration:none}.adm-site:hover{color:#E04F12}'
           '.nav.adm .menu-btn,.nav.adm .burger,.nav.adm button{display:none!important}'
           '.nav.adm{display:flex!important;grid-template-columns:none!important;justify-content:flex-start!important}'
           ':root:root:root .nav.adm .logo{position:static!important;left:auto!important;right:auto!important;transform:none!important;translate:none!important;margin:0!important}'
           '@media (max-width:700px){.nav.adm{gap:10px}:root:root:root .nav.adm .logo{font-size:20px!important}.adm-tag{font-size:10px;padding:5px 8px 4px}.adm-site{font-size:14px}}</style>\n')
    return page.replace('</head>', css + '</head>', 1)
