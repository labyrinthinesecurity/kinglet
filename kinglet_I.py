#!/usr/bin/python3 -u
from kingletcommon import *

exprs=[]
for n in range(0,2**len(containers)):
  aexpr='sol.add(Implies(And('
  exprs.append(aexpr)

for i in range(0,2**len(containers)):
  sbit=int2strwrapper(i,2,len(containers))
  nots=0
  for j in sbit:
    if j=='0':
      nots=nots+1
  for n in range(0,len(nodes)):
    c=0
    for j in sbit:
      if j=="0":
        openb='Not('
        endb=')'
      elif j=='1':
        openb=''
        endb=''
      exprs[i]=exprs[i]+openb+'containers['+str(c)+'].locations['+str(n)+']'+endb
      if c<len(sbit)-1:
        exprs[i]=exprs[i]+','
      else:
        exprs[i]=exprs[i]+')'
      c=c+1
    exprs[i]=exprs[i]+',UGE(nodes['+str(n)+'].size,'+str(len(containers)-nots)+'))'
    if n<len(nodes)-1:
      exprs[i]=exprs[i]+',Implies(And('
  exprs[i]=exprs[i]+')'
  eval(exprs[i])
  print(i,exprs[i])

cos={}

#print(sol)
#print("model",sol.check())

if sol.check()==sat:
  mdl=sol.model()
  for d in mdl.decls():
    if d.name()[:10]=='container_':
      cc=d.name()[10:]
      for e in mdl.decls():
        if str(mdl[e])==str(mdl[d]):
          if e.name()[:5]=='node_':
            cos[cc]=e.name()[5:]
  if VERBOSE:
    print(sol)
    for d in mdl.decls():
      print(" >", d.name(),mdl[d])
  for aC in cos:
    for aN in nodes:
      if aN.name==cos[aC]:
        print('Container',aC,'goes to node',cos[aC],"(node size: "+str(aN.max_size)+")")
else:
  print(sol)
  print('unsat')
