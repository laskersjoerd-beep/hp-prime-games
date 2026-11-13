#STREETZ - a low-poly open-world city game for the HP Prime
#Walk, take any car, do jobs for cash, and shake off the police.
#Python app (hpprime module). Touch buttons + keyboard.
from hpprime import *
from math import *

try:
  ticks()
except:
  def ticks():
    return int(eval("TICKS()"))

_rs=[20261027]
def rnd():
  _rs[0]=(_rs[0]*1103515245+12345)&0x7fffffff
  return _rs[0]/2147483648.0
def rint(n):
  return int(rnd()*n)

G=1;SW=320;SH=240
CX=160;CY=120;F=180.0
PITCH=0.19;CPI=cos(PITCH);SPI=sin(PITCH)
HOR=int(CY-F*tan(PITCH))
NEAR=0.35
SKY=0x9CCBF0;SKY2=0x4E96D8;HAZE=0xC9DDEB
ASPH=0x4C5058

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
def shade(c,f):
  if f>1:f=1
  return (int(((c>>16)&255)*f)<<16)|(int(((c>>8)&255)*f)<<8)|int((c&255)*f)
def mix(c,d,t):
  if t<=0:return c
  if t>1:t=1
  u=1-t
  return (int(((c>>16)&255)*u+((d>>16)&255)*t)<<16)|(int(((c>>8)&255)*u+((d>>8)&255)*t)<<8)|int((c&255)*u+(d&255)*t)
def box2(x,y,w,h,c):
  FR(x,y,w,2,c);FR(x,y+h-2,w,2,c);FR(x,y,2,h,c);FR(x+w-2,y,2,h,c)

FONT={
'A':"0111010001111111000110001",'B':"1111010001111101000111110",
'D':"1111010001100011000111110",'E':"1111110000111101000011111",
'R':"1111010001111101001010001",'S':"0111110000011100000111110",
'T':"1111100100001000010000100",'U':"1000110001100011000101110",
'Z':"1111100010001000100011111",'W':"1000110001101011101110001",
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
  textout(G,(SW-len(s)*7)//2+1,y+1,s,0);textout(G,(SW-len(s)*7)//2,y,s,c)
def otext(x,y,s,c):
  textout(G,x+1,y+1,s,0);textout(G,x,y,s,c)

#---------- input ----------
K_UP=2;K_DN=12;K_LT=7;K_RT=8;K_ESC=4;K_ENTER=30;K_MENU=13;K_DEL=19
K_8=33;K_5=38;K_4=37;K_6=39;K_PLUS=50;K_MINUS=45;K_SPC=49
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
      if f and len(f)>=2 and f[0]>=0 and f[1]>=0:pts.append((f[0],f[1]))
  except:
    pass
  return pts
def inside(b,pts):
  x,y,w,h=b
  for p in pts:
    if x<=p[0]<x+w and y<=p[1]<y+h:return 1
  return 0
BL=(4,184,52,52);BR=(60,184,52,52);BB=(208,184,52,52);BG=(264,184,52,52);BC=(130,196,60,40)
def tbtn(b,on,col):
  x,y,w,h=b
  if on:FR(x,y,w,h,col)
  box2(x,y,w,h,0xFFFFFF)
def drawButtons(l,r,b,g,c,incar):
  tbtn(BL,l,0x3060C0);tbtn(BR,r,0x3060C0);tbtn(BB,b,0xC03030);tbtn(BG,g,0x30A040);tbtn(BC,c,0xC08020)
  x,y,w,h=BL;poly([(x+12,y+26),(x+38,y+11),(x+38,y+41)],0xFFFFFF)
  x,y,w,h=BR;poly([(x+40,y+26),(x+14,y+11),(x+14,y+41)],0xFFFFFF)
  x,y,w,h=BB;poly([(x+26,y+40),(x+42,y+14),(x+10,y+14)],0xFFFFFF)
  x,y,w,h=BG;poly([(x+26,y+10),(x+42,y+38),(x+10,y+38)],0xFFFFFF)
  textout(G,BC[0]+(9 if incar else 12),BC[1]+13,"EXIT" if incar else "CAR",0xFFFFFF)

#---------- city ----------
NB=8;BS=38.0;ROAD=14.0;SP=BS+ROAD;WW=NB*SP+ROAD
RC=[k*SP+ROAD/2 for k in range(NB+1)]
BCOL=[0xC8B8A0,0xA8B4C0,0xD0A080,0x8890A0,0xE0D8C8,0x90A890,0xB09080,0x7C8CA8,0xD8C090]
def gencity():
  global BLK
  BLK=[]
  for j in range(NB):
    row=[]
    for i in range(NB):
      x0=ROAD+i*SP;z0=ROAD+j*SP
      d=sqrt((i-3.5)**2+(j-3.5)**2)
      kind=0
      if (i,j) in ((1,5),(6,2),(4,6)):kind=1   #park
      if (i,j)==(5,5):kind=2                  #spray shop
      b=[]
      if kind==0:
        if rnd()<0.3 and d<2.5:
          h=40+rint(35);b.append((x0+3,z0+3,x0+BS-3,z0+BS-3,h,BCOL[rint(9)]))
        else:
          for a in range(2):
            for c in range(2):
              h=(8+rint(14)) if d>2.5 else (16+rint(34))
              lx=x0+2+a*BS/2;lz=z0+2+c*BS/2
              b.append((lx+1,lz+1,lx+BS/2-3,lz+BS/2-3,h,BCOL[rint(9)]))
      elif kind==2:
        b.append((x0+6,z0+6,x0+BS-6,z0+BS-14,7,0xD040A0))
      trees=[]
      if kind==1:
        for t in range(5):
          trees.append((x0+6+rint(int(BS-12)),z0+6+rint(int(BS-12)),5+rint(4)))
      row.append((x0,z0,kind,b,trees))
    BLK.append(row)

def blockAt(x,z):
  i=int((x-ROAD)/SP);j=int((z-ROAD)/SP)
  if i<0 or j<0 or i>=NB or j>=NB:return None
  bx=x-ROAD-i*SP;bz=z-ROAD-j*SP
  if bx>BS or bz>BS:return None
  return BLK[j][i]

def inBuilding(x,z,r):
  b=blockAt(x,z)
  if not b:return 0
  for (x0,z0,x1,z1,h,c) in b[3]:
    if x0-r<x<x1+r and z0-r<z<z1+r:return 1
  return 0

def collide(o,r):
  #push object out of buildings, returns 1 if hit
  hit=0
  for di in (-r,0,r):
    for dj in (-r,0,r):
      b=blockAt(o.x+di,o.z+dj)
      if not b:continue
      for (x0,z0,x1,z1,h,c) in b[3]:
        if o.x>x0-r and o.x<x1+r and o.z>z0-r and o.z<z1+r:
          dl=o.x-(x0-r);dr=(x1+r)-o.x;dn=o.z-(z0-r);df=(z1+r)-o.z
          m=min(dl,dr,dn,df)
          if m==dl:o.x=x0-r
          elif m==dr:o.x=x1+r
          elif m==dn:o.z=z0-r
          else:o.z=z1+r
          hit=1
  if o.x<1:o.x=1;hit=1
  if o.z<1:o.z=1;hit=1
  if o.x>WW-1:o.x=WW-1;hit=1
  if o.z>WW-1:o.z=WW-1;hit=1
  return hit

#---------- camera / 3D ----------
CAM=[0.0,3.0,0.0,1.0,0.0]
def tf(x,y,z):
  x-=CAM[0];y-=CAM[1];z-=CAM[2]
  c=CAM[3];s=CAM[4]
  x2=x*c-z*s;z2=x*s+z*c
  return (x2,y*CPI+z2*SPI,-y*SPI+z2*CPI)
def poly3(P,c):
  inn=0
  for p in P:
    if p[2]>=NEAR:inn+=1
  if inn==0:return
  if inn<len(P):
    Q=[];n=len(P)
    for i in range(n):
      a=P[i];b=P[(i+1)%n]
      ai=a[2]>=NEAR;bi=b[2]>=NEAR
      if ai:Q.append(a)
      if ai!=bi:
        t=(NEAR-a[2])/(b[2]-a[2])
        Q.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),NEAR))
    P=Q
  pts=[];mnx=9999;mxx=-9999;mny=9999;mxy=-9999
  for p in P:
    sx=CX+F*p[0]/p[2];sy=CY-F*p[1]/p[2]
    if sx<mnx:mnx=sx
    if sx>mxx:mxx=sx
    if sy<mny:mny=sy
    if sy>mxy:mxy=sy
    pts.append((int(sx),int(sy)))
  if mxx<0 or mnx>=SW or mxy<0 or mny>=SH:return
  poly(pts,c)
