#ABYSSAL - deep-sea facility horror for the HP Prime
#Go deeper room by room. When the lights flicker, HIDE in a locker.
#Python app (hpprime module). Touch buttons + keyboard.
from hpprime import *
from math import *

try:
  ticks()
except:
  def ticks():
    return int(eval("TICKS()"))

_rs=[ticks()&0xffff|1]
def rnd():
  _rs[0]=(_rs[0]*1103515245+12345)&0x7fffffff
  return _rs[0]/2147483648.0
def rint(n):
  return int(rnd()*n)

SW=320;VH=200;HH=100;G=1

FRM=[0]
def FR(x,y,w,h,c):
  if w<=0 or h<=0:return
  if FRM[0]==0:
    try:
      fillrect(G,int(x),int(y),int(w),int(h),c,c);return
    except:
      FRM[0]=1
  x=int(x);y=int(y);w=int(w);h=int(h)
  if w>h:
    for i in range(h):line(G,x,y+i,x+w-1,y+i,c)
  else:
    for i in range(w):line(G,x+i,y,x+i,y+h-1,c)

def shade(c,f):
  if f>1:f=1
  if f<0:f=0
  return (int(((c>>16)&255)*f)<<16)|(int(((c>>8)&255)*f)<<8)|int((c&255)*f)

