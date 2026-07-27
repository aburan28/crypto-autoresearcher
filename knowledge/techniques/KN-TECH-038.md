---
id: KN-TECH-038
type: technique
title: The primal (uSVP) attack on LWE
tags: [primal-attack, usvp, embedding, kannan, lwe, bkz, block-size, gsa, success-condition, security-estimate, lattice]
confidence: reported
complexity: cost of BKZ at the smallest block size b satisfying the success condition; under core-SVP that is 2^(0.292b) classical, 2^(0.265b) quantum
applicability: LWE and LWE-derived instances (Ring-LWE, Module-LWE, NTRU) where the secret-error vector is unusually short relative to the lattice; the standard attack against deployed lattice KEM and signature parameters
source_refs: [KN-LIT-107, KN-LIT-108, KN-LIT-100, KN-LIT-101, KN-TECH-020, KN-TECH-021]
added: 2026-07-24
superseded_by: null
---

## Method
Turn the LWE instance into a unique-SVP instance and solve it with lattice
reduction. Given a matrix instance `(A, b = As + e)` with `A` an `m x n` matrix
mod `q`, build

```text
Lambda = { x in Z^(m+n+1) : (A | -I_m | -b) x = 0 mod q }
```

of dimension `d = m+n+1` and volume `q^m`. The vector `v = (s, e, 1)` lies in
`Lambda` and has norm about `sigma * sqrt(n+m)`, which for LWE parameters is far
shorter than the lattice's Gaussian-heuristic shortest vector -- a unique-SVP
instance. Run BKZ and ask how large the block size `b` must be for it to find
`v`. The number of samples `m` is a free parameter and is numerically optimised.
This is the construction and framing given in KN-LIT-107, read directly.

## The success condition is the contested part
Predicting the required `b` means predicting the shape of the reduced basis,
which is done with the Geometric Series Assumption (KN-LIT-100) -- a heuristic
whose author called it a simplification, and which KN-LIT-107 notes is
*optimistic from the attacker's point of view*. Two mutually inconsistent
success conditions were used in the literature for years: the older one
descending from Gama-Nguyen's 2008 prediction work, and the one in KN-LIT-107.
They gave materially different security numbers for published parameter sets.
KN-LIT-108 settled this experimentally in favour of the KN-LIT-107 condition,
while observing that reduction sometimes does somewhat better still.

Consequences for anyone quoting a primal-attack cost:
1. The cost is `f(b)` where `b` comes from a heuristic prediction, not a
   measurement. State which success condition was used.
2. `b` then has to be priced, and that is a separate convention choice
   (KN-TECH-040). Two "primal attack costs" can differ by tens of bits purely
   through these two choices with no algorithmic disagreement at all.
3. The whole prediction is validated only in the dimensions where experiments
   have been run, far below deployed parameters.

## Applicability limits
The construction needs the secret-error vector to be unusually short; it does
not apply to a lattice problem with no planted short vector. The embedding
dimension and sample count interact, so a cost quoted without the optimised `m`
is incomplete. On NTRU lattices the same reduction machinery applies but the
success behaviour changes qualitatively above the fatigue point, and the
prediction here is invalid there -- see KN-TECH-045. Hints or side information
change the lattice and the condition; see KN-TECH-047.

## Verified vs reported
The lattice construction, the norm of `v`, the GSA-based modelling and its
stated optimism, and the numerical optimisation over `m` are read directly from
KN-LIT-107's Section 6.3. The resolution of the competing success conditions is
reported from KN-LIT-108's abstract and has not been reproduced here. No
implementation of this attack exists in this repository and no internal
measurement supports any figure in this entry.
