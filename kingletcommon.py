#!/usr/bin/python3 -u
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

NODENUM=3
CONTAINERNUM=3

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
  node=None
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
    self.node=Const('node_'+str(name),NodeSort)
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
      expr=expr+'And(self.node==nodes['+str(i)+'].node,self.locations['+str(i)+'],'
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
      expr=expr+'self.node==nodes['+str(i)+'].node,'
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
