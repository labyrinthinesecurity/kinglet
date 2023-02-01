![alt text](https://github.com/labyrinthinesecurity/kinglet/blob/main/banner.png?raw=true)

# Introduction
Let the tiny king guide you through the intricacies of automated reasoning... Under His Enlightened Command, learn how Z3, a state-of-the-art SMT (Satisfiability Modulo Theories) solver leverages Bitvectors theory, Propositional logic theory and Equality theory to enforce memory constraints and to meet affinity and anti-affinity constraints on a Kubernetes-like cluster.

Kinglet simulates how the scheduler part of a Kubernetes orchestrator distributes workloads over a cluster, in a provable way.

## Quickstart

```
./kinglet.py --nodes 2 --pods 50 --camability 30
```

Places 50 pods on 2 nodes, each node can hold up to 30 pods. Affinities are set at random.

# Installation

Kinglet is a python3 script. For most of us, the only module one might have to install is the z3 module... Very simple!

# Options

Run kinglet.py --help 

Possible options are:
- ***nodes N*** number N of worker nodes in the cluster
- ***pods P*** number P of pods/containers to launch on the cluster
- ***capability C*** the max number C of pods/containers a node may run
- ***seed S*** a seed for the Pseudo Ranom Numbers Generator. Useful if you want to give consistent placements between several runs

## Controling verbosity

If you want to see how Kinglet constructs a SMT model on-the-fly and see the solutions (if there are any!), set VERBOSE to True.

# Constraints

Each time kinglet is run, it will attach random constraints to containers. The constraints can be of three types:
- affinity
- anti-affinity
- no constraint at all for this container

Please note that, as of today, the random generator is rather silly and may attach contradictory constraints to a container.

## Affinities

Affinities are declared in the ***affinities*** dictionary. Feel free to add/remove your own!

## Anti-affinities

Affinities are declared in the ***affinities*** dictionary. Feel free to add/remove your own!

It is also possible to mix and match affinities and anti-affinities 

# Behind the scenes

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
Or(self.node==nodes[0].node,...,self.node==nodes[NODENUM-1])
```

They are also fitted with a list of AffinitySort variables: one for each possible affinity or anti-affinity: *self.affinities*

```
And(self.affinity['old']==affinity['old'],...,self.affinity['small']==affinity['small'])
```

Finally, they contain a list of as many BoolSort variables *self.location* as there are nodes. *self.location[i]* is set to **True** if *self.container* is set to node number i, and to **False** otherwise:

```
And(self.node==nodes[n].node,self.location[n],Not(self.location[0],...,Not(self.location[NODENUM-1])
```

## Equality theory for affinity constraints

Each time a container is created, all the affinities and anti-affinities attached to this container are equated. So all affinities and anti-affinities of this container belong to the same **equivalence class**.

When Z3 attempts to attach a container to a node, the affinity of this node is also added to the equivalence class of the container:
- if this is not possible, Z3 tries to find another "compatible" node
- if it can't then the scheduling is unsatisfiable

## Bitvectors theory for size constraints

Each container c has a list of n *container[c].location[n]* BoolSort variables. All these Booleans are False except the one corresponding to the node chosen by Z3. 

For example, if container 54 is hosted on node 4, then container[53].location[3] will be True. All other locations under container[53] will be False.

So for each node it is easy to set a lower bound to its capacity: for a given node n, we write as many Implies statements as there as possible combinations of container locations set to n.

## Propositional logic theory for unifying size and affinity

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
