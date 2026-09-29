---
id: KN-FIND-f54a82
type: internal_finding
title: "An isolated LLL/GSO-preprocessing-step probe in fpylll is not evidence about the full BKZ tour it is used to characterize or validate a fix against"
tags: [fpylll, fplll, bkz, lll, numerical-stability, gso-row-expo, mpfr, instrument-design, methodology, cross-validation, ml-kem, negative-result, toy-scale]
confidence: derivation_via_direct_code_reproduction_by_one_session_from_two_independently_produced_raw_observations
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-3b9962, TASK-20260814-ffd791, TASK-20260814-a94ddf, TASK-20260814-fe02ff, TASK-20260814-87a572]
internal_refs: [EV-MLKEM-ef0261, DEC-20260814-4ac30a]
sibling_findings_narrowed: []
sibling_findings_note: "This entry does not narrow any prior finding in this goal; it is a distinct instrument-design/methodology lesson about testing numerical-stability fixes at the correct operation level, not a further measurement of any C1/C2 candidate or the fibre-constancy criteria KN-FIND-9d44b4/KN-FIND-7d098b address. internal_refs carries LEDGER records only, matching the shape those entries use."
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/archives/TASK-20260814-87a572/adjudication/ADJUDICATION.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/archives/TASK-20260814-87a572/adjudication/adjudicate_precision.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/archives/TASK-20260814-87a572/adjudication/adjudicate_wrapping.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/archives/TASK-20260814-87a572/adjudication/adjudicate_full_tour.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/archives/TASK-20260814-87a572/adjudication/adjudicate_d192.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe3_isolate_lll_step_no_strategies.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe5_precision_fix_at_cheapest_failing_d.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-a94ddf/probes/probe_root_cause_precision2.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-a94ddf/probes/probe_dimension_sweep.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe4_dimension_scan.py
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-a94ddf/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/red_team_report.md
added: '2026-08-14'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on
any FIPS 203 parameter set, on any attack cost, or on any cost model. Measured
only against `IntegerMatrix.random(d, "qary", k=d//2, q=3329)`, `fpylll` 0.6.4,
one host.

**THIS ENTRY DOES NOT CLAIM fpylll OR fplll IS BROKEN, AND IT DOES NOT CLAIM THE
FIX IT DESCRIBES IS CHEAP OR PRACTICAL AT ANY SCALE.** The real per-cell cost of
the fix remains completely unmeasured (§4) — that is a separate, still-open
question this entry does not touch.

The finding, in one sentence:

> In `fpylll` (>= 0.6.4), a probe that exercises only the isolated LLL/GSO
> preprocessing step (`GSO.Mat(...)` -> `LLL.Reduction(...)` -> `lll_obj()`, no
> `BKZ.Param`, no actual block-enumeration tour) is measurably, non-trivially
> more numerically permissive than the full BKZ tour
> (`BKZReduction.__call__` / `BKZ.reduction(A, par)` with real block
> enumeration) it is naturally reached for as a cheap stand-in when validating a
> fix or characterizing a numerical-stability boundary — and this recurred
> **twice, independently**, within one batch, diagnosing two structurally
> different questions.

## 1. What was measured, and how the pattern was found

`BATCH-3b9962`'s lead producer (`TASK-20260814-ffd791`) reported all 6 of
PREREG-8's own Stage-0 main-grid `(d, beta)` cells failing identically with
`fpylll.util.ReductionError('infinite loop in babai')`, and characterized this
as "a genuine, unfixable incompatibility... not resolved by the one alternative
precision setting that could be tested to a definite result [mpfr]."

Two independent reviews — the Validator and the Red Team, working blind to each
other — each probed this characterization further and reported **apparently
contradictory** results, **twice**:

- **The mpfr-fixability question.** The Red Team's `probe5` constructed an
  explicit, correctly-configured `GSO.Mat(A, float_type="mpfr")` with no
  `GSO.ROW_EXPO` flag and found the isolated LLL step **succeeds** in 0.004s on
  the exact failing instance. The Validator's `probe_root_cause_precision2.py`
  raised mpfr precision explicitly to 212 and 424 bits, WITH `GSO.ROW_EXPO`, and
  found the (wrapped, full-tour) construction **fails identically**.
- **The dimension-boundary question.** The Red Team's `probe4_dimension_scan.py`
  reported a boundary of d=192 (succeeds) / d=224 (fails). The Validator's
  `probe_dimension_sweep.py` reported a lower boundary, d<=184 (succeeds) /
  d>=192 (fails) — at the same fixed `beta=10`.

