---
id: KN-FIND-9d44b4
type: internal_finding
title: "A fibre-constancy test evaluated on floating-point values cannot separate 'reads the instance' from 'reads a nuisance parameter'; evaluated exactly it needs a scale"
tags: [dispersion-criterion, admissibility-gate, g-var2, fibre-condition, am-16, am-17, am-18, floating-point, machine-epsilon, bit-identity, scale-degenerate, null-object, precision-invariance, instrument-design, pre-registration, ml-kem, negative-result, toy-scale]
confidence: derivation_plus_three_independent_lines_in_two_review_sessions_on_one_model
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-4ed139, BATCH-9e3584, TASK-20260812-34b86c, TASK-20260812-56b9da, TASK-20260812-4b8ede, TASK-20260812-55056b, TASK-20260812-696cd4]
internal_refs: [EV-MLKEM-aa39ad, DEC-20260812-781961, DEC-20260812-7c4a1e, DEC-20260809-afe29b, DEC-20260808-05b684]
sibling_findings_narrowed: [KN-FIND-4b8d73, KN-FIND-2a35aa]
sibling_findings_note: "`internal_refs` carries LEDGER records only, which is the shape the validator checks and the shape `KN-FIND-4b8d73` itself uses. The sibling findings this entry narrows are named here and throughout the body; neither is edited and neither `superseded_by` is set."
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null_threads1_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_argset.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-55056b/probes/probe_gvar2_rederive.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-55056b/probes/probe_null_and_riders.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-55056b/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/results_gvar2.json
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-55056b/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/red_team_report.md
added: '2026-08-12'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. Measured at
`q = 3329`, `d in {20, 30, 40, 100, 140}`, the frozen `(k, beta)` grid, 8 frozen
bases per lattice per family, four declared families plus three fibre seed prefixes,
six declared arithmetic routes for determinant-only candidates, `numpy 2.4.6` float64
on one 4-core Linux host, **no reduction at all** in the measurement this entry rests
on. No number here transports to `beta = 606`, `d = 1420` or any other parameter set
by extrapolation, by analogy or by any other route. There is no cryptographic
baseline, so `dominated_by` and `sota_delta` are **not applicable for that reason**
and not by omission.

**THIS ENTRY MAKES NO ADMISSIBILITY CLAIM ABOUT ANY OBSERVABLE IN EITHER DIRECTION.**
The pre-registration it rests on says so before any measurement exists: passing the
criterion carries no claim that an observable carries lattice information, and
neither does failing it. What follows is about an **instrument**.

The finding, in one sentence:

> A **fibre-constancy test evaluated on floating-point values** cannot separate
> "reads the instance" from "reads a nuisance parameter", because machine epsilon
> makes every arithmetic route that sums `d` logarithms non-constant on the fibre;
> and the same test **evaluated exactly** requires a scale, which reintroduces
> precisely the threshold the fibre clause was introduced to avoid.

## 1. Why this entry exists, and what it narrows

`KN-FIND-4b8d73` §3 records the fibre condition as **"the named separator — and it
has been named and never scored"**, and carries an explicit prediction with the note
that **"nobody has measured this"**. `BATCH-4ed139` scored it, under a termination
clause frozen and notarized before any measurement existed. This entry narrows
`KN-FIND-4b8d73` in exactly two places, **by reference**:

1. **The separator it names is now scored, and the clause as operationalized is
   defeated.** `G-VAR2` — the scaled criterion of `AM-16(a)` extended by the fibre
   clause of `AM-17(c)` — **ADMITS** `rdet`, which reads **zero entries of `A`**, at
   38 of 38 scored cells through three of its six declared arithmetic routes, on the
   fixture `AM-16(d)` was written against. §2 below.
2. **Its open prediction is discharged.** The scaled criterion **does** refuse
   `V_evade` (`X_null + 1e-9·A[0,0]/q`): `VAR-S` alone refuses it at 38 of 38 cells
   through all six routes, max between-basis `sd` `3.912e-10`, reproducing the
   `3.91e-10` the prediction was derived from. That was frozen in advance as a
   **CONSISTENCY CHECK** and is not counted as empirical content — it is recorded
   here because the corpus entry asked for it.

