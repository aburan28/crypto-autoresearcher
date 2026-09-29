# EXP-ECRANK-73275e v2 review

## Scope and custody

This is the Coordinator composition for `REVIEW-PLAN-BATCH-8fa16f` over the
snapshot-bound v2 replication package produced by `TASK-20260908-5291f8`.
The scientific input is fixed by snapshot commit
`796eed5fa06ac369f592175b55395d5853329dfa`, with custody recorded in
`coordination/goals/GOAL-ECRANK-002/batches/BATCH-e3cf55/archives/TASK-20260908-9439c0/snapshot-receipt.json`.
The review plan records the prior, three separately owned joints, mutual
blindness, the proves-too-much objects, and the required blind
re-derivation. This review does not edit the v1 contract, re-score v1 runs,
promote C1, or change the status of the hypothesis, experiment, or goal.

The reviewed claim is deliberately observational: R9 and R15 pass their
amended control gates; R10 recovers the nine named planted elliptic n=6
instances; R12 records 33 certified n=6 instances and R13 replays them
canonically; R14 completes its declared finite integer-box enumeration with
zero found; and R9/R11 retain `CERTIFIER_LIMITED` ladder outcomes. No result
is interpreted outside the snapshot and protocol boundaries below.

## Coordinator prior

Before the review, the recorded prior expected the control-admission receipts
and R12/R13 determinism to reproduce, R10's 9/9 detection to support the R12
count only at its toy scope, R14's zero to remain limited to its declared
integer box, and `CERTIFIER_LIMITED` to remain an instrument boundary. A hash
mismatch, certificate failure, false control label, or inference extending
R14 beyond its box would have overturned that prior.

## Joint findings

### J1: blind control derivation

`TASK-20260909-07a594` derives the IV-1R and IV-4R truth conditions from the
frozen blind input. It correctly states that `degenerate_deg_s_2`, a nonzero
`x^2` coefficient, and certified total zero are required for every R9 n=6
control; and that R15 requires zero solutions plus the `no_real_root`
infeasibility flag. After freezing, its exact comparison finds eight R9
controls satisfying IV-1R and 64 R15 null cases satisfying IV-4R.

The report also identifies the unavoidable limitation: the blind input does
not include the defining polynomial, discriminant, field, or specialization
map, so it cannot independently derive the geometry of the `d=(1,...,1)`
specialization. It therefore validates the conditional gate and the receipt
values, not the omitted geometric derivation. The report truthfully records
`blind_from_respected_before_freeze: true` and
`blind_from_respected: false`, because the frozen plan expressly requires
post-freeze reads of raw R9 and R15 receipts under the broad `runs` prefix.

### J2: receipt and certificate integrity

`TASK-20260909-9ee65f` independently recomputes the declared custody and
integrity checks. The snapshot has 63 staged paths and 62 hash-bound paths,
with all 62 hashes matching and no missing paths. All seven terminal v2 runs
have the required companions and completed manifests, and each respects its
operations cap.

The seeded R10 reconstruction reproduces nine distinct `(b, pattern)` pairs,
nine distinct `h_A` values, nine elliptic objects, and exact solver recovery
of 9/9 plants. R12 and R13 have identical canonical found lists, per-height
counts, checkpoint content, and counted operations (`9,447,724`). Three
preselected R12 certificate summaries independently re-compute as `PASS`:
found indices 0, 11, and 21, with aggregate totals 2, 2, and 6 respectively.
This is a custody and exact spot-check finding; it is not a claim that every
R12 certificate was re-derived in the review.

### J3: scope and proves-too-much controls

`TASK-20260909-66f9be` finds no counterexample within the declared scope and
holds all three scope boundaries. R14's zero covers the completed 10^4
b-tuples in the integer coefficient box
`[-min(H,20), min(H,20)]^2`, with `c` solved exactly, at the stated n=8
heights. It does not cover non-integer coefficients, the full rational
height-H lattice, another box, unrestricted height, or an asymptotic lattice.

R9 and R11 remain `CERTIFIER_LIMITED`: their top-rung totals are, respectively,
`[6,6,7,7,7,7,7,6]` and `[5,7,7,7,7,7,5,6,6]`, rather than an all-7 exact
certificate. The three ladder rungs are recorded as a no-op for these inputs
because the committed certifier's good-prime list is capped at 60 primes
below the nominal 1500 bound. The totals are lower bounds and the ladder is
an instrument-boundary observation.

