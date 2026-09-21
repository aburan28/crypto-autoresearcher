---
id: KN-TECH-010
type: technique
title: Finite-field incidence bounds (Szemeredi-Trotter type)
tags: [incidence-geometry, szemeredi-trotter, finite-field, point-line, rich-lines, sum-product, relation-harvesting, ecdlp]
confidence: reported
complexity: point-line incidences over F_p bounded ~ O(m^{2/3}n^{2/3} + m + n) (balanced range); expander form |I - mn/p| <= sqrt(p*m*n); characteristic-p range restrictions apply
applicability: counting collinear configurations (chords) among curve/factor-base points; COUNTING bounds, not algorithmic reporting primitives
source_refs: [KN-LIT-019]
added: 2026-07-21
superseded_by: null
---

## Method
For m points and n lines in F_p^2, incidence theorems bound the number of
point-on-line pairs:
- **Expander form** (Vinh 2011): |I - m*n/p| <= sqrt(p*m*n) -- incidences
  concentrate around the expected main term m*n/p.
- **Szemeredi-Trotter form** (Stevens-de Zeeuw 2017, via Rudnev's point-plane
  bound, KN-LIT-019): O(m^{2/3} n^{2/3} + m + n) in a balanced range, with a
  characteristic-p range restriction (roughly n = O(p^2)) inherited from the
  point-plane theorem.

## Role in the program
Elliptic-curve chords (lines through two curve points) are a structured line
family; each collinear triple with all points in the factor base is a relation.
These bounds control how many such rich-line relations can exist, and whether EC
chord arrangements sit at the generic Szemeredi-Trotter ceiling or show a
curve-specific excess -- the program's incidence candidates
(RQ-INC-001, RQ-INCB-001, EXP-INC-001, EXP-INCB-001).

## The critical distinction (counting vs reporting)
These are *counting/existence* bounds. They do NOT provide an algorithmic,
output-sensitive REPORTING primitive that lists the s-rich lines with subquadratic
setup -- and the program's own literature search found no such finite-field
reporting algorithm. So a harvesting proposal that assumes cheap listing is
assuming a primitive that is itself an open problem (KN-OPEN-005 neighborhood);
the bounds only tell you how much output there could be, not how cheaply to
enumerate it. Over F_p there is no order/continuity for the real-case partition-
tree reporters.

## Applicability limits
Bounds are strongest when point/line sets are large relative to p, and carry the
characteristic-p range restriction. A measured curve-specific excess of rich
lines must be separated from the generic ceiling and from small-field
coincidences (needs random-line-set negative controls).
