#!/usr/bin/python3 -u
from z3 import *
import random,math,sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--nodes", type=int, nargs='?', default=2, help="number of worker nodes in cluser (default: 2 nodes)")
parser.add_argument("--pods", type=int, nargs='?', default=2, help="number of pods in cluser (default: 2 pods)")
parser.add_argument("--capability", nargs='?', default=2, type=int, help="how many pods per node ,at most (default: max 2 pods per node)")
parser.add_argument("--seed", type=int, nargs='?', const=1, help="seed for the RNG (default: no seed)")
args = parser.parse_args()


VERBOSE=True
SAVE=True
INTERACTIVE=False

rand=False

NODENUM=args.nodes
CONTAINERNUM=args.pods
DEFAULTSIZE=args.capability

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

up,down,white,black,small,big,far,close,old,aged,jupiter,venus,mars,mercury,soft,good,cat,dog,bird,snake,camel=Consts('up down white black small big far close old aged jupiter venus mars mercury soft good cat dog bird snake camel',AffinitySort)
affinities={}
affinities['up']=up
affinities['down']=down
affinities['white']=white
affinities['black']=black
affinities['small']=small
affinities['big']=big
affinities['far']=far
affinities['close']=close

affinities['jupiter']=jupiter
affinities['venus']=venus
affinities['mars']=mars
affinities['mercury']=mercury

affinities['old']=old
affinities['aged']=aged
affinities['soft']=soft
affinities['good']=good

affinities['cat']=cat
affinities['dog']=dog
affinities['bird']=bird
affinities['snake']=snake
affinities['camel']=camel

sol.add(up!=down)   # anti affinity
sol.add(white!=black) # anti affinity
sol.add(big!=small) # anti affinity
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
    sol.add(ULE(self.size,msize))
    sol.add(UGE(self.size,0))
    if VERBOSE==True:
      print("sol.add(ULT("+self.name+".size,"+str(msize)+'))')

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
    if VERBOSE==True:
      print('Container',self.name)
    for i in range(0,len(nodes)):
      self.locations.append(Const(str(name)+'_'+str(i),BoolSort()))
      addBit(str(name)+'_'+str(i))
    self.node=Const('node_'+str(name),NodeSort)
    for aA in affs:
      nza=Const('affinity_c'+str(name)+'_'+aA,AffinitySort)
      self.affinities.append(nza)
      sol.add(nza==affinities[aA])
      if VERBOSE==True:
        print('  sol.add('+'affinity_c'+str(name)+'_'+aA+'==affinities['+aA+'])')
    expr='sol.add(Or('
    for i in range(0,len(nodes)):
      if i>0:
        expr=expr+','
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
    expr=expr+'))'
    if VERBOSE==True:
      print("  "+expr)
    eval(expr)
    expr='sol.add(Or('
    for i in range(0,len(nodes)):
      expr=expr+'self.node==nodes['+str(i)+'].node,'
    expr=expr[:-1]
    expr=expr+'))'
    eval(expr)

def adder(curN,curC,left):
  global X
  global containers
  if curC==0:
    sol.add(X[curN][curC][0]==containers[curC].locations[curN])
    sol.add(C[curN][curC][0]==False)
    for i in range(1,logc):
      sol.add(X[curN][curC][i]==False)
      sol.add(C[curN][curC][i]==False)
    return
  if left is None:
    print("killed")
    sys.exit()
  zleft=left
  sol.add(X[curN][curC][0] == Xor(containers[curC].locations[curN], zleft[0]))
  sol.add(C[curN][curC][0] == And(containers[curC].locations[curN], zleft[0]))
  for i in range(1,logc):
    sol.add(X[curN][curC][i] == Xor(C[curN][curC][i-1], zleft[i]))
    sol.add(C[curN][curC][i] == And(C[curN][curC][i-1], zleft[i]))

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
  return rez[::-1]+prefix

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

if args.seed:
  random.seed(args.seed)
for i in range(0,NODENUM):
   if rand:
     size=random.randint(3,6)
   else:
     size=DEFAULTSIZE
   nodes.append(node(str(i),size))
for i in range(0,CONTAINERNUM):
   zaffs=[]
   j=random.randint(1,4)*random.randint(1,4)
   if j>11:
     j=1
   elif j>2:
     j=0
   for k in range(0,j):
     l=random.choice(list(affinities.values()))
     zaffs.append(str(l))
   print(zaffs)
   zC=container('C'+str(i),zaffs)
   containers.append(zC)
   for aC in containers[:-1]:
     sol.add(aC.node!=zC.node)

logc=1+int(math.floor(math.log(len(containers),2)))

n=len(nodes)
m=len(containers)

X = [ [ [Const("X_%s_%s_%s" % (k, j, i), BoolSort()) for i in range(logc)] for j in range(m)] for k in range(n)]
C = [ [ [Const("C_%s_%s_%s" % (k, j, i), BoolSort()) for i in range(logc)] for j in range(m)] for k in range(n)]

ZERO = [Const("ZERO_%s" % i, BoolSort()) for i in range(logc)]
ONE = [Const("ONE_%s" % i, BoolSort()) for i in range(logc)]
 for i in range(logc):
  sol.add(ZERO[i]==False)
  if i>0:
    sol.add(ONE[i]==False)
  else:
    sol.add(ONE[i]==True)

print("")
print("N=",len(nodes)," C=",len(containers)," logc="+str(logc),"SIZE=",DEFAULTSIZE,"seed=",str(args.seed))
if VERBOSE==True:
  for aN in nodes:
    print(aN.name,aN.max_size,end=' ')
    for aA in aN.affinities:
      print(aA,end='')
    print('')
  for aC in containers:
    print(aC.name,aC.affinities)
print("")
    