`KN-FIND-4b8d73` and `KN-FIND-2a35aa` are immutable and are **not edited**; both
`superseded_by` fields stay `null`, exactly as each left its own predecessor's. This
entry inherits their narrowing of `KN-FIND-f38a89` §4 item 3. The adjudication is
`DEC-20260812-781961`; the evidence is `EV-MLKEM-aa39ad`.

## 2. What was measured

The criterion is a conjunction, frozen in advance. `VAR-S` is scaled between-basis
dispersion against the candidate's own between-cell range at fixed `(d, k)`;
`VAR-F` requires the candidate to be non-constant on a **fibre** family that holds
its declared nuisance arguments fixed while the free content of `A` varies. Two
frozen sub-rules matter:

- **The degenerate-scale rule.** A candidate taking no `beta` argument is constant
  across the beta grid at fixed `(d, k)`, so its own between-cell range is `0`
  **exactly** and `VAR-S` is `scale_degenerate` — *not a pass and not a fail*. The
  cell is then decided by `VAR-F` **alone**.
- **The bit-identity fallback.** At a `scale_degenerate` fibre cell, non-constancy is
  decided by **bit identity of 8 IEEE-754 doubles**.

| what | measured |
|---|---|
| `rdet = exp(log\|det B\|/d)` on the reference family `F0` | `scale_degenerate` at **38/38** cells under **all six** routes, so `VAR-S` decided **none** of them |
| exact integer `\|det B_i\|` across the 8 fibre bases | **bit-identical everywhere**, at all 10 lattices in all 6 fibre families (an asserted and printed guard) |
| float `log\|det B\|` across those same bases | **not** bit-identical under 3 of the 6 routes: fibre `sd` `5.42e-13`…`4.18e-11` (QR of `B^T`), `5.69e-09`…`6.03e-07` (`0.5·slogdet(BB^T)`), `2.81e-13`…`3.35e-11` (`slogdet(BH)`) |
| consequence | `VAR-F` **PASSes**, the conjunction **ADMITS**, and the fixture's declared target for `rdet` is **MISSED at 38/38 cells on three routes** |

**It is not about `rdet`.** The Validator's blind null `N2` —
`X_parfree(B) = log|det B|/(d·k)`, named nowhere in the frozen text and scored by no
producer — reproduces the admission exactly, with the prediction written into the
probe before the numbers were read: `scale_degenerate` 38/38 on all six routes,
`VAR-F` PASS and ADMIT 38/38 under the same three routes, 0 under the other three.
**Any beta-free determinant-only functional evaluated through such a route is
admitted.**

**It is not about the threshold either.** The verdict surface was recomputed across
**sixteen decades** of the threshold, `1e-16` to `1`: `rdet`'s admissions are
`114 = 3 routes × 38 cells` at **every** value. Bit-identity at a `scale_degenerate`
cell **has no threshold at all**, so the failure is entirely structural and the
calibration is not load-bearing for it.

## 3. The null-object control, and the nearby object that should not fail

`docs/inventor-protocol.md` §3: name the parameter that should destroy the signal and
run the identical measurement on a null object of the same shape.

- **Null object** `rdet` (reads zero entries of `A`) against **real object**
  `X_gso_k` (reads the leading `k` Gram–Schmidt norms), same fibre, same code path.
- **Parameter**: arithmetic precision.

| object | relative fibre dispersion, float64 | float32/float64 ratio |
|---|---|---|
| `rdet`, all routes | max `2.64e-09` (exactly `0.0` under `slogdet(B)`) | `1.4e6` … `5.9e8`, median `5.5e7` |
| `X_gso_k` | `5.71e-04` … `1.09e-02` | `0.9999991` … `1.0000001` |

`eps32/eps64 = 5.369e8`. **The null object's dispersion moves by up to `5.9e8` when
epsilon moves by `5.4e8`; the real object's does not move at all.** That is the
canonical artifact signature, and the falsifier — either half failing — did not fire
in either direction.

**The nearby object.** Take `log|det B|` from the **exact integer determinant** at 60
significant digits, changing nothing else — same observable, same family, same fibre
family, same declared arguments, same threshold, same two clauses. The criterion then
**REFUSES `rdet` at 38/38 and the fixture's declared target is MET.** Identical with
all five BLAS thread caps pinned to `1`.

