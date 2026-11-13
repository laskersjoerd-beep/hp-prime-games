#HELLRAY - a Doom-style raycasting shooter for the HP Prime
#Python app (hpprime module). Runs on G1 and G2, firmware 2020+.
from hpprime import *
from math import *

#---------- timing ----------
try:
  ticks()
except:
  def ticks():
    return int(eval("TICKS()"))

#---------- random (own LCG, no module needed) ----------
_rs=[12345]
def rnd():
  _rs[0]=(_rs[0]*1103515245+12345)&0x7fffffff
  return _rs[0]/2147483648.0

#---------- screen ----------
SW=320
VH=200          #3D view height, HUD below
HH=VH//2
G=1             #back buffer

#fillrect with fallback (some firmwares differ)
FRM=[0]
def FR(x,y,w,h,c):
  if w<=0 or h<=0:
    return
  if FRM[0]==0:
    try:
      fillrect(G,int(x),int(y),int(w),int(h),c,c)
      return
    except:
      FRM[0]=1
  x=int(x);y=int(y);w=int(w);h=int(h)
  if w>h:
    for i in range(h):
      line(G,x,y+i,x+w-1,y+i,c)
  else:
    for i in range(w):
      line(G,x+i,y,x+i,y+h-1,c)

def shade(c,f):
  if f>1:f=1
  r=int(((c>>16)&255)*f)
  g=int(((c>>8)&255)*f)
  b=int((c&255)*f)
  return (r<<16)|(g<<8)|b

#---------- keys (bit numbers for keyboard()) ----------
K_UP=2;K_DN=12;K_LT=7;K_RT=8
K_ESC=4;K_ENTER=30;K_MENU=13
K_4=37;K_6=39;K_8=33;K_5=38
K_0=47;K_SPC=49;K_PLUS=50;K_MINUS=45
def kd(k,b):
  return (k>>b)&1

