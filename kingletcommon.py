#!/usr/bin/python3 -u
#from common import *
from z3 import *
import random,math,sys
import hashlib
from uuid import *
from re import *

VERBOSE=True
DEFAULTSIZE=5
RELAXEDSIZE=False
INTERACTIVE=False

rand=False
sample=0

NODENUM=2
CONTAINERNUM=7

sol=Solver()
registers=[]
false=Const('False',BoolSort())
sol.add(Not(false))
aC={}
aC['name']='False'
aC['value']=false
registers.append(aC)
NodeSort=DeclareSort('Node')
AffinitySort=DeclareSort('Affinity')

up,down,white,black,small,big,far,close,old,aged=Consts('up down white black small big far close old aged',AffinitySort)
affinities={}
affinities['up']=up
affinities['down']=down
affinities['white']=white
affinities['black']=black
affinities['small']=small
affinities['big']=big
affinities['far']=far
affinities['close']=close
affinities['old']=old
affinities['aged']=aged

sol.add(up!=down)   # anti affinity
sol.add(white!=black) # anti affinity
sol.add(big!=small) # anti affinity
sol.add(far!=close) # anti affinity

nodes=[]
containers=[]
digits = "0123456789ABCDEF"

class node:
  node=None
  size=None
  max_size=None
  affinities=None
  name=None

  def __init__(self,name,msize):
    global sol
    global affinities
    self.node=Const('node_'+str(name),NodeSort)
    self.name=name
    self.max_size=msize
    self.affinities=[]
    aA=Const('affinity_n'+str(name),AffinitySort)
    self.affinities.append(aA)
    self.size=BitVec('size_n'+str(node),16)
    sol.add(ULT(self.size,msize))
    sol.add(UGE(self.size,0))

class container:
  container=None
  affinities=None
  locations=None
  name=None

  def __init__(self,name,affs):
    global nodes
    global containers
    global affinities
    self.locations=[]
    self.affinities=[]
    self.name=name
    for i in range(0,len(nodes)):
      self.locations.append(Const(str(name)+'_'+str(i),BoolSort()))
      addBit(str(name)+'_'+str(i))
    self.container=Const('container_'+str(name),NodeSort)
    for aA in affs:
      nza=Const('affinity_c'+str(name)+'_'+aA,AffinitySort)
      self.affinities.append(nza)
      sol.add(nza==affinities[aA])
      if VERBOSE==True:
        print('sold.add('+'affinity_c'+str(name)+'_'+aA+'==affinities['+aA+'])')
    expr='sol.add(Or('
    for i in range(0,len(nodes)):
      if i>0:
        expr=expr+','
#      expr=expr+'Implies(self.container==nodes['+str(i)+'].node,And(self.locations['+str(i)+'],'
      expr=expr+'And(self.container==nodes['+str(i)+'].node,self.locations['+str(i)+'],'
      for a in range(0,len(self.affinities)):
        expr=expr+'Or('
        for b in range(0,len(nodes[i].affinities)):
          expr=expr+'self.affinities['+str(a)+']==nodes['+str(i)+'].affinities['+str(b)+']'
          expr=expr+','
          if b==len(nodes[i].affinities)-1:
              expr=expr[:-1]
        expr=expr+'),'
      for j in range(0,len(nodes)):
        if i!=j:
          expr=expr+'Not(self.locations['+str(j)+'])'
          if j<len(nodes):
            expr=expr+','
        if j==len(nodes)-1:
          expr=expr[:-1]
      expr=expr+')'
#    expr=expr+'))))'
    expr=expr+'))'
    if VERBOSE==True:
      print(expr)
    eval(expr)
    expr='sol.add(Or('
    for i in range(0,len(nodes)):
      expr=expr+'self.container==nodes['+str(i)+'].node,'
    expr=expr[:-1]
    expr=expr+'))'
    eval(expr)

