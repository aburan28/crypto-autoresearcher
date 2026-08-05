# BATCH-70a55a scope decision — GOAL-SSI-001 — **DECLINED (not opened)**

Candidate: `ledger/proposals/IDEA-20260803-82b2b7.yaml` — "trace-collision test for
QM-STOPPING".

**Disposition: DECLINE.** BATCH-70a55a is **not opened**. No producer, review, or
archive task is dispatched. No `batch.yaml`, no `dispatch_queue.json`, no task card,
and no handoff record is written under this batch identifier. This file is the whole
of the batch.

This is a **pre-compute falsification decline under `docs/inventor-protocol.md`
section 8 / `knowledge/techniques/KN-TECH-080.md`**, not a saturation decline. The
proposal's `proof_search_map` is audited below and two of its four audits fail against
committed artifacts. Section 8 binds the Coordinator specifically: *"the Coordinator
does not approve implementation or expensive experiments without one [a passing
`proof_search_map`]"*, and *"a failed audit is often the useful result."* That is what
happened here.

---

## 1. What the proposal asserts as its bottleneck

`IDEA-20260803-82b2b7.proof_search_map.bottleneck`:

> Whether the stopping event is invariant under the FC0 trace projection. The exact
> bottleneck claim is that this single measurability question is what QM-STOPPING has
> been failing on for eight batches, and that every intervening MEMORY-MAP artifact is
> orthogonal to it.

Everything downstream in the proposal — the collision search, the planted lossy-π'
control, the two "terminal" dispositions — rests on that identification of the
blocker. If the identification is wrong, a crisp answer from the instrument is worse
than no answer, because it produces a citable `OBSTRUCTION_NAMED` string that later
readers will attach to QM-STOPPING.

## 2. The committed record says the blocker is something else

### 2.1 The QM-STOPPING FAIL is seven instantiation rows, not one measurability row

`coordination/goals/GOAL-SSI-001/batches/BATCH-018/tasks/TASK-20260730-043/stopping_law_artifact.md`
§4 records the control's FAIL as a table of seven obligations. Six are
`not_instantiated` and one is `rejected_as_insufficient`:

| Obligation (§4, verbatim) | Status | Stated reason |
|---|---|---|
| Source-compatible τ covering discards/retries/recovery/residual | `not_instantiated` | "Schema exists; transition kernel, independence, uniform success bound absent" |
| Verify-relative terminal σ-algebra | `not_instantiated` | "`Verify(x,k')` absent in pinned code; recovery_spec only" |
| `E Σ Q_k < ∞` under τ | `not_instantiated` | "Q̃_total ≠ required random sum" |
| `E Σ S_k < ∞` under τ | `not_instantiated` | "Eq. (4.1) typical/essential estimate only" |
| `E Σ P_k < ∞` under τ | `not_instantiated` | "Postprocessing transitions uncosted jointly" |
| `E[Σ C_k + H] < ∞` under τ | `not_instantiated` | "Classical recovery/tail/Verify uninstantiated" |
| ttm-v2 one-retry horizon as global τ | `rejected_as_insufficient` | "Local panel horizon ≠ end-to-end law" |

**Not one row is "the stopping event is not measurable with respect to an FC0 trace
projection."** Six are absences of source material; the seventh is a scope refusal.
§1.1 requires τ on *"a single source-compatible probability space and global attempt
timeline"* with a *"Verify-relative"* terminal σ-algebra — the procedure's own
filtration, not an FC0 interface package's observable image. The proposal conflates
"the FC0 extension package" with "the observable process generating the filtration."

The one row that is genuinely σ-algebraic — "Verify-relative terminal σ-algebra" —
carries the reason *"`Verify(x,k')` absent in pinned code."* That is an **absence**,
not an obstruction. A trace-collision witness cannot convert an absence into a
non-existence proof.

### 2.2 The lane's own evidence has already classified the gap, in these words

`ledger/evidence/EV-SSI-041.yaml`:

