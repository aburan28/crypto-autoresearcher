---
id: KN-TECH-035
type: technique
title: Full-cost accounting - charging memory, wiring, and communication
tags: [full-cost, cost-model, memory, communication, wiring, area-time, bsgs, pollard-rho, parallel-collision-search, index-calculus, baseline, asymptotics, ecdlp]
confidence: established
complexity: BSGS n^{1/2} processor steps but n^{2/3+o(1)} full cost; parallel collision search retains its asymptotic advantage under the same accounting
applicability: any comparison between a low-memory and a high-memory algorithm; mandatory whenever a proposed mechanism stores a factor base, relation set, or matrix
source_refs: [KN-LIT-094, KN-LIT-012, KN-TECH-006, KN-TECH-031, KN-TECH-008]
added: 2026-07-24
superseded_by: null
---

## Method
Price an attack by *full cost* -- the quantity of hardware multiplied by the
time it is occupied -- rather than by processor steps. Wiener (KN-LIT-094)
resolves the underlying question of how expensively many processors can be
wired to a large memory in three dimensions, and the answer changes exponents,
not just constants: Shanks's baby-step giant-step needs n^{1/2+o(1)} processor
steps but has full cost n^{2/3+o(1)}, because the sqrt(n)-element table cannot
be reached in unit time. Parallel collision search keeps its advantage under
the same accounting precisely because per-processor storage stays small.

## Why this program needs it
The program's baseline convention is "0.886*sqrt(n) group operations, van
Oorschot-Wiener parallelization assumed, fully charged." KN-LIT-094 is what
makes "fully charged" a defined term rather than a slogan, and it bites hardest
on exactly the mechanism family the program keeps proposing:

- **Index-calculus-style routes** buy a lower step count by storing a factor
  base and a relation matrix, then running sparse linear algebra
  (KN-TECH-008). Under step counting that storage is free; under full cost it
  is not, and the linear-algebra phase is memory-bound rather than
  compute-bound. A relation-collection speedup that is paid for in matrix size
  may be a wash or a loss.
- **Memory-heavy shortcuts** must clear a higher bar than sqrt(n). If
  unrestricted memory only buys BSGS's n^{2/3} full cost, then a mechanism
  claiming to beat sqrt(n) *while using sqrt(n) storage* has not necessarily
  beaten rho at all.
- **Preprocessing and advice** (KN-LIT-013) are the same issue in another
  guise: stored advice is hardware occupied over time, and the program's rule
  that preprocessing must be charged follows from this model.

Wiener also states the converse caution explicitly, and it should be preserved:
counting only processor steps is *conservative from the defender's side*, so
using step counts to choose key sizes is safe. It is unsafe only when used to
declare two algorithms equivalent.

## Applicability limits
The results are asymptotic, with o(1) exponents and unextracted constants, so
full cost cannot settle a claimed constant-factor advantage -- it settles
exponent-level comparisons and identifies which side of a trade-off is being
undercharged. The wiring model assumes three spatial dimensions and a
particular technology abstraction; real machines add communication latency,
bandwidth limits, and energy costs that this model does not itemize. For
concrete rather than asymptotic budgeting, the published record computations
(KN-TECH-036) are the better instrument.

## Verified vs reported
The full-cost results and the explicit statement that BSGS and rho differ in
full cost are read directly from KN-LIT-094 and are that paper's proven
results (confidence: established); the wiring derivation was not re-checked
and the o(1) constants were not extracted. The application to index-calculus
relation matrices and to this program's preprocessing rule is the program's
own reasoning and has not been carried out quantitatively for any specific
proposed mechanism -- doing so for one is an obvious next step.
