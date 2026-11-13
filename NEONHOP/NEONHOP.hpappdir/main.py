#NEONHOP 2 - a one-button rhythm platformer for the HP Prime
#8 game modes, 7 levels and a level editor that saves.
#Tap ANYWHERE on the screen (or press Up/Space/Enter) to jump.
#Python app (hpprime module).
from hpprime import *
from math import *

try:
  ticks()
except:
  def ticks():
    return int(eval("TICKS()"))

G=1;SW=320;SH=240
T=20            #tile size (px)
ROWS=8
GY=200          #screen y of ground top
TOPY=GY-ROWS*T  #screen y of play area top (40)
CEIL=ROWS*T-T   #highest player height (touching the top)
PX=80           #player screen x
DT=1/60.0

#physics (px, px/s, px/s^2); hy = player height above the floor, + is up
GRAV=1750.0;JV=392.0;PADV=575.0;ORBV=430.0
SHIPUP=1450.0;SHIPDN=1100.0;SHIPMAX=330.0
BALLG=1400.0
UFOG=1200.0;UFOV=330.0
ROBV=300.0;ROBT=1400.0;ROBTIME=0.22
SWINGA=1300.0
MODES="CSBUWRPG"     #cube ship ball ufo wave robot spider swing
MNAME=["CUBE","SHIP","BALL","UFO","WAVE","ROBOT","SPIDER","SWING"]
MCOL=[0x40FF80,0xFF60E0,0xFF8020,0xFFE040,0x40E0FF,0xE0E0E0,0xA060FF,0xFFB0D0]
PORTALS="CSBUWRPGud<>"

#---------- drawing ----------
FRM=[0]
def FR(x,y,w,h,c):
  if w<=0 or h<=0:return
  if FRM[0]==0:
    try:
      fillrect(G,int(x),int(y),int(w),int(h),c,c);return
    except:
      FRM[0]=1
  x=int(x);y=int(y)
  for i in range(int(h)):line(G,x,y+i,x+int(w)-1,y+i,c)

def scanfill(pts,c):
  n=len(pts);ys=[p[1] for p in pts]
  y0=max(0,int(min(ys)));y1=min(SH-1,int(max(ys)))
  for y in range(y0,y1+1):
    xl=99999;xr=-99999
    for i in range(n):
      ax,ay=pts[i];bx,by=pts[(i+1)%n]
      if (ay<=y<by) or (by<=y<ay):
        x=ax+(y-ay)*(bx-ax)/(by-ay)
        if x<xl:xl=x
        if x>xr:xr=x
    if xl<=xr:line(G,int(max(-1,xl)),y,int(min(SW,xr)),y,c)
FPM=[0]
def poly(pts,c):
  if FPM[0]==1:
    fillpoly(G,pts,c);return
  if FPM[0]==0:
    try:
      fillpoly(G,pts,c);FPM[0]=1;return
    except:
      FPM[0]=2
  scanfill(pts,c)

def box(x,y,w,h,c):
  FR(x,y,w,1,c);FR(x,y+h-1,w,1,c);FR(x,y,1,h,c);FR(x+w-1,y,1,h,c)

def shade(c,f):
  if f>1:f=1
  return (int(((c>>16)&255)*f)<<16)|(int(((c>>8)&255)*f)<<8)|int((c&255)*f)
def mix(c,d,t):
  u=1-t
  return (int(((c>>16)&255)*u+((d>>16)&255)*t)<<16)|(int(((c>>8)&255)*u+((d>>8)&255)*t)<<8)|int((c&255)*u+(d&255)*t)