Both apparent contradictions were resolved the same way, by direct comparison
of the two probes' own source code followed by live re-execution of each
review's exact construction at the exact disputed point:

- Red Team's probes in both cases call **only** the isolated step —
  `GSO.Mat(A, flags=...)` -> `LLL.Reduction(...)` -> `lll_obj()` — with no
  `BKZ.Param` and no `bkz(par, tracer=True)` call anywhere.
- Validator's probes in both cases call the **full operation** —
  `BKZReduction(...)` wrapped around a full `bkz(par, tracer=True)` tour, or
  the native `BKZ.reduction(A, par)` free function with a real
  `BKZ.Param(block_size=..., ...)`.

Direct re-execution at the two exact disputed points confirms both reviews were
correct about the exact construction each one tested:

- At (d=256, beta=40): the isolated LLL step succeeds under mpfr regardless of
  `GSO.ROW_EXPO` (~0.004s both settings — `adjudicate_precision.py`,
  `adjudicate_wrapping.py`). The **full tour** with `GSO.ROW_EXPO=True` (the
  construction `stage0_feasibility.py`'s own `worker_main_cell()` actually
  produces from a raw `IntegerMatrix`) fails in 0.282s with the identical
  exception (`adjudicate_full_tour.py`); with `GSO.ROW_EXPO=False` it does not
  hit that immediate failure but also does not complete within 100s here or
  684s in the Red Team's own `probe6`.
- At d=192, beta=10: the isolated-LLL-step construction **completes** in
  0.0061s; the full native-BKZ-tour construction **fails**
  (`RuntimeError: Aborted`, the same underlying "infinite loop in babai"
  condition surfacing as an uncaught C++ abort) after 6.65s
  (`adjudicate_d192.py`).

## 2. Why this recurrence, not the single instance, is the finding

A single reconciled disagreement could be an anecdote about one probe's own
construction choice. **This recurred twice, independently, from two
structurally unrelated questions neither probe was designed to test against
the other** — one review pair was investigating whether precision fixes a
specific failing instance; the other was mapping a dimension boundary at a
fixed, cheap beta. Neither probe pairing was built with the other's own
question in mind. That the identical asymmetry (isolated step more permissive
than full tour) explains BOTH apparent contradictions, discovered
independently and resolved by the same two-step method (source comparison,
then live re-execution) each time, is what elevates this from a single
reconciled disagreement to a **generalizable methodological lesson**: reusable
well beyond this one batch, to any goal in this portfolio that tests a
proposed numerical fix or a numerical-stability boundary against a cheap
sub-step of an iterative reduction pipeline (`fpylll` or otherwise) rather
than its actual full operation.

The mechanism, so far as characterized (see §4 for what remains open): the
`GSO.ROW_EXPO` flag — which `BKZReduction` builds into its own internal GSO by
default when handed a raw `IntegerMatrix`, and which is documented incompatible
with `float_type="mpfr"` — is decisive only at the full-tour level. Both
settings of the flag succeed identically at the isolated-LLL-step and wrapped
`lll_obj()` levels; the divergence appears only once a real BKZ tour (repeated
internal basis updates, block enumeration) is actually run.

## 3. What this changes, and what it does not

**It changes no measured figure and not the fired termination branch.**
`T-PROJNOISE-NODATA` firing for `TASK-20260814-ffd791`'s own reported
observation (the default, `GSO.ROW_EXPO`-on construction, exactly as run) is
confirmed correct by both reviews and this reconciliation.

**It changes what the producer's own root-cause characterization is entitled
to claim.** "Not resolved by the one precision setting that could be tested"
is correct for the exact construction `stage0_feasibility.py` actually runs,
but incorrect as a general claim about `fpylll`/`fplll`'s own capability: an
ordinary, already-available construction change (drop `GSO.ROW_EXPO`; raise
mpfr precision explicitly) demonstrably avoids the immediate exception at the
isolated-LLL-preprocessing level, on the exact same failing instance.

**It does not establish that the fix is practical.** See §4.

## 4. What remains open

1. **The real per-cell cost of the corrected (mpfr, no-`ROW_EXPO`) full-tour
   construction is completely unmeasured.** Every attempt by every session
   (producer: never tried; Red Team's `probe6`/`probe2`; this entry's own
   `adjudicate_full_tour.py`) has been time-bounded and terminated before
   completion or error — none for longer than ~684s. Preliminary evidence is
   consistent with, but does not prove, a materially larger real cost than a
   double-precision-based estimate would assume.
