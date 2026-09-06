---
id: KN-FIND-14706d
type: internal_finding
title: >-
  A Semaev-summation-polynomial branch-discriminant character filter can
  never reject a genuine factor-base-membership candidate, for any curve
  or arity -- its quadratic-character tests collapse identically to the
  candidate's own on-curve membership, which is guaranteed true by
  construction
tags:
  - semaev-polynomial
  - index-calculus
  - monodromy
  - quadratic-character
  - imprimitivity
  - relation-rate
  - ecdlp
  - elliptic-curve
  - prime-field
  - toy-scale
  - derivation
  - negative-result
  - instrument-scope
  - reusable-lemma
confidence: established
confidence_note: >-
  Established via two entirely independent methods, converging on the
  same conclusion: (1) the Validator's exhaustive per-cell computation,
  tracing the actual implementation and verifying by exact set equality
  at all 6 tested (p,m) cells that the filter's reject-set is exactly
  the complement of the on-curve x-coordinate set; (2) the Red Team's
  from-scratch symbolic derivation, generic in the curve parameters
  (A,B), proving the underlying discriminant identity directly. Neither
  reviewer read the other's approach before reporting (blind, parallel
  review round TASK-20260905-77a64b). A proves-too-much control on the
  experiment's own ground-truth root-finding path also held, ruling out
  a broken measurement instrument as an alternative explanation.
internal_refs:
  - H-MONO-6adf3c
  - H-MONO-39b1f0
  - IDEA-20260807-5126f4
  - EXP-MONO-7f39bf
  - EV-MONO-c32ca3
  - DEC-20260905-a0c497
  - RQ-MONO-001
proof_status: derivation
proof_refs:
  - experiments/EXP-MONO-7f39bf/runs/RUN-MONO-7f39bf-3/raw-result.json
  - experiments/EXP-MONO-7f39bf/runs/RUN-MONO-7f39bf-4/raw-result.json
  - ledger/handoffs/TASK-20260905-77a64b.yaml
  - ledger/evidence/EV-MONO-c32ca3.yaml
added: '2026-09-05'
superseded_by: null
---

## The identity

For the Semaev-summation-polynomial branch construction used to test
factor-base membership of a target `T` (fix `m-2` factor-base
coordinates `x_1,...,x_{m-2}` on-curve, leave the target `T` and one
summation coordinate `x_free` free): each branch's own value `tb`
(obtained via genuine elliptic-curve point addition/subtraction on the
fixed coordinates, e.g. `t_+ = x(P1+P2)`, `t_- = x(P1-P2)` at `m=4`, or
the four sign-combination roots at `m=5`) is *itself* an x-coordinate of
a real point on the curve. Consequently, for a curve `E: y^2=x^3+Ax+B`
over `F_p`:

```
discriminant(S3(x_free, T, tb), x_free) / (T^3 + A*T + B) = 16 * (tb^3 + A*tb + B)
```

**exactly**, for generic `A, B, tb` -- confirmed symbolically (not merely
at sampled points). Because `tb` is on-curve, `f(tb) = tb^3+A*tb+B` is
*always* a quadratic residue mod `p`. So the right-hand constant factor
never flips the discriminant's own quadratic character, and:

```
chi(disc_branch(T)) = chi(f(T))     identically, for every branch
```

**The consequence.** A membership filter built from these branches
computes `m-2` (at `m=4`) or, per the corrected general count below,
`2^(m-2)` (at `m=5` and beyond) Legendre-symbol tests -- but every one of
them is testing the *same* quantity: whether `T` itself is an on-curve
x-coordinate. Any genuine relation-search candidate target is by
definition a point of `E(F_p)`, so `chi(f(T)) = +1` always, and the
filter's REJECT verdict (which requires every branch to disagree,
i.e. `chi = -1` unanimously) is a **mathematical impossibility** for any
candidate that could ever legitimately arise. The filter accepts (PASS)
every genuine candidate unconditionally -- not usually, not with high
probability, but always, by this identity.