> OUTCOME-D ∀-hosts remains undischarged (**availability/host gap, not object
> obstruction**). QM-STOPPING lane paused_pending_revisit with concrete REV-1
> (admissible CollimationSieve pin) and REV-2 (host-independent collision/mixing
> result meeting OUTCOME-R).

The proposal seeks an **object obstruction**. The committed evidence states the gap is
**availability**. This single sentence is the strongest citation for this decline, and
it predates the proposal by two batches.

### 2.3 The projection π the proposal calls "already frozen" is not in the freeze

`IDEA-20260803-82b2b7.claim`: *"Let pi be the projection from executions of the pinned
CollimationSieve@6f9188e4 host to the FC0 observable trace, **as already frozen in
FC0-EXT-PKG-SSI-001** and instantiated by the BATCH-022 scaffold."*

`coordination/goals/GOAL-SSI-001/batches/BATCH-021/tasks/TASK-20260730-055/fc0_extension_package.yaml`
does not contain such a map. Its `surfaces_frozen` list is interface signatures —
`Verify(x, k_prime)`, `W/R/B/M_tail birth/death/cleanup`, and
`stage_live_sets_and_F_star_error_channels_as_spec_checklists`. It defines no execution
model, no trace, and no projection. It states of itself:

> This package is an in-repo specification surface, not an external repository pin and
> not a CollimationSieve patch.

and, in `retained_prior_certificates.collimation_sieve_negative_control.constraint`:

> Do not invent Verify(x,k') or W/R/B/M_tail lifetime APIs on this pin. This package is
> a separate in-repo interface, **not a CollimationSieve API surface.**

There is therefore no map from host executions to anything, and constructing one is
exactly the CollimationSieve API invention every decision from BATCH-019 onward
prohibits and which the proposal itself forswears in its first `assumptions` entry.

The proposal anticipates a weaker version of this as falsification condition F3 ("π is
not unambiguously determined by the freeze"). The committed state is stronger than F3:
π is **absent**, not ambiguous. Under the proposal's own step (1) — *"if pi is not
unambiguously determined, STOP and report the freeze defect"* — the batch's modal
outcome is an immediate stop. That outcome is already established here by reading two
committed files, at zero dispatch cost.

## 3. `proof_search_map` audit (KN-TECH-080 section 8)

| Audit | Verdict | Basis |
|---|---|---|
| Exact bottleneck identification | **FAIL** | §2.1, §2.2 above. The named bottleneck is not the recorded blocker. |
| Baseline reproduction | **PASS, but powerless** | BATCH-013's committed result is real and reproducible — `coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/analyzer_results.yaml` records `zero_progress_count: 16`, 36 parameter rows, 1014 ordered reachable child-vector pairs, `min positive p = 1/4`, representative witness `{n:3, ell:2, s:1, theta:"3/4", v1:[0,1], v2:[0,2]}`. But BATCH-013 searched a **reachable-state progress model** for `p = 0` states. It is not a projection-collision search. Reproducing it exercises enumeration machinery only and has **no power over the collision predicate**. The proposal's claim that it is "a collision search over a finite model" overstates it. |
| Quantifier order | **PASS** | Correctly stated as `∃ (e1,e2)` with π fixed before the search, and the frozen-π guard is the right defence. |
| Method ceiling / nearby-object control | **UNCONSTRUCTIBLE** | The planted lossy-π' control — the proposal's own hard blocker and the thing that gives a negative any meaning — cannot be constructed at all when π is absent (§2.3). Without it, by the proposal's own F1, *"neither primary outcome may be read."* |

Two of four audits fail or cannot run. Under section 8 this batch is not approved for
implementation.

## 4. The questions the dispatching session asked, answered directly

**Q: Does this constitute the "NEW committed structure" whose absence the recorded
`next_action` gives as the reason for not launching?**

**No.** The `next_action`'s clause reads *"if not reachable and no NEW committed
structure exists to probe."* The structure in question is structure **to probe for an
admissible pin** — host material, source, a `Verify` body, a pin. PR #141 / commit
`8c0ca209` added proposal records and an analysis. A new committed *record* is not new
committed *structure* in that sense: `BATCH-020 no_admissible_pin` is unchanged, the
`CollimationSieve@6f9188e4` pin is unchanged, and no source artifact bearing on REV-1
was added. The stated reason for not launching still holds, and it holds against this
proposal a fortiori, since this proposal does not even attempt REV-1.

**Q: Does it reopen the PAUSED QM-STOPPING lane in a prohibited way, or does it attack
the REV-1 gate from a direction the pause does not cover?**

**Both partly, and the answer does not carry the decision.** Being strict, as asked:

- It does **not** re-queue the lane's obligation programme in the narrow sense. It
  seeks no pin (REV-1) and claims no host-independent mixing result (REV-2). Its
  question is logically prior to and independent of both gates. On that construction it
  is not a prohibited re-queue.
- It **does** target QM-STOPPING's disposition. `predictions[lane_disposition_emitted]`
  states *"'Retain FAIL' IS NOT AN ADMISSIBLE OUTCOME OF THIS BATCH"*, and `claim`
  states the batch *"RETIRES THE FAIL RETENTION either way."* The standing prohibition
  is to **retain** QM-STOPPING FAIL. A batch whose design makes retention structurally
  unavailable is, in the sense that matters, a reopening — and it is in direct verbal
  conflict with a prohibition I am required to carry forward verbatim.

Had the bottleneck audit passed, that conflict would be repairable in a task card (the
batch produces a *candidate* artifact; only a later Coordinator decision could retire
anything). It is **not** the ground of this decline. The ground is §2 and §3.

**A standing concern, recorded rather than resolved.** A pause whose exit conditions
are REV-1 (an admissible pin, recorded absent at BATCH-020 and estimated unreachable by
the goal's own `next_action`) and REV-2 (a host-independent mixing result the lane has
no route to) has no reachable exit **in either direction** — it can neither be lifted
nor honestly closed. Under AGENTS.md rule 9 a deprioritization must carry a concrete
successor or revisit condition; under `docs/inventor-protocol.md` section 4 a closure
needs a named obstruction, an argument, and forward guidance. A permanently
unreachable pause satisfies neither, and is exactly the "unbounded non-closure" the
BATCH-039 red team named and `analysis/SSI-ECDLP-SYNTHESIS-20260803.md` §2 documents.
**This decline does not dispute that pathology.** It disputes only the fitness of this
instrument for it. The successor in §6 is aimed at the pathology directly.

## 5. Claim ceiling (binding on anything that cites this file)

`toy` / `control`. No breakthrough, closure, novelty, SOTA, QUERY_MEMORY-clearance,
`PIN_COMPLETE`, or completion claim is authorized. Pollard rho remains the ECDLP
baseline and ordinary `sota_delta` is zero. `dominated_by`: not applicable — no attack,
no Pareto point, no cost claim; written explicitly rather than left null.

## 6. Rule-9 record

**Evidence cited.** `ledger/goals/GOAL-SSI-001/goal.yaml` (`next_action`);
`coordination/goals/GOAL-SSI-001/batches/BATCH-018/tasks/TASK-20260730-043/stopping_law_artifact.md`
§§1.1, 4, 5; `ledger/evidence/EV-SSI-041.yaml`; `ledger/evidence/EV-SSI-042.yaml`;
`coordination/goals/GOAL-SSI-001/batches/BATCH-021/tasks/TASK-20260730-055/fc0_extension_package.yaml`;
`coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/analyzer_results.yaml`;
`coordination/goals/GOAL-SSI-001/batches/BATCH-022/tasks/TASK-20260730-059/scaffold/types.py`;
`ledger/proposals/IDEA-20260803-82b2b7.yaml`;
`analysis/SSI-ECDLP-SYNTHESIS-20260803.md` §2; `docs/inventor-protocol.md` §§4, 8.

**Budget.** Zero consumed. No Executor, Validator, or Red Team session dispatched. The
decline cost one Coordinator read of two committed artifacts, which is the intended
cost of a section-8 pre-compute audit.

**Test boundary.** This decline is scoped to **IDEA-20260803-82b2b7 as written**, at
the committed state of `FC0-EXT-PKG-SSI-001`, `BATCH-013`, `BATCH-018`, and
`BATCH-022`. It says nothing about CSIDH, nothing about the collimation sieve, nothing
about whether a stopping law exists, and nothing about `KN-OPEN-014`, which remains
open and is not narrowed.

**Ranking against the alternatives not picked** (rule 9 requires the comparison):

1. **(chosen) Decline both candidates; open no batch; name the successor in this
   record.** Highest expected information per unit budget: the section-8 audit already
   produced the decision-relevant fact (the blocker is availability, not object
   obstruction), and it produced it for free.
2. **Launch the standing BATCH-043 pin-seeking / host-admissibility re-probe.** Ranked
   second. Still declined, on the goal's own recorded and unretracted ground —
   *"uncertainty reduction from a re-probe is low absent new committed structure"* —
   which §4 confirms is unchanged by PR #141. It is ranked above option 3 because it at
   least targets REV-1, which is the actual gate.
3. **Launch IDEA-20260803-82b2b7 as BATCH-70a55a.** Ranked last. Its design virtues are
   real — a hard-blocker positive control evaluated before the primary search, a
   known-answer reproduction gate, and a disposition set that makes an eighth
   non-discriminating CONFIRM unavailable. Those virtues are wasted on a
   misidentified target, and the downside is asymmetric: a crisp `OBSTRUCTION_NAMED`
   emitted against a scaffold this programme built would be an overclaim vector with a
   long half-life, attached to a blocker whose committed diagnosis is source
   unavailability. Catching that at the approval gate is what section 8 exists for.

**Remaining uncertainty.**

- Whether *any* QM-STOPPING obligation row is object-obstructed rather than
  source-absent has never been adjudicated row by row. §2.1 reads the reasons as
  stated; it is not a proof that no row hides an obstruction.
- Whether REV-1 or REV-2 is reachable from any obtainable artifact is unadjudicated.
  `BATCH-020 no_admissible_pin` is a negative on one search, not a proof of
  unreachability.
- The proposal's underlying observation — that eight-plus batches retained a FAIL with
  no named obstruction — stands unrefuted by this decline.

**Concrete successor (named, not approved here).** A bounded, zero-compute
**QM-STOPPING premise-and-exit audit**, routed through `/propose-ideas` on `RQ-SSI-001`
so that it acquires an `IDEA-*` record, a novelty screen, and its own
`proof_search_map` before any Coordinator approval. Its deliverable:

1. Each of the seven `stopping_law_artifact.md` §4 rows classified as
   `source_absent | object_obstructed | undetermined`, with the exact committed
   citation for each classification.
2. For every `source_absent` row, the exact missing source artifact named.
3. An explicit statement of whether **any** row is `object_obstructed` — the only
   class a zero-compute search could ever close.
4. A reachability verdict on REV-1 and REV-2: is there any committed or obtainable
   artifact that could meet either, or are they unreachable — in which case the lane's
   honest disposition is a scoped **closure at budget** under inventor-protocol
   section 4, with the obstruction named as *source unavailability of the pinned
   host*, an argument, and `KN-OPEN-014` named as what remains open.

This is the batch that can actually terminate the lane, it invents no host API, it
iterates no width, and it constructs no τ.

**Revisit condition for IDEA-20260803-82b2b7 specifically.** Reconsider if **either**
of the following becomes true and is committed:

- (R-A) A committed artifact defines an execution model and an observable projection π
  on it, together with the stopping event `S` as a subset of that model — i.e. the
  object the proposal presumes exists is actually frozen. Then the collision search is
  well posed *within that model*, and its ceiling is restated to that model.
- (R-B) The §6 successor audit classifies at least one QM-STOPPING §4 row as
  `object_obstructed`. Then a measurability instrument has a target, and this proposal
  is the natural first candidate for it.

## 7. Standing prohibitions — carried forward verbatim, unchanged by this decline

Quoted exactly from `ledger/goals/GOAL-SSI-001/goal.yaml` `next_action`:

> Do NOT reopen paused QM-STOPPING while REV-1/REV-2 unmet; do NOT run another
> zero-compute QM-ERROR tightening pass expecting obligation movement; do NOT iterate
> toy peak-byte width; do NOT attempt fake-τ gate B. Retain
> FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED, QM-STOPPING FAIL (lane paused),
> QM-MEMORY-MAP numeric_composition_operator_protocol_toy_partial, and BATCH-020
> no_admissible_pin.

and, from the same field, binding on any BATCH-043-class successor:

> bounded, zero curve/isogeny/quantum compute, no EXP-SSI-001 [...] that does NOT
> invent host APIs

All of the above remain in force. This decline changes **no** status: QM-STOPPING
remains `control_result: FAIL` with the lane `paused_pending_revisit` and REV-1/REV-2
unmet; QM-ERROR remains
`f_union_ledger_partial_spec_internal_reverse_inclusion_scoped` with REV-E1/E2/E3 open;
QM-MEMORY-MAP remains `numeric_composition_operator_protocol_toy_partial`;
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` is retained; the
`CollimationSieve@6f9188e4` pin is untouched and the BATCH-022 scaffold is unmodified.

## 8. Identifier and archival hygiene

**Unconsumed identifiers.** The following were pre-allocated to this batch and are
**consumed by no record**. No `TASK-*` handoff, task card, or queue entry exists for
any of them:

`TASK-20260805-16603c`, `TASK-20260805-657c61`, `TASK-20260805-f8cdb3`,
`TASK-20260805-822b89`, `TASK-20260805-450937`.

Per AGENTS.md rule 14 identifiers are never reused. A successor batch should mint its
own with `python3 tools/allocate_id.py --next task --date <YYYYMMDD>` and `--check`
before use rather than adopting these.

**Goal record untouched.** `ledger/goals/GOAL-SSI-001/goal.yaml` is **not** edited by
this task, by explicit constraint. `current_batch_id` remains `BATCH-042` and the
goal's single `next_action` is preserved unchanged. No checkpoint shard is written.
This decline creates no second next action.

**Archival ownership of this file.** This file is a coordination record, not evidence.
It is staged by the launching session as ordinary batch-scoping scaffolding; it carries
no archive receipt and asserts no commit. Its promotion to a
`ledger/decisions/DEC-20260805-0e1c91.yaml` record — with a token minted by
`tools/allocate_id.py --next decision --date 20260805` and `--check`ed, which this
session cannot do (no shell) and must not fabricate — is **owed to the next
GOAL-SSI-001 ledger archive**. Until then this decision is durable as a reviewable
coordination artifact and is **not** an official ledger transition.

---

```yaml
coordinator_decision:
  id: DEC-20260805-0e1c91              # ledger/decisions/DEC-20260805-0e1c91.yaml, owed to the
                                # next GOAL-SSI-001 ledger archive. Not minted here:
                                # this session has no shell, cannot run
                                # tools/allocate_id.py --check, and will not fabricate
                                # an identifier (AGENTS.md rules 5 and 14).
  recorded_at: '2026-08-05'
  decided_by: coordinator
  goal_id: GOAL-SSI-001
  question_id: RQ-SSI-001
  subject: IDEA-20260803-82b2b7
  proposed_batch_id: BATCH-70a55a
  decision: pause
  disposition: decline_do_not_open
  rationale: >-
    Pre-compute proof_search_map audit under docs/inventor-protocol.md section 8 /
    KN-TECH-080 fails on two of four audits. (1) BOTTLENECK MISIDENTIFIED: the proposal
    names "whether the stopping event is invariant under the FC0 trace projection" as
    what QM-STOPPING has been failing on. The committed control artifact records the
    FAIL as seven obligation rows, six not_instantiated for absence of source material
    and one rejected_as_insufficient; none is a measurability row. EV-SSI-041 already
    classifies the gap in terms: "availability/host gap, not object obstruction". The
    proposal seeks an object obstruction where the committed evidence says there is an
    availability gap. (2) NEARBY-OBJECT CONTROL UNCONSTRUCTIBLE: FC0-EXT-PKG-SSI-001
    freezes interface signatures and declares itself "not a CollimationSieve API
    surface"; it defines no execution model and no projection pi. The planted lossy-pi'
    control is the proposal's own hard blocker and cannot be built without inventing a
    host API, which every decision from BATCH-019 onward prohibits and which the
    proposal itself forswears. Under the proposal's own F3 the modal outcome is an
    immediate stop, which this audit has already established at zero dispatch cost.
    Separately, the proposal's lane_disposition_emitted prediction ("Retain FAIL IS NOT
    AN ADMISSIBLE OUTCOME") is in direct verbal conflict with the standing prohibition
    to retain QM-STOPPING FAIL; that conflict is repairable in a task card and is NOT
    the ground of this decline.
  evidence_refs:
  - ledger/goals/GOAL-SSI-001/goal.yaml
  - coordination/goals/GOAL-SSI-001/batches/BATCH-018/tasks/TASK-20260730-043/stopping_law_artifact.md
  - ledger/evidence/EV-SSI-041.yaml
  - ledger/evidence/EV-SSI-042.yaml
  - coordination/goals/GOAL-SSI-001/batches/BATCH-021/tasks/TASK-20260730-055/fc0_extension_package.yaml
  - coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/analyzer_results.yaml
  - coordination/goals/GOAL-SSI-001/batches/BATCH-022/tasks/TASK-20260730-059/scaffold/types.py
  - ledger/proposals/IDEA-20260803-82b2b7.yaml
  - analysis/SSI-ECDLP-SYNTHESIS-20260803.md
  status_changes: []
  hypothesis_status_changes: []
  experiment_approvals: []
  claim_ceiling: toy_control
  knowledge_promotion:
    promoted: false
    not_warranted_reason: >-
      No evidence record was produced and no experiment ran. A decline on a
      pre-compute design audit is not replicated or strong evidence and promotes no
      KN-FIND. The reading of stopping_law_artifact.md section 4 that grounds this
      decline is a Coordinator reading of one committed artifact; it becomes
      promotable only if the section 6 successor audit adjudicates the seven rows
      independently and is reviewed.
  dominated_by: >-
    Not applicable - no attack, no Pareto point, no cost claim. Written explicitly
    rather than left null.
  sota_delta: >-
    Zero on every cryptanalytic axis. Pollard rho remains the ECDLP baseline and no
    supersingular-isogeny cost claim is made or moved.
  next_actions:
  - >-
    DO NOT open BATCH-70a55a. GOAL-SSI-001 capacity remains intentionally unfilled;
    current_batch_id stays BATCH-042 and the goal's single next_action is preserved
    unchanged by this task.
  - >-
    Route the section 6 QM-STOPPING premise-and-exit audit to /propose-ideas on
    RQ-SSI-001 so it acquires an IDEA record, a novelty screen, and its own
    proof_search_map before any Coordinator approval. Its deliverable is a row-by-row
    source_absent | object_obstructed | undetermined classification of the seven
    stopping_law_artifact.md section 4 obligations plus a reachability verdict on
    REV-1 and REV-2.
  - >-
    Promote this decision to ledger/decisions/DEC-20260805-0e1c91.yaml at the next
    GOAL-SSI-001 ledger archive, minting the token with tools/allocate_id.py and
    --check. Until then it is a coordination record and not an official transition.
  - >-
    Reconsider IDEA-20260803-82b2b7 only on revisit condition R-A (a committed
    artifact defines an execution model, a projection pi, and S as a subset of it) or
    R-B (the successor audit classifies at least one section 4 row as
    object_obstructed).
  inference:
    requested_policy: coordinator-orchestration-code
    resolved_model_id: claude-opus-5
    reasoning_effort: null
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness cannot resolve the policy aliases in
      orchestration/model-policies.yaml; per-role policy selection under this runtime
      is process-level. Recorded, never silently substituted (AGENTS.md rule 11).
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >-
      No adapter probe receipt exists for this session; no
      `python3 -m orchestration.adapter doctor --probe` was run.
```
