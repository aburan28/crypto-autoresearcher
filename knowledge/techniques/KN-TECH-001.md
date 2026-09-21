---
id: KN-TECH-001
type: technique
title: Pollard rho for ECDLP (generic square-root baseline)
tags: [pollard-rho, baseline, generic, ecdlp]
confidence: established
complexity: expected ~sqrt(pi*n/2) group operations, O(1) storage, for group order n
applicability: any ECDLP instance (uses only the group law); parallelizable with linear speedup
source_refs: [KN-LIT-008]
added: 2026-07-19
superseded_by: null
---

## Method
Pseudo-random walk x_{i+1} = f(x_i) on the group, with each iterate tracked as
a_i*P + b_i*Q. A cycle (found via Floyd/Brent or distinguished points) yields
a_i*P + b_i*Q = a_j*P + b_j*Q, giving k = (a_i - a_j)/(b_j - b_i) mod n when
b_j != b_i.

## Why it is the baseline
Generic and optimal up to constants for a black-box group: no known algorithm
beats it over prime-field ECDLP (KN-OPEN-001). Every claimed improvement in
this program is measured against a matched rho reference under a common cost
model. Solutions are trivially verifiable (check k*P == Q), so rho emits a
verifiable certificate (see docs/claims-and-verification.md).

## Applicability limits
The sqrt-order cost is a wall for generic methods; structure-exploiting
attacks (index calculus) only beat it in specific extension-field regimes
(KN-LIT-002, KN-LIT-003), not over prime fields.
