#MATHRUN - an original school-maze math game for the HP Prime
#Find 7 notebooks, solve the math, and escape before Ms. Margin
#(the strictest grader in school) catches you.
#Python app (hpprime module). Touch buttons + keyboard.
from hpprime import *
from math import *
import gc

try:
  ticks()
except:
  def ticks():
    return int(eval("TICKS()"))

_rs=[1]
def rnd():
  _rs[0]=(_rs[0]*1103515245+12345)&0x7fffffff
  return _rs[0]/2147483648.0
def rint(n):
  return int(rnd()*n)

SW=320;VH=200;HH=100;G=1;CXS=160

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
'A':"0111010001111111000110001",'C':"0111110000100001000001111",
'D':"1111010001100011000111110",'E':"1111110000111101000011111",
'G':"0111110000100111000101111",'H':"1000110001111111000110001",
'M':"1000111011101011000110001",'N':"1000111001101011001110001",
'P':"1111010001111101000010000",'R':"1111010001111101001010001",
'S':"0111110000011100000111110",'T':"1111100100001000010000100",
'U':"1000110001100011000101110",'Y':"1000101010001000010000100",
'O':"0111010001100011000101110",'I':"1111100100001000010011111",
'!':"0010000100001000000000100",' ':"0000000000000000000000000"}
def bigtext(s,y,sz,c,sh=0):
  x0=(SW-len(s)*6*sz)//2
  for n in range(len(s)):
    f=FONT.get(s[n],FONT[' '])
    for i in range(25):
      if f[i]=='1':
        if sh:FR(x0+n*6*sz+(i%5)*sz+2,y+(i//5)*sz+2,sz,sz,sh)
        FR(x0+n*6*sz+(i%5)*sz,y+(i//5)*sz,sz,sz,c)

#---------- input ----------
K_UP=2;K_DN=12;K_LT=7;K_RT=8;K_ESC=4;K_ENTER=30;K_SPC=49;K_DEL=19;K_MENU=13
K_PLUS=50;K_MINUS=45
DIGK={47:0,42:1,43:2,44:3,37:4,38:5,39:6,32:7,33:8,34:9}
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
B_FW=(46,112,40,40);B_LT=(4,156,40,40);B_BK=(46,156,40,40);B_RT=(88,156,40,40)
B_RUN=(196,150,58,44);B_ITEM=(258,150,58,44);B_SWAP=(258,108,58,36)
def tbtn(b,on,lab,col=0x2060A0):
  x,y,w,h=b
  if on:FR(x,y,w,h,col)
  box2(x,y,w,h,0xF0F0FF)
  textout(G,x+(w-len(lab)*7)//2,y+h//2-6,lab,0xF0F0FF)

#---------- school map (original layout) ----------
#0 floor  1 hallway wall  2 classroom wall  3 lockers  4 door  5 exit door
MW=44
RM0=[3,13,23,33]     #room block starts (8x8 with walls)
def gen(seed):
  global MAP,DOORS,ROOMS,EXITS
  _rs[0]=seed
  MAP=[bytearray([0]*MW) for i in range(MW)]
  for i in range(MW):
    MAP[0][i]=1;MAP[MW-1][i]=1;MAP[i][0]=1;MAP[i][MW-1]=1
  ROOMS=[];DOORS={}
  for by in range(4):
    for bx in range(4):
      x0=RM0[bx];y0=RM0[by];x1=x0+7;y1=y0+7
      for i in range(8):
        MAP[y0][x0+i]=2;MAP[y1][x0+i]=2;MAP[y0+i][x0]=2;MAP[y0+i][x1]=2
      #lockers on the hallway side of some walls
      if rnd()<0.6:
        for i in range(2,6):MAP[y0][x0+i]=3
      if rnd()<0.6:
        for i in range(2,6):MAP[y1][x0+i]=3
      #one or two doors into the classroom
      sides=[0,1,2,3];nd=1+rint(2)
      for k in range(nd):
        s=sides.pop(rint(len(sides)))
        p=3+rint(2)
        if s==0:dx,dy=x0+p,y0
        elif s==1:dx,dy=x0+p,y1
        elif s==2:dx,dy=x0,y0+p
        else:dx,dy=x1,y0+p
        MAP[dy][dx]=4;DOORS[(dx,dy)]=0.0
      #a few desks inside (low cabinets)
      if rnd()<0.5:MAP[y0+3][x0+3]=2
      ROOMS.append((x0+1,y0+1,x1-1,y1-1))
  #exits in the middle of each outer wall
  EXITS=[(21,0),(22,0),(21,MW-1),(22,MW-1),(0,21),(0,22),(MW-1,21),(MW-1,22)]
  for (x,y) in EXITS:MAP[y][x]=5

def solidAt(x,y):
  ix=int(x);iy=int(y)
  if ix<0 or iy<0 or ix>=MW or iy>=MW:return 1
  v=MAP[iy][ix]
  if v==4:return DOORS.get((ix,iy),0)<=0
  return v!=0
def wallAt(ix,iy):
  if ix<0 or iy<0 or ix>=MW or iy>=MW:return 1
  v=MAP[iy][ix]
  if v==4 and DOORS.get((ix,iy),0)>0:return 0
  return v

#---------- sprites (all original pixel art) ----------
def packRuns(art):
  #sprite stored as: (cols, rows, [bytes per column: y0,len,key...], keys)
  rows=len(art);cols=len(art[0]);keys=""
  out=[]
  for x in range(cols):
    b=bytearray();y=0
    while y<rows:
      ch=art[y][x]
      if ch=='.':
        y+=1;continue
      y0=y
      while y<rows and art[y][x]==ch:y+=1
      k=keys.find(ch)
      if k<0:keys+=ch;k=len(keys)-1
      b.append(y0);b.append(y-y0);b.append(k)
    out.append(bytes(b))
  return (cols,rows,out,keys)

def scale2x(art):
  #Scale2x pixel-art upscaling: twice the resolution, smoother diagonals
  h=len(art);w=len(art[0]);out=[]
  for y in range(h):
    r0=[];r1=[]
    for x in range(w):
      P=art[y][x]
      A=art[y-1][x] if y>0 else P
      Bp=art[y][x+1] if x<w-1 else P
      C=art[y][x-1] if x>0 else P
      D=art[y+1][x] if y<h-1 else P
      if C==A and C!=D and A!=Bp:e0=A
      else:e0=P
      if A==Bp and A!=C and Bp!=D:e1=Bp
      else:e1=P
      if D==C and D!=Bp and C!=A:e2=C
      else:e2=P
      if Bp==D and Bp!=A and D!=C:e3=D
      else:e3=P
      r0.append(e0+e1);r1.append(e2+e3)
    out.append("".join(r0));out.append("".join(r1))
  return out

def runs(art,up=0):
  if up:art=scale2x(art)
  return packRuns(art)

def runsOld(art):
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
# Ms. Margin (original): grey bun with a pencil, round glasses, rosy cheeks,
# gold brooch on a white collar, purple cardigan with buttons + pocket,
# navy skirt, dark tights, black shoes, red grading pen. 20 x 44.
MTOP=[
"........gggg........",
".......gGggGg.......",
"......ggggggggy.....",
".......gggggg.y.....",
".....gggggggggg.....",
"....gGssssssssGg....",
"....gsKKKssKKKsg....",
"....sKwlKsKwlKs.....",
"....sKlKKsKlKKs.....",
"....ssKKssssKKss....",
"....srsssSSsssrs....",
".....sssmmmmsss.....",
"......SssssssS......",
".......SssssS.......",
".....ppwwwowwwpp....",
"...pppPwwwwwwPppp...",
"..ppppPPwwwwPPpppp..",
".pppppPpPwwPpPppppp.",
".ppppppPpowPpppppp..",
"pppPpppPpwwPpppPppp.",
"pppPppppPowPppppPppp",
"pppPpppppPPpppppPppp",
"pppPpppppowpppppPppp",
"pppPppppppPppppqqPpp",
"pppPpppppPPppppqpPpp",
"hhhPppppppPppppPPhhh",
"hhh.ppppppPpppp..hRh",
".h..ppppppPpppp..hRh",
"....kkkkkkkkkkkk..R.",
"....kqkkkkkkkkqk..R.",
"...kkqkkkkkkkkqkk.n.",
"...kkqkkkkkkkkqkk...",
"...kkqkkkkkkkkqkk...",
"..kkkqkkkkkkkkqkkk..",
"..kkkqkkkkkkkkqkkk..",
"..kkkkkkkkkkkkkkkk.."]
MLEGS=[[
".....ttt....ttt.....",
".....ttt....ttt.....",
".....ttt....ttt.....",
".....ttt....ttt.....",
".....ttt....ttt.....",
".....ttt....ttt.....",
"....nnnn....nnnn....",
"...nnnnn....nnnnn..."],[
".....ttt.....ttt....",
"....ttt......ttt....",
"....ttt.......ttt...",
"...ttt........ttt...",
"...ttt.........ttt..",
"...ttt.........ttt..",
"..nnnn........nnnn..",
".nnnnn........nnnnn."]]
# Mop Bot (original): yellow dome robot, antenna light, visor eyes,
# grey bumper, blue body with water tank, spinning mop. 16 x 16.
BTOP=[
".......Rr.......",
".......K........",
".....yyyyyy.....",
"...yyYYYYYYyy...",
"..yYYyyyyyyYYy..",
"..yKKKKKKKKKKy..",
"..yKcKKKKKKcKy..",
"..yKKKKKKKKKKy..",
"..yyyyyyyyyyyy..",
".gggggggggggggg.",
".gGGGGGGGGGGGGg.",
"..bbbbbWWbbbbb..",
"..bbbbWllWbbbb.."]
BMOP=[[
"..dddddddddddd..",
".cCcCcCcCcCcCcC.",
"CcCcCcCcCcCcCcCc"],[
"..dddddddddddd..",
".CcCcCcCcCcCcCc.",
"cCcCcCcCcCcCcCcC"]]
# Paper-plane kid (original): blue cap, freckles, orange hoodie with a star,
# jeans, sneakers, paper plane. 14 x 28. Frame 2 = throwing.
KTOP=[
"....bbbbbb....",
"...bbBBBBbb...",
"..bbbbbbbbbbb.",
"...ssssssss...",
"...sKssssKs...",
"...sfsssfss...",
"...ssssssss...",
"....smmms.....",
".....ssss....."]
KBODY=[[
"...oooooooo...",
"..oooOOOOooo..",
".oooOOyOOOoooW",
".ooOOyyyOOooWW",
".ooOOOyOOOoooW",
".ooOOOOOOOoo..",
".hoOOOOOOOoh..",
".h.oooooooo.h.",
"...jjjjjjjj...",
"...jjjJJjjj...",
"...jjj..jjj...",
"...jjj..jjj...",
"...jjj..jjj...",
"..wwww..wwww..",
"..kkkk..kkkk.."],[
"...oooooooo.hW",
"..oooOOOOoooWW",
".oooOOyOOOooh.",
".ooOOyyyOOoo..",
".ooOOOyOOOoo..",
".ooOOOOOOOoo..",
".hoOOOOOOOoo..",
".h.oooooooo...",
"...jjjjjjjj...",
"...jjjJJjjj...",
"...jjj..jjj...",
"..jjj....jjj..",
"..jjj....jjj..",
".wwww....wwww.",
".kkkk....kkkk."]]
# notebook: blue cover, white spiral rings, name label, page edge
NOTE=[
"wbbbbbbbbb",
"cbbbbbbbbb",
"wbbBBBBBbb",
"cbbBwwwBbb",
"wbbBBBBBbb",
"cbbbbbbbbb",
"wbbbbbbbbb",
"cbbbbbbbbb",
"wbbbbbbbbb",
"cbbbbbbbbb",
"wbbbbbbbbb",
"cppppppppp"]
ITEMS=[
["..oooooo..",".oyyyyyyo.","oyRRRRRyyo","oyyyyyyyyo",".oooooooo."],
["...pppp...","..pPPPPp..",".pppppppp.",".bbbbbbbb.","..bBBBBb.."],
["yyyyyyyy","yKKKKyyy","yyyyyyyy","yKKKyyyy","yyyyyyyy","yyyyyyYY"]]

MARGINF=[runs(MTOP+MLEGS[0]),runs(MTOP+MLEGS[1])]
MARGP={'g':0xB0B0B8,'G':0x808088,'y':0xF0C030,'s':0xF2CDA8,'S':0xD8A882,'K':0x181018,
       'w':0xFFFFFF,'l':0xB8E0F0,'r':0xF08890,'m':0xB02848,'o':0xE8C040,'p':0x7A3FA0,
       'P':0x5A2A80,'q':0x9A60C0,'h':0xF2CDA8,'R':0xE02020,'k':0x283050,'t':0x403848,'n':0x101010}
MARGANG=dict(MARGP);MARGANG.update({'w':0xFFE0E0,'l':0xFF8080,'r':0xFF4040,'s':0xFFB898,'p':0x9A2F90,'m':0x700010})
MOPF=[runs(BTOP+BMOP[0]),runs(BTOP+BMOP[1])]
MOPP={'R':0xFF3030,'r':0xFFA0A0,'K':0x303030,'y':0xF0C020,'Y':0xFFE870,'c':0x60E0FF,
      'g':0x707880,'G':0x505860,'b':0x3070C0,'W':0xB0E0FF,'l':0x60C0F0,'d':0x806040,'C':0xE0F0FF}
KIDF=[runs(KTOP+KBODY[0]),runs(KTOP+KBODY[1])]
KIDP={'b':0x2050C0,'B':0x4078E0,'s':0xE0B080,'K':0x101010,'f':0xC07850,'m':0x903030,
      'o':0xF07020,'O':0xD05810,'y':0xFFE040,'W':0xFFFFFF,'h':0xE0B080,'j':0x3858A8,
      'J':0x284078,'w':0xF0F0F0,'k':0x303030}
NOTEB=runs(NOTE)
NOTEP={'w':0xF0F0F0,'c':0xA0A0A8,'b':0x2878E0,'B':0x1850B0,'p':0xF8F4E8}
ITEMART={0:runs(ITEMS[0]),1:runs(ITEMS[1]),2:runs(ITEMS[2])}
ITEMP={0:{'o':0x805030,'y':0xFFD040,'R':0xD03030},1:{'p':0xFF90B0,'P':0xFFC0D0,'b':0x5070D0,'B':0x3050A0},
       2:{'y':0xFFF060,'Y':0xE0D040,'K':0x707070}}
del MTOP,MLEGS,BTOP,BMOP,KTOP,KBODY,NOTE,ITEMS
gc.collect()
PLANE=runs(["W.....","WWW...","WWWWW.","WWWWWW","WWWW..","WW...."])
INAME=["Energy Bar","Eraser","Sticky Map"]

#---------- state ----------
class O:
  pass
PL=O();ST={};ENTS=[]
RES=[80,107,160,320]
OPT=[160];ZB=[0.0]*320

def freeCell(room):
  x0,y0,x1,y1=room
  for t in range(40):
    x=x0+1+rint(x1-x0-1);y=y0+1+rint(y1-y0-1)
    if MAP[y][x]==0:return x+0.5,y+0.5
  return x0+1.5,y0+1.5

def newgame():
  gen(ticks()&0x7fff|1)
  PL.x=21.5;PL.y=22.0;PL.a=-pi/2;PL.st=1.0;PL.stun=0.0;PL.slide=0.0;PL.vx=0.0;PL.vy=0.0
  ST.update(nb=0,wrong=0,active=0,items=[None,None,None],slot=0,msg="",msgt=0.0,
    t=0.0,map=0,hunt=0.0,dead=0,win=0,btn=1,beat=0.0)
  ENTS[:]=[]
  rooms=list(range(16));order=[]
  while rooms:order.append(rooms.pop(rint(len(rooms))))
  for k in range(7):
    x,y=freeCell(ROOMS[order[k]]);ENTS.append(ent(0,x,y))
  for k in range(6):
    x,y=freeCell(ROOMS[order[(k+7)%16]]);e=ent(1,x,y);e.kind=k%3;ENTS.append(e)
  #the teacher starts in her office next to the lobby
  M.x=21.5;M.y=12.0;M.tx=M.x;M.ty=M.y;M.path=[];M.rep=0.0;M.stun=0.0;M.seen=0.0
  B.x=1.5;B.y=1.5;B.dir=0;B.wet={}
  K.x=1.5;K.y=MW-2.5;K.cd=3.0;K.pl=None
  say("Find 7 notebooks! Watch out for Ms. Margin...",4)
def ent(t,x,y):
  e=O();e.t=t;e.x=x;e.y=y;e.alive=1;e.kind=0;return e
M=O();B=O();K=O()

def say(m,t=2.5):
  ST['msg']=m;ST['msgt']=t

#---------- math notebook ----------
KP=[]
for i in range(12):
  KP.append((170+(i%3)*48,60+(i//3)*36,44,32))
KPL=["7","8","9","4","5","6","1","2","3","-","0","OK"]
def problem(level,k):
  if level<2 or k==0:
    a=rint(10)+1;b=rint(10)+1
    if rnd()<0.5:return (str(a)+" + "+str(b),a+b)
    a+=b;return (str(a)+" - "+str(b),a-b)
  if level<5:
    a=rint(9)+2;b=rint(9)+2;return (str(a)+" x "+str(b),a*b)
  a=rint(12)+2;b=rint(12)+2;c=rint(20)+1
  if rnd()<0.5:return (str(a)+" x "+str(b)+" - "+str(c),a*b-c)
  return (str(a)+" x "+str(b)+" + "+str(c),a*b+c)

def notebook():
  ok=0;release()
  for q in range(3):
    txt,ans=problem(ST['nb'],q)
    typed=""
    while True:
      FR(0,0,SW,240,0xF4F0E0)
      for r in range(12):FR(0,30+r*16,SW,1,0xB0C8E8)
      FR(20,0,2,240,0xE08080)
      otext(30,8,"NOTEBOOK "+str(ST['nb']+1)+" / 7    problem "+str(q+1)+"/3",0x2040A0)
      textout(G,30,44,"Solve:",0x303030)
      textout(G,30,64,txt+" = ?",0x101010)
      FR(30,90,120,24,0xFFFFFF);box2(30,90,120,24,0x303030)
      textout(G,36,96,typed+("_" if int(ticks()/300)%2 else ""),0x101010)
      textout(G,30,124,"Type with the number keys",0x606060)
      textout(G,30,138,"or tap the keypad. Enter = OK",0x606060)
      if ST['wrong']>0:textout(G,30,166,"Wrong answers: "+str(ST['wrong']),0xC02020)
      for i in range(12):
        x,y,w,h=KP[i];FR(x,y,w,h,0xD8D0B8);box2(x,y,w,h,0x404040)
        textout(G,x+(w-len(KPL[i])*7)//2,y+10,KPL[i],0x101010)
      strblit(0,0,0,320,240,G)
      k=keyboard();key=None
      for b,d in DIGK.items():
        if kd(k,b):key=str(d)
      if kd(k,K_MINUS):key="-"
      if kd(k,K_DEL):key="DEL"
      if kd(k,K_ENTER):key="OK"
      p=touches()
      for i in range(12):
        if inside(KP[i],p):key=KPL[i]
      if key is None:continue
      release()
      if key=="OK":
        if typed in ("","-"):continue
        break
      if key=="DEL":typed=typed[:-1]
      elif key=="-":typed="-" if typed=="" else typed
      elif len(typed)<5:typed+=key
    right=int(typed)==ans
    FR(170,190,140,30,0x30A040 if right else 0xC03030)
    textout(G,180,198,"CORRECT!" if right else "WRONG! ("+str(ans)+")",0xFFFFFF)
    strblit(0,0,0,320,240,G);t0=ticks()
    while ticks()-t0<700:pass
    if right:ok+=1
    else:
      ST['wrong']+=1
  return ok

#---------- wall textures (original designs, 64x64) ----------
#Each texture is painted once into its own off-screen graphic (G2..G6),
#in 8 shades side by side: 4 distance levels x lit/shadow side. Every
#screen column is then ONE stretched copy of a 1-pixel texture column.
TS=64
SHADES=[1.0,0.84,0.66,0.48]
TEXOK=[0]
def texDesign(w):
  #list of (x,y,w,h,colour) rectangles; drawn back to front
  r=[];_rs[0]=900+w
  if w==1:
    #hallway: painted plaster, blue band, wood skirting, faint panel seams
    r.append((0,0,64,64,0xD8C8A0))
    for i in range(70):
      r.append((rint(63),rint(63),1+rint(2),1,0xCCBC92 if i%2 else 0xE2D4AE))
    r.append((0,27,64,9,0x3060B0));r.append((0,27,64,1,0x6890D8));r.append((0,35,64,1,0x203E78))
    r.append((0,55,64,9,0x705030));r.append((0,55,64,1,0x9A7448))
    for x in (0,32):r.append((x,0,1,27,0xBFAE86));r.append((x,36,1,19,0xBFAE86))
  elif w==2:
    #classroom: cream wall, green band, cork notice board with notes + pins
    r.append((0,0,64,64,0xE4D8B8))
    for i in range(50):
      r.append((rint(63),rint(63),1,1,0xD6CAA8))
    r.append((0,31,64,5,0x40A060));r.append((0,31,64,1,0x70C890))
    r.append((0,56,64,8,0x507050));r.append((0,56,64,1,0x78A078))
    r.append((14,6,36,22,0x8A5A30));r.append((16,8,32,18,0xC89058))
    for i in range(40):r.append((16+rint(31),8+rint(17),1,1,0xB07840))
    for (x,y,c) in ((18,10,0xFFF080),(30,9,0xFFFFFF),(39,12,0x90D0FF),(22,17,0xFFB0C0),(35,18,0xFFFFFF)):
      r.append((x,y,8,6,c));r.append((x+1,y+2,6,1,0x909090));r.append((x+3,y,2,1,0xE02020))
  elif w==3:
    #row of blue lockers: vents, numbers plate, handles, dark gaps
    r.append((0,0,64,64,0x4070B0))
    for x in (0,16,32,48):
      r.append((x,0,1,64,0x203860));r.append((x+1,0,1,64,0x6090D0))
      for k in range(4):r.append((x+4,6+k*3,8,1,0x203860))
      r.append((x+5,20,6,4,0xD8D8E0));r.append((x+12,30,2,8,0xC0C0C8));r.append((x+12,30,1,8,0xF0F0F8))
    r.append((0,60,64,4,0x283848))
  elif w==4:
    #wooden classroom door: grain, glass window with shine, handle, frame
    r.append((0,0,64,64,0x6A4020));r.append((4,0,56,64,0x8A5A30))
    for i in range(36):
      y=rint(63);r.append((4+rint(40),y,6+rint(14),1,0x7A4E28 if i%2 else 0x9A6838))
    r.append((18,8,28,20,0x40403C));r.append((20,10,24,16,0x8CC8E8));r.append((22,12,4,12,0xD8F0FF));r.append((28,12,2,12,0xB8E0F8))
    r.append((48,34,6,3,0xE0C040));r.append((48,34,6,1,0xFFF0A0))
    r.append((4,62,56,2,0x4A2C14))
  else:
    #exit door: red metal with push bar and a green EXIT sign
    r.append((0,0,64,64,0xA02020));r.append((6,10,52,54,0xC03030))
    r.append((6,10,52,1,0xE05050));r.append((31,10,2,54,0x801818))
    r.append((10,36,44,4,0xC0C0C8));r.append((10,36,44,1,0xF0F0F8))
    r.append((16,1,32,8,0x103010))
    #E X I T in 2x2 pixel blocks
    for (ox,pat) in ((18,"111100110100111"),(26,"101010010101101"),(34,"111010010010111"),(42,"111010010010010")):
      for i in range(15):
        if pat[i]=='1':r.append((ox+(i%3)*2,2+(i//3),2,1,0x40FF60))
  return r

def makeTextures():
  try:
    for w in range(1,6):
      g=w+1
      dimgrob(g,TS*8,TS,0)
      d=texDesign(w)
      for v in range(8):
        f=SHADES[v%4]*(0.8 if v>=4 else 1.0)
        ox=v*TS
        for (x,y,ww,hh,c) in d:
          fillrect(g,ox+x,y,ww,hh,shade(c,f),shade(c,f))
    #test one stretched copy; if this firmware can't, fall back to flat walls
    strblit(G,0,0,2,8,2,0,0,1,TS)
    TEXOK[0]=1
  except:
    TEXOK[0]=0
  gc.collect()

#---------- raycaster ----------
WCOL={1:0xD8C8A0,2:0xE4D8B8,3:0x4070B0,4:0x8A5A30,5:0xC03030}
def cast(N):
  px=PL.x;py=PL.y;a=PL.a
  dX=cos(a);dY=sin(a);plX=-dY*0.66;plY=dX*0.66
  cw=SW/N
  FR(0,0,SW,HH,0xE8E8E0)
  for i in range(1,7):
    y=HH-int(HH/(i*0.9+0.4));FR(0,y,SW,1,0xD0D0C8)
  FR(0,HH,SW,HH,0x9AA0A8)
  for i in range(1,9):
    y=HH+int(HH/(i*0.8+0.2));FR(0,min(y,VH-1),SW,1,0x868C94)
  #floor tile seams converge to the middle of the view
  for k in range(-6,7):
    line(G,CXS+k*8,HH,CXS+k*90,VH,0x8A9098)
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
    while n<48:
      if sdx<sdy:
        sdx+=ddx;mx+=sx;side=0
      else:
        sdy+=ddy;my+=sy;side=1
      w=wallAt(mx,my)
      if w:break
      n+=1
    if n>=48:w=1
    if side==0:
      pd=(mx-px+(1-sx)/2)/rx;wx=py+pd*ry
    else:
      pd=(my-py+(1-sy)/2)/ry;wx=px+pd*rx
    if pd<0.05:pd=0.05
    ZB[i]=pd
    wx-=int(wx)
    h=VH/pd;top=HH-h/2
    f=1.15/(1+pd*0.12)
    if side:f*=0.82
    c=WCOL.get(w,0xD8C8A0)
    x0=int(i*cw);x1=int((i+1)*cw);ww=x1-x0
    if TEXOK[0]:
      #texture column: pick a distance shade, copy 1 texel column stretched
      lv=0 if pd<2.2 else (1 if pd<4.5 else (2 if pd<8 else 3))
      tx=int(wx*TS)
      if tx>=TS:tx=TS-1
      sx_=(lv+(4 if side else 0))*TS+tx
      if top>=0:
        strblit(G,x0,int(top),ww,int(h)+1,w+1,sx_,0,1,TS)
      else:
        #wall taller than the screen: copy only the visible texture rows
        sy=-top/h*TS;sh=VH/h*TS
        strblit(G,x0,0,ww,VH,w+1,sx_,int(sy),1,max(1,int(sh+0.5)))
      continue
    t=int(top);hh=int(h)
    if t<0:
      hh+=t;t=0
    if t+hh>VH:hh=VH-t
    f=1.15/(1+pd*0.12)
    if side:f*=0.82
    c=WCOL.get(w,0xD8C8A0)
    FR(x0,t,ww,hh,shade(c,f))

def drawSprite(R,pal,sx,depth,scale,lift,N):
  cols,rows,cr,keys=R
  h=VH/depth*scale;w=h*cols/rows*0.8
  pc=[shade(pal[k],1.1/(1+depth*0.1)) for k in keys]
  bot=HH+VH/depth*0.5-lift*VH/depth;top=bot-h
  cwid=w/cols;rh=h/rows;x0=sx-w/2;cw=SW/N
  f=1.1/(1+depth*0.1)
  for j in range(cols):
    xa=x0+j*cwid;xb=xa+cwid;xc=(xa+xb)/2
    if xb<0 or xa>=SW:continue
    s=int(xc/cw)
    if s<0 or s>=N or ZB[s]<depth:continue
    b=cr[j]
    for q in range(0,len(b),3):
      FR(xa,top+b[q]*rh,xb-xa+1,b[q+1]*rh+1,pc[b[q+2]])

def project(x,y):
  a=PL.a;dX=cos(a);dY=sin(a);plX=-dY*0.66;plY=dX*0.66
  inv=1/(plX*dY-dX*plY)
  rx=x-PL.x;ry=y-PL.y
  return inv*(dY*rx-dX*ry),inv*(-plY*rx+plX*ry)

def render():
  N=OPT[0];cast(N)
  vis=[]
  for e in ENTS:
    if not e.alive:continue
    tx,ty=project(e.x,e.y)
    if ty>0.2:vis.append((ty,tx,0,e))
  for o,kd_ in ((M,1),(B,2),(K,3)):
    if kd_==1 and not ST['active'] and ST['nb']==0:pass
    tx,ty=project(o.x,o.y)
    if ty>0.2:vis.append((ty,tx,kd_,o))
  if K.pl:
    tx,ty=project(K.pl[0],K.pl[1])
    if ty>0.2:vis.append((ty,tx,4,None))
  vis.sort(key=lambda v:-v[0])
  for ty,tx,kd_,e in vis:
    sx=SW/2*(1+tx/ty)
    if kd_==0:
      if e.t==0:drawSprite(NOTEB,NOTEP,sx,ty,0.18,0.25+0.05*sin(ST['t']*3),N)
      else:drawSprite(ITEMART[e.kind],ITEMP[e.kind],sx,ty,0.12,0.15,N)
    elif kd_==1:
      ang=ST['wrong']>0 and ST['active']
      fr=MARGINF[int(ST['t']*4)%2] if (ST['active'] and M.stun<=0) else MARGINF[0]
      drawSprite(fr,MARGANG if ang else MARGP,sx+(rnd()-0.5)*4*(M.stun>0),ty,1.05,0,N)
    elif kd_==2:drawSprite(MOPF[int(ST['t']*6)%2],MOPP,sx,ty,0.45,0,N)
    elif kd_==3:drawSprite(KIDF[1 if K.cd>4.4 else 0],KIDP,sx,ty,0.72,0,N)
    else:drawSprite(PLANE,{'W':0xFFFFFF},sx,ty,0.12,0.45,N)
  #wet floor warning tint
  if (int(PL.x),int(PL.y)) in B.wet:FR(0,VH-6,SW,6,0x60C0F0)

def minimap():
  s=3;ox=SW-MW*s-2;oy=2
  FR(ox-1,oy-1,MW*s+2,MW*s+2,0x000000)
  for y in range(MW):
    row=MAP[y]
    for x in range(MW):
      v=row[x]
      if v:FR(ox+x*s,oy+y*s,s,s,WCOL.get(v,0x888888))
  for e in ENTS:
    if e.alive and e.t==0:FR(ox+int(e.x*s)-1,oy+int(e.y*s)-1,3,3,0x2878E0)
  FR(ox+int(PL.x*s)-1,oy+int(PL.y*s)-1,3,3,0xFFFF00)

def hud(ctl):
  FR(0,VH,SW,40,0x202838);FR(0,VH,SW,1,0x6080C0)
  otext(4,VH+4,"Notebooks "+str(ST['nb'])+"/7",0x80C0FF)
  otext(4,VH+20,"Stamina",0xC0C0C0)
  FR(64,VH+24,80,8,0x402020);FR(64,VH+24,int(80*PL.st),8,0x40E060 if PL.st>0.3 else 0xE0A020)
  for i in range(3):
    x=158+i*36;FR(x,VH+6,32,28,0x303848);box2(x,VH+6,32,28,0xFFFF60 if i==ST['slot'] else 0x8090A0)
    it=ST['items'][i]
    if it is not None:
      textout(G,x+4,VH+13,["BAR","ERS","MAP"][it],[0xFFD040,0xFF90B0,0xFFF060][it])
  if ST['items'][ST['slot']] is not None:otext(268,VH+4,INAME[ST['items'][ST['slot']]][:7],0xFFFFFF)
  if ST['map']>0:minimap()
  #heartbeat: the screen edge pulses red when she is close
  if ST['active']:
    d=sqrt((M.x-PL.x)**2+(M.y-PL.y)**2)
    if d<10:
      k=(1-d/10)
      if int(ST['t']*(2+k*6))%2==0:
        w=int(2+k*8);c=0xC00000
        FR(0,0,SW,w,c);FR(0,VH-w,SW,w,c);FR(0,0,w,VH,c);FR(SW-w,0,w,VH,c)
  if PL.stun>0:ctext("HIT BY A PAPER PLANE!",80,0xFFFFFF)
  if ST['msgt']>0:ctext(ST['msg'],22,0xFFFFFF if not ST['nb']>=7 else 0x60FF80)
  if ST['btn']:
    lt,rt,fw,bk,run,it,sw=ctl
    tbtn(B_FW,fw,"^");tbtn(B_BK,bk,"v");tbtn(B_LT,lt,"<");tbtn(B_RT,rt,">")
    tbtn(B_RUN,run,"RUN",0x806020);tbtn(B_ITEM,it,"USE",0x308040);tbtn(B_SWAP,sw,"SWAP",0x404880)

#---------- game logic ----------
def los(x0,y0,x1,y1):
  dx=x1-x0;dy=y1-y0;d=sqrt(dx*dx+dy*dy);n=int(d*3)+1
  for i in range(1,n):
    t=i/n
    if solidAt(x0+dx*t,y0+dy*t):return 0
  return 1

def bfsPath(sx,sy,tx,ty):
  #shortest path on the grid (doors count as open for the teacher)
  if (sx,sy)==(tx,ty):return []
  prev={(sx,sy):None};q=[(sx,sy)];h=0
  while h<len(q):
    x,y=q[h];h+=1
    if (x,y)==(tx,ty):break
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
      nx=x+dx;ny=y+dy
      if (nx,ny) in prev:continue
      if nx<1 or ny<1 or nx>=MW-1 or ny>=MW-1:continue
      v=MAP[ny][nx]
      if v!=0 and v!=4:continue
      prev[(nx,ny)]=(x,y);q.append((nx,ny))
  if (tx,ty) not in prev:return []
  path=[];c=(tx,ty)
  while c!=(sx,sy):
    path.append(c);c=prev[c]
  path.reverse()
  return path

def tryMove(o,nx,ny,r=0.22):
  if not (solidAt(nx-r,o.y-r) or solidAt(nx+r,o.y-r) or solidAt(nx-r,o.y+r) or solidAt(nx+r,o.y+r)):o.x=nx
  if not (solidAt(o.x-r,ny-r) or solidAt(o.x+r,ny-r) or solidAt(o.x-r,ny+r) or solidAt(o.x+r,ny+r)):o.y=ny

def openDoorsNear(x,y):
  for (dx,dy) in DOORS:
    if abs(dx+0.5-x)<1.6 and abs(dy+0.5-y)<1.6:DOORS[(dx,dy)]=2.0

def useItem():
  it=ST['items'][ST['slot']]
  if it is None:
    say("No item in this slot",1.2);return
  ST['items'][ST['slot']]=None
  if it==0:PL.st=1.0;say("Energy Bar: stamina full!",2)
  elif it==1:
    d=sqrt((M.x-PL.x)**2+(M.y-PL.y)**2)
    if ST['active'] and d<6:M.stun=5.0;say("Eraser hit her glasses! She can't see for 5 s",2.5)
    else:say("Eraser wasted - throw it when she is close!",2)
  else:ST['map']=25.0;say("Sticky Map: notebooks on the map for 25 s",2.5)

def update(dt,fw,bk,lt,rt,run):
  ST['t']+=dt;ST['msgt']=max(0.0,ST['msgt']-dt)
  if ST['map']>0:ST['map']=max(0.0,ST['map']-dt)
  for k in DOORS:
    if DOORS[k]>0:DOORS[k]-=dt
  #player
  if PL.stun>0:
    PL.stun-=dt
  else:
    PL.a+=((1 if rt else 0)-(1 if lt else 0))*2.4*dt
    sp=0.0
    if fw:sp=2.6
    if bk:sp=-1.8
    if run and fw and PL.st>0:
      sp=4.4;PL.st=max(0.0,PL.st-dt*0.28)
    else:
      PL.st=min(1.0,PL.st+dt*(0.12 if sp else 0.2))
    wet=(int(PL.x),int(PL.y)) in B.wet
    vx=cos(PL.a)*sp;vy=sin(PL.a)*sp
    if wet:
      #slippery floor: you keep sliding
      PL.vx+=(vx-PL.vx)*min(1.0,dt*0.8);PL.vy+=(vy-PL.vy)*min(1.0,dt*0.8)
    else:
      PL.vx=vx;PL.vy=vy
    tryMove(PL,PL.x+PL.vx*dt,PL.y+PL.vy*dt)
  openDoorsNear(PL.x,PL.y)
  #pick-ups
  for e in ENTS:
    if e.alive and (e.x-PL.x)**2+(e.y-PL.y)**2<0.5:
      if e.t==0:
        e.alive=0
        ok=notebook()
        ST['nb']+=1
        if not ST['active']:
          ST['active']=1;say("Ms. Margin heard you... RUN!",3)
        if ok<3:ST['hunt']=10.0
        if ST['nb']>=7:say("All notebooks! Find a green EXIT sign!",5)
        elif ok==3:say("Perfect! She didn't notice. "+str(7-ST['nb'])+" to go",2.5)
        else:say(str(3-ok)+" wrong - she is angrier and knows where you are!",3)
        return
      else:
        slot=None
        if ST['items'][ST['slot']] is None:slot=ST['slot']
        else:
          for i in range(3):
            if ST['items'][i] is None:slot=i;break
        if slot is not None:
          ST['items'][slot]=e.kind;e.alive=0;say("Got "+INAME[e.kind],1.5)
  #exits
  if ST['nb']>=7:
    for (x,y) in EXITS:
      if abs(x+0.5-PL.x)<1.1 and abs(y+0.5-PL.y)<1.1:ST['win']=1
  #Ms. Margin
  if ST['active']:
    speed=1.5+0.38*ST['wrong']+0.12*ST['nb']
    if M.stun>0:
      M.stun-=dt
    else:
      sees=los(M.x,M.y,PL.x,PL.y) and (M.x-PL.x)**2+(M.y-PL.y)**2<200
      if sees or ST['hunt']>0:
        M.tx=PL.x;M.ty=PL.y;M.seen=1.0
      ST['hunt']=max(0.0,ST['hunt']-dt)
      M.rep-=dt
      if M.rep<=0:
        M.rep=0.35
        M.path=bfsPath(int(M.x),int(M.y),int(M.tx),int(M.ty))
        if not M.path and M.seen<=0:
          #wander to a random room
          r=ROOMS[rint(16)];M.tx,M.ty=r[0]+2.5,r[1]+2.5
        M.seen-=0.35
      if M.path:
        nx,ny=M.path[0]
        gx=nx+0.5;gy=ny+0.5
        dx=gx-M.x;dy=gy-M.y;d=sqrt(dx*dx+dy*dy)
        if d<0.1:M.path.pop(0)
        else:
          st=min(d,speed*dt);M.x+=dx/d*st;M.y+=dy/d*st
      elif sees:
        dx=PL.x-M.x;dy=PL.y-M.y;d=sqrt(dx*dx+dy*dy)+1e-6
        tryMove(M,M.x+dx/d*speed*dt,M.y+dy/d*speed*dt)
      openDoorsNear(M.x,M.y)
      if (M.x-PL.x)**2+(M.y-PL.y)**2<0.45:ST['dead']=1
  #Mop Bot patrols the hallways and leaves wet floors
  dirs=((1,0),(0,1),(-1,0),(0,-1))
  dx,dy=dirs[B.dir]
  nx=B.x+dx*1.3*dt;ny=B.y+dy*1.3*dt
  if solidAt(nx+dx*0.4,ny+dy*0.4) or rnd()<dt*0.15:
    B.dir=(B.dir+(1 if rnd()<0.5 else 3))%4
    B.x=int(B.x)+0.5;B.y=int(B.y)+0.5
  else:
    B.x=nx;B.y=ny
  B.wet[(int(B.x),int(B.y))]=8.0
  for k in list(B.wet.keys()):
    B.wet[k]-=dt
    if B.wet[k]<=0:del B.wet[k]
  #Paper-plane kid wanders and throws planes when he sees you
  K.cd-=dt
  if K.pl:
    px,py,vx,vy,life=K.pl
    px+=vx*dt;py+=vy*dt;life-=dt
    if solidAt(px,py) or life<=0:K.pl=None
    elif (px-PL.x)**2+(py-PL.y)**2<0.3:
      K.pl=None;PL.stun=1.4;say("Paper plane! You're dazed",1.5)
    else:K.pl=(px,py,vx,vy,life)
  d2=(K.x-PL.x)**2+(K.y-PL.y)**2
  if K.cd<=0 and d2<64 and los(K.x,K.y,PL.x,PL.y):
    d=sqrt(d2)+1e-6
    K.pl=(K.x,K.y,(PL.x-K.x)/d*5.0,(PL.y-K.y)/d*5.0,3.0);K.cd=5.0
  else:
    a=ST['t']*0.4+1.3
    tryMove(K,K.x+cos(a*0.7)*0.9*dt,K.y+sin(a)*0.9*dt)
  openDoorsNear(K.x,K.y)

#---------- screens ----------
def flip():
  strblit(0,0,0,320,240,G)
def screen(title,col,lines,bg=0x182030):
  FR(0,0,320,240,bg)
  for i in range(12):FR(0,40+i*16,320,1,mix(bg,0xFFFFFF,0.08))
  bigtext(title,30,5,col,0x000000)
  y=90
  for s in lines:
    ctext(s,y,0xF0F0F0);y+=15
  flip()
def waitkey(bits):
  release()
  while True:
    k=keyboard()
    for b in bits:
      if kd(k,b):return b
    if touches():
      release();return bits[0]
def title():
  screen("MATHRUN",0xFFD040,["Collect 7 notebooks and solve the math.",
    "Every WRONG answer makes Ms. Margin",
    "angrier, faster - and she hears you.",
    "Then escape through a green EXIT.",
    "RUN uses stamina. Items: Energy Bar,",
    "Eraser (stuns her), Sticky Map.",
    "Watch for wet floors and paper planes!",
    "","Tap or press Enter to start   Esc: quit"])
  return waitkey([K_ENTER,K_ESC])

def main():
  dimgrob(G,320,240,0)
  FR(0,0,320,240,0);ctext("Painting the school...",110,0xFFFFFF);flip()
  makeTextures()
  if title()==K_ESC:return
  newgame();gc.collect()
  last=ticks();prevk=keyboard();pit=0;psw=0
  while True:
    now=ticks();dt=(now-last)/1000.0;last=now
    if dt>0.12:dt=0.12
    if dt<=0:dt=0.01
    k=keyboard();pk=k&~prevk;prevk=k
    pts=touches() if ST['btn'] else []
    if kd(k,K_ESC):return
    fw=kd(k,K_UP) or inside(B_FW,pts)
    bk=kd(k,K_DN) or inside(B_BK,pts)
    lt=kd(k,K_LT) or inside(B_LT,pts)
    rt=kd(k,K_RT) or inside(B_RT,pts)
    run=kd(k,K_ENTER) or inside(B_RUN,pts)
    ti=inside(B_ITEM,pts);ts=inside(B_SWAP,pts)
    if kd(pk,K_SPC) or (ti and not pit):useItem()
    if kd(pk,K_PLUS) or (ts and not psw):ST['slot']=(ST['slot']+1)%3
    pit=ti;psw=ts
    if kd(pk,K_DEL):ST['btn']=1-ST['btn']
    if kd(pk,32) or kd(pk,34):
      i=RES.index(OPT[0]);i=max(0,i-1) if kd(pk,32) else min(len(RES)-1,i+1)
      OPT[0]=RES[i];say("Detail: "+str(OPT[0])+" columns",1.2)
    if kd(pk,K_MENU):ST['map']=0.0 if ST['map']>0 else 9999.0
    nb0=ST['nb']
    update(dt,fw,bk,lt,rt,run)
    if ST['nb']!=nb0:last=ticks();prevk=keyboard()
    if ST['dead']:
      screen("CAUGHT!",0xFF4040,["Ms. Margin caught you.","Detention for a week!",
        "Notebooks: "+str(ST['nb'])+"/7   Wrong answers: "+str(ST['wrong']),"",
        "Tap / Enter: try again    Esc: quit"],0x301010)
      if waitkey([K_ENTER,K_ESC])==K_ESC:return
      newgame();last=ticks();prevk=keyboard();continue
    if ST['win']:
      screen("YOU ESCAPED!",0x60FF80,["You got out with all 7 notebooks!",
        "Time: "+str(int(ST['t']))+" s   Wrong answers: "+str(ST['wrong']),
        "A+ for running!" if ST['wrong']==0 else "Study harder next time...","",
        "Tap / Enter: play again    Esc: quit"],0x103018)
      if waitkey([K_ENTER,K_ESC])==K_ESC:return
      newgame();last=ticks();prevk=keyboard();continue
    render()
    hud((lt,rt,fw,bk,run,ti,ts))
    flip()

main()
