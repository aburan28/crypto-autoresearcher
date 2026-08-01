# BATCH-021 OPENING — CTRL-RT047-MATCHED-NULL

- Goal: `GOAL-ECDLP-001` (active) — Sub-goal `SG-ECDLP-001`
- Experiment: `EXP-DS-001` — Hypothesis: `H-DS-001` (status `analyzed`, unchanged by this opening)
- Control protocol: `CTRL-RT047-MATCHED-NULL` — Amendment: `PA-DS-001-v2-ctrl-matched-null`
- Run to be executed (gated): `RUN-DS-001-ctrl-matched-null`
- Opened by: `DEC-20260801-004`, executing the single `next_action` recorded at the
  BATCH-020 close (`DEC-20260801-003`)
- Queue: `coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/dispatch_queue.json`
- Tasks: `TASK-20260801-001` … `TASK-20260801-009`, `max_concurrent` 3

## What BATCH-021 tests

RT047-CTRL-1 variant (a): the **matched-ALGORITHM null**. `naive_search` and
`split_search` run UNCHANGED — same code, `smoothness_abort=false`, same
`charge_backend_units`, same frozen wall-derived cost identity, 200 relations,
seed 101 — against the additive group **Z/753848Z** (order matched to the
BATCH-020 curve group order) with a 128-element negation-closed random signed
factor base and 200 uniform random targets. R and R_null are reported under
**both** the wall proxy and the charged-unit proxy, with neither privileged,
plus per-arm `n_enum`, peak claw-table entries and peak RSS.

## Why it is the single ranked next action

BATCH-020's favourable R (0.0322 wall / 0.0147 units) came from an arm that
exercises **no elliptic-curve structure at all**: RT047-B2 derived that
`smoothness_abort` was false, that `encode_intermediate` is provably the identity
map at this cell (D = 2^40 against x < 2^20), and that the join is exact
x-coordinate equality. What was measured is a depth-3 → depth-2 enumeration
change with a hash table — generic meet-in-the-middle. If the same code produces
the same R on a group with no curve in it, the "win" has nothing to do with
ECDLP. The legacy null `NULL-DS-RANDOM-MULTIHOMOGENEOUS` cannot decide this: it
changes the *algorithm* and leaves the *object* question untouched, so it is not
a matched control (inventor-protocol §3.2).

This is the cheapest experiment that can kill — or vindicate — the lane's
central inference. Under 60 seconds of compute, no new dependencies, no new
mathematics, decisive in both directions. The other three RT047 controls rank
behind it: CTRL-2's B-sweep is only interpretable once the object-level null is
known; CTRL-3 is a contract-drafting item with no compute; CTRL-4 presumes the
arm under test is the arm of interest, which is exactly what CTRL-1 decides.

## Pre-registration is the point of this batch

The disposition map is **frozen in the control addendum before the run exists**.
The lane's central inference is finally being tested, so the reading rule is
written before the data. `TASK-20260801-002` hash-binds it before any independent
session reads it; `TASK-20260801-003` is instructed to attack the
pre-registration adversarially — to try to construct a result the map cannot
classify or classifies two ways.

Decision variable: `W` = R_matched_null (wall proxy), `U` = R_matched_null
(charged-unit proxy). Bands: LOW < 0.5, MID 0.5–0.9, HIGH ≥ 0.9. The 0.5 and 0.9
thresholds are inherited from H-DS-001's own prediction clause and R-1's F2
branch; they are not new.

