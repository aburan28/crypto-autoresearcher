---
id: KN-FIND-edd62c
type: internal_finding
title: >-
  The m=4 symmetric-base Semaev census's 1^4-excess is an exact, derived,
  independently-reverified sum over halvable 2-torsion fixed-point pairs --
  D = h_+ n_- + h_- n_+, linear in (#E[4], #E^d[4]) by structural necessity,
  confirmed exactly at two independent h_- values with a quadratic rival excluded
tags:
- semaev-polynomial
- monodromy
- degenerate-stratum
- elliptic-curve
- 2-torsion
- quadratic-twist
- index-calculus
- prime-field
- toy-scale
- derivation
confidence: established
confidence_note: >-
  established for the univariate h_- slice (h_+=0 throughout the tested data):
  the derivation is elementary, independently re-derived from the group law
  alone by a reviewer via two separate combinatorial methods, and confirmed
  exactly on two independent curves at different h_- values (1 and 3), with a
  plausible nonlinear alternative (h_-^2) decisively excluded at h_-=3. NOT
  yet established for the full bivariate form: every tested curve has h_+=0,
  so the h_+ term and any h_+/h_- interaction remain empirically untested --
  see "What this does not settle".
internal_refs:
- H-MONO-d4c511
- H-MONO-fa4cb9
- EXP-MONO-4e6faa
- EXP-MONO-ee06e2
- EV-MONO-91bca2
- EV-MONO-fae201
- DEC-20260904-46b71e
- DEC-20260904-e9df3f
- IDEA-20260904-4f614a
- RQ-MONO-001
proof_status: derivation
proof_refs:
- ledger/proposals/IDEA-20260904-4f614a.yaml
- experiments/EXP-MONO-4e6faa/reviews/validator/validation-report.yaml
- experiments/EXP-MONO-4e6faa/reviews/red-team/red-team-report.yaml
- experiments/EXP-MONO-ee06e2/reviews/validator/validation-report.yaml
- experiments/EXP-MONO-ee06e2/reviews/red-team/red-team-report.yaml
added: 2026-09-04
superseded_by: null
---

## The identity

For `E: y² = x³ + Ax + B` over `F_p` (`p > 3`) with full rational 2-torsion
(`f(X) = X³+AX+B` splits into 3 distinct roots, `Z=3`, `τ=4`), consider the
m=4 symmetric-base Semaev census restricted to the distinct-split stratum
(monic cubics `g(X)=X³-e1X²+e2X-e3` splitting into 3 distinct `F_p`-rational
roots, none a root of `f`). Let `χ` be the quadratic character, `n_+`/`n_-`
the counts of `x ∈ F_p \ Z(f)` with `χ(f(x)) = ±1`, and

```
h_+ = (#E(F_p)[4]  - τ) / 4         h_- = (#E^d(F_p)[4] - τ) / 4
```

where `E^d` is the quadratic twist. Then, **exactly, with no error term and
no free parameter**:

```
D      := h_+ n_-  +  h_- n_+
#1^4    = C(n_+,3) + C(n_-,3) + D
#2+1+1  = 3 n_+ n_-  -  3 D
#2+2    = C(n_+ + n_-, 3) - C(n_+,3) - C(n_-,3) - 3 n_+ n_- + 2 D
```

**Proof sketch (mechanism, independently re-derived).** Translation by a
rational 2-torsion point `T = (e_i, 0)` descends to the x-line as the
Möbius involution `μ_T(x) = e_i + f'(e_i)/(x - e_i)`, which preserves
`χ(f(·))` on `S := F_p \ Z(f)`. A base point's Semaev fibre degenerates
exactly where its root multiset meets a `μ_T`-orbit twice. An *ordinary*
collision moves mass `2+2 → 2+1+1` and leaves `1^4` alone; the exception is
when the colliding pair's third point is itself a **fixed point** of some
`μ_T'` (`T' ≠ T`) — i.e. an x-coordinate of a point of exact order 4. Each
halvable 2-torsion point `T'` contributes **exactly one** rational
fixed-point pair (independently re-derived: these pairs are provably
disjoint across distinct halvable `T'`, by direct computation from the
group law, not merely asserted), landing in the `χ=+1` half (`h_+` such
pairs, each contributing `n_-` to the `1^4` excess) or the `χ=-1` half
(`h_-` such pairs, each contributing `n_+`). Summing: `1^4` excess
`= h_+ n_- + h_- n_+ = D`. The `2+1+1` count follows from the same
partition by an independent two-cycle count (`A_+ = 3n_+/2 - 3h_+` ordinary
pairs in the `χ=+1` half, and symmetrically for `A_-`), reproducible by two
separate combinatorial methods (multiplicity counting; direct 4-orbit
combinatorics under the Klein four-group action) that were run
independently of the original derivation.

## Why this is linear, not merely fit

The mechanism is a **sum of independent, additive per-pair contributions**:
each halvable 2-torsion point contributes its own fixed-point pair,
disjoint from every other's, each contributing a fixed amount (`n_-` or
`n_+`) regardless of how many *other* halvable points the curve has. This
gives the mechanism **no combinatorial slot** for a non-linear term such as
`h_-²` or a `h_+·h_-` cross-interaction — such a term would require
distinct halvable points' fixed-point pairs to *interact*, which the
disjointness property rules out. This was checked, not assumed: a named
quadratic rival `D_quad = h_+ n_- + h_-² n_+` was pre-registered and tested
against real data.

