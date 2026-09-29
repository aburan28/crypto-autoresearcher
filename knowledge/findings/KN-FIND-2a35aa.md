---
id: KN-FIND-2a35aa
type: internal_finding
title: "Bit identity is not zero dispersion: a float-equality dispersion criterion refuses an arithmetic route, not an observable"
tags: [dispersion-criterion, admissibility-gate, g-var, am-11, floating-point, instrument-design, null-object, observable-invariance, ml-kem, negative-result, toy-scale, correction]
confidence: derivation_plus_single_source_measurement
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-9e3584, BATCH-cbe023, TASK-20260809-cda2f6, TASK-20260809-444fe7, TASK-20260809-3f1dc4]
internal_refs: [EV-MLKEM-9346bb, DEC-20260809-afe29b, EV-MLKEM-9b8f7f, DEC-20260808-05b684]
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/red_team_report.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-3f1dc4/validation_report.yaml
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-3f1dc4/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/red_team_report.md
added: '2026-08-11'
superseded_by: null
---

## What this says, and what it does NOT say

**It does not overturn `R-OUT-1`, and that is the first thing to read.** The
`BATCH-9e3584` finding that the `AM-4`/`AM-8` admissibility gate is INADMISSIBLE
stands: the notarized closed-form `X_null` *is* refused, `G-VAR` *did* fire, and
**no admissibility claim is reportable from that gate in either direction**. One
refused blind observable is sufficient for that verdict, and finding further
escapes cannot make a gate more admissible.

What this entry records is a **bound on the repair**:

> A dispersion criterion operationalized as **exact bit identity of
> floating-point values across the frozen bases** refuses an **arithmetic route**,
> not an observable. The same closed-form function of the parameters, evaluated
> through a different float path, is **admitted** — while agreeing with the refused
> evaluation to ~`1e-14` and reproducing the governing reference table to every
> printed digit.

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on
any FIPS 203 parameter set, on any attack cost, or on any cost model. Measured at
`q = 3329`, `d in {20, 30, 40, 100, 140}`, the frozen `(k, beta)` grid, 8 frozen
bases, no reduction beyond the frozen HKZ pipeline at `d <= 40`. There is no
cryptographic baseline, so `dominated_by` and `sota_delta` are `null` for that
reason.

## 1. The setup, stated so the point lands on it

`AM-11` of `DEC-20260808-05b684` requires every admissibility gate in
`GOAL-MLKEM-005` to include a dispersion criterion, quantified over **functions**:

> an admissible observable must have non-zero dispersion across the frozen bases
> at fixed `(d, k, beta, q)`. Equivalently, **any closed-form function of
> `(d, k, beta, q)`** with zero between-basis variance MUST be refused.

`BATCH-9e3584` implemented that as `G-VAR`: `tau_var` exactly `0`, decided by
**bit identity of the 8 IEEE-754 doubles** rather than by a tolerance. The choice
was deliberate and was defended in the frozen text and in the producer source, on
the correct ground that a *tolerance* would be tunable.

The defence does not reach the actual failure. **Bit identity is a property of
the arithmetic route used to evaluate a function, not of the function.** The
producer's own source states the opposite (`measure_relvar.py:260`): the closed
form is computed matrix-free "*so that its zero dispersion is a property of the
observable and not of a float path*". The comment asserts what the code cannot
deliver.

## 2. The counterexample, built rather than argued

The `BATCH-9e3584` Red Team (`TASK-20260809-444fe7`, `probes/probe_nullroute.py`,
0.31 s, 39 MB) evaluated **the same mathematical observable**
`X_null = (beta/d)(1/d) log|det B|` through six routes to `log|det B|`, every one
of which equals `(d-k) log q` exactly for every `A` under the frozen construction
`B = [[I_k, A],[0, q I_{d-k}]]`, and scored each through the *same* `rho_both` /
`G-REL` / bit-identity path:

