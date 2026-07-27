---
id: KN-FIND-003
title: mu_3 supplies infinity-norm-1 MW relations on the frozen j=0 free-x family; polarisation Gram rank is not Shioda rank
type: internal_finding
status: established
tags: [lifting, xedni, function-field, mu3, mordell-weil, coefficient-bound, methodology, toy-scale]
evidence: [EV-XEDN-002]
decision: [DEC-20260724-009]
---

# KN-FIND-003

On the frozen EXP-XEDN family `y²=x³+b(t)` with `a=0` (hence `j=0`) at primes
`p≡1 mod 3`, free-x integral sections of shape `deg x≤2`, `deg y≤3` accepted by
the frozen `is_square_poly` predicate organize into `μ₃` orbits satisfying
`S+wS+w²S=O`. Those relations have infinity-norm 1 and specialise to O on smooth
fibres. Across `p∈{7,13,19,31}` the shortest observed relation among free-x
sections therefore has `max_|coeff|=1` with no growth vs `log p`.

Separately, the polarisation height Gram built from
`⟨P,Q⟩=ĥ(P+Q)-ĥ(P)-ĥ(Q)` with `ĥ=(1/2)max(deg num x, deg den x)` can report
ranks above the Shioda–Tate bound `r≤8` even when the height-control
`deg(num x(nS))=2n²` holds. Treat that Gram as diagnostic only; do not equate
its rank with geometric Mordell–Weil rank without local corrections.

Scope: toy isotrivial family only; not a closure of candidate B2 or of
non-isotrivial / number-field xedni.