FONT={
'A':"0111010001111111000110001",'B':"1111010001111101000111110",
'C':"0111110000100001000001111",'D':"1111010001100011000111110",
'E':"1111110000111101000011111",'H':"1000110001111111000110001",
'I':"1111100100001000010011111",'L':"1000010000100001000011111",
'O':"0111010001100011000101110",'P':"1111010001111101000010000",
'S':"0111110000011100000111110",'U':"1000110001100011000101110",
'Y':"1000101010001000010000100",'R':"1111010001111101001010001",
'T':"1111100100001000010000100",'N':"1000111001101011001110001",
'!':"0010000100001000000000100",' ':"0000000000000000000000000"}
def bigtext(s,y,sz,c):
  x0=(SW-len(s)*6*sz)//2
  for n in range(len(s)):
    f=FONT.get(s[n],FONT[' '])
    for i in range(25):
      if f[i]=='1':
        FR(x0+n*6*sz+(i%5)*sz,y+(i//5)*sz,sz,sz,c)
def ctext(s,y,c):
  textout(G,(SW-len(s)*7)//2,y,s,c)

#---------- input ----------
K_UP=2;K_DN=12;K_LT=7;K_RT=8;K_ESC=4;K_ENTER=30;K_SPC=49;K_DEL=19
K_8=33;K_5=38;K_4=37;K_6=39;K_PLUS=50;K_MINUS=45
def kd(k,b):
  return (k>>b)&1
def touches():
  pts=[]
  try:
    m=mouse()
  except:
    try:
      m=eval("MOUSE")
    except:
      return pts
  try:
    if len(m)>=2 and type(m[0]) in (int,float):
      m=[m]
    for f in m:
      if f and len(f)>=2 and f[0]>=0 and f[1]>=0:
        pts.append((f[0],f[1]))
  except:
    pass
  return pts
def inside(b,pts):
  x,y,w,h=b
  for p in pts:
    if x<=p[0]<x+w and y<=p[1]<y+h:return 1
  return 0
B_FW=(46,112,40,40);B_LT=(4,156,40,40);B_BK=(46,156,40,40);B_RT=(88,156,40,40)
B_ACT=(262,140,54,54)
def tbtn(b,on,lab):
  x,y,w,h=b
  if on:FR(x,y,w,h,0x2080A0)
  FR(x,y,w,1,0xA0E0F0);FR(x,y+h-1,w,1,0xA0E0F0)
  FR(x,y,1,h,0xA0E0F0);FR(x+w-1,y,1,h,0xA0E0F0)
  textout(G,x+(w-len(lab)*7)//2,y+h//2-6,lab,0xE0F8FF)

#---------- level generation ----------
NR=40         #rooms
MH=13         #map height
ZONEC=[0x4E7C80,0x7A6650,0x6E4A52,0x3E4C6E]
ZONEN=["Upper Labs","Rusted Hold","Red Sector","The Trench"]
def gen():
  global MAP,MW,ROOMS,ENTS,ZX
  rooms=[];x=1;prev=6
  cols=[]
  for r in range(NR):
    w=5+rint(5);h=3+rint(5)
    if r==NR-1:w=7;h=5
    lo=max(1,prev-h+1);hi=min(prev,MH-1-h)
    y0=lo+rint(hi-lo+1);y1=y0+h-1
    dy=y0+rint(h)
    rooms.append([x,x+w-1,y0,y1,x+w,dy,prev])
    x=x+w+1;prev=dy
  MW=x+1
  MAP=[[1]*MW for i in range(MH)]
  ENTS=[]
  ZX=[0]*MW
  for r in range(NR):
    x0,x1,y0,y1,dx,dy,py=rooms[r]
    z=min(3,r*4//NR)
    for xx in range(x0-1,min(MW,x1+2)):ZX[xx]=z
    for yy in range(y0,y1+1):
      for xx in range(x0,x1+1):
        MAP[yy][xx]=0
    #pillar in big rooms
    if x1-x0>=6 and y1-y0>=4 and rnd()<0.6:
      MAP[(y0+y1)//2][(x0+x1)//2]=2
    #windows to the ocean
    for xx in range(x0,x1+1):
      if rnd()<0.22:MAP[y0-1][xx]=6
      if rnd()<0.22:MAP[y1+1][xx]=6
    #lockers (always at least one)
    n=1+rint(3)
    for i in range(n):
      xx=x0+rint(x1-x0+1)
      if rnd()<0.5:MAP[y0-1][xx]=5
      else:MAP[y1+1][xx]=5
    #door to next room
    if r==NR-1:
      MAP[dy][dx]=8
    elif (r+1)%6==0:
      MAP[dy][dx]=10
      ex,ey=freeCell(rooms[r]);ENTS.append(Ent(ex,ey,0))
    else:
      MAP[dy][dx]=9
    if r>1 and rnd()<0.2:
      ex,ey=freeCell(rooms[r]);ENTS.append(Ent(ex,ey,1))
    if r>=7 and rnd()<0.2 and x1-x0>=5:
      ENTS.append(Ent(x0+(x1-x0)*0.5+0.5,y0+0.5,2))
  ENTS=[e for e in ENTS if MAP[int(e.y)][int(e.x)]==0]
  ROOMS=rooms

def freeCell(r):
  x0,x1,y0,y1=r[0],r[1],r[2],r[3]
  for i in range(40):
    x=x0+rint(x1-x0+1);y=y0+rint(y1-y0+1)
    if MAP[y][x]==0:return x+0.5,y+0.5
  return x0+0.5,r[6]+0.5

def roomAt(x):
  for r in range(len(ROOMS)):
    if x<ROOMS[r][4]+1:return r
  return len(ROOMS)-1

def solid(x,y):
  ix=int(x);iy=int(y)
  if ix<0 or iy<0 or ix>=MW or iy>=MH:return 1
  return MAP[iy][ix]!=0

#---------- sprite art (original) ----------
def runs(art):
  rows=len(art);cols=len(art[0]);out=[]
  for x in range(cols):
    r=[];y=0
    while y<rows:
      ch=art[y][x]
      if ch=='.':
        y+=1;continue
      y0=y
      while y<rows and art[y][x]==ch:y+=1
      r.append((y0,y-y0,ch))
    out.append(r)
  return (cols,rows,out)
SURGE=runs(["..rr..rr..",
            ".rRRrrRRr.",
            "rRwRRRRwRr",
            "rRRRRRRRRr",
            "RRkkkkkkRR",
            "RkwkwkwkkR",
            "RkkkkkkkkR",
            "RkkwkwkwkR",
            ".RRkkkkRR.",
            "..rRRRRr.."])
SURGEP={'r':0x801010,'R':0xFF3020,'w':0xFFFFFF,'k':0x100000}
ECHOP={'r':0x103080,'R':0x40A0FF,'w':0xFFFFFF,'k':0x000818}
EYE=runs(["..wwww..",
          ".wwwwww.",
          "wwyyyyww",
          "wwykkyww",
          "wwykkyww",
          "wwyyyyww",
          ".wwwwww.",
          "..wwww.."])
EYEP={'w':0xE8E0D0,'y':0x30D0A0,'k':0x000000}
KEYC=runs(["yyyyyy",
           "ykkkky",
           "yyyyyy",
           "ybbyyy"])
KEYP={'y':0xF0C020,'k':0x202020,'b':0x2060FF}
MED=runs(["wwwwww","wwrrww","wrrrrw","wwrrww","wwwwww"])
MEDP={'w':0xEEEEEE,'r':0xDD1111}

class Ent:
  def __init__(s,x,y,k):
    s.x=x;s.y=y;s.k=k   #0 keycard 1 medkit 2 watcher eye
    s.alive=1

#---------- state ----------
class O:
  pass
PL=O();ST={};MON=[None]
OPT=[64];RES=[40,64,80,107]
ZB=[0.0]*160

def newgame():
  gen()
  r0=ROOMS[0]
  PL.x=r0[0]+0.5;PL.y=r0[6]+0.5;PL.a=0.0
  ST.update(hp=100,keys=0,room=0,best=0,hide=0,hidet=0.0,hx=0,hy=0,ha=0,
    warn=0.0,cool=3,msg="",msgt=0.0,light=1.0,hurt=0.0,dead="",win=0,look=0.0,t=0)
  MON[0]=None
  say("ROOM 001  -  "+ZONEN[0])

def say(m,t=2.5):
  ST['msg']=m;ST['msgt']=t

def tryMove(nx,ny):
  r=0.22
  if not (solid(nx-r,PL.y-r) or solid(nx+r,PL.y-r) or solid(nx-r,PL.y+r) or solid(nx+r,PL.y+r)):
    PL.x=nx
  if not (solid(PL.x-r,ny-r) or solid(PL.x+r,ny-r) or solid(PL.x-r,ny+r) or solid(PL.x+r,ny+r)):
    PL.y=ny

def los(x0,y0,x1,y1):
  dx=x1-x0;dy=y1-y0;d=sqrt(dx*dx+dy*dy);n=int(d*3)+1
  for i in range(1,n):
    t=i/n
    if solid(x0+dx*t,y0+dy*t):return 0
  return 1

#---------- rendering ----------
WALLC={2:0x506070,5:0x4A6A5A,6:0x0A2A50,9:0x707A80,10:0x804040,8:0xC0B030}
def cast(N,L):
  px=PL.x;py=PL.y;a=PL.a
  dX=cos(a);dY=sin(a);plX=-dY*0.66;plY=dX*0.66
  cw=SW/N
  FR(0,0,SW,HH,shade(0x101820,L))
  for i in range(5):
    FR(0,HH+i*20,SW,20,shade(0x1C2A2C,(0.3+i*0.17)*L))
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
    while n<30:
      if sdx<sdy:
        sdx+=ddx;mx+=sx;side=0
      else:
        sdy+=ddy;my+=sy;side=1
      if mx<0 or my<0 or mx>=MW or my>=MH:
        w=1;break
      w=MAP[my][mx]
      if w:break
      n+=1
    if n>=30:w=1
    if side==0:
      pd=(mx-px+(1-sx)/2)/rx;wx=py+pd*ry
    else:
      pd=(my-py+(1-sy)/2)/ry;wx=px+pd*rx
    if pd<0.05:pd=0.05
    ZB[i]=pd
    wx-=int(wx)
    h=VH/pd;top=HH-h/2
    f=L*1.2/(1+pd*0.45+pd*pd*0.02)
    if side:f*=0.75
    if w==1:
      c=ZONEC[ZX[mx] if 0<=mx<MW else 0]
    else:
      c=WALLC.get(w,0x506070)
    x0=int(i*cw);x1=int((i+1)*cw);ww=x1-x0
    t=int(top);hh=int(h)
    if t<0:
      hh+=t;t=0
    if t+hh>VH:hh=VH-t
    if w==6:
      #window: frame + deep water + light ray
      FR(x0,t,ww,hh,shade(0x405058,f))
      FR(x0,int(HH-h*0.3),ww,int(h*0.5),0x0A3C6A if (wx>0.15 and wx<0.85) else shade(0x405058,f*0.6))
      if 0.45<wx<0.55:FR(x0,int(HH-h*0.28),ww,int(h*0.12),0x3080B0)
      continue
    if wx<0.05 or wx>0.95:
      FR(x0,t,ww,hh,shade(c,f*0.45));continue
    FR(x0,t,ww,hh,shade(c,f))
    if w==1:
      FR(x0,int(HH+h*0.28),ww,max(1,int(h*0.05)),shade(c,f*0.55))
      FR(x0,int(HH-h*0.38),ww,max(1,int(h*0.03)),shade(0xB0C0C0,f))
    elif w==5:
      #locker: vents
      if 0.2<wx<0.8:
        for v in range(3):
          FR(x0,int(HH-h*0.30+v*h*0.06),ww,max(1,int(h*0.025)),shade(0x101010,f))
        FR(x0,int(HH+h*0.05),ww,int(h*0.04),shade(0xC0C0C0,f)) if 0.6<wx<0.7 else None
    elif w==9 or w==10:
      FR(x0,int(HH-h*0.45),ww,int(h*0.06),0x30FF80 if w==9 else 0xFF3030)
      if 0.48<wx<0.52:FR(x0,t,ww,hh,shade(0x202020,f))
    elif w==8:
      FR(x0,int(HH-h*0.2),ww,int(h*0.4),0x30FFFF if int(ticks()/250)%2 else 0x108080)

def drawSprite(R,pal,sx,depth,scale,lift,N,f):
  cols,rows,cr=R
  h=VH/depth*scale;w=h*cols/rows
  bot=HH+VH/depth*0.5-lift*VH/depth;top=bot-h
  cwid=w/cols;rh=h/rows;x0=sx-w/2;cw=SW/N
  for j in range(cols):
    xa=x0+j*cwid;xb=xa+cwid;xc=(xa+xb)/2
    if xb<0 or xa>=SW:continue
    s=int(xc/cw)
    if s<0 or s>=N or ZB[s]<depth:continue
    for (r0,rl,ch) in cr[j]:
      FR(xa,top+r0*rh,xb-xa+1,rl*rh+1,shade(pal[ch],f))

def project(x,y):
  a=PL.a;dX=cos(a);dY=sin(a);plX=-dY*0.66;plY=dX*0.66
  inv=1/(plX*dY-dX*plY)
  rx=x-PL.x;ry=y-PL.y
  return inv*(dY*rx-dX*ry),inv*(-plY*rx+plX*ry)

def render():
  N=OPT[0];L=ST['light']
  cast(N,L)
  vis=[]
  for e in ENTS:
    tx,ty=project(e.x,e.y)
    if ty>0.2:vis.append((ty,tx,e))
  m=MON[0]
  if m:
    tx,ty=project(m.x,m.y)
    if ty>0.2:vis.append((ty,tx,m))
  vis.sort(key=lambda v:-v[0])
  for ty,tx,e in vis:
    sx=SW/2*(1+tx/ty)
    f=L*1.2/(1+ty*0.45)
    if e is m:
      drawSprite(SURGE,SURGEP if m.k==0 else ECHOP,sx,ty,1.0,0.0,N,1.0)
    elif e.k==0:
      drawSprite(KEYC,KEYP,sx,ty,0.18,0,N,max(0.5,f))
    elif e.k==1:
      drawSprite(MED,MEDP,sx,ty,0.22,0,N,f)
    elif e.k==2:
      drawSprite(EYE,EYEP,sx,ty,0.45,0.35,N,max(0.6,f))
  #hands / flashlight glow
  FR(SW//2-1,HH-3,2,6,0x80A0A0)
  if ST['hurt']>0 or ST['look']>0:
    c=0xC00000
    FR(0,0,SW,5,c);FR(0,VH-5,SW,5,c);FR(0,0,5,VH,c);FR(SW-5,0,5,VH,c)

def hideView():
  m=MON[0]
  near=m and abs(m.x-PL.x)<9
  FR(0,0,SW,VH,0x050505)
  for v in range(5):
    c=0x501010 if (near and rnd()<0.7) else shade(0x203034,ST['light'])
    FR(70,60+v*18,180,6,c)
  FR(60,50,200,2,0x202020);FR(60,150,200,2,0x202020)
  ctext("HIDING...  ACT to leave",166,0xA0C0C0)
  p=min(1.0,ST['hidet']/22.0)
  FR(70,184,120,8,0x202020)
  FR(70,184,int(120*p),8,0x30C0C0 if p<0.6 else (0xE0C020 if p<0.85 else 0xFF2020))
  textout(G,196,181,"PRESSURE",0x80A0A0)

def hud():
  FR(0,VH,SW,40,0x0C1416);FR(0,VH,SW,1,0x30C0C0)
  hp=ST['hp']
  textout(G,6,VH+5,"HEALTH",0x80A0A0)
  FR(6,VH+21,90,9,0x300000)
  FR(6,VH+21,int(90*max(0,hp)/100),9,0x30D0A0 if hp>40 else 0xE03020)
  r=ST['room']+1
  textout(G,110,VH+5,"ROOM",0x80A0A0)
  textout(G,110,VH+20,("00" if r<10 else "0")+str(r)+"/"+str(NR),0xFFFFFF)
  textout(G,178,VH+5,"DEPTH",0x80A0A0)
  textout(G,178,VH+20,str(1500+ST['room']*35)+" m",0x60C0FF)
  if ST['keys']>0:
    FR(250,VH+12,22,15,0xF0C020);FR(253,VH+15,16,3,0x202020)
    textout(G,276,VH+14,"x"+str(ST['keys']),0xF0C020)

#---------- game logic ----------
def act():
  if ST['hide']:
    ST['hide']=0;PL.x=ST['hx'];PL.y=ST['hy'];PL.a=ST['ha'];ST['hidet']=0.0
    return
  a=PL.a
  for d in (0.5,0.9,1.3):
    tx=int(PL.x+cos(a)*d);ty=int(PL.y+sin(a)*d)
    if 0<=tx<MW and 0<=ty<MH:
      v=MAP[ty][tx]
      if v==5:
        ST['hide']=1;ST['hx']=PL.x;ST['hy']=PL.y;ST['ha']=PL.a;ST['hidet']=0.0
        return
      if v==10:
        if ST['keys']>0:
          ST['keys']-=1;MAP[ty][tx]=0;say("KEYCARD ACCEPTED")
        else:
          say("LOCKED - find the keycard in this room")
        return
      if v==8:
        ST['win']=1;return
      if v:return

def autodoors():
  for dy in (-1,0,1):
    for dx in (-1,0,1):
      x=int(PL.x+dx*0.9);y=int(PL.y+dy*0.9)
      if 0<=x<MW and 0<=y<MH and MAP[y][x]==9:
        MAP[y][x]=0
      if 0<=x<MW and 0<=y<MH and MAP[y][x]==10 and ST['keys']>0:
        ST['keys']-=1;MAP[y][x]=0;say("KEYCARD ACCEPTED")

def spawnMonster():
  m=O()
  r=ST['room']
  m.k=1 if (r>=12 and rnd()<0.4) else 0
  m.passes=1 if m.k==0 else 2+rint(2)
  m.dir=1
  m.x=max(-3.0,PL.x-34)
  m.y=PL.y
  m.sp=13.0+r*0.12
  MON[0]=m

def monY(x):
  r=roomAt(x)
  x0,x1,y0,y1,dx,dy,py=ROOMS[r]
  if x<x0:return py+0.5
  if x>x1:return dy+0.5
  return (y0+y1)/2+0.5

def update(dt,fw,bk,lt,rt,sl,sr):
  for k in ('msgt','hurt','look'):
    ST[k]=max(0.0,ST[k]-dt)
  ST['t']+=dt
  m=MON[0]
  #lights
  if ST['warn']>0 or m:
    ST['light']=0.25+0.75*rnd() if rnd()<0.5 else 0.15
  else:
    ST['light']=1.0 if rnd()>0.01 else 0.6
  if ST['hide']:
    ST['hidet']+=dt
    if ST['hidet']>22:
      ST['hp']-=20*dt;ST['hurt']=0.2
      if ST['hp']<=0:ST['dead']="The pressure crushed you in the locker."
  else:
    ts=2.5*dt
    if lt:PL.a-=ts
    if rt:PL.a+=ts
    a=PL.a;sp=2.7*dt;mx=0.0;my=0.0
    if fw:mx+=cos(a);my+=sin(a)
    if bk:mx-=cos(a);my-=sin(a)
    if sl:mx+=sin(a);my-=cos(a)
    if sr:mx-=sin(a);my+=cos(a)
    if mx or my:tryMove(PL.x+mx*sp,PL.y+my*sp)
    autodoors()
  #room progress
  r=roomAt(PL.x)
  if r>ST['room']:
    ST['room']=r
    if r>ST['best']:
      ST['best']=r
      ST['cool']-=1
      z=min(3,r*4//NR);zp=min(3,(r-1)*4//NR)
      n=r+1
      say("ROOM "+("00" if n<10 else "0")+str(n)+("  -  "+ZONEN[z] if z!=zp else ""))
      if r>=3 and ST['cool']<=0 and not m and ST['warn']<=0 and rnd()<0.35:
        ST['warn']=max(3.2,6.0-r*0.07);ST['cool']=3
        say("The lights flicker... HIDE!",ST['warn'])
  elif r<ST['room']:
    ST['room']=r
  #warning -> monster
  if ST['warn']>0:
    ST['warn']-=dt
    if ST['warn']<=0:
      spawnMonster()
  m=MON[0]
  if m:
    ox=m.x
    m.x+=m.dir*m.sp*dt
    m.y=monY(m.x)
    if min(ox,m.x)-0.6<PL.x<max(ox,m.x)+0.6 and not ST['hide'] and not ST['dead']:
      ST['dead']="Caught by "+("the SURGE." if m.k==0 else "the ECHO.")
    if (m.dir>0 and m.x>PL.x+24) or (m.dir<0 and m.x<PL.x-24):
      m.passes-=1
      if m.passes<=0:
        MON[0]=None;say("It's gone... for now.")
      else:
        m.dir=-m.dir;say("It's coming BACK!",1.5)
  #entities
  for e in ENTS:
    dx=e.x-PL.x;dy=e.y-PL.y;d=sqrt(dx*dx+dy*dy)
    if e.k==0 and d<0.6 and not ST['hide']:
      ST['keys']+=1;e.alive=0;say("Picked up a KEYCARD")
    elif e.k==1 and d<0.6 and not ST['hide'] and ST['hp']<100:
      ST['hp']=min(100,ST['hp']+35);e.alive=0;say("+35 HEALTH")
    elif e.k==2 and not ST['hide'] and d<7:
      tx,ty=project(e.x,e.y)
      if ty>0.2 and abs(tx/ty)<0.35 and los(PL.x,PL.y,e.x,e.y):
        ST['hp']-=30*dt;ST['look']=0.15
        if ST['msgt']<=0:say("DON'T LOOK AT IT!",1.0)
        if ST['hp']<=0:ST['dead']="You stared into the WATCHER."
  i=0
  while i<len(ENTS):
    if not ENTS[i].alive:ENTS.pop(i)
    else:i+=1

#---------- screens ----------
def flip():
  strblit(0,0,0,320,240,G)

def screen(title,col,lines):
  FR(0,0,320,240,0x02080C)
  for i in range(10):
    FR(0,240-i*10,320,10,shade(0x0A3C50,(10-i)/14))
  bigtext(title,40,6,col)
  y=110
  for s in lines:
    ctext(s,y,0xD0E8F0);y+=16
  flip()

def waitkey(bits):
  while keyboard() or touches():
    pass
  while True:
    k=keyboard()
    for b in bits:
      if kd(k,b):return b
    if touches():
      while touches():
        pass
      return bits[0]

def title():
  screen("ABYSSAL",0x30D0D0,["Descend 40 rooms of a flooded facility.",
    "Lights flicker = HIDE in a locker!","Don't stare at the eye. Find keycards.",
    "Arrows/8456 move  Space/Enter: ACT",
    "Del: touch buttons on/off  Esc: quit","","Tap or press ENTER"])
  return waitkey([K_ENTER,K_ESC])

def main():
  dimgrob(G,320,240,0)
  if title()==K_ESC:return
  newgame()
  tb=[1]
  last=ticks();prev=0;pact=0
  while True:
    now=ticks();dt=(now-last)/1000.0;last=now
    if dt>0.15:dt=0.15
    if dt<=0:dt=0.01
    k=keyboard();pk=k&~prev;prev=k
    pts=touches() if tb[0] else []
    if kd(k,K_ESC):return
    fw=kd(k,K_UP) or kd(k,K_8) or inside(B_FW,pts)
    bk=kd(k,K_DN) or kd(k,K_5) or inside(B_BK,pts)
    lt=kd(k,K_LT) or inside(B_LT,pts)
    rt=kd(k,K_RT) or inside(B_RT,pts)
    sl=kd(k,K_4);sr=kd(k,K_6)
    ta=inside(B_ACT,pts)
    if kd(pk,K_SPC) or kd(pk,K_ENTER) or (ta and not pact):
      act()
    pact=ta
    if kd(pk,K_DEL):tb[0]=1-tb[0]
    if kd(pk,K_PLUS) or kd(pk,K_MINUS):
      i=RES.index(OPT[0])
      i=min(len(RES)-1,i+1) if kd(pk,K_PLUS) else max(0,i-1)
      OPT[0]=RES[i];say("DETAIL "+str(OPT[0]),1.0)
    update(dt,fw,bk,lt,rt,sl,sr)
    if ST['dead'] or ST['hp']<=0:
      if not ST['dead']:ST['dead']="You died."
      FR(0,0,320,240,0x400000);flip()
      screen("YOU DIED",0xFF3030,[ST['dead'],"Reached room "+str(ST['best']+1)+" of "+str(NR),
        "","ENTER / tap: new dive    ESC: quit"])
      if waitkey([K_ENTER,K_ESC])==K_ESC:return
      newgame();last=ticks();prev=keyboard();continue
    if ST['win']:
      screen("ESCAPED",0x30FFA0,["You reached the escape pod!",
        "Depth "+str(1500+ST['room']*35)+" m   Time "+str(int(ST['t']))+" s",
        "","ENTER / tap: dive again    ESC: quit"])
      if waitkey([K_ENTER,K_ESC])==K_ESC:return
      newgame();last=ticks();prev=keyboard();continue
    if ST['hide']:
      hideView()
    else:
      render()
    if ST['msgt']>0:
      ctext(ST['msg'],24,0xFFFFFF if ST['warn']<=0 else 0xFF6060)
    hud()
    if tb[0]:
      if not ST['hide']:
        tbtn(B_FW,fw,"^");tbtn(B_BK,bk,"v");tbtn(B_LT,lt,"<");tbtn(B_RT,rt,">")
      tbtn(B_ACT,ta,"ACT")
    flip()

main()
