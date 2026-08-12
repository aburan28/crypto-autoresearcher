# GOAL-HQC-001 — BATCH-001 opening

- **Goal**: `GOAL-HQC-001` — *HQC: is the decoding-failure-rate model that
  carries IND-CCA correct under measurement?*
- **Question**: `RQ-HQC-001`
- **Opened**: 2026-08-02
- **Branch**: `claude/goal-target-hqc-launch-vndegi`
- **Base commit merged from `main`**: `76f555447a3134f4db0ff79632025e8d638a6837`
  (`git merge origin/main` reported *Already up to date* — the branch was
  created at that tip and carries no divergence.)
- **Owner**: coordinator

## 1. What this batch is, and what it is not

BATCH-001 is a **source-acquisition and convention-fixing batch**. It

- produces **no hypothesis** (`active_hypothesis_ids` stays empty),
- designs **no experiment**,
- runs **no decoding trial**, and
- asserts **nothing about HQC's security in either direction**.

It exists because `RQ-HQC-001.constraints` forbids designing an experiment
before the relevant primary sources are filed as `KN-LIT` entries, and because
`GOAL-HQC-001.next_action` names an ISD memory-charging convention that must be
shared with `GOAL-SDITH-001` rather than derived twice.

Nothing in this batch is admissible toward the AGENTS.md rule 13 closure
quorum. The claim-tier ceiling declared by `RQ-HQC-001` — **toy** — is
untouched.

## 2. Activation

`GOAL-HQC-001` was created 2026-07-29 at `status: draft` and never launched.
This batch transitions it to `status: active`.

**The activation is a user authorization recorded by the Coordinator, not a
self-grant.** The user's instruction this session was to launch a goal
targeting HQC; `GOAL-HQC-001` is the only goal record whose
`scheme_context.scheme` is `HQC`, so selection was unambiguous and no
disambiguation was required. Recorded in the goal's `status_value_history`.

Activation meets no completion criterion, approaches none, and moves no claim
tier.

## 3. Pre-batch corpus census (the HAWK lesson, applied before dispatch)

`GOAL-HAWK-001` BATCH-001 spent an executor task acquiring a source that was
**already in the corpus** as `KN-LIT-7592`, filed one day before that goal
asked for it, because the goal named the referent only as "the disclosed
attack" and cited no ID. That is a cheap, repeatable failure. This batch runs
the census **first**, in the opening, so the executor's handoff can name what
already exists and be scored on *upgrading* rather than *duplicating*.

Census performed 2026-08-02 over `knowledge/` (`grep -ril "hqc\|hamming
quasi"`) and `ledger/proposals/` (`grep -l "RQ-HQC-001"`):

| Record | Title (as filed) | `confidence` / `citation_verified` | Relevance to this goal |
|---|---|---|---|
| `KN-LIT-2141` | *A New Decryption Failure Attack against HQC* (Guo, Johansson) | `reported` / `read` | **Directly the DFR lane.** Record is weak: `year`, `venue`, `identifiers.*` and `url` are all `null`. |
| `KN-LIT-7565` | *Multilevel Amortized Gaussian Elimination in ISD: Applications to HQC and PCG* (Carrier, Hatey, Luzzi, Tillich, iacr:2026/1498) | `reported` / `web` | **Directly the ISD-baseline lane.** Abstract-level only. |
| `KN-LIT-1798` | *Optimizing Polynomial Multiplication and …* (HQC on Cortex-M4, iacr:2026/1450) | `reported` / `read` | Implementation, peripheral. |
| `KN-LIT-2083` | *A Holistic Approach Towards Side-Channel Secure Fixed-Weight Polynomial Sampling* | `reported` / `read` | Touches the fixed-weight sampler implicated in the HQC timing line. |
| `KN-LIT-3859` | *Fault-Injection Attacks against NIST's PQC Round KEM* | `reported` / `read` | FO-transform equality test; separate claim class. |
| `KN-LIT-2541` | *Anonymity of NIST PQC Round-3 KEMs* (Xagawa) | `reported` / `read` | Peripheral. |

**The HQC specification itself is absent from the corpus.** So is any primary
statement of the analytic decoding-failure-rate model. That absence — not the
absence of HQC material in general — is what gates this goal.

## 4. A defect in this goal's own `next_action`, found before dispatch

`GOAL-HQC-001.next_action` reads: *"Run `/propose-ideas RQ-HQC-001`."*

**That instruction is already partly discharged and must not be re-run
blindly.** `ledger/proposals/IDEA-20260801-011.yaml` exists, is bound to
`question_id: RQ-HQC-001`, and is exactly the DFR-measurement proposal the
goal calls "the distinctive lane". It was filed 2026-08-01, three days after
the goal record was written.

Worse for the goal as written, `IDEA-20260801-011` **is not executable as
specified**. Its `minimal_test.design` says *"compare empirical failure counts
to the model"* and its controls say *"Recompute the model's prediction
independently"* — but no one in this program has read the model. Its
`novelty_screen.corpus_paths_grepped` lists `knowledge/literature` and
`ledger/proposals` and concludes only that this program has not made the
measurement; it screens for internal duplication, not against the external
literature, and `KN-LIT-2141` — a decryption-failure attack on HQC already in
the corpus — is not cited by it.

This is recorded here rather than repaired here. The proposal record is
immutable; if it needs correction it is superseded by a Coordinator decision,
not edited.

