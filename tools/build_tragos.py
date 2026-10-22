from hoist_meta import hoist
import json,html,re
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
TOOLS=ROOT+'tools/'
SITE=ROOT+'site/'
A=SITE
exec(open(TOOLS+'build_recipes.py').read().split("base=open")[0])  # PHOTO, TAGS, D
s=open(TOOLS+'tragos_base.html').read()
CSS='''<style>
/* ---------- tragos: photo grid, every drink opens its own page ---------- */
.tg{padding-top:calc(var(--navh,84px) + clamp(48px,6vw,88px));padding-bottom:clamp(64px,8vw,110px)}
.tg-head{text-align:center;max-width:760px;margin:0 auto clamp(32px,4vw,56px)}
.tg-eye{font-family:var(--type);font-weight:700;font-size:14px;letter-spacing:.12em;text-transform:uppercase;color:#E8561A}
.tg-head h1{font-family:var(--display);font-size:clamp(48px,6vw,96px);line-height:.92;margin:.2em 0 .25em;text-transform:uppercase}
.tg-head p{font-size:clamp(17px,1.4vw,20px);margin:0}
.tg-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:clamp(18px,2.2vw,32px) clamp(14px,1.8vw,26px)}
.tg-card{text-decoration:none;display:grid;gap:12px}
.tg-ph{position:relative;border-radius:var(--radius);overflow:hidden;aspect-ratio:4/5;background:var(--crema-2)}
.tg-ph img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s cubic-bezier(.16,1,.3,1)}
.tg-card:hover .tg-ph img{transform:scale(1.04)}
.tg-tags{position:absolute;left:12px;bottom:12px;right:12px;display:flex;gap:6px;flex-wrap:wrap}
.tg-tags span{font-weight:700;font-size:12px;letter-spacing:.04em;text-transform:uppercase;border-radius:999px;padding:.5em .95em .45em}
.tg-tags .t1{background:#E8561A;color:var(--crema)}.tg-tags .t2{background:var(--amarillo);color:#8A2F0C}
.tg-name{font-family:var(--display);font-size:clamp(24px,2.1vw,32px);line-height:.95;text-transform:uppercase}
.tg-meta{font-size:15px;color:var(--negro-60);margin-top:-6px}
.tg-card:hover .tg-name{color:#E04F12}
@media (max-width:1100px){.tg-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:700px){.tg-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.tg-tags{left:8px;right:8px;bottom:8px;gap:4px;flex-wrap:nowrap}.tg-tags span{font-size:9.5px;padding:.5em .75em .42em}.tg-meta{font-size:13px}}
/* petite: see more drinks at once */
.tg{padding-top:calc(var(--navh,84px) + 40px)!important}
.tg-head{margin-bottom:28px!important;max-width:620px}
.tg-eye{font-size:11px}
.tg-head h1{font-size:clamp(32px,3.2vw,48px)!important;margin:.25em 0 .3em!important}
.tg-head p{font-size:15px!important}
.tg-grid{max-width:1180px;margin-inline:auto;grid-template-columns:repeat(6,minmax(0,1fr))!important;gap:22px 16px!important}
.tg-card{gap:8px!important;align-content:start}
.tg-ph{aspect-ratio:1/1!important;border-radius:16px!important}
.tg-tags{left:8px!important;right:8px!important;bottom:8px!important;gap:4px!important}
.tg-tags span{font-size:9.5px!important;padding:.45em .75em .4em!important}
.tg-name{font-size:clamp(17px,1.35vw,21px)!important}
.tg-meta{font-size:12.5px!important;margin-top:-4px!important}
@media (max-width:1100px){.tg-grid{grid-template-columns:repeat(4,minmax(0,1fr))!important}}
@media (max-width:700px){.tg{padding-top:calc(var(--navh,84px) + 24px)!important}.tg-grid{grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:16px 10px!important}.tg-tags{display:none!important}.tg-name{font-size:15px!important}.tg-meta{font-size:11px!important}.tg-ph{border-radius:12px!important}}
/* big monitors: scale the petite layout up so it doesn't look tiny */
@media (min-width:1800px){.tg{zoom:1.2}}
@media (min-width:2300px){.tg{zoom:1.45}}
/* loading placeholder: the photo's own color with a soft shimmer, then the photo fades in */
.tg-ph{background:var(--ph,#F6E2C8)!important}
.tg-ph::before{content:"";position:absolute;inset:0;z-index:0;background:linear-gradient(100deg,transparent 30%,rgba(255,244,230,.28) 50%,transparent 70%) 0 0/250% 100%;animation:tg-shim 1.3s ease-in-out infinite}
.tg-ph img{position:relative;z-index:1;opacity:0;transition:opacity .35s ease,transform .5s cubic-bezier(.16,1,.3,1)!important}
.tg-ph .tg-tags{z-index:2}
.tg-ph.ld img{opacity:1}
.tg-ph.ld::before{animation:none;opacity:0}
@keyframes tg-shim{from{background-position:120% 0}to{background-position:-20% 0}}
@media (prefers-reduced-motion:reduce){.tg-ph::before{animation:none}}
</style>'''
def esc(t): return html.escape(t,quote=True)
from PIL import Image as _Im
def avg_color(name):
    """the photo's average color, shown as the placeholder while the photo loads"""
    try:
        im=_Im.open(SITE+'assets/tragos/sm/'+name+'.webp').convert('RGB').resize((1,1),_Im.BILINEAR)
        return '#%02x%02x%02x'%im.getpixel((0,0))
    except Exception: return '#F6E2C8'
