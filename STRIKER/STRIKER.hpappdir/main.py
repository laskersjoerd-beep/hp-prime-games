#STRIKER - an original combined-arms battle game for the HP Prime
#Drive a tank or fly a plane. Two teams of bot tanks and bot planes fight
#over capture point A. Destroy enemies and hold A to drain their tickets.
#Python app (hpprime module). Touch icon dashboard + keyboard.
from hpprime import *
from math import *
from array import array
import gc

try:
  ticks()
except:
  def ticks():
    return int(eval("TICKS()"))

_rs=[1]
def seed(s):
  _rs[0]=(s&0x7fffffff) or 1
def rnd():
  _rs[0]=(_rs[0]*1103515245+12345)&0x7fffffff
  return _rs[0]/2147483648.0

G=1;SW=320;SH=240;VB=187
CX=160;CY=88
NEAR=0.5
K_UP=2;K_DN=12;K_LT=7;K_RT=8;K_ESC=4;K_ENTER=30;K_MENU=13;K_DEL=19
K_PLUS=50;K_MINUS=45;K_0=47;K_2=43;K_4=37;K_6=39;K_8=33;K_7=32;K_9=34

#---------- drawing helpers ----------
def I(v):
  if v>3000:return 3000
  if v<-3000:return -3000
  return int(v)
def FR(x,y,w,h,c):
  if w<=0 or h<=0:return
  x0=int(x);y0=int(y);x1=int(x+w);y1=int(y+h)
  if x1==x0:x1=x0+1
  if y1==y0:y1=y0+1
  if x0<0:x0=0
  if y0<0:y0=0
  if x1>SW:x1=SW
  if y1>SH:y1=SH
  if x1>x0 and y1>y0:fillrect(G,x0,y0,x1-x0,y1-y0,c,c)
def poly(p,c):
  fillpoly(G,[(I(v[0]),I(v[1])) for v in p],c)
def L(x1,y1,x2,y2,c):
  line(G,I(x1),I(y1),I(x2),I(y2),c)
def T(x,y,s,c):
  textout(G,int(x),int(y),s,c)