| route to `log\|det B\|` | max rel. dev. from the closed form | bit-identical | `G-VAR` | `G-REL2` | reproduces the notarized table |
|---|---|---|---|---|---|
| R0 closed form *(the producer's)* | `0` | 38 of 38 | **REFUSES** | 19/19 | 304/304 |
| R1 `slogdet(B)` | `1.1e-15` | 38 of 38 | **REFUSES** | 19/19 | 304/304 |
| **R2 QR of `B^T`** | `5.07e-14` | **0 of 38** | **admits** | 19/19 | **304/304** |
| R3 `slogdet(UB)`, `U` unimodular | `9.8e-16` | 38 of 38 | REFUSES | 19/19 | 304/304 |
| R4 `0.5 slogdet(BB^T)` | `2.35e-09` | 0 of 38 | admits | 19/19 | 304/304 |
| **R5 `slogdet(BH)`, `H` ambient isometry** | `3.11e-14` | **0 of 38** | **admits** | 19/19 | **304/304** |

Read the R2 and R5 rows. Those observables are the **same function of
`(d, k, beta, q)`**, so `AM-11`'s antecedent holds; they reproduce the notarized
pre-registration's own reference table at **304 of 304 cell-by-basis entries to
every printed digit**, so at the resolution the governing text itself uses they
are indistinguishable from the refused one; they walk `G-REL1` at 10 of 10 and
`G-REL2` at 19 of 19 exactly as the refused route does; and `G-VAR` **admits**
them. Their between-basis float `sd` is `1.20e-13` and `5.44e-14`, which is
`5.0e-12` and `2.3e-12` times the committed between-basis `sd` of the genuinely
basis-dependent candidate `hkz` (`0.023888` at `L7 beta = 5`).

`R5` is not an exotic construction: it is the transform the gate's **own `G-INV`
`T1` clause** applies.

### 2.1 The producer's own committed number already carried it

`results_relvar.json`, `forced_arithmetic` block:

```
rdet_T1_ambient_isometry_residual  = 3.865352482534945e-12
rdet_T2_permutation_residual       = 0.0
rdet_T3_unimodular_residual        = 0.0
```

while `report_relvar.md` §4 states of `G-INV` for `rdet` and `X_null` that
"Residuals are `0` identically". **That sentence is true of `X_null` and of `rdet`
under `T2` and `T3`, and false of `rdet` under `T1`, in the producer's own
artifact.** That non-zero residual *is* the vanishing basis dependence that
escapes a bit test: had the frozen family presented its bases post-isometry,
`rdet` would not have been bit-identical and `G-VAR` would have admitted it.

This is a **second, independent carrier** of the same fact, inside the measured
artifact rather than inside the review.

## 3. Why bit identity fails, in one sentence

Two float routes to the same exact quantity agree in exact arithmetic and differ
in their last ULPs, and *any* non-zero difference — `1e-16` or `1e-13` — clears a
threshold set at exactly zero. **A criterion that draws its line at zero cannot
distinguish "carries no information" from "carries information at `1e-16`", and
those are thirteen orders of magnitude apart in a quantity the artifact already
records** (`float_sd`) and then discards in favour of a Boolean.

A companion narrowness, same source: the implemented refusal is an **all-cells**
test (`G_VAR_REFUSES` iff `n_zero == len(cells)`), so an observable that is
parameter-determined at 37 of 38 cells and basis-dependent at 1 is admitted, with
nothing recorded about how close it came.

## 4. The repair, named because a negative result owes forward guidance

Replace bit identity with a **scaled** dispersion test and report a **profile**:

- between-basis `sd` at fixed `(d, k, beta, q)`, measured against the candidate's
  **own between-cell range** at fixed `(d, k)`;
- reported per cell across all scored cells, never reduced to an all-cells
  Boolean;
- every candidate scored through **at least two declared arithmetic routes**, with
  the route recorded beside each value, before any dispersion verdict is reported.
  *The route is currently an undeclared free parameter of the gate.*

On the measured numbers this separates cleanly: the escaping routes sit at
`1e-13` against a between-cell range of order `1`, while `hkz` sits at `2.4e-2`.

**Validation object, already built and committed.** `probes/probe_nullroute.py`
and its recorded output are the regression fixture: a correct scaled criterion
must REFUSE all six routes to `X_null` and to `rdet` while ADMITTING `lam1n`,
`hkz` and `rawtail`. Cost of the check: `0.31 s`. This is carried as amendment
`AM-16` in `DEC-20260809-afe29b`.

## 5. The compositional statement a successor must carry

- Deleting a dispersion criterion leaves the `AM-4`/`AM-8` gate admitting
  `X_null` — the `BATCH-cbe023` and `BATCH-9e3584` finding.
- Adding `G-VAR` **in its present form** leaves the gate admitting
  `X_null`-by-QR — this entry's finding.

So the strengthened invariant still does not imply the target property — *that an
admitted observable carries information about the lattice* — and **the first step
that fails is the operationalization of dispersion, not its motivation.**
`AM-11`'s motivation is undisturbed and is not re-litigated anywhere.

## 6. Scope and limits — read before citing

1. **SINGLE-SOURCE.** One probe, one run, one reviewer
   (`TASK-20260809-444fe7`). The `BATCH-9e3584` Validator
   (`TASK-20260809-3f1dc4`) did not test routes R2, R4 or R5 and **expressly
   declines to have adjudicated them**. Re-running `probe_nullroute.py` costs
   `0.31 s` and a successor should. Any citation must carry this.
2. **The two reviews are NOT in conflict, and the union of their measurements is
   one consistent table.** The Validator's counterfactual (`V-P5`) — `X_null` from
   `slogdet` on the actual matrix — **is** row R1 above, and both reviewers report
   the identical result for it: 38 of 38 bit-identical. There is no route on which
   both measured and disagreed. The Validator's conclusion that the producer's
   matrix-free choice is "not load-bearing" is TRUE OF THE VERDICT (`R-OUT-1`
   holds either way) and FALSE OF THE JUSTIFICATION (bit identity does not
   operationalize a quantification over functions). Both stand; neither reviewer
   is corrected. The adjudication is `DEC-20260809-afe29b`.
3. **Derivation, not a theorem, and not an impossibility result.** That distinct
   float routes to one exact quantity differ in their last ULPs is elementary; the
   counterexample is a construction, checkable in seconds. Nothing here says a
   dispersion criterion cannot work — §4 names one that would, and it is untested.
4. **`AM-3` IS NOT RETIRED**, `BATCH-a44d08` IS NOT RESCORED in any respect, and
   `AM4-OBS-1` is cited only through `KN-FIND-f38a89`. Nothing in this entry bears
   on any of them.
5. **Independence in `GOAL-MLKEM-005` is PROCEDURAL AND NEVER MODEL-LEVEL.**
   AGENTS.md rule 12 is UNMET AND UNWAIVED: one session wrote the
   pre-registration, ran all four producers and made both archives, and the two
   reviews are that batch's entire independence budget. Both record
   `model_verified: false`.
6. **Every bitwise agreement cited here is reproducibility, not portability.**
   Every probe ran on the producers' own machine and library versions.

## Superseding relationship

This entry **narrows** `knowledge/findings/KN-FIND-f38a89.md` §4 item 3, which
records that the frozen gate admitted a parameter-determined null and states that
"the missing ingredient is a **dispersion criterion** ... see `DEC-20260808-05b684`
amendment `AM-11`". That remains correct as a diagnosis. What this entry adds is
that **the repair as operationalized in `G-VAR` does not close the hole**, so a
successor must not treat `AM-11` as discharged by a bit-identity test.

`KN-FIND-f38a89` is immutable and is **not edited**; its `superseded_by` stays
`null` and only its §4 item 3 is narrowed, by reference, exactly as that entry
itself narrowed `AM4-OBS-1`. **Declared cost of that discipline:** a reader
arriving at `KN-FIND-f38a89` first is not pointed forward to this entry. That is
an accepted consequence of immutability and is recorded rather than worked
around; the link exists here and in `DEC-20260809-afe29b.knowledge_promotion`.
