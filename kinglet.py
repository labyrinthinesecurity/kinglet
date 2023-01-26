#!/usr/bin/python3 -u
from kingletcommon import *

for nd in range(0,len(nodes)):
  adder(nd,0,None)
  for c in range(1,len(containers)):
    adder(nd,c,X[nd][c-1])

m_1=str(len(containers)-1)
for nd in range(len(nodes)):
  for nm in range(2**logc):
    stringOfBits=int2strwrapper(nm,2,logc)
    expr='sol.add(Implies(And('
    j=-1
    val=0
    for b in stringOfBits:
      j=j+1
      if b=='0':
        expr=expr+'Not('
      expr=expr+'X['+str(nd)+']['+m_1+']['+str(j)+']'
      if b=='0':
        expr=expr+')'
      else:
        val=val+2**j
      expr=expr+','
    expr=expr[:-1]
    expr=expr+'),UGE(nodes['+str(nd)+'].size,'+str(val)+')))'
    if VERBOSE:
      print(nd,stringOfBits,expr)
    eval(expr)


for nd in range(len(nodes)):
#  print("NODE",nd)
  cnt=0
  for aA in nodes[nd].affinitySet:
#    print("  ","affinitySet["+str(cnt)+"]",nodes[nd].affinitySet[cnt])
    cnt=cnt+1

print("checking satisfiability...")
print('')
if sol.check()==sat:
  nodesol={}
  mdl = sol.model()
  if VERBOSE==True:
    for nd in range(len(nodes)):
      print("NODE",nd,"   (",mdl.evaluate(nodes[nd].node),")")
      print("  X["+str(nd)+"]["+str(m-1)+"]")
      print("  ",end='')
      for j in range(logc):
        print(" ",mdl.evaluate(X[nd][m-1][j]),end='')
      print('')
      print("  C["+str(nd)+"]["+str(m-1)+"]")
      print("  ",end='')
      for j in range(logc):
        print(" ",mdl.evaluate(C[nd][m-1][j]),end='')
      print('')
      cnt=0
      for aA in nodes[nd].affinitySet:
        print("  affinitySet["+str(cnt)+"]",aA,mdl.evaluate(aA))
        cnt=cnt+1
      print('')
    print('')
  for nc in range(m):
    zv=mdl.evaluate(containers[nc].node)
    if zv not in nodesol:
      nodesol[zv]=0
    nodesol[zv]=nodesol[zv]+1
  if SAVE==True:
    for nd in range(len(nodes)):
      print("NODE",mdl.evaluate(nodes[nd].node),mdl.evaluate(nodes[nd].affinitySet[0]))
    for key in nodesol:
      print(key,nodesol[key])
  if VERBOSE==True:
    print(sol)
else:
  print("unsat...")
  print(sol)