R10's 9/9 result is only the named planted R3-family shape at n=6 with
`h_A <= 10000`, the recorded seed and injection stream, and the disclosed
same-machine/runtime setup. Its exponent-window and per-decade calibration
checks fail (`all_in_window: false`, ratios `[2.25, 1.0]` outside `[5,20]`).
Those failures void the calibration reading, not the finite detection
observation. The 9/9 ratio does not establish arbitrary-instance
completeness, machine independence, or asymptotic behavior.

## Observations retained from the v2 report

| Run | Observation | Boundary |
| --- | --- | --- |
| R9 | Eight n=6 controls reject as `degenerate_deg_s_2`, have nonzero `x^2` coefficients, and have certified total 0; n=8 top-rung totals are `[6,6,7,7,7,7,7,6]`. | IV-1R passes; IV-1C is `CERTIFIER_LIMITED`, with lower bounds and a no-op ladder. |
| R10 | Nine distinct elliptic n=6 plants are recovered 9/9. | Planted R3-family scope only; exponent and per-decade calibration fail. |
| R11 | Nine n=8 planted controls produce top-rung totals `[5,7,7,7,7,7,5,6,6]`. | `CERTIFIER_LIMITED`; no exact all-7 conclusion. |
| R12 | 10,000 declared b-tuples complete; 33 instances are found, with convention-A counts `{100: 20, 1000: 28, 10000: 33}` and convention-B counts `{100: 26, 1000: 33, 10000: 33}`. | Exact tested n=6 toy scope; no asymptotic count-law inference. |
| R13 | R12 instance list, counts, checkpoints, and operations replay identically. | Same seed and same disclosed machine/runtime; determinism evidence. |
| R14 | 10,000 integer-box b-tuples complete with `found=0`, `feasible=0`, and `near_miss_total=0` at n=8. | Completed finite integer-box observation; full rational lattice remains unmeasured. |
| R15 | 64 null cases have zero solutions and `no_real_root=true`; the too-strict first attempt is preserved. | IV-4R passes; attempt-1 is an implementation-check defect, not mathematical evidence. |

## Scoped disposition

The three assigned joints hold as bounded review findings. The v2 round
provides replicated toy-scope observations for the control gates, the
R10 planted detection control, the R12/R13 deterministic package, and the
finite R14 enumeration. The fresh v2 seed round does not supply an independent
machine or runtime, and the review does not turn the observations into a
cryptanalytic result.

The following claims are expressly rejected as unsupported mutations of the
reviewed claim:

* R14's integer-box zero is not a zero over the full rational-height lattice.
* `CERTIFIER_LIMITED` is not `PASS`, an exact total, or evidence that the
  nominal prime-bound ladder was exercised.
* R10's 9/9 planted recovery is not arbitrary solver completeness,
  machine-independent reliability, or an asymptotic law.
* The failed R10 exponent and per-decade checks are not silently omitted.
* The R12 convention tables and R14 zero do not validate `HEUR-1`'s
  exponent-plus-two count law; the dual-convention readings remain a scoped
  unresolved measurement.

No C1 closure or breakthrough-tier review is claimed. C1 remains open and
unpromoted under its existing gate. Any broader rational-lattice enumeration,
other plant families, independent-machine transfer, or exact certifier ladder
requires a new additive protocol and fresh artifacts.

## Procedure deviations and integrity limits

The mechanical independence check reports two record-level deviations. First,
J1's required post-freeze comparison reads two raw receipts beneath a path
prefix that the plan also lists in `blind_from`; the report records the
pre-freeze boundary and the exception rather than claiming all-session
blindness. Second, the J3 report uses the field
`review_attestation.joint_scoped_verdict` and omits the checker-required
aggregate `review_attestation.verdict`. The report's three J3 objections and
its `joint_scoped_verdict: holds` are preserved exactly; the missing aggregate
field is a schema/conformance defect, not a reason to invent a verdict.

Accordingly, `python3 tools/check_review_independence.py --batch
coordination/goals/GOAL-ECRANK-002/batches/BATCH-8fa16f` reports two
independence problems. The queue nevertheless establishes that all three
review tasks completed in separate sessions, had disjoint joint ownership,
and read no sibling reports. These deviations are included in the ledger
decision and are not converted into scientific evidence.

The executor's `fallback_used: true`, unverified `vllm/qwen3.8-27b` model
identifier, and same-machine disclosure are provenance limitations. They do
not change the recorded observations or support a claim about the mathematics.

## Next action

Preserve this evidence and decision as the bounded review archive. Keep C1
open and unpromoted. Continue the separately authorized BATCH-a9c273
execution lane from its own frozen queues; it has no dependency on this
review's record contents. If the program needs a broader conclusion, first
freeze an additive protocol covering rational coefficients, independent
machine/runtime transfer, and a certifier whose ladder is not capped below
its advertised bounds.