The goal's `next_action` is superseded at activation — with the prior text
preserved in `next_action_history`, never overwritten — because the goal cannot
simultaneously say "run `/propose-ideas`" while this batch deliberately does
not. But **the disposition of the section 4 finding itself is left open on
purpose.** Red Team (`TASK-20260802-73a352`) is directed to challenge both
halves of it against the actual records, because the equivalent Coordinator
claim in `GOAL-HAWK-001` BATCH-001 was itself found to be an overread by that
batch's red team. The formal disposition is deferred to the BATCH-001 ledger
archive, which will have that challenge in hand. The second clause of the
original `next_action` — coordinate the ISD baseline with `GOAL-SDITH-001` — is
**not** superseded; it is carried forward as `TASK-20260802-0100a5`.

**Consequence for this batch:** `/propose-ideas` is *not* dispatched.
Re-running ideation before the model is in hand would generate more proposals
with the same unmet dependency.

## 5. Batch composition

Two producers with disjoint write scopes, one snapshot archive, two independent
reviews, one ledger archive. `max_concurrent: 3`; at most two producers and two
reviewers ever run at once.

| Task | Role | Purpose |
|---|---|---|
| `TASK-20260802-6344ed` | executor | Acquire the HQC specification and the primary DFR-analysis literature; transcribe the analytic DFR model and every numbered assumption verbatim; upgrade rather than duplicate the six census records above. |
| `TASK-20260802-0100a5` | executor | Derive the shared **memory-charged ISD costing convention** that `GOAL-HQC-001` and `GOAL-SDITH-001` must both bind to, from committed program state. Scheme-independent; produces no HQC parameter numbers. |
| `TASK-20260802-a3dc0a` | coordinator | Snapshot archive of both producers' exact artifacts. Runs alone. |
| `TASK-20260802-b8d69f` | validator | Receipt integrity, transcription fidelity, provenance level. |
| `TASK-20260802-73a352` | red-team | Attack the batch's own framing, §4 above, and the premature-closure risk. |
| `TASK-20260802-a157ad` | coordinator | Ledger archive: `EV-HQC-9906b9`, `DEC-20260802-344883`, goal checkpoint. Runs alone. |

The opening artifacts (this file, `dispatch_queue.json`, and the activated goal
record) are committed **outside** the queue's archive mechanism. This is
deliberate and follows the `GOAL-HAWK-001` BATCH-001 amendment:
`research_dispatch.py` requires `archive.source_task_ids` to be nonempty and
forbids an archive claiming another archive, so an opening snapshot with no
producer task is not expressible as a queue archive. Modelling it as a queue
task and then amending it — which is what HAWK had to do — is avoided by not
modelling it as one.

## 6. Two producers, and why the second is not filler

`TASK-20260802-0100a5` is not there to fill a concurrency slot. `GOAL-HQC-001`
and `GOAL-SDITH-001` are the program's two code-based goals and both must
produce a memory-charged ISD baseline. Their goal records were written on the
same day with the same completion criterion wording, and `GOAL-HQC-001`'s own
`next_action` warns that the two "do not derive two different memory-charging
conventions". Deriving the convention once, before either goal has parameters
to plug into it, is the cheapest possible ordering. It is also the lane where
this program's standing failure mode lives — `GOAL-SDITH-001.next_action` says
so outright: *"this program's standing failure mode is a partial win that dies
once memory and preprocessing are charged, and ISD is the canonical place that
happens."*

It is scheme-independent by construction, so it does not depend on
`TASK-20260802-6344ed` succeeding, and the two can run concurrently. If the
source gate blocks the first producer entirely, the batch still returns a
usable artifact.

## 7. Model policy and the fallback that applies to every task here

`orchestration/model-policies.yaml` routes coordinator work to
`coordinator-orchestration-code`, executor work to `executor-implementation`,
and validator/red-team work to `review-adversarial` (which requires `xhigh`
reasoning and an independent session).

**Under this harness none of those policy aliases resolve.** `CLAUDE.md`
records the reason: subagent frontmatter in `.claude/agents/` supports only
Claude models, so all subagents run `model: inherit`. Every task in this batch
therefore runs on the session model, `claude-opus-5`, with
`fallback_used: true` against its requested policy. This is recorded per task
in the queue's `handoff.inference` block and is not concealed.

Two consequences are stated now rather than discovered later:

1. The validator and red-team sessions are **independent sessions but not
   independent models**. They are separate subagent invocations that did not
   produce the artifact they review, which is what `docs/dynamic-subagent-dispatch.md`
   requires of a review; they are not three distinct backends.
2. It follows that **this batch cannot contribute to a closure quorum**, which
   requires pairwise-distinct `resolved_model_id`. Under this harness that is
   the common case (`CLAUDE.md` rule 8 says so explicitly). No attestation is
   recorded here, and none may be synthesized later from this batch's reviews.

## 8. Repository state at open

Recorded so that no defect this batch does not own is later attributed to it.

- `tools/validate_ledger.py` at `76f55544`: `FAIL: 183 new validation error(s)`
  above the 1138-line grandfathered baseline. **All 183 pre-date this batch**;
  the working tree was clean when they were measured. None names `GOAL-HQC-001`,
  `RQ-HQC-001`, `IDEA-20260801-011`, or any HQC record.
- `tools/check_merge_hygiene.py` at `76f55544`: `FAIL: 6 unparseable records`,
  all under `coordination/goals/GOAL-AES-003/batches/BATCH-002/`. Also
  pre-existing and unrelated.

BATCH-001's obligation is not to repair these. It is not to add to them.

## 9. Completion gate for the batch as a whole

BATCH-001 closes when the ledger archive has committed `EV-HQC-9906b9`,
`DEC-20260802-344883`, both review reports, and a `GOAL-HQC-001` checkpoint
carrying exactly one `next_action` — and that commit's declared paths equal its
committed paths under `tools/research_dispatch.py` verification.

A source gate that blocks acquisition is an **honest scoped outcome** recorded
against `pause_conditions[1]`, not a failure of the batch and not evidence
about HQC. AGENTS.md rule 5 applies unchanged.