def fog(c,z):
  return mix(c,HAZE,(z-60)/110.0)

def drawBox(x0,z0,x1,z1,h,col,d,win):
  cx=CAM[0];cy=CAM[1];cz=CAM[2]
  c=fog(col,d)
  if cx<x0:
    poly3([tf(x0,0,z0),tf(x0,0,z1),tf(x0,h,z1),tf(x0,h,z0)],shade(c,0.8))
    if win:wins(x0,z0,x0,z1,h,d,0.8)
  elif cx>x1:
    poly3([tf(x1,0,z1),tf(x1,0,z0),tf(x1,h,z0),tf(x1,h,z1)],shade(c,0.8))
    if win:wins(x1,z1,x1,z0,h,d,0.8)
  if cz<z0:
    poly3([tf(x1,0,z0),tf(x0,0,z0),tf(x0,h,z0),tf(x1,h,z0)],shade(c,0.62))
    if win:wins(x1,z0,x0,z0,h,d,0.62)
  elif cz>z1:
    poly3([tf(x0,0,z1),tf(x1,0,z1),tf(x1,h,z1),tf(x0,h,z1)],shade(c,0.62))
    if win:wins(x0,z1,x1,z1,h,d,0.62)
  if cy>h:
    poly3([tf(x0,h,z0),tf(x1,h,z0),tf(x1,h,z1),tf(x0,h,z1)],shade(c,0.95))

def wins(ax,az,bx,bz,h,d,f):
  #3 vertical window strips on a facade
  wc=fog(shade(0x284868,f+0.1),d)
  for k in range(3):
    t0=0.12+k*0.29;t1=t0+0.17
    x0=ax+(bx-ax)*t0;z0=az+(bz-az)*t0;x1=ax+(bx-ax)*t1;z1=az+(bz-az)*t1
    poly3([tf(x0,2.5,z0),tf(x1,2.5,z1),tf(x1,h-1.5,z1),tf(x0,h-1.5,z0)],wc)

