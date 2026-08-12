---
id: KN-TECH-021
type: technique
title: Lattice hard problems (SVP/CVP/SIS/LWE) and worst-case-to-average-case reductions
tags: [svp, cvp, sis, lwe, worst-case-average-case, smoothing-parameter, np-hardness, post-quantum, adjacent]
confidence: established
complexity: SVP NP-hard to approximate within a constant (randomized reductions); best solvers 2^{Theta(n)}; SIS/LWE hard on average assuming worst-case approx-SVP/SIVP hard
applicability: the hardness foundations of lattice-based cryptography (a post-quantum domain, adjacent to ECDLP)
source_refs: [KN-LIT-049, KN-LIT-050, KN-LIT-051]
added: 2026-07-23
superseded_by: null
---

## Method / landscape
The core worst-case lattice problems are the Shortest Vector Problem (SVP) and
Closest Vector Problem (CVP), with approximation variants (GapSVP, SIVP). SVP is
NP-hard to approximate within some constant under randomized reductions
(Micciancio, SIAM J. Comput. 30(6):2008-2035, 2001); the best algorithms take
2^{Theta(n)} time (KN-TECH-020). The two average-case problems used in crypto:
- **SIS** (KN-LIT-049): find a short integer kernel vector of a random matrix mod
  q -- hard on average assuming worst-case approx-SVP/SIVP is hard.
- **LWE** (KN-LIT-050): solve noisy random linear equations mod q -- hard on
  average via a quantum reduction from worst-case lattice problems.
The reductions run through Gaussian measures and the *smoothing parameter*
(Micciancio-Regev), the standard technical tool.

## Relevance to this program
The hardness basis of lattice cryptography, ADJACENT to (not part of) the ECDLP
mission. Recorded so the corpus states clearly WHY lattice schemes are the
post-quantum replacements for ECDLP-based crypto: SIS/LWE reduce to worst-case
lattice problems believed quantum-hard, whereas ECDLP is broken by Shor. No known
reduction connects lattice problems and ECDLP in either direction.

## Applicability limits
The worst-case/average-case reductions are asymptotic and lose polynomial factors,
so they justify the FORM of the assumption but not concrete parameters -- those
come from cryptanalysis and the estimator (KN-TECH-023). The LWE reduction is
quantum (classical reductions cover only some parameter regimes). NP-hardness is
for near-exact SVP; the approximation factors used in crypto are far larger, where
NP-hardness is not known. None of this bears directly on ECDLP hardness.