cards=''.join(f'''<a class="tg-card" href="recetas/{d['slug']}"><div class="tg-ph" style="--ph:{avg_color(PHOTO[d['code']])}"><img src="assets/tragos/sm/{PHOTO[d['code']]}.webp" onload="this.parentNode.classList.add('ld')" decoding="async" alt="{esc(d['name'])} con Tres Naranjos" loading="eager"{' fetchpriority="high"' if i<6 else ''}><div class="tg-tags"><span class="t1">{esc(TAGS[d['code']][0])}</span><span class="t2">{esc(TAGS[d['code']][1])}</span></div></div><span class="tg-name">{esc(d['name'])}</span></a>''' for i,d in enumerate(D))
main=f'''<main id="top" class="tg wrap">
  <header class="tg-head"><span class="tg-eye">Cócteles con Tres Naranjos</span><h1>Recetas con triple sec</h1><p>Margaritas, cosmos, sangría y más. Clásicos y criollos que quedan mejor con nuestro triple sec, y en cualquier receta que pida Cointreau o Grand Marnier, usa la misma medida.</p></header>
  <div class="tg-grid">{cards}</div>
</main>'''
a=s.index('<main id="top">');b=s.index('</main>',a)+7;s=s[:a]+main+s[b:]
s=s.replace('</head>',CSS+'\n</head>',1)
# SEO: what people search ("cócteles / bebidas / recetas con triple sec"; never "tragos") goes in the title and description
s=re.sub(r'<title>.*?</title>','<title>Recetas con triple sec: cócteles fáciles | Tres Naranjos</title>',s,count=1)
s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Cócteles y bebidas con triple sec: margarita, cosmo, sangría, mezcalita y más. Recetas fáciles con Tres Naranjos, el triple sec de Puerto Rico.">',s,count=1)
BASE=B
s=s.replace('</head>','<meta property="og:type" content="website"><meta property="og:site_name" content="Tres Naranjos"><meta property="og:title" content="Recetas con triple sec | Tres Naranjos"><meta property="og:description" content="Recetas fáciles de cócteles y bebidas con triple sec: margarita, cosmo, sangría y más."><meta property="og:image" content="'+BASE+'/share/margarita.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="'+BASE+'/recetas/">\n</head>',1)
a=s.index('/* =====================================================================\n   RECETAS');b=s.index('</script>',a)
js='''/* ---- old links like recetas/#A1 go to the drink's own page ---- */
const SL='''+json.dumps({d['code']:d['slug'] for d in D})+''';
(function(){const h=(location.hash||'').replace('#','').toUpperCase();if(/^[ABC][1-4]$/.test(h))location.replace('recetas/'+(SL[h]||''));
  const nav=document.getElementById('nav');if(nav)document.documentElement.style.setProperty('--navh',nav.offsetHeight+'px')})();
'''
s=s[:a]+js+s[b:]
s=re.sub(r'<style>\.t-page\{[^<]*</style>\n','',s)
os.makedirs(A+'recetas',exist_ok=True);s=s.replace('<meta charset','<base href="../">\n<meta charset',1);open(A+'recetas/index.html','w').write(hoist(s));print('ok')