## Doubly independent confirmation

- **Validator** (empirical, per-cell): traced the actual
  `evaluate_candidate` code, found concrete `T` values at all 6 tested
  `(p,m)` cells that genuinely trigger REJECT (ruling out "REJECT is
  disabled by a bug"), then showed by exhaustive computation that the
  REJECT-triggering set equals *exactly* the off-curve complement of the
  on-curve x-coordinate set, at every cell.
- **Red Team** (symbolic, curve-generic): derived the discriminant
  identity above directly, independent of any specific tested prime,
  and verified its numerical consequence at `p=211` (`m=4`, `m=5`) and
  `p=1009` (`m=4`): REJECT fires on exactly the off-curve `T`'s and
  never on an on-curve one.
- **Proves-too-much control** (Red Team): the experiment's own
  independent ground-truth root-finding path was checked against a
  hand-constructed root-free `T` and a hand-constructed non-trivial-root
  `T`; both matched the implementation exactly, ruling out a broken
  measurement instrument as an alternative explanation for the observed
  pattern.

## A correction to the idea's own branch-count claim

`IDEA-20260807-5126f4`'s own mechanism text predicted `m-2` character
tests. The Red Team's independent, from-scratch derivation establishes
the correct general branch count is `2^(m-3)` (`2` at `m=4`, `4` at
`m=5`, `8` at `m=6`, ...) -- exponential in `m`, not linear. The two
formulas coincide only at `m=4` (both equal `2`); the idea's own claim
was extrapolated from that single coincidental data point and diverges
at every larger arity.

## What this does not settle

- **Does not close KN-OPEN-009.** This is a narrow, scoped refutation of
  one proposed algorithm (the branch-discriminant character filter) built
  one specific way; `H-MONO-45183a`'s own imprimitivity finding and the
  relation-rate half resolved via `IDEA-20260805-a9a95d` are untouched.
- **Toy scale for the measurement** (`p` in `{211,431,1009}`, `m` in
  `{4,5}`), but the discriminant identity itself is derived generically
  in the curve parameters and is not scale-limited for this exact
  construction. Extension to `m>=6` (where the corrected `2^(m-3)` count
  continues) is a well-grounded conjecture from the identical
  construction pattern, not independently verified here.
- **No ECDLP, relation-rate, cost, or exponent claim** in any direction.
  A cheaper membership predicate, had one existed, would only ever have
  moved the relation-collection constant (`FINDING-PF-IC-001` says the
  linear-algebra stage dominates).

## The reusable lemma

Read the other way, per `EV-MONO-c32ca3`'s own `resource_check`: **any**
proposed membership filter in this lane built from a Semaev-polynomial
branch decomposition, where the branch values are themselves obtained by
summing already-on-curve points, is structurally guaranteed to collapse
to a curve-membership tautology. This can be checked -- and any such idea
ruled out -- *before* implementation, by verifying whether the proposed
branch values are themselves on-curve x-coordinates. This is cheaper than
building and running the filter to rediscover the same vacuity
empirically, which is exactly what happened twice in this exact
sub-thread (`H-MONO-39b1f0`, then this record via `EXP-MONO-7f39bf`).
Future idea generation on `RQ-MONO-001`'s imprimitivity branch should
apply this check as a pre-compute audit.

## Attribution

The corrected experimental construction was designed by the Coordinator
following an earlier independent-review correction (`H-MONO-39b1f0`,
`TASK-20260905-153d93`) that caught a prior draft's own conflation of
this construction with an already-decided null control. The actual
discriminant identity, its curve-generic proof, the branch-count
correction, and the proves-too-much confirmation were all produced by
the independent Validator and Red Team review of `EXP-MONO-7f39bf`
(`TASK-20260905-77a64b`), working blind and in parallel -- not by the
Coordinator's own initial reading of the raw results, which noted the
`n_reject=0` pattern as a striking observation but did not, before
review, know whether it reflected a genuine mathematical fact, a
sampling artifact, or an implementation defect.
