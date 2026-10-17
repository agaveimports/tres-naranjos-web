"""Builds site/preguntas.html from tools/faq.json (questions and answers, HTML links allowed in answers)."""
import json, html, re, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
TOOLS=ROOT+'tools/'; SITE=ROOT+'site/'
B=json.load(open(TOOLS+'config.json'))['site_url'].rstrip('/')
FAQ=json.load(open(TOOLS+'faq.json'))
s=open(TOOLS+'tragos_base.html').read()
esc=lambda t:html.escape(t,quote=True)
s=re.sub(r'<title>.*?</title>','<title>Preguntas frecuentes | Tres Naranjos</title>',s,count=1)
s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Todo sobre Tres Naranjos Triple Sec: qué es, de dónde es, cuánto alcohol tiene, dónde comprarlo en Puerto Rico y qué tragos hacer.">',s,count=1)
s=s.replace('<a href="tragos/" aria-current="page">','<a href="tragos/">',1)
plain=lambda a:re.sub(r'<[^>]+>','',a)
LD={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f['q'],"acceptedAnswer":{"@type":"Answer","text":plain(f['a'])}} for f in FAQ]}
CSS='''<style>
main#top.fq{padding-top:calc(var(--navh,70px) + env(safe-area-inset-top,0px) + clamp(36px,6vw,80px));padding-bottom:clamp(64px,8vw,110px);max-width:720px;margin-inline:auto}
.fq-head{margin-bottom:clamp(24px,3vw,36px)}
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
.fq .ans{padding:0 0 20px;font-size:16px;line-height:1.6;max-width:62ch}
.fq .ans a{color:#E04F12;font-weight:700;text-decoration:underline;text-underline-offset:3px}
.fq-more{margin-top:clamp(28px,3vw,40px);font-size:16px}
@media (min-width:1800px){.fq{zoom:1.2}}
</style>'''
items=''.join(f'<details><summary>{esc(f["q"])}</summary><div class="ans">{f["a"]}</div></details>' for f in FAQ)
main=f'''<main id="top" class="fq wrap">
  <header class="fq-head"><span class="fq-eye">Preguntas frecuentes</span><h1>Todo sobre Tres Naranjos</h1><p>Lo que más nos preguntan. ¿No ves la tuya? Escríbenos.</p></header>
  {items}
  <p class="fq-more">¿Otra pregunta? Escríbenos por WhatsApp o a <button type="button" class="copy-mail" data-mail="info@agaveimportspr.com" aria-label="Copiar info@agaveimportspr.com"><span>info@agaveimportspr.com</span></button>.</p>
</main>'''
a=s.index('<main id="top">'); b=s.index('</main>',a)+7; s=s[:a]+main+s[b:]
s=s.replace('</head>',CSS+f'<meta property="og:type" content="website"><meta property="og:site_name" content="Tres Naranjos"><meta property="og:title" content="Preguntas frecuentes | Tres Naranjos"><meta property="og:image" content="{B}/share/home.jpg"><link rel="canonical" href="{B}/preguntas"><script type="application/ld+json">{json.dumps(LD,ensure_ascii=False)}</script>\n</head>',1)
a=s.index('/* =====================================================================\n   RECETAS'); b=s.index('</script>',a)
s=s[:a]+"(function(){const n=document.getElementById('nav');if(n)document.documentElement.style.setProperty('--navh',n.offsetHeight+'px')})();\n"+s[b:]
s=re.sub(r'<style>\.t-page\{[^<]*</style>\n','',s)
open(SITE+'preguntas.html','w').write(s); print('ok', len(FAQ), 'questions')
