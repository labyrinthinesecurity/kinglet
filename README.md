![alt text](https://github.com/labyrinthinesecurity/kinglet/blob/main/banner.png?raw=true)

# Introduction

Let the tiny king guide you through the intricacies of automated reasoning... Under His Enlightened Command, learn how Z3, a state-of-the-art SMT (Satisfiability Modulo Theories) solver leverages propositional logic to enforce memory constraints and to meet affinity and anti-affinity constraints on a Kubernetes-like cluster.

Kinglet simulates how the scheduler part of a Kubernetes orchestrator distributes workloads over a cluster, in a provable way.

# Installation

Kinglet is a python3 script. For most of us, the only module one might have to install is the z3 module... Very simple!
The scrip comes in two flavours:

- The stable version, **kinglet_I.py** is unoptimized in terms of performance. The number of logical formulaes increases exponantially with the number of containers.
- The next verion, **kinglet_II.py** is currently in alpha. It uses a logical adder to drastically reduce the number of logical formulaes (see below).

# Options

## Disabling interactions

By default, the INTERACTIVE variable is set to True, meaning that the Good King will display a splash screen and ask you some questions. Since the first question is whether you want to run one of the tutorial described below, I strongly advise you to let it as it is.

## Controling verbosity

If you want to see how Kinglet constructs a SMT model on-the-fly and see the solutions (if there are any!), set VERBOSE to True.

## Playing with the number of nodes and/or containers

Set NODENUM to the number of nodes in a cluster, and CONTAINERNUM to the number of containers to schedule.

# Default constraints

## Affinities

Only two independent affinities are set by default: *aged* and *old*. Feel free to add your own!

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
When you run kinglet I or kinglet II, enter numbers 1 to 4 to select one of the samples.

## Customization

To skip samples, enter 0. You will be asked for a series of questions to customize a test run:
- how many nodes
- what is the size of the nodes
- how many containers

# Behind the scene

Kinglet is dynamic solver: the Z3 STM model is built on-the-fly depending to the number of containers and nodes on the cluster. Thank you Python's eval() function!

Affinity and size constraints are intricated, since placing a container on a node given an affinity constraint depends on the node "free space" capacity. 
In the code, intrication is materialized by propositional logic statements of the form:

```
Implies(And(affinity constraints), lower bound on Bitvector node capacity)
```

## Classes

For both versions of kinglet, nodes and containers are specified in the common file **kingletcommon.py**

### The node class

- nodes have a hardcoded maximum capacity: *self.max_size*. By default, it is set to DEFAULTMAXSIZE.
- the current capacity is expressed as an **unbounded** BitVector *self.size* which has a lower bound (UGE) set to 0 and and upper bound (ULT) set to self.max_size
- nodes are also equipped with an **unbounded** AffinitySort: *self.affinities[0]*
- only the first item in the self.affinities list is used. 

### The container class

- containers are equiped with an **unbounded** NodeSort *self.container* that is used to express to which node the node is scheduled. A constraint is placed on this variable to force it to be equal to an existing node expressed as a NodeSort
- they are also fitted with a list of **bounded** AffinitySort variables: on for each possible affinity or anti-affinity: *self.affinities*
- they are fitted with a list of as many **unbounded** BoolSort variables *self.location* as there are nodes. *self.location[i]* is set to **True** if *self.container* is set to node number i, and to **False** otherwise.

## Equality for affinity constraints

Each time a container is created, all the affinities and ant-affinities attached to this container are equated. So all affinities and anti-affinities of this container belong to the same **equivalence class**.

When Z3 attempts to attach a container to a node, the affinity of this node is also added to the equivalence class of the container:
- if this is not possible, Z3 tries to find another "compatible" node
- if it can't then the scheduling is unsatisfiable

## Bitvector for size constraints

### Stable version

In **kinglet_I.py**, each container c has a list of n *container[c].location[n]* BoolSort. So for each node it is easy to set a lowerbound on its capacity: for a given node n, we write as many Implies statements as there as possible combinations of container locations are set to n.

For example, considering node 1 and 7 containers (ranging from 0 to 6):

We start from the situation where no container locations are set to node 1, in which case the lower bound on the node capacity is zero:
```
Implies(And(Not(containers[0].locations[1]),Not(containers[1].locations[1]),Not(containers[2].locations[1]),Not(containers[3].locations[1]),Not(containers[4].locations[1]),Not(containers[5].locations[1]),Not(containers[6].locations[1])),UGE(nodes[1].size,0)))
```

We review all combinations until all container locations are set to node 1, in which case the lower bound on the node capacity is 7:

```
Implies(And(containers[0].locations[1],containers[1].locations[1],containers[2].locations[1],containers[3].locations[1],containers[4].locations[1],containers[5].locations[1],containers[6].locations[1]),UGE(nodes[1].size,7)))
```


### Alpha version

**kinglet_II.py** improves on the above design by placing a constraint on the bitwise sum of containers locations rather than enumerating all possible combinations.

As a result, the number of *Implies()* statements falls from exponential to linear.

The sum is performed with a standard logical adder as described below.

#### Logical adder

![source www.101computing.net](https://www.101computing.net/wp/wp-content/uploads/Binary-addition-using-binary-adder-circuits.png)
