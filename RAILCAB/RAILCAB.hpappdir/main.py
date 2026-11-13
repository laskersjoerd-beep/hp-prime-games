#RAILCAB - an original train-driving game for the HP Prime
#Drive from the cab, obey signals and speed limits, stop at the
#marker, open the doors and keep to the timetable.
#Python app (hpprime module). Touch + keyboard.
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
def rint(n):
  return int(rnd()*n)

G=1;GD=3;SW=320;SH=240;CX=160;HOR=64;F=200.0;CH=2.9;VH=160
SEG=8.0;MPH=2.23694
K_UP=2;K_DN=12;K_LT=7;K_RT=8;K_ESC=4;K_ENTER=30;K_MENU=13;K_DEL=19
K_PLUS=50;K_MINUS=45;K_7=32;K_9=34;K_SPC=49

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
  q=[]
  for v in p:q.append((I(v[0]),I(v[1])))
  fillpoly(G,q,c)
def L(x1,y1,x2,y2,c):
  line(G,I(x1),I(y1),I(x2),I(y2),c)
def T(x,y,s,c):
  textout(G,int(x),int(y),s,c)
def ctext(s,y,c):
  textout(G,(SW-len(s)*6)//2,y,s,c)
# 7-segment digit decals (drawn with rectangles, scale with the sign)
SEGS=("abcdef","bc","abged","abgcd","fgbc","afgcd","afgedc","abc","abcdefg","abcdfg")
def digits(cx,cy,hgt,s,c):
  #number s centred on (cx,cy), digit height hgt pixels
  w=hgt*0.55;t=max(1,hgt*0.16);gap=w*0.35;n=len(s)
  x0=cx-(n*w+(n-1)*gap)/2;y0=cy-hgt/2;hh=hgt/2
  for ch in s:
    for g in SEGS[ord(ch)-48]:
      if g=='a':FR(x0,y0,w,t,c)
      elif g=='b':FR(x0+w-t,y0,t,hh+t/2,c)
      elif g=='c':FR(x0+w-t,y0+hh-t/2,t,hh+t/2,c)
      elif g=='d':FR(x0,y0+hgt-t,w,t,c)
      elif g=='e':FR(x0,y0+hh-t/2,t,hh+t/2,c)
      elif g=='f':FR(x0,y0,t,hh+t/2,c)
      else:FR(x0,y0+hh-t/2,w,t,c)
    x0+=w+gap
def speedSign(cx,cy,R,v,ring=0xD82020,face=0xFFFFFF):
  #round speed-limit sign: red ring, white face, black number decal
  n=8 if R<6 else 14
  disc(cx,cy,R,ring,n)
  if R<2.5:return
  disc(cx,cy,R*0.74,face,n)
  if R>=4:digits(cx,cy,R*0.78,str(v),0x101010)

def mix(c,d,t):
  if t<=0:return c
  if t>1:t=1
  u=1-t
  return (int(((c>>16)&255)*u+((d>>16)&255)*t)<<16)|(int(((c>>8)&255)*u+((d>>8)&255)*t)<<8)|int((c&255)*u+(d&255)*t)
def shade(c,f):
  return (int(((c>>16)&255)*f)<<16)|(int(((c>>8)&255)*f)<<8)|int((c&255)*f)
def disc(x,y,r,c,n=12):
  p=[]
  for i in range(n):
    a=6.2832*i/n;p.append((x+r*cos(a),y+r*sin(a)))
  poly(p,c)

FONT={
'A':"0111010001111111000110001",'B':"1111010001111101000111110",
'R':"1111010001111101001010001",'I':"1111100100001000010011111",
'L':"1000010000100001000011111",'C':"0111110000100001000001111"}
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

#---------- world data ----------
# environments: sky bands, haze, ground a/b, ballast a/b, far layer, water, wires, rain
ENVS=[
 ((0x4F96E0,0x6FAEEA,0x93C4F0,0xBBDAF4),0xC6DDEE,0x8CBB58,0x83B150,0x938878,0x8A7F70,0x8FA6B8,0x2F7FC2,1,0,'day'),
 ((0x5F6B76,0x727E89,0x87929C,0x9DA7AF),0x9DA8AF,0x4C7A3A,0x467236,0x7C7670,0x746E68,0x55705E,0x3C6E86,0,1,'rain'),
 ((0x231D48,0x4B2F66,0x9A4C76,0xE88D63),0x7C5070,0x45403C,0x403B37,0x5C5650,0x56504B,0x2A2440,0x2D3A5C,1,0,'dusk')]
TUN=1;BRG=2;PLL=4;PLR=8;WAL=16
# scenery types
PINE=1;OAK=2;HOUSE=3;TOWER=4;ROCK=5;BOAT=6;HUT=7;LIGHT=8;BUSH=9;FACT=10

ROUTES=[
 ("Saltmere Coast Line","SC",0,70,8*3600+42*60,"2C14",
  ["Kittiwake Bay","Saltmere Pier","Gullhaven","Cobble Point","Port Arran"],[2300,2600,2100,2700]),
 ("Pinewood Valley Line","PV",1,85,13*3600+5*60,"1V07",
  ["Elmstead","Brackenford","Hollow Pines","Thornvale","Fernhill Jct"],[3000,3400,2800,3200]),
 ("Dusk Metro","DM",2,50,19*3600+48*60,"2M31",
  ["Vantor Central","Lumen Park","Ironbridge Row","Quartz Square","Halvard Docks","Northgate"],[1500,1400,1700,1500,1600])]
# name, class, vmax mph, accel, brake, length m, dial scale, cab colour, dash colour, body colour
TRAINS=[
 ("Class 271 Gull","271",75,1.0,1.15,80,100,0xB9C2CC,0x8C96A2,0x2F7FD0),
 ("Class 418 Kestrel","418",110,0.62,0.95,120,120,0x5A5E66,0x45484F,0xD03838),
 ("Class 156 Badger","156",60,0.8,1.0,46,80,0xCFC7AE,0x8F9A78,0x2E8A4E)]

RT={}
STN=[];SG=[];PAX=[];OB={}

NMAX=1800
BUF=[array('f',[0.0]*NMAX),array('f',[0.0]*NMAX),bytearray(NMAX),bytearray(NMAX),bytearray(NMAX),bytearray(NMAX),bytearray(NMAX)]
gc.collect()
def build(ri):
  global RT,STN,SG,PAX,OB
  RT={};STN=[];SG=[];PAX=[];OB={}
  gc.collect()
  name,code,env,ls,clk,hc,names,gaps=ROUTES[ri]
  seed(ri*7919+101)
  stops=[200.0]
  for g in gaps:stops.append(stops[-1]+g)
  endm=stops[-1]+24.0
  n=int(endm/SEG)+150
  curv=BUF[0];elev=BUF[1];flag=BUF[2];sl=BUF[3];sr=BUF[4];lim=BUF[5];hs=BUF[6]
  for j in range(NMAX):
    curv[j]=0.0;elev[j]=0.0;flag[j]=0;sl[j]=0;sr[j]=0;lim[j]=0
  for j in range(n):hs[j]=rint(256)
  PLAT=170.0
  zones=[]
  for s in stops:zones.append((s+10-PLAT-130,s+10+130))
  def dz(p):
    d=99999.0
    for a,b in zones:
      if p<a:e=a-p
      elif p>b:e=p-b
      else:e=0.0
      if e<d:d=e
    return d
  def ff(j):
    d=dz(j*SEG)
    return 1.0 if d>=100 else d/100.0
  # curves
  mags=(0.05,0.08,0.11,0.15) if env<2 else (0.05,0.07,0.1,0.13)
  j=0
  while j<n:
    Ln=12+rint(40)
    c=0.0
    if rnd()>0.38:c=mags[rint(4)]*(1 if rnd()<0.5 else -1)
    for k in range(Ln):
      if j+k>=n:break
      e=min(1.0,k/5.0,(Ln-1-k)/5.0)
      curv[j+k]=c*e
    j+=Ln
  # hills
  hf=(0.7,1.3,0.35)[env]
  e=0.0;gr=0.0;tg=0.0
  for j in range(n):
    if j%28==0:tg=(rnd()-0.5)*0.026*hf
    gr+=(tg-gr)*0.07
    f=ff(j)
    curv[j]*=f
    elev[j]=e;e+=gr*f*SEG
  # stations, platforms
  for i in range(len(stops)):
    s=stops[i];s1=s+10;s0=s1-PLAT
    STN.append([names[i],1+(i*3+ri*2+1)%(4 if env<2 else 6),s0,s1,s,0,0])
    for j in range(int(s0/SEG),int(s1/SEG)):
      flag[j]|=PLL
      if env==2 or i==0 or i==len(stops)-1:flag[j]|=PLR
  # tunnels and bridges in the gaps
  for i in range(len(stops)-1):
    a=int((stops[i]+150)/SEG);b=int((stops[i+1]-320)/SEG)
    room=b-a
    if room<30:continue
    if env==1 and rnd()<0.8:
      tl=min(room-12,32+rint(36));t0=a+6+rint(max(1,room-tl-12))
      for j in range(t0,t0+tl):flag[j]|=TUN
      r=1+(t0+tl)
      bl=7+rint(6);b0=r+8+rint(max(1,b-r-bl-10))
      if b0+bl<b and rnd()<0.7:
        for j in range(b0,b0+bl):
          if not flag[j]&TUN:flag[j]|=BRG
    elif env==0 and i==1:
      b0=a+room//3
      for j in range(b0,b0+24):flag[j]|=BRG
    elif env==2 and i in (1,3):
      b0=a+room//2
      for j in range(b0,b0+8):flag[j]|=BRG
  if env==2:
    for j in range(n):
      if not flag[j]&(PLL|BRG):flag[j]|=WAL
  # scenery
  for j in range(n):
    fl=flag[j]
    if fl&(TUN):continue
    h=hs[j];r1=rnd();r2=rnd()
    near=dz(j*SEG)<40
    if env==0:
      if fl&BRG:
        if r1<0.06:sl[j]=BOAT
        continue
      if near:
        if r1<0.5:sl[j]=HUT
        if r2<0.6:sr[j]=HOUSE
      else:
        if r1<0.05:sl[j]=BOAT
        elif r1<0.12:sl[j]=ROCK
        if r2<0.28:sr[j]=HOUSE
        elif r2<0.42:sr[j]=ROCK
        elif r2<0.6:sr[j]=BUSH
        elif r2<0.605:sr[j]=LIGHT
    elif env==1:
      if fl&BRG:continue
      if near:
        if r1<0.35:sl[j]=HOUSE
        if r2<0.3:sr[j]=OAK
      else:
        sl[j]=PINE if r1<0.55 else (OAK if r1<0.68 else (ROCK if r1<0.72 else 0))
        sr[j]=PINE if r2<0.55 else (OAK if r2<0.66 else (BUSH if r2<0.72 else 0))
    else:
      if fl&BRG:continue
      sl[j]=TOWER if r1<0.55 else (FACT if r1<0.65 else 0)
      sr[j]=TOWER if r2<0.55 else (FACT if r2<0.62 else 0)
  # speed limits
  vm=ls
  for j in range(n):
    ac=abs(curv[j]);Lm=ls
    if ac>0.125:Lm=min(ls,int(ls*0.6/5)*5)
    elif ac>0.085:Lm=min(ls,int(ls*0.78/5)*5)
    p=j*SEG
    if p<stops[0]+320:Lm=min(Lm,30)
    if p>stops[-1]-420:Lm=min(Lm,30 if p<stops[-1]-120 else 20)
    lim[j]=Lm
  # restrictions start 160 m early
  tmp=bytearray(lim)
  for j in range(n):
    m=tmp[j]
    for q in range(1,21):
      if j+q<n and tmp[j+q]<m:m=tmp[j+q]
    lim[j]=m
  # remove short faster sections (<240 m)
  j=1
  while j<n:
    if lim[j]>lim[j-1]:
      k=j
      while k<n and lim[k]>=lim[j]:k+=1
      if k<n and k-j<30:
        for q in range(j,k):lim[q]=lim[j-1]
        continue
    j+=1
  # objects
  def add(pos,o):
    s=int(pos/SEG)
    if s in OB:OB[s].append(o)
    else:OB[s]=[o]
  for j in range(1,n):
    if lim[j]!=lim[j-1]:add(j*SEG,(j*SEG,'L',lim[j],0))
  # signals: starters + automatics
  num=2
  for i in range(len(stops)):
    if i<len(stops)-1:
      SG.append([stops[i]+25,num,1,0,-1.0,0,i]);num+=2
      p=stops[i]+25+700+rint(300)
      while p<stops[i+1]-PLAT-260:
        SG.append([p,num,0,1 if rnd()<0.38 else 0,-1.0,0,-1]);num+=2
        p+=850+rint(400)
  for i in range(len(SG)):add(SG[i][0],(SG[i][0],'S',i,0))
  # platform furniture and passengers
  cols=(0xD04040,0x3A6FD0,0x40A050,0xE0B030,0x8050B0,0xE07830,0x30A0A0,0xF0F0F0)
  for i in range(len(STN)):
    st=STN[i];s0=st[2];s1=st[3];stop=st[4]
    add(stop,(stop,'M',0,0))
    p=s0+12
    while p<s1-5:
      add(p,(p,'B',i,-1))
      if flag[int(p/SEG)]&PLR:add(p+3,(p+3,'B',i,1))
      p+=45
    np=4+rint(5)
    if i==len(STN)-1:np=0
    for q in range(np):
      pp=stop-6-rnd()*100
      PAX.append([i,1])
      add(pp,(pp,'P',len(PAX)-1,-3.2-rnd()*3.5,rint(8)))
    for q in range(3+rint(4)):
      pp=s0+10+rnd()*(PLAT-20)
      if flag[int(pp/SEG)]&PLR:add(pp,(pp,'P',-1,6.2+rnd()*3.5,rint(8)))
  add(endm,(endm,'X',0,0))
  # timetable
  fac=(1.6,1.8,1.47)[TI[0]]*(1.0,1.0,0.93)[env]
  t=clk+14
  STN[0][5]=clk;STN[0][6]=t
  for i in range(1,len(STN)):
    a=int(STN[i-1][4]/SEG);b=int(STN[i][4]/SEG);s=0.0
    for j in range(a,b):s+=min(lim[j],TRAINS[TI[0]][2])
    avg=s/max(1,b-a)/MPH
    run=(STN[i][4]-STN[i-1][4])/avg*fac+5
    STN[i].append(avg)
    t+=run;STN[i][5]=int(t);t+=14;STN[i][6]=int(t)
  STN[0].append(10.0)
  RT={'n':n,'curv':curv,'elev':elev,'flag':flag,'sl':sl,'sr':sr,'lim':lim,'hs':hs,
      'env':env,'ri':ri,'fac':fac,'endm':endm,'ls':ls,'code':code,'clk':clk,'hc':hc,'name':name}
  # far scenery profile
  fh=bytearray(64)
  seed(ri*31+7)
  hgt=0
  for i in range(64):
    if env==0:
      v=0 if (i%32)<14 else int(6+10*sin((i%32-14)*0.18)+rint(4))
    elif env==1:
      hgt=(hgt+rint(9)-4)
      v=int(14+9*sin(i*0.2)+5*sin(i*0.53)+rint(3))
    else:
      v=4+rint(26) if rnd()<0.8 else 2
    fh[i]=max(0,v)
  RT['far']=fh
  gc.collect()

#---------- game state ----------
TI=[0];RI=[0]
DET=[1]
DDS=((60,20,1),(95,24,1),(140,28,1))
ST={}
def newgame():
  T=TRAINS[TI[0]]
  build(RI[0])
  st=STN[0]
  ST.clear()
  ST.update({'pos':st[4],'v':0.0,'tgt':0,'emerg':0,'doors':1,'doorT':0.0,'board':0.0,
    'ns':0,'score':0,'t':0.0,'msg':'Passengers boarding...','msgT':4.0,'msg2':'','map':0,
    'wipe':1 if RT['env']==1 else 0,'wa':1.1,'wd':1,'drops':[],'bgx':0.0,'pow':0.0,'brk':0.0,
    'over':0.0,'perfect':0,'ontime':0,'stops':0,'pen':0,'spad':0,'done':0,'nsig':0,
    'ot':[0,0.0,0.0,0],'ott':25.0,'arr':0,'pause':0,'unit':T[1]+'%03d'%(11+RI[0]*7+TI[0]*5),
    'hint':0,'fin':0,'lastLim':0,'ovt':0.0})
  gc.collect()

def say(s,t=3.0):
  ST['msg']=s;ST['msgT']=t
def award(p,s):
  # no point penalties: mistakes only show a message and are counted
  if p<0:
    ST['pen']+=1;say(s,3.0);return
  ST['score']+=p
  say(s+'  +%d'%p,3.0)

def sigRed(i):
  s=SG[i]
  if s[2]==1:return not s[5]
  if s[3]:return s[4]<0 or ST['t']<s[4]
  return 0
def aspect(i):
  if i>=len(SG):return 2
  if sigRed(i):return 0
  if i+1<len(SG) and sigRed(i+1):return 1
  return 2

def curLimit():
  lim=RT['lim'];T=TRAINS[TI[0]]
  p=ST['pos'];a=int(max(0,p-T[5])/SEG);b=int(p/SEG)
  m=255
  for j in range(a,b+1):
    if lim[j]<m:m=lim[j]
  return min(m,T[2])
def nextLimit():
  lim=RT['lim'];p=ST['pos'];b=int(p/SEG);c=lim[b]
  for j in range(b+1,min(RT['n'],b+120)):
    if lim[j]!=c:return lim[j],j*SEG-p
  return 0,0

def update(dt):
  T=TRAINS[TI[0]]
  vmax=T[2]/MPH;a0=T[3];bk=T[4];tl=T[5]
  v=ST['v'];tgt=ST['tgt']/MPH
  ST['t']+=dt
  power=0.0;brake=0.0;dec=0.0
  if ST['emerg']:
    dec=1.5
    if v<=0:ST['emerg']=0
  elif ST['doors']:
    brake=1.0
  else:
    err=tgt-v
    if err>0.08:power=min(1.0,err*0.9)
    elif err<-0.2:brake=min(1.0,0.25-err*0.7)
    if tgt<=0 and v<3.0:brake=1.0
  ST['pow']=power;ST['brk']=1.0 if ST['emerg'] else brake
  acc=0.0
  if power>0:
    v1=0.42*vmax
    acc=power*a0*(1.0 if v<v1 else v1/v)
  # gradient + resistance
  elev=RT['elev'];j=int(ST['pos']/SEG)
  if j<RT['n']-1:acc-=9.81*(elev[j+1]-elev[j])/SEG
  acc-=0.006+0.00005*v*v
  acc-=brake*bk+dec
  if v<=0.0 and acc<0:acc=0.0
  v+=acc*dt
  if v<0:v=0.0
  if v>vmax:v=vmax
  if v<0.03 and (brake>0 or dec>0):v=0.0
  ST['v']=v
  old=ST['pos'];ST['pos']=old+v*dt;pos=ST['pos']
  # background parallax
  ST['bgx']+=RT['curv'][j]*v*dt*F/(SEG*SEG)*0.9
  # signals
  i=ST['nsig']
  while i<len(SG) and SG[i][0]<pos-0.01:
    if SG[i][0]>old-0.01 and sigRed(i):
      ST['spad']+=1;ST['emerg']=1
      award(-400,'SPAD! Signal at danger')
      SG[i][5]=1;SG[i][3]=0
    i+=1
  ST['nsig']=i
  for q in range(i,min(len(SG),i+3)):
    s=SG[q]
    if s[2]==0 and s[3] and s[4]<0 and s[0]-pos<1050:s[4]=ST['t']+6+rnd()*18
    if s[2]==1 and s[6]<ST['ns']:s[5]=1
  # speed limit / overspeed
  lm=curLimit();mph=v*MPH
  if mph>lm+3:
    ST['over']+=dt;ST['ovt']+=dt
    if ST['ovt']>=1.0:
      ST['ovt']-=1.0
    if mph>lm+12 and not ST['emerg']:
      ST['emerg']=1;award(-100,'OVERSPEED TRIP')
  else:
    ST['ovt']=0.0
  # stations
  ns=ST['ns']
  if ns<len(STN):
    st=STN[ns]
    if pos>st[3]+6 and ST['doors']==0:
      award(-300,'Missed '+st[0]+'!')
      ST['ns']=ns+1
      if ns+1>=len(STN):ST['done']=2
  # doors
  if ST['doors']==1:
    ST['doorT']+=dt;ST['board']+=dt
    if ST['board']>0.75:
      ST['board']=0.0
      for p in PAX:
        if p[0]==ns and p[1]:
          p[1]=0;break
    if ns==len(STN)-1 and ST['doorT']>6:ST['done']=1
  elif ST['doors']==2:
    ST['doorT']+=dt
    if ST['doorT']>2.0:
      ST['doors']=0
      ST['ns']=ns+1
      say('Doors closed - signal clear. Depart!',3)
  # buffers
  if pos>RT['endm']-0.5:
    ST['pos']=RT['endm']-0.5;ST['v']=0.0
    if not ST['done']:award(-500,'Hit the buffers!');ST['done']=1
  # brake hint
  ST['hint']=0
  if ns<len(STN) and not ST['doors']:
    rem=STN[ns][4]-pos
    if 0<rem<1200 and tgt>0 and v>1:
      if v*v/(2*max(rem,1.0))>0.62*bk:ST['hint']=1
  if i<len(SG) and sigRed(i):
    rem=SG[i][0]-pos-12
    if 0<rem<900 and v>1 and v*v/(2*max(rem,1.0))>0.62*bk:ST['hint']=2
  # oncoming train
  ot=ST['ot']
  if ot[0]:
    ot[1]-=ot[2]*dt
    if ot[1]<pos-20:ot[0]=0;ST['ott']=40+rnd()*70
  else:
    ST['ott']-=dt
    if ST['ott']<0 and pos+900<RT['endm']:
      ot[0]=1;ot[1]=pos+DDS[DET[0]][0]*SEG+150;ot[2]=18+rnd()*14;ot[3]=rint(3)
  # rain
  if RT['env']==1:
    d=ST['drops']
    if len(d)<28 and rnd()<dt*(9+v*0.3):d.append([50+rnd()*220,14+rnd()*136])
    for q in d:q[1]+=dt*(4+v*0.25)
  if ST['wipe']:
    ST['wa']+=ST['wd']*dt*2.6
    if ST['wa']>3.05:ST['wa']=3.05;ST['wd']=-1
    if ST['wa']<1.08:ST['wa']=1.08;ST['wd']=1
    d=ST['drops'];k=0
    while k<len(d):
      q=d[k];a=atan2(159-q[1],q[0]-200)
      if abs(a-ST['wa'])<0.18 and (q[0]-200)**2+(159-q[1])**2<150*150:d.pop(k)
      else:k+=1
  if ST['msgT']>0:ST['msgT']-=dt

def atPlatform():
  ns=ST['ns']
  if ns>=len(STN):return 0
  st=STN[ns];p=ST['pos']
  return st[2]+TRAINS[TI[0]][5]-2<=p<=st[3]+1

def doorButton():
  d=ST['doors']
  if d==0:
    if ST['v']>0.05:say('Stop the train first',2);return
    if not atPlatform():
      if ST['ns']<len(STN) and ST['pos']<STN[ST['ns']][4]:say('Pull up to the STOP marker',2)
      else:say('Not at a platform',2)
      return
    ST['doors']=1;ST['doorT']=0.0;ST['board']=-1.0
    ns=ST['ns'];st=STN[ns]
    off=ST['pos']-st[4];ad=abs(off)
    pts=0
    if ad<=1.5:pts=150;txt='Perfect stop!'
    elif ad<=5:pts=100;txt='Good stop'
    elif ad<=12:pts=50;txt='Stop OK'
    else:pts=10;txt='Long way from marker'
    ST['stops']+=1
    if ad<=1.5:ST['perfect']+=1
    late=ST['t']+RT['clk']-st[5]
    if -60<=late<=30:pts+=100;txt+=' On time';ST['ontime']+=1
    elif -120<=late<=90:pts+=50;txt+=' Near time'
    else:txt+=(' Late' if late>0 else ' Early')
    ST['arr']=late
    award(pts,txt)
  elif d==1:
    left=0
    for p in PAX:
      if p[0]==ST['ns'] and p[1]:left+=1
    if ST['ns']==len(STN)-1:say('Terminus - passengers leaving',2);return
    if left or ST['doorT']<3:say('Passengers still boarding',1.5);return
    ST['doors']=2;ST['doorT']=0.0
    say('Doors closing...',2)

#---------- renderer ----------
NB=[0]*128;BZ=[0.0]*128;BX=[0.0]*128;BY=[0.0]*128;BS=[0.0]*128;BW=[0.0]*128;BE=[0.0]*128
CAMY=[0.0];NBM=[0]

def project(cam):
  curv=RT['curv'];elev=RT['elev'];n=RT['n']
  base=int(cam/SEG)
  if base>n-4:base=n-4
  frac=cam/SEG-base
  camY=elev[base]+(elev[base+1]-elev[base])*frac+CH
  CAMY[0]=camY
  dd,nearc,_=DDS[DET[0]]
  x=0.0;dx=-curv[base]*frac
  j=base;m=0;k=0
  mid=nearc*3
  while m<127:
    x+=dx;dx+=curv[j];j+=1
    if j>=n-1:break
    k+=1
    if k>mid:
      if k&3:continue
    elif k>nearc and (k&1):continue
    if k>dd:break
    z=j*SEG-cam
    if z<1.0:z=1.0
    s=F/z
    NB[m]=j;BZ[m]=z;BW[m]=x;BE[m]=elev[j];BS[m]=s
    BX[m]=CX+x*s;BY[m]=HOR+(camY-elev[j])*s
    m+=1
  NBM[0]=m
  return m

def projZ(zr):
  m=NBM[0]
  if m<2:return None
  if zr<BZ[0]:return None
  k=0
  while k<m-2 and BZ[k+1]<zr:k+=1
  z0=BZ[k];z1=BZ[k+1]
  t=(zr-z0)/(z1-z0) if z1>z0 else 0
  if t>1:t=1.0
  wx=BW[k]+(BW[k+1]-BW[k])*t;we=BE[k]+(BE[k+1]-BE[k])*t
  if zr<1.0:zr=1.0
  s=F/zr
  return (CX+wx*s,HOR+(CAMY[0]-we)*s,s,k)

def sky():
  E=ENVS[RT['env']];sk=E[0]
  FR(0,0,SW,22,sk[0]);FR(0,22,SW,16,sk[1]);FR(0,38,SW,14,sk[2]);FR(0,52,SW,HOR-52+1,sk[3])
  env=RT['env']
  o=int(ST['bgx'])%640
  if env==2:disc(230-o*0.2%320,HOR-6,14,0xFFB060)
  if env==0:FR(0,HOR-3,SW,5,E[7])
  fh=RT['far'];p=[(0,HOR+2)]
  if env==2:
    for x in range(0,330,10):
      h=fh[((x+o)//10)%64];p.append((x,HOR-h));p.append((x+10,HOR-h))
  else:
    for x in range(0,330,10):p.append((x,HOR-fh[((x+o)//10)%64]))
  p.append((SW,HOR+2))
  poly(p,E[6])
  FR(0,HOR+1,SW,VH-HOR,mix(E[2],E[1],0.85))

def scen(t,side,bx,by,s,h,fg,hz,env):
  if t==PINE:
    X=side*(6+(h&15)*1.2);x=bx+X*s;H=8+(h>>4)*0.5
    FR(x-0.3*s,by-2*s,0.6*s,2*s,mix(0x5A3C22,hz,fg))
    c=mix(0x2F5A2A,hz,fg)
    poly(((x,by-H*s),(x-2.6*s,by-1.8*s),(x+2.6*s,by-1.8*s)),c)
    poly(((x,by-(H+1.5)*s),(x-1.6*s,by-H*0.55*s),(x+1.6*s,by-H*0.55*s)),mix(0x3B6C33,hz,fg))
  elif t==OAK:
    X=side*(7+(h&15));x=bx+X*s;r=2.6+(h>>5)*0.3
    FR(x-0.3*s,by-2.5*s,0.6*s,2.5*s,mix(0x5A3C22,hz,fg))
    c=mix(0x4A7A32 if env<2 else 0x2E4A2A,hz,fg);y=by-(2.5+r)*s
    poly(((x-r*s,y),(x-r*0.6*s,y-r*0.85*s),(x+r*0.6*s,y-r*0.85*s),(x+r*s,y),(x+r*0.6*s,y+r*0.8*s),(x-r*0.6*s,y+r*0.8*s)),c)
  elif t==HOUSE:
    X=side*(10+(h&15)*0.8);x=bx+X*s;w=7+(h&3);hh=5+(h>>6)
    pal=(0xF2E3C4,0xE7B8A0,0xBFD6E8,0xF4F0E6,0xD8E4B8,0xF0C870)
    c=pal[h%6] if env!=1 else (0xD8CFC0,0xC9B79C,0xE6E0D2)[h%3]
    FR(x-w*s/2,by-hh*s,w*s,hh*s,mix(c,hz,fg))
    poly(((x-w*s/2-0.5*s,by-hh*s),(x,by-(hh+3)*s),(x+w*s/2+0.5*s,by-hh*s)),mix(0x8A3A30 if h&1 else 0x50545C,hz,fg))
    if s>0.5:
      wc=mix(0x30404C,hz,fg)
      FR(x-w*s/4-0.6*s,by-hh*0.7*s,1.2*s,1.2*s,wc);FR(x+w*s/4-0.6*s,by-hh*0.7*s,1.2*s,1.2*s,wc)
  elif t==TOWER:
    X=side*(16+(h&15)*1.6);x=bx+X*s;w=12+(h&7)*1.5;hh=22+(h>>3)*1.4
    c=mix((0x3A3A50,0x4A4058,0x30384A,0x504A5A)[h&3],hz,fg*0.8)
    FR(x-w*s/2,by-hh*s,w*s,hh*s,c)
    if w*s>14:
      lit=(0xFFD27A,0xFFB050,0xBFE0FF)
      cw=max(1,int(1.6*s));rr=int(hh/4)
      for q in range(8):
        hq=(h*7+q*29)&255
        if hq<120:continue
        cx=x-w*s/2+((hq>>2)%4+0.5)*w*s/4.2;cy=by-hh*s+((hq*3)%rr+0.6)*4*s
        FR(cx,cy,cw*1.6,cw,lit[hq%3])
  elif t==ROCK:
    r=1.5+(h>>5)*0.5;X=side*(4.5+r*1.7+(h&15)*0.5);x=bx+X*s;hh=r*(1.4 if env==0 else 1)
    poly(((x-r*1.5*s,by),(x-r*s,by-hh*s),(x,by-hh*1.5*s),(x+r*1.1*s,by-hh*0.9*s),(x+r*1.6*s,by)),mix(0x8C8478 if env==0 else 0x6E6A64,hz,fg))
  elif t==BOAT:
    X=side*(45+(h&63));x=bx+X*s;yy=by
    poly(((x-3*s,yy-0.8*s),(x+3*s,yy-0.8*s),(x+2*s,yy),(x-2*s,yy)),mix(0x8A4A2A,hz,fg))
    poly(((x,yy-6*s),(x,yy-0.8*s),(x+2.6*s,yy-0.8*s)),mix(0xF4F4F0,hz,fg))
  elif t==HUT:
    X=side*(7+(h&7));x=bx+X*s
    FR(x-1.2*s,by-2.4*s,2.4*s,2.4*s,mix((0xE05050,0x50A0E0,0xF0D040,0x50C080)[h&3],hz,fg))
    poly(((x-1.5*s,by-2.4*s),(x,by-3.4*s),(x+1.5*s,by-2.4*s)),mix(0xF4F0E8,hz,fg))
  elif t==LIGHT:
    X=side*24;x=bx+X*s
    FR(x-1.2*s,by-16*s,2.4*s,16*s,mix(0xF4F4F4,hz,fg));FR(x-1.2*s,by-11*s,2.4*s,2.4*s,mix(0xD03030,hz,fg))
    FR(x-0.8*s,by-18*s,1.6*s,2*s,0xFFF0A0)
  elif t==BUSH:
    r=1+(h>>6)*0.4;X=side*(4+r*1.8+(h&15)*0.5);x=bx+X*s
    poly(((x-r*1.6*s,by),(x-r*s,by-r*1.2*s),(x+r*s,by-r*1.3*s),(x+r*1.7*s,by)),mix(0x4F8A3A,hz,fg))
  elif t==FACT:
    X=side*(20+(h&15));x=bx+X*s;w=18;hh=9
    FR(x-w*s/2,by-hh*s,w*s,hh*s,mix(0x4A4044,hz,fg*0.8))
    FR(x+w*s/4,by-(hh+10)*s,1.6*s,10*s,mix(0x5A4C48,hz,fg*0.8))
    if s>0.4:FR(x-w*s/3,by-hh*0.6*s,w*s*0.6,1.0*s,0xFFC070)

def person(x,y,s,c,fg,hz):
  FR(x-0.22*s,y-0.85*s,0.44*s,0.85*s,mix(0x2A2A38,hz,fg))
  FR(x-0.28*s,y-1.5*s,0.56*s,0.7*s,mix(c,hz,fg))
  FR(x-0.15*s,y-1.82*s,0.3*s,0.32*s,mix(0xE8B890,hz,fg))

def drawObj(o,k,fg,hz,env):
  p=projZ(o[0]-ST['pos'])
  if not p:return
  bx,by,s,_=p
  kd_=o[1]
  if kd_=='S':
    i=o[2];a=aspect(i) if i>=ST['nsig'] else 0
    x=bx-2.5*s
    FR(x-0.09*s,by-4.4*s,max(1,0.18*s),4.4*s,0x38383C)
    FR(x-0.36*s,by-6.2*s,max(2,0.72*s),max(3,1.9*s),0x0C0C0C)
    lc=(0xFF2020,0xFFC020,0x20FF60)[a]
    ly=(by-4.6*s,by-5.2*s,by-5.8*s)[a]
    r=max(1,0.26*s)
    if s>4:
      for q in range(3):
        if q!=a:FR(x-r,(by-4.6*s,by-5.2*s,by-5.8*s)[q]-r,2*r,2*r,0x2A2A2A)
    FR(x-r,ly-r,2*r,2*r,lc)
    if s>7:
      FR(x-0.3*s,by-3.4*s,0.6*s,0.4*s,0xF0F0F0)
  elif kd_=='L':
    x=bx-2.6*s
    FR(x-0.07*s,by-2.6*s,max(1,0.14*s),2.6*s,0x505050)
    speedSign(x,by-3.35*s,max(1.5,0.8*s),o[2],mix(0xD82020,hz,fg*0.5),mix(0xFFFFFF,hz,fg*0.5))
  elif kd_=='B':
    side=o[3];x=bx+(-6.6 if side<0 else 9.6)*s;y=by-0.95*s
    w=4.6*s
    L(x-w*0.4,y,x-w*0.4,y-2.2*s,0x404040);L(x+w*0.4,y,x+w*0.4,y-2.2*s,0x404040)
    FR(x-w/2,y-3.0*s,w,max(1,0.8*s),mix(0x1E3A78 if env!=2 else 0x5A1E5A,hz,fg))
    nm=STN[o[2]][0]
    if w>len(nm)*6+4:T(x-len(nm)*3,y-3.0*s+(0.8*s-10)/2,nm,0xFFFFFF)
  elif kd_=='M':
    x=bx-1.9*s
    FR(x-0.04*s,by-1.4*s,max(1,0.08*s),1.4*s,0x303030)
    FR(x-0.35*s,by-2.1*s,max(2,0.7*s),max(2,0.7*s),0xF8F8F8)
    if s>6:FR(x-0.2*s,by-1.95*s,0.4*s,0.4*s,0x101010)
  elif kd_=='P':
    pid=o[2]
    if pid>=0 and not PAX[pid][1]:return
    c=(0xD04040,0x3A6FD0,0x40A050,0xE0B030,0x8050B0,0xE07830,0x30A0A0,0xF0F0F0)[o[4]]
    person(bx+o[3]*s,by-0.95*s,s,c,fg,hz)
  elif kd_=='X':
    FR(bx-1.1*s,by-1.2*s,2.2*s,0.6*s,0xC02020)
    FR(bx-1.0*s,by-0.6*s,0.25*s,0.6*s,0x303030);FR(bx+0.75*s,by-0.6*s,0.25*s,0.6*s,0x303030)
    FR(bx-0.2*s,by-1.6*s,0.4*s,0.4*s,0xFF3030)

def drawOther(fg,hz):
  ot=ST['ot']
  zf=ot[1]-ST['pos']
  p=projZ(zf)
  if not p:return
  zr=zf+70
  q=projZ(zr)
  bx,by,s,_=p
  body=(0x2F7FD0,0xD07A20,0x30A060)[ot[3]]
  if q:
    qx,qy,qs,_=q
    poly(((bx+2.5*s,by-0.5*s),(bx+2.5*s,by-3.9*s),(qx+2.5*qs,qy-3.9*qs),(qx+2.5*qs,qy-0.5*qs)),mix(shade(body,0.75),hz,fg))
    poly(((bx+2.5*s,by-2.4*s),(bx+2.5*s,by-3.1*s),(qx+2.5*qs,qy-3.1*qs),(qx+2.5*qs,qy-2.4*qs)),mix(0x1A2430,hz,fg))
  FR(bx+2.5*s,by-3.9*s,2.8*s,3.4*s,mix(body,hz,fg))
  FR(bx+2.5*s,by-1.6*s,2.8*s,1.1*s,mix(0xF0D020,hz,fg))
  FR(bx+2.75*s,by-3.5*s,2.3*s,1.0*s,0x182028)
  FR(bx+2.75*s,by-1.3*s,0.4*s,0.3*s,0xFFFFE0);FR(bx+4.65*s,by-1.3*s,0.4*s,0.3*s,0xFFFFE0)

def render():
  R=RT;env=R['env'];E=ENVS[env]
  flag=R['flag'];sl=R['sl'];sr=R['sr'];hs=R['hs']
  cam=ST['pos']
  m=project(cam)
  sky()
  hz=E[1];g1=E[2];g2=E[3];b1=E[4];b2=E[5];water=E[7];wires=E[8]
  maxz=BZ[m-1] if m>0 else 1.0
  camY=CAMY[0]
  sleep=DDS[DET[0]][2]
  ot=ST['ot'];otz=ot[1]-cam if ot[0] else -1
  for k in range(m-2,-1,-1):
    jn=NB[k];jf=NB[k+1]
    xn=BX[k];yn=BY[k];sn=BS[k];xf=BX[k+1];yf=BY[k+1];sf=BS[k+1]
    zn=BZ[k]
    fg=zn/maxz;fg=fg*fg*0.85
    fl=flag[jn]
    vis=yn>yf-0.5
    if vis and yf<VH:
      y0=yf;h=yn-yf+1
      if fl&TUN:FR(0,y0,SW,h,0x1E1C1A)
      elif fl&BRG:FR(0,y0,SW,h,mix(water,hz,fg))
      else:
        FR(0,y0,SW,h,mix(g1 if (jn>>1)&1 else g2,hz,fg))
        if env==0:
          poly(((-1,yf),(xf-15*sf,yf),(xn-15*sn,yn),(-1,yn)),mix(0xE6D2A0,hz,fg))
          poly(((-1,yf),(xf-24*sf,yf),(xn-24*sn,yn),(-1,yn)),mix(water if (jn>>2)&1 else shade(water,0.92),hz,fg))
      bc=b1 if jn&1 else b2
      if fl&TUN:bc=mix(bc,0x101010,0.55+fg*0.4)
      poly(((xn-2.1*sn,yn),(xn+6.0*sn,yn),(xf+6.0*sf,yf),(xf-2.1*sf,yf)),mix(bc,hz,fg))
      # sleepers
      if sleep and zn<26:
        z0=BZ[k];z1=BZ[k+1];w0=BW[k];w1=BW[k+1];e0=BE[k];e1=BE[k+1]
        t=ceil((cam+z0)/0.9)*0.9-cam
        sc=0x4A3C30 if env==1 else 0x6E6A64
        while t<z1:
          if t>4.5:
            u=(t-z0)/(z1-z0);s=F/t
            wx=CX+(w0+(w1-w0)*u)*s;wy=HOR+(camY-(e0+(e1-e0)*u))*s
            hh=CH*F*0.22/(t*t)
            if wy<VH:
              FR(wx-1.3*s,wy-hh,2.6*s,hh,sc)
              if t<16:FR(wx+2.6*s,wy-hh,2.6*s,hh,sc)
          t+=0.9
      # rails
      rc=0xB8B2AA if not fl&TUN else 0x5A5652
      if k<5:
        for X in (-0.75,0.67):
          poly(((xn+X*sn,yn),(xn+(X+0.08)*sn,yn),(xf+(X+0.08)*sf,yf),(xf+X*sf,yf)),rc)
      else:
        L(xn-0.72*sn,yn,xf-0.72*sf,yf,rc);L(xn+0.72*sn,yn,xf+0.72*sf,yf,rc)
      if zn<450:
        L(xn+3.18*sn,yn,xf+3.18*sf,yf,rc);L(xn+4.62*sn,yn,xf+4.62*sf,yf,rc)
    # platforms
    if fl&PLL:
      pc=mix(0xA8A49C,hz,fg)
      poly(((xn-1.6*sn,yn),(xn-1.6*sn,yn-0.95*sn),(xf-1.6*sf,yf-0.95*sf),(xf-1.6*sf,yf)),mix(0x58544E,hz,fg))
      poly(((xn-1.6*sn,yn-0.95*sn),(xn-8*sn,yn-0.95*sn),(xf-8*sf,yf-0.95*sf),(xf-1.6*sf,yf-0.95*sf)),pc)
      L(xn-1.95*sn,yn-0.95*sn,xf-1.95*sf,yf-0.95*sf,0xF0D020)
      poly(((xn-8*sn,yn-0.95*sn),(xn-8*sn,yn-3.6*sn),(xf-8*sf,yf-3.6*sf),(xf-8*sf,yf-0.95*sf)),mix(0x8E6A54 if env!=2 else 0x5E5266,hz,fg))
      if jn%3==0:FR(xn-5.3*sn,yn-4.5*sn,max(1,0.25*sn),3.55*sn,mix(0x40464E,hz,fg))
      poly(((xn-3.2*sn,yn-4.5*sn),(xn-8*sn,yn-4.5*sn),(xf-8*sf,yf-4.5*sf),(xf-3.2*sf,yf-4.5*sf)),mix(0x6A6E76 if jn&1 else 0x62666E,hz,fg))
    if fl&PLR:
      pc=mix(0xA8A49C,hz,fg)
      poly(((xn+5.5*sn,yn),(xn+5.5*sn,yn-0.95*sn),(xf+5.5*sf,yf-0.95*sf),(xf+5.5*sf,yf)),mix(0x58544E,hz,fg))
      poly(((xn+5.5*sn,yn-0.95*sn),(xn+12*sn,yn-0.95*sn),(xf+12*sf,yf-0.95*sf),(xf+5.5*sf,yf-0.95*sf)),pc)
      L(xn+5.85*sn,yn-0.95*sn,xf+5.85*sf,yf-0.95*sf,0xF0D020)
      if jn%3==0:FR(xn+8.6*sn,yn-4.5*sn,max(1,0.25*sn),3.55*sn,mix(0x40464E,hz,fg))
      poly(((xn+7*sn,yn-4.5*sn),(xn+12*sn,yn-4.5*sn),(xf+12*sf,yf-4.5*sf),(xf+7*sf,yf-4.5*sf)),mix(0x6A6E76 if jn&1 else 0x62666E,hz,fg))
    # city walls
    if fl&WAL:
      wc=mix(0x8A4A38 if jn&1 else 0x7E4434,hz,fg)
      poly(((xn-4.2*sn,yn),(xn-4.2*sn,yn-2.8*sn),(xf-4.2*sf,yf-2.8*sf),(xf-4.2*sf,yf)),wc)
      poly(((xn+8.4*sn,yn),(xn+8.4*sn,yn-2.8*sn),(xf+8.4*sf,yf-2.8*sf),(xf+8.4*sf,yf)),wc)
    # bridges
    if fl&BRG:
      gc_=mix(0x50565E,hz,fg)
      L(xn-2.4*sn,yn-1.3*sn,xf-2.4*sf,yf-1.3*sf,gc_);L(xn-2.4*sn,yn,xf-2.4*sf,yf,gc_)
      L(xn+6.3*sn,yn-1.3*sn,xf+6.3*sf,yf-1.3*sf,gc_);L(xn+6.3*sn,yn,xf+6.3*sf,yf,gc_)
      L(xn-2.4*sn,yn,xn-2.4*sn,yn-1.3*sn,gc_);L(xn+6.3*sn,yn,xn+6.3*sn,yn-1.3*sn,gc_)
      if jn%4==0:FR(xn-2.6*sn,yn,8.9*sn,4*sn,mix(0x6A6660,hz,fg))
    # scenery
    if not fl&TUN:
      by=yn
      if sl[jn] and not fl&PLL:scen(sl[jn],-1,xn,by,sn,hs[jn],fg,hz,env)
      if sr[jn] and not fl&PLR:scen(sr[jn],1,xn+3.9*sn,by,sn,hs[jn]^0x5A,fg,hz,env)
    # tunnel
    if fl&TUN:
      dk=0.15+0.85*(1-min(1.0,zn/160.0))
      tc=shade(0x6A645C if jn&1 else 0x605A54,dk*0.8)
      poly(((xn-2.8*sn,yn),(xn-2.8*sn,yn-4.8*sn),(xf-2.8*sf,yf-4.8*sf),(xf-2.8*sf,yf)),tc)
      poly(((xn+6.7*sn,yn),(xn+6.7*sn,yn-4.8*sn),(xf+6.7*sf,yf-4.8*sf),(xf+6.7*sf,yf)),tc)
      tc2=shade(tc,0.8)
      poly(((xn-2.8*sn,yn-4.8*sn),(xn-0.8*sn,yn-6.6*sn),(xn+4.7*sn,yn-6.6*sn),(xn+6.7*sn,yn-4.8*sn),(xf+6.7*sf,yf-4.8*sf),(xf+4.7*sf,yf-6.6*sf),(xf-0.8*sf,yf-6.6*sf),(xf-2.8*sf,yf-4.8*sf)),tc2)
      if jn%5==0:FR(xn-2.7*sn,yn-3.2*sn,0.3*sn,0.3*sn,0xFFE8A0)
      if not flag[jn-1]&TUN:
        L_=xn-2.8*sn;R_=xn+6.7*sn;Tt=yn-6.6*sn;yt=yn-28*sn
        hc=mix(0x4C6A3C,hz,fg);sc=mix(0x7A746A,hz,fg)
        FR(L_-60*sn,yt,60*sn,yn-yt,hc);FR(R_,yt,60*sn,yn-yt,hc);FR(L_,yt,R_-L_,Tt-yt,hc)
        poly(((L_-60*sn,yt),(xn-20*sn,yn-36*sn),(xn+10*sn,yn-40*sn),(R_+60*sn,yt)),hc)
        FR(L_-0.8*sn,Tt-1.2*sn,R_-L_+1.6*sn,1.2*sn,sc)
        FR(L_-0.8*sn,Tt,0.8*sn,yn-Tt,sc);FR(R_,Tt,0.8*sn,yn-Tt,sc)
    # catenary
    if wires:
      if zn<440:
        wcl=mix(0x202428,hz,fg)
        L(xn,yn-5.6*sn,xf,yf-5.6*sf,wcl);L(xn+3.9*sn,yn-5.6*sn,xf+3.9*sf,yf-5.6*sf,wcl)
        if zn<120:L(xn,yn-6.6*sn,xf,yf-6.6*sf,wcl)
      if jn%6<(jf-jn) and zn<620:
        mc=mix(0x4A4E54,hz,fg);w=max(1,0.28*sn)
        if fl&TUN:
          FR(xn-0.8*sn,yn-6.6*sn,5.5*sn,max(1,0.2*sn),mc)
        else:
          FR(xn-(2.6 if not fl&PLL else 8.3)*sn,yn-7.2*sn,w,7.2*sn,mc)
          FR(xn+(6.6 if not fl&PLR else 12.3)*sn,yn-7.2*sn,w,7.2*sn,mc)
          FR(xn-(2.6 if not fl&PLL else 8.3)*sn,yn-7.3*sn,(9.2+(0 if not fl&PLL else 5.7)+(0 if not fl&PLR else 5.7))*sn,max(1,0.35*sn),mc)
    # objects in these segments
    for j in range(jf-1,jn-1,-1):
      ol=OB.get(j)
      if ol:
        for o in ol:drawObj(o,k,fg,hz,env)
    if otz>=zn and otz<BZ[k+1]:drawOther(fg,hz)

#---------- cab and HUD ----------
BTN={'door':(168,163,29,23),'wipe':(199,163,28,23),'stop':(168,188,29,23),
     'map':(199,188,28,23),'dn':(168,213,29,25),'up':(199,213,28,25)}
DCX=319;DCY=239;DR=66

DASH=[]
def dashPrep():
  # precompute the dial geometry once per train (no off-screen grob)
  T=TRAINS[TI[0]];sc=T[6]
  DASH[:]=[]
  p1=[(DCX,DCY)];p2=[(DCX,DCY)];p3=[(DCX,DCY)]
  for i in range(16):
    a=1.5708*i/15
    p1.append((int(DCX-(DR+3)*cos(a)),int(DCY-(DR+3)*sin(a))))
    p2.append((int(DCX-DR*cos(a)),int(DCY-DR*sin(a))))
  for i in range(7):
    a=1.5708*i/6;p3.append((int(DCX-15*cos(a)),int(DCY-15*sin(a))))
  ticks_=[];labs=[]
  for v in range(0,sc+1,10):
    a=1.5708*v/sc;ca=cos(a);sa=sin(a)
    r0=DR-(9 if v%20==0 else 5)
    ticks_.append((int(DCX-r0*ca),int(DCY-r0*sa),int(DCX-(DR-1)*ca),int(DCY-(DR-1)*sa)))
    if v%20==0 and v>0:
      t=str(v);labs.append((int(min(DCX-(DR-19)*ca-len(t)*3,316-len(t)*6)),int(DCY-(DR-19)*sa-5),t))
  DASH.extend([p1,p2,p3,ticks_,labs])

def icons():
  # DOOR: two door leaves sliding apart
  x,y=168,163
  FR(x+8,y+5,6,14,0xFFE070);FR(x+15,y+5,6,14,0xFFE070)
  FR(x+9,y+7,4,4,0x5A4A18);FR(x+16,y+7,4,4,0x5A4A18)
  fillpoly(G,[(x+2,y+12),(x+6,y+9),(x+6,y+15)],0xFFE070)
  fillpoly(G,[(x+27,y+12),(x+23,y+9),(x+23,y+15)],0xFFE070)
  # WIPER: windscreen with a wiper arm
  x,y=199,163
  fillpoly(G,[(x+4,y+19),(x+24,y+19),(x+21,y+5),(x+7,y+5)],0x7FB0D8)
  line(G,x+14,y+19,x+8,y+7,0x101214);line(G,x+15,y+19,x+9,y+7,0x101214)
  FR(x+13,y+18,3,3,0x101214)
  # EMERGENCY BRAKE: red disc with a white bar
  x,y=168,188
  disc(x+14,y+11,8,0xFF3030,8);FR(x+9,y+10,11,3,0xFFFFFF)
  # MAP: route line with stations and the train
  x,y=199,188
  FR(x+3,y+11,22,2,0xC0C8D0)
  for q in (4,13,22):FR(x+q,y+8,2,8,0xFFFFFF)
  fillpoly(G,[(x+9,y+14),(x+6,y+19),(x+12,y+19)],0x30F070)
  # max-speed marker down / up
  fillpoly(G,[(174,221),(191,221),(182,232)],0xA0FFA0)
  fillpoly(G,[(205,232),(222,232),(213,221)],0xA0FFA0)

def dashDraw():
  dc=TRAINS[TI[0]][8]
  fillrect(G,0,160,SW,80,dc,dc)
  FR(0,160,SW,2,shade(dc,1.25) if dc<0xC0C0C0 else 0xE8E8E8);FR(0,162,SW,1,shade(dc,0.6))
  FR(2,163,112,75,0x15181D);FR(2,163,112,1,0x3A4048)
  FR(117,163,48,36,0x15181D);FR(117,202,48,16,0x050607);FR(117,221,48,17,0x15181D)
  for key in BTN:
    x,y,w,h=BTN[key]
    c=0x2A2E34
    if key=='door':c=0x5A4A18
    if key=='stop':c=0x5A1A1A
    FR(x,y,w,h,c);FR(x,y,w,1,0x60666E)
  icons()
  FR(229,163,30,75,0x15181D);FR(232,166,6,68,0x050607)
  p1,p2,p3,tk,lb=DASH
  fillpoly(G,p1,0x50565E);fillpoly(G,p2,0x0C0E11)
  for q in tk:line(G,q[0],q[1],q[2],q[3],0xFFFFFF)
  for q in lb:T(q[0],q[1],q[2],0xFFFFFF)
  fillpoly(G,p3,0x2A2E34)
  T(293,226,"mph",0xA0A8B0)

def cab():
  T=TRAINS[TI[0]];cc=T[7]
  FR(0,0,SW,9,0x101214)
  poly(((0,0),(28,0),(42,VH),(0,VH)),cc)
  poly(((292,0),(SW,0),(SW,VH),(278,VH)),cc)
  L(28,0,42,VH,shade(cc,0.7));L(292,0,278,VH,shade(cc,0.7))
  # rain
  for q in ST['drops']:FR(q[0],q[1],1,3,0xC8D8E4)
  a=ST['wa'] if ST['wipe'] else 1.1
  x2=200+150*cos(a);y2=159-150*sin(a)
  L(200,159,x2,y2,0x141414);L(201,159,x2+1,y2,0x141414)

def mmss(t):
  t=int(abs(t));return '%02d:%02d'%(t//60,t%60)
def hhmm(t,sec=0):
  t=int(t)%86400
  if sec:return '%02d:%02d:%02d'%(t//3600,(t//60)%60,t%60)
  return '%02d:%02d'%(t//3600,(t//60)%60)
def dist(m):
  mi=m/1609.34
  if mi<0.1:return '%d yd'%int(m*1.0936)
  return '%.2f mi'%mi

def hud(ctl):
  TR=TRAINS[TI[0]]
  dashDraw()
  now=RT['clk']+ST['t']
  # points
  FR(2,11,82,14,0x15181D);T(6,13,'%d Points'%ST['score'],0xFFFFFF)
  # info panel: next stop, distance to go, timetable, platform
  ns=ST['ns']
  if ns<len(STN):
    st=STN[ns]
    T(6,165,'Terminus' if ns==len(STN)-1 else 'Next stop',0xA8B0B8)
    T(6,177,st[0],0xFFD030)
    ds=dist(max(0.0,st[4]-ST['pos']))
    T(6,190,ds,0xFFFFFF);T(7,190,ds,0xFFFFFF)
    T(8+len(ds)*7,190,'to go',0xA8B0B8)
    if ST['doors']==1 and atPlatform():
      late=ST['arr']
    else:
      gap=max(1.0,st[4]-STN[ns-1][4]) if ns>0 else 1.0
      rem=max(0.0,st[4]-ST['pos'])
      est=now+(rem/st[7]*RT['fac']+5*rem/gap if ns>0 else 0)
      late=est-st[5]
      if ns==0:late=0
    T(6,202,hhmm(st[5]),0xFFFFFF)
    T(42,202,('(+' if late>0 else '(-')+mmss(late)+')',0xFF6060 if late>30 else 0x60E060)
    T(6,214,'Platform %d'%st[1],0xFFFFFF)
  T(6,226,ST['unit']+' '+RT['hc'],0x8890A0)
  # signal box
  i=ST['nsig']
  if i<len(SG):
    a=aspect(i);d=SG[i][0]-ST['pos']
    blink=a<2 and d<400 and int(ST['t']*3)&1
    T(121,165,RT['code']+' %03d'%SG[i][1],0xFFFFFF if not blink else 0xFFC040)
    T(121,177,dist(d),0xFFFFFF)
    for q in range(3):
      c=(0xFF2020,0xFFC020,0x20E060)[q] if q==a else 0x2A2A2A
      FR(124+q*14,190,9,7,c)
  else:
    T(121,170,'No signals',0x808890)
  T(121,205,hhmm(now,1),0xFFFFFF)
  nl,nd=nextLimit()
  if nl:T(121,224,'%d in %s'%(nl,('%.1f'%(nd/1609.34))[1:] if nd>=160 else '%dy'%int(nd*1.09)),0xC0C8D0)
  # button highlights
  for key,on in ctl:
    if on:
      x,y,w,h=BTN[key];FR(x,y+h-3,w,3,0x60E080)
  if ST['doors']:FR(170,184,25,2,0xFFA020 if int(ST['t']*2)&1 else 0x804010)
  # notch bar
  if ST['pow']>0:h=int(ST['pow']*33);FR(232,200-h,6,h,0x30E060)
  if ST['brk']>0:
    h=int(min(1,ST['brk'])*33)
    FR(232,201,6,h,0xFF3030 if not ST['emerg'] or int(ST['t']*4)&1 else 0xFFFFFF)
  FR(231,200,8,1,0xFFFFFF)
  mph=ST['v']*MPH
  sp=str(int(mph+0.5))
  T(249-len(sp)*3,166,sp,0xFFFFFF);T(241,178,'mph',0x8890A0)
  # doors lamp
  FR(241,192,15,6,0x30C050 if ST['doors']==0 else (0xFFA020 if int(ST['t']*3)&1 else 0x603010))
  # limit disc
  lm=curLimit()
  over=mph>lm+3
  speedSign(245,224,12,lm,0xE02020 if not over or int(ST['t']*4)&1 else 0xFFFFFF,0xFFFFFF if not over else 0xFFE0E0)
  # dial: green marker = set max speed, white needle = speed
  sc=TR[6]
  a=1.5708*min(sc,ST['tgt'])/sc;ca=cos(a);sa=sin(a)
  ta=0.06
  poly(((DCX-(DR-11)*ca,DCY-(DR-11)*sa),(DCX-(DR+2)*cos(a-ta),DCY-(DR+2)*sin(a-ta)),(DCX-(DR+2)*cos(a+ta),DCY-(DR+2)*sin(a+ta))),0x20F060)
  a=1.5708*min(sc,mph)/sc;ca=cos(a);sa=sin(a)
  L(DCX-12*ca,DCY-12*sa,DCX-(DR-4)*ca,DCY-(DR-4)*sa,0xFFFFFF)
  L(DCX-12*ca+sa,DCY-12*sa-ca,DCX-(DR-4)*ca+sa,DCY-(DR-4)*sa-ca,0xFFFFFF)
  L(DCX-12*ca-sa,DCY-12*sa+ca,DCX-(DR-4)*ca-sa,DCY-(DR-4)*sa+ca,0xC0C8D0)
  s=str(ST['tgt']);T(300-len(s)*3,214,s,0x40F080)
  # hints
  if ST['hint'] and int(ST['t']*4)&1:
    FR(250,150,66,14,0xC02020);T(256,152,'BRAKE!',0xFFFFFF)
  if mph>lm+3:
    FR(110,140,100,14,0xC02020);T(118,142,'OVERSPEED',0xFFFFFF)
  if ST['msgT']>0:
    s=ST['msg'];w=len(s)*6+12
    FR(160-w//2,28,w,15,0x101418);FR(160-w//2,43,w,1,0xFFD030);T(166-w//2,30,s,0xFFFFFF)
  if ST['map']:drawMap()

def drawMap():
  FR(46,48,228,52,0x101418);FR(46,48,228,1,0xFFD030)
  tot=RT['endm'];x0=56;w=208
  FR(x0,74,w,2,0x808890)
  flag=RT['flag']
  for j in range(0,RT['n'],4):
    if j*SEG>tot:break
    if flag[j]&TUN:FR(x0+w*j*SEG/tot,72,2,6,0x404040)
    elif flag[j]&BRG:FR(x0+w*j*SEG/tot,73,2,4,0x3080E0)
  for i in range(len(SG)):
    x=x0+w*SG[i][0]/tot;a=aspect(i) if i>=ST['nsig'] else 0
    FR(x,68,2,3,(0xFF2020,0xFFC020,0x20E060)[a])
  for i in range(len(STN)):
    x=x0+w*STN[i][4]/tot;FR(x-1,70,3,10,0xFFFFFF)
    nm=STN[i][0][:3]
    T(x-9,(52 if i&1 else 82),nm,0xFFD030 if i==ST['ns'] else 0xC0C8D0)
  x=x0+w*ST['pos']/tot
  poly(((x,75),(x-4,84),(x+4,84)),0x30F070)

#---------- menu / results ----------
def flip():
  strblit(0,0,0,SW,SH,G)

def loadBest():
  try:
    f=open("railcab.txt","r");v=[int(a) for a in f.read().split(",")];f.close()
    while len(v)<3:v.append(0)
    return v
  except:
    return [0,0,0]
def saveBest(b):
  try:
    f=open("railcab.txt","w");f.write(",".join([str(a) for a in b]));f.close()
  except:
    pass

MB={'rl':(10,124,34,26),'rr':(276,124,34,26),'tl':(10,160,34,26),'tr':(276,160,34,26),'go':(110,198,100,30)}
def menu():
  best=loadBest()
  row=0;built=-1;cam=[0.0]
  prevk=keyboard();prevt=0;last=ticks()
  while True:
    if built!=RI[0]:
      ST.clear();build(RI[0]);built=RI[0]
      ST.update({'pos':260.0,'v':18.0,'bgx':0.0,'nsig':0,'t':0.0,'ns':0,'ot':[0,0,0,0],'wa':1.1,'wipe':0,'drops':[]})
      ST['pos']=260.0
    now=ticks();dt=min(0.2,max(0.01,(now-last)/1000.0));last=now
    ST['pos']+=18*dt;ST['t']+=dt
    if ST['pos']>RT['endm']-900:ST['pos']=260.0
    j=int(ST['pos']/SEG);ST['bgx']+=RT['curv'][j]*18*dt*F/(SEG*SEG)*0.9
    render()
    bigtext("RAILCAB",14,5,0xFFD030,0x101418)
    FR(0,46,SW,13,0x101418);ctext("drive - stop at the marker - open the doors",48,0xFFFFFF)
    R=ROUTES[RI[0]];Tn=TRAINS[TI[0]]
    FR(0,112,SW,124,0x101418)
    for key in ('rl','rr','tl','tr'):
      x,y,w,h=MB[key];FR(x,y,w,h,0x2A3A50)
      if key[1]=='l':poly(((x+10,y+13),(x+24,y+5),(x+24,y+21)),0xFFFFFF)
      else:poly(((x+24,y+13),(x+10,y+5),(x+10,y+21)),0xFFFFFF)
    c0=0xFFD030 if row==0 else 0xFFFFFF;c1=0xFFD030 if row==1 else 0xFFFFFF
    ctext("ROUTE",114,0x8890A0);ctext(R[0],126,c0)
    ctext('%d stations, %.1f mi, %s'%(len(R[6]),sum(R[7])/1609.34,ENVS[R[2]][10]),139,0xA8B0B8)
    ctext("TRAIN",152,0x8890A0);ctext(Tn[0],162,c1)
    ctext('top %d mph, %d m long'%(Tn[2],Tn[5]),175,0xA8B0B8)
    x,y,w,h=MB['go'];FR(x,y,w,h,0x30A050 if row==2 else 0x206838);ctext("START",y+10,0xFFFFFF)
    T(8,206,'Best %d'%best[RI[0]],0xC0C8D0)
    T(232,206,'Esc: quit',0xC0C8D0)
    flip()
    k=keyboard();pk=k&~prevk;prevk=k
    pts=touches();tap=pts and not prevt;prevt=1 if pts else 0
    if kd(pk,K_ESC):return 0
    if kd(pk,K_UP):row=(row+2)%3
    if kd(pk,K_DN):row=(row+1)%3
    d=0
    if kd(pk,K_LT):d=-1
    if kd(pk,K_RT):d=1
    if tap:
      if inside(MB['rl'],pts):row=0;d=-1
      elif inside(MB['rr'],pts):row=0;d=1
      elif inside(MB['tl'],pts):row=1;d=-1
      elif inside(MB['tr'],pts):row=1;d=1
      elif inside(MB['go'],pts):return 1
    if d:
      if row==0:RI[0]=(RI[0]+d)%3
      elif row==1:TI[0]=(TI[0]+d)%3
    if kd(pk,K_ENTER):
      if row==2:return 1
      row+=1

def results():
  best=loadBest()
  sc=ST['score'];ri=RI[0]
  nb=sc>best[ri]
  if nb:best[ri]=sc;saveBest(best)
  FR(30,30,260,170,0x101418);FR(30,30,260,2,0xFFD030)
  ctext("ROUTE COMPLETE" if ST['done']==1 and not ST['fin'] else "RUN OVER",38,0xFFD030)
  ctext(RT['name']+' - '+TRAINS[TI[0]][0],54,0xC0C8D0)
  y=74
  for a,b in (('Stations served','%d/%d'%(ST['stops'],len(STN)-1)),('Perfect stops',str(ST['perfect'])),
              ('On time',str(ST['ontime'])),('Signals passed at danger',str(ST['spad'])),
              ('Mistakes',str(ST['pen'])),('Overspeed time','%d s'%int(ST['over']))):
    T(48,y,a,0xFFFFFF);T(232,y,b,0xFFFFFF);y+=14
  ctext('%d Points'%sc,162,0x60F090)
  if nb:ctext("NEW BEST!",176,0xFFD030)
  ctext("Tap / Enter",188,0x8890A0)
  flip()
  while keyboard() or touches():
    pass
  while True:
    if kd(keyboard(),K_ENTER) or kd(keyboard(),K_ESC) or touches():break
  while keyboard() or touches():
    pass

#---------- main loop ----------
def play():
  newgame()
  dashPrep()
  say('Passengers boarding - then press DOOR',4)
  last=ticks();prevk=keyboard();prevt=0;rep=0.0
  while True:
    now=ticks();dt=(now-last)/1000.0;last=now
    if dt>0.2:dt=0.2
    if dt<=0:dt=0.01
    k=keyboard();pk=k&~prevk;prevk=k
    pts=touches();tap=1 if (pts and not prevt) else 0;prevt=1 if pts else 0
    if kd(pk,K_ESC):
      FR(80,90,160,40,0x101418);ctext("PAUSED",96,0xFFD030);ctext("Esc: quit  Enter: resume",112,0xFFFFFF);flip()
      while keyboard():
        pass
      q=0
      while True:
        kk=keyboard()
        if kd(kk,K_ESC):q=1;break
        if kd(kk,K_ENTER) or touches():break
      while keyboard() or touches():
        pass
      if q:return
      last=ticks();prevk=0;continue
    T_=TRAINS[TI[0]];vm=T_[2]
    up=kd(k,K_UP) or kd(k,K_PLUS) or inside(BTN['up'],pts)
    dn=kd(k,K_DN) or kd(k,K_MINUS) or inside(BTN['dn'],pts)
    upp=kd(pk,K_UP) or kd(pk,K_PLUS) or (tap and inside(BTN['up'],pts))
    dnp=kd(pk,K_DN) or kd(pk,K_MINUS) or (tap and inside(BTN['dn'],pts))
    if upp or dnp:rep=0.0
    if up or dn:
      rep+=dt
      if upp or dnp or rep>0.4:
        if rep>0.4:rep=0.28
        ST['tgt']=max(0,min(vm,ST['tgt']+(5 if up else -5)))
    if kd(pk,K_RT):ST['tgt']=curLimit()
    if kd(pk,K_LT):ST['tgt']=0
    for p in pts:
      dx=DCX-p[0];dy=DCY-p[1]
      if p[0]>=246 and p[1]>=170 and dx*dx+dy*dy<(DR+6)**2 and dx*dx+dy*dy>14*14:
        a=atan2(dy,dx);v=a/1.5708*T_[6]
        ST['tgt']=max(0,min(vm,int(v/5+0.5)*5))
    if kd(pk,K_ENTER) or (tap and inside(BTN['door'],pts)):doorButton()
    if kd(pk,K_DEL) or (tap and inside(BTN['stop'],pts)):
      if ST['v']>0:ST['emerg']=1;ST['tgt']=0;say('EMERGENCY BRAKE',2)
    if kd(pk,K_MENU) or (tap and inside(BTN['map'],pts)):ST['map']=1-ST['map']
    if kd(pk,K_SPC) or (tap and inside(BTN['wipe'],pts)):ST['wipe']=1-ST['wipe']
    if kd(pk,K_7) or kd(pk,K_9):
      DET[0]=max(0,min(2,DET[0]+(1 if kd(pk,K_9) else -1)))
      say('View distance %d m'%int(DDS[DET[0]][0]*SEG),1.5)
    n=int(dt/0.05)+1
    for s in range(n):update(dt/n)
    render();cab()
    hud((('door',ST['doors']==1),('wipe',ST['wipe']),('stop',ST['emerg']),('map',ST['map']),('dn',dn),('up',up)))
    flip()
    if ST['done']:
      results();return

def main():
  dimgrob(G,SW,SH,0)
  while True:
    if not menu():return
    play()
    gc.collect()

main()
