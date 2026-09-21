---
id: KN-TECH-031
type: technique
title: Baby-step giant-step and the deterministic generic baseline
tags: [baby-step-giant-step, bsgs, shanks, meet-in-the-middle, deterministic, interval-search, kangaroo, memory, generic, baseline, ecdlp]
confidence: established
complexity: 2*sqrt(n) group operations and sqrt(n) storage (deterministic); full cost n^{2/3+o(1)} once memory is charged
applicability: any finite cyclic group with an equality test; the standard finisher when the logarithm is confined to a known interval of length L (cost ~2*sqrt(L))
source_refs: [KN-LIT-083, KN-LIT-094, KN-TECH-001, KN-TECH-005]
added: 2026-07-24
superseded_by: null
---

## Method
To find k with Q = kP in a group of order n, set m = ceil(sqrt(n)). Store the
baby steps {i*P : 0 <= i < m} in a lookup structure, then walk the giant steps
Q - j*m*P for j = 0, 1, ... until a stored value matches; k = i + j*m. The
method is deterministic, needs no random-walk heuristic, and simultaneously
yields group-order information. Restricted to a known interval [a, a+L) it
costs ~2*sqrt(L) operations, which is the form that matters most here.

## Role in this program
BSGS is not the baseline -- rho is (KN-TECH-006) -- but it bounds two things
rho does not:

- **The memory-rich corner.** Any proposed mechanism that assumes large
  storage is competing against BSGS, not against constant-memory rho. Wiener
  (KN-LIT-094) shows the two are not interchangeable: BSGS is sqrt(n)
  processor steps but n^{2/3+o(1)} *full cost*, and he states explicitly that
  it is wrong to conclude Shanks's method and rho have the same full cost.
  So a memory-heavy mechanism must beat rho's full cost, and its own storage
  must be charged at the same wiring-aware rate.
- **The interval finisher.** Several program routes aim to localize k to a
  short interval rather than to solve outright (KN-OPEN-010's transfer-operator
  spectrum, and any partial-information mechanism). The residual work is then
  ~2*sqrt(L), so a mechanism that spends C operations to shrink the search from
  n to L only wins if C + 2*sqrt(L) < 0.886*sqrt(n). Stating L without stating
  C is not a result.

## Applicability limits
Storage of sqrt(n) group elements is infeasible at cryptographic size: a
128-bit subgroup would need ~2^64 stored points, which is why no record
computation uses BSGS and why rho with distinguished points is the practical
method. For interval search with small L, the kangaroo/lambda method is the
constant-memory competitor and is usually preferred over BSGS in practice.
BSGS gains nothing from curve automorphisms in the way rho does
(KN-TECH-018), so on Koblitz-type curves the gap widens further in rho's
favour.

## Verified vs reported
The algorithm, its deterministic sqrt(n) bound, and the interval variant are
textbook (KN-LIT-083; confidence: established). The n^{2/3+o(1)} full cost and
the explicit rho-versus-Shanks statement are read directly from KN-LIT-094 and
are that paper's results, not reproductions. The break-even inequality in
"Role in this program" is this program's own accounting convention and has not
been validated against a run.