**The effect is forced, not accidental**, and this is recorded *against* the reading
that it is a quirk of one machine: the fibre dispersions sit at **170 to `4.4e6` ULPs**
of the cell mean — exactly the accumulated rounding of a `d`-term float sum — so any
host reproduces non-bit-identity with overwhelming probability.

## 4. The other half: evaluated exactly, the clause needs a scale

Replacing the bit-identity fallback with a **relative-dispersion** test at the same
threshold repairs the null and breaks the real object: `rdet` would be refused
everywhere (max relative `2.6e-9`), and `X_gso_k` would **also** be refused at 3 of
the 10 lattices — **15 of the 38 cells**. The two objects are `5.3` orders apart, so a
separating threshold *exists*; the frozen one is not it. And the repair is not
precision-robust either: at float32 the null object's relative fibre dispersion
reaches `2.95e-01`, above any threshold that would admit anything.

**So the obstruction is two-sided, and both sides are measured.** A fibre-constancy
test on floats cannot separate the two; a fibre-constancy test evaluated exactly
needs a scale, and a scale is a threshold. **What remains open** — stated rather than
implied — is whether a scale exists that separates them **without being calibrated on
them**. The measured separation is genuinely wide, and the only shape that could work
is a scale declared **relative to the working precision** rather than to the
observable. Nobody in this campaign has tried that, and it is one line.

## 5. The second, independent defect in the same clause

Both reviewers found this separately, and it is recorded because it binds the next
criterion rather than this one: **the declared argument set is decorative in the
implementation.** The frozen text declares `A[0,0]` a nuisance argument to be held
fixed on the fibre for two candidates, and quantifies the fibre family **after** the
candidate; the implementation fixes one candidate-independent family pair **before**
any candidate is named, and the guard that exists to catch exactly this asserts and
prints only that `|det B|` is bit-identical. Measured: `A[0,0]` **varies** across the
8 fibre bases at **10 of 10 lattices in every one of the six fibre families**.

**It changes no outcome of the batch**, and that is reported at the same weight by the
reviewer whose objection it is: the one candidate actually scored with such a nuisance
set does not flip, because the scaled clause refuses it either way. It binds the
moment any candidate whose declared nuisance set contains a non-determinant argument
reaches `VAR-S` ADMIT or `scale_degenerate` — at which point the clause would be
decided on a fibre that lets the very argument it is supposed to pin float free.

## 6. What a successor must do, and what it must not

Carried as amendment **`AM-18`** in `DEC-20260812-781961`, whose first clause is a
**stopping condition rather than a repair**:

1. **No further dispersion criterion may be specified in this campaign until
   "non-constant on the fibre" is stated as a NUMBERED assumption with an explicit
   falsification condition, at finite precision.** The implicit assumption in force
   until now — *non-constant in IEEE-754 float64 ≡ non-constant* — is measured **false**
   here. This is a specification requirement, **not a lane closure**: it retires
   nothing and forbids no direction of inquiry. It exists because the branch that
   fired, unlike its sibling, carried no bar on an unbounded repair loop, and
   **premature closure and unbounded repair are the same failure mode in two
   directions.**
2. **Precision is a declared axis.** Any constancy clause is evaluated at two working
   precisions and reports the ratio; a clause whose verdict changes with precision is
   reading a *representation*. For a determinant-only candidate an exact-arithmetic
   route must be among the declared routes — one exists and costs `0.4 s` at this scale.
3. **The fibre family is per candidate**, built from that candidate's own declared
   nuisance set, and the guard prints which declared arguments were verified constant.
4. **A must-pass guard publishes its own reachability before the run.** In this batch
   the guard's VOID row was unreachable by a factor of **71.3** before anything ran, so
   its non-firing is **not evidence**; the informative content is the crossing
   amplitude, and a decadal grid reports that only as an **upper bound**.
5. **Calibrate any admission against a null object at declared amplitudes.** One built
   here — the observable plus a scaled SHA-256 digest of the exact integer basis, which
   reads every entry of `A` and carries **no** lattice information whatever — is
   **admitted at 38/38** at the top amplitude. It measures the width of the gap between
   *"depends on the presentation bits at relative amplitude ≥ τ"* and *"carries lattice
   information"*, and that gap is at least the distance from a cryptographic digest.
   `n = 1`.

