---
id: KN-FIND-26d76e
type: internal_finding
title: >-
  The j=m-1 (all-off-curve) branch of the Semaev summation fibre admits
  the same D_trial(E)=m-1 group-addition cost identity as the j=0
  branch, via quadratic-twist arithmetic -- completing a one-sided cost
  picture into a unified, two-branch law
tags:
  - semaev-polynomial
  - quadratic-twist
  - index-calculus
  - elliptic-curve
  - prime-field
  - toy-scale
  - derivation
  - cost-identity
  - positive-result
confidence: established
confidence_note: >-
  Established via two entirely independent methods, converging on the
  same conclusion: (1) the Validator's from-scratch symbolic re-derivation
  of the underlying discriminant identity plus concrete verification at
  5 tuples across 3 curves (including one never used in the actual run)
  and an exhaustive (not sampled) proves-too-much proof that the
  construction cannot even execute at j=0; (2) the Red Team's exact
  algebraic proof, spanning the FULL 100-trial mutant batch across both
  replication runs, that the wrong-rescaling-constant control isolates
  only the rescaling step. Both reviewers additionally traced two minor
  raw-data anomalies to their exact, benign mechanisms rather than
  leaving them unexplained. Neither read the other's approach before
  reporting (blind, parallel review round TASK-20260905-bc7d3f).
internal_refs:
  - H-MONO-10ca08
  - H-MONO-40aca5
  - H-MONO-45183a
  - IDEA-20260830-d84f6a
  - EXP-MONO-7c653b
  - EV-MONO-f8e108
  - DEC-20260905-eba1cb
  - RQ-MONO-001
proof_status: derivation
proof_refs:
  - experiments/EXP-MONO-7c653b/runs/RUN-MONO-7c653b-1/raw-result.json
  - experiments/EXP-MONO-7c653b/runs/RUN-MONO-7c653b-2/raw-result.json
  - ledger/handoffs/TASK-20260905-bc7d3f.yaml
  - experiments/EXP-MONO-7c653b/reviews/red-team/red-team-report.yaml
  - ledger/evidence/EV-MONO-f8e108.yaml
added: '2026-09-05'
superseded_by: null
---

## The identity

For the m-th Semaev summation polynomial `S_m(x_1,...,x_{m-1},T)` over
`E: y^2=f(x)=x^3+Ax+B` over `F_p`, `H-MONO-45183a`'s own Part A theorem
establishes the fibre splits completely over `F_p` iff `j=0` (every
coordinate on-curve) or `j=m-1` (every coordinate off-curve, `f(x_i)` a
quadratic non-residue), where `j` counts non-residue coordinates.
`H-MONO-40aca5` already established the `j=0` branch's cost: `D_trial(E)
= m-1` group additions on `E(F_p)` plus an O(1) lookup. Until this
record, no cost identity existed for the `j=m-1` branch -- its own
prior Red Team review found root-finding was genuinely needed there,
leaving the picture one-sided.

**The construction.** Fix a non-residue `delta mod p`. For each off-curve
coordinate `x_i`, `f(x_i)/delta` is a residue (non-residue/non-residue =
residue), so `y_i' in F_p` exists with `(y_i')^2 = f(x_i)/delta`. The map
`(x,y') -> (delta*x, delta^2*y')` carries the auxiliary curve
`E': (y')^2 = f(x)/delta` isomorphically onto the standard quadratic
twist `E_delta: Y^2 = X^3 + A*delta^2*X + B*delta^3` -- confirmed as a
formal polynomial identity (`delta^3*f(X/delta) = X^3+A*delta^2*X+B*delta^3`),
not a coincidence of any specific curve. Since isomorphisms of
Weierstrass curves over a field extension commute with the group law,
the signed sum `Q = sum eps_i*P_i` can be computed as
`R = sum eps_i*(delta*x_i, delta^2*y_i')` using `E_delta`'s ORDINARY
`F_p`-rational addition law -- `m-1` group additions, zero `F_{p^2}`
arithmetic -- and `x(Q) = X(R) * delta^{-1} mod p`.

**Measured and confirmed**, at `m in {4,5}`, `p in {211,1009}`, two
replication seeds: exact set equality between the twist route and the
direct polynomial-root route in 100% of 1400 tuples per run, zero
mismatches. The deliberately wrong-rescaling-constant proves-too-much
control failed to reproduce the direct root in 0/50 trials in both
runs, confirming the exact-match test's own discriminating power.

## Doubly independent confirmation

- **Validator** (mathematics-first): re-derived the discriminant identity
  symbolically from scratch, confirmed it at 5 concrete tuples across 3
  curves -- including a curve never used anywhere in the actual run --
  using independently-written code that never called the implementation.
  Then proved, exhaustively (checking all 111 on-curve x-coordinates at
  `p=211`, not sampling), that the twist construction cannot even be
  EXECUTED at `j=0`: `f(x)/delta` is forced to be a non-residue for
  every on-curve `x`, by the multiplicativity of the quadratic
  character, so no `F_p`-rational `y_i'` exists there. The exact-match
  test's discriminating power is therefore structural, not incidental
  to sampling.
- **Red Team** (code-and-data-first): reconstructed one trial by hand
  from raw data with independently-written code, then proved
  ALGEBRAICALLY across the full 100-trial mutant batch (both runs, not
  a spot check) that every mutant trial's own x-set equals the direct
  route's x-set scaled by the fixed constant `delta*delta'^{-1} mod p` --
  possible only if the pre-rescaling point `R` is identical between the
  correct and mutant constructions in every trial, proving the mutant
  isolates only the rescaling step, never the sum itself.
- **Two raw-data anomalies, both explained, neither a defect.** A
  root-count discrepancy (1989 measured vs. 2000 expected at one cell)
  traced by the Validator to a benign degree-drop phenomenon (~2% of
  tuples have a vanishing leading coefficient, correctly producing a
  point at infinity on the twist route for exactly the missing sign
  class). A tuple-count discrepancy (499 vs. 500 in one diagnostic
  counter) traced by the Red Team to a benign birthday collision in the
  SHA-256-derived sampling stream, with both underlying trials still
  fully and separately executed. Both findings improve confidence
  precisely because they were run down to an exact mechanism rather
  than left as unexplained noise in a clean-looking result.

## What this does not settle

- **Not a cost reduction.** `D_trial(E)` stays `O(m)` on both branches;
  the relation-search attempt count is unchanged and remains strictly
  worse than Pollard rho at every finite `m`. This is a cost-IDENTITY
  completion, not a speedup.
- **Does not touch the intermediate-`j` genericity question**
  (`H-MONO-45183a`'s own Part B / `HEUR-PARITY-2`), which this record's
  own experiment does not sample at all.
- **Toy scale for the measurement** (`p` in `{211,1009}`, `m` in
  `{4,5}`), though the underlying isomorphism mechanism is standard,
  curve-generic elliptic-curve theory, independently re-confirmed at a
  third curve outside the tested set.

## Attribution

The construction was hand-derived by the Idea Generator
(`IDEA-20260830-d84f6a`) without a code-execution tool available at the
time, and explicitly flagged there as unverified by computation. The
Coordinator's own design pass (`H-MONO-10ca08`) narrowed the experiment
to exactly this untested claim after finding the idea's other object
(the parity law) already decided by `EXP-MONO-12ce1c`. The machine
verification, the exhaustive multi-curve confirmation, the
proves-too-much non-existence proof, and the full-batch algebraic proof
of mutant isolation were all produced by the Executor and the
independent Validator/Red Team review (`TASK-20260905-bc7d3f`).