FONT={
'A':"0111010001111111000110001",'C':"0111110000100001000001111",
'D':"1111010001100011000111110",'E':"1111110000111101000011111",
'H':"1000110001111111000110001",'I':"1111100100001000010011111",
'L':"1000010000100001000011111",'M':"1000111011101011000110001",
'N':"1000111001101011001110001",'O':"0111010001100011000101110",
'P':"1111010001111101000010000",'R':"1111010001111101001010001",
'S':"0111110000011100000111110",'T':"1111100100001000010000100",
'U':"1000110001100011000101110",'G':"0111110000100111000101111",
'V':"1000110001100010101000100",'K':"1000110010111001001010001",
'B':"1111010001111101000111110",'F':"1111110000111101000010000",
'W':"1000110001101011101110001",'Y':"1000101010001000010000100",
'X':"1000101010001000101010001",'Z':"1111100010001000100011111",
'J':"0011100010000101001001100",'Q':"0111010001101011001001101",
'!':"0010000100001000000000100",' ':"0000000000000000000000000"}
def bigtext(s,y,sz,c,sh=0):
  x0=(SW-len(s)*6*sz)//2
  for n in range(len(s)):
    f=FONT.get(s[n],FONT[' '])
    for i in range(25):
      if f[i]=='1':
        if sh:FR(x0+n*6*sz+(i%5)*sz+2,y+(i//5)*sz+2,sz,sz,sh)
        FR(x0+n*6*sz+(i%5)*sz,y+(i//5)*sz,sz,sz,c)
def ctext(s,y,c):
  textout(G,(SW-len(s)*7)//2,y,s,c)

#---------- input: whole screen is a button ----------
K_UP=2;K_DN=12;K_LT=7;K_RT=8;K_ESC=4;K_ENTER=30;K_SPC=49;K_PLUS=50;K_MINUS=45
K_MENU=13;K_DEL=19
K_0=47;K_1=42;K_2=43;K_3=44;K_4=37;K_5=38;K_6=39;K_7=32;K_8=33;K_9=34
NUMK=[K_1,K_2,K_3,K_4,K_5,K_6,K_7,K_8,K_9,K_0]
def kd(k,b):
  return (k>>b)&1
def touchpos():
  try:
    m=mouse()
  except:
    try:
      m=eval("MOUSE")
    except:
      return None
  try:
    if len(m)>=2 and type(m[0]) in (int,float):
      return (m[0],m[1]) if m[0]>=0 else None
    for f in m:
      if f and len(f)>=2 and f[0]>=0:return (f[0],f[1])
  except:
    pass
  return None
def touched():
  return touchpos() is not None
def pressed():
  k=keyboard()
  return kd(k,K_UP) or kd(k,K_SPC) or kd(k,K_ENTER) or kd(k,K_8) or kd(k,K_PLUS) or touched()
def inbox(b,p):
  return p is not None and b[0]<=p[0]<b[0]+b[2] and b[1]<=p[1]<b[1]+b[3]
def release():
  while keyboard() or touched():
    pass

#---------- levels ----------
# chunks: rows top->bottom separated by '/', bottom-aligned to the ground
#   (n, ceiling_rows, floor_rows) = n columns of a block tunnel
# tiles:  # block   ^ spike   v hanging spike   = jump pad
#         o yellow orb (jump)   b blue orb (flip gravity)
# portals (fill the column): C cube S ship B ball U ufo W wave R robot
#         P spider G swing   u gravity up  d gravity down  > fast  < normal
LEVELS=[
 ["FIRST HOP",160.0,0x2050E0,0x40D0FF,[
  "................",
  "......^.........^.........^........",
  "......^^..........^^.........",
  ".......#.........##.........#........",
  "....##/..####/######........",
  "........^.......^^.......",
  "...#..#..#..#...........",
  ".....##.....##/..####...####........",
  "......^...^...^.........",
  "....#..../...##^^^##.......",
  ".....=........=......",
  "......^^.......#.......^^.......",
  "....###......../...#####^^^......",
  "......^.....^^.....^.........",
  "............................"]],
 ["NEON DRIFT",170.0,0xA020C0,0xFF60E0,[
  "..............",
  "......^.....^^.......=.^^^...........",
  "............o/..............^^^.......",
  "....##....##../..######..######^^^......",
  "...........=.^^^.................",
  "....S.....",
  (8,0,0),(6,0,2),(4,0,0),(6,3,0),(4,0,0),(6,0,3),(4,1,1),(6,4,0),(4,0,0),
  (6,0,4),(4,0,0),(5,2,2),(6,0,0),
  "....C.......",
  "......^^......#......^^.......",
  "....o...o...o/./...^^^^^^^^^^^^......",
  ".........####/......#######/^^^##########.......",
  "...................."]],
 ["OVERCLOCK",185.0,0xE04010,0xFFD030,[
  "............",
  "....^^......^^.......^.....^.....^......",
  "....##^^^##^^^##.........",
  "......=.....=.........o......",
  ".../.../..../...#######......",
  "...S..........",
  (6,0,0),(5,0,3),(3,0,0),(5,4,0),(3,0,0),(5,0,4),(3,1,1),(5,4,1),(3,1,1),
  (5,1,4),(3,0,0),(6,2,3),(4,0,0),(5,3,2),(6,0,0),
  "....C......",
  "....^....^^.....^^....o.......=.......",
  "....#^#^#^#.........",
  "..##.../...##^^^##^^^......",
  "............................"]],
 ["BOUNCE PARK",165.0,0xE05010,0xFF9040,[
  "............",
  "....^.......^^.........",
  "...B......",
  "##########################################/"
  "##########################################/"
  "............vvv.................vvv......./////"
  "......^^^................^^^..............",
  "....##.....##.....",
  "...U......",
  (4,0,0),(2,0,4),(5,0,0),(2,4,0),(5,0,0),(2,0,3),(4,0,0),(2,3,0),(5,0,0),(2,0,5),(6,0,0),
  "...C......",
  "...u.....",
  "vv........v........vv......."+"/"*7,
  "...d.....",
  "......^........^^.......",
  "................"]],
 ["WAVE RIDER",165.0,0x1060A0,0x40E0FF,[
  "............",
  "....^.....^^........",
  "...W......",
  (4,0,0),(3,0,4),(3,1,3),(3,2,2),(3,3,1),(3,4,0),(3,3,1),(3,2,2),(3,1,3),(3,0,4),
  (4,0,0),(3,0,4),(2,1,3),(2,2,2),(2,3,1),(3,4,0),(2,3,1),(2,2,2),(2,1,3),(3,0,4),(5,0,0),
  "...P......",
  "..............vvv.................vvv..........."+"/"*7+
  "......^^^.................^^^...........^^^.....",
  "...C......",
  "......^......^^......",
  "................"]],
 ["ROBOT WORKS",170.0,0x606878,0xE0E0F0,[
  "............",
  "...R......",
  "......#.......##.........###............",
  "....^^^^#......^^^^##......",
  "........#/.......##/....####^^^^^......",
  "...G......",
  (5,0,0),(3,0,3),(4,0,0),(3,3,0),(4,0,0),(3,0,4),(4,0,0),(3,4,0),(4,0,0),
  (3,2,2),(4,0,0),(3,0,3),(3,3,0),(6,0,0),
  "...C......",
  ".....^^.......o../.................^^^^^.....",
  "................"]],
 ["FULL SPECTRUM",175.0,0x202040,0xFF40A0,[
  "............",
  "......^......^^.......",
  "...S.....",
  (5,0,0),(4,0,3),(4,0,0),(4,3,0),(5,0,0),
  "...B.....",
  "################/################/"
  "......vvv......./////"
  "....^^^.........",
  "...U.....",
  (4,0,0),(2,0,4),(4,0,0),(2,4,0),(5,0,0),
  "...W.....",
  (3,0,0),(3,0,3),(3,1,2),(3,2,1),(3,3,0),(4,0,0),
  "...R.....",
  ".....#.......##.......",
  "...P.....",
  "..........vvv........"+"/"*7+
  "....^^^.........",
  "...G.....",
  (4,0,0),(3,0,3),(4,0,0),(3,3,0),(5,0,0),
  "...>.....",
  "...C.....",
  "......^........^^........^.........",
  "...<.....",
  "................"]]]

#custom levels (made in the editor)
NSLOT=2
CUST=[None]*NSLOT
CUSTSPEED=165.0

def chunkcols(chunks):
  cols=[]
  for ch in chunks:
    if type(ch)==tuple:
      n,cr,fr=ch
      for x in range(n):
        cols.append('#'*cr+'.'*(ROWS-cr-fr)+'#'*fr)
      continue
    rows=ch.split('/')
    if len(rows)>ROWS:raise ValueError('chunk has too many rows: '+ch[:20])
    w=max(len(r) for r in rows)
    rows=['.'*w]*(ROWS-len(rows))+[r+'.'*(w-len(r)) for r in rows]
    for x in range(w):
      cols.append("".join(rows[y][x] for y in range(ROWS)))
  return fixcols(cols)

def fixcols(cols):
  #portals always fill the whole column
  for i in range(len(cols)):
    c=cols[i]
    for ch in PORTALS:
      if ch in c:
        cols[i]=ch*ROWS;break
  return cols

def build(li):
  global LV,LW,SPEED,COL1,COL2,LNAME
  if li<len(LEVELS):
    name,sp,c1,c2,chunks=LEVELS[li]
    LNAME=name;SPEED=sp;COL1=c1;COL2=c2
    LV=chunkcols(chunks)
  else:
    k=li-len(LEVELS)
    LNAME="MY LEVEL "+str(k+1);SPEED=CUSTSPEED;COL1=0x208040;COL2=0x60FFA0
    cols=list(CUST[k]) if CUST[k] else []
    n=len(cols)
    while n>0 and cols[n-1]=='........':n-=1
    LV=['........']*6+cols[:n]+['........']*10
  LW=len(LV)

#---------- player physics (fixed step) ----------
class P:
  pass
def reset(p):
  p.x=0.0;p.hy=0.0;p.vy=0.0;p.ground=1;p.mode=0;p.ang=0.0;p.g=1;p.sf=1.0
  p.buf=0.0;p.dead=0;p.win=0;p.used={};p.rt=0.0;p.trail=[];p.tk=0

def surfaceDist(p,up):
  #spider: how far it can teleport up (up=1) or down (up=0)
  c0=int((p.x+1)/T);c1=int((p.x+T-1)/T)
  if up:
    best=CEIL
    for c in (c0,c1):
      if c>=LW:continue
      col=LV[c]
      for r in range(ROWS):
        if col[r]=='#':
          bot=(ROWS-1-r)*T
          if bot>=p.hy+T-1 and bot-T<best:best=bot-T
    return best
  best=0.0
  for c in (c0,c1):
    if c>=LW:continue
    col=LV[c]
    for r in range(ROWS):
      if col[r]=='#':
        top=(ROWS-r)*T
        if top<=p.hy+1 and top>best:best=top
  return best

def step(p,press,edge):
  if edge:p.buf=0.12
  elif p.buf>0:p.buf-=DT
  if not press:p.buf=0
  sp=SPEED*p.sf
  p.x+=sp*DT
  ph=p.hy;g=p.g;m=p.mode
  if m==0:
    if press and p.ground:
      p.vy=JV*g;p.ground=0
    p.vy-=GRAV*g*DT
  elif m==1:
    p.vy+=(SHIPUP if press else -SHIPDN)*g*DT
    if p.vy>SHIPMAX:p.vy=SHIPMAX
    if p.vy<-SHIPMAX:p.vy=-SHIPMAX
  elif m==2:
    if p.buf>0 and p.ground:
      p.g=-g;g=p.g;p.buf=0;p.ground=0;p.vy=-120.0*g
    p.vy-=BALLG*g*DT
  elif m==3:
    if p.buf>0:
      p.vy=UFOV*g;p.buf=0;p.ground=0
    p.vy-=UFOG*g*DT
  elif m==4:
    p.vy=(sp if press else -sp)*g
  elif m==5:
    if press and p.ground:
      p.vy=ROBV*g;p.rt=ROBTIME;p.ground=0
    if press and p.rt>0:
      p.vy+=ROBT*g*DT;p.rt-=DT
    else:
      p.rt=0.0
    p.vy-=GRAV*g*DT
  elif m==6:
    if p.buf>0 and p.ground:
      p.buf=0
      if g==1:p.hy=surfaceDist(p,1)
      else:p.hy=surfaceDist(p,0)
      p.g=-g;g=p.g;p.vy=0.0;ph=p.hy;p.ground=1
    p.vy-=GRAV*g*DT
  else:
    if p.buf>0:
      p.g=-g;g=p.g;p.buf=0
    p.vy-=SWINGA*g*DT
    if p.vy>SHIPMAX:p.vy=SHIPMAX
    if p.vy<-SHIPMAX:p.vy=-SHIPMAX
  if p.vy>900:p.vy=900.0
  if p.vy<-900:p.vy=-900.0
  p.hy+=p.vy*DT
  p.ground=0
  if p.hy<=0:
    p.hy=0.0
    if p.vy<0:p.vy=0.0
    if g==1:p.ground=1
  if p.hy>=CEIL:
    p.hy=CEIL
    if p.vy>0:p.vy=0.0
    if g==-1:p.ground=1
  x0=p.x+1;x1=p.x+T-1
  c0=int(x0/T);c1=int(x1/T)
  if c1>=LW:
    p.win=1;return
  headok=m in (1,2,3,4,7)
  for c in (c0-1,c0,c1,c1+1):
    if c<0 or c>=LW:continue
    col=LV[c]
    if col=='........':continue
    cx=c*T
    near=x1>cx and x0<cx+T
    for r in range(ROWS):
      ch=col[r]
      if ch=='.':continue
      bot=(ROWS-1-r)*T;top=bot+T
      if ch=='#':
        if near and p.hy+T-1>bot and p.hy+1<top:
          if p.vy<=0 and ph>=top-max(4,-p.vy*DT+3) and (g==1 or headok):
            p.hy=top;p.vy=0.0
            if g==1:p.ground=1
          elif p.vy>=0 and ph+T<=bot+max(4,p.vy*DT+3) and (g==-1 or headok):
            p.hy=bot-T;p.vy=0.0
            if g==-1:p.ground=1
          else:
            p.dead=1;return
      elif ch=='^':
        if x1>cx+6 and x0<cx+14 and p.hy<bot+11 and p.hy+T>bot+1:
          p.dead=1;return
      elif ch=='v':
        if x1>cx+6 and x0<cx+14 and p.hy+T>top-11 and p.hy<top-1:
          p.dead=1;return
      elif ch=='=':
        if near and m in (0,2,3,5,6) and p.hy<bot+6 and p.hy+T>bot:
          p.vy=PADV*g;p.ground=0
      elif ch=='o' or ch=='b':
        #ORB: works while you press (tap OR hold) and touch it, once per orb
        k=c*8+r
        if press and k not in p.used and abs(p.x+10-(cx+10))<21 and abs(p.hy+10-(bot+10))<21 and m!=4:
          p.used[k]=1;p.buf=0;p.ground=0
          if ch=='o':
            p.vy=(ORBV if m not in (1,7) else 260.0)*p.g
          else:
            p.g=-p.g;p.vy=-250.0*p.g
      else:
        if not near:continue
        i=MODES.find(ch)
        if i>=0:
          if p.mode!=i:
            p.mode=i;p.rt=0.0
            if i in (1,7):p.vy*=0.5
        elif ch=='u':p.g=-1
        elif ch=='d':p.g=1
        elif ch=='>':p.sf=1.3
        elif ch=='<':p.sf=1.0
  m=p.mode
  if m==0 or m==6 or m==5:
    if p.ground:
      p.ang=round(p.ang/(pi/2))*(pi/2)
    elif m==0:
      p.ang+=7.0*DT*p.g
  elif m==2:
    p.ang+=9.0*DT*p.g
  if m==4:
    p.tk+=1
    if p.tk%3==0:
      p.trail.append((p.x+10,p.hy+10))
      if len(p.trail)>16:p.trail.pop(0)
  elif p.trail:
    p.trail=[]

#---------- effects (visual only - never change the physics) ----------
_rs=[12345]
def rnd():
  _rs[0]=(_rs[0]*1103515245+12345)&0x7fffffff
  return _rs[0]/2147483648.0
FX=[]      #[kind,x,hy,vx,vy,life,maxlife,colour,size]
FXS={'shake':0.0,'flash':0.0,'fcol':0xFFFFFF,'txt':'','tt':0.0,'tcol':0xFFFFFF}
def fxBurst(x,hy,n,col,spd,life,up=0.0,size=4):
  for i in range(n):
    a=rnd()*2*pi;v=spd*(0.4+rnd()*0.6)
    FX.append(['p',x,hy,cos(a)*v,sin(a)*v+up,life,life,col,size])
  while len(FX)>48:FX.pop(0)
def fxRing(x,hy,col):
  FX.append(['r',x,hy,0,0,0.35,0.35,col,0])
def fxText(msg,col):
  FXS['txt']=msg;FXS['tt']=0.9;FXS['tcol']=col
def fxFlash(col,t=0.22):
  FXS['flash']=t;FXS['fcol']=col
def fxUpdate(dt):
  i=0
  while i<len(FX):
    f=FX[i];f[5]-=dt
    if f[5]<=0:
      FX.pop(i);continue
    if f[0]=='p':
      f[1]+=f[3]*dt;f[2]+=f[4]*dt;f[4]-=500*dt
    i+=1
  for k in ('shake','flash','tt'):
    if FXS[k]>0:FXS[k]=max(0.0,FXS[k]-dt)
def fxDraw(cam):
  for f in FX:
    sx=f[1]-cam;sy=GY-f[2];k=f[5]/f[6]
    if f[0]=='p':
      sz=max(1,int(f[8]*k+1))
      FR(int(sx-sz/2),int(sy-sz/2),sz,sz,f[7])
    else:
      rr=6+28*(1-k)
      pts=[(int(sx+rr*cos(a*pi/4)),int(sy+rr*sin(a*pi/4))) for a in range(9)]
      for j in range(8):line(G,pts[j][0],pts[j][1],pts[j+1][0],pts[j+1][1],f[7])
  if FXS['flash']>0:
    w=int(2+FXS['flash']*30);c=FXS['fcol']
    FR(0,TOPY,SW,w,c);FR(0,GY-w,SW,w,c);FR(0,TOPY,w,ROWS*T,c);FR(SW-w,TOPY,w,ROWS*T,c)
  if FXS['tt']>0:
    s=FXS['txt'];sz=3 if FXS['tt']<0.75 else 4
    bigtext(s,TOPY+14,sz,FXS['tcol'],0x000000)

def fxStep(p,b):
  #compare state before (b) and after one physics step and spawn effects
  m=p.mode;px=p.x+10;py=p.hy+10
  if m!=b[0]:
    fxFlash(MCOL[m]);fxText(MNAME[m]+"!",MCOL[m]);fxRing(px,py,MCOL[m]);fxBurst(px,py,10,MCOL[m],160,0.5)
  elif p.g!=b[1]:
    if m in (2,6,7):fxBurst(px,py,5,MCOL[m],110,0.3)
    else:fxRing(px,py,0xFFD000);fxText("GRAVITY!",0xFFD000)
  if len(p.used)>b[3]:
    fxRing(px,py,0xFFE020 if p.g==b[1] else 0x30A0FF);fxBurst(px,py,8,0xFFF080,150,0.4)
  if p.sf!=b[5]:
    fxText("FASTER!" if p.sf>1 else "NORMAL",0xFF6060 if p.sf>1 else 0x60FF60);fxFlash(0xFF4040 if p.sf>1 else 0x40FF40)
  if p.ground and not b[2] and m in (0,2,5,6) and abs(b[4])>150:
    fxBurst(px,p.hy if p.g==1 else p.hy+20,4,0xD0D0D0,70,0.3,0,3)
  if abs(p.vy-PADV*p.g)<1 and abs(b[4]-PADV*p.g)>1:
    fxBurst(px,p.hy,8,0xFFE020,140,0.45,120*p.g)
  #trails
  p.fxk=getattr(p,'fxk',0)+1
  if p.fxk%3==0 and m!=4:
    if m in (1,7):
      FX.append(['p',p.x+1,py-2*p.g,-60-rnd()*40,(rnd()-0.5)*40,0.3,0.3,0xFF9020 if rnd()<0.6 else 0xFFE060,4])
    else:
      FX.append(['p',p.x+4,py,-20,(rnd()-0.5)*20,0.28,0.28,shade(MCOL[m],0.7),4])

#---------- rendering ----------
def drawTile(ch,sx,sy,used,c,r):
  if ch=='#':
    FR(sx,sy,T,T,COL2);FR(sx+2,sy+2,T-4,T-4,0x0A0A14);FR(sx+7,sy+7,6,6,shade(COL2,0.5))
  elif ch=='^':
    poly([(sx+2,sy+T),(sx+10,sy+2),(sx+18,sy+T)],0xF0F0F0)
    poly([(sx+5,sy+T-1),(sx+10,sy+7),(sx+15,sy+T-1)],0x101010)
  elif ch=='v':
    poly([(sx+2,sy),(sx+10,sy+T-2),(sx+18,sy)],0xF0F0F0)
    poly([(sx+5,sy+1),(sx+10,sy+T-7),(sx+15,sy+1)],0x101010)
  elif ch=='=':
    gl=int(2+2*sin(ANIM[0]*10+sx*0.1))
    FR(sx+1,sy+T-5,T-2,5,0xFFE020);FR(sx+3,sy+T-5-gl,T-6,gl,0xFFF080)
  elif ch=='o' or ch=='b':
    oc=0x606060 if used else (0xFFE020 if ch=='o' else 0x30A0FF)
    k=1.0 if used else 0.85+0.15*sin(ANIM[0]*8+sx*0.05)
    cx=sx+10;cy=sy+10
    poly([(int(cx+9*k*cos(a*pi/4)),int(cy+9*k*sin(a*pi/4))) for a in range(8)],oc)
    q=int(3+2*k)
    FR(cx-q,cy-q,2*q,2*q,0xFFFFFF)
    if not used:box(int(cx-11*k)-1,int(cy-11*k)-1,int(22*k)+2,int(22*k)+2,shade(oc,0.6))

def portalCol(ch):
  i=MODES.find(ch)
  if i>=0:return MCOL[i]
  return {'u':0xFFD000,'d':0x30A0FF,'>':0xFF4040,'<':0x40FF40}.get(ch,0xFFFFFF)

ANIM=[0.0]
def drawPortal(ch,sx,lab=1):
  pc=portalCol(ch)
  FR(sx+4,TOPY,12,ROWS*T,shade(pc,0.45));FR(sx+8,TOPY,4,ROWS*T,pc)
  #shimmer: bright sparks running up the portal
  for k in range(3):
    y=GY-int((ANIM[0]*90+k*53+sx)%(ROWS*T))
    FR(sx+6,y,8,4,0xFFFFFF)
  if lab:
    FR(sx+3,TOPY+2,14,13,0x000000)
    textout(G,sx+6,TOPY+2,ch,pc)

def drawPlayer(p,sx,sy):
  #original NEONHOP designs: every mode is its own outlined, animated machine
  m=p.mode;g=p.g;t=ANIM[0]
  cx=sx+10;cy=sy+10
  col=MCOL[m];dk=shade(col,0.45);hl=mix(col,0xFFFFFF,0.55);OUT=0x05050A
  def F(x,y):
    return (int(cx+x),int(cy-y*g))
  def RP(pts,a):
    ca=cos(a);sa=sin(a)
    return [(int(cx+x*ca-y*sa),int(cy+x*sa+y*ca)) for (x,y) in pts]
  if m==0:
    #CUBE: bevelled tile with a glowing visor and a chevron
    a=p.ang
    poly(RP([(-11,-11),(11,-11),(11,11),(-11,11)],a),OUT)
    poly(RP([(-10,-10),(10,-10),(10,10),(-10,10)],a),0x30FF60)
    poly(RP([(-7,-7),(7,-7),(7,7),(-7,7)],a),0x10A040)
    poly(RP([(-7,-4),(7,-4),(7,0),(-7,0)],a),0x0A2A14)
    poly(RP([(-6,-3),(-1,-3),(-1,-1),(-6,-1)],a),0xC0FFD0)
    poly(RP([(-5,3),(0,6),(5,3),(5,5),(0,8),(-5,5)],a),0xB0FFC0)
  elif m==1:
    #SHIP: swept-wing jet with a glass cockpit and a flickering afterburner
    a=-atan2(p.vy*g,SPEED)*0.6
    def J(pts):
      return RP([(x,y*g) for (x,y) in pts],a)
    fl=4+int(4*rnd())
    poly(J([(-13,2),(-13-fl,4),(-13,6)]),0xFFB020)
    poly(J([(-13,-3),(14,1),(-13,7)]),OUT)
    poly(J([(-12,-2),(12,1),(-12,6)]),col)
    poly(J([(-9,3),(-5,9),(-1,9),(-2,3)]),dk)
    poly(J([(-11,-1),(-9,-5),(-6,-5),(-6,0)]),dk)
    poly(J([(-3,-2),(5,0),(-2,3)]),0x40D0FF)
    poly(J([(-2,-1),(1,-1),(-1,1)]),0xE0FFFF)
  elif m==2:
    #BALL: two-tone sphere with a spinning band and a shine
    pts=[(int(cx+11*cos(k*pi/6)),int(cy+11*sin(k*pi/6))) for k in range(12)]
    poly(pts,OUT)
    poly([(int(cx+10*cos(k*pi/6)),int(cy+10*sin(k*pi/6))) for k in range(12)],col)
    a=p.ang
    for k in range(3):
      b0=a+k*2*pi/3
      poly([(cx,cy),(int(cx+10*cos(b0)),int(cy+10*sin(b0))),(int(cx+10*cos(b0+0.5)),int(cy+10*sin(b0+0.5)))],dk)
    poly([(int(cx+4*cos(k*pi/3)),int(cy+4*sin(k*pi/3))) for k in range(6)],hl)
    FR(cx-6,cy-7,3,3,0xFFFFFF)
  elif m==3:
    #UFO: saucer with a glass dome and blinking rim lights
    poly([F(-13,-1),F(13,-1),F(9,-6),F(-9,-6)],OUT)
    poly([F(-12,-1),F(12,-1),F(8,-5),F(-8,-5)],0xB8BCD0)
    poly([F(-12,-1),F(12,-1),F(10,1),F(-10,1)],0x707488)
    poly([F(-6,-1),F(6,-1),F(5,5),F(2,8),F(-2,8),F(-5,5)],OUT)
    poly([F(-5,0),F(5,0),F(4,4),F(1,7),F(-1,7),F(-4,4)],0x50E0FF)
    FR(cx-3,cy-(5*g)-1,2,2,0xFFFFFF)
    on=int(t*8)%3
    for k in range(3):
      lx=-8+k*8
      c=0xFF4040 if k==on else 0x602020
      x,y=F(lx,-3);FR(x-1,y-1,3,3,c)
    x,y=F(0,-7);FR(x-3,y,6,2,col)
  elif m==4:
    #WAVE: glowing dart that points where it is going
    d=1 if p.vy*g>0 else -1
    a=-0.78*d*g
    poly(RP([(-9,-7),(11,0),(-9,7),(-5,0)],a),OUT)
    poly(RP([(-8,-6),(9,0),(-8,6),(-4,0)],a),col)
    poly(RP([(-3,-2),(6,0),(-3,2)],a),0xFFFFFF)
  elif m==5:
    #ROBOT: boxy walker with antenna, visor eye and stepping legs
    st=int(p.x/5)%4 if p.ground else 1
    lo=[(0,0),(2,-2),(0,0),(-2,2)][st]
    poly([F(-9,9),F(9,9),F(9,-3),F(-9,-3)],OUT)
    poly([F(-8,8),F(8,8),F(8,-2),F(-8,-2)],0xD8D8E8)
    poly([F(-6,6),F(6,6),F(6,1),F(-6,1)],0x202840)
    ex=int(2*sin(t*3));x,y=F(-2+ex,4);FR(x-2,y-1,5,3,0xFF3040)
    x,y=F(0,9);FR(x,min(y,y-4*g),1,4,0x909090)
    x,y=F(0,13);FR(x-1,y-1,3,3,0xFF3040 if int(t*4)%2 else 0x601020)
    for sd,o in ((-5,lo[0]),(4,lo[1])):
      poly([F(sd-1,-3),F(sd+2,-3),F(sd+2+o,-10),F(sd-1+o,-10)],OUT)
      poly([F(sd,-3),F(sd+1,-3),F(sd+1+o,-10),F(sd+o,-10)],0x9098B0)
      x,y=F(sd-2+o,-10);FR(x,y-1,6,2,0x606878)
  elif m==6:
    #SPIDER: round body with two eyes and six scuttling legs
    ph=(p.x*0.25)%6.28 if p.ground else 1.0
    for k in range(3):
      for sd in (-1,1):
        bx=sd*(3+k*2);kx=sd*(8+k*2);fx=sd*(10+k*2)+int(2*sin(ph+k+sd))
        x0,y0=F(bx,-1);x1,y1=F(kx,3);x2,y2=F(fx,-9)
        lc=mix(col,0xFFFFFF,0.2)
        line(G,x0,y0,x1,y1,lc);line(G,x1,y1,x2,y2,lc);line(G,x1+1,y1,x2+1,y2,lc)
    poly([(int(cx+8*cos(k*pi/4)),int(cy-1*g+7*sin(k*pi/4))) for k in range(8)],OUT)
    poly([(int(cx+7*cos(k*pi/4)),int(cy-1*g+6*sin(k*pi/4))) for k in range(8)],col)
    for ex in (-3,2):
      x,y=F(ex,2);FR(x,y-1,3,3,0xFFFFFF);FR(x+1,y,1,1,0x000000)
  else:
    #SWING: little pod hanging under a spinning rotor
    a=t*25
    for k in range(2):
      w=int(12*cos(a+k*pi/2))
      x,y=F(0,10);FR(x-abs(w),y-1,2*abs(w)+1,2,0xE0E0E0 if k==0 else 0xA0A0A0)
    x,y=F(0,10);x2,y2=F(0,5);line(G,x,y,x2,y2,0x808080)
    poly([F(-9,5),F(9,5),F(7,-6),F(-7,-6)],OUT)
    poly([F(-8,4),F(8,4),F(6,-5),F(-6,-5)],col)
    poly([F(-4,3),F(5,3),F(4,-2),F(-3,-2)],0x40D0FF)
    x,y=F(-2,2);FR(x,y,2,2,0xFFFFFF)
    x,y=F(-9,-1);FR(x-3,y-1,3,3,0xFFB020 if int(t*10)%2 else 0xFF6020)

def render(p,cam,att,t,parts,best):
  prog=min(1.0,p.x/(LW*T))
  bg=mix(shade(COL1,0.35),shade(COL2,0.25),prog)
  beat=(t*2.0)%1.0
  bc=COL2
  if beat<0.08:
    bg=mix(bg,0xFFFFFF,0.08);bc=mix(COL2,0xFFFFFF,0.5)
  ANIM[0]=t
  #screen shake after a crash
  if FXS['shake']>0:cam+=(rnd()-0.5)*14*FXS['shake']/0.35
  FR(0,0,SW,GY,bg)
  ps=int(cam*0.1)
  for i in range(5):
    x=(i*90-ps)%450-70
    FR(x,TOPY+10+(i*29)%40,64,64,mix(bg,0x000000,0.15))
  ps=int(cam*0.25)
  for i in range(6):
    x=(i*70-ps)%400-60
    s2=40+int(6*sin(t*2+i))
    FR(x,TOPY+40+(i*37)%70,s2,s2,mix(bg,0x000000,0.28))
  if p.mode!=0 and p.mode!=5:
    FR(0,TOPY-2,SW,2,COL2)
  FR(0,GY,SW,SH-GY,shade(COL1,0.55))
  FR(0,GY,SW,2,0xFFFFFF)
  gs=int(cam)%40
  for i in range(10):
    FR(i*40-gs,GY+2,1,SH-GY-2,shade(COL1,0.4))
  c0=int(cam/T);off=cam-c0*T
  for i in range(SW//T+2):
    c=c0+i
    if c<0 or c>=LW:continue
    col=LV[c]
    if col=='........':continue
    sx=int(i*T-off)
    if col[0] in PORTALS and col[0]==col[7]:
      drawPortal(col[0],sx);continue
    r=0
    while r<ROWS:
      ch=col[r]
      if ch=='#':
        #draw a whole vertical stack of blocks at once (much fewer draw calls)
        r0=r
        while r<ROWS and col[r]=='#':r+=1
        y0=TOPY+r0*T;h=(r-r0)*T
        FR(sx,y0,T,h,bc);FR(sx+2,y0+2,T-4,h-4,0x0A0A14)
        for q in range(r0,r):FR(sx+7,TOPY+q*T+7,6,6,shade(COL2,0.5))
        continue
      if ch!='.':drawTile(ch,sx,TOPY+r*T,(c*8+r) in p.used,c,r)
      r+=1
  ax=int(40-cam)
  if ax>-150:
    textout(G,ax,TOPY+20,"Attempt "+str(att),0xFFFFFF)
  #wave trail
  if p.mode==4 and len(p.trail)>1:
    for k in range(1,len(p.trail)):
      a=p.trail[k-1];b=p.trail[k]
      line(G,int(a[0]-cam),int(GY-a[1]),int(b[0]-cam),int(GY-b[1]),0x80F0FF)
  if not p.dead:
    drawPlayer(p,PX,GY-p.hy-T)
    if beat<0.08:box(PX-3,GY-p.hy-T-3,T+6,T+6,MCOL[p.mode])
  for q in parts:
    FR(int(q[0]-cam),int(GY-q[1]),5,5,q[4])
  fxDraw(cam)
  FR(112,6,148,6,0x202020);FR(112,6,int(148*prog),6,0x30FF60)
  textout(G,266,2,str(int(prog*100))+"%",0xFFFFFF)
  textout(G,4,2,LNAME,0xFFFFFF)
  textout(G,4,16,MNAME[p.mode]+(" (upside down)" if p.g<0 else ""),MCOL[p.mode])

def flip():
  strblit(0,0,0,SW,SH,G)

#---------- saving ----------
NLEV=len(LEVELS)+NSLOT
BEST=[0]*NLEV
def loadBest():
  try:
    f=open("neonhop.txt","r");v=f.read().split(",");f.close()
    for i in range(min(len(v),NLEV)):BEST[i]=int(v[i])
  except:
    pass
def saveBest():
  try:
    f=open("neonhop.txt","w");f.write(",".join(str(b) for b in BEST));f.close()
  except:
    pass
def slotfile(k):
  return "nhlevel"+str(k+1)+".txt"
def loadSlot(k):
  try:
    f=open(slotfile(k),"r");s=f.read();f.close()
    cols=[]
    for tok in s.strip().split(","):
      if "*" in tok:
        n,c=tok.split("*")
        cols+= [c]*int(n)
      elif tok:
        cols.append(tok)
    cols=[(c+'........')[:ROWS] for c in cols]
    CUST[k]=cols
  except:
    CUST[k]=None
def saveSlot(k,cols):
  #run-length compressed: "12*........,1*....##.." ...
  out=[];i=0;n=len(cols)
  while n>0 and cols[n-1]=='........':n-=1
  while i<n:
    j=i
    while j<n and cols[j]==cols[i]:j+=1
    out.append(str(j-i)+"*"+cols[i]);i=j
  try:
    f=open(slotfile(k),"w");f.write(",".join(out));f.close()
    CUST[k]=list(cols[:n])
    return 1
  except:
    CUST[k]=list(cols[:n])
    return 0

#---------- menus ----------
MBTN=[]
for i in range(10):
  MBTN.append((8+(i%2)*156,44+(i//2)*36,148,32))
DIFF=["EASY","NORMAL","HARD","NORMAL","NORMAL","HARD","INSANE"]
def drawMenu(t,hi):
  FR(0,0,SW,SH,0x0A0A20)
  #drifting neon squares + a pulsing title
  for i in range(7):
    x=int((i*53+t*(20+i*6))%(SW+40))-30;y=int(60+((i*71)%150)+8*sin(t*1.5+i))
    sz=14+(i*5)%16
    FR(x,y,sz,sz,mix(0x0A0A20,MCOL[i%8],0.22))
  pc=MCOL[int(t*2)%8]
  bigtext("NEONHOP",6,4,mix(0x30FF60,pc,0.5+0.5*sin(t*3)),0x004010)
  for i in range(10):
    x,y,w,h=MBTN[i]
    if i<len(LEVELS):
      c=LEVELS[i][2];name=str(i+1)+". "+LEVELS[i][0];sub=DIFF[i]+"  "+str(BEST[i])+"%"
    elif i<NLEV:
      c=0x208040;k=i-len(LEVELS)
      name=str(i+1)+". MY LEVEL "+str(k+1)
      sub=("best "+str(BEST[i])+"%") if CUST[k] else "empty - build it!"
    else:
      c=0x604010;name="0. LEVEL EDITOR";sub="build + save"
    lift=2 if i==hi else 0
    FR(x+2,y+2,w,h,0x000000)
    FR(x-lift,y-lift,w,h,shade(c,0.8 if i==hi else 0.6))
    ec=0xFFFFFF if i>=NLEV else (LEVELS[i][3] if i<len(LEVELS) else 0x60FFA0)
    box(x-lift,y-lift,w,h,mix(ec,0xFFFFFF,0.5+0.5*sin(t*6)) if i==hi else ec)
    textout(G,x+6-lift,y+3-lift,name,0xFFFFFF)
    textout(G,x+6-lift,y+17-lift,sub,0xE0E0FF)
    if i<NLEV:
      FR(x+w-44-lift,y+20-lift,38,6,0x101010);FR(x+w-44-lift,y+20-lift,int(38*BEST[i]/100),6,0x30FF60)
  ctext("Tap a level or press 1-9 / 0.  ESC quits.",224,0xA0A0C0)
  flip()

def menu():
  release()
  t0=ticks();hi=int((ticks()//1000)%10)
  while True:
    t=(ticks()-t0)/1000.0
    hi=int(t/1.5)%10
    drawMenu(t,hi)
    k=keyboard()
    if kd(k,K_ESC):return -1
    for i in range(10):
      if kd(k,NUMK[i]):return i
    tp=touchpos()
    if tp:
      for i in range(10):
        if inbox(MBTN[i],tp):
          drawMenu(t,i)
          release()
          return i

def play(li,fromEditor=0):
  build(li)
  if LW<=16:
    return
  p=P();att=1
  while True:
    reset(p)
    FX[:]=[];FXS['shake']=0;FXS['flash']=0;FXS['tt']=0
    t=0.0;acc=0.0;last=ticks();prev=0;parts=[]
    while pressed():
      pass
    while True:
      now=ticks();fdt=(now-last)/1000.0;last=now
      if fdt>0.1:fdt=0.1
      if fdt<0:fdt=0
      k=keyboard()
      if kd(k,K_ESC):
        return
      pr=1 if pressed() else 0
      edge=pr and not prev;prev=pr
      acc+=fdt;t+=fdt
      if not p.dead:
        if edge and acc<DT:acc=DT      #never lose a tap
        while acc>=DT and not p.dead and not p.win:
          b=(p.mode,p.g,p.ground,len(p.used),p.vy,p.sf)
          step(p,pr,edge);edge=0;acc-=DT
          if not p.dead:fxStep(p,b)
        fxUpdate(fdt)
        if p.dead:
          import_parts(parts,p)
          FXS['shake']=0.35;fxFlash(0xFFFFFF,0.25);fxBurst(p.x+10,p.hy+10,12,MCOL[p.mode],260,0.6)
          dtime=0.0
          pc=int(100*min(1.0,p.x/(LW*T)))
          if pc>BEST[li]:BEST[li]=pc;saveBest()
      else:
        acc=0
        fxUpdate(fdt)
        dtime+=fdt
        for q in parts:
          q[0]+=q[2]*fdt;q[1]+=q[3]*fdt;q[3]-=600*fdt
        if dtime>0.8:
          att+=1;break
      cam=p.x-PX
      render(p,cam,att,t,parts,BEST[li])
      if p.win:
        BEST[li]=100;saveBest()
        cols_=[0xFF4060,0xFFE040,0x40FF80,0x40C0FF,0xFF60E0,0xFFFFFF]
        for i in range(36):
          a=rnd()*pi;v=150+rnd()*250
          FX.append(['p',p.x+10,p.hy+10,cos(a)*v*1.2,sin(a)*v,1.3,1.3,cols_[i%6],5])
        fxFlash(0x30FF60,0.4)
        t1=ticks()
        while ticks()-t1<1100:
          fdt=0.04;fxUpdate(fdt);t+=fdt
          render(p,p.x-PX,att,t,parts,BEST[li]);flip()
        flip()
        FR(30,70,260,110,0x101030);box(30,70,260,110,0x30FF60)
        bigtext("COMPLETE",84,4,0xFFE020,0x000000)
        ctext(LNAME+"  -  "+str(att)+" attempt"+("s" if att>1 else ""),124,0xFFFFFF)
        ctext("Tap / Enter: "+("back to editor" if fromEditor else "menu"),150,0xA0FFA0)
        flip()
        while pressed():
          pass
        while not pressed():
          if kd(keyboard(),K_ESC):break
        while pressed():
          pass
        return
      flip()

def import_parts(parts,p):
  for i in range(14):
    a=i*2*pi/14
    parts.append([p.x+10,p.hy+10,cos(a)*(120+(i%3)*50),sin(a)*(120+(i%4)*40)+150,0x30FF60 if i%2 else 0xFFFFFF])

#---------- level editor ----------
PAL=".#^v=obCSBUWRPGud><"
PALN={'.':"ERASER",'#':"BLOCK",'^':"SPIKE",'v':"HANGING SPIKE",'=':"JUMP PAD",'o':"YELLOW ORB",
      'b':"BLUE ORB (flip)",'u':"GRAVITY UP",'d':"GRAVITY DOWN",'>':"FAST",'<':"NORMAL SPEED"}
for _i in range(8):PALN[MODES[_i]]=MNAME[_i]+" PORTAL"
EW=320           #editor level length (columns)
EB_L=(2,2,34,26);EB_R=(38,2,34,26);EB_PLAY=(160,2,50,26);EB_SAVE=(214,2,50,26);EB_EXIT=(268,2,50,26)
STRIP=(0,30,SW,9)   #overview of the whole level: tap/drag to jump there
PALY=210;PALX=6;PALS=16

def ebtn(b,label,c):
  x,y,w,h=b
  FR(x,y,w,h,c);box(x,y,w,h,0xFFFFFF)
  textout(G,x+(w-len(label)*7)//2,y+6,label,0xFFFFFF)

def drawPalIcon(ch,x,y,sel):
  FR(x,y,PALS,PALS,0x000000)
  if ch in PORTALS:
    pc=portalCol(ch);FR(x+5,y,6,PALS,pc);textout(G,x+4,y+1,ch,0x000000)
  elif ch=='.':
    box(x+3,y+3,10,10,0xFF4040);line(G,x+3,y+3,x+12,y+12,0xFF4040)
  elif ch=='#':
    box(x+1,y+1,14,14,COL2)
  elif ch=='^':
    poly([(x+1,y+15),(x+8,y+2),(x+15,y+15)],0xF0F0F0)
  elif ch=='v':
    poly([(x+1,y+1),(x+8,y+14),(x+15,y+1)],0xF0F0F0)
  elif ch=='=':
    FR(x+1,y+11,14,5,0xFFE020)
  else:
    FR(x+3,y+3,10,10,0xFFE020 if ch=='o' else 0x30A0FF)
  if sel:box(x-1,y-1,PALS+2,PALS+2,0xFFFFFF)

def editorRender(cols,ecam,cx,cy,sel,msg,strip=(),drag=0):
  FR(0,0,SW,SH,0x101828)
  FR(0,TOPY,SW,ROWS*T,0x182038)
  for i in range(SW//T+1):
    c=ecam+i
    if c%5==0:FR(i*T,TOPY,1,ROWS*T,0x283458 if c%20 else 0x4050A0)
    if c>=EW:FR(i*T,TOPY,T,ROWS*T,0x301010);continue
    col=cols[c]
    if col!='........':
      if col[0] in PORTALS and col[0]==col[7]:
        drawPortal(col[0],i*T)
      else:
        for r in range(ROWS):
          if col[r]!='.':drawTile(col[r],i*T,TOPY+r*T,0,c,r)
  for r in range(ROWS+1):
    FR(0,TOPY+r*T,SW,1,0x283458)
  if ecam==0:
    FR(0,GY-T,6*T,T,0x204020);textout(G,4,GY-T+3,"START",0x80FF80)
  #cursor
  box((cx-ecam)*T,TOPY+cy*T,T,T,0xFFFF00);box((cx-ecam)*T+1,TOPY+cy*T+1,T-2,T-2,0xFFFF00)
  FR(0,GY,SW,1,0xFFFFFF)
  ebtn(EB_L,"<<",0x304060);ebtn(EB_R,">>",0x304060)
  textout(G,78,2,"col "+str(cx),0xC0C0FF);textout(G,78,15,"EDIT "+str(ESLOT[0]+1),0x80FF80)
  #overview strip of the whole level with the visible window marked
  FR(0,30,SW,9,0x000000)
  for (x,w,c) in strip:FR(x,31,w,7,c)
  vx=int(ecam*SW/EW);vw=max(3,int(16*SW/EW))
  box(vx,30,vw,9,0xFFFF00)
  if drag:textout(G,250,PALY-12,"scrolling",0xFFFF80)
  ebtn(EB_PLAY,"PLAY",0x207030);ebtn(EB_SAVE,"SAVE",0x205090);ebtn(EB_EXIT,"EXIT",0x802020)
  for i in range(len(PAL)):
    drawPalIcon(PAL[i],PALX+i*PALS,PALY,PAL[i]==sel)
  textout(G,6,PALY-12+0,msg if msg else PALN.get(sel,sel),0xFFFFFF if msg else 0xFFE080)
  flip()

ESLOT=[0]
def makeStrip(cols):
  #overview: runs of columns with the same colour -> few draw calls
  out=[];sc=SW/EW;cur=None;x0=0
  for c in range(EW+1):
    col=cols[c] if c<EW else '........'
    if col=='........':k=None
    elif col[0] in PORTALS and col[0]==col[7]:k=portalCol(col[0])
    elif '^' in col or 'v' in col:k=0xF0F0F0
    elif 'o' in col or 'b' in col or '=' in col:k=0xFFE020
    else:k=COL2
    if k!=cur:
      if cur is not None:out.append((int(x0*sc),max(1,int((c-x0)*sc)),cur))
      cur=k;x0=c
  return out

def editor(k):
  ESLOT[0]=k
  build(len(LEVELS)+k)
  cols=list(CUST[k]) if CUST[k] else []
  cols=(cols+['........']*EW)[:EW]
  ecam=0;cx=8;cy=ROWS-1;sel='#'
  msg="Tap = place, drag = scroll, top bar = jump";mt=ticks()
  prevk=keyboard();prevt=None;dirty=0
  strip=makeStrip(cols)
  down=None;drag=0;rep=0;rept=0
  release()
  while True:
    if msg and ticks()-mt>2500:msg=""
    editorRender(cols,ecam,cx,cy,sel,msg,strip,drag)
    k=keyboard();pk=k&~prevk;prevk=k
    tp=touchpos()
    newtap=tp is not None and prevt is None
    lifted=tp is None and prevt is not None
    last_tp=prevt
    prevt=tp
    act=None
    if kd(pk,K_ESC) or (newtap and inbox(EB_EXIT,tp)):
      if dirty:saveSlot(k,cols)
      return
    if kd(pk,K_MENU) or (newtap and inbox(EB_SAVE,tp)):
      ok=saveSlot(k,cols);dirty=0
      msg="SAVED to "+slotfile(k) if ok else "Save failed (kept until you quit)";mt=ticks()
    if kd(pk,K_1) or (newtap and inbox(EB_PLAY,tp)):
      saveSlot(k,cols);dirty=0
      release()
      play(len(LEVELS)+k,1)
      release();prevk=keyboard();prevt=None;down=None;drag=0
      continue
    #arrow keys: press = 1 step, hold = keep moving
    arrows=k&((1<<K_LT)|(1<<K_RT)|(1<<K_UP)|(1<<K_DN))
    mv=pk&arrows
    if arrows and not mv:
      if ticks()-rept>(110 if rep else 320):mv=arrows;rep=1;rept=ticks()
    elif mv:
      rep=0;rept=ticks()
    if not arrows:rep=0
    if kd(mv,K_LT):cx=max(0,cx-1)
    if kd(mv,K_RT):cx=min(EW-1,cx+1)
    if kd(mv,K_UP):cy=max(0,cy-1)
    if kd(mv,K_DN):cy=min(ROWS-1,cy+1)
    if kd(pk,K_7) or (newtap and inbox(EB_L,tp)):ecam=max(0,ecam-12);cx=max(ecam,min(cx,ecam+15))
    if kd(pk,K_9) or (newtap and inbox(EB_R,tp)):ecam=min(EW-16,ecam+12);cx=max(ecam,min(cx,ecam+15))
    if kd(pk,K_PLUS):sel=PAL[(PAL.find(sel)+1)%len(PAL)]
    if kd(pk,K_MINUS):sel=PAL[(PAL.find(sel)-1)%len(PAL)]
    if mv:
      if cx<ecam:ecam=cx
      if cx>ecam+15:ecam=cx-15
    if kd(pk,K_ENTER):act=(cx,cy,sel)
    if kd(pk,K_DEL):act=(cx,cy,'.')
    #touch: palette / overview strip act at once; the grid places on release
    #unless you dragged (then it scrolls)
    if newtap:
      x,y=tp
      if PALY<=y<PALY+PALS and PALX<=x<PALX+len(PAL)*PALS:
        sel=PAL[int((x-PALX)//PALS)]
      elif inbox(STRIP,tp):
        down=('s',x,y,ecam)
      elif TOPY<=y<GY:
        down=('g',x,y,ecam);drag=0
    if tp is not None and down:
      if down[0]=='s':
        ecam=int(max(0,min(EW-16,tp[0]*EW/SW-8)));cx=max(ecam,min(cx,ecam+15))
      else:
        dx=tp[0]-down[1]
        if abs(dx)>10:drag=1
        if drag:
          ecam=int(max(0,min(EW-16,down[3]-round(dx/T))));cx=max(ecam,min(cx,ecam+15))
    if lifted and down:
      if down[0]=='g' and not drag:
        x,y=down[1],down[2]
        c=down[3]+int(x//T);r=int((y-TOPY)//T)
        if 0<=c<EW and 0<=r<ROWS:
          cx=c;cy=r
          cur=cols[c][r]
          act=(c,r,'.' if (cur==sel or (sel in PORTALS and cols[c][0]==sel)) else sel)
      down=None;drag=0
    if act:
      c,r,ch=act
      col=cols[c]
      if ch in PORTALS:
        col=ch*ROWS
      else:
        if col[0] in PORTALS and col[0]==col[7]:col='........'
        col=col[:r]+ch+col[r+1:]
      cols[c]=col;dirty=1
      strip=makeStrip(cols)

def slotMenu():
  FR(0,0,SW,SH,0x0A0A20)
  bigtext("EDITOR",16,4,0xFFB040,0x402000)
  b=[(30,70,260,40),(30,120,260,40),(30,180,260,34)]
  for i in range(NSLOT):
    x,y,w,h=b[i]
    FR(x,y,w,h,0x206040);box(x,y,w,h,0xFFFFFF)
    textout(G,x+10,y+6,"EDIT MY LEVEL "+str(i+1),0xFFFFFF)
    n=len(CUST[i]) if CUST[i] else 0
    textout(G,x+10,y+22,(str(n)+" columns saved") if n else "empty",0xC0FFC0)
  x,y,w,h=b[2];FR(x,y,w,h,0x602020);box(x,y,w,h,0xFFFFFF);textout(G,x+100,y+10,"BACK",0xFFFFFF)
  textout(G,10,222,"Editor keys: arrows move, Enter place, Del erase,",0xA0A0C0)
  flip()
  release()
  while True:
    k=keyboard()
    if kd(k,K_ESC):return -1
    if kd(k,K_1):return 0
    if kd(k,K_2):return 1
    tp=touchpos()
    if tp:
      for i in range(3):
        if inbox(b[i],tp):
          release()
          return i if i<NSLOT else -1

def main():
  dimgrob(G,SW,SH,0)
  loadBest()
  for k in range(NSLOT):loadSlot(k)
  while True:
    li=menu()
    if li<0:return
    if li==9:
      s=slotMenu()
      if s>=0:editor(s)
      continue
    if li>=len(LEVELS) and not CUST[li-len(LEVELS)]:
      editor(li-len(LEVELS));continue
    play(li)

main()
