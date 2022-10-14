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

# Customization
