---
id: KN-FIND-f38a89
type: internal_finding
title: "AM4-OBS-1 corrected and narrowed: its diagonal premise is refuted, its conclusion is subsumed by the projector-conjugacy argument OBS-GEN"
tags: [am4-obs-1, obs-gen, invariance, lattice-observables, gso-projector, ml-kem, instrument-design, correction, negative-result, toy-scale]
confidence: derivation
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-a44d08, BATCH-cbe023, TASK-20260808-2a9085, TASK-20260808-768137, TASK-20260808-6de788]
internal_refs: [EV-MLKEM-9b8f7f, DEC-20260808-05b684, EV-MLKEM-cd9878, DEC-20260806-607779]
proof_status: derivation
proof_refs:
  - knowledge/findings/KN-FIND-f38a89.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-35efa3/prereg.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-2a9085/report_am4.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-768137/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/red_team_report.md
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-768137/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/red_team_report.md
added: '2026-08-08'
superseded_by: null
---

## Why this entry exists, and what it is NOT

`EV-MLKEM-cd9878` recorded a named finding, **AM4-OBS-1**, and
`GOAL-MLKEM-005`'s standing next action owed it a knowledge promotion.
BATCH-cbe023 tested it and **refuted half of it**. This entry therefore
promotes a **corrected and narrowed** statement, and its first job is to stop
the refuted half from propagating.

**AM4-OBS-1 as stated is NOT promoted and must not be inherited.** Its original
statement was:

> Every observable proposed in GOAL-MLKEM-005 is a function of `diag(QQ^T)` in
> the standard basis, and no function of that diagonal can be AM-4-invariant.

The first clause (the **premise**) is false. The second clause (the
**conclusion**) is true but is a weaker special case of a cleaner argument that
does not mention the diagonal at all. Both corrections are below.

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on
any FIPS 203 parameter set, on any attack cost, or on any cost model. The
measured half was taken at `d <= 140`, `beta <= 95`, `q <= 3329`, `n = 8` bases.
Nothing here is a theorem that no admissible statistic exists, and nothing here
is a universal impossibility claim.

## 1. The premise is REFUTED for D

AM-4 (`DEC-20260806-14ac13`) requires an adjudicator of a claim about a lattice
to be invariant under ambient isometry `B -> BH`, row permutation, and
unimodular `B -> UB`. AM4-OBS-1 asserted that every observable this campaign had
proposed is a function of `diag(P)`, `P = QQ^T` the tail-`beta` GSO frame
projector in the standard coordinate basis.

BATCH-cbe023's pre-registered **diagonal-collision probe** builds a pair
`(P1, P2)` of rank-`beta` projectors with `diag(P2) = diag(P1)` **exactly**
(measured `max|diag(P1) - diag(P2)| = 0.0`, off-diagonal separation `0.433013`,
rank `40/40`, rebuilt independently by the Validator) while `P2 != P1` off the
diagonal. Any function of the diagonal alone must return `0` separation.

`X4 = D` (the `2^-10` tail-quantile ratio) **separates**:

| cell | separation, in units of the declared scale | D's own pooled-SE floor | margin |
|---|---|---|---|
| L3 `(d,k,beta) = (100,50,40)` | `0.15837` | `0.021137` | **7.5x** |
| L4 `(140,40,45)` | `0.03447` | `0.026745` | **1.29x** |

So **`D` is not a function of `diag(P)`**, and AM4-OBS-1's premise is refuted at
the tested cells.

### 1.1 And its apparent corroboration was arithmetic