**Empirical confirmation, twice, at genuinely discriminating values.** Both
`h_-=1` (the minimal positive value, `EXP-MONO-4e6faa`) and `h_-=3`
(`EXP-MONO-ee06e2`) give exact matches (zero residual on all three classes,
including the un-required `2+2` check) against the linear form. At `h_-=1`
alone, `D_lin` and `D_quad` coincide (`1=1²`) and cannot discriminate; at
`h_-=3` they diverge sharply (`D_lin=156` vs. `D_quad=468`), and the data
matches `D_lin` exactly while missing `D_quad` by `-312` / `+936` on the
two primary classes — a decisive exclusion, not a near-miss.

## What this does not settle

- **The full bivariate form is untested.** Both archived curves have
  `h_+=0`. The `h_+ n_-` term and any `h_+ / h_-` interaction have never
  been empirically exercised — only the `h_+=0` slice of the formula. A
  reviewer (`EXP-MONO-ee06e2`'s Red Team) already located a concrete
  candidate with `h_+=1, h_-=1` simultaneously: `p=103, A=1, B=11`
  (`Z=3`, ordinary, `n_+=58, n_-=42`) — the very next prime in the
  declared search range. This is the natural next test before the FULL
  bivariate closed form (as opposed to its univariate `h_-` slice, which
  this entry does promote) can be called `supported`.
- **Non-split strata (`Z<3`) are untested**, named by the parent idea as
  separate future work.
- **Toy scale only** (largest prime tested: 101). No claim about
  cryptographic-scale primes, no relation-rate, cost, exponent, or ECDLP
  hardness claim of any kind.
- **Does not re-scope `H-MONO-93bc4d`'s** own already-closed collision-rate
  closed form, which uses a related but distinct invariant
  (`F=(#E[4]-tau)/2`) in a different question (arithmetic-vs-CM collision
  rate, not the m=4 symmetric-base census); whether that formula is itself
  a proxy for the same fuller `(#E[4], #E^d[4])`-based law is named but
  explicitly deferred to a future ranking decision.
- **No `AGENTS.md` rule-12-equivalent three-model closure quorum** applies
  or was sought (that quorum is suspended program-wide; see
  `AGENTS.md` "Goal closure quorum"). Both reviews resolved to the same
  model as the producer under this harness's current runtime.

## Attribution

The closed form, the STEP 1-3 involution mechanism, and the initial
retrodiction to two probe-level witness curves came from
`IDEA-20260904-4f614a` (Coordinator, same session). **The independent
re-derivation of the STEP 4/5 fixed-point-disjointness and bookkeeping
argument — via two separate combinatorial methods, and the explicit
conclusion that this structurally forces linearity and leaves no slot for
a non-linear term — came from `EXP-MONO-ee06e2`'s own independent Red Team
review**, not from the original idea record, which stated but did not
itself re-verify this from first principles. The `h_+=1, h_-=1` curve
identified as the next concrete gap is also that same Red Team's own
discretionary finding, not requested by the review plan.
