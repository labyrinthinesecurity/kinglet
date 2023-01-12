#!/usr/bin/python3 -u
from kingletcommon import *

n=len(nodes)
m=len(containers)

print("nodes",n,"containers",m,"logc",logc)


X = [ [ [Const("X_%s_%s_%s" % (k, j, i), BoolSort()) for i in range(logc)] for j in range(m)] for k in range(n)]
C = [ [Const("C_%s_%s" % (k, i), BoolSort()) for i in range(logc)] for k in range(n)]

ZERO = [Const("ZERO_%s" % i, BoolSort()) for i in range(logc)]
ONE = [Const("ONE_%s" % i, BoolSort()) for i in range(logc)]

z = [ Const("z_%s" % i, BoolSort()) for i in range(len(nodes)*len(containers)*logc)]

carry = [ Const("carry_%s" % i, BoolSort()) for i in range(len(nodes)*len(containers)*logc)]

for i in range(logc):
  sol.add(ZERO[i]==False)
  if i>0:
    sol.add(ONE[i]==False)
  else:
    sol.add(ONE[i]==True)

#NO capacity:
#  X[N0][C0]= 000 + 001 if C0.locations[N0]
#             000 if not
#...
#  X[N0][Cm]= X[N0][Cm-1] + 001 if Cm.locations[N0]
#             X[N0][Cm-1] if not
#
#define zero = 000 and one = 001
#  X[N0][C0]=addder(None,C0.locations[N0])
#  X[N0][Cm]=addder(X[N0][Cm-1],Cm.locations[N0])
#

def adder(curN,curC,left):
  if left is None:
    zleft=ZERO
  else:
    zleft=left
  sol.add(X[curN][curC][0]== And(Or(zleft[0], containers[curC].locations[curN]), Not(And(zleft[0], containers[curC].locations[curN]))))
  sol.add(C[curN][0] == If( And(zleft[0], containers[curC].locations[curN]),True, False))
  for i in range(1,logc):
    if i<logc-1:
      sol.add(C[curN][i] == Or(And(zleft[i], containers[curC].locations[curN]), And(zleft[i], C[curN][i-1]), And(containers[curC].locations[curN], C[curN][i-1])))
    sol.add(X[curN][curC][i] == If(C[curN][i-1],zleft[i]==containers[curC].locations[curN], Xor(zleft[i], containers[curC].locations[curN])))

for nd in range(n):
  adder(nd,0,None)
  for c in range(1,m):
    adder(nd,c,X[nd][c-1])


for nd in range(0,len(nodes)):
  for m in range(0,len(nodes)):
    if nd!=m:
      sol.add(Not(nodes[nd].node==nodes[m].node))
      if VERBOSE==True:
        print('sol.add(Not(nodes['+str(n)+'].node==nodes['+str(m)+'].node))')

print("checking satisfiability...")
if sol.check()==sat:
  mdl = sol.model()
  for nd in range(n):
    print("NODE",nd)
    for j in range(logc):
      print(" ",j,mdl.evaluate(X[nd][m-1][j]),end='')
    print('')
