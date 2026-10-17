from hoist_meta import hoist
import json,html,re
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
TOOLS=ROOT+'tools/'
SITE=ROOT+'site/'
A=SITE
os.makedirs(SITE+'tragos',exist_ok=True)
import json as _j
B=_j.load(open(TOOLS+'config.json'))['site_url'].rstrip('/')
D=json.load(open(TOOLS+'drinks.json'))
PHOTO={d['code']:d['photo'] for d in D}
TAGS={d['code']:d['tags'] for d in D}
base=open(TOOLS+'tragos_base.html').read()
WA_SVG='<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 1.8a8.2 8.2 0 1 1-4.2 15.3l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 0 1 12 3.8zm-3.3 4.4c-.2 0-.5 0-.7.3-.2.3-.9.9-.9 2.2s.9 2.5 1 2.7c.1.2 1.8 2.8 4.4 3.9 2.2.9 2.6.7 3.1.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.2-.2-.5-.3l-1.8-.9c-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1-.3-.1-1.1-.4-2.1-1.3-.8-.7-1.3-1.5-1.4-1.8-.2-.3 0-.4.1-.5l.4-.4.3-.4c.1-.2 0-.3 0-.5l-.8-2c-.2-.5-.4-.4-.6-.4h-.5z"/></svg>'
BAG='<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 6.5h14l-1.2 13H6.2z"/><path d="M9 8.5V5a3 3 0 0 1 6 0v3.5"/></svg>'
CSS='''<style>
/* ---------- recipe page ---------- */
.rp{padding-top:calc(var(--navh,84px) + clamp(20px,3vw,40px));padding-bottom:clamp(56px,7vw,96px)}
.rp-back{display:inline-flex;gap:.4em;align-items:center;font-weight:700;font-size:15px;text-decoration:none;margin-bottom:clamp(16px,2vw,24px)}
.rp-back:hover{text-decoration:underline}
.rp-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(28px,4vw,64px);align-items:start}
.rp-photo{margin:0;position:sticky;top:calc(var(--navh,84px) + 20px);border-radius:var(--radius);overflow:hidden;aspect-ratio:4/5;background:var(--crema-2)}
.rp-photo img{width:100%;height:100%;object-fit:cover;display:block}
.rp-tags{position:absolute;left:18px;bottom:18px;display:flex;gap:8px;flex-wrap:wrap}
.rp-tags span{font-weight:700;font-size:14px;letter-spacing:.04em;text-transform:uppercase;border-radius:999px;padding:.55em 1.1em .5em}
.rp-tags .t1{background:#E8561A;color:var(--crema)}.rp-tags .t2{background:var(--amarillo);color:#8A2F0C}
.rp-eye{font-family:var(--type);font-weight:700;font-size:14px;letter-spacing:.12em;text-transform:uppercase;color:#E8561A}
.rp-body h1{font-family:var(--display);font-size:clamp(52px,6vw,96px);line-height:.9;margin:.18em 0 .12em;text-transform:uppercase}
.rp-meta{font-size:16px;color:var(--negro-60);margin:0 0 clamp(22px,3vw,34px)}
.rp-ctrl{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;padding-bottom:14px;border-bottom:1.5px dashed var(--negro)}
.rp-step{display:flex;align-items:center;gap:12px;font-weight:700;font-size:14px;letter-spacing:.06em;text-transform:uppercase}
.rp-step button{width:34px;height:34px;border-radius:50%;border:0;background:var(--crema-2);font:700 18px var(--mono);color:var(--negro);cursor:pointer}
.rp-step button:hover{background:#F1D5B2}
.rp-step output{font-size:20px;min-width:1.4em;text-align:center}
.rp-units{display:flex;background:var(--crema-2);border-radius:999px;padding:3px}
.rp-units button{border:0;background:none;border-radius:999px;padding:.45em 1em;font:700 13px var(--mono);letter-spacing:.06em;cursor:pointer;color:var(--negro)}
.rp-units button[aria-pressed="true"]{background:var(--negro);color:var(--crema)}
.rp-ing{list-style:none;margin:0;padding:0;font-family:var(--type);font-size:clamp(16px,1.3vw,18px)}
.rp-ing li{display:flex;justify-content:space-between;gap:16px;padding:12px 0;border-bottom:1px dotted rgba(45,41,38,.45)}
.rp-ing li.tn{font-weight:700;color:#C2410C}
.rp-ing .a{white-space:nowrap;font-weight:700}
.rp-label{display:block;margin:clamp(24px,3vw,34px) 0 10px;font-weight:700;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--negro-60)}
.rp-steps{margin:0;padding-left:1.3em;display:grid;gap:10px;font-size:clamp(16px,1.25vw,18px);line-height:1.5}
.rp-tip{margin:clamp(20px,2.4vw,28px) 0 0;padding:14px 18px;border-radius:16px;background:var(--crema-2);font-size:16px}
.rp-tip b{font-family:var(--type)}
.rp-acts{display:flex;flex-wrap:wrap;gap:12px;margin-top:clamp(26px,3vw,36px)}
.rp-acts .btn{font-size:15px;padding:.9em 1.6em .8em;gap:.6em;box-shadow:none}
.rp-acts .btn .ico{width:19px;height:19px}
.rp-acts .rp-wa{background:#1E8E4F!important;color:#fff!important}.rp-acts .rp-wa:hover{background:#187A42!important}
.rp-acts .rp-buy{background:#EE5F1C!important;color:var(--crema)!important}.rp-acts .rp-buy:hover{background:#E04F12!important}
.rp-more{margin-top:clamp(56px,7vw,100px)}
.rp-more h2{font-family:var(--display);font-size:clamp(34px,3.4vw,52px);line-height:.95;margin:0 0 clamp(16px,2vw,24px);text-transform:uppercase}
.rp-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(14px,2vw,24px)}
.rp-card{text-decoration:none;display:grid;gap:10px}
.rp-card img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:var(--radius);display:block;transition:transform .3s ease}
.rp-card:hover img{transform:scale(1.02)}
.rp-card b{font-family:var(--display);font-weight:400;font-size:clamp(22px,2vw,30px);line-height:1;text-transform:uppercase}
@media (min-width:861px){.rp-tags{top:18px;bottom:auto}}
@media (max-width:860px){.rp-grid{grid-template-columns:1fr}.rp-photo{position:relative;top:0;aspect-ratio:4/4.2}}
@media (max-width:600px){.rp-cards{grid-template-columns:repeat(2,minmax(0,1fr))}.rp-cards a:nth-child(3){display:none}.rp-acts .btn{width:100%;justify-content:center}}
/* simple centered layout: photo on top, recipe below */
.rp-back{display:flex;justify-content:center}
.rp-grid{grid-template-columns:1fr!important;max-width:620px;margin-inline:auto;gap:clamp(24px,3vw,36px)!important}
.rp-photo{position:relative!important;top:0!important;aspect-ratio:1/1!important;height:min(36svh,340px);width:auto;max-width:100%;margin-inline:auto!important;justify-self:center}
.rp-tags span{font-size:12px;padding:.5em .9em .45em}
.rp-tags{bottom:12px!important}
.rp{padding-top:calc(var(--navh,84px) + 14px)!important}
.rp-back{margin-bottom:12px!important}
.rp-grid{gap:18px!important}
.rp-body h1{font-size:clamp(40px,4.4vw,64px)!important;margin:.12em 0 .08em!important}
.rp-meta{margin-bottom:18px!important}
.rp-tags{top:auto!important;bottom:18px!important;left:50%!important;transform:translateX(-50%);justify-content:center;flex-wrap:nowrap}
.rp-body{text-align:center}
.rp-body h1{font-size:clamp(46px,5vw,76px)}
.rp-ctrl{justify-content:center;gap:24px}
.rp-ing,.rp-steps,.rp-tip{text-align:left}
.rp-steps{max-width:560px;margin-inline:auto}
.rp-acts{justify-content:center}
.rp-more{max-width:860px;margin-inline:auto;text-align:center}
.rp-card{justify-items:center}
/* photo next to the title */
.rp-grid{max-width:680px!important}
.rp-top{display:grid;grid-template-columns:auto minmax(0,1fr);gap:clamp(18px,3vw,36px);align-items:center;text-align:left;margin-bottom:clamp(22px,3vw,32px)}
.rp-top .rp-photo{height:clamp(150px,22vw,260px)!important;width:auto;aspect-ratio:1/1!important;margin:0!important}
.rp-top h1{font-size:clamp(34px,4.6vw,68px)!important;margin:.12em 0 .14em!important}
.rp-top .rp-meta{margin:0 0 14px!important}
.rp-top .rp-tags{position:static!important;transform:none!important;justify-content:flex-start;flex-wrap:wrap}
.rp-top .rp-tags span{font-size:12px}
@media (max-width:600px){.rp-top{gap:14px}.rp-top .rp-photo{height:132px!important}.rp-top .rp-meta{font-size:13px;margin-bottom:8px!important}.rp-top .rp-tags span{font-size:10px;padding:.45em .8em .4em}.rp-top .rp-eye{font-size:11px}}
/* petite: everything a size down */
.rp-grid{max-width:520px!important}
.rp-top{gap:24px!important;margin-bottom:22px!important}
.rp-top .rp-photo{height:clamp(120px,14vw,180px)!important;border-radius:16px}
.rp-top h1{font-size:clamp(30px,3vw,44px)!important}
.rp-top .rp-eye{font-size:11px}
.rp-top .rp-meta{font-size:14px!important;margin-bottom:10px!important}
.rp-top .rp-tags span{font-size:10.5px!important;padding:.45em .85em .4em!important}
.rp-ctrl{padding-bottom:10px!important}
.rp-step{font-size:12px!important;gap:8px!important}.rp-step button{width:28px!important;height:28px!important;font-size:15px!important}.rp-step output{font-size:16px!important}
.rp-units button{font-size:11px!important;padding:.4em .85em!important}
.rp-ing{font-size:14px!important}.rp-ing li{padding:9px 0!important}
.rp-label{font-size:12px!important;margin:24px 0 8px!important}
.rp-steps{font-size:15px!important;gap:6px!important;line-height:1.45!important}
.rp-tip{font-size:14px!important;padding:11px 14px!important}
.rp-acts{margin-top:24px!important}.rp-acts .btn{font-size:13px!important;padding:.85em 1.4em .75em!important}.rp-acts .btn .ico{width:16px!important;height:16px!important}
.rp-back{font-size:14px!important;display:flex!important;justify-content:flex-start!important;max-width:520px;margin-inline:auto}
.rp-more{max-width:640px!important}.rp-more h2{font-size:clamp(26px,2.4vw,36px)!important}.rp-card b{font-size:clamp(18px,1.5vw,22px)!important}
@media (min-width:1000px){.rp{position:relative}.rp-back{position:absolute;top:calc(var(--navh,84px) + 44px);left:calc(50% - 260px - 36px);transform:translateX(-100%);margin:0!important;max-width:none!important;white-space:nowrap}}
@media (max-width:600px){.rp-top .rp-photo{height:112px!important}.rp-top h1{font-size:30px!important}}
/* round arrow back button, smaller photo, more air under the nav */
.rp{padding-top:calc(var(--navh,84px) + 44px)!important}
.rp-back{width:40px;height:40px;border-radius:50%;background:var(--crema-2);justify-content:center!important;align-items:center;padding:0;text-decoration:none}
.rp-back:hover{background:#F1D5B2;text-decoration:none}
.rp-back svg{width:20px;height:20px}
@media (max-width:999px){.rp-back{margin:0 0 16px!important;margin-inline:0!important}.rp-grid{margin-top:0}}
.rp-top .rp-photo{height:clamp(110px,11vw,150px)!important}
@media (max-width:600px){.rp{padding-top:calc(var(--navh,84px) + 20px)!important}.rp-top .rp-photo{height:104px!important}}
/* note (not a tip): a quiet quote */
.rp-note{margin:22px auto 0;max-width:440px;text-align:center;font-style:italic;font-size:15px;line-height:1.5;color:var(--negro-60)}
.rp-note::before{content:"“";color:#E8561A;font-style:normal;font-weight:700;margin-right:2px}.rp-note::after{content:"”";color:#E8561A;font-style:normal;font-weight:700;margin-left:2px}
/* prev / next */
.rp-pager{max-width:520px;margin:clamp(36px,4vw,52px) auto 0;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.rp-pg{display:flex;align-items:center;gap:10px;padding:10px;border-radius:18px;background:var(--crema-2);text-decoration:none;transition:background .2s ease}
.rp-pg.next{justify-content:flex-end;text-align:right}
.rp-pg img{width:44px;height:44px;border-radius:12px;object-fit:cover;flex:none;transition:transform .3s cubic-bezier(.34,1.56,.64,1)}
.rp-pg:hover{background:#F1D5B2}.rp-pg:hover img{transform:rotate(-4deg) scale(1.06)}.rp-pg.next:hover img{transform:rotate(4deg) scale(1.06)}
.rp-arr{width:30px;height:30px;border-radius:50%;background:var(--crema);display:grid;place-items:center;flex:none;transition:transform .25s ease}
.rp-arr svg{width:16px;height:16px}
.rp-pg.prev:hover .rp-arr{transform:translateX(-3px)}.rp-pg.next:hover .rp-arr{transform:translateX(3px)}
.rp-pgt{display:grid;min-width:0}.rp-pgt small{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--negro-60)}
.rp-pgt b{font-family:var(--display);font-weight:400;font-size:19px;line-height:1;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:600px){.rp-pg img{display:none}.rp-pgt b{font-size:16px}}
/* prev/next always in view */
.rp{position:relative}
.rp-side{position:fixed;top:50%;z-index:20;width:52px;height:52px;border-radius:50%;background:var(--crema-2);display:grid;place-items:center;text-decoration:none;color:var(--negro);transition:background .2s ease,transform .25s ease}
.rp-side svg{width:22px;height:22px}
.rp-side.prev{left:calc(50% - 260px - 120px)}.rp-side.next{right:calc(50% - 260px - 120px)}
.rp-side:hover{background:#E8561A;color:var(--crema)}
.rp-side.prev:hover{transform:translateX(-4px)}.rp-side.next:hover{transform:translateX(4px)}
.rp-side span{position:absolute;top:calc(100% + 8px);left:50%;transform:translateX(-50%) translateY(-4px);white-space:nowrap;font-family:var(--display);font-size:16px;text-transform:uppercase;opacity:0;pointer-events:none;transition:opacity .2s ease,transform .2s ease;color:var(--negro)}
.rp-side:hover span{opacity:1;transform:translateX(-50%) translateY(0)}
@media (max-width:999px){.rp-side{position:absolute;top:calc(var(--navh,84px) + 20px);width:40px;height:40px}.rp-side svg{width:18px;height:18px}.rp-side span{display:none}
  .rp-side.prev{left:auto;right:calc(var(--gutter,16px) + 42px);border-radius:999px 0 0 999px;width:42px}.rp-side.next{right:var(--gutter,16px);border-radius:0 999px 999px 0;width:42px;box-shadow:inset 1.5px 0 0 var(--crema)}}
@media (min-width:601px) and (max-width:999px){.rp-side{top:calc(var(--navh,84px) + 44px)}}
/* drink switcher at the top */
.rp-side{display:none!important}
.rp-pager{margin:0 auto 24px!important}
.rp-pg{padding:8px!important;border-radius:16px!important}
.rp-pg img{width:36px!important;height:36px!important;border-radius:10px!important}
.rp-pgt b{font-size:17px!important}
@media (min-width:1000px){.rp-back{top:calc(var(--navh,84px) + 44px + 8px)!important}}
@media (max-width:999px){.rp-back{position:absolute;top:calc(var(--navh,84px) + 44px);left:var(--gutter,16px);margin:0!important}.rp-pager{margin-left:56px!important}}
@media (max-width:600px){.rp-back{top:calc(var(--navh,84px) + 20px)}.rp-pager{gap:8px}.rp-arr{display:none!important}.rp-pg{padding:8px 12px!important}.rp-pgt b{font-size:15px!important}}
/* wide screens: previous drink in the left margin, next drink in the right margin */
@media (min-width:1100px){
  .rp-pager{position:absolute;left:0;right:0;top:calc(var(--navh,84px) + 44px + 56px);margin:0!important;max-width:none!important;display:block;pointer-events:none}
  .rp-pg{position:absolute;width:220px;pointer-events:auto}
  .rp-pg.prev{left:calc(50% - 260px - 36px);transform:translateX(-100%)}
  .rp-pg.next{left:calc(50% + 260px + 36px)}
  .rp-back{top:calc(var(--navh,84px) + 44px)!important;left:calc(50% - 260px - 36px)!important}
}
/* wide screens: tiles pinned to the screen edges, vertically centered */
@media (min-width:1100px){
  .rp-pager{position:absolute!important;left:0!important;right:0!important;top:0!important;bottom:auto!important;height:100svh;z-index:15}
  .rp-pg{top:50%;transition:opacity .3s ease,background .2s ease}
  .rp-pg.prev{left:var(--gutter,32px)!important;transform:translateY(-50%)!important}
  .rp-pg.next{left:auto!important;right:var(--gutter,32px);transform:translateY(-50%)!important}
  .rp-pager.away .rp-pg{opacity:0;pointer-events:none}
  .rp-back{top:calc(var(--navh,84px) + 44px)!important;left:calc(50% - 260px - 28px)!important;transform:translateX(-100%)!important}
}
/* quiet tiles until hovered */
@media (min-width:1100px){.rp-pg{opacity:.45}.rp-pg:hover,.rp-pg:focus-visible{opacity:1}.rp-pager.away .rp-pg{opacity:0}}
/* slim footer */
.rp-foot{border-top:1.5px dashed var(--negro);padding-top:22px!important;padding-bottom:28px!important;margin-top:0;text-align:center;display:grid;gap:10px;justify-items:center}
.rp-flinks{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;font-weight:700;font-size:14px}
.rp-flinks a{text-decoration:none}.rp-flinks a:hover{text-decoration:underline}.rp-flinks span{opacity:.4}
.rp-foot p{margin:0;max-width:760px;font-size:11.5px;line-height:1.5;color:var(--negro-60)}
/* everything left-aligned to the column edge */
.rp-ctrl{justify-content:space-between!important}
.rp-label{text-align:left}
.rp-note{text-align:left!important;margin:22px 0 0!important;max-width:none!important}
.rp-acts{justify-content:flex-start!important}
/* no back button: Ver tragos in the menu covers it */
.rp-back{display:none!important}
@media (max-width:1099px){.rp-pager{margin-left:auto!important}}
/* same layout on every drink: title on one line, top row locked to the photo height */
.rp-top{align-items:center!important}
.rp-top .rp-title{min-width:0}
.rp-top h1{white-space:nowrap}
.rp-top .rp-meta{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
/* title box has a fixed height so shrunk names don't move anything */
.rp-top h1{height:46px;line-height:46px!important;display:flex;align-items:center;margin:4px 0 6px!important}
@media (max-width:600px){.rp-top h1{height:32px;line-height:32px!important}}
.rp-flinks .copy-mail{font-size:14px;font-weight:700;padding:0}
.rp-flinks .copy-mail svg{width:15px;height:15px}
/* big monitors: scale the petite layout up so it doesn't look tiny */
@media (min-width:1800px){.rp-grid,.rp-foot{zoom:1.2}.rp-pg{zoom:1.2}}
@media (min-width:2300px){.rp-grid,.rp-foot{zoom:1.45}.rp-pg{zoom:1.3}}
/* phones: prev/next tiles show the drink photo, like desktop */
@media (max-width:999px){:root:root .rp-pg img{display:block!important;width:40px!important;height:40px!important;border-radius:10px!important;object-fit:cover;flex:none}
  :root:root .rp-pg{gap:10px!important;align-items:center}}
/* iPhone Safari: give the photo a real width so it never collapses */
.rp-top .rp-photo{flex:0 0 auto!important;min-width:104px}
.rp-top .rp-photo img{display:block;width:100%;height:100%;object-fit:cover}
/* more room between the nav and the drink */
.rp{padding-top:calc(var(--navh,84px) + clamp(36px,5vw,76px))!important}
/* prev/next tiles: show the full drink name (wraps to two lines), same height either way */
:root:root .rp-pgt b{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;font-size:15px!important;line-height:1!important;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
@media (min-width:1100px){:root:root .rp-pg{min-height:62px;box-sizing:border-box}}
/* ingredient list: typewriter face with a little more body so it reads on screen */
.rp-ing{font-size:15.5px!important;-webkit-text-stroke:.4px currentColor}
.rp-ing li.tn,.rp-ing .a{-webkit-text-stroke:0}
/* smooth drink-to-drink swap: only the recipe fades */
.rp-body{view-transition-name:rp-body}
::view-transition-group(rp-body){animation:none!important}
::view-transition-old(rp-body){animation:rp-out .1s ease-in both!important}
::view-transition-new(rp-body){animation:rp-in .24s cubic-bezier(.2,.7,.2,1) .1s both!important}
@keyframes rp-out{to{opacity:0}}
@keyframes rp-in{from{opacity:0;transform:translateY(6px)}}
@media (prefers-reduced-motion:reduce){::view-transition-old(rp-body),::view-transition-new(rp-body){animation:none!important}}
/* phones: no prev/next tiles up top; the WhatsApp button sticks to the bottom with small, quiet prev/next arrows beside it */
.rp-sw{display:none}
@media (max-width:600px){
  :root:root .rp-pager{display:none!important}
  :root:root .rp{padding-top:calc(var(--navh,84px) + 22px)!important}
  .rp-acts{position:sticky;bottom:0;z-index:6;flex-wrap:nowrap!important;align-items:center;gap:6px!important;
    margin:clamp(22px,6vw,30px) calc(-1*var(--gutter,16px)) 0!important;padding:14px var(--gutter,16px) calc(12px + env(safe-area-inset-bottom,0px));
    background:linear-gradient(to top,var(--crema,#FFF4E6) 72%,rgba(255,244,230,0))}
  .rp-acts .btn{flex:1;width:auto!important;min-width:0;min-height:48px}
  .rp-sw{display:grid;place-items:center;flex:none;width:36px;height:48px;padding:0;border:0;background:none;color:rgba(45,41,38,.38);cursor:pointer;-webkit-tap-highlight-color:transparent}
  .rp-sw svg{width:20px;height:20px}
  .rp-sw:active{color:rgba(45,41,38,.7)}
}
</style>'''
def esc(t): return html.escape(t,quote=True)
order=[d['code'] for d in D]
ALLJS=json.dumps([{'code':x['code'],'slug':x['slug'],'name':x['name'],'sub':x['sub'],'vaso':x['vaso'],'serves':x['serves'],'ing':x['ing'],'steps':x['steps'],'tags':x['tags'],'photo':x['photo']} for x in D],ensure_ascii=False,separators=(',',':'))
for i,d in enumerate(D):
  c=d['code'];name=d['name'];tg=TAGS[c]
  more=[D[(i+k)%len(D)] for k in (2,3,4)]
  prv=D[(i-1)%len(D)];nxt=D[(i+1)%len(D)]
  title=f'{name} con Tres Naranjos'
  desc=f"{tg[0]} y {tg[1].lower()}. La receta completa de {name}, con Tres Naranjos Triple Sec."
  s=base
  s=re.sub(r'<title>.*?</title>',f'<title>{esc(name)} | Receta con Tres Naranjos</title>',s,count=1)
  s=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{esc(desc)}">',s,count=1)
  head_extra=(f'<base href="../">\n<meta property="og:type" content="article"><meta property="og:site_name" content="Tres Naranjos">'
    f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
    f'<meta property="og:image" content="{B}/share/{d['slug']}.jpg?v=10"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg">'
    f'<meta property="og:url" content="{B}/tragos/{d['slug']}"><meta name="twitter:card" content="summary_large_image">\n')
  s=s.replace('<meta charset',head_extra+'<meta charset',1) if '<meta charset' in s[:400] else s.replace('<head>','<head>'+head_extra,1)
  s=s.replace('</head>',CSS+'\n</head>',1)
  def iso(t):
    import re as _r;m=_r.search(r'(\d+)',t);return 'PT'+(m.group(1) if m else '3')+'M'
  def amt(a,n,tn):
    n='Tres Naranjos Triple Sec' if tn else n
    if a is None: return n
    w=int(a);f=round((a-w)*4)/4;fr={0:'',.25:'1/4',.5:'1/2',.75:'3/4'}[f];q=(str(w) if w else '')+(' ' if w and fr else '')+fr
    return f'{q} oz {n[0].lower()+n[1:] if not n.startswith("Tres") else n}'
  LD={"@context":"https://schema.org","@type":"Recipe","name":name,"description":desc,"image":[B+'/share/'+d['slug']+'.jpg',B+'/assets/tragos/'+PHOTO[c]+'.webp'],
      "author":{"@type":"Organization","name":"Tres Naranjos"},"recipeCategory":"Cóctel","recipeCuisine":"Puertorriqueña","keywords":', '.join(tg+['triple sec','cóctel',name.lower()]),
      "prepTime":iso(d['time']),"totalTime":iso(d['time']),"recipeYield":str(d['serves'])+(' porción' if d['serves']==1 else ' porciones'),
      "recipeIngredient":[amt(i[0],i[1],len(i)>2 and i[2]) for i in d['ing']],
      "recipeInstructions":[{"@type":"HowToStep","text":x} for x in d['steps']]}
  s=s.replace('</head>','<link rel="canonical" href="'+B+'/tragos/'+d['slug']+'"><script type="application/ld+json">'+json.dumps(LD,ensure_ascii=False)+'</script>\n</head>',1)
  s=s.replace('<a href="tragos/" aria-current="page">','<a href="tragos/">',1)
  main=f'''<main id="top" class="rp wrap">
  <a class="rp-back" href="tragos/" aria-label="Todos los tragos" title="Todos los tragos"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg></a>
  <nav class="rp-pager" aria-label="Otros tragos"><a class="rp-pg prev" href="tragos/{prv['slug']}" rel="prev"><span class="rp-arr"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg></span><img src="assets/tragos/sm/{PHOTO[prv['code']]}.webp" alt=""><span class="rp-pgt"><small>Anterior</small><b>{esc(prv['name'])}</b></span></a><a class="rp-pg next" href="tragos/{nxt['slug']}" rel="next"><span class="rp-pgt"><small>Siguiente</small><b>{esc(nxt['name'])}</b></span><img src="assets/tragos/sm/{PHOTO[nxt['code']]}.webp" alt=""><span class="rp-arr"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span></a></nav>
  <div class="rp-grid">
    <div class="rp-body">
      <div class="rp-top"><figure class="rp-photo"><img src="assets/tragos/sm/{PHOTO[c]}.webp" alt="{esc(name)} con Tres Naranjos Triple Sec"></figure>
      <div class="rp-title"><span class="rp-eye">Receta con Tres Naranjos</span>
      <h1>{esc(name)}</h1>
      <p class="rp-meta">{esc(d['sub'])} · {esc(d['vaso'])}</p>
      <div class="rp-tags"><span class="t1">{esc(tg[0])}</span><span class="t2">{esc(tg[1])}</span></div></div></div>
      <div class="rp-ctrl"><div class="rp-step">Para <button type="button" id="less" aria-label="Menos personas">−</button><output id="ppl">{d['serves']}</output><button type="button" id="more" aria-label="Más personas">+</button></div>
        <div class="rp-units" role="group" aria-label="Unidades"><button type="button" data-u="oz" aria-pressed="true">OZ</button><button type="button" data-u="ml" aria-pressed="false">ML</button></div></div>
      <ul class="rp-ing" id="ing"></ul>
      <span class="rp-label">Cómo se hace</span>
      <ol class="rp-steps">{''.join('<li>'+esc(x)+'</li>' for x in d['steps'])}</ol>
      <div class="rp-acts"><button type="button" class="rp-sw prev" aria-label="Trago anterior"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 6-6 6 6 6"/></svg></button><a class="btn rp-wa" id="share" href="#" target="_blank" rel="noopener">{WA_SVG}Mándasela a un pana</a><button type="button" class="rp-sw next" aria-label="Trago siguiente"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg></button></div>
    </div>
  </div>

</main>'''
  a=s.index('<main id="top">');b=s.index('</main>',a)+7;s=s[:a]+main+s[b:]
  fa=s.index('<footer');fb=s.index('</footer>',fa)+9
  s=s[:fa]+'''<footer class="rp-foot wrap">
  <nav class="rp-flinks"><a href="tragos/">Tragos</a><span>·</span><a href="donde-comprar">Dónde comprar</a><span>·</span><a href="preguntas">Preguntas</a><span>·</span><a href="https://instagram.com/tresnaranjosoficial" target="_blank" rel="noopener">Instagram ↗</a><span>·</span><button type="button" class="copy-mail" data-mail="info@agaveimportspr.com" aria-label="Copiar info@agaveimportspr.com"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/></svg><span>info@agaveimportspr.com</span></button></nav>
  <p><strong>Disfruta con responsabilidad.</strong> © Tres Naranjos 2026. Importado por Agave Imports LLC, San Juan, PR. Producido y embotellado por Bodegas Collado, S.A. de C.V., Ciudad de México.</p>
  <p><strong>GOVERNMENT WARNING:</strong> (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.</p>
</footer>'''+s[fb:]
  # keep shared scripts (WhatsApp, giants, age gate), drop the tragos picker
  a=s.index('/* =====================================================================\n   RECETAS');b=s.index('</script>',a)
  js='''/* ---- recipe page ---- */
let R='''+json.dumps({'code':c,'slug':d['slug'],'name':name,'serves':d['serves'],'ing':d['ing'],'tags':tg})+''';
const ALL='''+ALLJS+''';
(function(){
  const $=id=>document.getElementById(id);let ppl=R.serves,unit='oz';
  const step=R.serves>1?R.serves/2:1;
  function fmt(oz){if(unit==='ml'){const ml=oz*29.57;return (ml>=100?Math.round(ml/10)*10:Math.round(ml/5)*5)+' ml'}
    let w=Math.floor(oz),f=Math.round((oz-w)*4)/4;if(f===1){w++;f=0}const fr={0:'',.25:'1/4',.5:'1/2',.75:'3/4'}[f];return ((w?w:'')+(w&&fr?' ':'')+fr||'0')+' oz'}
  function render(){const k=ppl/R.serves;$('ppl').textContent=ppl;
    $('ing').innerHTML=R.ing.map(x=>'<li'+(x[2]?' class="tn"':'')+'><span>'+(x[2]?'Tres Naranjos Triple Sec':x[1])+'</span>'+(x[0]!=null?'<span class="a">'+fmt(x[0]*k)+'</span>':'')+'</li>').join('')}
  $('less').onclick=()=>{ppl=Math.max(step,ppl-step);render()};$('more').onclick=()=>{ppl=Math.min(40,ppl+step);render()};
  document.querySelectorAll('.rp-units button').forEach(b=>b.onclick=()=>{unit=b.dataset.u;document.querySelectorAll('.rp-units button').forEach(x=>x.setAttribute('aria-pressed',x===b));render()});
  const pgr=document.querySelector('.rp-pager'),ft=document.querySelector('footer');
  const h1=document.querySelector('.rp-top h1');
  function fitTitle(){if(!h1)return;h1.style.removeProperty('font-size');const max=parseFloat(getComputedStyle(h1).fontSize),w=h1.parentElement.clientWidth;let fs=max;h1.style.setProperty('font-size',fs+'px','important');while(h1.scrollWidth>w&&fs>18){fs-=1;h1.style.setProperty('font-size',fs+'px','important')}}
  fitTitle();(document.fonts&&document.fonts.ready||Promise.resolve()).then(fitTitle);addEventListener('resize',fitTitle);
  render();
  addEventListener('keydown',e=>{if(e.target.closest('input,textarea'))return;if(e.key==='ArrowLeft')go(cur-1,true);else if(e.key==='ArrowRight')go(cur+1,true)});
  const site=new URL('.',document.baseURI).href.replace(/\\/$/,'');
  function share(){const txt='Pana, tienes que hacer este trago: *'+R.name+'*\\n'+site+'/tragos/'+R.slug;
    $('share').href='https://wa.me/?text='+encodeURIComponent(txt)}
  share();
  /* ---- smooth drink-to-drink: swap the recipe in place, no page reload ---- */
  const N=ALL.length,mod=i=>(i%N+N)%N,sm=d=>'assets/tragos/sm/'+d.photo+'.webp';
  let cur=Math.max(0,ALL.findIndex(d=>d.slug===R.slug));
  const pre=i=>{const im=new Image();im.decoding='async';im.src=sm(ALL[mod(i)])};
  function warm(){pre(cur-1);pre(cur+1)}
  (window.requestIdleCallback||setTimeout)(warm);
  const q=s=>document.querySelector(s),txt=(el,t)=>{if(el)el.textContent=t};
  function body(d){
    R={code:d.code,slug:d.slug,name:d.name,serves:d.serves,ing:d.ing,tags:d.tags};ppl=d.serves;
    txt(h1,d.name);txt(q('.rp-meta'),d.sub+' · '+d.vaso);txt(q('.rp-tags .t1'),d.tags[0]);txt(q('.rp-tags .t2'),d.tags[1]);
    const ol=q('.rp-steps');ol.innerHTML='';d.steps.forEach(t=>{const li=document.createElement('li');li.textContent=t;ol.appendChild(li)});
    render();fitTitle();
  }
  /* same height for every drink, so the footer never jumps: measure all 12 in one frame (nothing paints in between) */
  const rb=q('.rp-body');
  function equalize(){if(!rb)return;const keepU=unit,keepP=ppl;rb.style.minHeight='';let mx=0;
    ALL.forEach(d=>{body(d);mx=Math.max(mx,rb.offsetHeight)});
    body(ALL[cur]);ppl=keepP;unit=keepU;render();rb.style.minHeight=mx+'px'}
  let eqT;addEventListener('resize',()=>{clearTimeout(eqT);eqT=setTimeout(equalize,150)});
  (document.fonts&&document.fonts.ready||Promise.resolve()).then(equalize);
  function fill(i){
    const d=ALL[i],prv=ALL[mod(i-1)],nxt=ALL[mod(i+1)];cur=i;
    body(d);
    const im=q('.rp-photo img');im.src=sm(d);im.alt=d.name+' con Tres Naranjos Triple Sec';
    [['.rp-pg.prev',prv],['.rp-pg.next',nxt]].forEach(([s,x])=>{const a=q(s);a.href='tragos/'+x.slug;txt(a.querySelector('b'),x.name);const pi=a.querySelector('img');if(pi)pi.src=sm(x)});
    document.title=d.name+' | Receta con Tres Naranjos';const cn=q('link[rel=canonical]');if(cn)cn.href=cn.href.replace(/[^/]+$/,d.slug);
    share();warm();
  }
  function go(i,push){i=mod(i);if(i===cur)return;
    const run=()=>{fill(i);if(push)history.pushState({slug:ALL[i].slug},'','tragos/'+ALL[i].slug);if(scrollY>0)scrollTo(0,0)};
    const im=new Image();im.src=sm(ALL[i]);
    const swap=()=>{if(document.startViewTransition&&!matchMedia('(prefers-reduced-motion: reduce)').matches)document.startViewTransition(run);else run()};
    (im.decode?im.decode():Promise.resolve()).then(swap,swap);
  }
  /* swipe left/right on the recipe to change drink (phones) */
  {let x0=null,y0=null;const zone=q('.rp-body');
   zone.addEventListener('touchstart',e=>{if(e.touches.length!==1){x0=null;return}x0=e.touches[0].clientX;y0=e.touches[0].clientY},{passive:true});
   zone.addEventListener('touchend',e=>{if(x0===null)return;const t=e.changedTouches[0],dx=t.clientX-x0,dy=t.clientY-y0;x0=null;
     if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.6&&!e.target.closest('button,input,.rp-units'))go(cur+(dx<0?1:-1),true)},{passive:true});}
  document.querySelectorAll('.rp-pg').forEach(a=>a.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button)return;e.preventDefault();go(cur+(a.classList.contains('prev')?-1:1),true)}));
  document.querySelectorAll('.rp-sw').forEach(b=>b.addEventListener('click',()=>go(cur+(b.classList.contains('prev')?-1:1),true)));
  history.replaceState({slug:R.slug},'');
  addEventListener('popstate',()=>{const sl=location.pathname.replace(/\\/$/,'').split('/').pop().replace('.html','');const i=ALL.findIndex(d=>d.slug===sl);if(i>=0){const t=()=>fill(i);document.startViewTransition?document.startViewTransition(t):t()}});
  const nav=$('nav');if(nav)document.documentElement.style.setProperty('--navh',nav.offsetHeight+'px');
})();
'''
  s=s[:a]+js+s[b:]
  open(A+f"tragos/{d['slug']}.html",'w').write(hoist(s))
print('built',len(D))