def quad0(x0,z0,x1,z1,y,c):
  poly3([tf(x0,y,z0),tf(x1,y,z0),tf(x1,y,z1),tf(x0,y,z1)],c)

#oriented low-poly boxes (cars, people)
def drawOBoxes(x,y,z,h,boxes):
  fx=sin(h);fz=cos(h);rx=fz;rz=-fx
  cx=CAM[0];cy=CAM[1];cz=CAM[2]
  faces=[]
  for (x0,x1,y0,y1,f0,f1,col) in boxes:
    cand=((0,1,0,((x0,y1,f0),(x1,y1,f0),(x1,y1,f1),(x0,y1,f1)),1.0),
          (-fx,0,-fz,((x0,y0,f0),(x1,y0,f0),(x1,y1,f0),(x0,y1,f0)),0.62),
          (fx,0,fz,((x0,y0,f1),(x1,y0,f1),(x1,y1,f1),(x0,y1,f1)),0.85),
          (-rx,0,-rz,((x0,y0,f0),(x0,y0,f1),(x0,y1,f1),(x0,y1,f0)),0.74),
          (rx,0,rz,((x1,y0,f0),(x1,y0,f1),(x1,y1,f1),(x1,y1,f0)),0.74))
    for nx,ny,nz,cs,sh in cand:
      mx=x+rx*(cs[0][0]+cs[2][0])/2+fx*(cs[0][2]+cs[2][2])/2
      my=y+(cs[0][1]+cs[2][1])/2
      mz=z+rz*(cs[0][0]+cs[2][0])/2+fz*(cs[0][2]+cs[2][2])/2
      if nx*(cx-mx)+ny*(cy-my)+nz*(cz-mz)<=0:continue
      P=[tf(x+rx*a+fx*f,y+u,z+rz*a+fz*f) for (a,u,f) in cs]
      faces.append(((P[0][2]+P[2][2])/2,P,shade(col,sh)))
  faces.sort(key=lambda q:-q[0])
  for d,P,c in faces:
    poly3(P,c)

def carBoxes(col,pol,t):
  b=[(-0.85,0.85,0.0,0.35,-1.8,1.8,0x181818),
     (-0.95,0.95,0.3,0.95,-2.1,2.1,col),
     (-0.8,0.8,0.95,1.5,-1.1,0.8,0x203040)]
  if pol:
    b.append((-0.6,0.6,1.5,1.7,-0.3,0.3,0xFF2020 if int(t*6)%2 else 0x2040FF))
  return b
def manBoxes(col,ph):
  s=sin(ph)*0.35
  return [(-0.28,-0.04,0.0,0.85,-0.12+s,0.12+s,0x283850),(0.04,0.28,0.0,0.85,-0.12-s,0.12-s,0x283850),
          (-0.32,0.32,0.85,1.5,-0.18,0.18,col),(-0.15,0.15,1.5,1.82,-0.15,0.15,0xE0B090)]

#---------- vehicles ----------
HDIR=[pi/2,0.0,-pi/2,pi]
DV=[(1,0),(0,1),(-1,0),(0,-1)]
RV=[(0,-1),(1,0),(0,1),(-1,0)]
LANE=3.3
CARCOL=[0xE53935,0x1E88E5,0xFDD835,0x43A047,0xF4F4F4,0x222222,0xFB8C00,0x8E24AA]
class Car:
  pass
def newTraffic(pol=0,near=None):
  c=Car()
  c.pol=pol;c.col=0xF0F0F0 if pol else CARCOL[rint(8)]
  c.mode=0;c.v=0.0;c.hit=0.0
  placeOnLane(c,near)
  return c
def placeOnLane(c,near=None,mind=55):
  for t in range(30):
    if near:
      sp=2 if mind<80 else 3
      k=int((near[0]-ROAD/2)/SP)+rint(2*sp+1)-sp;j=int((near[1]-ROAD/2)/SP)+rint(2*sp+1)-sp
    else:
      k=rint(NB+1);j=rint(NB+1)
    k=max(0,min(NB,k));j=max(0,min(NB,j))
    d=rint(4)
    if near is None or (abs(RC[k]-near[0])+abs(RC[j]-near[1])>mind):break
  c.d=d;dx,dz=DV[d];rx,rz=RV[d]
  c.x=RC[k]+rx*LANE+dx*SP*0.5;c.z=RC[j]+rz*LANE+dz*SP*0.5
  c.x=max(2,min(WW-2,c.x));c.z=max(2,min(WW-2,c.z))
  c.h=HDIR[d];c.v=9.0+rnd()*3
  nextTarget(c)

