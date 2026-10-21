"""Builds site/sobre-nosotros.html (the "Sobre nosotros" page: photo + FAQ) from tools/faq.json (questions and answers, HTML links allowed in answers)."""
from hoist_meta import hoist
import json, html, re, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
TOOLS=ROOT+'tools/'; SITE=ROOT+'site/'
B=json.load(open(TOOLS+'config.json'))['site_url'].rstrip('/')
FAQ=json.load(open(TOOLS+'faq.json'))
# photo next to the page title; swap for any photo in site/assets (portrait works best)
PHOTO='assets/sobre-banner-3.webp'
PHOTO_ALT='Etiqueta de Tres Naranjos Triple Sec al sol con media china'
s=open(TOOLS+'tragos_base.html').read()
esc=lambda t:html.escape(t,quote=True)
s=re.sub(r'<title>.*?</title>','<title>Sobre nosotros | Tres Naranjos</title>',s,count=1)
s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Todo sobre Tres Naranjos Triple Sec: qué es, de dónde es, cuánto alcohol tiene, dónde comprarlo en Puerto Rico y qué cócteles hacer.">',s,count=1)
s=s.replace('<a href="recetas/" aria-current="page">','<a href="recetas/">',1)
s=s.replace('<li class="nav-faq"><a href="sobre-nosotros">','<li class="nav-faq"><a href="sobre-nosotros" aria-current="page">',1)
plain=lambda a:re.sub(r'<[^>]+>','',a)
LD={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f['q'],"acceptedAnswer":{"@type":"Answer","text":plain(f['a'])}} for f in FAQ]}
CSS='''<style>
main#top.fq{padding-top:clamp(36px,4.5vw,64px)!important;padding-bottom:clamp(64px,8vw,110px);max-width:880px;margin-inline:auto}
.fq-hero{margin:var(--fqnav,77px) 0 0;height:clamp(170px,17vw,300px);overflow:hidden;background:#F6E2C8;border-bottom:1.5px dashed var(--negro)}
.fq-hero img{width:100%;height:100%;object-fit:cover;object-position:50% 35%;display:block}
@media (max-width:700px){.fq-hero{height:190px}.fq-hero img{object-position:50% 40%}main#top.fq{padding-top:28px!important}}
.fq-head{margin-bottom:clamp(20px,2.5vw,28px)}
.fq-eye{font-family:var(--type);font-weight:700;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#E8561A}
.fq h1{font-family:var(--display);font-size:clamp(36px,4vw,56px);line-height:.95;margin:.2em 0 .3em;text-transform:uppercase}
.fq-head p{font-size:16px;margin:0;color:var(--negro-60)}
.fq details{border-bottom:1.5px dashed var(--negro)}
.fq details:first-of-type{border-top:1.5px dashed var(--negro)}
.fq summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;line-height:1.35;gap:16px;padding:18px 0;font-weight:700;font-size:clamp(16px,1.3vw,18px)}
.fq summary::-webkit-details-marker{display:none}
.fq summary::after{content:"+";font:400 26px/1 var(--mono);color:#E8561A;transition:transform .2s ease;flex:none}
.fq details[open] summary::after{transform:rotate(45deg)}
.fq summary:hover{color:#E04F12}
.fq summary:focus:not(:focus-visible){outline:none}
.fq .ans{padding:0 0 20px;font-size:16px;line-height:1.6;max-width:62ch}
.fq .ans a{color:var(--negro);font-weight:700;text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:4px}
.fq .ans a:hover{color:#E04F12}
.fq-more{margin-top:clamp(28px,3vw,40px);font-size:16px}
.fq-head p a,.fq-more a{color:var(--negro);font-weight:700;text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:4px}
.fq-head p a:hover,.fq-more a:hover{color:#E04F12}
.fq .fq-wa,.fq .ans a.fq-wa{color:#1E8E4F!important;white-space:nowrap}.fq .fq-wa svg{width:1.05em;height:1.05em;vertical-align:-.17em;margin-right:.3em}.fq .fq-wa:hover{color:#25A05B!important}
.fq .fq-mail{display:inline-flex;align-items:center;gap:.3em;font:inherit;font-weight:700;padding:0;text-decoration:none!important;cursor:pointer;color:var(--negro)}.fq .fq-mail .cp{width:14px;height:14px;opacity:.45}.fq .fq-mail:hover{color:#E04F12}.fq .fq-mail:hover .cp{opacity:1}
@media (min-width:1800px){.fq{zoom:1.2}}
</style>'''
items=''.join(f'<details name="faq"><summary>{esc(f["q"])}</summary><div class="ans">{f["a"]}</div></details>' for f in FAQ)
main=f'''<div class="fq-hero"><img src="{PHOTO}" alt="{PHOTO_ALT}" width="2600" height="494" fetchpriority="high"></div>
<main id="top" class="fq wrap">
  <header class="fq-head"><span class="fq-eye">Sobre nosotros</span><h1>Conoce todo sobre Tres Naranjos</h1><p>¿No ves tu pregunta? <a class="js-wa-contact fq-wa" href="https://wa.me/19393730729" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 1.8a8.2 8.2 0 1 1-4.2 15.3l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 0 1 12 3.8zm-3.3 4.4c-.2 0-.5 0-.7.3-.2.3-.9.9-.9 2.2s.9 2.5 1 2.7c.1.2 1.8 2.8 4.4 3.9 2.2.9 2.6.7 3.1.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.2-.2-.5-.3l-1.8-.9c-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1-.3-.1-1.1-.4-2.1-1.3-.8-.7-1.3-1.5-1.4-1.8-.2-.3 0-.4.1-.5l.4-.4.3-.4c.1-.2 0-.3 0-.5l-.8-2c-.2-.5-.4-.4-.6-.4h-.5z"/></svg>Escríbenos</a></p></header>
  {items}
  <p class="fq-more">¿Otra pregunta? Escríbenos por <a class="js-wa-contact fq-wa" href="https://wa.me/19393730729" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 1.8a8.2 8.2 0 1 1-4.2 15.3l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 0 1 12 3.8zm-3.3 4.4c-.2 0-.5 0-.7.3-.2.3-.9.9-.9 2.2s.9 2.5 1 2.7c.1.2 1.8 2.8 4.4 3.9 2.2.9 2.6.7 3.1.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.2-.2-.5-.3l-1.8-.9c-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1-.3-.1-1.1-.4-2.1-1.3-.8-.7-1.3-1.5-1.4-1.8-.2-.3 0-.4.1-.5l.4-.4.3-.4c.1-.2 0-.3 0-.5l-.8-2c-.2-.5-.4-.4-.6-.4h-.5z"/></svg>WhatsApp</a> o a <button type="button" class="copy-mail fq-mail" data-mail="info@agaveimportspr.com" aria-label="Copiar info@agaveimportspr.com"><span>info@agaveimportspr.com</span></button>.</p>
</main>
<script>/* space under the fixed header */(function(){{const n=document.getElementById('nav');const f=()=>{{if(n)document.documentElement.style.setProperty('--fqnav',n.getBoundingClientRect().bottom+'px')}};f();addEventListener('resize',f);addEventListener('load',f)}})();</script>
<script>/* one answer open at a time (older browsers that ignore name="faq") */document.querySelectorAll('.fq details').forEach(d=>d.addEventListener('toggle',()=>{{if(d.open)document.querySelectorAll('.fq details[open]').forEach(o=>{{if(o!==d)o.open=false}})}}))</script>
<script>addEventListener('DOMContentLoaded',()=>document.querySelectorAll('.js-wa-sell').forEach(a=>a.href='https://wa.me/'+(typeof WHATSAPP!=='undefined'?WHATSAPP:'19393730729')+'?text='+encodeURIComponent('¡Hola! Tengo un negocio y me interesa vender Tres Naranjos.')))</script>'''
a=s.index('<main id="top">'); b=s.index('</main>',a)+7; s=s[:a]+main+s[b:]
s=s.replace('</head>',CSS+f'<meta property="og:type" content="website"><meta property="og:site_name" content="Tres Naranjos"><meta property="og:title" content="Sobre nosotros | Tres Naranjos"><meta property="og:image" content="{B}/share/home.jpg?v=2"><link rel="canonical" href="{B}/sobre-nosotros"><script type="application/ld+json">{json.dumps(LD,ensure_ascii=False)}</script>\n</head>',1)
a=s.index('/* =====================================================================\n   RECETAS'); b=s.index('</script>',a)
s=s[:a]+"(function(){const n=document.getElementById('nav');if(n)document.documentElement.style.setProperty('--navh',n.offsetHeight+'px')})();\n"+s[b:]
s=re.sub(r'<style>\.t-page\{[^<]*</style>\n','',s)
open(SITE+'sobre-nosotros.html','w').write(hoist(s)); print('ok', len(FAQ), 'questions')
