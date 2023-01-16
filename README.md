![alt text](https://github.com/labyrinthinesecurity/kinglet/blob/main/banner.png?raw=true)

# Introduction

Let the tiny king guide you through the intricacies of automated reasoning... Under His Enlightened Command, learn how Z3, a state-of-the-art SMT (Satisfiability Modulo Theories) solver leverages propositional logic to enforce memory constraints and to meet affinity and anti-affinity constraints on a Kubernetes-like cluster.

Kinglet simulates how the scheduler part of a Kubernetes orchestrator distributes workloads over a cluster, in a provable way.

# Installation

Kinglet is a python3 script. For most of us, the only module one might have to install is the z3 module... Very simple!

# Options

## Disabling interactions

By default, the INTERACTIVE variable is set to True: the Good King will display a splash screen and ask you some questions. Since the first question is whether you want to run one of the tutorial described below, I strongly advise you to let it as it is.

## Controling verbosity

If you want to see how Kinglet constructs a SMT model on-the-fly and see the solutions (if there are any!), set VERBOSE to True.

## Playing with the number of nodes and/or containers

Set NODENUM to the number of nodes in a cluster, and CONTAINERNUM to the number of containers to schedule.

# Default constraints

## Affinities

Only affinity is set by default: *old*. Feel free to add your own!

Kinglet will do its best to run containers sharing the same affinity labels on the same nodes.

## Anti-affinities

4 pairs of anti-affinities are set by default:
- *up* versus *down*
- *black* versus *white*
- *big* versus *small*
- *close* versus *far*

Any label in one pair can be freely combined with any label in another pair. For example, a container may be attached labels *black* and *down*.

It is also possible to mix and match affinities and anti-affinities on a same container. For example, *up*, *close* and *old*.


# Samples and customization

## Samples
When you run kinglet in INTERACTVE mode, enter numbers 1 to 4 to select one of the samples.

## Customization

To skip samples, enter 0. You will be asked for a series of questions to customize a test run:
- how many nodes
- what is the size of the nodes
- how many containers

# Behind the scene

Kinglet is a dynamic solver: the Z3 SMT model is built on-the-fly depending to the number of containers and nodes on the cluster. Thank you Python's eval() function!

Affinity and size constraints depend on one another, since placing a container on a node given an affinity constraint depends on the node "free space" capacity. 
In the code, intrication is materialized by propositional logic statements of the form:

```
Implies(And(affinity constraints), lower bound on Bitvector node capacity)
```

## Classes

Nodes and containers are specified in the common file **kingletcommon.py**

### The node class

- nodes have a hardcoded maximum capacity: *self.max_size*. By default, it is set to DEFAULTMAXSIZE.
- the current capacity is expressed as a variable of type BitVector, *self.size*, which has a lower bound (UGE) set to 0 and and upper bound (ULT) set to self.max_size
- nodes are also equipped with an AffinitySort variablr: *self.affinities[0]*
- only the first item in the self.affinities list is used.

### The container class

Containers are equiped with a variable of type NodeSort, *self.node*, that is used to express to which node the container is scheduled. A constraint is placed on this variable to force it to be equal to an existing node expressed as a NodeSort

```
Or(self.node==nodes[0].node,...,self.node==nodes[NODENUM])
```

They are also fitted with a list of AffinitySort variables: one for each possible affinity or anti-affinity: *self.affinities*

```
And(self.affinity['old']==affinity['old'],...,self.affinity['small']==affinity['small'])
```

Finally, they contain a list of as many BoolSort variables *self.location* as there are nodes. *self.location[i]* is set to **True** if *self.container* is set to node number i, and to **False** otherwise:

```
And(self.node==nodes[n].node,self.location[n],Not(self.location[0],...,Not(self.location[NODENUM])
```

## Equality for affinity constraints

Each time a container is created, all the affinities and anti-affinities attached to this container are equated. So all affinities and anti-affinities of this container belong to the same **equivalence class**.

When Z3 attempts to attach a container to a node, the affinity of this node is also added to the equivalence class of the container:
- if this is not possible, Z3 tries to find another "compatible" node
- if it can't then the scheduling is unsatisfiable

## Bitvector for size constraints

Each container c has a list of n *container[c].location[n]* BoolSort variables. All these Booleans are False except the one corresponding to the node chosen by Z3. 

For example, if container 54 is hosted on node 4, then container[53].location[4] will be True. All other locations under container[53] will be False.

So for each node it is easy to set a lower bound to its capacity: for a given node n, we write as many Implies statements as there as possible combinations of container locations set to n.

Imagine that we have 7 containers to place on just one node. Addressing 7 containers takes only a 3-bits register R0, R1, and R2.

```
Implies(Not(R0),Not(R1),Not(R2), UGE(nodes[1].size,0))
...
Implies(R0,R1,R2, UGE(nodes[1].size,7))
```

To define registers R0 to R2, we make bitwise addition of all container locations node 1:

```
(R0,R1,R2)= containers[0].location[1]+containers[1].location[1]+...containers[6].location[1]
```

The bitwise addition is performed by the adder() function.

# License information
The cover picture is copyright Adobe Photo Stock. It is used with permission.

The rest of this repository is licensed under 
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
