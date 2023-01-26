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


VERBOSE=False
SAVE=True
INTERACTIVE=False

rand=False

NODENUM=args.nodes
CONTAINERNUM=args.pods

if args.pods>args.nodes*args.capability:
#  args.capability=1+int(args.pods/args.nodes)
  print("WARNING! Insufficiant capability detected.")
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

affinities={}
affinities['up']='up'
affinities['down']='down'
affinities['white']='white'
affinities['black']='black'
affinities['small']='small'
affinities['big']='big'
affinities['far']='far'
affinities['close']='close'

affinities['jupiter']='jupiter'
affinities['venus']='venus'
affinities['mars']='mars'
affinities['mercury']='mercury'

affinities['old']='old'
affinities['aged']='aged'
affinities['soft']='soft'
affinities['good']='good'

affinities['cat']='cat'
affinities['dog']='dog'
affinities['bird']='bird'
affinities['snake']='snake'
affinities['camel']='camel'

direction={'up': 'down'}
color={'white': 'black'}
size={'big': 'small'}
distance={'far': 'close'}
antiAffinities= [ direction, color, size, distance ]

nodes=[]
containers=[]
digits = "0123456789ABCDEF"

class node:
  node=None
  size=None
  max_size=None
  name=None
  affinitySet=None
  AffinitySort=None

  def __init__(self,name,msize):
    global sol
    global affinities
    global antiAffinities
    self.node=Const('node_'+str(name),NodeSort)
    self.name=name
    self.max_size=msize
    self.affinitySet=[]
    self.AffinitySort=DeclareSort('Affinity_n'+str(name))
    aA=Const('n'+str(name)+"_ground_affinity",self.AffinitySort)
    self.affinitySet.append(aA)
    for aAK in affinities.keys():
      aA=Const('n'+str(name)+"_affinity_"+str(aAK),self.AffinitySort)
      self.affinitySet.append(aA)
    self.size=BitVec('size_n'+str(node),16)
    sol.add(ULE(self.size,msize))
    sol.add(UGE(self.size,0))
    if VERBOSE==True:
      print("sol.add(ULE("+self.name+".size,"+str(msize)+'))')
    for aA in antiAffinities:
      aK=list(aA.keys())[0]
      aV=list(aA.values())[0]
      cntfound=1  # 0 is reserved for ground affinity!
      for aAK in affinities.keys():
        if aAK==aK:
          cntantifound=1
          for aAK in affinities.keys():
            if aAK==aV:
#              print(cntfound,cntantifound,"antifound",aK,aV,self.affinitySet[cntfound],"!=",self.affinitySet[cntantifound])
              if VERBOSE==True:
                print('sol.add(self.affinitySet['+str(cntfound)+']!=self.affinitySet['+str(cntantifound)+']')
              sol.add(self.affinitySet[cntfound]!=self.affinitySet[cntantifound])
              break
            cntantifound=cntantifound+1
        cntfound=cntfound+1

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
    print('Container',self.name,end='')
    for i in range(0,len(nodes)):
      self.locations.append(Const(str(name)+'_'+str(i),BoolSort()))
      addBit(str(name)+'_'+str(i))
    self.node=Const('node_'+str(name),NodeSort)
    cnt=0
    for aAK in affinities.keys():
      for aA in affs:
        if aA==aAK:
#          print(cnt,aA,aAK)
          self.affinities.append(cnt)
          break
      cnt=cnt+1
    expr='sol.add(Or('
    for i in range(0,len(nodes)):
      expr=expr+'self.node==nodes['+str(i)+'].node,'
    expr=expr[:-1]
    expr=expr+'))'
    if VERBOSE==True:
      print("  "+expr)
    eval(expr)
    print("  ",self.affinities)
    for i in range(0,len(nodes)):
      expr='sol.add('
      expr=expr+'Implies(self.node==nodes['+str(i)+'].node,And(self.locations['+str(i)+'],'
      for a in self.affinities:
#        print("a",a)
        expr=expr+'nodes['+str(i)+'].affinitySet[0]==nodes['+str(i)+'].affinitySet['+str(a+1)+'],'
      for j in range(0,len(nodes)):
        if i!=j:
          expr=expr+'Not(self.locations['+str(j)+'])'
          if j<len(nodes):
            expr=expr+','
        if j==len(nodes)-1:
          expr=expr[:-1]
      expr=expr+')))'
      if VERBOSE==True:
        print("  "+expr)
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
   zN=node(str(i),size)
   nodes.append(zN)
   for aN in nodes[:-1]:
     sol.add(aN.name!=zN.name)
for i in range(0,CONTAINERNUM):
   zaffs=[]
   j=random.randint(1,4)*random.randint(1,4)
   if j>7:
     j=6
   elif j>6:
     j=5
   elif j>4:
      j=4
   elif j>2:
     j=3
   elif j>1:
     j=2
   else:
    j=1
   for k in range(0,j):
     l=random.choice(list(affinities.values()))
     found=False
     print("checking ",l,zaffs)
     for aA in antiAffinities:
        aK=list(aA.keys())[0]
        aV=list(aA.values())[0]
        if aK==l:
          for aF in zaffs:
            print("+"+aF)
            if aF==aV:
              found=True
#              print("contradiction",l,zaffs)
              break
        if aV==l:
          for aF in zaffs:
            if aF==aK:
              found=True
#              print("contradiction",l,zaffs)
              break
     if found==False:
       zaffs.append(str(l))
     print("final",zaffs)
   zC=container('C'+str(i),zaffs)
   containers.append(zC)

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
    print("node ",aN.name,"size ",aN.max_size)
  for aC in containers:
    print(aC.name,aC.affinities)
print("")
