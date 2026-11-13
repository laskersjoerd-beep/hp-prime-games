#WOODLOT - a lumber tycoon game for the HP Prime
#Chop trees, haul logs, saw planks, sell wood, buy better gear and build
#your own house on your plot. Original island and buildings.
#Python app (hpprime module). Touch buttons + keyboard.
from hpprime import *
from math import *
import gc

try:
  ticks()
except:
  def ticks():
    return int(eval("TICKS()"))

_rs=[777]
def rnd():
  _rs[0]=(_rs[0]*1103515245+12345)&0x7fffffff
  return _rs[0]/2147483648.0

G=1;SW=320;SH=240
CX=160;CY=110;F=170.0
NEAR=0.3
SKY=0x9CCBF0;SKY2=0x5E9ED8;HAZE=0xC8DCE8;SEA=0x3A78C0

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
  if f<0:f=0
  return (int(((c>>16)&255)*f)<<16)|(int(((c>>8)&255)*f)<<8)|int((c&255)*f)
def mix(c,d,t):
  if t<=0:return c
  if t>1:t=1
  u=1-t
  return (int(((c>>16)&255)*u+((d>>16)&255)*t)<<16)|(int(((c>>8)&255)*u+((d>>8)&255)*t)<<8)|int((c&255)*u+(d&255)*t)
def box2(x,y,w,h,c):
  FR(x,y,w,1,c);FR(x,y+h-1,w,1,c);FR(x,y,1,h,c);FR(x+w-1,y,1,h,c)
def otext(x,y,s,c):
  textout(G,x+1,y+1,s,0);textout(G,x,y,s,c)
