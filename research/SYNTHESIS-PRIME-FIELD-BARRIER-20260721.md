# Synthesis: the generic prime-field ECDLP barrier and its precise obstruction (2026-07-21)

Author role: Coordinator synthesis. Scope: generic ordinary elliptic curves
E/F_p (End(E) = Z), toy scale. This consolidates why every executable
index-calculus-style attack on prime-field ECDLP tested to date returns a
barrier, and states precisely what a breakthrough must overcome. It is an
explanatory synthesis and a heuristic obstruction argument, NOT a hardness
proof and NOT a breakthrough (AGENTS rules 5-7).

## 1. The multi-angle evidence, all pointing one way

| angle | record | verdict |
|---|---|---|
| Best index-calculus exponent vs rho | EV-ICI-001 | `contradicts`: crossbred 0.91, MITM 0.58 — structure gives a **constant** win, not an **exponent** win (rho = 0.5) |
| Output-sensitive relation harvesting (chord incidence reporting) | EV-INC-001 | `contradicts`: candidate-proportional, not output-proportional; no complete-cost row below 0.49 |
| Chord-arrangement richness excess (collinear triples) | EV-INCB-001 | `weakens`: EC 3-rich-line counts **at or below random** in every cell (excess ratio 0.75-1.0); the all-sizes gate is not crossed |
| Factor-base structure yield (m=3) | H-FB-001 | `rejected_scoped`; (m=2) EV-SEMAEV-003 | `supported`: no structured base beats random by >1.5x |
| Decomposition-yield scaling | KN-FIND-001 | yield saturates the birthday bound `~k*B^m/#E`, `k` bounded and flat over ~100x in #E; m=2 is combinatorially capped at `~B^2/#E` |
| Working index calculus vs rho (this session) | harness/indexcalc.py | index calculus costs **10-27x more** group operations than rho at bits 12-18 |
| Degree of regularity (binary Weil-descent proxy) | EV-DREG-002/003, DEC-20260720-002 | `inconclusive, trending weakened`; no super-linear syzygy growth on-lattice; degree axis unmeasured past D=5 |
| Literature | KN-LIT-006 (Galbraith-Gaudry survey) | rho remains the best known prime-field attack |

## 2. The single unifying obstruction

Every index-calculus attack needs a **super-linear source of relations** among
an efficiently-describable factor base: from |F| = B factor-base elements it
must harvest > B independent relations at sub-B^2 (ideally output-sensitive)
cost, so that relation collection plus sparse linear algebra beats rho's
sqrt(#E).

A relation is a small-support vanishing group combination of factor-base
points (a collinear triple `P_i + P_j + P_k = O`, or an m-term decomposition).
Its existence is a statement of **additive structure in the group**. So an
exponent win requires the efficiently-describable factor base to carry
**more additive structure than a random subset of the group.**

The obstruction: on a generic curve `End(E) = Z`, the only efficiently
computable relation among points is the group law itself. An
efficiently-describable base — points with x-coordinate in an interval,
subgroup, AP, algebraic set — is described by a condition on the **x-coordinate
line**, and the map `x-coordinate -> discrete log` is structureless (it is the
very function ECDLP asks us to invert). Hence such a base is, in its additive
group statistics, indistinguishable from a random subset:

- EV-INCB-001 measures exactly this and finds no collinear-triple excess.
- KN-FIND-001 shows the decomposition surface is saturated at the birthday
  rate `B^m/#E` with an O(1) constant, and for m=2 caps at the sumset size
  `~B^2` — a hard combinatorial ceiling no base can exceed.

You cannot manufacture additive group structure from an x-coordinate
description without already knowing discrete logs.

## 3. Why the two "escape hatches" only give constants

- **Extra endomorphisms (CM curves, End(E) != Z).** j = 0 / 1728 curves admit
  an efficiently-computable automorphism (mult-by-zeta / mult-by-i). This DOES
  expose additive relations (P and its image), but only O(1) per point, giving
  the well-known automorphism/negation speedups (GLV, Duursma-Gaudry-Morain):
  a **constant factor** on rho, never an exponent, and only for non-generic
  (small-discriminant) curves. Consistent with EV-ICI-001's "constant win".
- **Extension-field descent (Gaudry/Diem/Semaev, KN-LIT-002/003).** Weil
  restriction over GF(q^n) yields a *determined* multivariate summation system
  and a subexponential attack — but there is **no Weil restriction over a prime
  field**. The determined low-degree system that makes descent work simply does
  not exist over F_p; the only determined system carries the degree-B
  factor-base indicator, whose solving cost is tied to B. This is the same
  obstruction viewed on the degree-of-regularity axis.

## 4. Precise restatement of the open problem (what a breakthrough must defeat)

> A medium-or-greater prime-field ECDLP breakthrough requires an
> **efficiently-computable map that exposes a super-linear number of additive
> relations among an efficiently-describable factor base on a generic curve
> (End = Z)** — equivalently, a determined low-degree relation system over F_p
> not paid for by a degree-Theta(B) factor-base constraint. No known technique
> provides this, and the measured additive statistics of natural factor bases
> match random (no exploitable excess).

This does not prove such a map cannot exist (that would be a hardness theorem).
It states the target sharply: the barrier is not any single algorithm's
weakness but the absence of efficiently-computable additive structure on
generic curves. Progress will come from a genuinely new structure-exposing
primitive, not from re-tuning decomposition/incidence/degree parameters, all of
which this program has now measured against their controls and found at the
generic ceiling.

## 5. Honest status against the standing research goal (GOAL-ECDLP-001)

No breakthrough. This synthesis is a negative-result consolidation plus a
sharpened obstruction statement. It is toy-scale and heuristic, cites the
evidence it rests on, and makes no crypto-scale or impossibility claim. The one
axis not yet validly measured — degree of regularity past D=5 on a repaired
instrument — remains the campaign's live frontier (DEC-20260720-002) and is
Sage/m4ri-blocked in the current environment.
