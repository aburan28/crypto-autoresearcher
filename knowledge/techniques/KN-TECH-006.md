---
id: KN-TECH-006
type: technique
title: Parallel collision search and distinguished points (the practical rho baseline)
tags: [pollard-rho, distinguished-points, parallel, collision-search, baseline, generic, ecdlp]
confidence: established
complexity: expected ~0.886*sqrt(n) group operations serial; ~sqrt(n)/m wall-clock on m processors; small per-processor memory
applicability: any ECDLP instance (uses only the group law); the standard form used in real record computations
source_refs: [KN-LIT-012, KN-LIT-008]
added: 2026-07-21
superseded_by: null
---

## Method
Run pseudo-random walks x_{i+1} = f(x_i), each iterate tracked as a_i*P + b_i*Q,
on many processors. A point is *distinguished* if its encoding meets an easy
predicate (e.g. d leading zero bits). Only distinguished points are stored
centrally; when two walks hit the same distinguished point, the collision yields
a_i*P + b_i*Q = a_j*P + b_j*Q, hence k = (a_i - a_j)/(b_j - b_i) mod n. Negation
and other cheap automorphisms give a further constant-factor speedup.

## Why it is THE baseline (not the 1978 serial method)
Real ECDLP records run this parallel form (van Oorschot-Wiener, KN-LIT-012), not
the serial 1978 walk (KN-LIT-008). The program's baseline convention --
"0.886*sqrt(n) group operations, van Oorschot-Wiener parallelization assumed,
fully charged (setup + failed attempts + verification + memory traffic)" -- is
exactly this technique. The distinguished-point granularity d sets the
memory/steps tradeoff. Walk quality (the constant 0.886) is tightened by Teske
2001: well-chosen r-adding walks reach the ideal random-walk constant, ~20%
faster than Pollard's original three-branch map.

## Applicability limits
The near-linear parallel speedup rests on the heuristic random-walk assumption
(measured to hold for good walks). The sqrt-order cost is the generic wall
(KN-TECH-005); this technique realizes it with optimal memory/parallelism, so a
claimed improvement must beat the *fully-charged parallel* cost -- including
memory traffic and distinguished-point overhead -- not an idealized serial count.