2. **The underlying C++ mechanism is not identified.** No `fplll` C++ source
   was available in this environment to inspect directly, and no upstream
   issue-tracker search was performed to check whether this is an
   already-known, already-reported defect for `fpylll` 0.6.4 (confirmed the
   latest PyPI release by the Validator's own `ART-8`).
3. **Whether this generalizes beyond this one lattice family
   (`IntegerMatrix.random(d,"qary",k=d//2,q=3329)`) and this one `fpylll`
   version is untested.**

## 5. What a successor must do, and what it must not

1. **Before trusting an isolated-step probe's own result as a proxy for a full
   iterative-reduction operation, read the probe's own source code and confirm
   it actually invokes the full operation** (a real `BKZ.Param` + tour call,
   not just the preprocessing step) — a cheap, general diagnostic, costing
   seconds to apply, that would have caught both apparent contradictions in
   this batch before they were reported as contradictions at all.
2. **This is not a claim that isolated-step probes are useless** — they
   correctly and cheaply characterize the preprocessing step itself (as both
   reviews' own isolated-step results correctly did). It is a claim that their
   result must not be silently extrapolated to the full operation without
   testing the full operation directly.
3. A follow-up task re-measuring the corrected construction's real cost
   (§4.1) is named in `DEC-20260814-4ac30a`'s own `next_actions`; this entry
   does not perform or wait on that measurement.

## 6. Scope and limits — read before citing

1. **THE RAW OBSERVATIONS WERE INDEPENDENTLY PRODUCED.** The Validator and Red
   Team each built and ran their own probes blind to the other's write scope,
   on both the mpfr-fixability question and the dimension-boundary question.
2. **THE RECONCILIATION WAS NOT.** Both apparent contradictions were resolved
   by the SAME orchestrating session (not a fourth, independent reviewer)
   comparing the two probes' own source code and re-executing each
   construction directly. This is a genuine limitation on how independently
   the RECONCILIATION itself may be described, even though it does not
   undermine the raw, independently-produced observations the reconciliation
   explains.
3. **INDEPENDENCE IS PROCEDURAL — NEVER MODEL-LEVEL.** AGENTS.md rule 12 is
   UNMET AND UNWAIVED. The Validator, Red Team, and the reconciling
   orchestrating session all ran on the same model and the same host as the
   producer.
4. **THIS ENTRY MAKES NO CLAIM THAT THE FIX IS CHEAP, PRACTICAL, OR USABLE AT
   ANY SCALE THAT MATTERS.** See §4.1. That is a separate, still-open question.
5. **DERIVATIONS AND LIVE CODE EXECUTION, NOT THEOREMS.** Every claim in this
   entry traces to a specific script's recorded output at a specific
   (d, beta) or (d, beta, precision) instance, not a general proof about
   `fplll`'s own numerical behavior.
6. **IT ESTABLISHES NOTHING ABOUT ANY LATTICE, ML-KEM PARAMETER SET, OR C1/C2
   CANDIDATE.** `BATCH-3b9962` adjudicates no such proposition, and neither
   does this entry. `T-PROJNOISE-NODATA`'s own FORBIDS clause is honoured
   throughout.

## Identifier provenance

`KN-FIND-f54a82` was drawn as a random 6-hex token (matching this corpus's own
established `KN-FIND-<tok>` pattern; `tools/allocate_id.py` does not register
a `--next` type for `KN-*` records, so no scan-free minting path exists for
this record class) and then confirmed in **two scopes** by the orchestrating
session at the Coordinator's request (`DEC-20260814-4ac30a`'s own
`knowledge_promotion.promotion_note`): worktree `tools/allocate_id.py --check
KN-FIND-f54a82` (well-formed pattern not enforced for `KN-*`, 0 occurrences
across 6,810 identifier-bearing paths) **and** a cross-ref sweep of the 25
most-recently-updated remote branches (0 hits), matching the two-scope
discipline `KN-FIND-9b5df0`'s own "Identifier provenance" section documents
for this same class of record. The Coordinator that specified this entry's
content held no shell and claimed neither check as its own; both were
performed by the orchestrating session.

## Superseding relationship

This entry does not narrow any prior finding in this goal. **No prior entry is
edited and no `superseded_by` is set** on any of them. It stands as an
independent instrument-design/methodology lesson, cross-referenced from
`DEC-20260814-4ac30a`'s `knowledge_promotion` field.