## 7. Scope and limits — read before citing

1. **THE CONCLUSION IS REACHED BY THREE INDEPENDENT LINES; SEVERAL MECHANISMS ARE
   SINGLE-SOURCE.** The headline was reached by the producer, by a Validator
   implementation written from the frozen text importing no producer module (1368 of
   1368 per-cell values bit-identical, 1368 of 1368 verdicts agreeing, not one cell
   differing), and by a Red Team reproduction with `numpy` alone. The precision null,
   the exact route, the repair simulation, the null object and the argument-set
   mutation are each **one probe, one run, one session**. Any citation must carry that
   split.
2. **INDEPENDENCE IS PROCEDURAL — NEVER MODEL-LEVEL, AND HERE NOT ENVIRONMENTAL
   EITHER.** AGENTS.md rule 12 is **UNMET AND UNWAIVED** in this campaign. Both
   reviews are **two SESSIONS on ONE MODEL and ONE HOST**, on the same stack as every
   producer, and every record carries `model_verified: false` with no adapter probe
   receipt anywhere. **Nothing in this entry may be cited as model-level or
   environmental corroboration**, and agreement between reviewer and producer float
   numbers carries no cross-platform weight at all.
3. **THIS IS A STATEMENT ABOUT FLOATING-POINT EVALUATION, NOT ABOUT MATHEMATICS.** In
   exact arithmetic the null object is exactly constant on the fibre, and three of the
   six routes reproduce that and refuse it. On an exact-arithmetic or uniformly-rounded
   stack the refusal half would pass. **The finding's generality is bounded by that**,
   and one further portability caveat is measured: the ambient-isometry route's float
   *magnitudes* are not portable across BLAS builds (148 scalars move, max absolute
   `1.34e-10`) while its *qualitative* outcome is, and the failure survives losing that
   route entirely.
4. **NOTHING HERE IS AN IMPOSSIBILITY RESULT.** §4 names a shape that might work and is
   untested. A count of criteria that failed is a fatigue report, not a closure, and
   this entry does not close the lane, the criterion family, or the campaign.
5. **DERIVATIONS AND CONSTRUCTIONS, NOT THEOREMS.** That distinct float routes to one
   exact quantity differ in their last ULPs is elementary; that a scale-free test cannot
   separate `4.18e-11` from `9.02e-02` is elementary — measured at **9.33 orders of
   magnitude, same verdict**; the rest are built counterexamples.
6. **IT ESTABLISHES NOTHING ABOUT ANY LATTICE.** The batch it comes from adjudicates no
   proposition about a lattice, revalidates no prior batch, retires no prior amendment,
   and closes, pauses and completes nothing.

## Identifier provenance

`KN-FIND-9d44b4` was drawn **without scanning state** (AGENTS.md rule 14) and then
confirmed in **two scopes** by the dispatching session at the Coordinator's request:
worktree `tools/allocate_id.py --check` (well-formed, 0 occurrences) **and** a
cross-ref sweep of the 25 most-recently-updated remote branches (0 hits), plus
confirmation that it is not tracked under `knowledge/findings/` on `origin/main`.
Recorded as two-scope confirmed and **never** as `--check` alone: `--check` answers
from the working tree only, which is how the same tool once reported two identifiers
"free" while both were already bound on a pushed branch. **A passing `--check` is
necessary and not sufficient.** The Coordinator that authored this entry held no shell
and claims neither check as its own.

## Superseding relationship

This entry **narrows** `knowledge/findings/KN-FIND-4b8d73.md` in the two places listed
in §1 and inherits its narrowing of `knowledge/findings/KN-FIND-2a35aa.md` and
`knowledge/findings/KN-FIND-f38a89.md`. **No prior entry is edited and no
`superseded_by` is set**: each remains correct on what it measured, and each is
extended rather than corrected. **Declared cost of that discipline**, restated because
it compounds with every link: a reader arriving at `KN-FIND-f38a89`,
`KN-FIND-2a35aa` or `KN-FIND-4b8d73` first is not pointed forward to this entry. That
is an accepted consequence of immutability; the links exist here and in
`DEC-20260812-781961.knowledge_promotion`.
