---
id: KN-OPEN-006
type: open_problem
title: Can designed (arithmetic-progression) relation supports give a low-displacement-rank matrix whose structured solve beats generic sparse linear algebra, net of the relation-probability penalty?
tags: [displacement-rank, structured-linear-algebra, wiedemann, arithmetic-progression, relation-matrix, prime-field, index-calculus, open]
confidence: reported
status: open
source_refs: [KN-LIT-016, KN-LIT-017, KN-TECH-008]
added: 2026-07-21
superseded_by: null
---

## Statement
If relation harvesting is constrained to supports forming short arithmetic
progressions {x, x+d, ..., x+(m-1)d}, is the resulting relation matrix of O(1)
displacement rank (Toeplitz/Hankel-like), so a superfast structured solve
(O~(alpha*n)) beats generic sparse Wiedemann on the linear-algebra stage -- AND
does the advantage survive the relation-probability penalty that the extra
AP constraint imposes on harvesting?

## Current state (as reported)
Sparse solvers (Wiedemann / block Wiedemann, KN-LIT-016, KN-LIT-017) and
displacement-rank theory (KN-TECH-008) are both standard, but designing relation
*supports* to force operator structure in EC index calculus is not established
prior art. The program's structured-matrix candidate (RQ-STR-001, H-STR-001)
frames the two competing effects: the displacement rank alpha must stay O(1)
(not grow like sqrt(B)), and the AP hit-probability drop must not inflate the
factor-base size B until the LA saving is swamped. Negation/twist symmetry can
break the translation invariance the structure relies on. Whether a net win
exists over prime fields is open.

## Why it matters here
The linear-algebra stage is half of index calculus, and the corpus previously
documented no way to accelerate it. This is a concrete, measurable question
(numerically estimate alpha; measure AP hit rate vs random-support baseline;
time structured solve vs Wiedemann on matched matrices) whose answer is a bounded
finding either way. It is the LA-stage counterpart to the relation-generation
questions KN-OPEN-002 and KN-OPEN-004, and must be judged under the same
fully-charged cost model (the LA saving counts only if the harvesting penalty
does not cancel it).