def splashScreen():
  banner='''
                                    .---.
     .     .--.   _..._             |   |      __.....__
   .'|     |__| .'     '.   .--./)  |   |  .-''         '.
 .'  |     .--..   .-.   . /.''\\   |   | /     .-''"'-.  `.      .|
<    |     |  ||  '   '  || |  | |  |   |/     /________\   \   .' |_
 |   | ____|  ||  |   |  | \`-' /   |   ||                  | .'     |
 |   | \ .'|  ||  |   |  | /("'`    |   |\    .-------------''--.  .-'
 |   |/  . |  ||  |   |  | \ '---.  |   | \    '-.____...---.   |  |
 |    /\  \|__||  |   |  |  /'""'.\ |   |  `.             .'    |  |
 |   |  \  \   |  |   |  | ||     ||'---'    `''-...... -'      |  '.'
 '    \  \  \  |  |   |  | \'. __//                             |   /
'------'  '---''--'   '--'  `'---'                              `'-'
v1.0 (Godefroy the First)
               +--------------------------------------------+
               |    All your pods shall belong to me.       |
               |  github.com/labyrinthinesecurity/kinglet   |
               +--------------------------------------------+
'''
  print(banner)

def int2str(x, base, logw):
    rez=str(x) if x < base else int2str(x//base, base, logw) + digits[x % base]
    return rez

def int2strwrapper(x,base,logw):
  rez=int2str(x,base,logw)
  prefix=''
  if len(rez)<logw:
    delta=logw-len(rez)
    for i in range(0,delta):
      prefix=prefix+'0'
  return prefix+rez

def addBit(name):
  global registers
  aC={}
  aC['name']=name
  aC['value']=Const(name,BoolSort())
  registers.append(aC)
  return aC['value']

def searchBit(name):
  global registers
  n=0
  for aC in registers:
    if aC['name']==name:
      return n
    n=n+1
  return None

def half_adder1(a,b,sm,carry):
  global sol
  global registers
  foundA=False
  foundB=False
  foundSum=False
  foundCarry=False
  av=None
  bv=None
  sv=None
  cv=None
  zcarry=None
  zsum=None
  if (a is None) or (b is None):
    if a is None:
      a='False'
    if b is None:
      b='False'
    if carry is None:
      carry='c:'+str(uuid.uuid4())
  if carry is None:
    carry='c:'+a+'_'+b
  if sm is None:
    sm='s:'+a+'+'+b
  for c in registers:
    if c['name']==a:
      foundA=True
      av=c['value']
    elif c['name']==b:
      foundB=True
      bv=c['value']
    elif c['name']==sm:
      foundSum=True
      sv=c['value']
      zsum=c
    elif c['name']==carry:
      foundCarry=True
      cv=c['value']
      zcarry=c
  if foundA==False:
    av=addBit(a)
  if foundB==False:
    bv=addBit(b)
  if foundSum==False:
    sv=addBit(sm)
    for c in registers:
      if c['name']==sm:
        zsum=c
        break
  if foundCarry==False:
    cv=addBit(carry)
    for c in registers:
      if c['name']==carry:
        zcarry=c
        break
  sol.add(sv==Xor(av,bv),cv==And(av,bv))
  if VERBOSE==True:
    print('sol.add(sv==Xor('+a+','+b+'),'+carry+'==And(+'+a+','+b+'))')
#  print("(i) HALF "+a+" + "+b+" init with carry",zcarry['name'],"sum",zsum['name'])
  return zcarry,zsum

def adderNregisters(az,bz,nregisters):
  global sol
  zsm=[]
  zsm2=[]
  tsm=[]
  tsm2=[]
  for n in range(0,nregisters):
    zsm.append([])
    zsm2.append([])
    zsm[n]='s:'+az[n]+'+'+bz[n]+'b'+str(n)
    tsm.append([])
    tsm2.append([])
#  print("half0 IN",az[0],bz[0],zsm[0],None)
  carry,tsm[0]=half_adder1(az[0],bz[0],zsm[0],None)   
  tsm2[0]=tsm[0]
#  print("     OUT",carry,tsm2[0])
  for i in range(1,len(az)):
    prevcarry=carry
#    print("half1 IN",i,az[i],bz[i],zsm[i],None)
    carry,tsm[i]=half_adder1(az[i],bz[i],zsm[i],None)
    print("     OUT",carry,tsm[i])
    if i==1:
#      print("half2-first IN",prevcarry['name'],zsm[i],"None","None")
      carry2,tsm2[i]=half_adder1(prevcarry['name'],tsm[i]['name'],None,None)
#      print("           OUT",carry2,tsm2[i])
      for n in range(0,nregisters):
        zsm2[n]=tsm2[i]['name']+'b'+str(n)
    else:
#      print("half2-secnd IN",prevcarry['name'],zsm[i],zsm2[i],carry2['name'])
      carry,tsm2[i]=half_adder1(prevcarry['name'],zsm[i],zsm2[i],carry2['name'])
#      print("           OUT",carry2,tsm2[i])
  return tsm2

if INTERACTIVE:
  splashScreen()

  while True:
      try:
          sample = int(input("Which sample number? Enter 0 to skip[4|3|2|1|0]"))
      except ValueError:
          print("Sorry, I didn't understand that.")
          continue
      else:
          if sample<=4 and sample>=0:
            break
          else:
            print("Sorry, I didn't understand that.")
            continue
  while True and sample==0:
      try:
          NODENUM = int(input("How many nodes[1-5]?"))
      except ValueError:
          print("Sorry, I didn't understand that.")
          continue
      else:
          if NODENUM<=5 and NODENUM>0:
            break
          else:
            print("Sorry, I didn't understand that.")
            continue
  while True and sample==0:
      try:
          CONTAINERNUM = int(input("How many containers[1-10]?"))
      except ValueError:
          print("Sorry, I didn't understand that.")
          continue
      else:
          if CONTAINERNUM<=10 and CONTAINERNUM>0:
            break
          else:
            print("Sorry, I didn't understand that.")
            continue

  while True and sample==0:
    try:
      qrand = int(input("Randomized node sizes?[1|0]?"))
    except ValueError:
      print("Sorry, I didn't understand that.")
      continue
    else:
      if qrand>=0 and qrand<=1:
        rand=False
        if qrand==1:
          rand=True
        break
      else:
        print("Sorry, I didn't understand that.")
        continue
if sample>0:
  VERBOSE=False
  rand=False

if sample==0:
  for i in range(0,NODENUM):
    if rand:
      size=random.randint(3,6)
    else:
      size=DEFAULTSIZE
    nodes.append(node(str(i),size))
  for i in range(0,CONTAINERNUM):
    containers.append(container('C'+str(i),['close','old']))
elif sample==1:
# 4 nodes,up!down,white!=black,big!small,far!close,aged,old AC:1 B:2 D:3  E:0
  NODENUM=4
  for i in range(0,NODENUM):
    nodes.append(node(str(i),DEFAULTSIZE))
  containers.append(container('A',['black','up','close']))
  containers.append(container('B',['down','small']))
  containers.append(container('C',['up','big']))
  containers.append(container('D',['white','small']))
  containers.append(container('E',['close']))
elif sample==2:
# 2 nodes,up!down,white!=black,big!small,far!close,aged,old ACE:1 BD:0
  NODENUM=2
  for i in range(0,NODENUM):
    nodes.append(node(str(i),DEFAULTSIZE))
  containers.append(container('A',['black','up','close']))
  containers.append(container('B',['down','small']))
  containers.append(container('C',['up','big']))
  containers.append(container('D',['white','small']))
  containers.append(container('E',['close']))
elif sample==3:
# 3 nodes,up!down,white!=black,big!small,far!close,aged,old AC:1  BD:2 E: 0
  NODENUM=3
  for i in range(0,NODENUM):
    nodes.append(node(str(i),DEFAULTSIZE))
  containers.append(container('A',['black','up','close']))
  containers.append(container('B',['down','small']))
  containers.append(container('C',['up','big']))
  containers.append(container('D',['white','small']))
  containers.append(container('E',['close']))
elif sample==4:
# 3 nodes,up!down,white!=black,big!small,far!close,aged,old ACE:2  BD:1
  NODENUM=3
  for i in range(0,NODENUM):
    nodes.append(node(str(i),DEFAULTSIZE))
  containers.append(container('A',['black','up','close','old']))
  containers.append(container('B',['down','small']))
  containers.append(container('C',['up','big']))
  containers.append(container('D',['white','small']))
  containers.append(container('E',['close','old']))

logc=1+int(math.floor(math.log(len(containers),2)))
print("N=",len(nodes)," C=",len(containers),"("+str(logc)+")")

