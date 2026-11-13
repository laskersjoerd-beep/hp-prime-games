#LAPRUSH 2 - low-poly stunt racer for the HP Prime
#Loops, wall-rides, magnetic ceilings, jumps. Touch buttons + keyboard.
#Python app (hpprime module).
from hpprime import *
from math import *

try:
  ticks()
except:
  def ticks():
    return int(eval("TICKS()"))

G=1
SW=320;SH=240
CX=160;CY=120;F=190.0
NEAR=0.4
SKY=0x8EC9F5;SKY2=0x5AA8E8;HAZE=0xC8E2F4
GRAV=16.0
VTOP=52.0      #top speed on gas alone (~187 km/h)
VBOOST=100.0   #boost strips push you up to ~360 km/h
XR=[CX/F,CY/F]

#---------- compact storage (the calculator has little memory) ----------
try:
  from array import array
except:
  try:
    from uarray import array
  except:
    array=None
import gc

class V3:
  #3D points/vectors packed into ONE preallocated float array (no growing
  #-> no memory fragmentation on the calculator)
  def __init__(s,cap):
    s.a=array('f',bytes(12*cap)) if array else [0.0]*(3*cap);s.n=0
  def append(s,v):
    j=3*s.n;a=s.a
    if j>=len(a):
      a.append(0.0);a.append(0.0);a.append(0.0)
    a[j]=v[0];a[j+1]=v[1];a[j+2]=v[2];s.n+=1
  def __getitem__(s,i):
    if i<0:i+=s.n
    a=s.a;j=3*i
    return (a[j],a[j+1],a[j+2])
  def __len__(s):
    return s.n
  def __iter__(s):
    a=s.a
    for j in range(0,3*s.n,3):
      yield (a[j],a[j+1],a[j+2])

class P6:
  #six 3D points per track vertex (road edges, kerbs, underside)
  def __init__(s,cap):
    s.a=array('f',bytes(72*cap)) if array else [0.0]*(18*cap);s.n=0
  def append(s,pts):
    a=s.a;j=18*s.n
    for q in pts:
      a[j]=q[0];a[j+1]=q[1];a[j+2]=q[2];j+=3
    s.n+=1
  def __getitem__(s,i):
    a=s.a;j=18*i
    return ((a[j],a[j+1],a[j+2]),(a[j+3],a[j+4],a[j+5]),(a[j+6],a[j+7],a[j+8]),
            (a[j+9],a[j+10],a[j+11]),(a[j+12],a[j+13],a[j+14]),(a[j+15],a[j+16],a[j+17]))

class F1:
  #one small number per vertex (flags) in a preallocated byte array
  def __init__(s,cap):
    s.a=bytearray(cap);s.n=0
  def append(s,v):
    if s.n>=len(s.a):s.a.append(0)
    s.a[s.n]=v;s.n+=1
  def __getitem__(s,i):
    return s.a[i]
  def __len__(s):
    return s.n

class FA:
  #one float per vertex in a preallocated array
  def __init__(s,cap):
    s.a=array('f',bytes(4*cap)) if array else [0.0]*cap;s.n=0
  def append(s,v):
    if s.n>=len(s.a):s.a.append(0.0)
    s.a[s.n]=v;s.n+=1
  def __getitem__(s,i):
    return s.a[i]
  def __len__(s):
    return s.n

def countVerts(stunt,data):
  #how many vertices a track will have (so we can allocate once)
  if not stunt:
    n=0;P=data;m=len(P)
    for i in range(m):
      b=P[i];c=P[(i+1)%m]
      n+=max(2,int(sqrt((c[0]-b[0])**2+(c[1]-b[1])**2)/6))
    return n
  n=1
  for pc in data:
    k=pc[0]
    if k=='C':continue
    if k=='G':n+=1;continue
    if k=='B':pc=('X',pc[1],0,0,0)
    st=8.0 if (pc[2]==0 and pc[3]==0 and pc[4]==0 and not (len(pc)>5 and pc[5])) else 4.0
    n+=max(1,int(pc[1]/st+0.5))
  return n+1

#---------- vectors ----------
def vadd(a,b):return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def vsub(a,b):return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def vmul(a,s):return (a[0]*s,a[1]*s,a[2]*s)
def vdot(a,b):return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def vcross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def vnorm(a):
  l=sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
  if l<1e-9:return (0.0,1.0,0.0)
  return (a[0]/l,a[1]/l,a[2]/l)
def vlerp(a,b,t):return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t)
def ortho(T,U):
  T=vnorm(T);U=vnorm(vsub(U,vmul(T,vdot(U,T))))
  return T,U

#---------- drawing helpers ----------
FRM=[0]
def FR(x,y,w,h,c):
  if w<=0 or h<=0:return
  if FRM[0]==0:
    try:
      fillrect(G,int(x),int(y),int(w),int(h),c,c);return
    except:
      FRM[0]=1
  x=int(x);y=int(y)
  for i in range(int(h)):
    line(G,x,y+i,x+int(w)-1,y+i,c)

def scanfill(pts,c):
  n=len(pts)
  ys=[p[1] for p in pts]
  y0=max(0,int(min(ys)));y1=min(SH-1,int(max(ys)))
  for y in range(y0,y1+1):
    xl=99999;xr=-99999
    for i in range(n):
      ax,ay=pts[i];bx,by=pts[(i+1)%n]
      if (ay<=y<by) or (by<=y<ay):
        x=ax+(y-ay)*(bx-ax)/(by-ay)
        if x<xl:xl=x
        if x>xr:xr=x
    if xl<=xr:
      line(G,int(max(-1,xl)),y,int(min(SW,xr)),y,c)

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
def fog(c,z):
  return mix(c,HAZE,(z-60)/220.0)

