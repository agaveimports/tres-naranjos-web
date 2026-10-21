"""Shared password screen for the private team pages (anadir-tienda, anadir-receta).
The page content stays hidden until the code is checked against the sheet's Apps Script (?accion=clave).
The code is remembered on that phone or computer (localStorage 'tn-clave'); if it stops working, the page asks again."""

CSS = '''<style>
.gate{max-width:420px;margin:clamp(20px,6vh,70px) auto 0;text-align:center}
.gate h1{font-family:var(--display);font-size:clamp(34px,4.2vw,50px);line-height:.95;margin:0 0 .3em;text-transform:uppercase}
.gate p{margin:0 0 18px;color:var(--negro-60);line-height:1.5}
.gate form{display:flex;gap:8px}
.gate input{flex:1;min-width:0;box-sizing:border-box;font:500 16px "Hanken Grotesk",system-ui,sans-serif;color:var(--negro);background:#fff;border:1.5px solid var(--negro);border-radius:999px;padding:.85em 1.2em;outline:none}
.gate input:focus{border-color:#E8561A}
.gate button{min-height:50px;padding:.8em 1.5em .7em;border:0;border-radius:999px;font:700 14px "Hanken Grotesk",system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;background:var(--negro);color:var(--crema)}
.gate button:hover{background:#433D39}.gate button[disabled]{opacity:.5;cursor:default}
.gate button:focus{outline:none}.gate button:focus-visible{outline:2px solid #E8561A;outline-offset:3px}
.gate .gmsg{margin:12px 0 0;font-size:15px;min-height:1.4em}.gate .gmsg.err{color:#B3361A;font-weight:600}
@media (max-width:420px){.gate form{flex-direction:column}}
</style>'''

HTML = '''<div class="gate" id="gate-team" hidden>
  <h1>Para el equipo</h1>
  <p>Escribe la contraseña para entrar. Solo se pide una vez en este teléfono o computadora.</p>
  <form id="gate-form" autocomplete="off"><input type="password" id="gate-key" placeholder="Contraseña" aria-label="Contraseña"><button type="submit" id="gate-go">Entrar</button></form>
  <p class="gmsg" id="gate-msg" role="status" aria-live="polite"></p>
</div>'''


def js(script_url, app_id):
    return '''<script>
(function(){
  const URL_ = %r, app = document.getElementById(%r), gate = document.getElementById('gate-team');
  const get = () => { try { return localStorage.getItem('tn-clave') || ''; } catch (e) { return window.__tnKey || ''; } };
  const set = v => { window.__tnKey = v; try { v ? localStorage.setItem('tn-clave', v) : localStorage.removeItem('tn-clave'); } catch (e) {} };
  const open = () => { gate.hidden = true; app.hidden = false; };
  const lock = msg => { set(''); app.hidden = true; gate.hidden = false; document.getElementById('gate-msg').textContent = msg || ''; document.getElementById('gate-msg').className = 'gmsg' + (msg ? ' err' : ''); document.getElementById('gate-key').focus(); };
  window.tnClave = get;
  window.tnLock = () => lock('La contraseña cambió. Escribe la nueva.');
  if (get()) open(); else lock('');
  document.getElementById('gate-form').addEventListener('submit', e => {
    e.preventDefault();
    const k = document.getElementById('gate-key').value.trim(), btn = document.getElementById('gate-go'), m = document.getElementById('gate-msg');
    if (!k) return;
    btn.disabled = true; m.className = 'gmsg'; m.textContent = 'Revisando…';
    fetch(URL_ + '?' + new URLSearchParams({accion: 'clave', clave: k})).then(r => r.json()).then(r => {
      if (r.ok) { set(k); m.textContent = ''; open(); } else { m.className = 'gmsg err'; m.textContent = 'Contraseña incorrecta.'; }
    }).catch(() => { m.className = 'gmsg err'; m.textContent = 'No pudimos conectarnos. Vuelve a intentar.'; })
      .finally(() => { btn.disabled = false; });
  });
})();
</script>''' % (script_url, app_id)
