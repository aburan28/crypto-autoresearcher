# Independent replication of BATCH-d2a728 review, 2026-08-13

**These are not archived reviews and are not evidence.** They carry no receipt,
no `path_sha256` binding, and no ledger record, and they change no status.

`GOAL-MLKEM-004` closed as `closed_at_budget` on 2026-08-05 under
`DEC-20260805-0b3e11`. `BATCH-d2a728` was reviewed and ledger-archived long
before that under `TASK-20260803-586a7f`. The reviews in this directory were
produced on 2026-08-13 by a session resuming from a stale snapshot that still
showed the batch as pending; the full account is `KN-FIND-3546c2`.

The artifacts live here, rather than in
`batches/BATCH-d2a728/tasks/TASK-20260803-{535d15,bc2f41}/`, because those paths
hold immutable files bound by hash to the ledger archive. Writing to them would
break that archive permanently (AGENTS.md rule 15).

They are retained for one reason: the red team had no access to the archived
reviews and independently reproduced the campaign's central negative result by a
different route — a norm-matched sign-and-coordinate permutation null returning a
402x variance design effect against 404x for the real sieve `X`, versus the
campaign's ablated-Y-only arm holding `X` exactly fixed. Same conclusion, no
contact, different null.

| File | Origin | Status |
| --- | --- | --- |
| `red_team_report.yaml` | `TASK-20260803-bc2f41` re-run | complete; verdict `blocking_objections` |
| `red_team_notes.md` | `TASK-20260803-bc2f41` re-run | complete |
| `validator_report.yaml` | `TASK-20260803-535d15` re-run | complete; verdict `ADMISSIBLE_WITH_DEFECTS` |
| `validator_notes.md` | `TASK-20260803-535d15` re-run | complete |
| `validator_scripts/*.py` | `TASK-20260803-535d15` re-run | three audited recomputation scripts |

## The cross-check worth reading

The two sessions ran concurrently and in isolation, with nothing forwarded
between them, and they reached the candidate-class null offset by different
methods:

| | Centred-binomial null mean | Uniform null mean |
| --- | --- | --- |
| Validator, measured | `0.00856739` | `0.00018357` |
| Red team, derived analytically | `0.008567389` | `0` |

Agreement to eight significant figures between a measurement and a closed-form
derivation, obtained independently, is what settles the interpretation. The
offset is candidate-prior Fourier mass against a fixed population baseline. It
is a property of how the candidate set was drawn, not of residual LWE structure,
sieve geometry, or lattice membership, and its size was predictable without
running the experiment at all.

The two sessions then differ only on what follows from that. The validator, which
did not derive the analytic value, reports the difference at 90.4 SE and requires
class-matched or stratified null baselines before any batch-2 comparison. The red
team holds that the significance scale is beside the point once the value is
analytically predicted, and that the deeper problem is object mismatch: batch 1
scores full secret candidates while `MATZOV.Nf` models a split enumeration plus
FFT bin, so no amount of null repair makes the comparison well-posed.

Both conclusions point the same way for any successor: the null must be matched
to the candidate prior, and the measured object must be the one the cost model
actually describes.

## Verdicts and their standing

`ADMISSIBLE_WITH_DEFECTS` (validator, 30 claims reproduced, 1 not reproduced, 4
unable to check) and `blocking_objections` (red team, 8 objections) are addressed
to a batch-2 design that events superseded. Read them as methodological
commentary, not as live gates. Both record `fallback_used: true`,
`degraded_requirements: []`, `model_verified: false`.

Among the validator's four defects, two are durable process lessons independent
of this campaign: the producer reused a pre-existing virtual environment instead
of rebuilding it, and its receipt recorded `dirty_tree: false` inaccurately.

The red team's `blocking_objections` verdict and its eight objections are
addressed to a batch-2 design that was superseded by events; read them as
methodological commentary, not as a live gate. Its model provenance records
`fallback_used: true` with `degraded_requirements: []` and
`model_verified: false`.