The same probe returned `coll = 0` exactly for `E_I`, `V`, `m3`, `W`, `OD` and
`TRIV`. **These six zeros are not six independent corroborations.** `E_I`, `V`,
`m3` and `W` are explicit sums over `diag(P)`; `TRIV = tr(P^2) = tr(P) = beta`
identically; and `OD = beta - V - beta^2/d` by the projector identity
`P^2 = P` (verified to `4.26e-14` over 6765 frames by the producer and to
`2.84e-14` on the Validator's own 200 frames). For all six, `coll = 0` is
**forced by algebra** given `diag(P2) = diag(P1)`. The producer disclosed this
plainly and against its own interest.

### 1.2 The frozen refutation clause could not have fired

The Validator's finding F-4 is the sharper statement and is the durable one:
the frozen outcome map's premise clause triggered on `X1, X2, X3, X5` — **exactly
the four candidates for which the premise is true by algebra** — while the one
candidate on which the premise had testable content, `X4 = D`, was the one the
clause excluded. **No collision probe of that design could ever have refuted
AM4-OBS-1's premise.** The refutation exists only because the run reported `D`'s
separation in prose beside the outcome field.

Score: premise **refuted at 1 of 1 testable candidates, corroborated at 0 of 0.**

## 2. The conclusion survives, and is subsumed by OBS-GEN

The surviving half needs no diagonal premise and is strictly stronger.

**OBS-GEN.** Let `f` be any function of the tail-`beta` frame projector `P`
alone with `f(H^T P H) = f(P)` for every orthogonal `H in O(d)`. Every rank-`beta`
orthogonal projector in `R^d` is conjugate to every other by some orthogonal
`H`. Hence `f` is constant on that entire set:

```
f(P) = f(d, beta)     for every rank-beta orthogonal projector P in R^d
```

**Therefore no function of the tail-`beta` frame alone can be both
ambient-isometry invariant and informative about anything.** Any `f(P)`-class
observable must fail invariance or fail sensitivity; there is no third option.

`X7 = tr(P^2) = beta` is not an arbitrary control — it is the canonical
representative of the whole class that passes ambient isometry, which is exactly
why an invariance criterion alone cannot be an admissibility gate. Measured:
`TRIV` invariant to `1.30e-15` (Validator's own frames: `8.29e-16`) and
distinguishing `q = 3329` from `q = 1` by `3.55e-16` of scale — i.e. by nothing.

This is a **derivation**: elementary, self-contained, checkable by a reader step
by step, and verified numerically on its canonical representative. It is **not**
a machine-checked proof, and it decides an entire class of observables **before
any datum**, which is why any numerical "verification" of it cannot fail and must
never be cited as evidence for it.

## 3. What OBS-GEN does NOT entail, and what was measured separately

OBS-GEN speaks only about `O(d)`-invariance, i.e. the ambient-isometry transform
`T1`. It says nothing about the basis-change subgroup. BATCH-cbe023 measured
that separately: on the frozen grid at 8 bases and 8 replicates per transform,
the six diagonal-determined observables also move far beyond `tau_inv = 0.01`
under **row permutation** (`0.667`–`89.0` of scale) and **unimodular change of
basis** (`0.690`–`57.9`), so they are not even *basis* invariants — they are
functions of a presentation, not of a lattice.

**Replication status, stated exactly.** The `T1` refusals reproduce under an
implementation the Validator wrote himself with his own basis construction, QR
path, Haar stream and seed (`E_I 0.7339`, `V 0.9877`, `m3 1.0187`, `W 1.0714`,
`OD 6.1696`), 1–2 orders above the threshold and 13–14 orders above the measured
`T0` noise floor of `6.20e-11`. **The `T2`/`T3` residuals are SINGLE-SOURCE**:
they exist only in the producer's output and no reviewer re-measured them.

## 4. Scope and limits — read before citing

1. **The `D` refutation is one probe, one run, two cells, single-source.** The
   Validator rebuilt the probe *construction* and confirmed the six arithmetic
   zeros, but did not independently recompute `D`'s collision value. The L4
   margin is only `1.29x` its floor. Whether `D`'s dependence on `P` beyond
   `diag(P)` is general or a property of that collision pair is **untested**.
   Any citation must carry this.
2. **OBS-GEN is a derivation, not a theorem this program proved machine-checked,
   and it is not an impossibility result.** It says every `O(d)`-invariant
   function of the *tail-frame projector alone* is constant. It says nothing
   about observables that are functions of the lattice by other routes
   (`|det B|^{1/d}`, `lambda_1/|det B|^{1/d}`, HKZ profile ratios), and three
   such candidates were scored in BATCH-cbe023.
3. **Passing an invariance gate is not admissibility, and BATCH-cbe023 showed
   the converse too.** The frozen AM-4/AM-8 gate admitted a *parameter-determined
   null* — `X_null(B,beta) = (beta/d)*(1/d)*log|det B|`, standard deviation
   exactly `0.0` across the eight frozen bases — at its top outcome. So clearing
   an invariance-plus-sensitivity-plus-relevance gate does **not** certify that
   an observable carries lattice information. The missing ingredient is a
   **dispersion criterion**: an admissible observable must vary across bases at
   fixed `(d, k, beta, q)`. See `DEC-20260808-05b684` amendment AM-11.
4. **A `q`-sweep down to `q = 1` under the construction
   `B = [[I_k, A],[0, q I_{d-k}]]` with `A` uniform on `[0,q)` gives `A = 0` and
   `B = I_d`**, so every such sweep compares a `q`-ary lattice against `Z^d` —
   a change of *lattice*, not of `q`-ary structure at fixed lattice. Sensitivity
   demonstrated that way is not evidence that the criterion separates informative
   from uninformative observables.
5. **Gram-matrix pipelines cannot test ambient isometry at all.**
   `G(BH) = BHH^T B^T = BB^T` identically, so for any observable computed from
   the integer Gram matrix, `T1` is the exact identity on its input and a `0.0`
   residual is not a test that could have failed. Two of BATCH-cbe023's three
   "AM-4-admissible" candidates are in this position; their `T2`/`T3` residuals
   are genuine and their isometry clause is **untested**.

## 5. Forward guidance

The two repairs the frozen contract itself names remain **open**, and neither is
closed by anything here:

- **(i)** weaken AM-4 to the basis-change subgroup `{T2, T3}` only, retaining the
  standard coordinate frame, under which the spill question is well posed and
  this goal's existing observables become candidates again; or
- **(ii)** restate the target question in isometry-invariant terms (for example
  about the GSO profile of a canonical reduction). **This is a DIFFERENT question
  and must be labelled as one.**

The cheapest open check is whether any of the three non-`f(P)` candidates carries
block-attribution content at all: at the one mirrored pair anybody replicated,
`hkz`'s mirrored gap has mean `0.00103` against a between-basis sd of
`0.0239`–`0.0392` and a paired `t` of `-0.064` over 8 bases — indistinguishable
from zero — and the producer's own values *decay* with `d`, which is the wrong
direction for a real block effect.

## Superseding relationship

This entry **corrects and narrows** the named finding AM4-OBS-1 recorded in
`EV-MLKEM-cd9878`. That evidence record is immutable and is not edited; per
AGENTS.md rule 4 the correction is made by this superseding entry and by
`EV-MLKEM-9b8f7f.named_finding_disposition`. Any successor citing AM4-OBS-1 must
cite this entry instead.
