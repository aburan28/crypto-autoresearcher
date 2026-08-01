---
id: KN-FIND-004
title: Non-isotrivial free-x sections still admit infinity-norm-1 MW relations; Gram can over-report coefficients without μ₃
type: internal_finding
status: established
tags: [lifting, xedni, function-field, non-isotrivial, mordell-weil, coefficient-bound, methodology, toy-scale]
evidence: [EV-XEDN-003]
decision: [DEC-20260725-001]
---

# KN-FIND-004

On non-isotrivial Weierstrass surfaces `y²=x³+a(t)x+b(t)` over `F_p(t)` with
`a≠0`, `deg a≤2`, `deg b=6`, and non-constant `j`, free-x integral sections of
shape `deg x≤2`, `deg y≤3` accepted by the frozen `is_square_poly` predicate
still admit Mordell–Weil relations with infinity-norm 1 among the observed
slots at `p∈{7,13,19,31}` (EXP-XEDN-004 / EV-XEDN-003). μ₃ orbits do not lie
on these curves, so the bound is not the isotrivial automorphism saturation
seen in KN-FIND-003.

Separately, polarisation-Gram LLL can report large coefficients for true but
non-shortest kernel vectors (archived example: Gram inf-norm 15 vs group-law
inf-norm 1 on a `p=13` surface). Coefficient claims must rest on group-law
verified short search (or an equivalent lattice of specialised embeddings),
not on Gram LLL alone.

Scope: toy non-isotrivial degree window only; not a closure of candidate B2
or crypto-scale ECDLP.