| Branch | Condition | Disposition |
|---|---|---|
| **D-1** ARTIFACT CONFIRMED | `W < 0.5 AND U < 0.5` (anchor ≈0.03 wall / ≈0.015 units) | **weaken**, win reattributed to generic meet-in-the-middle; H-DS-001 `analyzed → weakened` scoped to the *structure attribution*. Fires H-DS-001's OWN falsification condition and R-1's F2 branch for the first time in the series. **Explicitly NOT reject-as-impossibility.** Refutation artifact archived first; replication + RT047-CTRL-2 scheduled. Sub-branches D-1a (within 2× of the live real-arm re-measure) and D-1b (partial transfer — must be written as partial). |
| **D-2** STRUCTURE EVIDENCE | `W ≥ 0.9 AND U ≥ 0.9` | **replicate**. First genuine structure evidence this experiment has produced. H-DS-001 stays `analyzed` — no `support`, no S1_met (one bit size against a two-bit-size criterion; unreplicated). RT047-CTRL-2's B-sweep becomes the immediate follow-on. |
| **D-3** PARTIAL ATTENUATION | `0.5 ≤ W < 0.9 AND 0.5 ≤ U < 0.9` | **inconclusive**. Neither explanation accounts for it alone; H-DS-001's falsifier (0.5) does not fire and the structure gate (0.9) is not met. Next: B-sweep plus an object-cost-parity measurement. |
| **D-4** PROXY DISAGREEMENT | `W` and `U` in different bands | **inconclusive** on mechanism, but a *positive* cost-model finding: proxy choice determines the sign of the conclusion, establishing RT047-B1/H4 as measured defects. Next: repair the cost model — number the wall-faithfulness heuristic, build an operation count that charges table-build and per-candidate additions. |
| **D-5** GUARD FIRED | INADMISSIBLE, certificates < 100%, any capped attempt, amortization mismatch, short arm, undeclared code change, timeout/crash/exhaustion | Map **SUSPENDED**. Infrastructure/instrument signal, never a mathematical result. Scoped repair, then re-run under the same frozen map. |

D-1…D-4 partition the entire two-proxy outcome space (LOW/LOW, HIGH/HIGH,
MID/MID, and all six mixed-band combinations). There is no gap and therefore no
room for a post-hoc reading.

Also declared in the addendum: `PER_TARGET_CAP_SECONDS = 5.0` (Validator defect
D-3 — previously an undeclared hard-coded per-attempt cap), with its bias
direction stated (it truncates the slower **naive** arm first at larger
parameters and therefore biases R **downward**) and a suspension guard if any
arm records a capped attempt. RT047-B1's proxy-sensitivity disclosure is carried
into the reporting template as a property of the instrument, not of the write-up.

## RC-21 — one-cycle amendment cap

At most **one** amendment/review cycle for this control addendum. A REVISE at
`TASK-20260801-003` is a BATCH-021 non-execution failure for the control run;
there is no second cycle in this batch. A cycle-cap ruling on any further
request is assigned to a session that did **not** author `TASK-20260801-001`.
No Executor run without APPROVAL_DETERMINATION APPROVED at `TASK-20260801-004`.

## Forbidden in BATCH-021

- `S1_met`, `F1_met`, `structure_gate_passed` — under **every** branch
- `support` for H-DS-001; any movement of asymptotic promotion gates G1–G4
- any asymptotic, crypto-scale, or affected-scheme claim
- `reject_scoped`, and in particular reject_scoped-as-impossibility
- HEUR-DS-1 validation or refutation
- altering `H-IC-001` or `H-STR-002`
- touching FAEST or XEDN
- executing v1
- **running the live plant** — `plant_divisor` is 1.0 on every arm;
  `CTRL-RT025-PLANT-LIVE` stays UNDISCHARGED and RT047-CTRL-3 gates its repair
- `dominated_by: null` anywhere downstream
- editing `specification.v2.yaml`, `specification.v1-frozen-*`,
  `CTRL-RT025-UNPLANTED.yaml`, `v2_ctrl_unplanted.yaml`, `ds001_driver.py`,
  `ds001_ctrl_unplanted.py`, any BATCH-020 artifact, EV-DS-001/002/003, or any
  DEC record

## Budget

`campaign_budget.maximum_batches` is **50**; BATCH-021 is the **twenty-first**
batch. **No pause condition fires.** Stated explicitly rather than left implicit.
Goal status remains `active`.
