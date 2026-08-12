---
id: KN-TECH-042
type: technique
title: Lattice enumeration, pruning, and the crossover with sieving
tags: [enumeration, extreme-pruning, pruning, svp, sieving, crossover, memory, superexponential, bkz, lattice, baseline]
confidence: reported
complexity: 2^Theta(n log n) time in polynomial space, with small constants and extreme pruning; overtaken by sieving at dimension 70 for exact SVP in the G6K/FPLLL comparison
applicability: exact SVP/CVP in low to moderate dimension, and as the inner loop of BKZ; the memory-feasible alternative whenever sieving's exponential space is unaffordable
source_refs: [KN-LIT-102, KN-LIT-101, KN-LIT-106, KN-LIT-107, KN-TECH-020, KN-TECH-043]
added: 2026-07-24
superseded_by: null
---

## Method
Enumeration searches the lattice tree of coefficient vectors within a radius
bound, using the Gram-Schmidt profile to prune subtrees that cannot contain a
short enough vector. It is superexponential, `2^Theta(n log n)`, but uses only
polynomial space. *Extreme pruning* (KN-LIT-102) discards so much of the tree
that any single run succeeds with tiny probability, then compensates with many
randomised restarts; the expected total work drops exponentially. KN-LIT-102
also supplies what its authors describe as the first sound analysis of pruning,
which had been used heuristically since the 1990s. Pruned enumeration was
immediately adopted as BKZ's inner loop (KN-LIT-101) and is why BKZ at large
block size became feasible.

## The crossover is the useful fact
Enumeration and sieving are the two SVP oracle families, and which one wins is
dimension-dependent, not settled by asymptotics:

- Enumeration: superexponential time, **polynomial space**, small constants.
- Sieving: single-exponential time `2^(0.292n)`, **exponential space**, large
  constants.

Asymptotically sieving wins outright. In practice enumeration led for roughly a
decade after sieving became implementable (KN-LIT-103 reports its own sieve as
slower than enumeration up to dimension 50). The measured crossing point:
**dimension 70**, where G6K overtakes FPLLL's enumeration for exact SVP
(KN-LIT-106). KN-LIT-107 argues from the other end that enumeration can be
ignored above dimension 250, since a superexponential cost must eventually lose
to `2^(0.265b)`.

## Applicability limits
The crossover is a property of two particular implementations on particular
hardware at a particular date, not a mathematical constant; it moves with
engineering effort and with the memory available. That last dependence is the
one to watch: sieving's win is purchased with exponential memory, so under a
cost model that charges memory the crossing point moves to higher dimension, and
in the extreme, enumeration's polynomial space is what keeps it relevant at all
(KN-TECH-044). Pruning also changes what "solving SVP" means -- extreme pruning
succeeds probabilistically per run, so a quoted enumeration cost must state the
target success probability.

## Verified vs reported
The extreme-pruning claims and the "first sound analysis" characterisation are
from KN-LIT-102's published abstract; the exponential speedup was not
reproduced. The dimension-70 crossover is KN-LIT-106's reported measurement, and
the dimension-250 argument is KN-LIT-107's reasoning; neither was independently
checked. The asymptotic time and space characterisations are textbook. No
enumeration or sieving has been run in this repository.
