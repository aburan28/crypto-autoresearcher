---
id: KN-FIND-19f5ea
type: internal_finding
title: >-
  For an m=4 symmetric-base census curve with full rational 2-torsion,
  the halvability counts (h_+, h_-) are jointly bounded by residue class
  mod 4 -- h_+>=1 AND h_->=1 is achievable only as (1,1), forced at p=3
  mod 4, making the D-term's h_+/h_- interaction permanently untestable
  on this stratum
tags:
- semaev-polynomial
- monodromy
- 2-torsion
- quadratic-twist
- elliptic-curve
- prime-field
- toy-scale
- derivation
- negative-result
- instrument-scope
confidence: established
confidence_note: >-
  Established for the achievable-set claim and its consequence: derived
  independently twice (Coordinator; Validator, blind, before reading the
  Coordinator's own claim) from the exact, already-validated
  `h_pair_from_characters` code, and confirmed by exhaustive enumeration
  at 18 distinct primes total (Validator: full scans at p=101, p=103;
  Red Team: 16 further primes up to p=2003) with zero counterexamples.
  The D_prod=D_sum-at-(1,1) algebraic identity is confirmed both by hand
  and via sympy. NOT a claim about any other stratum (Z<3) or about
  cryptographic scale.
internal_refs:
- H-MONO-dd666a
- H-MONO-1297d7
- EXP-MONO-98abb2
- EXP-MONO-8ec0e5
- EXP-MONO-d4840b
- DEC-20260905-021e6e
- RQ-MONO-001
proof_status: derivation
proof_refs:
- experiments/EXP-MONO-d4840b/reviews/validator/validation-report.yaml
- experiments/EXP-MONO-d4840b/reviews/red-team/red-team-report.yaml
- ledger/corrections/CORR-20260905-783157.yaml
- ledger/corrections/CORR-20260905-191da0.yaml
added: '2026-09-05'
superseded_by: null
---

## The identity

For a curve `E: y²=x³+Ax+B` over `F_p` (`p>3`) with full rational
2-torsion (`f` splits into 3 distinct roots `e1,e2,e3`, `Z=3`), define
`h_+`/`h_-` via the already-established, brute-force-validated
character classification (`h_pair_from_characters`): for each root `e_i`
with the other two `e_j,e_k`, let `a=χ(e_i-e_j)`, `b=χ(e_i-e_k)`;
increment `h_+` if `(a,b)=(+1,+1)`, increment `h_-` if `(a,b)=(-1,-1)`,
do nothing if mixed. Then, **exactly**:

```
p ≡ 1 (mod 4):  (h_+, h_-) ∈ {(0,1), (0,3), (1,0), (3,0)}
p ≡ 3 (mod 4):  (h_+, h_-) ∈ {(0,0), (1,1)}
```

**Proof.** Write `u=χ(e1-e2)`, `v=χ(e1-e3)`, `w=χ(e2-e3)`. Since
`χ(e_j-e_i)=χ(-1)·χ(e_i-e_j)`, the reverse-direction values needed by
each of the three loop indices are `χ(-1)` times the canonical ones.
Euler's criterion gives `χ(-1)=+1` iff `p≡1 (mod 4)`. Substituting into
`h_pair_from_characters`'s own three index computations and enumerating
all 8 sign patterns of `(u,v,w)` for each value of `χ(-1)` gives the two
sets above exhaustively — no sign pattern produces any other pair.
**Independently confirmed two ways**: a from-scratch hand/script
re-derivation (blind, before reading any prior claim), and an
exhaustive computational scan of every actual curve at `p=101` (1650
non-supersingular `Z=3` curves) and `p=103` (1717), plus 16 further
primes up to `p=2003` — zero pairs outside the derived sets, at any
prime tested.

## The consequence: an interaction term this program's own instrument cannot see

`IDEA-20260904-4f614a`'s own closed form predicts, on the distinct-split
stratum, `D = h_+ n_- + h_- n_+`, with a named rival `D_prod = h_+ h_-
(n_++n_-)` proposed specifically to test whether the `h_+`/`h_-`
contributions interact multiplicatively rather than adding
independently. **This test is unanswerable by any `Z=3` curve at any
prime**: the only point where both `h_+` and `h_-` are simultaneously
nonzero is `(h_+,h_-)=(1,1)` (reachable only at `p≡3 mod 4`), and

```
D_prod - D_sum = h_-(h_+-1)n_+ + h_+(h_--1)n_-
```

is the **identically zero polynomial in `n_+,n_-`** when evaluated at
`h_+=h_-=1` — both coefficients `(h_+-1)` and `(h_--1)` vanish. So
`D_prod` and `D_sum` (and, by the same mechanism, *any* rival formula
that agrees with `D_sum` specifically at `h_+=h_-=1`) are forced to
coincide at the only reachable joint-nonzero point, for every curve,
regardless of its own `n_+,n_-`. Three independent search algorithms
(an `O(p³)` scan, an `O(log p)`-splitting-test variant, and a
structurally `O(p²)` root-pair enumeration) each examined the full
declared range up to their own budget limits and correctly found zero
curves satisfying the (as it turns out, empty) target set `h_+>=1 AND
h_->=1 AND max(h_+,h_-)>=2` — not because the target was rare, but
because no such curve exists.

## What this does not settle

- **Does not affect the already-promoted univariate result**
  (`KN-FIND-edd62c`, the `h_-`-with-`h_+=0` slice): that promotion rests
  on curves with `h_+=0` specifically (`h_-=1` and `h_-=3` both tested
  and confirmed), untouched by this finding.
- **Does not falsify the additive form.** `D_sum` is not shown wrong —
  it is shown *untestable against this specific rival* on this stratum.
  The additive mechanism's own independent re-derivation
  (`EXP-MONO-ee06e2`'s own Red Team review) remains valid.
- **Does not rule out testing the interaction term on a different
  stratum.** The non-split (`Z<3`) strata are untouched by this
  argument (the classification code and the `h_+`/`h_-` definition used
  here are intrinsically `Z=3`-specific); whether an analogous
  three-way-or-different classification exists there, and whether it
  admits a genuinely joint-nonzero point, is an open question this
  entry does not attempt.
- **Toy scale only.** No claim about cryptographic-scale primes, no
  relation-rate, cost, or exponent claim of any kind.

## Attribution

The achievable-set claim and its search-futility consequence were first
suspected by the Coordinator, prompted by (but going beyond) an
incomplete observation in an Executor's own final report for
`EXP-MONO-d4840b`. **The full, rigorous confirmation — including the
blind independent re-derivation, the exhaustive multi-prime scans, and
the symbolic proof that `D_prod-D_sum` vanishes identically at
`(1,1)` — came from the independent Validator and Red Team review**
(`TASK-20260905-495a4c`), not from the Coordinator's own initial,
time-pressured derivation, which is recorded here as flagged-then-
confirmed rather than self-certified.