def nextTarget(c,chase=None):
  d=c.d;dx,dz=DV[d];rx,rz=RV[d]
  #centre line coordinates of current road
  if dx!=0:
    j=int(round((c.z-rz*LANE-ROAD/2)/SP));j=max(0,min(NB,j))
    k=int(floor((c.x-ROAD/2)/SP))+(1 if dx>0 else 0)
    if dx>0 and RC[max(0,min(NB,k))]<=c.x+0.01:k+=1
    if dx<0 and RC[max(0,min(NB,k))]>=c.x-0.01:k-=1
    k=max(0,min(NB,k))
  else:
    k=int(round((c.x-rx*LANE-ROAD/2)/SP));k=max(0,min(NB,k))
    j=int(floor((c.z-ROAD/2)/SP))+(1 if dz>0 else 0)
    if dz>0 and RC[max(0,min(NB,j))]<=c.z+0.01:j+=1
    if dz<0 and RC[max(0,min(NB,j))]>=c.z-0.01:j-=1
    j=max(0,min(NB,j))
  opts=[]
  for d2 in (d,(d+1)%4,(d+3)%4):
    ex,ez=DV[d2];kk=k+ex;jj=j+ez
    if 0<=kk<=NB and 0<=jj<=NB:opts.append(d2)
  if not opts:opts=[(d+2)%4]
  if chase:
    best=None
    for d2 in opts:
      ex,ez=DV[d2]
      dd=(RC[k]+ex*SP-chase[0])**2+(RC[j]+ez*SP-chase[1])**2
      if best is None or dd<best[0]:best=(dd,d2)
    d2=best[1]
  else:
    d2=opts[rint(len(opts))]
    if d in opts and rnd()<0.5:d2=d
  r2=RV[d2]
  if d2==d:
    c.tx=RC[k]+rx*LANE;c.tz=RC[j]+rz*LANE
  elif d2==(d+2)%4:
    c.tx=RC[k]+rx*LANE;c.tz=RC[j]+rz*LANE
  else:
    c.tx=RC[k]+rx*LANE+r2[0]*LANE;c.tz=RC[j]+rz*LANE+r2[1]*LANE
  c.td=d2

def laneDrive(c,dt,chase=None):
  dx,dz=DV[c.d]
  step=c.v*dt
  rem=(c.tx-c.x)*dx+(c.tz-c.z)*dz
  if rem<=step:
    c.x=c.tx;c.z=c.tz
    if c.td==(c.d+2)%4:
      #dead end: U-turn into the other lane
      rx,rz=RV[c.d];c.x-=rx*LANE*2;c.z-=rz*LANE*2
    c.d=c.td;c.h=HDIR[c.d]
    nextTarget(c,chase)
  else:
    c.x+=dx*step;c.z+=dz*step
    c.h=HDIR[c.d]

def snapLane(c,px,pz):
  #put a car back onto the nearest lane, heading towards the player
  k=int(round((c.x-ROAD/2)/SP));j=int(round((c.z-ROAD/2)/SP))
  k=max(0,min(NB,k));j=max(0,min(NB,j))
  if abs(c.x-RC[k])<abs(c.z-RC[j]):
    d=1 if pz>c.z else 3;rx,rz=RV[d];c.x=RC[k]+rx*LANE
  else:
    d=0 if px>c.x else 2;rx,rz=RV[d];c.z=RC[j]+rz*LANE
  c.d=d;c.h=HDIR[d]
  nextTarget(c,(px,pz))

#---------- state ----------
class O:
  pass
PL=O();ST={};TRAF=[];PARK=[];COPS=[]
VIEW=[95.0];VIEWS=[70.0,95.0,120.0,150.0]

def say(m,t=3.0):
  ST['msg']=m;ST['msgt']=t

def newgame():
  _rs[0]=20261027
  gencity()
  TRAF[:]=[];PARK[:]=[];COPS[:]=[]
  PL.x=RC[2]+5.5;PL.z=RC[3]+20;PL.h=0.0;PL.v=0.0;PL.car=None;PL.ph=0.0;PL.cy=0.0
  for i in range(9):TRAF.append(newTraffic(0,(PL.x,PL.z)))
  TRAF.append(newTraffic(1,(PL.x,PL.z)))
  for i in range(8):
    c=Car();c.pol=0;c.col=CARCOL[rint(8)];c.mode=1;c.v=0.0;c.hit=0.0
    k=rint(NB+1);j=rint(NB)
    c.x=RC[k]+6.0;c.z=RC[j]+SP*0.5+rnd()*10;c.h=0.0
    PARK.append(c)
  #one parked car right next to you
  c=Car();c.pol=0;c.col=0xE53935;c.mode=1;c.v=0.0;c.hit=0.0
  c.x=PL.x+0.5;c.z=PL.z+3.6;c.h=0.0;PARK.append(c)
  ST.update(cash=ST.get('cash',100),want=0,wt=0.0,lose=0.0,bust=0.0,msg="",msgt=0.0,
    job=None,jx=0,jz=0,t=0.0,map=1,btn=1)
  newJobSpot()
  CAM[0]=PL.x;CAM[2]=PL.z-6;CAM[1]=2.5
  say("Grab a car! Yellow marker = job",4)

def newJobSpot():
  k=rint(NB+1);j=rint(NB+1)
  ST['jx']=RC[k]+(rnd()-0.5)*6;ST['jz']=RC[j]+(rnd()-0.5)*6
  ST['job']=None

SPRAY=(ROAD+5*SP+BS/2,ROAD+5*SP+BS-6)

def addWant(n,why=""):
  w=min(3,ST['want']+n)
  if w>ST['want']:
    ST['want']=w;ST['lose']=0.0
    say(why+("  " if why else "")+"WANTED "+"*"*w,2.5)

def copsNear(r):
  for c in COPS+TRAF:
    if c.pol and (c.x-PL.x)**2+(c.z-PL.z)**2<r*r:return 1
  return 0

