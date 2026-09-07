# Coordinator PRIOR — EXP-ECRANK-73275e review (BATCH-e15a65)

**Recorded 2026-09-07T17:42:52Z, BEFORE any reviewer is dispatched and before any
review verdict exists.** A prior written after the verdicts is worth nothing
(AGENTS.md, "Review architecture"). This file is a PRIOR, not a finding, not a
conclusion, and not an instruction to a reviewer. It is written from
`experiments/EXP-ECRANK-73275e/execution-report.yaml` and
`experiments/EXP-ECRANK-73275e/specification.yaml` only.

Recorded by: coordinator-ecrank-a2bf8b-2 (Coordinator, session
neural-differential-linear-masks-32bfff).

## The claim as its producer stated it

The Executor stated none. `execution-report.yaml` sets
`interpretation: none` and its `report_scope_statement` declines to map the
recorded facts to the frozen success criterion, which is correct under its
handoff. So there is no producer claim to review — only recorded observations
and the frozen contract's own decidable rules.

## The prior

The frozen contract's invalidation rules (`specification.yaml`, invalidation
rules block) state:

- **IV-1 failure voids ALL runs of this experiment.**
- IV-2 failure voids R3 and R5 readings.
- IV-3 failure voids the R3/R5 COUNT readings; feasibility-fraction and
  near-miss data remain as measurements.
- IV-4 failure voids every count.
- IV-5 failure voids the audit (R2) only.

IV-1 is defined as: known-false `d = (1, 1, ...)` Mestre degeneration (R7) at
n = 6 and n = 8, **certified totals must equal n - 1** (5 and 7).

What the Executor recorded for R7:

    n6_per_b_built: false
    n6_reason_all_eight: degenerate_deg_s_2
    n8_aggregate_totals: [5, 6, 7, 7, 7, 7, 6, 7]
    n8_expected: 7
    n6_all_match: false
    n8_all_match: false

What the Executor recorded for R8 (IV-3):

    n_plants_declared: 9
    n_plants_built: 0
    build_reason: degenerate_deg_s_2
    recovered: 0
    recovered_denominator: 0
    log_log_slope: null
    decade_ratios: {}

**My prior is therefore:** the run set most likely fails its own preregistered
IV-1 known-false control, which by the frozen contract voids all eight runs,
and separately fails IV-3, which voids the R3/R5 count readings. If that holds,
the expected disposition is **`inconclusive` with an executor-repair
successor** — not `support`, not `weaken`, not `reject_scoped`. I expect R3's
reading of 28 certified n = 6 instances at `feasibility_fraction: 0.002` to be
UNUSABLE as a count.

I expect this to assert **nothing** about HEUR-1 and nothing about
H-ECRANK-36d8d7. A control failure is an instrument failure, not negative
mathematical evidence (AGENTS.md rule 3).

## The two ways I expect I could be wrong

Reviewers are free to reach either, and a reviewer who reaches one of these
against my prior is doing the job correctly.

- **(a) `degenerate_deg_s_2` may be the CORRECT behaviour of a known-false
  object.** A `d = (1, 1, ...)` tuple is *supposed* to degenerate. If so,
  "not built" is the control PASSING, and the spec's "certified totals must
  equal n - 1" is the wrong operationalization of it. This must be decided
  from the frozen spec's own text, never from which reading is convenient.
- **(b) The n = 8 totals deviate from 7 in exactly three of eight positions.**
  Whether the spec requires ALL eight to equal n - 1 or an aggregate is a
  reading question with opposite consequences.

## Joints this creates — each needs exactly one owner and a worked attack

1. **IV-1 disposition** (per (a) and (b)). Load-bearing: decides whether any
   count in the experiment survives.
2. **IV-3 disposition** — whether the positive control ran at all. A
   planted-yield control that built 0 of 9 plants has not demonstrated the
   solver detects what it should see; `recovered: 0/0` is an empty
   denominator, not a 0% rate.
3. **PD-2.** R5 recorded `counted_exact_ops: 100002120` with
   `ops_cap_respected: false` against the 1.0e8 cap. The stopping rule makes
   exhaustion **inert in both directions**, so R5's `found: 0` must not be
   read as a negative. Verify no downstream reading treats it as one.
4. **PD-3.** The n = 8 Bezout enumeration used the integer `(a, b)` box of
   width `min(H, 20)` (IC-732-3 in `implementation.md`), NOT the full rational
   height-H coefficient lattice. State what the executed object actually was
   and whether the frozen spec permits it.
5. **PD-1.** R6's `null_proof_first` is null in `raw-result.json` because
   `construct_arm` overwrote the b_index-0 proof; the frozen infeasibility
   formula is in `source/null_family.py`, written before any R6 step. IV-4
   nonetheless recorded `found: []` exactly. Decide whether the null object
   still discriminates given the recording gap.
6. **R4 / IV-2.** `iv2_counts_identical` is **false** in `raw-result.json`;
   the Executor's note says the in-memory flag compared int-keyed vs
   str-keyed dicts and that both `counts_per_H` equal
   `{100: 15, 1000: 22, 10000: 28}` after JSON. This is a claim about a bug
   in the check, made by the party being checked. Requires blind
   re-derivation from the two `raw-result.json` files, not acceptance of the
   note.
7. **Executor inference provenance.** The report records
   `backend: cursor_cloud_native`, `resolved_model_id: cursor-grok-4.6`,
   `model_verified: false`, `fallback_used: true` — against a handoff setting
   `degraded_allowed: false` and `independent_session_required: true`. Whether
   that is a permitted fallback or a policy violation has consequences for the
   whole run set.
8. **IV-8.** No 4-class instance appeared in R3 or R5; the Executor recorded
   an explicit untested statement. Confirm the untested scope is carried
   forward and not quietly closed.

## Blind re-derivation required

Two quantities must be re-derived from raw artifacts WITHOUT reading the
Executor's summary of them:

- (i) the R3-vs-R4 `counts_per_H` equality (joint 6);
- (ii) the R7 n = 8 per-tuple certified totals (joint 1(b)).

## Proves-too-much control

If the reviewers' reading of the controls would ALSO invalidate the
predecessor EXP-ECRANK-76a70d run set — or would validate this one — the
review must say what distinguishes the two. A reading that proves too much
about the predecessor is a defective reading.

## Scope

Nothing in this file promotes a claim, changes a status, or authorizes
execution. H-ECRANK-36d8d7 stays `specified`; C1 stays OPEN and UNPROMOTED;
IMP-2 stands.