#---------- tiny block font for big titles ----------
FONT={
'A':"01110100011111110001100011",'C':"0111110000100001000001111",
'D':"1111010001100011000111110",'E':"1111110000111101000011111",
'H':"1000110001111111000110001",'I':"1111100100001000010011111",
'L':"1000010000100001000011111",'O':"0111010001100011000101110",
'R':"1111010001111101001010001",'U':"1000110001100011000101110",
'Y':"1000101010001000010000100",'V':"1000110001100010101000100",
'T':"1111100100001000010000100",'N':"1000111001101011001110001",
'G':"0111110000100111000101111",'M':"1000111011101011000110001",
'S':"0111110000011100000111110",'K':"1000110010111001001010001",
'!':"0010000100001000000000100",' ':"0000000000000000000000000",
'W':"1000110001101011101110001",'P':"1111010001111101000010000"}
def bigtext(s,y,sz,c):
  w=len(s)*6*sz
  x0=(SW-w)//2
  for n in range(len(s)):
    f=FONT.get(s[n],FONT[' '])
    for i in range(25):
      if f[i]=='1':
        FR(x0+n*6*sz+(i%5)*sz,y+(i//5)*sz,sz,sz,c)

def ctext(s,y,c):
  textout(G,(SW-len(s)*7)//2,y,s,c)

#---------- levels ----------
# # stone  B brick  T tech  W wood  D door  X exit switch
# P player  E imp  K brute  H health  A ammo
LEVELS=[
["################",
 "#P...#....E....#",
 "#....#.........#",
 "#..A.D....##...#",
 "#....#....##.H.#",
 "###D##.........#",
 "#....#BBBDBBB..#",
 "#.E..#B.....B..#",
 "#....#B..E..B.E#",
 "#.H..DB..A..B..#",
 "#....#BBBBBBB..#",
 "#..............#",
 "#.TTTT...WWW.WW#",
 "#.T.ET...W.....#",
 "#.T..D.E.W..K.X#",
 "################"],
["################",
 "#P..#.....T....#",
 "#...#..E..T..K.#",
 "#.A.D.....D....#",
 "#...#..H..T....#",
 "##D######TTTTDT#",
 "#......W.......#",
 "#..E...W..E..A.#",
 "#......D.......#",
 "#BBBDBBWBBBBBDB#",
 "#..........B...#",
 "#.K.....E..B.E.#",
 "#..........D...#",
 "#.H..BB.A..B...#",
 "#....BB....B..X#",
 "################"]]

WALLC={1:0x8C8C8C,2:0xA0442C,3:0x3E6FB0,4:0x8A5A2E,9:0x6E6E78,8:0x22AA44}
CEIL=0x2A2A30
FLOOR=0x4A3A2A

#---------- sprite art (original pixel art) ----------
#palette per sprite: '.'=transparent
IMP=["..r..r..",
     ".rrrrrr.",
     ".rYrrYr.",
     ".rrrrrr.",
     "..rkkr..",
     ".drrrrd.",
     "dRrrrrRd",
     "d.rrrr.d",
     "..r..r..",
     ".dd..dd."]
IMPP={'r':0xB0301E,'d':0x6E1A10,'R':0xD85030,'Y':0xFFE000,'k':0x200000}
BRUTE=["g......g",
       "gggggggg",
       "gwggggwg",
       "gggkkggg",
       ".gggggg.",
       "GGggggGG",
       "GggggggG",
       "G.gggg.G",
       ".gg..gg.",
       "ggg..ggg"]
BRUTEP={'g':0x3C8C3C,'G':0x225522,'w':0xFF3030,'k':0x101010}
CORPG={'r':0x3C8C3C,'d':0x225522,'R':0x55AA55}
CORPSE=["........",
        "........",
        "........",
        "........",
        "........",
        "........",
        "........",
        "..dr.d..",
        ".rrdrrd.",
        "dRrrrrrd"]
MEDKIT=["wwwwww",
        "wwrrww",
        "wrrrrw",
        "wwrrww",
        "wwwwww"]
MEDP={'w':0xEEEEEE,'r':0xDD1111}
AMMO=["..yy..",
      ".yyyy.",
      ".bbbb.",
      ".bbbb.",
      ".bbbb."]
AMMOP={'y':0xE8B422,'b':0x7A5A20}
FIREB=["..oo..",
       ".oyyo.",
       "oyyyyo",
       ".oyyo.",
       "..oo.."]
FIREP={'o':0xFF6000,'y':0xFFE060}
GUN=["...kGkkGk...",
     "...kGkkGk...",
     "...kGkkGk...",
     "...kGkkGk...",
     "..kggggggk..",
     "..khhhhhhk..",
     ".skhhhhhhks.",
     "sshhhhhhhhss",
     "sssshhhhssss",
     "ssss....ssss"]
GUNP={'k':0x202020,'g':0x606068,'G':0x9090A0,'h':0x704020,'s':0xE0A880}

#precompute column runs: list per column of (row,len,colorkey)
def runs(art):
  rows=len(art);cols=len(art[0])
  out=[]
  for x in range(cols):
    r=[];y=0
    while y<rows:
      ch=art[y][x]
      if ch=='.':
        y+=1;continue
      y0=y
      while y<rows and art[y][x]==ch:
        y+=1
      r.append((y0,y-y0,ch))
    out.append(r)
  return (cols,rows,out)
R_IMP=runs(IMP);R_BRUTE=runs(BRUTE);R_CORPSE=runs(CORPSE)
R_MED=runs(MEDKIT);R_AMMO=runs(AMMO);R_FIRE=runs(FIREB);R_GUN=runs(GUN)
HURTP={}
for _k in "rdRYkgGw":
  HURTP[_k]=0xFFFFFF

#---------- game state ----------
class Ent:
  def __init__(s,x,y,kind):
    s.x=x;s.y=y;s.k=kind   #0 imp 1 brute 2 med 3 ammo 4 fireball 5 corpse
    s.hp=3 if kind==0 else 7
    s.awake=0;s.cd=1.0;s.hurt=0.0;s.vx=0.0;s.vy=0.0;s.d=0.0;s.alive=1

ST={}
OPT=[64]   #number of ray columns (resolution)
RES=[40,64,80,107,160]

def load(n):
  global MAP,ENTS
  MAP=[];ENTS=[]
  L=LEVELS[n]
  for y in range(16):
    row=[]
    for x in range(16):
      ch=L[y][x]
      v={'#':1,'B':2,'T':3,'W':4,'D':9,'X':8}.get(ch,0)
      row.append(v)
      if ch=='P':
        ST['px']=x+0.5;ST['py']=y+0.5;ST['a']=0.0
      elif ch=='E':ENTS.append(Ent(x+0.5,y+0.5,0))
      elif ch=='K':ENTS.append(Ent(x+0.5,y+0.5,1))
      elif ch=='H':ENTS.append(Ent(x+0.5,y+0.5,2))
      elif ch=='A':ENTS.append(Ent(x+0.5,y+0.5,3))
    MAP.append(row)
  ST['lvl']=n
  ST['kills']=0
  ST['total']=sum(1 for e in ENTS if e.k<2)

def newgame():
  ST['hp']=100;ST['ammo']=24;ST['score']=0
  ST['flash']=0.0;ST['hit']=0.0;ST['fcd']=0.0;ST['bob']=0.0
  ST['map']=0;ST['msg']="";ST['msgt']=0.0
  load(0)

def solid(x,y):
  ix=int(x);iy=int(y)
  if ix<0 or iy<0 or ix>15 or iy>15:
    return 1
  return MAP[iy][ix]!=0

def tryMove(o,nx,ny,r):
  #move object o (has x,y) with radius r, sliding along walls
  if not (solid(nx-r,o.y-r) or solid(nx+r,o.y-r) or solid(nx-r,o.y+r) or solid(nx+r,o.y+r)):
    o.x=nx
  if not (solid(o.x-r,ny-r) or solid(o.x+r,ny-r) or solid(o.x-r,ny+r) or solid(o.x+r,ny+r)):
    o.y=ny

def los(x0,y0,x1,y1):
  dx=x1-x0;dy=y1-y0
  d=sqrt(dx*dx+dy*dy)
  n=int(d*3)+1
  for i in range(1,n):
    t=i/n
    if solid(x0+dx*t,y0+dy*t):
      return 0
  return 1

class P:
  pass
PL=P()

#---------- rendering ----------
ZB=[0.0]*160

def cast(N):
  px=PL.x;py=PL.y;a=ST['a']
  dX=cos(a);dY=sin(a)
  plX=-dY*0.66;plY=dX*0.66
  cw=SW/N
  #ceiling + floor bands (cheap depth shading)
  FR(0,0,SW,HH,CEIL)
  for i in range(5):
    FR(0,HH+i*20,SW,20,shade(FLOOR,0.45+i*0.14))
  for i in range(N):
    cx=2*i/N-1
    rx=dX+plX*cx;ry=dY+plY*cx
    mx=int(px);my=int(py)
    ddx=abs(1/rx) if rx!=0 else 1e9
    ddy=abs(1/ry) if ry!=0 else 1e9
    if rx<0:
      sx=-1;sdx=(px-mx)*ddx
    else:
      sx=1;sdx=(mx+1-px)*ddx
    if ry<0:
      sy=-1;sdy=(py-my)*ddy
    else:
      sy=1;sdy=(my+1-py)*ddy
    side=0;w=0;n=0
    while n<40:
      if sdx<sdy:
        sdx+=ddx;mx+=sx;side=0
      else:
        sdy+=ddy;my+=sy;side=1
      if mx<0 or my<0 or mx>15 or my>15:
        w=1;break
      w=MAP[my][mx]
      if w:
        break
      n+=1
    if side==0:
      pd=(mx-px+(1-sx)/2)/rx
      wx=py+pd*ry
    else:
      pd=(my-py+(1-sy)/2)/ry
      wx=px+pd*rx
    if pd<0.05:pd=0.05
    ZB[i]=pd
    wx-=int(wx)
    h=VH/pd
    top=HH-h/2
    f=1.15/(1+pd*0.22)
    if side:f*=0.75
    c=WALLC.get(w,0x8C8C8C)
    if w==8 and int(ticks()/300)%2:
      c=0x55FF77
    x0=int(i*cw);x1=int((i+1)*cw)
    t=int(top);hh=int(h)
    if t<0:
      hh+=t;t=0
    if t+hh>VH:hh=VH-t
    if wx<0.06 or wx>0.94:
      FR(x0,t,x1-x0,hh,shade(c,f*0.45))
    else:
      FR(x0,t,x1-x0,hh,shade(c,f))
      #per-type detail band
      if w==2:
        FR(x0,int(HH-h*0.17),x1-x0,max(1,int(h*0.04)),shade(c,f*0.5))
        FR(x0,int(HH+h*0.17),x1-x0,max(1,int(h*0.04)),shade(c,f*0.5))
      elif w==3:
        FR(x0,int(HH-h*0.05),x1-x0,max(1,int(h*0.1)),shade(0x60C0FF,f))
      elif w==9:
        FR(x0,int(HH-h*0.02),x1-x0,max(1,int(h*0.04)),shade(0xE8B422,f))
      elif w==8:
        FR(x0,int(HH-h*0.1),x1-x0,max(1,int(h*0.2)),0xFFFFFF if wx>0.4 and wx<0.6 else shade(c,f*0.6))

def drawSprite(R,pal,sx,depth,scale,lift,N):
  #R=(cols,rows,colruns); sx=screen x center; scale relative to wall height
  cols,rows,cr=R
  h=VH/depth*scale
  w=h*cols/rows
  bot=HH+VH/depth*0.5-lift*VH/depth
  top=bot-h
  cwid=w/cols;rh=h/rows
  x0=sx-w/2
  cw=SW/N
  fdim=1.1/(1+depth*0.18)
  for j in range(cols):
    xa=x0+j*cwid;xb=xa+cwid
    xc=(xa+xb)/2
    if xb<0 or xa>=SW:continue
    s=int(xc/cw)
    if s<0 or s>=N or ZB[s]<depth:continue
    for (r0,rl,ch) in cr[j]:
      FR(xa,top+r0*rh,xb-xa+1,rl*rh+1,shade(pal[ch],fdim))

def render():
  N=OPT[0]
  cast(N)
  a=ST['a'];dX=cos(a);dY=sin(a)
  plX=-dY*0.66;plY=dX*0.66
  inv=1/(plX*dY-dX*plY)
  vis=[]
  for e in ENTS:
    rx=e.x-PL.x;ry=e.y-PL.y
    tx=inv*(dY*rx-dX*ry)
    ty=inv*(-plY*rx+plX*ry)
    if ty>0.2:
      e.d=ty
      vis.append((ty,tx,e))
  vis.sort(key=lambda v:-v[0])
  for ty,tx,e in vis:
    sx=SW/2*(1+tx/ty)
    k=e.k
    if k==0:
      drawSprite(R_IMP,HURTP if e.hurt>0 else IMPP,sx,ty,0.8,0,N)
    elif k==1:
      drawSprite(R_BRUTE,HURTP if e.hurt>0 else BRUTEP,sx,ty,0.95,0,N)
    elif k==2:
      drawSprite(R_MED,MEDP,sx,ty,0.25,0,N)
    elif k==3:
      drawSprite(R_AMMO,AMMOP,sx,ty,0.3,0,N)
    elif k==4:
      drawSprite(R_FIRE,FIREP,sx,ty,0.25,0.4,N)
    elif k==5:
      drawSprite(R_CORPSE,IMPP if e.hp==0 else CORPG,sx,ty,0.8,0,N)
  #weapon
  b=ST['bob']
  gx=SW//2-42+int(sin(b)*8);gy=VH-66+int(abs(cos(b))*6)
  if ST['flash']>0:
    FR(gx+22,gy-22,40,22,0xFF9020)
    FR(gx+30,gy-30,24,18,0xFFE060)
    FR(gx+36,gy-26,12,10,0xFFFFFF)
    gy+=6
  cols,rows,cr=R_GUN
  for j in range(cols):
    for (r0,rl,ch) in cr[j]:
      FR(gx+j*7,gy+r0*7,7,rl*7,GUNP[ch])
  #crosshair
  FR(SW//2-1,HH-5,2,4,0xFFFFFF);FR(SW//2-1,HH+2,2,4,0xFFFFFF)
  #damage flash border
  if ST['hit']>0:
    FR(0,0,SW,6,0xFF0000);FR(0,VH-6,SW,6,0xFF0000)
    FR(0,0,6,VH,0xFF0000);FR(SW-6,0,6,VH,0xFF0000)
  if ST['map']:
    minimap()
  hud()

def minimap():
  s=5;ox=SW-16*s-4;oy=4
  for y in range(16):
    for x in range(16):
      v=MAP[y][x]
      if v:
        FR(ox+x*s,oy+y*s,s,s,WALLC.get(v,0x888888))
      else:
        FR(ox+x*s,oy+y*s,s,s,0x101010)
  for e in ENTS:
    if e.k<2:
      FR(ox+int(e.x*s)-1,oy+int(e.y*s)-1,3,3,0xFF4040)
  px=ox+int(PL.x*s);py=oy+int(PL.y*s)
  FR(px-1,py-1,3,3,0xFFFF00)
  line(G,px,py,px+int(cos(ST['a'])*8),py+int(sin(ST['a'])*8),0xFFFF00)

def hud():
  FR(0,VH,SW,240-VH,0x303030)
  FR(0,VH,SW,2,0x808080)
  hp=ST['hp']
  textout(G,6,VH+6,"HEALTH",0xC0C0C0)
  FR(6,VH+22,100,10,0x500000)
  FR(6,VH+22,max(0,hp),10,0x20D020 if hp>50 else (0xE0C020 if hp>25 else 0xE02020))
  textout(G,110,VH+20,str(hp),0xFFFFFF)
  textout(G,146,VH+6,"AMMO",0xC0C0C0)
  textout(G,146,VH+20,str(ST['ammo']),0xFFE060)
  textout(G,200,VH+6,"KILLS",0xC0C0C0)
  textout(G,200,VH+20,str(ST['kills'])+"/"+str(ST['total']),0xFF8080)
  textout(G,262,VH+6,"LEVEL",0xC0C0C0)
  textout(G,262,VH+20,str(ST['lvl']+1)+"/"+str(len(LEVELS)),0x80C0FF)
  if ST['msgt']>0:
    ctext(ST['msg'],HH+30,0xFFFFFF)

def say(m):
  ST['msg']=m;ST['msgt']=2.0

#---------- game logic ----------
def shoot():
  if ST['fcd']>0:return
  if ST['ammo']<=0:
    say("OUT OF AMMO");ST['fcd']=0.4;return
  ST['ammo']-=1;ST['fcd']=0.55;ST['flash']=0.12
  N=OPT[0]
  zc=ZB[N//2]
  a=ST['a'];dX=cos(a);dY=sin(a)
  plX=-dY*0.66;plY=dX*0.66
  inv=1/(plX*dY-dX*plY)
  best=None;bd=99
  for e in ENTS:
    if e.k>1:continue
    rx=e.x-PL.x;ry=e.y-PL.y
    tx=inv*(dY*rx-dX*ry)
    ty=inv*(-plY*rx+plX*ry)
    if ty<0.2 or ty>zc+0.3:continue
    sx=SW/2*(1+tx/ty)
    hw=VH/ty*0.4
    if abs(sx-SW/2)<hw and ty<bd:
      best=e;bd=ty
  if best:
    dmg=3 if bd<2.5 else (2 if bd<6 else 1)
    best.hp-=dmg;best.hurt=0.12;best.awake=1
    if best.hp<=0:
      best.hp=0 if best.k==0 else 1
      best.k=5;ST['kills']+=1;ST['score']+=100

def use():
  a=ST['a']
  for d in (0.6,1.0,1.4):
    tx=int(PL.x+cos(a)*d);ty=int(PL.y+sin(a)*d)
    if 0<=tx<16 and 0<=ty<16:
      v=MAP[ty][tx]
      if v==9:
        MAP[ty][tx]=0;say("DOOR OPENED");return 0
      if v==8:
        return 1
      if v:
        return 0
  return 0

def update(dt,k):
  ST['fcd']=max(0,ST['fcd']-dt);ST['flash']=max(0,ST['flash']-dt)
  ST['hit']=max(0,ST['hit']-dt);ST['msgt']=max(0,ST['msgt']-dt)
  ts=2.6*dt
  if kd(k,K_LT):ST['a']-=ts
  if kd(k,K_RT):ST['a']+=ts
  a=ST['a'];sp=3.0*dt
  mx=0.0;my=0.0
  if kd(k,K_UP) or kd(k,K_8):mx+=cos(a);my+=sin(a)
  if kd(k,K_DN) or kd(k,K_5):mx-=cos(a);my-=sin(a)
  if kd(k,K_4):mx+=sin(a);my-=cos(a)
  if kd(k,K_6):mx-=sin(a);my+=cos(a)
  if mx or my:
    tryMove(PL,PL.x+mx*sp,PL.y+my*sp,0.22)
    ST['bob']+=dt*9
  for e in ENTS:
    if e.hurt>0:e.hurt-=dt
    dx=PL.x-e.x;dy=PL.y-e.y
    d=sqrt(dx*dx+dy*dy)+1e-6
    if e.k==2 or e.k==3:
      if d<0.6:
        if e.k==2 and ST['hp']<100:
          ST['hp']=min(100,ST['hp']+25);e.alive=0;say("+25 HEALTH")
        elif e.k==3:
          ST['ammo']+=12;e.alive=0;say("+12 SHELLS")
    elif e.k==4:
      nx=e.x+e.vx*dt;ny=e.y+e.vy*dt
      if solid(nx,ny):
        e.alive=0
      else:
        e.x=nx;e.y=ny
      if d<0.4:
        e.alive=0;hurt(8+int(rnd()*8))
    elif e.k<2:
      e.cd-=dt
      if not e.awake:
        if d<9 and los(e.x,e.y,PL.x,PL.y):
          e.awake=1
        continue
      spd=(1.3 if e.k==0 else 0.9)*dt
      if d>0.8:
        tryMove(e,e.x+dx/d*spd,e.y+dy/d*spd,0.25)
      if e.cd<=0:
        if d<1.1:
          hurt((6 if e.k==0 else 14)+int(rnd()*6));e.cd=1.0
        elif e.k==0 and d<8 and rnd()<dt*1.2 and los(e.x,e.y,PL.x,PL.y):
          f=Ent(e.x,e.y,4);f.vx=dx/d*4.5;f.vy=dy/d*4.5
          ENTS.append(f);e.cd=1.6
  i=0
  while i<len(ENTS):
    if not ENTS[i].alive:
      ENTS.pop(i)
    else:
      i+=1

def hurt(n):
  ST['hp']-=n;ST['hit']=0.25
  if ST['hp']<0:ST['hp']=0

#---------- screens ----------
def flip():
  strblit(0,0,0,320,240,G)

def screen(title,col,lines):
  FR(0,0,320,240,0x000000)
  for i in range(12):
    FR(0,240-i*8,320,8,shade(0x801000,(12-i)/14))
  bigtext(title,40,6,col)
  y=110
  for s in lines:
    ctext(s,y,0xFFFFFF);y+=18
  flip()

def waitkey(bits):
  #wait for release then press of any key in bits
  while keyboard():
    pass
  while True:
    k=keyboard()
    for b in bits:
      if kd(k,b):
        return b

def title():
  screen("HELLRAY",0xFF3020,["A Doom-style shooter",
    "Arrows/8456: move  4/6: strafe",
    "ENTER or 0: fire   SPACE: open/use",
    "MENU: map   +/-: detail   ESC: quit",
    "","Press ENTER to start"])
  return waitkey([K_ENTER,K_ESC])

def main():
  dimgrob(G,320,240,0)
  if title()==K_ESC:
    return
  newgame()
  PL.x=ST['px'];PL.y=ST['py']
  last=ticks();prev=0
  while True:
    now=ticks()
    dt=(now-last)/1000.0
    last=now
    if dt>0.2:dt=0.2
    if dt<=0:dt=0.01
    k=keyboard()
    pressed=k&~prev
    prev=k
    if kd(k,K_ESC):
      break
    if kd(k,K_ENTER) or kd(k,K_0):
      shoot()
    if kd(pressed,K_SPC):
      if use():
        if ST['lvl']+1<len(LEVELS):
          screen("CLEAR",0x30FF60,["Level "+str(ST['lvl']+1)+" complete",
            "Kills "+str(ST['kills'])+"/"+str(ST['total']),"","Press ENTER"])
          waitkey([K_ENTER])
          load(ST['lvl']+1);PL.x=ST['px'];PL.y=ST['py']
          last=ticks();prev=keyboard()
          continue
        else:
          screen("VICTORY",0xFFE020,["You cleared every level!",
            "Score "+str(ST['score']+ST['hp']*10),"","ENTER: play again  ESC: quit"])
          if waitkey([K_ENTER,K_ESC])==K_ESC:return
          newgame();PL.x=ST['px'];PL.y=ST['py'];last=ticks();prev=keyboard()
          continue
    if kd(pressed,K_MENU):
      ST['map']=1-ST['map']
    if kd(pressed,K_PLUS) or kd(pressed,K_MINUS):
      i=RES.index(OPT[0])
      i=min(len(RES)-1,i+1) if kd(pressed,K_PLUS) else max(0,i-1)
      OPT[0]=RES[i];say("DETAIL "+str(OPT[0])+" COLUMNS")
    update(dt,k)
    if ST['hp']<=0:
      screen("YOU DIED",0xFF2020,["Kills "+str(ST['kills'])+"/"+str(ST['total']),
        "","ENTER: try again  ESC: quit"])
      if waitkey([K_ENTER,K_ESC])==K_ESC:return
      newgame();PL.x=ST['px'];PL.y=ST['py'];last=ticks();prev=keyboard()
      continue
    render()
    flip()

main()
