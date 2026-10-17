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
/* tragos grid: white page, cream nav and footer */
html{background:var(--crema)}
body{background:#fff!important}
.nav{background:var(--crema)!important}
footer{background:var(--crema)}

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
</style>'''
def esc(t): return html.escape(t,quote=True)
cards=''.join(f'''<a class="tg-card" href="tragos/{d['slug']}"><div class="tg-ph"><img src="assets/tragos/sm/{PHOTO[d['code']]}.webp" decoding="async" alt="{esc(d['name'])} con Tres Naranjos" loading="eager"{' fetchpriority="high"' if i<6 else ''}><div class="tg-tags"><span class="t1">{esc(TAGS[d['code']][0])}</span><span class="t2">{esc(TAGS[d['code']][1])}</span></div></div><span class="tg-name">{esc(d['name'])}</span></a>''' for i,d in enumerate(D))
main=f'''<main id="top" class="tg wrap">
  <header class="tg-head"><span class="tg-eye">Recetas con Tres Naranjos</span><h1>Doce tragos, una naranja.</h1><p>Clásicos y criollos que quedan mejor con nuestro triple sec. Escoge uno y te enseñamos cómo.</p></header>
  <div class="tg-grid">{cards}</div>
</main>'''
a=s.index('<main id="top">');b=s.index('</main>',a)+7;s=s[:a]+main+s[b:]
s=s.replace('</head>',CSS+'\n</head>',1)
BASE=B
s=s.replace('</head>','<meta property="og:type" content="website"><meta property="og:site_name" content="Tres Naranjos"><meta property="og:title" content="Tragos con Tres Naranjos"><meta property="og:description" content="Doce recetas de cócteles con Tres Naranjos Triple Sec."><meta property="og:image" content="'+BASE+'/share/margarita.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="'+BASE+'/tragos/">\n</head>',1)
a=s.index('/* =====================================================================\n   RECETAS');b=s.index('</script>',a)
js='''/* ---- old links like tragos/#A1 go to the drink's own page ---- */
const SL='''+json.dumps({d['code']:d['slug'] for d in D})+''';
(function(){const h=(location.hash||'').replace('#','').toUpperCase();if(/^[ABC][1-4]$/.test(h))location.replace('tragos/'+(SL[h]||''));
  const nav=document.getElementById('nav');if(nav)document.documentElement.style.setProperty('--navh',nav.offsetHeight+'px')})();
'''
s=s[:a]+js+s[b:]
s=re.sub(r'<style>\.t-page\{[^<]*</style>\n','',s)
os.makedirs(A+'tragos',exist_ok=True);s=s.replace('<meta charset','<base href="../">\n<meta charset',1);open(A+'tragos/index.html','w').write(hoist(s));print('ok')