#---------- big block font ----------
FONT={
'A':"0111010001111111000110001",'C':"0111110000100001000001111",
'E':"1111110000111101000011111",'F':"1111110000111101000010000",
'G':"0111110000100111000101111",'H':"1000110001111111000110001",
'I':"1111100100001000010011111",'L':"1000010000100001000011111",
'N':"1000111001101011001110001",'O':"0111010001100011000101110",
'P':"1111010001111101000010000",'R':"1111010001111101001010001",
'S':"0111110000011100000111110",'T':"1111100100001000010000100",
'U':"1000110001100011000101110",'B':"1111010001111101000111110",
'W':"1000110001101011101110001",'!':"0010000100001000000000100",
'1':"0010001100001000010001110",'2':"1111000001011101000011111",
'3':"1111000001011100000111110",'D':"1111010001100011000111110",
'Y':"1000101010001000010000100",'M':"1000111011101011000110001",
'K':"1000110010111001001010001",'V':"1000110001100010101000100",
'X':"1000101010001000101010001",'Z':"1111100010001000100011111",
'J':"0011100010000101001001100",'Q':"0111010001101011001001101",
' ':"0000000000000000000000000"}
def bigtext(s,y,sz,c,sh=0):
  x0=(SW-len(s)*6*sz)//2
  for n in range(len(s)):
    f=FONT.get(s[n],FONT[' '])
    for i in range(25):
      if f[i]=='1':
        if sh:FR(x0+n*6*sz+(i%5)*sz+sz//3+1,y+(i//5)*sz+sz//3+1,sz,sz,sh)
        FR(x0+n*6*sz+(i%5)*sz,y+(i//5)*sz,sz,sz,c)
def ctext(s,y,c):
  textout(G,(SW-len(s)*7)//2+1,y+1,s,0);textout(G,(SW-len(s)*7)//2,y,s,c)

#---------- input ----------
K_UP=2;K_DN=12;K_LT=7;K_RT=8;K_ESC=4;K_ENTER=30;K_MENU=13
K_8=33;K_5=38;K_4=37;K_6=39;K_1=42;K_2=43;K_3=44;K_PLUS=50;K_MINUS=45;K_DEL=19
K_7=32;K_9=34
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
    if x<=p[0]<x+w and y<=p[1]<y+h:
      return 1
  return 0

BL=(4,178,58,58);BR=(66,178,58,58)
BB=(196,178,58,58);BG=(258,178,58,58)
BX=(126,3,68,20)
def button(b,on,col):
  x,y,w,h=b
  if on:FR(x,y,w,h,col)
  FR(x,y,w,2,0xFFFFFF);FR(x,y+h-2,w,2,0xFFFFFF)
  FR(x,y,2,h,0xFFFFFF);FR(x+w-2,y,2,h,0xFFFFFF)
def drawButtons(l,r,b,g,x):
  button(BL,l,0x3060C0);button(BR,r,0x3060C0)
  button(BB,b,0xC03030);button(BG,g,0x30A040)
  button(BX,x,0x806020)
  x0,y0,w,h=BL
  poly([(x0+14,y0+29),(x0+42,y0+12),(x0+42,y0+46)],0xFFFFFF)
  x0,y0,w,h=BR
  poly([(x0+44,y0+29),(x0+16,y0+12),(x0+16,y0+46)],0xFFFFFF)
  x0,y0,w,h=BB
  FR(x0+14,y0+14,30,30,0xFFFFFF)
  FR(x0+18,y0+18,22,22,0xC03030 if not b else 0xFFFFFF)
  textout(G,x0+9,y0+44,"BRAKE",0xFFFFFF)
  x0,y0,w,h=BG
  poly([(x0+29,y0+8),(x0+50,y0+40),(x0+8,y0+40)],0xFFFFFF)
  textout(G,x0+17,y0+44,"GAS",0xFFFFFF)
  textout(G,BX[0]+11,BX[1]+4,"RESET",0xFFFFFF)

#---------- tracks ----------
#Classic tracks: closed loop of control points (x, z, height), 3 laps.
#Stunt tracks: built from pieces, point to point, 1 run:
#  ('X', length, yaw, pitch, roll [,side [,magnetic]])  degrees over the piece
#  ('G', length, drop, landpitch)  gap: fly over it!
#  ('C',)  checkpoint here
#  yaw + = turn right, pitch + = climb, roll + = bank right side down
TRACKS=[
 ["MEADOW",0,10.0,1,
  [(0,0,0),(80,0,0),(135,25,0),(150,85,0),(110,125,0),(65,100,0),
   (30,135,0),(-35,140,0),(-80,100,0),(-65,50,0),(-105,15,0),(-65,-25,0)]],
 ["SKYWAY",0,9.0,0,
  [(0,0,6),(70,0,6),(125,-30,9),(165,10,12),(150,75,10),(90,90,7),
   (45,60,5),(5,90,8),(-50,100,11),(-95,45,9),(-80,-5,7),(-45,-20,6)]],
 ["LOOP VALLEY",1,10.0,0,[
  ('X',60,0,0,0),('X',36,60,0,18),('X',36,30,0,-18),('X',48,0,0,0),('C',),
  ('X',20,0,14,0),('G',22,3,10),('X',16,0,10,0),('C',),('X',56,0,0,0),
  ('X',69.1,0,360,0,12),('X',36,0,0,0),
  ('X',24,-45,0,-20),('X',24,-45,0,20),('X',40,0,0,0),('C',),
  ('X',20,0,12,0),('X',24,0,-24,0),('X',20,0,12,0),('X',60,0,0,0)]],
 ["WALL RIDER",1,10.0,0,[
  ('X',60,0,0,0),('X',30,35,0,75),('X',50,110,0,0),('X',30,35,0,-75),
  ('X',50,0,0,0),('C',),
  ('X',20,0,-10,0),('X',20,0,10,0),('X',40,0,0,0),
  ('X',30,-35,0,-75),('X',50,-110,0,0),('X',30,-35,0,75),
  ('X',60,0,0,0),('C',),
  ('X',20,0,14,0),('G',18,2,10),('X',14,0,10,0),('X',60,0,0,0)]],
 ["UPSIDE DOWN",1,10.0,0,[
  ('X',60,0,0,0),('X',20,0,16,0),('X',20,0,-16,0),('X',30,0,0,0),
  ('X',40,0,0,180,0,1),('X',34,0,0,0,0,1),('X',40,0,0,180,0,1),
  ('C',),('X',56,0,0,0),
  ('X',69.1,0,360,0,-12),('X',30,0,0,0),
  ('X',30,60,0,25),('X',30,60,0,-25),('C',),('X',50,0,0,0),
  ('X',20,0,15,0),('G',24,3,10),('X',14,0,10,0),('X',40,0,0,0),
  ('X',30,0,0,90,0,1),('X',40,70,0,0,0,1),('X',30,0,0,-90,0,1),('X',50,0,0,0)]]]

#---------- long tracks ----------
TRACKS.append(["SPEEDWAY",1,12.0,0,[
  ('X',60,0,0,0),('B',40),('X',160,0,0,0),('C',),
  ('X',130,45,0,18),('X',130,45,0,-18),
  ('X',80,0,0,0),('B',30),('X',140,0,0,0),
  ('X',150,-60,0,-20),('X',150,-60,0,20),
  ('X',60,0,0,0),('C',),
  ('X',40,0,5,0),('X',40,0,-5,0),('X',100,0,0,0),('B',40),('X',60,0,0,0),
  ('X',24,0,9,0),('G',45,7,7),('X',30,0,7,0),('X',180,0,0,0),('C',),
  ('X',160,70,0,22),('X',160,70,0,-22),('X',60,0,0,0),('B',30),
  ('X',200,0,0,0),('X',120,-40,0,-15),('X',120,-40,0,15),('X',150,0,0,0)]])
TRACKS.append(["GRAND TOUR",1,10.0,0,[
  ('X',60,0,0,0),('B',30),('X',120,0,0,0),
  ('X',90,40,0,20),('X',90,40,0,-20),('X',60,0,0,0),('C',),
  ('X',60,0,0,0),('X',69.1,0,360,0,12),('X',80,0,0,0),('B',30),
  ('X',60,0,0,0),('X',40,40,0,75),('X',90,100,0,0),('X',40,40,0,-75),
  ('X',80,0,0,0),('C',),
  ('X',120,0,0,0),('X',50,0,0,180,0,1),('X',60,0,0,0,0,1),('X',50,0,0,180,0,1),
  ('X',80,0,0,0),('B',30),('X',60,0,0,0),('X',22,0,12,0),('G',40,5,8),('X',26,0,8,0),('X',150,0,0,0),('C',),
  ('X',120,-50,0,-18),('X',120,-50,0,18),('X',80,0,0,0),
  ('X',40,0,-12,0),('X',40,0,12,0),('X',60,0,0,0),('X',69.1,0,360,0,-12),('X',60,0,0,0),
  ('B',40),('X',200,0,0,0),('X',100,60,0,20),('X',100,60,0,-20),('X',160,0,0,0)]])
_m=[('X',60,0,0,0),('B',30),('X',100,0,0,0)]
for _k in range(9):
  _d=1 if _k%2==0 else -1
  _m+=[('X',110,40*_d,0,16*_d),('X',110,40*_d,0,-16*_d),('X',50,0,8,0),('X',50,0,-8,0)]
  if _k%3==1:_m+=[('C',)]
  if _k%3==2:_m+=[('B',30),('X',60,0,0,0),('X',20,0,10,0),('G',40,4,8),('X',24,0,8,0),('X',100,0,0,0),('C',)]
_m+=[('X',150,0,0,0)]
TRACKS.append(["MARATHON",1,11.0,0,_m])

def trackInfo(ti):
  #length + feature list for the menu card (no need to build the track)
  name,stunt,w,ground,data=TRACKS[ti]
  feats=[];L=0.0
  if not stunt:
    for i in range(len(data)):
      a=data[i];b=data[(i+1)%len(data)]
      L+=sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
    feats.append(("3 LAPS",0x4080FF))
    feats.append(("GRASS",0x40A040) if ground else ("SKY",0x60A0E0))
    return L,feats
  fl={}
  for pc in data:
    k=pc[0]
    if k=='C':continue
    L+=pc[1]
    if k=='G':fl['JUMP']=1
    elif k=='B':fl['BOOST']=1
    else:
      if abs(pc[3])>=300:fl['LOOP']=1
      if len(pc)>6 and pc[6]:fl['MAGNET']=1
      elif abs(pc[4])>=60:fl['WALL']=1
      if len(pc)>7 and pc[7]:fl['BOOST']=1
  cols={'LOOP':0xC2185B,'WALL':0x7B1FA2,'JUMP':0xE65100,'BOOST':0x10A050,'MAGNET':0x8040E0}
  for k in ('BOOST','LOOP','WALL','MAGNET','JUMP'):
    if k in fl:feats.append((k,cols[k]))
  return L,feats

def cr(a,b,c,d,t):
  t2=t*t;t3=t2*t
  return 0.5*(2*b+(c-a)*t+(2*a-5*b+4*c-d)*t2+(3*b-a-3*c+d)*t3)

def build(ti):
  #build a track; if memory runs out, free everything and try once more
  try:
    _build(ti)
  except MemoryError:
    freeTrack();gc.collect()
    _build(ti)

def _build(ti):
  global VP,VB,VT,VU,GAP,MAG,FOL,BOOST,SL,KV,N,SEGT,SEGB,VPTS,TW,HW,CLOSED,GROUND,GY,CPS,MM,TNAME,TREES,LAPS,MINY,MTN3,ELEV
  name,stunt,w,ground,data=TRACKS[ti]
  TNAME=name;TW=w;HW=w/2;GROUND=ground;CLOSED=not stunt
  global VTOP
  VTOP=44.0 if CLOSED else 52.0   #classic 3-lap tracks keep their original top speed
  #free the previous track BEFORE building the next one
  VP=VB=VT=VU=GAP=MAG=FOL=BOOST=SL=KV=SEGT=SEGB=VPTS=TREES=None
  freeTrack()
  gc.collect()
  NN=countVerts(stunt,data)
  VP=V3(NN);VB=V3(NN) if stunt else None;VT=V3(NN);VU=V3(NN);GAP=F1(NN);MAG=F1(NN);cps=[]
  if CLOSED:
    P=data;n=len(P)
    for i in range(n):
      a=P[i-1];b=P[i];c=P[(i+1)%n];d=P[(i+2)%n]
      L=sqrt((c[0]-b[0])**2+(c[1]-b[1])**2)
      m=max(2,int(L/6))
      for s in range(m):
        t=s/m
        VP.append((cr(a[0],b[0],c[0],d[0],t),cr(a[2],b[2],c[2],d[2],t),cr(a[1],b[1],c[1],d[1],t)))
    N=len(VP)
    for i in range(N):
      T=vsub(VP[(i+1)%N],VP[i-1])
      T,U=ortho(T,(0,1,0))
      VT.append(T);VU.append(U);GAP.append(0);MAG.append(0)
    FOL=F1(N);BOOST=F1(N)
    for i in range(N):FOL.append(0);BOOST.append(0)
    VB=VP
    LAPS=3
  else:
    P=(0.0,30.0,0.0);T=(0.0,0.0,1.0);U=(0.0,1.0,0.0);off=(0.0,0.0,0.0)
    VP.append(P);VB.append(P);VT.append(T);VU.append(U)
    gaps=GAP;mags=MAG;fols=F1(NN);boos=F1(NN)
    for pc in data:
      k=pc[0]
      if k=='C':
        cps.append(len(VP)-1);continue
      if k=='G':
        L,drop,lp=pc[1],pc[2],pc[3]
        h=vnorm((T[0],0,T[2]))
        P=(P[0]+h[0]*L,P[1]-drop,P[2]+h[2]*L)
        a=radians(lp)
        T=vnorm((h[0]*cos(a),-sin(a),h[2]*cos(a)))
        T,U=ortho(T,(0,1,0))
        gaps.append(1);mags.append(0);fols.append(0);boos.append(0)
        VP.append(P);VB.append(vsub(P,off));VT.append(T);VU.append(U)
        continue
      if k=='B':pc=('X',pc[1],0,0,0,0,0,1)
      L,yw,pt,rl=pc[1],pc[2],pc[3],pc[4]
      side=pc[5] if len(pc)>5 else 0
      mg=pc[6] if len(pc)>6 else 0
      bo=pc[7] if len(pc)>7 else 0
      #straight pieces need fewer points (saves memory); curves keep 4 m steps
      stp=8.0 if (yw==0 and pt==0 and rl==0 and not side) else 4.0
      n=max(1,int(L/stp+0.5));ds=L/n
      ay=radians(yw)/n;ap=radians(pt)/n;ar=radians(rl)/n
      for s in range(n):
        if ay:
          #turn around the world vertical, keeping any bank
          c=cos(ay);sn=sin(ay)
          T=(T[0]*c+T[2]*sn,T[1],-T[0]*sn+T[2]*c)
          U=(U[0]*c+U[2]*sn,U[1],-U[0]*sn+U[2]*c)
        if ap:
          T2=vadd(vmul(T,cos(ap)),vmul(U,sin(ap)));U=vsub(vmul(U,cos(ap)),vmul(T,sin(ap)));T=T2
        if ar:
          R=vcross(U,T);U=vadd(vmul(U,cos(ar)),vmul(R,sin(ar)))
        T,U=ortho(T,U)
        R=vcross(U,T)
        P=vadd(P,vmul(T,ds))
        if side:
          o=vmul(R,side/n);P=vadd(P,o);off=vadd(off,o)
        gaps.append(0);mags.append(mg);fols.append(1 if abs(pt)>=90 else 0);boos.append(bo)
        VP.append(P);VB.append(vsub(P,off));VT.append(T);VU.append(U)
    N=len(VP)
    gaps.append(0);mags.append(0);fols.append(0);boos.append(0)
    FOL=fols;BOOST=boos;gaps=mags=fols=boos=None
    LAPS=1
  #segment directions: real (SEGT) and untwisted (SEGB, ignores the sideways
  #shift of twisting loops - your car's heading follows this one)
  gc.collect()
  SEGT=V3(N);SEGB=V3(N)
  for i in range(N):
    j=(i+1)%N
    if not CLOSED and i>=N-1:
      SEGT.append(VT[i]);SEGB.append(VT[i])
    else:
      SEGT.append(vnorm(vsub(VP[j],VP[i])));SEGB.append(vnorm(vsub(VB[j],VB[i])))
  VB=None
  #segment lengths and curvature vectors
  SL=FA(N);KV=V3(N)
  for i in range(N):
    j=(i+1)%N
    if not CLOSED and i==N-1:
      SL.append(4.0);KV.append((0.0,0.0,0.0));continue
    d=vsub(VP[j],VP[i]);l=sqrt(vdot(d,d))
    SL.append(max(0.5,l))
  for i in range(N):
    if not CLOSED and (i==0 or i>=N-2):KV.append((0.0,0.0,0.0));continue
    b=segT(i)
    a=b if GAP[(i-1)%N] else segT(i-1)
    c=b if GAP[(i+1)%N] else segT((i+1)%N)
    ds=SL[i] if SL[i]>0.5 else 4.0
    KV.append(vmul(vsub(c,a),0.5/ds))
  if CLOSED:
    CPS=[0,N//4,N//2,(3*N)//4]
  else:
    CPS=[0]+cps+[N-2]
  MINY=min(p[1] for p in VP)
  GY=0.0 if GROUND else (MINY-35 if CLOSED else 0.0)
  ELEV=not GROUND
  TREES={}
  if GROUND:
    for i in range(2,N,4):
      s=1 if (i//4)%2 else -1
      d=HW+5+(i*7)%5
      R=vcross(VU[i],VT[i])
      TREES[i]=(VP[i][0]+R[0]*d*s,VP[i][2]+R[2]*d*s,5+(i*3)%4)
  mnx=mxx=VP[0][0];mnz=mxz=VP[0][2]
  for p in VP:
    if p[0]<mnx:mnx=p[0]
    if p[0]>mxx:mxx=p[0]
    if p[2]<mnz:mnz=p[2]
    if p[2]>mxz:mxz=p[2]
  sc=58.0/max(mxx-mnx,mxz-mnz)
  MM=(mnx,mnz,sc,mxx,mxz)
  cx=(mnx+mxx)/2;cz=(mnz+mxz)/2
  MTN3=[]
  for k in range(9):
    a=k*0.7+0.3;r=900+(k*137)%300
    MTN3.append((cx+sin(a)*r,cz+cos(a)*r,a,140+(k*53)%90,[0x6C8CA8,0x5E7E9C,0x7896B0][k%3]))
  precompute()
  gc.collect()

def freeTrack():
  global VPTS,GATEW,PILW
  VPTS=GATEW=PILW=None

def segT(i):
  return SEGT[i%N]

def frameAt(i,t):
  #surface point, forward, up, right at segment i, fraction t
  j=(i+1)%N
  if not CLOSED and j>=N:j=N-1
  P=vlerp(VP[i],VP[j],t)
  T=segT(i)
  T,U=ortho(T,vlerp(VU[i],VU[j],t))
  return P,T,U,vcross(U,T)

#---------- camera ----------
CAM=[(0.0,5.0,-7.0),(1.0,0.0,0.0),(0.0,1.0,0.0),(0.0,0.0,1.0)]   #pos, right, up, fwd
def tf(x,y,z):
  p=CAM[0];r=CAM[1];u=CAM[2];f=CAM[3]
  dx=x-p[0];dy=y-p[1];dz=z-p[2]
  return (dx*r[0]+dy*r[1]+dz*r[2],dx*u[0]+dy*u[1]+dz*u[2],dx*f[0]+dy*f[1]+dz*f[2])
def tfv(v):
  return tf(v[0],v[1],v[2])

def poly3(P,c):
  #P: camera-space points. Fast path when nothing is behind the camera.
  allin=1
  for p in P:
    if p[2]<NEAR:
      allin=0;break
  if allin:
    #whole polygon off one side of the screen? skip it
    l=r=u=d=1
    for p in P:
      x=p[0];y=p[1];z=p[2]
      if x>-XR[0]*z:l=0
      if x<XR[0]*z:r=0
      if y<XR[1]*z:u=0
      if y>-XR[1]*z:d=0
    if l or r or u or d:return
    poly([(int(CX+F*p[0]/p[2]),int(CY-F*p[1]/p[2])) for p in P],c)
    return
  inn=0
  for p in P:
    if p[2]>=NEAR:inn+=1
  if inn==0:return
  Q=[];n=len(P)
  for i in range(n):
    a=P[i];b=P[(i+1)%n]
    ai=a[2]>=NEAR;bi=b[2]>=NEAR
    if ai:Q.append(a)
    if ai!=bi:
      t=(NEAR-a[2])/(b[2]-a[2])
      Q.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),NEAR))
  pts=[]
  mnx=9999;mxx=-9999;mny=9999;mxy=-9999
  for p in Q:
    sx=CX+F*p[0]/p[2];sy=CY-F*p[1]/p[2]
    if sx<mnx:mnx=sx
    if sx>mxx:mxx=sx
    if sy<mny:mny=sy
    if sy>mxy:mxy=sy
    if sx<-4000:sx=-4000
    if sx>4000:sx=4000
    if sy<-4000:sy=-4000
    if sy>4000:sy=4000
    pts.append((int(sx),int(sy)))
  if mxx<0 or mnx>=SW or mxy<0 or mny>=SH:return
  poly(pts,c)

def background():
  u=CAM[2]
  #sky gradient, darker when looking up
  for i in range(4):
    FR(0,i*60,SW,60,mix(SKY2,SKY,i/3.0))
  #ground plane (follows any camera roll)
  p=CAM[0];D=2500.0
  gc=0x6FB04A if GROUND else 0x86B8E0
  poly3([tf(p[0]-D,GY,p[2]-D),tf(p[0]+D,GY,p[2]-D),tf(p[0]+D,GY,p[2]+D),tf(p[0]-D,GY,p[2]+D)],mix(gc,HAZE,0.35))
  D=180.0
  poly3([tf(p[0]-D,GY+0.01,p[2]-D),tf(p[0]+D,GY+0.01,p[2]-D),tf(p[0]+D,GY+0.01,p[2]+D),tf(p[0]-D,GY+0.01,p[2]+D)],gc)
  for (mx,mz,a,h,c) in MTN3:
    sx=cos(a)*160;sz=-sin(a)*160
    b0=tf(mx-sx,GY,mz-sz);b1=tf(mx+sx,GY,mz+sz);tp=tf(mx,GY+h,mz)
    poly3([b0,b1,tp],c)

#---------- track rendering ----------
ROAD=(0x5C6370,0x646B78)
MROAD=(0x6A3C9A,0x7848A8)
VIEW=[20]
VIEWS=[12,16,20,26,34]

def precompute():
  #everything about the track that never moves, computed once per track
  global VPTS,GATEW,PILW,MMG
  hw=HW;cw=hw+0.9
  gc.collect()
  VPTS=P6(N);GATEW={};PILW={}
  for i in range(N):
    P=VP[i];U=VU[i];R=vcross(U,VT[i])
    L=vsub(P,vmul(R,hw));Rr=vadd(P,vmul(R,hw))
    LO=vsub(P,vmul(R,cw));RO=vadd(P,vmul(R,cw))
    D=vmul(U,-0.9)
    VPTS.append((L,Rr,LO,RO,vadd(LO,D),vadd(RO,D)))
    if ELEV and i%3==0 and U[1]>0.85 and not GAP[i]:
      PILW[i]=((P[0]-R[0]*1.2,P[1]-0.9,P[2]-R[2]*1.2),(P[0]+R[0]*1.2,P[1]-0.9,P[2]+R[2]*1.2),
               (P[0]+R[0]*1.2,GY,P[2]+R[2]*1.2),(P[0]-R[0]*1.2,GY,P[2]-R[2]*1.2))
  for i in CPS:
    P=VP[i];U=VU[i];R=vcross(U,VT[i]);gw=HW+1.2;H=5.0;ps=[]
    for sd in (-1,1):
      b=vadd(P,vmul(R,gw*sd));a0=vsub(b,vmul(R,0.4));a1=vadd(b,vmul(R,0.4))
      ps.append((a0,a1,vadd(a1,vmul(U,H)),vadd(a0,vmul(U,H))))
    e0=vsub(P,vmul(R,gw+0.4));e1=vadd(P,vmul(R,gw+0.4))
    bar=(vadd(e0,vmul(U,H)),vadd(e1,vmul(U,H)),vadd(e1,vmul(U,H-1.3)),vadd(e0,vmul(U,H-1.3)))
    GATEW[i]=(ps,bar)
  MMG[0]=0

def tfl(pts):
  #transform a list of world points to camera space (inlined for speed)
  p=CAM[0];r=CAM[1];u=CAM[2];f=CAM[3]
  px=p[0];py=p[1];pz=p[2];r0=r[0];r1=r[1];r2=r[2];u0=u[0];u1=u[1];u2=u[2];f0=f[0];f1=f[1];f2=f[2]
  out=[]
  for q in pts:
    dx=q[0]-px;dy=q[1]-py;dz=q[2]-pz
    out.append((dx*r0+dy*r1+dz*r2,dx*u0+dy*u1+dz*u2,dx*f0+dy*f1+dz*f2))
  return out

FARZ=50.0
FARV=[36]   #extra far-view vertices (drawn 3 at a time)
def renderTrack(si):
  T={}
  idx=[]
  for k in range(-4,VIEW[0]+1):
    i=si+k
    if CLOSED:i=i%N
    elif i<0 or i>=N:continue
    idx.append(i)
    T[i]=tfl(VPTS[i])
  items=[]
  for i in idx:
    j=(i+1)%N
    if j not in T:continue
    A=T[i];B=T[j]
    z=(A[0][2]+A[1][2]+B[0][2]+B[1][2])*0.25
    if A[2][2]<NEAR and A[3][2]<NEAR and B[2][2]<NEAR and B[3][2]<NEAR:continue
    if not GAP[i]:
      items.append((z,0,i,A,B))
    if i in GATEW and (i!=CPS[0] or CLOSED):
      items.append((z-0.5,1,i,None,None))
    if i in PILW:
      items.append((z+2,2,i,None,None))
    if i in TREES:
      items.append((z+1,3,i,None,None))
  #far road: every 3rd vertex, one polygon each -> you can see far ahead at speed
  far=FARV[0]
  k=VIEW[0]
  while k<VIEW[0]+far:
    i=si+k;j=i+3
    if CLOSED:i%=N;j%=N
    elif j>=N-1:break
    if not (GAP[i] or GAP[(i+1)%N] or GAP[(i+2)%N]):
      A=tfl((VPTS[i][2],VPTS[i][3]));B=tfl((VPTS[j][2],VPTS[j][3]))
      z=(A[0][2]+B[0][2])*0.5
      if A[0][2]>NEAR or B[0][2]>NEAR:
        items.append((z,4,i,A,B))
    k+=3
  items.sort(key=lambda q:-q[0])
  for z,ty,i,A,B in items:
    if ty==4:
      poly3([A[0],A[1],B[1],B[0]],fog(0x18E070 if BOOST[i] else (MROAD if MAG[i] else ROAD)[0],z))
    elif ty==0:
      seg(i,A,B,z)
    elif ty==1:
      gate(i,z)
    elif ty==2:
      poly3(tfl(PILW[i]),fog(0x8890A0,z))
    else:
      tree(TREES[i])

def seg(i,A,B,z):
  #top or underside depending on where the camera is
  c=CAM[0];P=VP[i];U=VU[i]
  above=(c[0]-P[0])*U[0]+(c[1]-P[1])*U[1]+(c[2]-P[2])*U[2]>0
  if z>FARZ:
    #far away: one polygon for road + kerbs
    if above:
      poly3([A[2],A[3],B[3],B[2]],fog(0x18E070 if BOOST[i] else (MROAD if MAG[i] else ROAD)[i%2],z))
    else:
      poly3([A[4],A[5],B[5],B[4]],fog(0x2A2F38,z))
    return
  if ELEV and z<36:
    poly3([A[2],B[2],B[4],A[4]],fog(0x3A4250,z))
    poly3([A[3],B[3],B[5],A[5]],fog(0x30363F,z))
  if not above:
    poly3([A[4],A[5],B[5],B[4]],fog(0x2A2F38,z))
    return
  fin=(not CLOSED and i==N-3) or (CLOSED and i==0)
  if fin:
    for c in range(6):
      t0=c/6.0;t1=(c+1)/6.0
      p0=lerp3(A[0],A[1],t0);p1=lerp3(A[0],A[1],t1)
      q0=lerp3(B[0],B[1],t0);q1=lerp3(B[0],B[1],t1)
      m0=lerp3(p0,q0,0.5);m1=lerp3(p1,q1,0.5)
      poly3([p0,p1,m1,m0],0xF0F0F0 if c%2 else 0x202020)
      poly3([m0,m1,q1,q0],0x202020 if c%2 else 0xF0F0F0)
  elif BOOST[i]:
    poly3([A[0],A[1],B[1],B[0]],fog(0x10C060 if i%2 else 0x18E070,z))
    m0=lerp3(A[0],A[1],0.5);l0=lerp3(A[0],A[1],0.2);r0=lerp3(A[0],A[1],0.8)
    tip=lerp3(lerp3(B[0],B[1],0.5),m0,0.1)
    poly3([l0,tip,r0,lerp3(m0,tip,0.45)],0xF0FFF0)
  else:
    poly3([A[0],A[1],B[1],B[0]],fog((MROAD if MAG[i] else ROAD)[i%2],z))
  if MAG[i]:
    cc=fog(0xC060FF if i%2 else 0xF5F5F5,z)
  else:
    cc=fog(0xE53935 if i%2 else 0xF5F5F5,z)
  poly3([A[2],A[0],B[0],B[2]],cc)
  poly3([A[1],A[3],B[3],B[1]],cc)

def lerp3(a,b,t):
  return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t)

def gate(i,z):
  if i==CPS[NEXTCP[0]] and not (CLOSED and i==0):
    col=0xFFC107;bar=0xFF8F00
  elif CLOSED and i==0:
    col=0xF0F0F0;bar=0x202020
  else:
    col=0x42A5F5;bar=0x1E88E5
  col=fog(col,z);bar=fog(bar,z)
  ps,bw=GATEW[i]
  for q in ps:poly3(tfl(q),col)
  poly3(tfl(bw),bar)

def tree(t):
  x,z,h=t
  b=tf(x,0,z)
  if b[2]<1.5:return
  top=tf(x,h,z);mid=tf(x,1.0,z)
  s=F/b[2]
  sx=CX+F*b[0]/b[2]
  if sx<-60 or sx>SW+60:return
  sy=CY-F*b[1]/b[2];ty=CY-F*top[1]/top[2];my=CY-F*mid[1]/mid[2]
  tx=CX+F*top[0]/top[2];mx=CX+F*mid[0]/mid[2]
  w=1.9*s
  poly([(int(sx-0.25*s),int(sy)),(int(sx+0.25*s),int(sy)),(int(mx+0.25*s),int(my)),(int(mx-0.25*s),int(my))],fog(0x6D4C33,b[2]))
  poly([(int(tx),int(ty)),(int(mx-w),int(my)),(int(mx),int(my))],fog(0x2E7D32,b[2]))
  poly([(int(tx),int(ty)),(int(mx+w),int(my)),(int(mx),int(my))],fog(0x43A047,b[2]))

#---------- car model ----------
#boxes: x0,x1 (right), y0,y1 (up), f0,f1 (forward), colour
CARBOX=[(-0.95,0.95,0.0,0.6,0.8,1.6,0x1A1A1A),(-0.95,0.95,0.0,0.6,-1.6,-0.8,0x1A1A1A),
        (-0.9,0.9,0.25,0.75,-1.9,1.9,0xFF5722),
        (-0.7,0.7,0.75,1.25,-1.0,0.5,0x263238),
        (-0.95,0.95,1.0,1.1,-2.0,-1.65,0xFFB300)]
CARSH=[[shade(c,k) for k in (1.0,0.62,0.85,0.75)] for (a,b,cc,d,e,f,c) in CARBOX]
def drawCar():
  p=CAR.pos;fw=CAR.fwd;up=CAR.up;rt=vcross(up,fw)
  #camera position in car-local coordinates (for back-face culling)
  d=vsub(CAM[0],p)
  lx=vdot(d,rt);ly=vdot(d,up);lz=vdot(d,fw)
  #car axes and origin in camera space
  o=tfv(p);cr=CAM[1];cu=CAM[2];cf=CAM[3]
  ax=(vdot(rt,cr),vdot(rt,cu),vdot(rt,cf))
  ay=(vdot(up,cr),vdot(up,cu),vdot(up,cf))
  az=(vdot(fw,cr),vdot(fw,cu),vdot(fw,cf))
  def C(a,u,f):
    return (o[0]+ax[0]*a+ay[0]*u+az[0]*f,o[1]+ax[1]*a+ay[1]*u+az[1]*f,o[2]+ax[2]*a+ay[2]*u+az[2]*f)
  faces=[]
  for bi in range(len(CARBOX)):
    x0,x1,y0,y1,f0,f1,col=CARBOX[bi];sh=CARSH[bi]
    if ly>y1:faces.append((C(x0,y1,f0),C(x1,y1,f0),C(x1,y1,f1),C(x0,y1,f1),sh[0]))
    if lz<f0:faces.append((C(x0,y0,f0),C(x1,y0,f0),C(x1,y1,f0),C(x0,y1,f0),sh[1]))
    elif lz>f1:faces.append((C(x0,y0,f1),C(x1,y0,f1),C(x1,y1,f1),C(x0,y1,f1),sh[2]))
    if lx<x0:faces.append((C(x0,y0,f0),C(x0,y0,f1),C(x0,y1,f1),C(x0,y1,f0),sh[3]))
    elif lx>x1:faces.append((C(x1,y0,f0),C(x1,y0,f1),C(x1,y1,f1),C(x1,y1,f0),sh[3]))
  faces.sort(key=lambda q:-(q[0][2]+q[2][2]))
  for q in faces:
    poly3(q[:4],q[4])

#---------- state ----------
class Obj:
  pass
CAR=Obj()
NEXTCP=[1]
BEST=[None]*len(TRACKS)

def loadBest():
  try:
    f=open("best.txt","r");s=f.read();f.close()
    p=s.split(",")
    for i in range(min(len(p),len(BEST))):
      BEST[i]=None if p[i].strip()=="-" else int(p[i])
  except:
    pass
def saveBest():
  try:
    f=open("best.txt","w")
    f.write(",".join(["-" if b is None else str(b) for b in BEST]));f.close()
  except:
    pass

def place(i):
  #(re)spawn the car on the track at vertex i
  CAR.mode=0;CAR.i=i;CAR.s=0.0;CAR.lat=0.0;CAR.psi=0.0;CAR.phi=0.0;CAR.v=0.0;CAR.vlat=0.0;CAR.drift=0
  CAR.vel=(0.0,0.0,0.0);CAR.air=0.0;CAR.fall=0.0;CAR.h=0.0;CAR.N=GRAV
  P,T,U,R=frameAt(i,0.0)
  CAR.pos=P;CAR.fwd=T;CAR.up=U
  CAR.cf=T;CAR.cu=U;CAR.boost=0.0
  global F
  F=190.0;XR[0]=CX/F;XR[1]=CY/F
  CAM[0]=vadd(vsub(P,vmul(T,7.0)),vmul(U,2.8))
  setcam()

def fmt(ms):
  if ms is None:return "--:--.--"
  s=ms//1000;cs=(ms%1000)//10
  return str(s//60)+":"+("0" if s%60<10 else "")+str(s%60)+"."+("0" if cs<10 else "")+str(cs)

def engine(v,gas,brk,vmax,dt):
  if v>vmax:
    #above top speed (after a boost): ease back down slowly
    v-=((v-vmax)*0.22+1.5)*dt
  if gas:
    if v<0:v+=30*dt
    elif v<vmax:v+=19*dt*max(0.0,1-v/vmax)
  if brk:
    if v>0:v-=32*dt
    else:v-=9*dt
    if v<-9:v=-9.0
  if not gas and not brk:
    v-=v*0.35*dt
  return v

def crossed(old,new):
  if CLOSED:
    d=(new-old)%N
    if not (0<d<N//2):return
    rng=[(old+s)%N for s in range(1,d+1)]
  else:
    if new<=old:return
    rng=range(old+1,new+1)
  for j in rng:
    if j==CPS[NEXTCP[0]]:
      RACE.last=j
      if CLOSED:
        if NEXTCP[0]==0:
          RACE.lapdone=1
        else:
          RACE.flash=1.0;RACE.msg="CHECKPOINT "+str(NEXTCP[0])+"/"+str(len(CPS)-1)
        NEXTCP[0]=(NEXTCP[0]+1)%len(CPS)
      else:
        if NEXTCP[0]==len(CPS)-1:
          RACE.lapdone=1
        else:
          RACE.flash=1.0;RACE.msg="CHECKPOINT "+str(NEXTCP[0])+"/"+str(len(CPS)-2)
          NEXTCP[0]+=1

def detach():
  P,T,U,R=frameAt(CAR.i,CAR.s/SL[CAR.i])
  mv=vadd(vmul(T,cos(CAR.psi)),vmul(R,sin(CAR.psi)))
  CAR.vel=vadd(vmul(mv,CAR.v),vmul(R,CAR.vlat))
  CAR.drift=0
  CAR.pos=vadd(CAR.pos,vmul(U,0.05))
  CAR.mode=1;CAR.air=0.0

def attachTo(i,t,lat,U,T,R):
  vt=vdot(CAR.vel,T);vr=vdot(CAR.vel,R)
  CAR.mode=0;old=CAR.i;CAR.i=i;CAR.s=t*SL[i];CAR.lat=lat
  CAR.v=sqrt(vt*vt+vr*vr)*(1 if vt>=0 else -1)
  CAR.psi=atan2(vr,abs(vt)) if vt>=0 else 0.0
  if abs(CAR.psi)>1.0:CAR.psi=1.0 if CAR.psi>0 else -1.0
  CAR.phi=CAR.psi;CAR.drift=0
  CAR.vlat=0.0
  crossed(old,i)

def surfaceNear(pos,ci,back,fwd,tol):
  #find a track surface under pos near segment ci. returns (i,t,lat,h,P,T,U,R) or None
  best=None
  for k in range(-back,fwd+1):
    i=ci+k
    if CLOSED:i=i%N
    elif i<0 or i>=N-1:continue
    if GAP[i]:continue
    A=VP[i];T=segT(i);d=vsub(pos,A)
    al=vdot(d,T)
    if al<-0.3 or al>SL[i]+0.3:continue
    t=min(1.0,max(0.0,al/SL[i]))
    P,T,U,R=frameAt(i,t)
    d=vsub(pos,P)
    h=vdot(d,U);lat=vdot(d,R)
    if abs(lat)>HW+tol:continue
    if best is None or abs(h)<abs(best[3]):
      best=(i,t,lat,h,P,T,U,R)
  return best

SMOKE=[]
def smoke(T,R,U):
  p=CAR.pos;f=CAR.fwd;r=vcross(CAR.up,f)
  for sd in (-0.9,0.9):
    q=vadd(vadd(p,vmul(f,-1.6)),vadd(vmul(r,sd),vmul(CAR.up,0.25)))
    SMOKE.append([q,0.6])
  while len(SMOKE)>16:SMOKE.pop(0)

def drawSmoke(dt):
  for sm in SMOKE[:]:
    sm[1]-=dt
    if sm[1]<=0:
      SMOKE.remove(sm);continue
    q=tfv(vadd(sm[0],vmul(CAR.up,(0.6-sm[1])*1.5)))
    if q[2]<NEAR:continue
    sz=int(F*(0.5+(0.6-sm[1])*1.2)/q[2])+1
    x=int(CX+F*q[0]/q[2]);y=int(CY-F*q[1]/q[2])
    FR(x-sz//2,y-sz//2,sz,sz,mix(0xE8E8E8,0x9A9A9A,sm[1]/0.6))

def keepHeading(a,b):
  #No part of the track turns your car: bends and banks keep your own
  #direction. Twisting loops still shift you sideways, but your car keeps
  #pointing the same way (SEGB ignores the twist).
  T0=SEGB[a%N];T1=SEGB[b%N]
  R0=vcross(VU[b if b>a or (CLOSED and a==N-1 and b==0) else a],T0)
  d=atan2(vdot(T1,R0),vdot(T1,T0))
  CAR.psi-=d;CAR.phi-=d
  if CAR.psi>pi:CAR.psi-=2*pi;CAR.phi-=2*pi
  if CAR.psi<-pi:CAR.psi+=2*pi;CAR.phi+=2*pi

def physics(dt,gas,brk,st):
  if CAR.mode==0:
    i=CAR.i;t=CAR.s/SL[i]
    P,T,U,R=frameAt(i,t)
    fw=vadd(vmul(T,cos(CAR.psi)),vmul(R,sin(CAR.psi)))
    sp=abs(CAR.v)
    #DRIFT: brake + steer at speed kicks the rear out. Keep it going with
    #gas and counter-steer; let go of the steering to straighten up.
    slip=CAR.phi-CAR.psi
    if not CAR.drift and brk and st and sp>14 and CAR.v>0:
      CAR.drift=1
    elif CAR.drift and ((st==0 and abs(slip)<0.10) or sp<7 or CAR.v<0):
      CAR.drift=0
    if CAR.drift:
      v=CAR.v
      if gas and v<VTOP-6:v+=11*dt*max(0.0,1-v/(VTOP-6))
      elif v>VTOP:v-=((v-VTOP)*0.22+1.5)*dt
      elif brk:v-=6*dt
    else:
      v=engine(CAR.v,gas,brk,VTOP,dt)
    v-=GRAV*fw[1]*dt
    if BOOST[i] and v<VBOOST:
      v=min(VBOOST,v+75*dt);CAR.boost=0.6
    #sliding sideways costs speed
    v-=abs(sin(slip))*abs(v)*0.32*dt
    CAR.v=v
    sp=abs(v)
    rate=st*2.3*min(1.0,sp/7.0)/(1+sp/55.0)
    if CAR.drift:rate*=1.25
    if v<0:rate=-rate
    CAR.phi+=rate*dt
    #the direction of travel follows where the car points: fast with grip,
    #slowly while drifting
    grip=(2.4 if st else 4.5) if CAR.drift else 10.0
    CAR.psi+=(CAR.phi-CAR.psi)*min(1.0,grip*dt)
    slip=CAR.phi-CAR.psi
    if slip>0.8:CAR.phi=CAR.psi+0.8
    elif slip<-0.8:CAR.phi=CAR.psi-0.8
    if CAR.drift:
      RACE.dpts=getattr(RACE,'dpts',0.0)+abs(sin(slip))*sp*dt*4
      CAR.sm=getattr(CAR,'sm',0)+1
      if CAR.sm%3==0:smoke(T,R,U)
    #normal force: curvature + gravity + magnet
    K=KV[i]
    Nf=v*v*vdot(K,U)+GRAV*U[1]+(26.0 if MAG[i] else 0.0)
    CAR.N=Nf
    if Nf<-0.5:
      CAR.up=U;detach();return
    #sideways slide when gravity/centrifugal beat the tyres
    alat=-GRAV*R[1]
    grip=0.9*max(0.0,Nf)+2.0
    if alat>grip:CAR.vlat+=(alat-grip)*dt
    elif alat<-grip:CAR.vlat+=(alat+grip)*dt
    CAR.vlat-=CAR.vlat*min(1.0,3.0*dt)
    ds=v*cos(CAR.psi)*dt
    CAR.lat+=(v*sin(CAR.psi)+CAR.vlat)*dt
    old=i;s=CAR.s+ds;launch=0
    while s>SL[i]:
      if GAP[(i+1)%N]:
        #ramp edge: take off along the ramp
        s=SL[i];launch=1;break
      s-=SL[i];pi_=i;i+=1
      if CLOSED:i%=N
      elif i>=N-1:i=N-2;s=SL[i]
      if i!=pi_:keepHeading(pi_,i)
    while s<0:
      pi_=i;i-=1
      if CLOSED:i%=N
      elif i<0:i=0;s=0.0;CAR.v=max(0.0,CAR.v);break
      keepHeading(pi_,i)
      s+=SL[i]
    CAR.i=i;CAR.s=min(s,SL[i])
    crossed(old,i)
    P,T,U,R=frameAt(i,CAR.s/SL[i])
    Tb,Ub=ortho(SEGB[i],U);Rb=vcross(Ub,Tb)
    CAR.fwd=vadd(vmul(Tb,cos(CAR.phi)),vmul(Rb,sin(CAR.phi)))
    CAR.up=U
    CAR.pos=vadd(P,vmul(R,CAR.lat))
    if launch:
      detach();CAR.i=(i+1)%N;return
    if abs(CAR.lat)>HW+0.9:
      if GROUND and P[1]<0.5:
        toGround();return
      detach();return
  elif CAR.mode==1:
    CAR.air+=dt
    vel=(CAR.vel[0],CAR.vel[1]-GRAV*dt,CAR.vel[2])
    #a little air steering
    if st:
      a=st*1.2*dt;c=cos(a);s=sin(a)
      vel=(vel[0]*c+vel[2]*s,vel[1],-vel[0]*s+vel[2]*c)
    CAR.vel=vel
    CAR.pos=vadd(CAR.pos,vmul(vel,dt))
    up=vnorm(vadd(CAR.up,vmul(vsub((0.0,1.0,0.0),CAR.up),min(1.0,dt*1.8))))
    fw=vnorm(vadd(CAR.fwd,vmul(vsub(vnorm(vel),CAR.fwd),min(1.0,dt*2.0))))
    CAR.fwd,CAR.up=ortho(fw,up)
    hit=surfaceNear(CAR.pos,CAR.i,6,max(34,int(14+sqrt(vdot(vel,vel))*0.9)),0.6)
    if hit:
      i,t,lat,h,P,T,U,R=hit
      if -2.0<h<0.35 and vdot(vel,U)<=0.5 and (U[1]>0.3 or MAG[i]):
        CAR.pos=vadd(P,vmul(R,lat))
        attachTo(i,t,lat,U,T,R);return
    if GROUND and CAR.pos[1]<=0.0:
      toGround();return
    if not GROUND and (CAR.pos[1]<MINY-20 or CAR.air>3.0):
      CAR.fall=1.0
  else:
    #driving on the grass (meadow)
    v=engine(CAR.v,gas,brk,13.0,dt)
    if v>13:v-=35*dt
    CAR.v=v
    sp=abs(v)
    rate=st*2.3*min(1.0,sp/7.0)/(1+sp/38.0)
    if v<0:rate=-rate
    CAR.h+=rate*dt
    x=CAR.pos[0]+sin(CAR.h)*v*dt;z=CAR.pos[2]+cos(CAR.h)*v*dt
    CAR.pos=(x,0.0,z);CAR.fwd=(sin(CAR.h),0.0,cos(CAR.h));CAR.up=(0.0,1.0,0.0)
    hit=surfaceNear(CAR.pos,CAR.i,8,8,40.0)
    if hit:
      i,t,lat,h,P,T,U,R=hit
      CAR.i=i
      if abs(lat)<HW+0.4:
        CAR.vel=vmul(CAR.fwd,CAR.v);attachTo(i,t,lat,U,T,R);return
      if abs(lat)>HW+16:
        CAR.v=-CAR.v*0.3;CAR.pos=(x-sin(CAR.h)*v*dt*2,0.0,z-cos(CAR.h)*v*dt*2)
    else:
      #lost: snap back to the nearest vertex
      best=None
      for k in range(N):
        d=vsub(CAR.pos,VP[k]);d2=vdot(d,d)
        if best is None or d2<best[0]:best=(d2,k)
      CAR.i=best[1]

def toGround():
  v=CAR.vel if CAR.mode==1 else vmul(CAR.fwd,CAR.v)
  CAR.mode=2
  f=CAR.fwd
  CAR.h=atan2(f[0],f[2])
  CAR.v=sqrt(v[0]*v[0]+v[2]*v[2]) if vdot(v,f)>=0 else -sqrt(v[0]*v[0]+v[2]*v[2])
  CAR.pos=(CAR.pos[0],0.0,CAR.pos[2])

def setcam():
  cu=CAR.cu;p=CAR.pos
  look=vadd(p,vmul(cu,1.0))
  f=vnorm(vsub(look,CAM[0]))
  r=vnorm(vcross(cu,f))
  u=vcross(f,r)
  CAM[1]=r;CAM[2]=u;CAM[3]=f

def camera(dt):
  k=min(1.0,dt*4.0)
  CAR.cf=vnorm(vlerp(CAR.cf,CAR.fwd,k))
  #lean with the car, but stay partly upright so walls look like walls
  tu=vnorm(vadd(CAR.up,(0.0,0.65,0.0))) if CAR.mode!=1 else (0.0,1.0,0.0)
  CAR.cu=vnorm(vlerp(CAR.cu,tu,min(1.0,dt*3.0)))
  CAR.cf,CAR.cu=ortho(CAR.cf,CAR.cu)
  tgt=vadd(vsub(CAR.pos,vmul(CAR.cf,7.0)),vmul(CAR.cu,2.8))
  CAM[0]=vlerp(CAM[0],tgt,min(1.0,dt*7))
  setcam()
  global F
  sp=abs(CAR.v) if CAR.mode!=1 else sqrt(vdot(CAR.vel,CAR.vel))
  tf_=190.0-min(70.0,max(0.0,sp-45.0)*1.3)
  F+= (tf_-F)*min(1.0,dt*3)
  XR[0]=CX/F;XR[1]=CY/F
  CAR.boost=max(0.0,getattr(CAR,'boost',0.0)-dt)

MMG=[0]
def minimap():
  mnx,mnz,sc,mxx,mxz=MM
  ox=256;oy=26
  if MMG[0]==0:
    MMG[0]=-1
    try:
      dimgrob(2,66,66,0x202830)
      px=None
      for i in range(0,N+1,2):
        k=i%N
        if not CLOSED and i>=N:break
        x=3+int((VP[k][0]-mnx)*sc);y=61-int((VP[k][2]-mnz)*sc)
        if px is not None and not GAP[k-2 if k>=2 else 0]:
          line(2,px,py,x,y,0xC060FF if MAG[k] else 0xE0E0E0)
        px=x;py=y
      MMG[0]=1
    except:
      MMG[0]=-1
  if MMG[0]==1:
    try:
      strblit(G,ox-3,oy-3,66,66,2)
    except:
      MMG[0]=-1
  if MMG[0]==-1:
    FR(ox-3,oy-3,66,66,0x202830)
    px=None
    for i in range(0,N+1,4):
      k=i%N
      if not CLOSED and i>=N:break
      x=ox+int((VP[k][0]-mnx)*sc);y=oy+58-int((VP[k][2]-mnz)*sc)
      if px is not None:line(G,px,py,x,y,0xE0E0E0)
      px=x;py=y
  c=CPS[NEXTCP[0]]
  FR(ox+int((VP[c][0]-mnx)*sc)-2,oy+58-int((VP[c][2]-mnz)*sc)-2,4,4,0xFFC107)
  FR(ox+int((CAR.pos[0]-mnx)*sc)-2,oy+58-int((CAR.pos[2]-mnz)*sc)-2,5,5,0xFF3D00)

def hudtext(x,y,s,c):
  textout(G,x+1,y+1,s,0x000000);textout(G,x,y,s,c)

RACE=Obj()
SPL=[0.3,1.1,2.0,2.7,3.5,4.2,5.0,5.8,0.7]
def frame(dt,ctl,showb):
  background()
  renderTrack(CAR.i)
  drawCar()
  drawSmoke(dt)
  sp=abs(CAR.v) if CAR.mode!=1 else sqrt(vdot(CAR.vel,CAR.vel))
  if sp>55:
    #speed lines streaking past the edges of the screen
    n=int((sp-55)/8)+2
    for k in range(min(n,9)):
      a=SPL[k%len(SPL)]+RACE.t*0.0017*k
      r0=70+(RACE.t//5+k*37)%110;r1=r0+20+sp*0.5
      ca=cos(a);sa=sin(a)
      line(G,int(CX+ca*r0),int(CY+sa*r0*0.75),int(CX+ca*r1),int(CY+sa*r1*0.75),0xE8F4FF if k%2 else 0xA8C8E8)
  if getattr(CAR,'boost',0)>0:
    ctext("BOOST!",94,0x40FF90)
  if CLOSED:
    hudtext(4,4,"LAP "+str(min(RACE.lap,LAPS))+"/"+str(LAPS),0xFFFFFF)
  else:
    hudtext(4,4,"CP "+str(NEXTCP[0]-1)+"/"+str(len(CPS)-2),0xFFFFFF)
  hudtext(4,20,fmt(RACE.t),0xFFFF60)
  hudtext(4,36,"BEST "+fmt(BEST[RACE.ti]),0xC0E0FF)
  kmh=int(sp*3.6)
  hudtext(252,4,str(kmh)+" km/h",0xFFFFFF if kmh<200 else (0xFFD040 if kmh<300 else 0xFF5050))
  FR(252,17,64,3,0x202020);FR(252,17,min(64,int(64*sp/VBOOST)),3,0x40FF90 if sp>VTOP else 0xFFFFFF)
  if RACE.map:minimap()
  if RACE.flash>0:
    ctext(RACE.msg,58,0xFFE060)
  if CAR.fall>0:
    ctext("FELL OFF! RESETTING...",76,0xFF6060)
  elif CAR.mode==1 and CAR.air>0.4:
    ctext("AIR "+str(int(CAR.air*10)/10.0)+"s",76,0x80E0FF)
  elif CAR.mode==0 and CAR.up[1]<-0.3:
    ctext("UPSIDE DOWN!",76,0xE0A0FF)
  elif CAR.mode==0 and CAR.drift:
    ctext("DRIFT!  "+str(int(getattr(RACE,'dpts',0))),76,0xFFB040)
  if showb:
    drawButtons(ctl[3],ctl[2],ctl[1],ctl[0],ctl[4])

def flip():
  strblit(0,0,0,SW,SH,G)

def race(ti):
  build(ti)
  RACE.ti=ti;RACE.lap=1;RACE.t=0;RACE.laps=[];RACE.last=0
  RACE.flash=0.0;RACE.msg="";RACE.lapdone=0;RACE.lapstart=0;RACE.resets=0;RACE.dpts=0.0;SMOKE[:]=[]
  if not hasattr(RACE,'map'):RACE.map=1
  if not hasattr(RACE,'btn'):RACE.btn=1
  NEXTCP[0]=1
  st0=2 if CLOSED else 1
  place(st0)
  RACE.last=st0
  for s in ("3","2","1"):
    t0=ticks()
    while ticks()-t0<700:
      camera(0.05)
      frame(0,(0,0,0,0,0),RACE.btn)
      bigtext(s,80,10,0xFFFFFF,0x000000)
      flip()
      if kd(keyboard(),K_ESC):return
  last=ticks();prevk=keyboard();prevx=0
  go=0.8
  while True:
    now=ticks();dt=(now-last)/1000.0;last=now
    if dt>0.25:dt=0.25
    if dt<=0:dt=0.001
    k=keyboard();pk=k&~prevk;prevk=k
    pts=touches() if RACE.btn else []
    if kd(k,K_ESC):return
    gas=kd(k,K_UP) or kd(k,K_8) or inside(BG,pts)
    brk=kd(k,K_DN) or kd(k,K_5) or inside(BB,pts)
    lt=kd(k,K_LT) or kd(k,K_4) or inside(BL,pts)
    rt=kd(k,K_RT) or kd(k,K_6) or inside(BR,pts)
    rx=inside(BX,pts)
    st=(1 if rt else 0)-(1 if lt else 0)
    if kd(pk,K_MENU):RACE.map=1-RACE.map
    if kd(pk,K_DEL):RACE.btn=1-RACE.btn
    if kd(pk,K_PLUS) or kd(pk,K_MINUS):
      i=VIEWS.index(VIEW[0])
      i=min(len(VIEWS)-1,i+1) if kd(pk,K_PLUS) else max(0,i-1)
      VIEW[0]=VIEWS[i];RACE.flash=1.2;RACE.msg="DRAW DISTANCE "+str(VIEW[0])
    if (kd(pk,K_ENTER) or (rx and not prevx)) or CAR.fall>0 and CAR.air>3.6 or (CAR.fall>0 and CAR.pos[1]<MINY-40):
      place(RACE.last);RACE.resets+=1
    prevx=rx
    n=int(dt/0.025)+1
    for s in range(n):
      physics(dt/n,gas,brk,st)
      if CAR.fall>0:CAR.air+=dt/n
    camera(dt)
    RACE.t+=int(dt*1000)
    RACE.flash=max(0.0,RACE.flash-dt)
    if RACE.lapdone:
      RACE.lapdone=0
      lt_=RACE.t-RACE.lapstart;RACE.laps.append(lt_);RACE.lapstart=RACE.t
      RACE.lap+=1
      if RACE.lap>LAPS:
        results();return
      RACE.flash=1.5;RACE.msg="LAP "+str(RACE.lap-1)+"  "+fmt(lt_)
    frame(dt,(gas,brk,rt,lt,rx),RACE.btn)
    if go>0:
      go-=dt;bigtext("GO!",80,10,0x40FF40,0x000000)
    flip()

def results():
  bl=min(RACE.laps)
  nb=BEST[RACE.ti] is None or RACE.t<BEST[RACE.ti]
  if nb:
    BEST[RACE.ti]=RACE.t;saveBest()
  RACE.result=(RACE.t,bl,nb)

#---------- menus ----------
MBT=[(14,92,140,34),(166,92,140,34),(14,132,140,34),(166,132,140,34),(14,172,140,34),(166,172,140,34)]
RB1=(40,190,112,40);RB2=(168,190,112,40)
def waitTap(btns,keys):
  while keyboard() or touches():
    pass
  while True:
    k=keyboard()
    for i in range(len(keys)):
      if keys[i] is not None and kd(k,keys[i]):
        return i
    p=touches()
    if p:
      for i in range(len(btns)):
        if btns[i] and inside(btns[i],p):
          while touches():
            pass
          return i

def menuButton(b,label,sub,c):
  x,y,w,h=b
  FR(x+3,y+3,w,h,0x000000)
  FR(x,y,w,h,c)
  FR(x,y,w,3,0xFFFFFF)
  textout(G,x+(w-len(label)*7)//2,y+5,label,0xFFFFFF)
  if sub:textout(G,x+(w-len(sub)*6)//2,y+19,sub,0xFFFFE0)

MB_L=(4,150,40,50);MB_R=(276,150,40,50);MB_GO=(110,206,100,30);MB_Q=(262,4,54,22)
TSEL=[2]
def menuCard(ti,t):
  L,feats=trackInfo(ti)
  #top: logo
  FR(0,0,SW,30,0x0C141C)
  pc=[0xFF7043,0xFFC107,0x40FF90,0x40C0FF][int(t*1.5)%4]
  bigtext("LAPRUSH",3,4,mix(0xFF7043,pc,0.5+0.5*sin(t*2.5)),0x000000)
  FR(MB_Q[0],MB_Q[1],MB_Q[2],MB_Q[3],0x7A2020);textout(G,MB_Q[0]+10,MB_Q[1]+4,"QUIT",0xFFFFFF)
  #bottom: track card
  FR(0,144,SW,96,0x0C141C);FR(0,144,SW,2,pc)
  name=TRACKS[ti][0]
  textout(G,52,150,str(ti+1)+"/"+str(len(TRACKS)),0x8090A0)
  bigtext(name,160,3 if len(name)<=9 else 2,0xFFFFFF,0x000000)
  info=("%.1f km" % (L/1000.0))+("  x3 laps" if not TRACKS[ti][1] else "  start > finish")
  ctext(info,180,0xC0D0E0)
  x=(SW-sum(len(f[0])*7+10 for f in feats))//2
  for f,c in feats:
    w=len(f)*7+6;FR(x,194,w,12,c);textout(G,x+3,194,f,0xFFFFFF);x+=w+4
  textout(G,8,214,"BEST",0x8090A0);textout(G,8,226,fmt(BEST[ti]),0xFFE060)
  #arrows + race button
  for b,d in ((MB_L,-1),(MB_R,1)):
    x,y,w,h=b;FR(x,y,w,h,0x203040)
    cx=x+w//2;cy=y+h//2
    poly([(cx+10*d,cy),(cx-6*d,cy-12),(cx-6*d,cy+12)],0xFFFFFF)
  x,y,w,h=MB_GO
  gc=mix(0x2E7D32,0x60FF80,0.5+0.5*sin(t*5))
  FR(x+2,y+2,w,h,0x000000);FR(x,y,w,h,gc);textout(G,x+30,y+8,"RACE!",0xFFFFFF)
  textout(G,222,214,"< > pick",0x8090A0);textout(G,222,226,"Enter race",0x8090A0)

def title():
  ti=TSEL[0];built=-1
  t0=ticks();last=t0;gi=1;gs=0.0
  while keyboard() or touches():
    pass
  prevk=0
  while True:
    if built!=ti:
      try:
        build(ti)
      except MemoryError:
        FR(0,100,SW,40,0x400000);ctext("Not enough memory for this track",112,0xFFFFFF);flip()
        gc.collect();ti=(ti+1)%len(TRACKS);continue
      built=ti;gi=2 if CLOSED else 1;gs=0.0
      place(gi);CAR.v=32.0
    now=ticks();dt=min(0.1,(now-last)/1000.0);last=now;t=(now-t0)/1000.0
    #ghost car flies along the track
    gs+=32.0*dt
    while gs>SL[gi]:
      gs-=SL[gi];gi+=1
      if CLOSED:gi%=N
      elif gi>=N-3:gi=1;gs=0.0;place(1)
      if GAP[gi]:gi+=1
    P,T,U,R=frameAt(gi,min(1.0,gs/SL[gi]))
    CAR.pos=P;CAR.fwd=T;CAR.up=U;CAR.mode=0;CAR.i=gi;CAR.v=32.0
    camera(dt)
    #swing the camera out to the side a little for a nicer view
    CAM[0]=vadd(CAM[0],vmul(vcross(CAR.cu,CAR.cf),sin(t*0.6)*3.0*dt))
    background();renderTrack(gi);drawCar()
    menuCard(ti,t)
    flip()
    k=keyboard();pk=k&~prevk;prevk=k
    if kd(pk,K_ESC):return -1
    if kd(pk,K_ENTER):TSEL[0]=ti;return ti
    if kd(pk,K_LT):ti=(ti-1)%len(TRACKS)
    if kd(pk,K_RT):ti=(ti+1)%len(TRACKS)
    for n,kk in enumerate([K_1,K_2,K_3,K_4,K_5,K_6,K_7,K_8]):
      if kd(pk,kk) and n<len(TRACKS):ti=n
    p=touches()
    if p:
      while touches():
        pass
      if inside(MB_L,p):ti=(ti-1)%len(TRACKS)
      elif inside(MB_R,p):ti=(ti+1)%len(TRACKS)
      elif inside(MB_GO,p):TSEL[0]=ti;return ti
      elif inside(MB_Q,p):return -1
      last=ticks()

def resultScreen():
  t,bl,nb=RACE.result
  FR(30,28,260,208,0x10202C)
  FR(30,28,260,4,0xFF7043)
  bigtext("FINISH",40,5,0xFFFFFF,0x000000)
  ctext("TIME  "+fmt(t),80,0xFFFF60)
  y=100
  if CLOSED:
    ctext("BEST LAP  "+fmt(bl),y,0xFFFFFF);y+=20
    for i in range(len(RACE.laps)):
      ctext("lap "+str(i+1)+"   "+fmt(RACE.laps[i]),y,0xB0C4D0);y+=14
  else:
    ctext(TNAME,y,0xFFFFFF);y+=18
    ctext("resets: "+str(RACE.resets),y,0xB0C4D0);y+=16
    ctext("drift points: "+str(int(RACE.dpts)),y,0xFFB040);y+=16
  if nb:ctext("NEW TRACK RECORD!",y+4,0x40FF60)
  menuButton(RB1,"RETRY","Enter",0x2E7D32)
  menuButton(RB2,"MENU","Esc",0x6A4C93)
  flip()
  return waitTap([RB1,RB2],[K_ENTER,K_ESC])

def main():
  dimgrob(G,SW,SH,0)
  loadBest()
  while True:
    c=title()
    if c<0:return
    while True:
      RACE.result=None
      race(c)
      if RACE.result is None:break
      if resultScreen()==1:break

main()
