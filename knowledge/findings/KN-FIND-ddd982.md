---
id: KN-FIND-ddd982
type: internal_finding
title: The f_V-free Semaev S_3 Jacobian ideal's elimination polynomial is exactly the curve's own Weierstrass cubic
tags: [semaev, jacobian-ideal, elimination-polynomial, 2-torsion, groebner, degenerate-invariant, isogeny-class]
confidence: proved
evidence_level: theorem_backed
source_refs: [EXP-ICINV-e0cd8f, RUN-ICINV-e0cd8f-m3class, EV-ICINV-8afb64, DEC-20260811-a3398a]
internal_refs: [EV-ICINV-8afb64, DEC-20260811-a3398a, H-ICINV-6c7920]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-ddd982.md]
added: '2026-08-11'
superseded_by: null
---

## Finding

For a short Weierstrass curve `y^2 = x^3 + a*x + b` over `F_p`, let `S_3(x1, x2, x3)`
be the third Semaev summation polynomial (as committed in `harness/semaev.py`,
degree (2,2,2)), and let `I_3 = <S_3, dS_3/dx1, dS_3/dx2, dS_3/dx3>` be the
Jacobian ideal of its own singular locus -- the object
`experiments/EXP-ICINV-e0cd8f` measures, **deliberately excluding** any
factor-base membership polynomial `f_V`.

**The monic generator of `I_3 intersect F_p[x3]` (the elimination ideal to
`x3` alone) is exactly `x3^3 + a*x3 + b` -- the curve's own defining
Weierstrass cubic, not merely a polynomial related to it or sharing a root
with it.** This is a symbolic identity over `Q(a,b)`, verified independently
three times by three different methods before being recorded here:

1. A from-scratch `sympy.groebner` computation of `I_3` in lex order
   `x1 > x2 > x3` over `QQ.frac_field(a,b)` (this Coordinator, during
   EXP-ICINV-e0cd8f's evidence review): the lex Groebner basis has exactly
   three elements, and the one purely in `x3` is `a*x3 + b + x3**3`,
   confirmed by polynomial division against `x3^3+a*x3+b` to have quotient 1
   and remainder 0.
2. An independent `sympy.groebner` derivation (Red Team, EXP-ICINV-e0cd8f
   review) reaching the identical result.
3. An independent empirical cross-check (Validator, EXP-ICINV-e0cd8f review):
   factoring `x^3+a*x3+b` over `F_4001` directly for 18 sample curves and
   confirming exact agreement with the run's own reported
   `elimination_factor_partition` on all 18.

**Consequence.** `elimination_factor_partition` -- the `F_p`-factorisation
type of this elimination polynomial, computed by `harness/exp_icinv_e0cd8f.py`
via two independent computer-algebra backends (Singular, Macaulay2) and two
monomial orders -- is, by exact identity and not by inference or
correlation, the classical **rational 2-torsion structure of `E(F_p)`**:
partition `(1,1,1)` means all three roots of the cubic are in `F_p` (full
2-torsion), `(1,2)` means exactly one root is in `F_p`, and `(3,)` means the
cubic is irreducible over `F_p` (no rational 2-torsion point beyond the
identity). This is the SAME quantity this campaign already computes as
`two_torsion_x_count` / informally "`r`" in `harness/exp_icinv.py`
(documented there as NOT an isogeny-class invariant), already measured on
this exact class (`p=4001, t=30`) in `BATCH-cb71b5` with the identical
66/72 split, and already the explicit subject of
`ledger/hypotheses/H-ICINV-6c7920.yaml`, which treats it as a sampling-bias
nuisance covariate rather than a discovery (adjudicated `reject_scoped` for
its own specific over-dispersion-mechanism claim in `DEC-20260810-cc6577`,
on grounds unrelated to and not contradicted by this finding).

**A direct corollary, needing no isogeny-class-specific argument:** on any
class with fixed EVEN group order (any fixed even trace `t`, since
`#E(F_p) = p+1-t`), the partition `(3,)` (zero rational 2-torsion points) is
IMPOSSIBLE for every class member, by Cauchy's/Lagrange's theorem applied to
the order of a hypothetical 2-torsion point. A random-curve control drawn
from mixed traces is not so constrained. Observing "the class never shows
`(3,)`, the control sometimes does" therefore requires no isogeny-class
geometry to explain -- it is forced by the class's fixed group-order parity
alone.

## Why this matters going forward

Any future experiment that removes `f_V` from a Semaev-derived ideal and
reports the elimination polynomial's factorisation type (at `m=3`; `m=4`'s
analogous elimination object has not been checked and may or may not reduce
this cleanly) is, per this identity, measuring 2-torsion structure, not new
Semaev-variety or Jacobian-ideal geometry. A future contract wanting a
genuinely new curve-dependent signal from this family of constructions
should either (a) explicitly exclude `elimination_factor_partition` from
its list of informative invariants, or (b) provide an explicit, checked
mechanism argument connecting rational-2-torsion structure to
Groebner-solving degree or regularity before treating a variation in this
specific family as informative for attack-cost purposes.

## What this finding does not establish

It says nothing about the OTHER invariant families EXP-ICINV-e0cd8f
measured (S_3 monomial support, singular-locus dimension/degree,
Castelnuovo-Mumford regularity, graded Betti table) -- those were found
constant across both the tested class and its control, a separate question
addressed in DEC-20260811-a3398a. It makes no claim about `m=4`. It makes
no attack-cost, exponent, or speedup claim of any kind; `claim_tier: toy`,
`sota_delta: 0` throughout its source experiment.