def ctext(s,y,c):
  otext((SW-len(s)*7)//2,y,s,c)
FONT={
'A':"0111010001111111000110001",'D':"1111010001100011000111110",
'L':"1000010000100001000011111",'O':"0111010001100011000101110",
'T':"1111100100001000010000100",'W':"1000110001101011101110001",
' ':"0000000000000000000000000"}
def bigtext(s,y,sz,c,sh=0):
  x0=(SW-len(s)*6*sz)//2
  for n in range(len(s)):
    f=FONT.get(s[n],FONT[' '])
    for i in range(25):
      if f[i]=='1':
        if sh:FR(x0+n*6*sz+(i%5)*sz+2,y+(i//5)*sz+2,sz,sz,sh)
        FR(x0+n*6*sz+(i%5)*sz,y+(i//5)*sz,sz,sz,c)

#---------- input ----------
K_UP=2;K_DN=12;K_LT=7;K_RT=8;K_ESC=4;K_ENTER=30;K_MENU=13;K_DEL=19
K_SPC=49;K_PLUS=50;K_MINUS=45;K_8=33;K_5=38;K_4=37;K_6=39
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
def release():
  while keyboard() or touches():
    pass
B_LT=(4,190,44,46);B_FW=(52,170,44,32);B_BK=(52,206,44,30);B_RT=(100,190,44,46)
B_ACT=(250,176,66,60);B_BLD=(180,200,64,36)
def tbtn(b,on,lab,col=0x3060A0):
  x,y,w,h=b
  FR(x,y,w,h,col if on else shade(col,0.45))
  box2(x,y,w,h,0xFFFFFF)
  textout(G,x+(w-len(lab)*7)//2,y+h//2-6,lab,0xFFFFFF)

#---------- 3D ----------
CAM=[0.0,3.0,0.0,1.0,0.0]   #x,y,z,cos(yaw),sin(yaw)
PIT=[0.25]
def tf(x,y,z):
  x-=CAM[0];y-=CAM[1];z-=CAM[2]
  c=CAM[3];s=CAM[4]
  x2=x*c-z*s;z2=x*s+z*c
  cp=cos(PIT[0]);sp=sin(PIT[0])
  return (x2,y*cp+z2*sp,-y*sp+z2*cp)
CPS=[1.0,0.0]
def tff(x,y,z):
  #fast version using cached pitch
  x-=CAM[0];y-=CAM[1];z-=CAM[2]
  c=CAM[3];s=CAM[4]
  x2=x*c-z*s;z2=x*s+z*c
  return (x2,y*CPS[0]+z2*CPS[1],-y*CPS[1]+z2*CPS[0])
def poly3(P,c):
  allin=1
  for p in P:
    if p[2]<NEAR:
      allin=0;break
  if allin:
    l=r=u=d=1;xr=CX/F*1.05;yr=(SH-CY)/F*1.05
    for p in P:
      x=p[0];y=p[1];z=p[2]
      if x>-xr*z:l=0
      if x<xr*z:r=0
      if y<CY/F*1.05*z:u=0
      if y>-yr*z:d=0
    if l or r or u or d:return
    poly([(int(CX+F*p[0]/p[2]),int(CY-F*p[1]/p[2])) for p in P],c)
    return
  Q=[];n=len(P)
  for i in range(n):
    a=P[i];b=P[(i+1)%n]
    ai=a[2]>=NEAR;bi=b[2]>=NEAR
    if ai:Q.append(a)
    if ai!=bi:
      t=(NEAR-a[2])/(b[2]-a[2])
      Q.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),NEAR))
  if len(Q)<3:return
  pts=[]
  for p in Q:
    sx=CX+F*p[0]/p[2];sy=CY-F*p[1]/p[2]
    pts.append((int(max(-3000,min(3000,sx))),int(max(-3000,min(3000,sy)))))
  poly(pts,c)
def fog(c,z):
  return mix(c,HAZE,(z-40)/90.0)

def obox(cx,cy,cz,h,hw,hh,hl,col,d,pitch=0.0):
  #oriented box: centre, yaw h, half sizes (width, height, length), optional pitch
  fx=sin(h);fz=cos(h)
  if pitch:
    cp=cos(pitch);sp=sin(pitch)
    F3=(fx*cp,sp,fz*cp);U3=(-fx*sp,cp,-fz*sp)
  else:
    F3=(fx,0.0,fz);U3=(0.0,1.0,0.0)
  R3=(fz,0.0,-fx)
  ex=CAM[0]-cx;ey=CAM[1]-cy;ez=CAM[2]-cz
  lr=ex*R3[0]+ez*R3[2];lu=ex*U3[0]+ey*U3[1]+ez*U3[2];lf=ex*F3[0]+ey*F3[1]+ez*F3[2]
  c=fog(col,d)
  def V(a,b,e):
    return tff(cx+R3[0]*a+U3[0]*b+F3[0]*e,cy+U3[1]*b+F3[1]*e,cz+R3[2]*a+U3[2]*b+F3[2]*e)
  if lu>hh:poly3([V(-hw,hh,-hl),V(hw,hh,-hl),V(hw,hh,hl),V(-hw,hh,hl)],c)
  elif lu<-hh:poly3([V(-hw,-hh,-hl),V(hw,-hh,-hl),V(hw,-hh,hl),V(-hw,-hh,hl)],shade(c,0.5))
  if lf>hl:poly3([V(-hw,-hh,hl),V(hw,-hh,hl),V(hw,hh,hl),V(-hw,hh,hl)],shade(c,0.85))
  elif lf<-hl:poly3([V(-hw,-hh,-hl),V(hw,-hh,-hl),V(hw,hh,-hl),V(-hw,hh,-hl)],shade(c,0.7))
  if lr>hw:poly3([V(hw,-hh,-hl),V(hw,-hh,hl),V(hw,hh,hl),V(hw,hh,-hl)],shade(c,0.75))
  elif lr<-hw:poly3([V(-hw,-hh,-hl),V(-hw,-hh,hl),V(-hw,hh,hl),V(-hw,hh,-hl)],shade(c,0.75))

#---------- the island (original map) ----------
#zones: x0,z0,x1,z1, ground colour, wood type planted there (-1 none), name
WOODS=[  #name, bark, leaves, $ per m3, hardness, min axe tier, shape
 ("Pine",0x6B4A2E,0x2E6B3A,8,1.0,0,0),
 ("Birch",0xE8E4D8,0x8CC860,12,1.0,0,1),
 ("Oak",0x7A5230,0x3F8A30,18,1.6,0,2),
 ("Frost Pine",0x8A8FA0,0xDDE8F0,26,1.8,1,0),
 ("Bogwood",0x3A3A24,0x6A7A30,42,2.2,1,2),
 ("Emberwood",0x202020,0xFF5020,110,3.0,2,1)]
ZONES=[
 (160,160,250,240,0xB8A888,-1,"Millbrook Town"),
 (20,20,150,150,0x3E7A38,0,"Pine Forest"),
 (160,260,300,380,0x7AB050,1,"Birch Meadow"),
 (20,170,150,330,0x4E8A3A,2,"Old Oak Wood"),
 (170,20,300,140,0xE8EEF4,3,"Frost Hills"),
 (20,345,150,392,0x4A5A30,4,"The Bog"),
 (340,40,395,360,0x2E2626,5,"Cinder Isle")]
RIVER=(310,0,332,400);BRIDGE=(305,193,337,207)
PLOT=(255,172,297,228)
SAWMILL=(266,184)
BUYER=(226,178)       #drop wood on the pad to sell it
SHOPS=[("Axe Barn",186,176,0xA04030),("Truck Yard",186,218,0x3060A0),("Saw Works",226,220,0x707020)]
AXES=[("Rusty Axe",1.0,0),("Iron Axe",2.0,150),("Steel Axe",3.5,700),("Fire Axe",6.0,2600)]
SAWS=[("Old Sawmill",1.0,0),("Fast Sawmill",2.0,600),("Turbo Sawmill",3.5,2000)]
TRUCKP=500

def zoneAt(x,z):
  for zn in ZONES:
    if zn[0]<=x<=zn[2] and zn[1]<=z<=zn[3]:return zn
  return None
def walkable(x,z):
  if x<2 or z<2 or x>398 or z>398:return 0
  if RIVER[0]<=x<=RIVER[2] and not (BRIDGE[1]<=z<=BRIDGE[3]):return 0
  if 332<x<340 and not (BRIDGE[1]<=z<=BRIDGE[3]):return 0   #sea channel
  return 1

#---------- game state ----------
class O:
  pass
PL=O();ST={}
TREES=[]   #[x,z,type,height,radius,hp,maxhp,state,fallt,fallh,regrow]
OBJS=[]    #[kind 0 log/1 plank, x,z, h, length, radius, type, value, state, slot, y]
BPS=[]     #[cx,cz,level,kind 0 floor/1 wall/2 pillar,rot,fill wood or -1]
TR=O()     #truck

def plantTrees():
  TREES[:]=[]
  _rs[0]=4242
  for zn in ZONES:
    if zn[5]<0:continue
    x0,z0,x1,z1=zn[0],zn[1],zn[2],zn[3]
    n=int((x1-x0)*(z1-z0)/600)
    for i in range(n):
      x=x0+4+rnd()*(x1-x0-8);z=z0+4+rnd()*(z1-z0-8)
      newTree(zn[5],x,z)

def newTree(w,x,z):
  h=4.0+rnd()*5.0;r=0.25+rnd()*0.35
  if w==5:h=3.5+rnd()*3;r=0.3+rnd()*0.2
  hp=r*12*WOODS[w][4]
  TREES.append([x,z,w,h,r,hp,hp,0,0.0,0.0,0.0])

def newgame():
  PL.x=235.0;PL.z=200.0;PL.h=pi/2;PL.mode=0;PL.hold=None;PL.swing=0.0;PL.ph=0.0;PL.cy=PL.h
  ST.update(money=40,axe=0,saw=0,truck=0,msg="",msgt=0.0,t=0.0,btn=1,map=1,build=0)
  OBJS[:]=[];BPS[:]=[]
  TR.x=200.0;TR.z=232.0;TR.h=pi/2;TR.v=0.0;TR.slots=[None,None,None,None]
  plantTrees()
  ST['saw_q']=None;ST['saw_t']=0.0
  load()
  say("Chop a tree! Find the forests on the island.",4)

def say(m,t=2.5):
  ST['msg']=m;ST['msgt']=t

def objValue(o):
  w=WOODS[o[6]]
  vol=pi*o[5]*o[5]*o[4] if o[0]==0 else o[5]
  return int(vol*w[3]*(1.6 if o[0]==1 else 1.0))+1

#---------- saving ----------
def save():
  try:
    f=open("woodlot.txt","w")
    f.write("%d %d %d %d\n"%(ST['money'],ST['axe'],ST['saw'],ST['truck']))
    for b in BPS:
      f.write("%d %d %d %d %d %d\n"%(b[0],b[1],b[2],b[3],b[4],b[5]))
    f.close()
    return 1
  except:
    return 0
def load():
  try:
    f=open("woodlot.txt","r");lines=f.read().split("\n");f.close()
    a=[int(v) for v in lines[0].split()]
    ST['money'],ST['axe'],ST['saw'],ST['truck']=a[0],a[1],a[2],a[3]
    for ln in lines[1:]:
      v=ln.split()
      if len(v)==6:BPS.append([int(x) for x in v])
  except:
    pass

#---------- interaction ----------
def nearestTree():
  best=None;fx=sin(PL.h);fz=cos(PL.h)
  for t in TREES:
    if t[7]!=0:continue
    dx=t[0]-PL.x;dz=t[1]-PL.z;d=sqrt(dx*dx+dz*dz)
    if d<2.6 and (dx*fx+dz*fz)>-0.3*d:
      if best is None or d<best[0]:best=(d,t)
  return best[1] if best else None

def nearestObj(r=2.6):
  best=None
  for o in OBJS:
    if o[8]==1:continue
    if o[8]==3:continue
    ox,oz=o[1],o[2]
    if o[8]==2:ox,oz=slotPos(o[9])
    dx=ox-PL.x;dz=oz-PL.z
    #distance to the log's line, not just its centre
    fx=sin(o[3]);fz=cos(o[3])
    al=max(-o[4]/2,min(o[4]/2,dx*fx+dz*fz))
    px=ox-fx*al;pz=oz-fz*al
    d=sqrt((px-PL.x)**2+(pz-PL.z)**2)
    if d<r and (best is None or d<best[0]):best=(d,o)
  return best[1] if best else None

def slotPos(k):
  fx=sin(TR.h);fz=cos(TR.h);rx=fz;rz=-fx
  off=-0.4-(k//2)*1.3;side=-0.45 if k%2==0 else 0.45
  return (TR.x+fx*off+rx*side,TR.z+fz*off+rz*side)

def nearShop():
  for i in range(len(SHOPS)):
    s=SHOPS[i]
    if abs(PL.x-(s[1]+5))<3 and abs(PL.z-s[2])<4:return i
  return -1

def onPlot(x,z):
  return PLOT[0]<=x<=PLOT[2] and PLOT[1]<=z<=PLOT[3]

def contextAction():
  #what the big ACTION button does right now
  if PL.mode==1:return ("EXIT",None)
  if PL.hold is not None:return ("DROP",None)
  s=nearShop()
  if s>=0:return ("SHOP",s)
  t=nearestTree()
  if t:return ("CHOP",t)
  o=nearestObj()
  if o:return ("GRAB",o)
  if ST['truck'] and (TR.x-PL.x)**2+(TR.z-PL.z)**2<12:return ("DRIVE",None)
  return ("",None)

def chop(t):
  if PL.swing>0:return
  PL.swing=0.42
  w=WOODS[t[2]]
  if AXES_TIER()<w[5]:
    say("Too hard! You need the "+AXES[w[5]][0],2);return
  t[5]-=AXES[ST['axe']][1]
  CHIPS.append([t[0],0.8,t[1],0.35,w[1]])
  if t[5]<=0:
    #timber! it falls away from you
    t[7]=1;t[8]=0.0;t[9]=atan2(t[0]-PL.x,t[1]-PL.z)
    say(w[0]+" tree is falling!",1.5)
def AXES_TIER():
  return ST['axe']

def dropHeld():
  o=PL.hold;PL.hold=None;o[8]=0
  fx=sin(PL.h);fz=cos(PL.h)
  o[1]=PL.x+fx*(o[4]/2+0.8);o[2]=PL.z+fz*(o[4]/2+0.8);o[3]=PL.h;o[10]=0.0
  #sell?
  if abs(o[1]-BUYER[0])<4.5 and abs(o[2]-BUYER[1])<4.5:
    v=objValue(o);ST['money']+=v;OBJS.remove(o)
    say("SOLD "+WOODS[o[6]][0]+(" plank" if o[0] else " log")+"  +$"+str(v),2.5);save();return
  #sawmill input?
  if o[0]==0 and abs(o[1]-SAWMILL[0])<3.5 and abs(o[2]-SAWMILL[1])<3.5:
    if ST['saw_q'] is None:
      o[8]=3;ST['saw_q']=o;ST['saw_t']=0.0;say("Sawing "+WOODS[o[6]][0]+"...",2);return
    say("The sawmill is busy",1.5)
  #truck bed?
  if ST['truck'] and PL.mode==0 and (TR.x-o[1])**2+(TR.z-o[2])**2<14:
    for k in range(4):
      if TR.slots[k] is None:
        TR.slots[k]=o;o[8]=2;o[9]=k;say("Loaded onto the truck ("+str(k+1)+"/4)",1.5);return
  #fill a blueprint?
  if o[0]==1:
    best=None
    for b in BPS:
      if b[5]>=0:continue
      bx,bz,by=bpCentre(b)
      d=(bx-PL.x)**2+(bz-PL.z)**2
      if d<12 and (best is None or d<best[0]):best=(d,b)
    if best:
      best[1][5]=o[6];OBJS.remove(o);say("Built with "+WOODS[o[6]][0]+"!",1.5);save();return

def grab(o):
  if o[8]==2:
    TR.slots[o[9]]=None
  o[8]=1;PL.hold=o
  say("Holding "+WOODS[o[6]][0]+(" plank" if o[0] else " log")+"  ($"+str(objValue(o))+")",2)

def bpCentre(b):
  x=PLOT[0]+1+b[0]*2.0;z=PLOT[1]+1+b[1]*2.0;y=b[2]*2.4
  return x,z,y

#---------- shop ----------
def shopMenu(i):
  name=SHOPS[i][0]
  if i==0:
    items=[(a[0],a[2],"chop power "+str(a[1])) for a in AXES]
  elif i==1:
    items=[("Pickup Truck",TRUCKP,"carries 4 logs")]
  else:
    items=[(s[0],s[2],"speed x"+str(s[1])) for s in SAWS]
  sel=0;release()
  while True:
    FR(10,20,300,200,0x1A1410);box2(10,20,300,200,0xE0C080)
    ctext(name,28,0xFFE0A0)
    otext(20,44,"Money: $"+str(ST['money']),0x80FF80)
    rows=[]
    for k in range(len(items)):
      y=64+k*34;rows.append((20,y,280,30))
      nm,pr,info=items[k]
      own=(i==0 and ST['axe']>=k) or (i==1 and ST['truck']) or (i==2 and ST['saw']>=k)
      FR(20,y,280,30,0x3A3020 if k!=sel else 0x6A5030);box2(20,y,280,30,0xA08050)
      otext(28,y+3,nm,0xFFFFFF);otext(28,y+16,info,0xC0C0A0)
      otext(220,y+9,"OWNED" if own else "$"+str(pr),0x80FF80 if own else (0xFFFFFF if ST['money']>=pr else 0xFF8080))
    otext(20,200,"Tap item to buy - Esc / tap here to leave",0xC0C0C0)
    flip()
    k=keyboard()
    if kd(k,K_ESC):release();return
    if kd(k,K_UP):sel=max(0,sel-1);release()
    if kd(k,K_DN):sel=min(len(items)-1,sel+1);release()
    buy=-1
    if kd(k,K_ENTER):buy=sel;release()
    p=touches()
    if p:
      for k2 in range(len(rows)):
        if inside(rows[k2],p):buy=k2;sel=k2
      if p[0][1]>=196:release();return
      release()
    if buy>=0:
      nm,pr,info=items[buy]
      own=(i==0 and ST['axe']>=buy) or (i==1 and ST['truck']) or (i==2 and ST['saw']>=buy)
      if own:continue
      if ST['money']<pr:
        FR(40,100,240,30,0x600000);ctext("Not enough money!",108,0xFFFFFF);flip();t0=ticks()
        while ticks()-t0<700:pass
        continue
      ST['money']-=pr
      if i==0:ST['axe']=buy
      elif i==1:
        ST['truck']=1;TR.x=196.0;TR.z=226.0;TR.h=pi/2
      else:ST['saw']=buy
      save()

#---------- update ----------
CHIPS=[]   #wood chips / sawdust particles [x,y,z,life,colour]
def update(dt,fw,bk,lt,rt):
  ST['t']+=dt
  ST['msgt']=max(0.0,ST['msgt']-dt)
  PL.swing=max(0.0,PL.swing-dt)
  if PL.mode==0:
    PL.h+=((1 if rt else 0)-(1 if lt else 0))*2.6*dt
    sp=(5.5 if fw else 0.0)-(3.0 if bk else 0.0)
    if PL.hold is not None:sp*=0.8
    nx=PL.x+sin(PL.h)*sp*dt;nz=PL.z+cos(PL.h)*sp*dt
    if walkable(nx,PL.z):PL.x=nx
    if walkable(PL.x,nz):PL.z=nz
    if sp:PL.ph+=dt*10
  else:
    v=TR.v
    if fw:v+=10*dt*max(0.0,1-v/18.0)
    elif bk:v-=14*dt if v>0 else 6*dt
    else:v-=v*0.8*dt
    v=max(-6.0,v);TR.v=v
    st=(1 if rt else 0)-(1 if lt else 0)
    TR.h+=st*1.7*min(1.0,abs(v)/4.0)*(1 if v>=0 else -1)*dt
    nx=TR.x+sin(TR.h)*v*dt;nz=TR.z+cos(TR.h)*v*dt
    if walkable(nx,nz):TR.x=nx;TR.z=nz
    else:TR.v=-TR.v*0.3
    PL.x=TR.x;PL.z=TR.z;PL.h=TR.h
  #held object follows you
  o=PL.hold
  if o is not None:
    fx=sin(PL.h);fz=cos(PL.h)
    tx=PL.x+fx*(o[4]/2+0.8);tz=PL.z+fz*(o[4]/2+0.8)
    o[1]+=(tx-o[1])*min(1.0,dt*8);o[2]+=(tz-o[2])*min(1.0,dt*8)
    dh=PL.h-o[3]
    while dh>pi:dh-=2*pi
    while dh<-pi:dh+=2*pi
    o[3]+=dh*min(1.0,dt*6);o[10]=0.9
  #truck cargo rides along
  for k in range(4):
    c=TR.slots[k]
    if c is not None:
      c[1],c[2]=slotPos(k);c[3]=TR.h;c[10]=1.1
  #falling trees become logs
  for t in TREES:
    if t[7]==1:
      t[8]+=dt*(0.6+t[8]*2.5)
      if t[8]>=1.0:
        t[7]=2;t[10]=60.0+rnd()*60
        L=t[3]*0.92
        cx=t[0]+sin(t[9])*L/2;cz=t[1]+cos(t[9])*L/2
        o=[0,cx,cz,t[9],L,t[4],t[2],0,0,0,0.0]
        OBJS.append(o)
        while len(OBJS)>24:
          for q in OBJS:
            if q[8]==0 and q is not PL.hold:
              OBJS.remove(q);break
          else:
            break
    elif t[7]==2:
      t[10]-=dt
      if t[10]<=0:
        #a new tree grows somewhere in the same forest
        zn=[z for z in ZONES if z[5]==t[2]][0]
        t[0]=zn[0]+4+rnd()*(zn[2]-zn[0]-8);t[1]=zn[1]+4+rnd()*(zn[3]-zn[1]-8)
        t[3]=4.0+rnd()*5.0;t[5]=t[6];t[7]=0
  #sawmill
  q=ST['saw_q']
  if q is not None:
    ST['saw_t']+=dt*SAWS[ST['saw']][1]
    need=q[4]*0.9
    q[1]=SAWMILL[0];q[2]=SAWMILL[1]-2+min(1.0,ST['saw_t']/need)*4;q[3]=0.0;q[10]=0.9
    if int(ST['t']*10)%2==0:CHIPS.append([SAWMILL[0]+rnd()-0.5,1.2,SAWMILL[1],0.4,0xE8D8A0])
    if ST['saw_t']>=need:
      n=max(1,int(q[4]/1.6))
      vol=pi*q[5]*q[5]*q[4]/n
      OBJS.remove(q);ST['saw_q']=None
      for k in range(n):
        OBJS.append([1,SAWMILL[0]+3.2+(k%3)*0.9,SAWMILL[1]+3+(k//3)*0.5,0.0,1.6,vol,q[6],0,0,0,0.0])
      say(str(n)+" "+WOODS[q[6]][0]+" planks ready!",2.5)
  #particles
  i=0
  while i<len(CHIPS):
    c=CHIPS[i];c[3]-=dt;c[1]+=dt*1.5
    if c[3]<=0:CHIPS.pop(i)
    else:i+=1

def camera(dt):
  d=PL.h-PL.cy
  while d>pi:d-=2*pi
  while d<-pi:d+=2*pi
  PL.cy+=d*min(1.0,dt*5)
  dist=9.0 if PL.mode==1 else 5.5;hh=4.6 if PL.mode==1 else 3.2
  tx=PL.x-sin(PL.cy)*dist;tz=PL.z-cos(PL.cy)*dist
  k=min(1.0,dt*7)
  CAM[0]+=(tx-CAM[0])*k;CAM[2]+=(tz-CAM[2])*k;CAM[1]+=(hh-CAM[1])*k
  CAM[3]=cos(PL.cy);CAM[4]=sin(PL.cy)
  PIT[0]=0.27;CPS[0]=cos(PIT[0]);CPS[1]=sin(PIT[0])

#---------- render ----------
VIEW=[70.0]
def ground():
  hor=int(CY-F*tan(PIT[0]))
  for i in range(4):
    FR(0,i*hor//4,SW,hor//4+1,mix(SKY2,SKY,i/3.0))
  FR(0,hor,SW,SH-hor,SEA)
  FR(0,hor-3,SW,5,HAZE)
  #the island and its regions
  def quad(x0,z0,x1,z1,c,y=0.0):
    poly3([tff(x0,y,z0),tff(x1,y,z0),tff(x1,y,z1),tff(x0,y,z1)],c)
  quad(0,0,400,400,0x5E9E48)
  for zn in ZONES:
    if abs((zn[0]+zn[2])/2-CAM[0])<(zn[2]-zn[0])/2+VIEW[0]+40 and abs((zn[1]+zn[3])/2-CAM[2])<(zn[3]-zn[1])/2+VIEW[0]+40:
      quad(zn[0],zn[1],zn[2],zn[3],zn[4],0.01)
  quad(RIVER[0],RIVER[1],RIVER[2],RIVER[3],0x3C80D0,0.02)
  quad(332,0,340,400,SEA,0.02)
  quad(BRIDGE[0],BRIDGE[1],BRIDGE[2],BRIDGE[3],0x8A6A40,0.05)
  quad(PLOT[0],PLOT[1],PLOT[2],PLOT[3],0xC8BC98,0.03)
  quad(BUYER[0]-4,BUYER[1]-4,BUYER[0]+4,BUYER[1]+4,0x40C060,0.04)

def tree(t,d):
  w=WOODS[t[2]];x,z=t[0],t[1];h=t[3];r=t[4]
  bark=w[1];leaf=w[2]
  if t[2]==5:leaf=mix(leaf,0xFFE040,0.5+0.5*sin(ST['t']*4+x))
  if t[7]==2:
    obox(x,0.25,z,0.0,r,0.25,r,shade(bark,0.8),d);return
  if t[7]==1:
    #falling: the whole tree tips over
    a=t[8]*1.5
    obox(x+sin(t[9])*sin(a)*h/2,cos(a)*h/2,z+cos(t[9])*sin(a)*h/2,t[9],r,h/2,r,bark,d,pitch=-a if a>0.01 else 0.0)
    return
  if d>40:
    #far away: cheap flat billboard
    b=tff(x,0,z);top=tff(x,h,z)
    if b[2]<1:return
    s=F/b[2];sx=CX+F*b[0]/b[2];sy=CY-F*b[1]/b[2];ty=CY-F*top[1]/top[2]
    if sx<-40 or sx>SW+40:return
    poly([(int(sx-r*s),int(sy)),(int(sx+r*s),int(sy)),(int(sx+r*s),int(ty)),(int(sx-r*s),int(ty))],fog(bark,d))
    cw=(1.6+r*2)*s
    poly([(int(sx),int(ty-cw*1.2)),(int(sx-cw),int(sy-(sy-ty)*0.45)),(int(sx+cw),int(sy-(sy-ty)*0.45))],fog(leaf,d))
    return
  obox(x,h*0.35,z,0.6,r,h*0.35,r,bark,d)
  shp=w[6]
  if shp==0:
    #conifer: two stacked pyramids
    for (y0,y1,rad) in ((h*0.35,h*0.8,1.7+r*2),(h*0.65,h*1.05,1.1+r*2)):
      tp=tff(x,y1,z);cs=[tff(x+rad*cos(k*2.09+0.3),y0,z+rad*sin(k*2.09+0.3)) for k in range(3)]
      c=fog(leaf,d)
      for k in range(3):
        a=cs[k];b=cs[(k+1)%3]
        poly3([a,b,tp],shade(c,0.7+0.3*((k+int(PL.cy*1.5))%3)/2))
  elif shp==1:
    obox(x,h*0.78,z,0.3,1.2+r,h*0.28,1.2+r,leaf,d)
  else:
    obox(x,h*0.75,z,0.8,2.0+r*2,h*0.25,2.0+r*2,leaf,d)
    obox(x+0.6,h*1.0,z-0.4,0.2,1.2+r,0.6,1.2+r,shade(leaf,1.15),d)

def drawObj(o,d):
  w=WOODS[o[6]]
  y=o[10]+(o[5] if o[0]==0 else 0.12)
  if o[0]==0:
    obox(o[1],y,o[2],o[3],o[5],o[5],o[4]/2,w[1],d)
  else:
    obox(o[1],o[10]+0.1,o[2],o[3],0.35,0.08,o[4]/2,mix(w[1],0xF0D8A0,0.35),d)

def drawTruck(d):
  x,z,h=TR.x,TR.z,TR.h;fx=sin(h);fz=cos(h)
  obox(x,0.3,z,h,0.95,0.3,2.3,0x181818,d)
  obox(x-fx*0.9,0.65,z-fz*0.9,h,1.0,0.25,1.4,0x505860,d)
  obox(x+fx*1.3,1.15,z+fz*1.3,h,0.95,0.55,0.9,0x3070C0,d)
  obox(x+fx*1.35,1.95,z+fz*1.35,h,0.85,0.25,0.6,0x203040,d)

def drawPlayer(d):
  if PL.mode==1:return
  x,z,h=PL.x,PL.z,PL.h;fx=sin(h);fz=cos(h);rx=fz;rz=-fx
  s=sin(PL.ph)*0.25
  obox(x-rx*0.15+fx*s,0.42,z-rz*0.15+fz*s,h,0.11,0.42,0.12,0x30405A,d)
  obox(x+rx*0.15-fx*s,0.42,z+rz*0.15-fz*s,h,0.11,0.42,0.12,0x30405A,d)
  obox(x,1.15,z,h,0.3,0.33,0.17,0xC03030,d)
  obox(x,1.65,z,h,0.16,0.16,0.16,0xE8B888,d)
  #axe swing
  a=PL.swing/0.42
  ax=x+rx*0.42+fx*(0.3+0.4*a);az=z+rz*0.42+fz*(0.3+0.4*a)
  obox(ax,1.1+0.4*a,az,h,0.04,0.35,0.04,0x6B4A2E,d)
  obox(ax+fx*0.08,1.4+0.4*a,az+fz*0.08,h,0.03,0.1,0.15,[0x806050,0xA0A0A8,0xD0D8E0,0xFF6020][ST['axe']],d)

def drawBuilding(x,z,w,dpt,hgt,col,roof,d):
  obox(x,hgt/2,z,0.0,w,hgt/2,dpt,col,d)
  obox(x,hgt+0.35,z,0.0,w+0.4,0.35,dpt+0.4,roof,d)

def drawBP(b,d):
  x,z,y=bpCentre(b)
  k=b[3];rot=b[4]
  filled=b[5]>=0
  col=mix(WOODS[b[5]][1],0xF0D8A0,0.35) if filled else 0x60A0FF
  if k==0:
    hw,hh,hl,cy=1.0,0.1,1.0,y+0.1
  elif k==1:
    hw,hh,hl,cy=(1.0,1.2,0.12,y+1.2) if rot%2==0 else (0.12,1.2,1.0,y+1.2)
  else:
    hw,hh,hl,cy=0.2,1.2,0.2,y+1.2
  if filled:
    obox(x,cy,z,0.0,hw,hh,hl,col,d)
  else:
    #ghost blueprint: outline only
    pts=[tff(x-hw,cy-hh,z-hl),tff(x+hw,cy-hh,z-hl),tff(x+hw,cy-hh,z+hl),tff(x-hw,cy-hh,z+hl),
         tff(x-hw,cy+hh,z-hl),tff(x+hw,cy+hh,z-hl),tff(x+hw,cy+hh,z+hl),tff(x-hw,cy+hh,z+hl)]
    pr=[]
    for p in pts:
      if p[2]<NEAR:return
      pr.append((int(CX+F*p[0]/p[2]),int(CY-F*p[1]/p[2])))
    for a,b2 in ((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)):
      line(G,pr[a][0],pr[a][1],pr[b2][0],pr[b2][1],0x80C0FF)

def render():
  ground()
  items=[]
  V=VIEW[0];cx=CAM[0];cz=CAM[2];c=CAM[3];s=CAM[4]
  def depth(x,z):
    return (x-cx)*s+(z-cz)*c
  for t in TREES:
    dx=t[0]-cx;dz=t[1]-cz
    if abs(dx)>V or abs(dz)>V:continue
    d=dx*s+dz*c
    if d<-3 or d>V:continue
    if abs(dx*c-dz*s)>d*1.0+8:continue
    items.append((d,0,t))
  for o in OBJS:
    d=depth(o[1],o[2])
    if -3<d<V:items.append((d,1,o))
  for b in BPS:
    x,z,y=bpCentre(b);d=depth(x,z)
    if -3<d<V:items.append((d,2,b))
  for i in range(len(SHOPS)):
    sh=SHOPS[i];d=depth(sh[1],sh[2])
    if -6<d<V+20:items.append((d,3,i))
  d=depth(SAWMILL[0],SAWMILL[1])
  if -4<d<V:items.append((d,4,None))
  if ST['truck']:
    d=depth(TR.x,TR.z)
    if -4<d<V:items.append((d,5,None))
  d=depth(370,200)
  if d>-30:items.append((d+20,6,None))
  items.append((depth(PL.x,PL.z),7,None))
  items.sort(key=lambda q:-q[0])
  for d,ty,o in items:
    if ty==0:tree(o,d)
    elif ty==1:drawObj(o,d)
    elif ty==2:drawBP(o,d)
    elif ty==3:
      sh=SHOPS[o];drawBuilding(sh[1],sh[2],4.0,3.5,3.4,0xD8C8A8,sh[3],d)
      if d<30:
        p=tff(sh[1]+4.2,3.0,sh[2])
        if p[2]>1:otext(int(CX+F*p[0]/p[2])-len(sh[0])*3,int(CY-F*p[1]/p[2]),sh[0],0xFFFFA0)
    elif ty==4:
      obox(SAWMILL[0],0.6,SAWMILL[1],0.0,1.2,0.6,2.4,0x707880,d)
      obox(SAWMILL[0],1.6,SAWMILL[1],0.0,0.08,0.5,0.5,0xD0D0D8 if int(ST['t']*12)%2 else 0xA0A0A8,d)
      obox(SAWMILL[0]+3.2,0.05,SAWMILL[1]+3.4,0.0,1.6,0.05,1.2,0x806040,d)
    elif ty==5:drawTruck(d)
    elif ty==6:
      #the volcano on Cinder Isle
      b0=tff(352,0,188);b1=tff(388,0,188);b2=tff(388,0,212);b3=tff(352,0,212);tp=tff(370,26,200)
      poly3([b0,b1,tp],0x3A2C28);poly3([b1,b2,tp],0x2A201C);poly3([b3,b0,tp],0x4A3830)
      poly3([tff(367,24,198),tff(373,24,198),tff(370,27.5,200)],0xFF5010)
    else:drawPlayer(d)
  for ch in CHIPS:
    p=tff(ch[0],ch[1],ch[2])
    if p[2]>NEAR:FR(int(CX+F*p[0]/p[2])-1,int(CY-F*p[1]/p[2])-1,3,3,ch[4])
  #labels for the buyer + sawmill
  for (x,z,txt) in ((BUYER[0],BUYER[1],"SELL WOOD HERE"),(SAWMILL[0],SAWMILL[1]-3,"SAWMILL - drop logs")):
    p=tff(x,2.6,z)
    if 1<p[2]<35:otext(int(CX+F*p[0]/p[2])-len(txt)*3,int(CY-F*p[1]/p[2]),txt,0xA0FFA0)

def minimap():
  ox=4;oy=36;S=60;sc=S/400.0
  FR(ox-1,oy-1,S+2,S+2,0x101010);FR(ox,oy,S,S,SEA);FR(ox,oy,S,S,SEA)
  FR(ox,oy,S,S,0x5E9E48)
  for zn in ZONES:
    FR(ox+int(zn[0]*sc),oy+int(zn[1]*sc),max(1,int((zn[2]-zn[0])*sc)),max(1,int((zn[3]-zn[1])*sc)),zn[4])
  FR(ox+int(RIVER[0]*sc),oy,max(2,int((RIVER[2]-RIVER[0])*sc)),S,0x3C80D0)
  FR(ox+int(PLOT[0]*sc),oy+int(PLOT[1]*sc),int((PLOT[2]-PLOT[0])*sc),int((PLOT[3]-PLOT[1])*sc),0xFFFF60)
  px=ox+int(PL.x*sc);pz=oy+int(PL.z*sc)
  FR(px-1,pz-1,3,3,0xFF2020)

def hud(ctl,act):
  otext(4,2,"$"+str(ST['money']),0x80FF80)
  otext(4,16,AXES[ST['axe']][0],0xE0E0E0)
  zn=zoneAt(PL.x,PL.z)
  nm=zn[6] if zn else ("Your Plot" if onPlot(PL.x,PL.z) else "Wilds")
  if onPlot(PL.x,PL.z):nm="Your Plot"
  otext(SW-len(nm)*7-4,2,nm,0xFFFFA0)
  if ST['map']:minimap()
  if PL.hold is not None:
    o=PL.hold;otext(SW-150,16,"Holding: $"+str(objValue(o)),0xFFE080)
  t=nearestTree() if PL.mode==0 and PL.hold is None else None
  if t:
    w=WOODS[t[2]];FR(110,28,100,6,0x301010);FR(110,28,int(100*max(0,t[5])/t[6]),6,0xE0A040)
    otext(110,36,w[0]+" $"+str(w[3])+"/m3",0xFFFFFF)
  if ST['msgt']>0:ctext(ST['msg'],56,0xFFFFFF)
  if ST['btn']:
    lt,rt,fw,bk,a,bl=ctl
    tbtn(B_LT,lt,"<");tbtn(B_RT,rt,">");tbtn(B_FW,fw,"^");tbtn(B_BK,bk,"v")
    lab=act[0] if act[0] else "-"
    tbtn(B_ACT,a,lab,0x308040 if act[0] else 0x404040)
    if onPlot(PL.x,PL.z) and PL.mode==0:tbtn(B_BLD,bl,"BUILD",0x806020)

def flip():
  strblit(0,0,0,SW,SH,G)

#---------- build mode ----------
BB_FLOOR=(4,4,58,24);BB_WALL=(66,4,58,24);BB_PIL=(128,4,58,24);BB_ROT=(190,4,40,24);BB_LVL=(234,4,40,24);BB_DEL=(278,4,38,24)
BB_DONE=(250,206,66,30)
GW=int((PLOT[2]-PLOT[0])/2);GD=int((PLOT[3]-PLOT[1])/2)
def buildMode():
  kind=1;rot=0;lvl=0;cx=GW//2;cz=GD//2;msg="Tap the grid to place blueprints"
  release();prevk=0
  while True:
    #top-down view of the plot
    FR(0,0,SW,SH,0x283018)
    cs=int(min(260/GW,190/GD));ox=(SW-GW*cs)//2;oz=32
    FR(ox,oz,GW*cs,GD*cs,0xC8BC98)
    for i in range(GW+1):FR(ox+i*cs,oz,1,GD*cs,0xA89C78)
    for j in range(GD+1):FR(ox,oz+j*cs,GW*cs,1,0xA89C78)
    sx=ox+int((SAWMILL[0]-PLOT[0])/2*cs);sz=oz+int((SAWMILL[1]-PLOT[1])/2*cs)
    FR(sx-cs//2,sz-cs,cs,cs*2,0x707880)
    for b in BPS:
      x0=ox+b[0]*cs;z0=oz+b[1]*cs
      c=mix(WOODS[b[5]][1],0xF0D8A0,0.35) if b[5]>=0 else 0x60A0FF
      if b[2]!=lvl:c=shade(c,0.5)
      if b[3]==0:FR(x0+1,z0+1,cs-2,cs-2,c)
      elif b[3]==1:
        if b[4]%2==0:FR(x0,z0+cs//2-1,cs,3,c)
        else:FR(x0+cs//2-1,z0,3,cs,c)
      else:FR(x0+cs//2-2,z0+cs//2-2,5,5,c)
    box2(ox+cx*cs,oz+cz*cs,cs,cs,0xFFFF00)
    for b,lab,on in ((BB_FLOOR,"FLOOR",kind==0),(BB_WALL,"WALL",kind==1),(BB_PIL,"POST",kind==2),
                     (BB_ROT,"ROT",0),(BB_LVL,"LV"+str(lvl+1),0),(BB_DEL,"DEL",kind==3)):
      FR(b[0],b[1],b[2],b[3],0x806020 if on else 0x403010);box2(b[0],b[1],b[2],b[3],0xFFFFFF)
      textout(G,b[0]+(b[2]-len(lab)*7)//2,b[1]+6,lab,0xFFFFFF)
    FR(BB_DONE[0],BB_DONE[1],BB_DONE[2],BB_DONE[3],0x307030);box2(BB_DONE[0],BB_DONE[1],BB_DONE[2],BB_DONE[3],0xFFFFFF)
    textout(G,BB_DONE[0]+16,BB_DONE[1]+9,"DONE",0xFFFFFF)
    nb=sum(1 for b in BPS if b[5]<0)
    otext(4,206,msg[:34],0xFFFFFF)
    otext(4,222,str(nb)+" empty blueprints - drop planks on them",0xC0E0C0)
    flip()
    k=keyboard();pk=k&~prevk;prevk=k
    act=0
    if kd(pk,K_ESC) or kd(pk,K_MENU):save();release();return
    if kd(pk,K_LT):cx=max(0,cx-1)
    if kd(pk,K_RT):cx=min(GW-1,cx+1)
    if kd(pk,K_UP):cz=max(0,cz-1)
    if kd(pk,K_DN):cz=min(GD-1,cz+1)
    if kd(pk,K_ENTER):act=1
    if kd(pk,K_PLUS):kind=(kind+1)%4
    if kd(pk,K_DEL):kind=3;act=1
    p=touches()
    if p:
      q=p[0]
      if inside(BB_FLOOR,p):kind=0
      elif inside(BB_WALL,p):kind=1
      elif inside(BB_PIL,p):kind=2
      elif inside(BB_ROT,p):rot=(rot+1)%2;msg="Walls now "+("left-right" if rot==0 else "front-back")
      elif inside(BB_LVL,p):lvl=1-lvl;msg="Building on level "+str(lvl+1)
      elif inside(BB_DEL,p):kind=3;msg="Tap blueprints to remove them"
      elif inside(BB_DONE,p):save();release();return
      elif ox<=q[0]<ox+GW*cs and oz<=q[1]<oz+GD*cs:
        cx=int((q[0]-ox)//cs);cz=int((q[1]-oz)//cs);act=1
      release()
    if act:
      if kind==3:
        for b in BPS:
          if b[0]==cx and b[1]==cz and b[2]==lvl:
            BPS.remove(b);msg="Removed";break
      else:
        dup=[b for b in BPS if b[0]==cx and b[1]==cz and b[2]==lvl and b[3]==kind and (kind!=1 or b[4]==rot)]
        if dup:msg="Already a blueprint there"
        elif len(BPS)>=90:msg="Blueprint limit reached (90)"
        else:
          BPS.append([cx,cz,lvl,kind,rot,-1]);msg=["Floor","Wall","Post"][kind]+" blueprint placed"

#---------- main ----------
def title():
  FR(0,0,SW,SH,0x18301C)
  for i in range(9):
    x=10+i*36;h=40+(i*37)%50
    FR(x+8,200-h,6,h,0x5A3E26);poly([(x,200-h+10),(x+11,200-h-30),(x+22,200-h+10)],0x2E6B3A)
  FR(0,200,SW,40,0x3E7A38)
  bigtext("WOODLOT",20,6,0xFFD080,0x402000)
  ctext("chop - haul - saw - sell - build",62,0xFFFFFF)
  for i,s in enumerate(["< > turn    ^ v walk/drive",
                        "ACTION: chop, grab, drop, shop, drive",
                        "BUILD on your plot: place blueprints,",
                        "then drop planks on them to build",
                        "Sell wood on the green pad in town",
                        "Menu: map  Del: buttons  Esc: save+quit",
                        "","Tap or press Enter to start"]):
    ctext(s,84+i*14,0xE0F0E0 if i<7 else 0xFFFF80)
  flip()
  release()
  while True:
    k=keyboard()
    if kd(k,K_ESC):return 0
    if kd(k,K_ENTER):return 1
    if touches():
      release();return 1

def main():
  dimgrob(G,SW,SH,0)
  if not title():return
  newgame()
  gc.collect()
  last=ticks();prevk=keyboard();preva=0;prevb=0
  while True:
    now=ticks();dt=(now-last)/1000.0;last=now
    if dt>0.15:dt=0.15
    if dt<=0:dt=0.01
    k=keyboard();pk=k&~prevk;prevk=k
    pts=touches() if ST['btn'] else []
    if kd(k,K_ESC):
      save();return
    fw=kd(k,K_UP) or kd(k,K_8) or inside(B_FW,pts)
    bk=kd(k,K_DN) or kd(k,K_5) or inside(B_BK,pts)
    lt=kd(k,K_LT) or kd(k,K_4) or inside(B_LT,pts)
    rt=kd(k,K_RT) or kd(k,K_6) or inside(B_RT,pts)
    ta=inside(B_ACT,pts);tb=inside(B_BLD,pts)
    act=contextAction()
    hit=kd(pk,K_ENTER) or kd(pk,K_SPC) or (ta and not preva)
    #chopping: hold ACTION to keep swinging
    if act[0]=="CHOP" and (kd(k,K_ENTER) or kd(k,K_SPC) or ta):
      chop(act[1])
    elif hit:
      a,o=act
      if a=="DROP":dropHeld()
      elif a=="GRAB":grab(o)
      elif a=="SHOP":shopMenu(o);last=ticks();prevk=keyboard()
      elif a=="DRIVE":PL.mode=1;say("Driving - ACTION to get out",2)
      elif a=="EXIT":
        PL.mode=0;TR.v=0.0
        PL.x=TR.x-cos(TR.h)*2.0;PL.z=TR.z+sin(TR.h)*2.0
        if not walkable(PL.x,PL.z):PL.x=TR.x+cos(TR.h)*2.0;PL.z=TR.z-sin(TR.h)*2.0
    preva=ta
    if (kd(pk,K_MENU) and onPlot(PL.x,PL.z)) or (tb and not prevb and onPlot(PL.x,PL.z) and PL.mode==0):
      buildMode();last=ticks();prevk=keyboard()
    elif kd(pk,K_MENU):
      ST['map']=1-ST['map']
    prevb=tb
    if kd(pk,K_DEL):ST['btn']=1-ST['btn']
    update(dt,fw,bk,lt,rt)
    camera(dt)
    render()
    hud((lt,rt,fw,bk,ta,tb),act)
    flip()

main()