def enterExit():
  if PL.car:
    c=PL.car;c.mode=1;c.v=0.0
    PARK.append(c)
    PL.x=c.x-cos(c.h)*2.2;PL.z=c.z+sin(c.h)*2.2;PL.h=c.h
    collide(PL,0.4)
    PL.car=None;PL.v=0.0
    return
  best=None
  for lst in (PARK,TRAF):
    for c in lst:
      d=(c.x-PL.x)**2+(c.z-PL.z)**2
      if d<16 and (best is None or d<best[0]):best=(d,c,lst)
  if not best:
    say("No car nearby",1.5);return
  d,c,lst=best
  lst.remove(c)
  if lst is TRAF:
    if c.pol:
      addWant(2,"You took a police car!")
    elif copsNear(70) or rnd()<0.25:
      addWant(1,"Carjacking reported!")
    else:
      say("Car taken",1.5)
    TRAF.append(newTraffic(0,(PL.x,PL.z)))
  c.mode=2
  PL.car=c;PL.x=c.x;PL.z=c.z;PL.h=c.h;PL.v=c.v*0.5

def physics(dt,gas,brk,st):
  if PL.car:
    v=PL.v;vmax=31.0
    if gas:
      v+=(14*dt*max(0.0,1-v/vmax)) if v>=0 else 28*dt
    if brk:
      v-=(26 if v>0 else 8)*dt
      if v<-8:v=-8.0
    if not gas and not brk:v-=v*0.6*dt
    PL.v=v;sp=abs(v)
    rate=st*2.1*min(1.0,sp/5.0)/(1+sp/30.0)
    if v<0:rate=-rate
    PL.h+=rate*dt
    PL.x+=sin(PL.h)*v*dt;PL.z+=cos(PL.h)*v*dt
    if collide(PL,1.3):
      if abs(PL.v)>10:say("CRASH!",0.8)
      PL.v*=-0.25
    c=PL.car;c.x=PL.x;c.z=PL.z;c.h=PL.h;c.v=PL.v
  else:
    PL.h+=st*2.8*dt
    v=(5.5 if gas else 0.0)-(3.0 if brk else 0.0)
    PL.v=v
    PL.x+=sin(PL.h)*v*dt;PL.z+=cos(PL.h)*v*dt
    collide(PL,0.45)
    if v:PL.ph+=dt*10

def updateAI(dt):
  px=PL.x;pz=PL.z
  pr=1.3 if PL.car else 0.6
  for c in TRAF:
    #brake for whatever is right ahead
    fx=sin(c.h);fz=cos(c.h)
    ax=px-c.x;az=pz-c.z;ahead=ax*fx+az*fz;side=abs(ax*fz-az*fx)
    tv=11.0
    if 0<ahead<9 and side<2.5:tv=0.0
    c.v+=(tv-c.v)*min(1.0,dt*3)
    laneDrive(c,dt)
    if (c.x-px)**2+(c.z-pz)**2>160*160:
      placeOnLane(c,(px,pz))
  #police chase
  w=ST['want']
  if w>0:
    #patrol cars join the chase
    for c in TRAF[:]:
      if c.pol:
        TRAF.remove(c);c.mode=3;COPS.append(c)
    while len(COPS)<w:
      c=newTraffic(1,(px,pz));placeOnLane(c,(px,pz),100);c.mode=3;COPS.append(c)
  for c in COPS[:]:
    d2=(c.x-px)**2+(c.z-pz)**2
    if w==0:
      if d2>90*90:
        COPS.remove(c)
        if not any(t.pol for t in TRAF):c.mode=0;TRAF.append(c)
      else:
        c.v+=(10-c.v)*min(1.0,dt*2);laneDrive(c,dt)
      continue
    if d2<26*26:
      #direct pursuit
      if c.mode!=4:c.mode=4
      want=atan2(px-c.x,pz-c.z)
      dd=want-c.h
      while dd>pi:dd-=2*pi
      while dd<-pi:dd+=2*pi
      c.h+=max(-2.2*dt,min(2.2*dt,dd*3*dt))
      tv=21.0 if d2>36 else 3.0
      c.v+=(tv-c.v)*min(1.0,dt*2)
      c.x+=sin(c.h)*c.v*dt;c.z+=cos(c.h)*c.v*dt
      if collide(c,1.3):c.v*=0.3
    else:
      if c.mode==4:
        snapLane(c,px,pz);c.mode=3
      c.v+=(24.0-c.v)*min(1.0,dt*2)
      laneDrive(c,dt,(px,pz))
    if d2>170*170:
      placeOnLane(c,(px,pz),125);c.mode=3
  #collisions between you and other cars
  for lst in (TRAF,COPS,PARK):
    for c in lst:
      dx=c.x-px;dz=c.z-pz;d2=dx*dx+dz*dz
      lim=(pr+1.3)**2
      if d2<lim and d2>0.0001:
        d=sqrt(d2);push=(pr+1.3-d)
        if PL.car:
          PL.x-=dx/d*push*0.6;PL.z-=dz/d*push*0.6
          c.x+=dx/d*push*0.4;c.z+=dz/d*push*0.4
          if abs(PL.v)>8 and ST['t']-c.hit>2:
            c.hit=ST['t']
            if c.pol:addWant(1,"You rammed a cop!")
            elif copsNear(45):addWant(1,"Reckless driving!")
          PL.v*=0.5
          PL.car.x=PL.x;PL.car.z=PL.z
        else:
          PL.x-=dx/d*push;PL.z-=dz/d*push

