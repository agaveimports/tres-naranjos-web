# Builds the WhatsApp preview cards in site/r/img/ (1200x630) from the drink photos.
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
TOOLS=ROOT+'tools/'
SITE=ROOT+'site/'
from PIL import Image,ImageDraw,ImageFont,ImageOps
import os,sys
S=TOOLS+'fonts/'
A=SITE+'assets/'
CREMA=(255,244,230);NEGRO=(45,41,38);NAR=(232,86,26)
import json
D=[(d['code'],d['name'],'tragos/'+d['photo']+'.webp') for d in json.load(open(TOOLS+'drinks.json'))]
TAGS_ALL={d['code']:d['tags'] for d in json.load(open(TOOLS+'drinks.json'))}
f=lambda n,s:ImageFont.truetype(S+n,s)
def tw(d,t,fo,ls=0): return d.textlength(t,font=fo)+ls*max(0,len(t)-1)
def spaced(d,xy,t,fo,fill,ls):
  x,y=xy
  for ch in t: d.text((x,y),ch,font=fo,fill=fill);x+=d.textlength(ch,font=fo)+ls
def wordmark(img,x,y,size,fill):
  fo=f('elc.ttf',size);d=ImageDraw.Draw(img)
  d.text((x,y),'TR',font=fo,fill=fill);x+=d.textlength('TR',font=fo)
  w=int(d.textlength('E',font=fo))+4;h=int(size*1.4)
  e=Image.new('RGBA',(w,h),(0,0,0,0));ImageDraw.Draw(e).text((0,0),'E',font=fo,fill=fill)
  img.paste(ImageOps.mirror(e),(int(x),int(y)),ImageOps.mirror(e));x+=d.textlength('E',font=fo)
  d.text((x,y),'S NARANJOS',font=fo,fill=fill)
def wrap(d,t,fo,maxw):
  words=t.upper().split();lines=[];cur=''
  for w in words:
    tt=(cur+' '+w).strip()
    if d.textlength(tt,font=fo)<=maxw: cur=tt
    else: lines.append(cur);cur=w
  lines.append(cur);return lines
W,H=1200,630;M=28;PH=436;R=30
from PIL import ImageFilter
for code,name,src in D:
  img=Image.new('RGB',(W,H),CREMA);d=ImageDraw.Draw(img)
  import numpy as np
  if src=='prod-pour.jpg':
    BW,BH=W-2*M,PH;ph=ImageOps.fit(Image.open(A+'hero-bottle.webp').convert('RGB'),(BW,BH),centering=(.74,.62))
  else:
    srci=Image.open(A+src).convert('RGB');BW,BH=W-2*M,PH
    ZS={'A1':(1.7,0.25)};zs,tp=ZS.get(code,(1.22,0.08));sc=BH*zs/srci.height;fg=srci.resize((int(srci.width*sc),int(srci.height*sc)),Image.LANCZOS)
    top=int(fg.height*tp);cx=int(fg.width*.16);fg=fg.crop((cx,top,fg.width-cx,top+BH))
    a=np.asarray(fg).astype(np.float32);x0=(BW-fg.width)//2
    canvas=np.zeros((BH,BW,3),np.float32)
    L=a[:,:30].mean(1,keepdims=True);Rr=a[:,-30:].mean(1,keepdims=True)
    canvas[:,:x0]=L;canvas[:,x0+fg.width:]=Rr
    t=np.linspace(0,1,fg.width)[None,:,None];canvas[:,x0:x0+fg.width]=L*(1-t)+Rr*t
    ext=Image.fromarray(canvas.clip(0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(10));canvas=np.asarray(ext).astype(np.float32)
    blend=np.ones(fg.width,np.float32);n=110;blend[:n]=np.linspace(0,1,n);blend[-n:]=np.linspace(1,0,n)
    canvas[:,x0:x0+fg.width]=a*blend[None,:,None]+canvas[:,x0:x0+fg.width]*(1-blend[None,:,None])
    rng=np.random.default_rng(1);canvas+=rng.normal(0,2.5,canvas.shape[:2])[...,None]
    ph=Image.fromarray(canvas.clip(0,255).astype('uint8'))
  mask=Image.new('L',ph.size,0);ImageDraw.Draw(mask).rounded_rectangle([0,0,ph.size[0]-1,ph.size[1]-1],R,fill=255)
  img.paste(ph,(M,M),mask)
  TAGS=TAGS_ALL
  COLS=[((232,86,26),CREMA),((247,196,90),(138,47,12)),((251,211,174),(184,66,15))]
  tf=f('hk7.ttf',32);tx=M+24;ty=M+PH-24-64
  for i,t in enumerate(TAGS[code]):
    bgc,fgc=COLS[i%3];tt=t.upper();tw_=sum(d.textlength(ch,font=tf)+1.5 for ch in tt)-1.5;bw=int(tw_+60)
    d.rounded_rectangle([tx,ty,tx+bw,ty+64],32,fill=bgc)
    xx=tx+30
    for ch in tt: d.text((xx,ty+14),ch,font=tf,fill=fgc);xx+=d.textlength(ch,font=tf)+1.5
    tx+=bw+12
  # bottom row: label + drink name on the left, wordmark on the right
  L=M+8;y0=M+PH+18
  spaced(d,(L,y0),'RECETA CON TRES NARANJOS',f('cp7.ttf',20),NAR,3)
  size=76
  while d.textlength(name.upper(),font=f('elc.ttf',size))>W-2*M-430 and size>44: size-=4
  d.text((L,y0+40),name.upper(),font=f('elc.ttf',size),fill=NEGRO)
  wm=40;fo=f('elcaps.ttf',wm);wmw=d.textlength('TRES NARANJOS',font=fo)
  x=W-M-8-wmw;yy=H-M-wm-18
  d.text((x,yy),'TR',font=fo,fill=NAR);x+=d.textlength('TR',font=fo)
  ew=int(d.textlength('E',font=fo))+2;e=Image.new('RGBA',(ew,int(wm*1.5)),(0,0,0,0));ImageDraw.Draw(e).text((0,0),'E',font=fo,fill=NAR);e=ImageOps.mirror(e)
  img.paste(e,(int(x),int(yy)),e);x+=d.textlength('E',font=fo);d.text((x,yy),'S NARANJOS',font=fo,fill=NAR)
  spaced(d,(W-M-8-310,y0+4),'',f('cp7.ttf',16),NEGRO,2)
  img.save(A+f'../r/img/{code}.jpg',quality=93,optimize=True,progressive=True,subsampling=0)
print('done')
