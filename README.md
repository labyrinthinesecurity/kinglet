![alt text](https://github.com/labyrinthinesecurity/kinglet/blob/main/banner.png?raw=true)

# Introduction

Let tiny king Godefroy The First guide you through the intricacies of automated reasoning... Under His Enlightened Command, learn how Z3, a state-of-the-art SMT (Satisfiability Modulo Theories) solver leverages propositional logic to enforce memory constraints and to meet affinity and anti-affinity constraints on a Kubernetes-like cluster.

Kinglet simulates how the scheduler part of a Kubernetes orchestrator distributes workloads over a cluster, in a provable way.

# Installation

Kinglet is a python3 script. For most of us, the only module one might have to install is the z3 module... Very simple!

# Options

## Disabling interactions

By default, the INTERACTIVE variable is set to True, meaning that the Good King will display a splash screen and ask you some questions. Since the first question is whether you want to run one of the tutorial described below, I strongly advise you to let it as it is.

## Controling verbosity

If you want to see how Kinglet constructs a SMT model on-the-fly and see the olutions found (if any!), set VERBOSE to True.

## Playing with the number of nodes and/or containers

Set NODENUM to the number of nodes in the cluster, and CONTAINERNUM to the number of containers to schedule.

# Default constraints

## Affinities

Only two independent affinities are set by default: *aged* and *old*.

Kinglet will do its best to run containers sharing the same affinity labels on the same nodes.

## Anti-affinities

4 pairs of anti-affinities are set by default:
- *up* versus *down*
- *black* versus *white*
- *big* versus *small*
- *close* versus *far*

Any label in one pair can be freely combined with any label in another pair. For example, a container may be attached labels *black* and *down*.

It is also possible to mix and match affinities and anti-affinities on a same container. For example, *up*, *close* and *old*.


# Tutorials

When you run kinglet.py, enter numbers 1 to 4 to select one of the tutorials.

## Tutorial 1

In this first tutorial, the cluster is configured with 4 nodes and 5 containers.

## Tutorial 2

## Tutorial 3

## Tutorial 4

# Behind the scene

As opposed to my previous automated reasoning models, this one is dynamic: it is built on the fly depending to the number of containers and nodes on the cluster. Thank you Python's eval() function!

Affinity and size constraints are intricated, since placing a container on a node given an affinity constraint depends on the node "free space" capacity. 
In the code, intrication is materialized by propositional logic statements of the form:

```
Implies(And(affinity constraints), lower bound on Bitvector node capacity)
```

An early version of kinglet needed an exponential number of such formulas.
With the introduction of an adder made of 2 log(n) bit registers (where n is the number of containers), kinglet now generates a linear number of Implies()

All what this means is that kinglet may now reason about much more nodes and containers!

![alt text](https://www.101computing.net/wp/wp-content/uploads/Binary-addition-using-binary-adder-circuits.png)
