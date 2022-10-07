![alt text](https://github.com/labyrinthinesecurity/kinglet/blob/main/banner.png?raw=true)

# Introduction

Let tiny king Godefroy I guide you through the intricacies of automated reasoning... Under his enlightened command, you will learn how the Z3 SMT solver leverages Bitvectors to enforce memory constraints and Equality to meet affinity and anti-affinity demands from the clergy and the noblemen.

Godefroy simulates how the scheduler part of any decent orchestrator distributes workloads over a cluster of VM nodes.

# Installation

Kinglet is a python3 script. The only module you might have to install is the z3 module... Very simple!

# Disabling interactions

By default, the INTERACTIVE variable is set to True, meaning that the good king will display a splash screen and ask you some questions. Since the first question is whether you want to run one of the tutorial described below, I strongly advise you to let it as it is.

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

## Nodes size

Each node can accomodate up to 10 containers. The maximum capacity a node can hold is called the **node size**.

# Tutorials

When you run kinglet.py, enter numbers 1 to 4 to select one of the tutorials.

## Tutorial 1

In this first tutorial, the cluster is configured with 4 nodes and 5 containers.

## Tutorial 2

## Tutorial 3

## Tutorial 4

# Customization