def updateWanted(dt):
  w=ST['want']
  if w==0:
    ST['bust']=0.0;return
  near=0;close=0
  for c in COPS:
    d2=(c.x-PL.x)**2+(c.z-PL.z)**2
    if d2<85*85:near=1
    if d2<5.5*5.5:close=1
  if near:ST['lose']=0.0
  else:
    ST['lose']+=dt
    if ST['lose']>9:
      ST['want']-=1;ST['lose']=0.0
      say("Lost them!" if ST['want']==0 else "WANTED "+"*"*ST['want'],2)
  if close and abs(PL.v)<1.8:
    ST['bust']+=dt
  else:
    ST['bust']=max(0.0,ST['bust']-dt)
  if ST['bust']>2.8:
    busted()
  #spray shop
  if PL.car and (PL.x-SPRAY[0])**2+(PL.z-SPRAY[1])**2<36:
    if ST['cash']>=50:
      ST['cash']-=50;ST['want']=0;ST['lose']=0
      PL.car.col=CARCOL[rint(8)];say("Resprayed! Stars cleared (-$50)",3)

def busted():
  ST['cash']=max(0,ST['cash']-100)
  ST['want']=0;ST['bust']=0.0
  if PL.car:
    PL.car=None
  PL.x=RC[4]+5.5;PL.z=RC[4]-12;PL.v=0.0;PL.h=0.0
  for c in COPS:c.mode=3
  ST['job']=None;newJobSpot()
  ST['bustscreen']=1

def updateJob(dt):
  j=ST['job']
  if j is None:
    if (PL.x-ST['jx'])**2+(PL.z-ST['jz'])**2<25:
      #start a job
      kind=rint(2)
      for t in range(30):
        k=rint(NB+1);jj=rint(NB+1)
        dx=RC[k]-PL.x;dz=RC[jj]-PL.z
        if dx*dx+dz*dz>150*150:break
      dist=sqrt(dx*dx+dz*dz)
      J=O();J.kind=kind;J.x=RC[k]+2;J.z=RC[jj]+2
      J.time=int(dist/10.0+(25 if PL.car else 45))
      J.pay=int(dist*2.2)//10*10+(150 if kind else 50)
      ST['job']=J
      if kind==0:
        say("DELIVERY: drive to the green marker!",3)
      else:
        say("GETAWAY: reach green + lose the cops!",3)
        addWant(2)
    return
  j.time-=dt
  if j.time<=0:
    say("Job failed - out of time",3);newJobSpot();return
  if (PL.x-j.x)**2+(PL.z-j.z)**2<30:
    if j.kind==1 and ST['want']>0:
      if ST['msgt']<=0:say("Lose the cops first!",1.0)
      return
    ST['cash']+=j.pay;say("JOB DONE!  +$"+str(j.pay),3)
    newJobSpot()

def camera(dt):
  incar=PL.car is not None
  d=PL.h-PL.cy
  while d>pi:d-=2*pi
  while d<-pi:d+=2*pi
  PL.cy+=d*min(1.0,dt*(4.0 if incar else 6.0))
  dist=7.5 if incar else 4.2;hh=3.2 if incar else 2.3
  #pull the camera in front of any wall between it and the player
  sd=dist
  for i in range(1,8):
    dd=dist*i/7.0
    if inBuilding(PL.x-sin(PL.cy)*dd,PL.z-cos(PL.cy)*dd,0.6):
      sd=max(1.2,dd-0.9);break
  tx=PL.x-sin(PL.cy)*sd;tz=PL.z-cos(PL.cy)*sd
  k=min(1.0,dt*8)
  if sd<dist:k=1.0
  hh+=(dist-sd)*0.5
  CAM[0]+=(tx-CAM[0])*k;CAM[2]+=(tz-CAM[2])*k;CAM[1]+=(hh-CAM[1])*min(1.0,dt*6)
  CAM[3]=cos(PL.cy);CAM[4]=sin(PL.cy)

