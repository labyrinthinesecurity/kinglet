#!/usr/bin/python3 -u
from kingletcommon import *

buf=[]
loc=[]
sm=[]
ssmv=[]
sums=[]

for n in range(0,len(nodes)):
  for m in range(0,len(nodes)):
    if n!=m:
      sol.add(Not(nodes[n].node==nodes[m].node))
      if VERBOSE==True:
        print('sol.add(Not(nodes['+str(n)+'].node==nodes['+str(m)+'].node))')

if RELAXEDSIZE==False:
  for n in range(0,len(nodes)):
    sums.append([])
    buf.append([])
    loc.append([])
    sm.append([])
    ssmv.append([])
    for j in range(0,logc):
      buf[n].append([])
  for n in range(0,len(nodes)):
    print("")
    print("Node="+str(n))
    for j in range(0,logc):
      buf[n][j]='N'+nodes[n].name+'b'+str(j) # buf = logc free variables for each node n
      bbv=addBit('N'+nodes[n].name+'b'+str(j))
      sol.add(Not(bbv))  # bound buffer to False
      if VERBOSE==True:
        print('sol.add(Not'+buf[n][j]+'))')
    for c in range(0,len(containers)):
      loc[n].append([])
      sm[n].append([])
      for j in range(0,logc):
        loc[n][c].append([])
        if j>0:
          loc[n][c][j]='False' # logc-1 variables bound to False for each node n
        else:
          loc[n][c][j]=containers[c].name+'_'+str(n) #1 variable bounded the container node for each node n
      if c==0:
  #      print("adder 1")
        auxv=adderNregisters(buf[n],loc[n][c],logc)  # input: 2 logc registers, output: 1 logc bit
  #      print("AUXV",auxv)
        print("adder1",buf[n],loc[n][c],logc)
      elif c>0:
  #      print("adder 2")
        print("CCC",n,c)
        auxv=adderNregisters(sm[n][c-1],loc[n][c],logc)
      else:
        pass
#        auxv=adderNregisters(buf[n],loc[n][c],logc)  # input: 2 logc registers, output: 1 logc bit
  #      print("adder2",sm[n][c-1],loc[n][c],logc)
      for j in range(0,len(auxv)):
        sm[n][c].append([])
        sm[n][c][j]=auxv[j]['name']
  #      print("adder",n,sm[n][c][j])
      if c==len(containers)-1:   # the last sm[n][c]contans the accumulation of all containers, it goes to sums[n]
        sums[n]=sm[n][c]
  #  print(len(sums[n]),sums[n])
    for val in range(0,2**len(sums[n])):
      u_expr='sol.add(Implies(And('
      sbit=int2strwrapper(val,2,logc)   
      print('SBIT',sbit,val)
      cnts=-1
      vz=0
      for s in reversed(sbit):
        cnts=cnts+1 
        if s=='1':
          vz=vz+2**cnts
          leftb=''
          rightb=''
        else:
          leftb='Not('
          rightb=')'
        rnk=searchBit(sums[n][cnts])
        u_expr=u_expr+leftb+'registers['+str(rnk)+']["value"]'+rightb+','
      u_expr=u_expr[:-1]+'),UGE(nodes['+str(n)+'].size,'+str(vz)+')))'
  #    print(s,sums[n][cnts])
      if VERBOSE==True:
        print(u_expr)
      eval(u_expr)
#sys.exit()

pernode=[]
cos={}
for n in range(0,len(nodes)):
  pernode.append([])
  pernode[n]=[]
  for j in range(0,logc):
    pernode[n].append([])

print("checking satisfiability...")
if sol.check()==sat:
  print("SAT!")
  mdl=sol.model()
  for d in mdl.decls():
      nodenum=-1
      for aSN in sums:  
        nodenum=nodenum+1
        for aN in reversed(aSN):
          trail=findall(r"\d+$",aN)
#          print("TRAIL",trail[0],aN)
#          print("aN",aN,nodenum)         
          if d.name()==aN:
            pernode[nodenum][int(trail[0])]=mdl[d]
            print(str(nodenum)+">",d.name(),mdl[d])
  for d in mdl.decls():
    if d.name()[:10]=='container_':
      cc=d.name()[10:]
      for e in mdl.decls():
        if str(mdl[e])==str(mdl[d]):
          if e.name()[:5]=='node_':
            cos[cc]=e.name()[5:]
#            print(cos[cc],e.name(),d.name())
#            sys.exit()
  if True:
    print(sol)
    for d in mdl.decls():
      print(" >", d.name(),mdl[d])
  for aC in cos:
    for aN in nodes:
      if aN.name==cos[aC]:
        print('Container',aC,'goes to node',cos[aC]," (size: "+str(aN.max_size)+")")
  n=-1
  if RELAXEDSIZE==False:
    for aN in pernode:
      n=n+1
      print("Pernode sums for node",n,aN)
else:
  if VERBOSE==True:
    print(sol)
  print('unsat...')

