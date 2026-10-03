---
id: KN-OPEN-c2e86a
type: open_problem
title: >-
  Frobenius beyond orbit bookkeeping on binary Koblitz curves: is there a
  coordinate-reading canonicaliser for orbits of a multiplier group H strictly
  larger than <+-lambda_pi> whose per-call cost beats the gain it buys?
tags: [koblitz, frobenius, canonicaliser, orbit-quotient, rho, index-calculus,
  binary-curves, cost-law, open, ecdlp]
confidence: unverified
status: open
source_refs: [IDEA-20260901-863e36, KN-TECH-ee6696, KN-OPEN-5e3dd0, KN-OPEN-095df5,
  KN-FIND-b9a41d, KN-FIND-47da4e, H-SEMBIN-c7e1d4, DEC-20261001-5c9e7a,
  DEC-20261003-4e91b7, TASK-20261001-9b3e70, TASK-20261002-9e27f4,
  TASK-20260929-c05f6e]
added: 2026-10-03
superseded_by: null
---

## Provenance

Filed by `DEC-20261003-4e91b7` (R5). The text is the corrected wording of
candidate OPEN-D (`coordination/tasks/TASK-20261001-9b3e70/DERIVATION.md`
section 5), from validator report `VAL-20261003-17b1e4`
(`coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261002-9e27f4/validation_report.yaml`,
joint JR-4, defects D-1, D-2). As worded, OPEN-D was **trivially settled with
zero gain**: it omitted the cost law, and orbit enumeration answers its literal
question "yes".

`confidence: unverified`: the triviality construction is toy scratch from one
validator session, and the generic lower bound on canonicalisation is carried by
a ledger **proposal** (`IDEA-20260901-863e36`, C4), not by a finding.

## Statement

Binary Koblitz curve, `n` prime, `<P>` of prime order `l`, and a multiplier
group `H <= (Z/l)^*` with `<+-lambda_pi> < H` of index
`k = |H| / (2n) >= 2`. Is there a canonicaliser for H-orbits that **reads
coordinates** (non-generic), with per-call cost

- `c_can(H) = o(sqrt(k)) * (c_step + c_can(<+-pi>))` in group-operation
  equivalents, for rho on H-orbits, or
- `c_can(H) = o(k)`, for index calculus on an H-saturated factor base,

for an x-coordinate-defined `F` with `HF = F`?

## Known

- **Orbit enumeration achieves no gain.** Take `H` of order `2nk` containing
  `<+-lambda>`, which exists whenever `2nk | l - 1` for some small `k >= 2`.
  The min-x representative over the H-orbit costs `k` scalar multiplications
  and `nk` Frobenius maps. It is H-invariant, and the H-saturation of `F_V` is
  x-defined and H-stable. So the literal question has answer "yes", and the
  rho gain `sqrt(k)` is consumed by the `k` scalar multiplications per step.
  Toy scratch: all 8 toy curves tried (`n` in {7, 11, 13, 17, 19, 23}) have a
  suitable `H` (`k` = 2, 5, 3, 7, 3, 2, 3, 2), and the canonicaliser is
  H-invariant on 25 of 25 random `(Q, h)` each (`VAL-20261003-17b1e4` S4).
- **Generic canonicalisers cost `Omega(sqrt(k))`** (`IDEA-20260901-863e36` C4,
  prime-field setting, a proposal's argument via Shoup; internal, not a
  finding). This entry is the binary-Koblitz transfer of that idea's open cell
  C6, where the morphism-induced part is already `<+-pi>`, of size `2n`.
- `KN-TECH-ee6696` row F6 names `c_can` as the binding cost of Gamma-orbit
  canonical forms.

## Resolution criterion

An exhibited canonicaliser meeting either cost condition (with its `H`, `k` and
measured `c_can`), or a proof that every coordinate-reading canonicaliser for
such `H` costs `Omega(sqrt(k))` (respectively `Omega(k)`) per call.
"A proof that any such canonicaliser computes DL-information" (the candidate's
original second branch) is **not** well-defined: the min-x representative is
computed without any DL information.

**Measurable quantity.** `c_can` against `k` on toy Koblitz curves, with a
matched null; the stabiliser of `F` per H-STAB of
`coordination/tasks/TASK-20260929-c05f6e/DESIGN.md` section 3.6.

## Exponent stake

Conditional. The gain is `sqrt(k)` for rho (`k` for index calculus) under the
cost law above. It moves the exponent only if admissible `H` with
`k = l^theta`, `theta > 0`, carry a canonicaliser meeting the cost condition.
No candidate is named. (Coordinator reading, `DEC-20261003-4e91b7` R5; the
validator's text does not state the stake.)

## What must NOT be said in the meantime

- **Not** "larger Frobenius-stable quotients are available": they are available
  only at a cost that consumes the gain, as far as anything here shows.
- **Not** that `KN-OPEN-5e3dd0` is this question: that entry is about membership
  presentations of Frobenius-stable orbit unions (`H = <pi>`), an adjacent object.
- Nothing here is a statement about the security of any curve.

## Related open surface

- `KN-OPEN-095df5` (Galois-invariant factor bases via Couveignes-Lercier at
  `n = 131`) and `KN-FIND-b9a41d`, `KN-FIND-47da4e` (sigma-stable `V`
  classification; orbit-union parameterisation is cost-neutral) are adjacent.
- `DEC-20261001-5c9e7a` R8 caps the `<+-pi>` orbit route at `2 log2(2n)` bits; this
  entry asks about what lies strictly beyond it.