#---------- render ----------
def background():
  for i in range(4):
    FR(0,i*HOR//4,SW,HOR//4+1,mix(SKY2,SKY,i/3.0))
  FR(0,HOR-5,SW,6,HAZE)
  FR(0,HOR,SW,SH-HOR,ASPH)
  FR(0,HOR,SW,4,mix(ASPH,HAZE,0.6))

def marker(x,z,col,t,d):
  h=18+2*sin(t*4)
  c=fog(col,d)
  sx=CAM[3];sz=-CAM[4]
  poly3([tf(x-sx*0.9,0,z-sz*0.9),tf(x+sx*0.9,0,z+sz*0.9),tf(x+sx*0.9,h,z+sz*0.9),tf(x-sx*0.9,h,z-sz*0.9)],c)
  quad0(x-2.5,z-2.5,x+2.5,z+2.5,0.05,shade(c,0.7))

def render(t):
  background()
  cxw=CAM[0];czw=CAM[2];V=VIEW[0]
  items=[]
  #blocks in range
  rng=int(V/SP)+1
  bi=int((cxw-ROAD)/SP);bj=int((czw-ROAD)/SP)
  foot=[]
  for j in range(max(0,bj-rng),min(NB,bj+rng+1)):
    for i in range(max(0,bi-rng),min(NB,bi+rng+1)):
      B=BLK[j][i];x0,z0=B[0],B[1]
      c=tf(x0+BS/2,0,z0+BS/2)
      if c[2]<-BS*0.75 or c[2]>V+BS:continue
      if abs(c[0])>c[2]*0.95+BS:continue
      foot.append((c[2],B))
      for (a0,b0,a1,b1,h,col) in B[3]:
        cc=tf((a0+a1)/2,0,(b0+b1)/2)
        items.append((cc[2],0,(a0,b0,a1,b1,h,col)))
      for tr in B[4]:
        cc=tf(tr[0],0,tr[1])
        if cc[2]>0.5:items.append((cc[2],1,tr))
  foot.sort(key=lambda q:-q[0])
  for d,B in foot:
    x0,z0=B[0],B[1]
    col=0x5E9E48 if B[2]==1 else (0xA060A0 if B[2]==2 else 0x9A9A9A)
    quad0(x0-1.5,z0-1.5,x0+BS+1.5,z0+BS+1.5,0.04,fog(col,d))
  #road centre dashes near the camera
  for k in range(NB+1):
    if abs(RC[k]-cxw)<40:
      for s in range(-5,6):
        zz=round((czw)/8)*8+s*8
        quad0(RC[k]-0.15,zz,RC[k]+0.15,zz+3,0.05,0xE8D060)
    if abs(RC[k]-czw)<40:
      for s in range(-5,6):
        xx=round((cxw)/8)*8+s*8
        quad0(xx,RC[k]-0.15,xx+3,RC[k]+0.15,0.05,0xE8D060)
  #cars, people, markers
  for lst in (TRAF,COPS,PARK):
    for c in lst:
      cc=tf(c.x,0,c.z)
      if cc[2]>0.5 and cc[2]<V and abs(cc[0])<cc[2]+5:items.append((cc[2],2,c))
  if PL.car:
    cc=tf(PL.x,0,PL.z);items.append((cc[2],2,PL.car))
  else:
    cc=tf(PL.x,0,PL.z);items.append((cc[2],3,None))
  j=ST['job']
  mk=[(j.x,j.z,0x30E060)] if j else [(ST['jx'],ST['jz'],0xFFD020)]
  if ST['want']>0:mk.append((SPRAY[0],SPRAY[1],0xFF40C0))
  for (x,z,col) in mk:
    cc=tf(x,0,z)
    if cc[2]>1 and cc[2]<V+60:items.append((cc[2],4,(x,z,col)))
  items.sort(key=lambda q:-q[0])
  for d,ty,o in items:
    if ty==0:
      a0,b0,a1,b1,h,col=o
      drawBox(a0,b0,a1,b1,h,col,d,d<55 and h>10)
    elif ty==1:
      x,z,h=o
      drawOBoxes(x,0,z,0.0,[(-0.3,0.3,0,2.0,-0.3,0.3,0x6D4C33),(-1.5,1.5,2.0,h,-1.5,1.5,fog(0x3E8E3E,d))])
    elif ty==2:
      drawOBoxes(o.x,0,o.z,o.h,carBoxes(fog(o.col,d),o.pol and (o.mode>=3),t))
    elif ty==3:
      drawOBoxes(PL.x,0,PL.z,PL.h,manBoxes(0x2E7D32,PL.ph))
    else:
      marker(o[0],o[1],o[2],t,d)

def radar():
  ox=4;oy=4;S=68;R=140.0
  FR(ox-2,oy-2,S+4,S+4,0x101418);FR(ox,oy,S,S,0x2A3A2A)
  sc=S/(2*R)
  def P(x,z):
    return (ox+S/2+(x-PL.x)*sc,oy+S/2-(z-PL.z)*sc)
  for k in range(NB+1):
    sx,sy=P(RC[k],PL.z)
    if ox<=sx<ox+S:FR(int(sx),oy,1,S,0x909090)
    sx,sy=P(PL.x,RC[k])
    if oy<=sy<oy+S:FR(ox,int(sy),S,1,0x909090)
  def dot(x,z,c,s):
    sx,sy=P(x,z)
    sx=max(ox+2,min(ox+S-3,sx));sy=max(oy+2,min(oy+S-3,sy))
    FR(int(sx)-s//2,int(sy)-s//2,s,s,c)
  j=ST['job']
  if j:dot(j.x,j.z,0x30E060,5)
  else:dot(ST['jx'],ST['jz'],0xFFD020,5)
  if ST['want']>0:dot(SPRAY[0],SPRAY[1],0xFF40C0,4)
  for c in COPS:
    dot(c.x,c.z,0xFF2020 if int(ST['t']*5)%2 else 0x2040FF,3)
  cx=ox+S/2;cy=oy+S/2;a=PL.h
  poly([(int(cx+sin(a)*6),int(cy-cos(a)*6)),(int(cx+sin(a+2.5)*4),int(cy-cos(a+2.5)*4)),
        (int(cx+sin(a-2.5)*4),int(cy-cos(a-2.5)*4))],0xFFFFFF)

def hud(ctl):
  if ST['map']:radar()
  otext(240,4,"$"+str(ST['cash']),0x60FF60)
  for i in range(3):
    c=0xFFFFFF if i<ST['want'] else 0x404040
    x=244+i*24;y=22
    poly([(x+8,y),(x+10,y+6),(x+16,y+6),(x+11,y+10),(x+13,y+16),(x+8,y+12),(x+3,y+16),(x+5,y+10),(x,y+6),(x+6,y+6)],c)
  if PL.car:otext(250,42,str(int(abs(PL.v)*3.6))+" km/h",0xFFFFFF)
  j=ST['job']
  if j:
    otext(80,4,("DELIVERY" if j.kind==0 else "GETAWAY")+"  "+str(int(j.time))+"s  $"+str(j.pay),0x30FF60)
    #direction arrow
    a=atan2(j.x-PL.x,j.z-PL.z)-PL.cy
    cx=160;cy=30
    poly([(int(cx+sin(a)*12),int(cy-cos(a)*12)),(int(cx+sin(a+2.4)*8),int(cy-cos(a+2.4)*8)),
          (int(cx+sin(a-2.4)*8),int(cy-cos(a-2.4)*8))],0x30FF60)
  if ST['bust']>0.3:
    ctext("POLICE: STOP!  (move to escape)",60,0xFF6060)
  if ST['msgt']>0:
    ctext(ST['msg'],76,0xFFFFFF)
  if ST['btn']:
    drawButtons(ctl[0],ctl[1],ctl[2],ctl[3],ctl[4],PL.car is not None)

def flip():
  strblit(0,0,0,SW,SH,G)

def title():
  newgame()
  PL.cy=0.6;CAM[0]=PL.x-14;CAM[2]=PL.z-16;CAM[1]=6;CAM[3]=cos(0.6);CAM[4]=sin(0.6)
  render(0.0)
  FR(0,34,SW,84,0x101820)
  bigtext("STREETZ",42,6,0xFFB020,0x000000)
  textout(G,48,82,"low-poly open city  -  cars, jobs, cops",0xFFFFFF)
  textout(G,48,100,"Tap the screen or press ENTER to play",0xC0E0FF)
  FR(0,140,SW,100,0x101820)
  textout(G,10,146,"Touch: < > steer/turn, GAS/BRAKE, CAR = get in/out",0xE0E0E0)
  textout(G,10,162,"Keys: arrows/8456 drive+walk, Enter: get in/out",0xE0E0E0)
  textout(G,10,178,"Menu: radar   Del: touch buttons   +/-: view dist",0xE0E0E0)
  textout(G,10,194,"Yellow = job, green = drop-off, pink = respray",0xE0E0E0)
  textout(G,10,210,"Too many stars? Lose the cops or hit the pink shop",0xE0E0E0)
  textout(G,10,224,"Esc: quit",0xE0E0E0)
  flip()
  while keyboard() or touches():
    pass
  while True:
    k=keyboard()
    if kd(k,K_ESC):return 0
    if kd(k,K_ENTER) or kd(k,K_SPC):return 1
    if touches():
      while touches():
        pass
      return 1

def main():
  dimgrob(G,SW,SH,0)
  loadCash()
  if not title():return
  newgame()
  last=ticks();prevk=keyboard();prevc=0
  while True:
    now=ticks();dt=(now-last)/1000.0;last=now
    if dt>0.2:dt=0.2
    if dt<=0:dt=0.01
    ST['t']+=dt
    k=keyboard();pk=k&~prevk;prevk=k
    pts=touches() if ST['btn'] else []
    if kd(k,K_ESC):
      saveCash();return
    gas=kd(k,K_UP) or kd(k,K_8) or inside(BG,pts)
    brk=kd(k,K_DN) or kd(k,K_5) or inside(BB,pts)
    lt=kd(k,K_LT) or kd(k,K_4) or inside(BL,pts)
    rt=kd(k,K_RT) or kd(k,K_6) or inside(BR,pts)
    cb=inside(BC,pts)
    st=(1 if rt else 0)-(1 if lt else 0)
    if kd(pk,K_ENTER) or (cb and not prevc):enterExit()
    prevc=cb
    if kd(pk,K_MENU):ST['map']=1-ST['map']
    if kd(pk,K_DEL):ST['btn']=1-ST['btn']
    if kd(pk,K_PLUS) or kd(pk,K_MINUS):
      i=VIEWS.index(VIEW[0])
      i=min(len(VIEWS)-1,i+1) if kd(pk,K_PLUS) else max(0,i-1)
      VIEW[0]=VIEWS[i];say("VIEW DISTANCE "+str(int(VIEW[0]))+" m",1.2)
    n=int(dt/0.05)+1
    for s in range(n):
      physics(dt/n,gas,brk,st)
      updateAI(dt/n)
    updateWanted(dt)
    if ST.get('bustscreen'):
      ST['bustscreen']=0
      FR(0,80,SW,70,0x000000);bigtext("BUSTED",88,5,0xFF4040)
      ctext("-$100   Tap / Enter to continue",126,0xFFFFFF);flip()
      while keyboard() or touches():
        pass
      while not (kd(keyboard(),K_ENTER) or touches()):
        pass
      while touches():
        pass
      last=ticks();prevk=keyboard();continue
    updateJob(dt)
    ST['msgt']=max(0.0,ST['msgt']-dt)
    camera(dt)
    render(ST['t'])
    hud((lt,rt,brk,gas,cb))
    flip()

def loadCash():
  try:
    f=open("streetz.txt","r");ST['cash']=int(f.read());f.close()
  except:
    ST['cash']=100
def saveCash():
  try:
    f=open("streetz.txt","w");f.write(str(ST['cash']));f.close()
  except:
    pass

main()