def ctext(s,y,c):
  textout(G,(SW-len(s)*6)//2,y,s,c)
def shade(c,f):
  if f>1:f=1
  if f<0:f=0
  return (int(((c>>16)&255)*f)<<16)|(int(((c>>8)&255)*f)<<8)|int((c&255)*f)
def mix(c,d,t):
  if t<=0:return c
  if t>1:t=1
  u=1-t
  return (int(((c>>16)&255)*u+((d>>16)&255)*t)<<16)|(int(((c>>8)&255)*u+((d>>8)&255)*t)<<8)|int((c&255)*u+(d&255)*t)
def disc(x,y,r,c,n=10):
  p=[]
  for i in range(n):
    a=6.2832*i/n;p.append((x+r*cos(a),y+r*sin(a)))
  poly(p,c)
SEGS=("abcdef","bc","abged","abgcd","fgbc","afgcd","afgedc","abc","abcdefg","abcdfg")
def digits(cx,cy,hgt,s,c):
  w=hgt*0.55;t=max(1,hgt*0.16);gap=w*0.35;n=len(s)
  x0=cx-(n*w+(n-1)*gap)/2;y0=cy-hgt/2;hh=hgt/2
  for ch in s:
    if ch=='-':
      FR(x0,y0+hh-t/2,w,t,c);x0+=w+gap;continue
    for g in SEGS[ord(ch)-48]:
      if g=='a':FR(x0,y0,w,t,c)
      elif g=='b':FR(x0+w-t,y0,t,hh+t/2,c)
      elif g=='c':FR(x0+w-t,y0+hh-t/2,t,hh+t/2,c)
      elif g=='d':FR(x0,y0+hgt-t,w,t,c)
      elif g=='e':FR(x0,y0+hh-t/2,t,hh+t/2,c)
      elif g=='f':FR(x0,y0,t,hh+t/2,c)
      else:FR(x0,y0+hh-t/2,w,t,c)
    x0+=w+gap
FONT={
'S':"0111110000011100000111110",'T':"1111100100001000010000100",
'R':"1111010001111101001010001",'I':"1111100100001000010011111",
'K':"1000110010111001001010001",'E':"1111110000111101000011111"}
def bigtext(s,y,sz,c,sh=0):
  x0=(SW-len(s)*6*sz)//2
  for n in range(len(s)):
    b=FONT.get(s[n])
    if not b:continue
    for i in range(25):
      if b[i]=='1':
        if sh:FR(x0+n*6*sz+(i%5)*sz+2,y+(i//5)*sz+2,sz,sz,sh)
        FR(x0+n*6*sz+(i%5)*sz,y+(i//5)*sz,sz,sz,c)

#---------- input ----------
def kd(k,b):
  return (k>>b)&1
def touches():
  pts=[]
  try:
    m=mouse()
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
def release():
  while keyboard() or touches():
    pass

#---------- maps ----------
NG=27;CS=40.0;MAPW=(NG-1)*CS
H=array('f',[0.0]*(NG*NG))
CC=[0]*((NG-1)*(NG-1))
ZX=520.0;ZZ=520.0;ZR=40.0
#name, grass a, grass b, field a, field b, dirt, rock, sand, water, sky, haze, far ground, tree, house walls
MAPS=[
 ("Green Valley",0x5E8A3C,0x547E36,0xB8A852,0x7E9A44,0x8A7452,0x7E7A74,0xC8B88A,0x3C78B4,0x8EC0EA,0xC4D8E6,0x7A9A70,0x2E5A2A,(0xE8E0D0,0xD8C8A8,0xC8B8A0)),
 ("Dust Ridge",0xC8A86A,0xBC9C60,0xD8C08A,0xB89A5E,0xA8885A,0x9A7E62,0xE2CC96,0x4A86A8,0xA8C8E0,0xE6DCC8,0xC4AE84,0x6A7A3A,(0xE0D2B4,0xD0BC94,0xC8A880))]
MI=[0]
TREES=[];HOUSES=[]
def Hget(i,j):
  return H[j*NG+i]
def hAt(x,z):
  fx=x/CS;fz=z/CS
  if fx<0:fx=0.0
  if fz<0:fz=0.0
  if fx>NG-1.001:fx=NG-1.001
  if fz>NG-1.001:fz=NG-1.001
  i=int(fx);j=int(fz);u=fx-i;w=fz-j;b=j*NG+i
  h0=H[b]+(H[b+1]-H[b])*u;h1=H[b+NG]+(H[b+NG+1]-H[b+NG])*u
  return h0+(h1-h0)*w
def gAt(x,z):
  #drawn ground height (water surface is flat at 0)
  h=hAt(x,z)
  return h if h>0 else 0.0

def genMap(mi):
  global TREES,HOUSES
  M=MAPS[mi];seed(mi*977+13)
  p1=rnd()*6;p2=rnd()*6;p3=rnd()*6
  for j in range(NG):
    for i in range(NG):
      x=i*CS;z=j*CS;dx=(x-ZX)/520;dz=(z-ZZ)/520
      h=7*sin(x*0.011+p1)*cos(z*0.009+p2)+4*sin(x*0.023+z*0.017+p3)+6
      h+=46*max(0.0,abs(dx)-0.5)**1.5*2.2
      h+=30*max(0.0,abs(dz)-0.75)
      r=sqrt(dx*dx+dz*dz)
      if r<0.28:h=h*(r/0.28)+3*(1-r/0.28)
      if mi==0:
        h-=16*exp(-((x-250)**2+(z-650)**2)/(110.0**2))
        h-=9*exp(-((x-760)**2+(z-330)**2)/(70.0**2))
      else:
        h+=9*max(0.0,sin(x*0.02+z*0.006+p1))**2
        h-=10*exp(-((x-700)**2+(z-700)**2)/(60.0**2))
      H[j*NG+i]=h
  # cell colours with simple lighting
  for j in range(NG-1):
    for i in range(NG-1):
      a=H[j*NG+i];b=H[j*NG+i+1];c=H[(j+1)*NG+i];d=H[(j+1)*NG+i+1]
      avg=(a+b+c+d)/4;sl=(max(a,b,c,d)-min(a,b,c,d))/CS
      x=(i+0.5)*CS;z=(j+0.5)*CS
      if avg<0.2:col=M[8]
      elif avg<1.4:col=M[7]
      elif sl>0.42:col=M[6]
      elif (x-ZX)**2+(z-ZZ)**2<150**2:col=M[5] if (i+j)%3==0 else M[1]
      elif sl<0.12 and ((i//2+j//3)%4==1):col=M[3] if (i+j)&1 else M[4]
      else:col=M[1] if (i+j)&1 else M[2]
      nx=((a+c)-(b+d))/(2*CS);nz=((a+b)-(c+d))/(2*CS)
      lt=0.86+0.9*(nx*0.6+nz*0.35)
      CC[j*(NG-1)+i]=shade(col,max(0.55,min(1.12,lt))) if lt<=1 else mix(col,0xFFFFFF,(lt-1)*0.8)
  # trees in forests
  TREES=[]
  n=0
  while len(TREES)<110 and n<4000:
    n+=1
    x=40+rnd()*(MAPW-80);z=40+rnd()*(MAPW-80)
    h=hAt(x,z)
    if h<2 or (x-ZX)**2+(z-ZZ)**2<170**2:continue
    if z<170 or z>MAPW-170:
      if abs(x-ZX)<180:continue
    f=sin(x*0.013+p2)*cos(z*0.011+p1)
    if f<0.25 and rnd()>0.08:continue
    TREES.append((x,h,z,6+rnd()*5))
  # village around point A
  HOUSES=[]
  for k in range(11):
    a=k*0.571+rnd()*0.25;r=62+rnd()*55
    x=ZX+sin(a)*r;z=ZZ+cos(a)*r
    hw=3+rnd()*2;hl=4+rnd()*3;hh=3+rnd()*2.5
    HOUSES.append((x,hAt(x,z),z,a,hw,hl,hh,M[13][k%3],(0x9A3A2A,0x5A5E66,0x7A4A2A)[k%3]))
  gc.collect()

#---------- vehicles ----------
TANK=0;PLANE=1
class V:
  pass
VEH=[]
TK=[25,25]          #tickets
ZONE=[0.0,-1]       #capture progress -1 (red) .. 1 (blue), owner (-1 none, 0 blue, 1 red)
DIFF=[1]
AIMERR=(0.011,0.0065,0.0035)
NAMES=(("Bastion","Swift"),("Warden","Talon"))
def newVeh(team,kind,idx):
  v=V();v.team=team;v.kind=kind;v.idx=idx;v.kills=0;v.deaths=0
  v.bot=1;spawn(v);return v
def spawn(v):
  side=1 if v.team==0 else -1
  bz=90.0 if v.team==0 else MAPW-90
  v.alive=1;v.dead=0.0;v.rel=0.0;v.rel2=0.0;v.think=rnd()*0.3;v.stuck=0.0;v.rev=0.0
  v.tgt=None;v.lx=0;v.lz=0;v.vx=0.0;v.vy=0.0;v.vz=0.0;v.hitT=0.0;v.burst=0.0
  off=(v.idx-2)*22.0
  if v.kind==TANK:
    v.x=ZX+off;v.z=bz;v.yaw=0.0 if side>0 else pi
    for k in range(12):
      if not blocked(v.x,v.z,v):break
      v.x+=9.0 if k&1 else -9.0*(k+1)
    v.y=hAt(v.x,v.z)
    v.hp=100.0;v.sp=0.0;v.ty=v.yaw;v.gp=0.0;v.mgp=0.0;v.pit=0.0;v.ammo=40;v.ammo2=600
  else:
    v.x=ZX+off*2;v.z=bz-side*60;v.yaw=0.0 if side>0 else pi;v.y=hAt(v.x,v.z)+230
    v.hp=50.0;v.sp=95.0;v.pit=0.0;v.roll=0.0;v.thr=0.75;v.ammo=500;v.ammo2=2
  v.lx=v.x;v.lz=v.z
def fwd(v):
  cp=cos(v.pit)
  return (sin(v.yaw)*cp,sin(v.pit),cos(v.yaw)*cp)

PR=[]   #projectiles [x,y,z,vx,vy,vz,team,kind 0 shell/1 bullet/2 bomb,life,owner]
FX=[]   #effects [x,y,z,t,kind 0 blast/1 smoke/2 spark,size]
MSG=[]  #[text,time,colour]
def say(s,c=0xFFFFFF,t=3.0):
  MSG.insert(0,[s,t,c])
  if len(MSG)>3:MSG.pop()

def los(a,b):
  #terrain line of sight between two vehicles
  ax=a.x;ay=a.y+2.5;az=a.z;bx=b.x;by=b.y+2.0;bz=b.z
  for k in range(1,8):
    t=k/8.0;x=ax+(bx-ax)*t;z=az+(bz-az)*t;y=ay+(by-ay)*t
    if y<hAt(x,z)+0.5:return 0
  return 1

def blocked(x,z,me):
  if x<8 or z<8 or x>MAPW-8 or z>MAPW-8:return 1
  if hAt(x,z)<-1.2:return 1
  for hs in HOUSES:
    dx=x-hs[0];dz=z-hs[2]
    if dx*dx+dz*dz<(max(hs[4],hs[5])+2.4)**2:return 1
  for t in TREES:
    dx=x-t[0];dz=z-t[2]
    if dx*dx+dz*dz<4.0:return 1
  for o in VEH:
    if o is me or not o.alive or o.kind!=TANK:continue
    dx=x-o.x;dz=z-o.z
    if dx*dx+dz*dz<20.0:return 1
  return 0

SHELLV=330.0;BULLV=650.0;GRAV=9.81
def fireShell(v):
  cy=cos(v.gp);d=(sin(v.ty)*cy,sin(v.gp),cos(v.ty)*cy)
  x=v.x+d[0]*4.6;y=v.y+2.0+d[1]*4.6;z=v.z+d[2]*4.6
  PR.append([x,y,z,d[0]*SHELLV,d[1]*SHELLV,d[2]*SHELLV,v.team,0,3.5,v])
  FX.append([x,y,z,0.0,2,1.6])
def fireMG(v):
  cy=cos(v.mgp);d=(sin(v.ty)*cy,sin(v.mgp),cos(v.ty)*cy)
  e=(rnd()-0.5)*0.02
  PR.append([v.x,v.y+3.0,v.z,(d[0]+e)*BULLV,(d[1]+e)*BULLV,(d[2]-e)*BULLV,v.team,1,1.0,v])
def fireGuns(v):
  f=fwd(v);s=0.012
  side=2.2 if int(v.rel2*1000)&1 else -2.2
  r=(cos(v.yaw),0,-sin(v.yaw))
  x=v.x+r[0]*side+f[0]*3;y=v.y+f[1]*3;z=v.z+r[2]*side+f[2]*3
  sp=v.sp+BULLV
  PR.append([x,y,z,f[0]*sp+(rnd()-0.5)*s*sp,f[1]*sp+(rnd()-0.5)*s*sp,f[2]*sp+(rnd()-0.5)*s*sp,v.team,1,1.1,v])
def dropBomb(v):
  f=fwd(v)
  PR.append([v.x,v.y-1.5,v.z,f[0]*v.sp,f[1]*v.sp,f[2]*v.sp,v.team,2,20.0,v])

def damage(v,dmg,src):
  if not v.alive:return
  v.hp-=dmg;v.hitT=0.3
  if v.hp<=0:kill(v,src)
def kill(v,src,why=''):
  v.alive=0;v.dead=0.0;v.hp=0;v.deaths+=1
  TK[v.team]=max(0,TK[v.team]-1)
  FX.append([v.x,v.y+1.5,v.z,0.0,0,9.0 if v.kind==TANK else 7.0])
  nm=('Blue ' if v.team==0 else 'Red ')+NAMES[v.team][v.kind]
  if v is VEH[0]:nm='You'
  if src is not None and src is not v:
    src.kills+=1
    sn='You' if src is VEH[0] else (('Blue ' if src.team==0 else 'Red ')+NAMES[src.team][src.kind])
    say(sn+' destroyed '+nm+why,0x80C0FF if src.team==0 else 0xFF8080)
  else:
    say(nm+' crashed' if v.kind==PLANE else nm+' destroyed',0xC0C0C0)
  if v.kind==PLANE:
    v.vy=-8.0

def hitTank(v,p,src):
  #armour: front plate is strong, sides weaker, rear weakest
  sp=sqrt(p[3]*p[3]+p[4]*p[4]+p[5]*p[5])+1e-6
  d=(p[3]*sin(v.yaw)+p[5]*cos(v.yaw))/sp
  if p[7]==0:
    base=30 if d<-0.55 else (52 if d<0.45 else 72)
    if rnd()<0.07:
      damage(v,999,src)
      return
    damage(v,base+rnd()*14,src)
  elif p[7]==1:
    damage(v,1.6 if p[4]<-60 else 0.3,src)

def stepProjectiles(dt):
  i=0
  while i<len(PR):
    p=PR[i];p[8]-=dt
    x0=p[0];y0=p[1];z0=p[2]
    if p[7]!=1:p[4]-=GRAV*dt
    else:p[4]-=GRAV*0.3*dt
    p[0]+=p[3]*dt;p[1]+=p[4]*dt;p[2]+=p[5]*dt
    dx=p[0]-x0;dy=p[1]-y0;dz=p[2]-z0;ll=dx*dx+dy*dy+dz*dz+1e-9
    hit=0
    for v in VEH:
      if not v.alive or v.team==p[6]:continue
      cy=v.y+(1.3 if v.kind==TANK else 0.0);r=2.7 if v.kind==TANK else 4.6
      ex=v.x-x0;ey=cy-y0;ez=v.z-z0
      t=(ex*dx+ey*dy+ez*dz)/ll
      if t<0:t=0.0
      if t>1:t=1.0
      qx=ex-dx*t;qy=ey-dy*t;qz=ez-dz*t
      if qx*qx+qy*qy+qz*qz<r*r:
        src=p[9]
        if v.kind==TANK:hitTank(v,p,src)
        else:damage(v,100 if p[7]==0 else (5.5 if p[7]==1 else 100),src)
        FX.append([x0+dx*t,y0+dy*t,z0+dz*t,0.0,2,1.2 if p[7]==1 else 3.0])
        if p[7]==2:explode(p)
        hit=1;break
    if not hit:
      g=gAt(p[0],p[2])
      if p[1]<g:
        hit=1
        if p[7]==2:explode(p)
        elif p[7]==0:FX.append([p[0],g,p[2],0.0,0,3.0])
        else:
          if rnd()<0.3:FX.append([p[0],g,p[2],0.0,2,0.8])
      elif p[8]<=0:hit=1
    if hit:PR.pop(i)
    else:i+=1
def explode(p):
  x=p[0];z=p[2];y=gAt(x,z)
  FX.append([x,y,z,0.0,0,14.0])
  for v in VEH:
    if not v.alive or v.team==p[6]:continue
    d=sqrt((v.x-x)**2+(v.y-y)**2+(v.z-z)**2)
    if d<16:damage(v,120*(1-d/16)+10,p[9])

#---------- physics ----------
def tankStep(v,dt,thr,steer,aimY,aimP,fire,fire2):
  v.rel-=dt;v.rel2-=dt
  mx=11.0 if thr>=0 else 4.0
  v.sp+=(thr*mx-v.sp)*min(1,dt*1.2)
  v.yaw+=steer*0.75*dt
  f0=sin(v.yaw);f1=cos(v.yaw)
  nx=v.x+f0*v.sp*dt;nz=v.z+f1*v.sp*dt
  if blocked(nx,nz,v):
    v.sp=0.0
  else:
    v.x=nx;v.z=nz
  v.y=hAt(v.x,v.z)
  if v.y<-0.3:v.y=-0.3
  v.pit=atan2(hAt(v.x+f0*2.5,v.z+f1*2.5)-hAt(v.x-f0*2.5,v.z-f1*2.5),5.0)
  d=aimY-v.ty
  while d>pi:d-=2*pi
  while d<-pi:d+=2*pi
  st=0.9*dt
  v.ty+=max(-st,min(st,d))
  tp=max(-0.12,min(0.35,aimP))
  v.gp+=max(-0.5*dt,min(0.5*dt,tp-v.gp))
  mp=max(-0.1,min(1.25,aimP))
  v.mgp+=max(-2*dt,min(2*dt,mp-v.mgp))
  if fire and v.rel<=0 and v.ammo>0:
    v.rel=4.2 if v is VEH[0] else 5.2;v.ammo-=1;fireShell(v)
  if fire2 and v.rel2<=0 and v.ammo2>0:
    v.rel2=0.09;v.ammo2-=1;fireMG(v)

def planeStep(v,dt,pin,rin,fire,fire2):
  v.rel-=dt;v.rel2-=dt
  tr=rin*1.15
  v.roll+=(tr-v.roll)*min(1,dt*3.0)
  v.yaw+=GRAV*tan(max(-1.2,min(1.2,v.roll)))/max(v.sp,35)*dt*1.6
  v.pit+=pin*0.85*dt*cos(v.roll)
  if v.sp<40:v.pit-=(40-v.sp)*0.03*dt
  v.pit=max(-1.25,min(1.25,v.pit))
  tgt=60+80*v.thr
  v.sp+=(tgt-v.sp)*0.35*dt-GRAV*sin(v.pit)*dt*0.9
  v.sp=max(28.0,min(175.0,v.sp))
  f=fwd(v)
  v.x+=f[0]*v.sp*dt;v.y+=f[1]*v.sp*dt;v.z+=f[2]*v.sp*dt
  if v.y>900:v.y=900.0
  #keep inside the battle area
  if v.x<-150 or v.x>MAPW+150 or v.z<-150 or v.z>MAPW+150:
    a=atan2(ZX-v.x,ZZ-v.z)-v.yaw
    while a>pi:a-=2*pi
    while a<-pi:a+=2*pi
    v.yaw+=max(-0.8*dt,min(0.8*dt,a))
  if v.y<gAt(v.x,v.z)+1.5:
    v.y=gAt(v.x,v.z)+1.5;kill(v,None)
    return
  for hs in HOUSES:
    if abs(v.x-hs[0])<hs[5]+1 and abs(v.z-hs[2])<hs[5]+1 and v.y<hs[1]+hs[6]*2:
      kill(v,None);return
  if fire and v.rel<=0 and v.ammo>0:
    v.rel=0.075;v.ammo-=1;v.rel2+=0.0005;fireGuns(v)
  if fire2 and v.ammo2>0 and v.rel2<=0:
    v.ammo2-=1;v.rel2=0.6;dropBomb(v)

#---------- bot AI ----------
def angd(a,b):
  d=a-b
  while d>pi:d-=2*pi
  while d<-pi:d+=2*pi
  return d
def aimAt(v,t,spd,grav):
  #lead + drop compensation: returns yaw, pitch
  dx=t.x-v.x;dz=t.z-v.z;dy=(t.y+(1.2 if t.kind==TANK else 0))-(v.y+2.0)
  dh=sqrt(dx*dx+dz*dz)+0.01;tt=sqrt(dh*dh+dy*dy)/spd
  tv=t.sp if t.kind==TANK else t.sp
  f=fwd(t) if t.kind==PLANE else (sin(t.yaw),0,cos(t.yaw))
  dx+=f[0]*tv*tt;dz+=f[2]*tv*tt;dy+=f[1]*tv*tt
  dh=sqrt(dx*dx+dz*dz)+0.01
  return atan2(dx,dz),atan2(dy+0.5*grav*tt*tt,dh)

def tankBot(v,dt):
  v.think-=dt
  if v.think<=0:
    v.think=0.35
    best=None;bd=1e9;bp=None;bpd=1e9
    for o in VEH:
      if not o.alive or o.team==v.team:continue
      d=(o.x-v.x)**2+(o.z-v.z)**2
      if o.kind==TANK:
        if d<760**2 and d<bd and los(v,o):best=o;bd=d
      else:
        if d<320**2 and o.y-v.y<260 and d<bpd:bp=o;bpd=d
    v.tgt=best;v.atgt=bp
    #movement goal
    own=ZONE[1]==v.team and abs(ZONE[0])>0.99
    if not own:gx=ZX+(v.idx-2)*12;gz=ZZ+(v.idx%2)*10-5
    elif best:gx=best.x;gz=best.z
    else:gx=ZX+(v.idx-2)*15;gz=ZZ+(70 if v.team==1 else -70)
    v.gx=gx;v.gz=gz
    #stuck detection
    mv=(v.x-v.lx)**2+(v.z-v.lz)**2
    if v.wantmove and mv<1.0:v.stuck+=0.35
    else:v.stuck=0.0
    v.lx=v.x;v.lz=v.z
    if v.stuck>2.0:v.rev=1.6;v.stuck=0.0
  thr=0.0;steer=0.0
  t=v.tgt
  dist_goal=sqrt((v.gx-v.x)**2+(v.gz-v.z)**2)
  engage=t is not None and (t.x-v.x)**2+(t.z-v.z)**2<520**2
  v.wantmove=0
  if v.rev>0:
    v.rev-=dt;thr=-0.8;steer=0.8 if v.idx&1 else -0.8;v.wantmove=1
  elif not engage and dist_goal>14:
    a=angd(atan2(v.gx-v.x,v.gz-v.z),v.yaw)
    steer=max(-1,min(1,a*2.2));thr=1.0 if abs(a)<0.7 else 0.25;v.wantmove=1
  elif engage:
    #advance while reloading, stop to take the shot
    if v.rel>1.2 and dist_goal>14:
      a=angd(atan2(v.gx-v.x,v.gz-v.z),v.yaw)
      steer=max(-1,min(1,a*2.2));thr=0.6 if abs(a)<0.7 else 0.2;v.wantmove=1
  ay=v.ty;ap=v.gp;fire=0;fire2=0
  if t:
    ay,ap=aimAt(v,t,SHELLV,GRAV)
    e=AIMERR[DIFF[0]]*(1+sqrt((t.x-v.x)**2+(t.z-v.z)**2)/600)
    ay+=sin(v.think*7+v.idx)*e;ap+=cos(v.think*5+v.idx)*e*0.5
    if abs(angd(ay,v.ty))<0.02 and abs(ap-v.gp)<0.012 and engage:fire=1
  if v.atgt:
    my,mp=aimAt(v,v.atgt,BULLV,GRAV*0.3)
    if not t:ay=my
    if abs(angd(my,v.ty))<0.25:
      v.burst-=dt
      if v.burst<-1.2:v.burst=1.0
      fire2=v.burst>0
    mpp=mp
  else:mpp=ap
  tankStep(v,dt,thr,steer,ay,ap,fire,0)
  v.mgp=max(-0.1,min(1.25,mpp)) if v.atgt else v.mgp
  if fire2 and v.rel2<=0 and v.ammo2>0:
    v.rel2=0.12;v.ammo2-=1;fireMG(v)

def planeBot(v,dt):
  v.think-=dt
  if v.think<=0:
    v.think=0.25
    best=None;bd=1e9
    for o in VEH:
      if not o.alive or o.team==v.team:continue
      d=(o.x-v.x)**2+(o.z-v.z)**2+(o.y-v.y)**2
      if o.kind==TANK:d=d*2.5+250000
      if d<bd:best=o;bd=d
    v.tgt=best
  t=v.tgt;pin=0.0;rin=0.0;fire=0;fire2=0
  gh=gAt(v.x,v.z);f=fwd(v)
  ahead=gAt(v.x+f[0]*250,v.z+f[2]*250)
  alt=v.y-max(gh,ahead)
  v.thr=0.9
  if t and t.alive:
    tx=t.x;ty=t.y;tz=t.z
    dist=sqrt((tx-v.x)**2+(ty-v.y)**2+(tz-v.z)**2)+0.1
    tt=dist/(BULLV+v.sp)
    if t.kind==PLANE:
      tf_=fwd(t);tx+=tf_[0]*t.sp*tt;ty+=tf_[1]*t.sp*tt;tz+=tf_[2]*t.sp*tt
    else:
      tx+=sin(t.yaw)*t.sp*tt;tz+=cos(t.yaw)*t.sp*tt
      dh=sqrt((tx-v.x)**2+(tz-v.z)**2)
      if dh>900 or (v.attack==0 and dh>350):
        ty=max(ty+220,v.y) if dh>600 else ty+170
        v.attack=0
      if dh<620 and v.y-t.y>140:v.attack=1
      if v.attack and (v.y-t.y<75 or dh<90):v.attack=0;v.climb=3.0
    if v.climb>0:
      v.climb-=dt;dy=1.0;dyaw=angd(atan2(ZX-v.x,ZZ-v.z),v.yaw)*0.3
    else:
      dyaw=angd(atan2(tx-v.x,tz-v.z),v.yaw)
      dy=atan2(ty-v.y,sqrt((tx-v.x)**2+(tz-v.z)**2)+0.1)
    rin=max(-1,min(1,dyaw*2.2))
    pin=max(-1,min(1,(max(-0.9,min(0.7,dy))-v.pit)*2.5))
    cosang=(f[0]*(tx-v.x)+f[1]*(ty-v.y)+f[2]*(tz-v.z))/sqrt((tx-v.x)**2+(ty-v.y)**2+(tz-v.z)**2+0.1)
    lim=0.996 if DIFF[0]==0 else (0.997 if DIFF[0]==1 else 0.998)
    if cosang>lim-0.004*(1 if t.kind==TANK else 0) and dist<650:fire=1
    if t.kind==TANK and v.ammo2>0:
      fall=sqrt(max(0.0,2*(v.y-t.y)/GRAV))
      ix=v.x+f[0]*v.sp*fall;iz=v.z+f[2]*v.sp*fall
      if (ix-t.x)**2+(iz-t.z)**2<16**2:fire2=1
  else:
    rin=0.4
  if alt<70 or v.y<gh+60:
    pin=1.0;rin*=0.3
  planeStep(v,dt,pin,rin,fire,fire2)

#---------- camera ----------
CAM=[0.0,0.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0]
FZ=[150.0]
def setCam(x,y,z,yaw,pit,roll,f):
  CAM[0]=x;CAM[1]=y;CAM[2]=z;CAM[3]=cos(yaw);CAM[4]=sin(yaw)
  CAM[5]=cos(pit);CAM[6]=sin(pit);CAM[7]=cos(roll);CAM[8]=sin(roll);FZ[0]=f
def tf(x,y,z):
  x-=CAM[0];y-=CAM[1];z-=CAM[2]
  x2=x*CAM[3]-z*CAM[4];z2=x*CAM[4]+z*CAM[3]
  y3=y*CAM[5]+z2*CAM[6];z3=-y*CAM[6]+z2*CAM[5]
  return (x2*CAM[7]-y3*CAM[8],x2*CAM[8]+y3*CAM[7],z3)
def rd(x,y,z):
  x2=x*CAM[3]-z*CAM[4];z2=x*CAM[4]+z*CAM[3]
  y3=y*CAM[5]+z2*CAM[6];z3=-y*CAM[6]+z2*CAM[5]
  return (x2*CAM[7]-y3*CAM[8],x2*CAM[8]+y3*CAM[7],z3)
def proj(p):
  return (CX+FZ[0]*p[0]/p[2],CY-FZ[0]*p[1]/p[2])
def poly3(P,c):
  F=FZ[0];allin=1
  for p in P:
    if p[2]<NEAR:
      allin=0;break
  if allin:
    xr=CX/F*1.1;yu=CY/F*1.1;yd=(VB-CY)/F*1.1
    l=r=u=d=1
    for p in P:
      x=p[0];y=p[1];z=p[2]
      if x>-xr*z:l=0
      if x<xr*z:r=0
      if y<yu*z:u=0
      if y>-yd*z:d=0
    if l or r or u or d:return
    pts=[(CX+F*p[0]/p[2],CY-F*p[1]/p[2]) for p in P]
    big=0
    for q in pts:
      if q[0]<-2000 or q[0]>2300 or q[1]<-2000 or q[1]>2300:big=1;break
    if not big:
      poly(pts,c);return
  else:
    Q=[];n=len(P)
    for i in range(n):
      a=P[i];b=P[(i+1)%n]
      ai=a[2]>=NEAR;bi=b[2]>=NEAR
      if ai:Q.append(a)
      if ai!=bi:
        t=(NEAR-a[2])/(b[2]-a[2])
        Q.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),NEAR))
    if len(Q)<3:return
    pts=[(CX+F*p[0]/p[2],CY-F*p[1]/p[2]) for p in Q]
  clip2(pts,c)
def clip2(pts,c):
  for ax,lim,keep in ((0,-2.0,1),(0,SW+2.0,-1),(1,-2.0,1),(1,VB+2.0,-1)):
    R=[];n=len(pts)
    if n<3:return
    for i in range(n):
      a=pts[i];b=pts[(i+1)%n]
      ai=(a[ax]-lim)*keep>=0;bi=(b[ax]-lim)*keep>=0
      if ai:R.append(a)
      if ai!=bi:
        t=(lim-a[ax])/(b[ax]-a[ax])
        R.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    pts=R
  if len(pts)>=3:poly([(int(p[0]),int(p[1])) for p in pts],c)

#---------- world rendering ----------
VR=[6]      #view radius in cells
VIEWS=(4,6,8)
def skyGround(M):
  #sky, then the far ground below the (possibly tilted) horizon
  FR(0,0,SW,VB,M[9])
  yaw=atan2(CAM[4],CAM[3])
  pts=[]
  for a in (-1.3,1.3):
    q=rd(sin(yaw+a),0.0,cos(yaw+a))
    if q[2]>0.01:pts.append(proj(q))
  down=rd(0.0,-1.0,0.0)
  if len(pts)<2:
    if down[2]>0:FR(0,0,SW,VB,M[12])
    return
  (ax,ay),(bx,by)=pts
  ux=bx-ax;uy=by-ay;l=sqrt(ux*ux+uy*uy)+1e-6;ux/=l;uy/=l
  nx=-uy;ny=ux
  g=rd(sin(yaw),-0.6,cos(yaw))
  if g[2]>0.01:
    gx,gy=proj(g)
  else:
    gx,gy=proj(down) if down[2]>0.01 else (CX,VB*3)
  if (gx-ax)*nx+(gy-ay)*ny<0:nx=-nx;ny=-ny
  K=3000
  A=(ax-ux*K,ay-uy*K);B=(bx+ux*K,by+uy*K)
  clip2([A,B,(B[0]+nx*8,B[1]+ny*8),(A[0]+nx*8,A[1]+ny*8)],M[10])
  clip2([(A[0]+nx*6,A[1]+ny*6),(B[0]+nx*6,B[1]+ny*6),(B[0]+nx*K,B[1]+ny*K),(A[0]+nx*K,A[1]+ny*K)],M[11])

def obox3(cx,cy,cz,R,U,Fv,hw,hh,hl,col):
  ex=CAM[0]-cx;ey=CAM[1]-cy;ez=CAM[2]-cz
  lr=ex*R[0]+ey*R[1]+ez*R[2];lu=ex*U[0]+ey*U[1]+ez*U[2];lf=ex*Fv[0]+ey*Fv[1]+ez*Fv[2]
  def P(a,b,e):
    return tf(cx+R[0]*a+U[0]*b+Fv[0]*e,cy+R[1]*a+U[1]*b+Fv[1]*e,cz+R[2]*a+U[2]*b+Fv[2]*e)
  if lu>hh:poly3([P(-hw,hh,-hl),P(hw,hh,-hl),P(hw,hh,hl),P(-hw,hh,hl)],col)
  elif lu<-hh:poly3([P(-hw,-hh,-hl),P(hw,-hh,-hl),P(hw,-hh,hl),P(-hw,-hh,hl)],shade(col,0.45))
  if lf>hl:poly3([P(-hw,-hh,hl),P(hw,-hh,hl),P(hw,hh,hl),P(-hw,hh,hl)],shade(col,0.85))
  elif lf<-hl:poly3([P(-hw,-hh,-hl),P(hw,-hh,-hl),P(hw,hh,-hl),P(-hw,hh,-hl)],shade(col,0.7))
  if lr>hw:poly3([P(hw,-hh,-hl),P(hw,-hh,hl),P(hw,hh,hl),P(hw,hh,-hl)],shade(col,0.75))
  elif lr<-hw:poly3([P(-hw,-hh,-hl),P(-hw,-hh,hl),P(-hw,hh,hl),P(-hw,hh,-hl)],shade(col,0.62))

def basisYP(yaw,pit):
  cp=cos(pit);sp=sin(pit);sy=sin(yaw);cy=cos(yaw)
  return (cy,0.0,-sy),(-sy*sp,cp,-cy*sp),(sy*cp,sp,cy*cp)
TCOL=((0x56663A,0x4A5832),(0x7A6E5A,0x6A5E4C))
PCOL=((0x4E6A86,0x3E5670),(0x8A5A4A,0x704838))
def drawTank(v,z,hz,fz):
  if v.alive:c1,c2=TCOL[v.team]
  else:c1=c2=0x2C2824
  c1=mix(c1,hz,fz);c2=mix(c2,hz,fz)
  R,U,Fv=basisYP(v.yaw,v.pit)
  y=v.y
  obox3(v.x,y+0.8,v.z,R,U,Fv,1.7,0.62,3.1,c1)
  if z>420:return
  R2,U2,F2=basisYP(v.ty,0.0)
  obox3(v.x-Fv[0]*0.3,y+1.85,v.z-Fv[2]*0.3,R2,U2,F2,1.0,0.45,1.35,c2)
  cg=cos(v.gp);d=(sin(v.ty)*cg,sin(v.gp),cos(v.ty)*cg)
  a=tf(v.x+d[0]*1.2,y+1.95+d[1]*1.2,v.z+d[2]*1.2);b=tf(v.x+d[0]*4.8,y+1.95+d[1]*4.8,v.z+d[2]*4.8)
  if a[2]>NEAR and b[2]>NEAR:
    pa=proj(a);pb=proj(b);w=max(1,int(FZ[0]*0.16/max(a[2],1)))
    for o in range(-(w//2),w-(w//2)):
      L(pa[0],pa[1]+o,pb[0],pb[1]+o,shade(c2,0.7))
def drawPlane(v,z,hz,fz):
  if v.alive:c1,c2=PCOL[v.team]
  else:c1=c2=0x2C2824
  c1=mix(c1,hz,fz);c2=mix(c2,hz,fz)
  F3=fwd(v);sy=sin(v.yaw);cy=cos(v.yaw);sp=sin(v.pit);cp=cos(v.pit)
  R0=(cy,0.0,-sy);U0=(-sy*sp,cp,-cy*sp)
  cr=cos(v.roll);sr=sin(v.roll)
  R=(R0[0]*cr-U0[0]*sr,R0[1]*cr-U0[1]*sr,R0[2]*cr-U0[2]*sr)
  U=(U0[0]*cr+R0[0]*sr,U0[1]*cr+R0[1]*sr,U0[2]*cr+R0[2]*sr)
  x=v.x;y=v.y;zz=v.z
  def P(a,b,e):
    return tf(x+R[0]*a+U[0]*b+F3[0]*e,y+R[1]*a+U[1]*b+F3[1]*e,zz+R[2]*a+U[2]*b+F3[2]*e)
  wing=[P(-6.0,0.0,-0.6),P(6.0,0.0,-0.6),P(5.5,0.0,0.9),P(-5.5,0.0,0.9)]
  tail=[P(-2.4,0.2,-4.3),P(2.4,0.2,-4.3),P(2.2,0.2,-3.4),P(-2.2,0.2,-3.4)]
  fin=[P(0.0,0.3,-4.5),P(0.0,2.1,-4.6),P(0.0,0.3,-3.2)]
  ey=(CAM[0]-x)*U[0]+(CAM[1]-y)*U[1]+(CAM[2]-zz)*U[2]
  wc=c2 if ey>0 else shade(c2,0.6)
  parts=[(sum(p[2] for p in wing)/4,0),(sum(p[2] for p in tail)/4,1),(sum(p[2] for p in fin)/3,2),(tf(x,y,zz)[2],3)]
  parts.sort(key=lambda q:-q[0])
  for _,k in parts:
    if k==0:poly3(wing,wc)
    elif k==1:poly3(tail,wc)
    elif k==2:poly3(fin,shade(c1,0.8))
    else:
      obox3(x,y,zz,R,U,F3,0.55,0.6,4.4,c1)
      if v.alive and z<160:
        q=P(0,0.45,1.4)
        if q[2]>NEAR:
          s=proj(q);FR(s[0]-1,s[1]-1,3,2,0x9CC8E8)

def render():
  M=MAPS[MI[0]];hz=M[10]
  skyGround(M)
  R=VR[0];cx=CAM[0];cz=CAM[2]
  alt=CAM[1]-gAt(cx,cz)
  st=1 if alt<90 else (2 if alt<400 else 3)
  maxd=R*st*CS
  ci=int(cx/CS);cj=int(cz/CS)
  i0=max(0,(ci-R*st)//st*st);i1=min(NG-1,ci+R*st+st)
  j0=max(0,(cj-R*st)//st*st);j1=min(NG-1,cj+R*st+st)
  items=[]
  TV={}
  F=FZ[0];xr=CX/F*1.25
  xs=list(range(i0,i1,st))+[i1];zs_=list(range(j0,j1,st))+[j1]
  for j in zs_:
    for i in xs:
      h=H[j*NG+i]
      TV[j*64+i]=tf(i*CS,h if h>0 else 0.0,j*CS)
  for jn in range(len(zs_)-1):
    j=zs_[jn];jj=zs_[jn+1]
    cj_=min(NG-2,(j+jj)//2)
    for inn in range(len(xs)-1):
      i=xs[inn];ii=xs[inn+1]
      a=TV[j*64+i];b=TV[j*64+ii];c=TV[jj*64+ii];d=TV[jj*64+i]
      if a[2]<NEAR and b[2]<NEAR and c[2]<NEAR and d[2]<NEAR:continue
      if a[0]>xr*a[2]+40 and b[0]>xr*b[2]+40 and c[0]>xr*c[2]+40 and d[0]>xr*d[2]+40:continue
      if a[0]<-xr*a[2]-40 and b[0]<-xr*b[2]-40 and c[0]<-xr*c[2]-40 and d[0]<-xr*d[2]-40:continue
      items.append(((a[2]+b[2]+c[2]+d[2])*0.25,0,(a,b,c,d,CC[cj_*(NG-1)+min(NG-2,(i+ii)//2)])))
  md2=(maxd+40)**2
  for t in TREES:
    dx=t[0]-cx;dz=t[2]-cz
    if dx*dx+dz*dz>min(md2,330**2):continue
    q=tf(t[0],t[1],t[2])
    if q[2]>2:items.append((q[2]-1,1,t))
  for hs in HOUSES:
    dx=hs[0]-cx;dz=hs[2]-cz
    if dx*dx+dz*dz>md2:continue
    q=tf(hs[0],hs[1],hs[2])
    if q[2]>-12:items.append((q[2],2,hs))
  q=tf(ZX,gAt(ZX,ZZ),ZZ)
  if q[2]>1:items.append((q[2],5,0))
  for v in VEH:
    if not v.alive and v.kind==PLANE and v.dead>1.0:continue
    q=tf(v.x,v.y,v.z)
    if q[2]>1.0 and q[2]<maxd+700:items.append((q[2],3,v))
  for p in PR:
    q=tf(p[0],p[1],p[2])
    if q[2]>NEAR and q[2]<1500:items.append((q[2],4,p))
  for e in FX:
    q=tf(e[0],e[1],e[2])
    if q[2]>NEAR:items.append((q[2],6,e))
  items.sort(key=lambda t:-t[0])
  for z,k,o in items:
    fz=z/maxd
    if fz>1:fz=1.0
    fz=fz*fz
    if k==0:
      poly3(o[:4],mix(o[4],hz,fz))
    elif k==1:
      x,y,zz,h=o;tc=mix(M[12],hz,fz)
      a=tf(x,y+h,zz);b=tf(x-1.8*CAM[3],y+0.8,zz+1.8*CAM[4]);c=tf(x+1.8*CAM[3],y+0.8,zz-1.8*CAM[4])
      poly3([a,b,c],tc)
      if z<160:
        a=tf(x,y+h*1.25,zz);b=tf(x-1.2*CAM[3],y+h*0.55,zz+1.2*CAM[4]);c=tf(x+1.2*CAM[3],y+h*0.55,zz-1.2*CAM[4])
        poly3([a,b,c],shade(tc,1.1) if tc<0xE0E0E0 else tc)
    elif k==2:
      x,y,zz,a,hw,hl,hh,wc,rc=o
      R,U,Fv=basisYP(a,0.0)
      obox3(x,y+hh*0.5,zz,R,U,Fv,hw,hh*0.5,hl,mix(wc,hz,fz))
      #roof ridge along the length
      rcol=mix(rc,hz,fz)
      def P(u,v_,w):
        return tf(x+R[0]*u+Fv[0]*w,y+v_,zz+R[2]*u+Fv[2]*w)
      ex=(CAM[0]-x)*R[0]+(CAM[2]-zz)*R[2]
      s=1 if ex>0 else -1
      poly3([P(s*(hw+0.4),hh,-hl-0.3),P(s*(hw+0.4),hh,hl+0.3),P(0,hh+hw*0.8,hl+0.3),P(0,hh+hw*0.8,-hl-0.3)],shade(rcol,0.9 if s>0 else 0.75))
    elif k==3:
      if o.kind==TANK:drawTank(o,z,hz,fz*0.8)
      else:drawPlane(o,z,hz,fz*0.6)
      if not o.alive and o.kind==TANK and o.dead<30 and int(o.dead*3)%3==0:
        FX.append([o.x+rnd()-0.5,o.y+3,o.z+rnd()-0.5,0.0,1,2.0])
    elif k==4:
      a=tf(o[0],o[1],o[2]);sp=0.022 if o[7]==1 else 0.03
      b=tf(o[0]-o[3]*sp,o[1]-o[4]*sp,o[2]-o[5]*sp)
      if a[2]>NEAR and b[2]>NEAR:
        pa=proj(a);pb=proj(b)
        col=0xFFE070 if o[7]==1 else (0xFFB040 if o[7]==0 else 0x303030)
        if o[7]==2:
          s=max(2,FZ[0]*0.8/a[2]);FR(pa[0]-s/2,pa[1]-s/2,s,s,col)
        else:
          L(pa[0],pa[1],pb[0],pb[1],col)
          if o[7]==0:L(pa[0]+1,pa[1],pb[0]+1,pb[1],col)
    elif k==5:
      #capture point flag
      g=gAt(ZX,ZZ);oc=(0x3070E0,0xE03030)[ZONE[1]] if ZONE[1]>=0 else 0xE0E0E0
      a=tf(ZX,g,ZZ);b=tf(ZX,g+14,ZZ)
      if a[2]>NEAR:
        pa=proj(a);pb=proj(b);L(pa[0],pa[1],pb[0],pb[1],0x303030)
        s=FZ[0]*4.5/b[2];poly([(pb[0],pb[1]),(pb[0]+s*1.6,pb[1]+s*0.5),(pb[0],pb[1]+s)],oc)
    else:
      a=tf(o[0],o[1],o[2])
      if a[2]>NEAR:
        p=proj(a);t=o[3];sz=o[5]
        if o[4]==0:
          r=FZ[0]*sz*(0.4+t*1.6)/a[2]
          if r>0.8:disc(p[0],p[1]-r*0.3,r,0xFFC040 if t<0.25 else (0xE06020 if t<0.5 else 0x585450),8 if r>6 else 6)
        elif o[4]==1:
          r=FZ[0]*sz*(0.5+t)/a[2]
          if r>0.8:disc(p[0],p[1],r,mix(0x3A3632,hz,min(1,t*0.6)),6)
        else:
          r=max(1,FZ[0]*sz*0.5/a[2]);FR(p[0]-r,p[1]-r,2*r,2*r,0xFFF0A0)

def stepFX(dt):
  i=0
  while i<len(FX):
    e=FX[i];e[3]+=dt
    if e[4]==1:e[1]+=dt*3
    life=1.0 if e[4]==0 else (2.5 if e[4]==1 else 0.12)
    if e[3]>life:FX.pop(i)
    else:i+=1
  while len(FX)>40:FX.pop(0)

#---------- HUD / dashboard ----------
B_UP=(24,189,22,24);B_LT=(2,214,22,25);B_DN=(24,214,22,25);B_RT=(46,214,22,25)
B_FIRE=(214,189,50,50);B_ALT=(266,189,52,24);B_SCOPE=(266,215,25,24);B_MAP=(293,215,25,24)
B_THR=(184,189,26,50)
def btn(b,on,col=0x2A2E34):
  x,y,w,h=b
  FR(x,y,w,h,shade(col,1.5) if on else col);FR(x,y,w,1,0x60666E)
def icShell(x,y,c):
  FR(x-2,y-2,5,8,c);poly([(x-2,y-2),(x+3,y-2),(x+0.5,y-7)],c);FR(x-2,y+4,5,2,shade(c,0.7))
def icBullets(x,y,c):
  for k in (-5,0,5):
    FR(x+k-1,y-2,3,7,c);poly([(x+k-1,y-2),(x+k+2,y-2),(x+k+0.5,y-5)],c)
def icBomb(x,y,c):
  disc(x,y+1,4,c,8);FR(x-1,y-8,3,5,c);FR(x-3,y-8,7,2,c)
def icCross(x,y,c):
  for a in range(0,8):
    t=a*0.785;FR(x+7*cos(t)-1,y+7*sin(t)-1,2,2,c)
  FR(x-1,y-10,2,6,c);FR(x-1,y+5,2,6,c);FR(x-10,y-1,6,2,c);FR(x+5,y-1,6,2,c)
def icMap(x,y,c):
  poly([(x-9,y-6),(x-3,y-8),(x+3,y-6),(x+9,y-8),(x+9,y+6),(x+3,y+8),(x-3,y+6),(x-9,y+8)],c)
  L(x-3,y-8,x-3,y+6,0x2A2E34);L(x+3,y-6,x+3,y+8,0x2A2E34);FR(x+4,y-2,3,3,0xE03030)
def icShield(x,y,c):
  poly([(x-5,y-6),(x+5,y-6),(x+5,y),(x,y+6),(x-5,y)],c)
def icTank(x,y,s,c):
  FR(x-9*s,y-1*s,18*s,5*s,c);FR(x-5*s,y-5*s,9*s,4*s,c);FR(x+4*s,y-4*s,9*s,2*s,c)
  for k in range(-7,8,4):disc(x+k*s,y+5*s,1.6*s,shade(c,0.6),6)
def icPlane(x,y,s,c):
  poly([(x-12*s,y),(x+10*s,y-2*s),(x+13*s,y),(x+10*s,y+2*s)],c)
  poly([(x-1*s,y),(x-5*s,y-10*s),(x-2*s,y-10*s),(x+5*s,y)],c)
  poly([(x-1*s,y),(x-5*s,y+10*s),(x-2*s,y+10*s),(x+5*s,y)],c)
  poly([(x-10*s,y),(x-12*s,y-5*s),(x-9*s,y-5*s),(x-7*s,y)],c)
def arrow(b,d,c):
  x,y,w,h=b;cx=x+w/2;cy=y+h/2
  if d==0:poly([(cx,cy-6),(cx-7,cy+5),(cx+7,cy+5)],c)
  elif d==1:poly([(cx,cy+6),(cx-7,cy-5),(cx+7,cy-5)],c)
  elif d==2:poly([(cx-6,cy),(cx+5,cy-7),(cx+5,cy+7)],c)
  else:poly([(cx+6,cy),(cx-5,cy-7),(cx-5,cy+7)],c)

def dashboard(ctl):
  p=VEH[0]
  FR(0,VB,SW,SH-VB,0x3A3E44);FR(0,VB,SW,1,0x7A8088)
  btn(B_UP,ctl[0]);btn(B_DN,ctl[1]);btn(B_LT,ctl[2]);btn(B_RT,ctl[3])
  ac=0xA0FFA0
  arrow(B_UP,0,ac);arrow(B_DN,1,ac);arrow(B_LT,2,ac);arrow(B_RT,3,ac)
  #status panel
  FR(71,189,111,50,0x15181D)
  hp=max(0,p.hp)/(100.0 if p.kind==TANK else 50.0)
  icShield(80,198,0x9CB8D8)
  FR(90,195,88,6,0x2A2A2A);FR(90,195,88*hp,6,0x40D060 if hp>0.5 else (0xF0C030 if hp>0.25 else 0xF03030))
  if p.kind==TANK:
    icShell(80,214,0xF0C060)
    r=1.0-max(0.0,p.rel)/4.2
    FR(90,211,52,6,0x2A2A2A);FR(90,211,52*r,6,0x40D060 if r>=1 else 0xC09030)
    digits(162,214,9,'%02d'%min(99,p.ammo),0xF0C060)
    icBullets(80,230,0xE0E0A0)
    digits(158,230,9,'%03d'%min(999,p.ammo2),0xE0E0A0)
  else:
    icBullets(80,214,0xF0E080)
    digits(150,214,9,'%03d'%min(999,p.ammo),0xF0E080)
    icBomb(80,230,0x9AA0A8)
    digits(150,230,9,str(p.ammo2),0xC0C8D0)
  #speed / altitude / throttle
  FR(184,189,28,50,0x15181D)
  kmh=int(abs(p.sp)*3.6)
  digits(198,198,9,'%03d'%min(999,kmh) if p.kind==PLANE else '%02d'%min(99,kmh),0x60F0A0)
  if p.kind==PLANE:
    alt=int(p.y-gAt(p.x,p.z))
    poly([(186,236),(191,226),(195,231),(199,224),(205,236)],0x7A8A9A)
    digits(198,215,7,'%03d'%max(0,min(999,alt)),0x80C8FF)
    FR(207,190,4,46,0x2A2A2A);h=int(46*p.thr);FR(207,236-h,4,h,0xF09030)
  else:
    poly([(190,226),(206,226),(206,232),(190,232)],0x3A3E44)
    g='D' if p.sp>0.5 else ('R' if p.sp<-0.5 else 'N')
    T(194,222,g,0xFFFFFF)
  #big fire button and the others
  btn(B_FIRE,ctl[4],0x6A1E1E)
  disc(239,214,15,0xE04030,10);disc(239,214,10,0x6A1E1E,10);disc(239,214,5,0xFFD060,8)
  btn(B_ALT,ctl[5])
  if p.kind==TANK:icBullets(292,201,0xE0E0A0)
  else:icBomb(292,201,0xC0C8D0)
  btn(B_SCOPE,ctl[6]);icCross(278,227,0xFFFFFF)
  btn(B_MAP,ctl[7]);icMap(305,227,0xD8C890)

def topHud():
  #tickets: blue left, red right, point A in the middle
  FR(4,3,120,6,0x101418);FR(4,3,120*TK[0]/25.0,6,0x3878E8)
  FR(196,3,120,6,0x101418);w=120*TK[1]/25.0;FR(316-w,3,w,6,0xE84040)
  digits(134,6,7,'%02d'%TK[0],0x80B0FF);digits(186,6,7,'%02d'%TK[1],0xFF9090)
  oc=(0x3070E0,0xE03030)[ZONE[1]] if ZONE[1]>=0 else 0x808890
  disc(160,9,8,oc,10);disc(160,9,6,0x101418,10)
  T(157,3,'A',0xFFFFFF)
  pz=ZONE[0]
  FR(140,19,40,3,0x101418)
  if pz>0:FR(160,19,20*pz,3,0x3878E8)
  elif pz<0:FR(160+20*pz,19,-20*pz,3,0xE84040)
  y=26
  for m in MSG:
    T(160-len(m[0])*3,y,m[0],m[2]);y+=11

def markers():
  me=VEH[0]
  for v in VEH:
    if v is me or not v.alive:continue
    q=tf(v.x,v.y+(4.5 if v.kind==TANK else 3.0),v.z)
    if q[2]<2 or q[2]>1500:continue
    p=proj(q)
    if p[0]<0 or p[0]>SW or p[1]<0 or p[1]>VB:continue
    c=0x60A0FF if v.team==me.team else 0xFF4040
    if v.kind==TANK:poly([(p[0]-4,p[1]-6),(p[0]+4,p[1]-6),(p[0],p[1])],c)
    else:poly([(p[0]-5,p[1]-3),(p[0],p[1]-7),(p[0]+5,p[1]-3),(p[0],p[1])],c)
    if v.team!=me.team and q[2]<900:
      dd=int(q[2]);T(p[0]-9,p[1]-17,str(dd),0xFFB0B0) if q[2]<500 else None

def crosshair(scope):
  p=VEH[0]
  if not p.alive:return
  if p.kind==TANK:
    cg=cos(p.gp);d=(sin(p.ty)*cg,sin(p.gp),cos(p.ty)*cg)
    q=tf(p.x+d[0]*400,p.y+2+d[1]*400,p.z+d[2]*400)
    if q[2]>1:
      s=proj(q)
      if scope:
        L(s[0]-60,s[1],s[0]-8,s[1],0x101010);L(s[0]+8,s[1],s[0]+60,s[1],0x101010)
        L(s[0],s[1]+8,s[0],s[1]+50,0x101010)
        for k in (1,2,3):L(s[0]-4,s[1]+k*10,s[0]+4,s[1]+k*10,0x101010)
      else:
        c=0x40FF60 if p.rel<=0 else 0xFFB040
        L(s[0]-7,s[1],s[0]-3,s[1],c);L(s[0]+3,s[1],s[0]+7,s[1],c)
        L(s[0],s[1]-7,s[0],s[1]-3,c);L(s[0],s[1]+3,s[0],s[1]+7,c)
    FR(CX-1,CY-1,2,2,0xFFFFFF)
  else:
    f=fwd(p);q=tf(p.x+f[0]*400,p.y+f[1]*400,p.z+f[2]*400)
    if q[2]>1:
      s=proj(q);c=0x40FF60
      L(s[0]-8,s[1],s[0]-3,s[1],c);L(s[0]+3,s[1],s[0]+8,s[1],c);L(s[0],s[1]-8,s[0],s[1]-3,c)
    #lead marker on the nearest enemy plane in front
    best=None;bd=1e9
    for v in VEH:
      if v.alive and v.team!=p.team and v.kind==PLANE:
        d=(v.x-p.x)**2+(v.y-p.y)**2+(v.z-p.z)**2
        if d<bd and d<900**2:best=v;bd=d
    if best:
      tt=sqrt(bd)/(BULLV+p.sp);g=fwd(best)
      q=tf(best.x+g[0]*best.sp*tt,best.y+g[1]*best.sp*tt,best.z+g[2]*best.sp*tt)
      if q[2]>1:
        s=proj(q)
        if 0<s[0]<SW and 0<s[1]<VB:
          for a in range(8):
            t=a*0.785;FR(s[0]+5*cos(t),s[1]+5*sin(t),1,1,0xFF6040)

def minimap():
  FR(70,14,180,170,0x101418)
  s=160.0/MAPW;ox=80;oy=19
  for j in range(0,NG-1,2):
    for i in range(0,NG-1,2):
      FR(ox+i*CS*s,oy+(NG-2-j)*CS*s-CS*s,2*CS*s+1,2*CS*s+1,CC[j*(NG-1)+i])
  for hs in HOUSES:FR(ox+hs[0]*s-1,oy+160-hs[2]*s-1,3,3,0x303030)
  oc=(0x3070E0,0xE03030)[ZONE[1]] if ZONE[1]>=0 else 0xFFFFFF
  disc(ox+ZX*s,oy+160-ZZ*s,ZR*s,oc,10)
  T(ox+ZX*s-3,oy+160-ZZ*s-6,'A',0x000000)
  for v in VEH:
    if not v.alive:continue
    x=ox+v.x*s;y=oy+160-v.z*s
    c=(0x60A0FF,0xFF4040)[v.team]
    if v is VEH[0]:c=0xFFFF40
    if v.kind==TANK:FR(x-2,y-2,5,5,c)
    else:poly([(x+4*sin(v.yaw),y-4*cos(v.yaw)),(x-3*cos(v.yaw),y-3*sin(v.yaw)),(x+3*cos(v.yaw),y+3*sin(v.yaw))],c)

#---------- battle ----------
ST={}
def battleInit(mi):
  global VEH,PR,FX,MSG
  MI[0]=mi;genMap(mi)
  VEH=[];PR=[];FX=[];MSG=[]
  TK[0]=25;TK[1]=25;ZONE[0]=0.0;ZONE[1]=-1
  for team in (0,1):
    for k in range(5):
      kind=TANK if k<3 else PLANE
      v=newVeh(team,kind,k if k<3 else k-1)
      v.wantmove=0;v.gx=ZX;v.gz=ZZ;v.atgt=None;v.attack=0;v.climb=0.0
      VEH.append(v)
  ST.clear();ST.update({'t':0.0,'drain':0.0,'scope':0,'map':0,'ay':0.0,'ap':0.0,'cy':0.0,'over':0,
    'drag':None,'spawn':1,'resp':0.0,'cam':0,'ptime':0.0})
  gc.collect()

def setPlayer(kind):
  p=VEH[0];p.kind=kind;p.bot=0;p.idx=0;spawn(p)
  p.wantmove=0;p.gx=ZX;p.gz=ZZ;p.atgt=None;p.attack=0;p.climb=0.0
  ST['ay']=p.yaw;ST['ap']=0.0;ST['cy']=p.yaw;ST['scope']=0
  say('Capture point A and destroy the enemy!',0xFFFFFF)

def zoneStep(dt):
  b=r=0
  for v in VEH:
    if v.alive and v.kind==TANK and (v.x-ZX)**2+(v.z-ZZ)**2<ZR*ZR:
      if v.team==0:b+=1
      else:r+=1
  if b!=r:
    old=ZONE[1]
    ZONE[0]=max(-1.0,min(1.0,ZONE[0]+(b-r)*dt/12.0))
    if ZONE[0]>=1.0 and old!=0:ZONE[1]=0;say('Blue team captured A',0x80B0FF)
    elif ZONE[0]<=-1.0 and old!=1:ZONE[1]=1;say('Red team captured A',0xFF8080)
    elif abs(ZONE[0])<0.02:ZONE[1]=-1
  if ZONE[1]>=0 and abs(ZONE[0])>=1.0:
    ST['drain']+=dt
    if ST['drain']>6:
      ST['drain']=0.0;e=1-ZONE[1];TK[e]=max(0,TK[e]-1)

def worldStep(dt,ctl):
  ST['t']+=dt
  p=VEH[0]
  for v in VEH:
    if v.alive:
      if v is p and not ST.get('auto'):
        if v.kind==TANK:tankStep(v,dt,ctl[0],ctl[1],ST['ay'],ST['ap'],ctl[4],ctl[5])
        else:
          if ctl[8]:v.thr=max(0.0,min(1.0,v.thr+ctl[8]*dt*0.6))
          planeStep(v,dt,ctl[0],ctl[1],ctl[4],ctl[5])
      elif v.kind==TANK:tankBot(v,dt)
      else:planeBot(v,dt)
    else:
      v.dead+=dt
      if v.kind==PLANE and v.dead<6:
        v.vy-=GRAV*dt;f=fwd(v);v.x+=f[0]*v.sp*0.5*dt;v.z+=f[2]*v.sp*0.5*dt;v.y+=v.vy*dt
        if v.y<gAt(v.x,v.z):
          if v.vy<-1:FX.append([v.x,gAt(v.x,v.z),v.z,0.0,0,8.0])
          v.y=gAt(v.x,v.z);v.vy=0.0
        elif int(v.dead*8)&1:FX.append([v.x,v.y,v.z,0.0,1,1.5])
      if v is not p and v.dead>15 and TK[v.team]>0:
        spawn(v);v.wantmove=0;v.atgt=None;v.attack=0;v.climb=0.0
  stepProjectiles(dt)
  stepFX(dt)
  zoneStep(dt)
  for m in MSG:m[1]-=dt
  while MSG and MSG[-1][1]<=0:MSG.pop()

def camStep(dt):
  p=VEH[0]
  if p.kind==TANK:
    if ST['scope']:
      cg=cos(p.gp);d=(sin(p.ty)*cg,cos(p.ty)*cg)
      setCam(p.x+d[0]*1.5,p.y+2.6,p.z+d[1]*1.5,p.ty,-p.gp,0.0,520.0)
    else:
      cy=ST['ay']
      dist=11.0;ap=ST['ap']
      x=p.x-sin(cy)*dist*cos(ap);z=p.z-cos(cy)*dist*cos(ap);y=p.y+4.2-sin(ap)*dist
      y=max(y,gAt(x,z)+1.5)
      setCam(x,y,z,cy,0.22-ap,0.0,150.0)
  else:
    f=fwd(p);sr=sin(p.roll);cr=cos(p.roll)
    up=(-sin(p.yaw)*sin(p.pit),cos(p.pit),-cos(p.yaw)*sin(p.pit))
    d=16.0 if not ST['scope'] else 7.0
    x=p.x-f[0]*d+up[0]*3.5;y=p.y-f[1]*d+up[1]*3.5;z=p.z-f[2]*d+up[2]*3.5
    y=max(y,gAt(x,z)+2)
    setCam(x,y,z,p.yaw,-p.pit+0.06,p.roll,150.0)

def spawnScreen():
  #choose tank or plane
  sel=0;release();prevk=0
  while True:
    camOrbit()
    render();topHud()
    FR(30,40,260,140,0x101418);FR(30,40,260,2,0xFFD030)
    ctext('CHOOSE YOUR VEHICLE',48,0xFFD030)
    for k in (0,1):
      x=46+k*124
      FR(x,64,104,92,0x2A3A50 if sel==k else 0x1E2632)
      if sel==k:FR(x,154,104,2,0xFFD030)
      if k==0:icTank(x+52,98,2.2,0xC8D0A0)
      else:icPlane(x+52,98,2.6,0xC0D0E0)
      T(x+52-len(NAMES[0][k])*3,128,NAMES[0][k],0xFFFFFF)
      T(x+20,140,'tank' if k==0 else 'fighter-bomber',0xA0A8B0)
    ctext('Left/Right + Enter, or tap',164,0xC0C8D0)
    flip()
    k=keyboard();pk=k&~prevk;prevk=k;pts=touches()
    if kd(pk,K_LT):sel=0
    if kd(pk,K_RT):sel=1
    if kd(pk,K_ENTER):break
    if kd(pk,K_ESC):return -1
    if pts:
      if inside((46,64,104,92),pts):sel=0;break
      if inside((170,64,104,92),pts):sel=1;break
  release()
  return sel

CO=[0.0]
def camOrbit():
  CO[0]+=0.01
  a=CO[0];setCam(ZX-sin(a)*260,gAt(ZX,ZZ)+90,ZZ-cos(a)*260,a,0.3,0.0,150.0)

def flip():
  strblit(0,0,0,SW,SH,G)

def play(mi):
  battleInit(mi)
  k=spawnScreen()
  if k<0:return
  setPlayer(TANK if k==0 else PLANE)
  last=ticks();prevk=keyboard();prevt=[]
  while True:
    now=ticks();dt=(now-last)/1000.0;last=now
    if dt>0.15:dt=0.15
    if dt<=0:dt=0.01
    p=VEH[0]
    k=keyboard();pk=k&~prevk;prevk=k
    pts=touches();tap=pts and not prevt
    if kd(pk,K_ESC):
      FR(80,80,160,40,0x101418);ctext("PAUSED",86,0xFFD030);ctext("Esc: quit  Enter: resume",102,0xFFFFFF);flip()
      release();q=0
      while True:
        kk=keyboard()
        if kd(kk,K_ESC):q=1;break
        if kd(kk,K_ENTER) or touches():break
      release()
      if q:return
      last=ticks();prevk=0;continue
    up=kd(k,K_UP) or inside(B_UP,pts);dn=kd(k,K_DN) or inside(B_DN,pts)
    lt=kd(k,K_LT) or inside(B_LT,pts);rt=kd(k,K_RT) or inside(B_RT,pts)
    fire=kd(k,K_ENTER) or inside(B_FIRE,pts)
    fire2=kd(k,K_DEL) or inside(B_ALT,pts)
    if kd(pk,K_0) or (tap and inside(B_SCOPE,pts)):ST['scope']=1-ST['scope']
    if kd(pk,K_MENU) or (tap and inside(B_MAP,pts)):ST['map']=1-ST['map']
    if kd(pk,K_7) or kd(pk,K_9):
      n=VIEWS.index(VR[0])+(1 if kd(pk,K_9) else -1);VR[0]=VIEWS[max(0,min(2,n))]
      say('View distance %d m'%int(VR[0]*CS),0xC0C8D0,1.5)
    #drag on the 3D view to aim (tank) or steer (plane)
    dragx=0.0;dragy=0.0
    vp=[q for q in pts if q[1]<VB-2]
    if vp and not ST['map']:
      if ST['drag'] is not None:
        dragx=vp[0][0]-ST['drag'][0];dragy=vp[0][1]-ST['drag'][1]
      if p.kind==TANK or ST['drag'] is None:ST['drag']=vp[0]
    else:ST['drag']=None
    thr=0
    if p.kind==TANK:
      zs=0.3 if ST['scope'] else 1.0
      ST['ay']+=((kd(k,K_6)-kd(k,K_4))*1.1*dt+dragx*0.006)*zs
      ST['ap']+=((kd(k,K_8)-kd(k,K_2))*0.5*dt-dragy*0.004)*zs
      ST['ap']=max(-0.25,min(1.2,ST['ap']))
      ctl=(up-dn,rt-lt,0,0,fire,fire2,0,0,0)
    else:
      pin=up-dn;rin=rt-lt
      if ST['drag'] is not None and vp:
        pin=max(-1,min(1,-dragy/40.0));rin=max(-1,min(1,dragx/40.0))
      th=kd(k,K_PLUS)-kd(k,K_MINUS)
      if inside(B_THR,pts):th=1 if [q for q in pts if q[1]<214 and B_THR[0]<=q[0]] else -1
      ctl=(pin,rin,0,0,fire,fire2,0,0,th)
    if p.alive:
      n=int(dt/0.05)+1
      for s in range(n):worldStep(dt/n,ctl)
    else:
      for s in range(int(dt/0.05)+1):worldStep(dt/(int(dt/0.05)+1),(0,0,0,0,0,0,0,0,0))
      ST['resp']+=dt
    if p.alive:camStep(dt)
    else:
      a=ST['resp']*0.3
      setCam(p.x-sin(a)*40,max(p.y,gAt(p.x,p.z))+18,p.z-cos(a)*40,a,0.35,0.0,150.0)
    render();markers();crosshair(ST['scope'])
    if ST['scope'] and p.kind==TANK:
      FR(0,0,40,VB,0x080808);FR(280,0,40,VB,0x080808)
    if p.hitT>0:
      p.hitT-=dt;FR(0,0,SW,3,0xFF2020);FR(0,VB-3,SW,3,0xFF2020)
    topHud()
    if ST['map']:minimap()
    dashboard((up,dn,lt,rt,fire,fire2,ST['scope'],ST['map']))
    if not p.alive:
      FR(80,70,160,30,0x101418);ctext('DESTROYED',76,0xFF6060)
      ctext('respawn in %d'%max(0,int(4-ST['resp'])+1),88,0xFFFFFF)
    flip()
    prevt=pts
    if TK[0]<=0 or TK[1]<=0:
      results();return
    if not p.alive and ST['resp']>4:
      k=spawnScreen()
      if k<0:return
      ST['resp']=0.0;setPlayer(TANK if k==0 else PLANE);last=ticks()

def results():
  p=VEH[0];won=TK[1]<=0
  FR(40,40,240,120,0x101418);FR(40,40,240,2,0xFFD030)
  ctext('VICTORY' if won else 'DEFEAT',50,0x60F090 if won else 0xFF6060)
  ctext(MAPS[MI[0]][0],66,0xC0C8D0)
  T(60,86,'Your kills',0xFFFFFF);T(220,86,str(p.kills),0xFFFFFF)
  T(60,100,'Your deaths',0xFFFFFF);T(220,100,str(p.deaths),0xFFFFFF)
  T(60,114,'Tickets left',0xFFFFFF);T(200,114,'%d : %d'%(TK[0],TK[1]),0xFFFFFF)
  ctext('Tap / Enter',140,0x8890A0)
  flip();release()
  while True:
    k=keyboard()
    if kd(k,K_ENTER) or kd(k,K_ESC) or touches():break
  release()

MB={'ml':(10,120,34,26),'mr':(276,120,34,26),'dl':(10,156,34,26),'dr':(276,156,34,26),'go':(110,194,100,30)}
def menu():
  row=0;release();prevk=0;built=-1
  while True:
    if built!=MI[0]:
      genMap(MI[0]);built=MI[0]
      global VEH
      VEH=[]
    camOrbit();render()
    bigtext("STRIKER",14,5,0xFFD030,0x101418)
    FR(0,46,SW,13,0x101418);ctext("tanks and planes - capture point A",48,0xFFFFFF)
    FR(0,108,SW,132,0x101418)
    for key in ('ml','mr','dl','dr'):
      x,y,w,h=MB[key];FR(x,y,w,h,0x2A3A50)
      if key[1]=='l':poly(((x+10,y+13),(x+24,y+5),(x+24,y+21)),0xFFFFFF)
      else:poly(((x+24,y+13),(x+10,y+5),(x+10,y+21)),0xFFFFFF)
    ctext("MAP",110,0x8890A0);ctext(MAPS[MI[0]][0],126,0xFFD030 if row==0 else 0xFFFFFF)
    ctext("BOT SKILL",146,0x8890A0);ctext(("Easy","Normal","Hard")[DIFF[0]],162,0xFFD030 if row==1 else 0xFFFFFF)
    x,y,w,h=MB['go'];FR(x,y,w,h,0x30A050 if row==2 else 0x206838);ctext("BATTLE",y+10,0xFFFFFF)
    T(232,226,'Esc: quit',0xC0C8D0)
    flip()
    k=keyboard();pk=k&~prevk;prevk=k
    pts=touches()
    if kd(pk,K_ESC):return 0
    if kd(pk,K_UP):row=(row+2)%3
    if kd(pk,K_DN):row=(row+1)%3
    d=kd(pk,K_RT)-kd(pk,K_LT)
    if pts:
      if inside(MB['ml'],pts):row=0;d=-1
      elif inside(MB['mr'],pts):row=0;d=1
      elif inside(MB['dl'],pts):row=1;d=-1
      elif inside(MB['dr'],pts):row=1;d=1
      elif inside(MB['go'],pts):release();return 1
      release()
    if d:
      if row==0:MI[0]=(MI[0]+d)%2
      elif row==1:DIFF[0]=(DIFF[0]+d)%3
    if kd(pk,K_ENTER):
      if row==2:release();return 1
      row+=1

def main():
  dimgrob(G,SW,SH,0)
  while True:
    if not menu():return
    play(MI[0])
    gc.collect()

main()
