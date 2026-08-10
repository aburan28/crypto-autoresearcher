---
id: KN-FIND-e87720
type: internal_finding
title: "KN-FIND-4e7a92 and KN-FIND-d1c853 narrowed: neither is the entry that was scheduled, and only their L5 alpha measurement is supported by committed evidence"
tags: [correction, narrowing, supersession, corpus-hygiene, wesolowski, supersingular-isogeny, p13, l5, alpha, fc-4, heuristic-1, unvalidated, open-item, toy-scale]
confidence: unverified
evidence_level: provenance_review_of_two_committed_corpus_entries
proof_status: not_applicable
proof_status_note: >-
  This entry makes no mathematical claim of its own. It is a provenance and
  scope narrowing over two committed entries, so there is no proposition here
  for a certificate or a derivation to back. The one measurement it leaves
  citable carries its own basis on EV-WESO-556063 (`empirical_only`).
proof_refs: []
internal_refs:
  - H-WESO-001
  - EV-WESO-556063
  - EV-WESO-b6ceff
  - DEC-20260802-48c72c
  - DEC-20260804-e19a65
  - DEC-20260809-a2f829
  - TASK-20260809-4119f6
narrows:
  - KN-FIND-4e7a92
  - KN-FIND-d1c853
source_goal: GOAL-P13-001
source_batch: BATCH-403f13
source_evidence: EV-WESO-556063
source_decision: DEC-20260809-a2f829
added: '2026-08-09'
superseded_by: null
---

## What this entry is, and what it is not

`KN-FIND-4e7a92` and `KN-FIND-d1c853` were added to this corpus on 2026-08-04
by the BATCH-403f13 archive attempt, in commit
`133f7d47b93b96ce0a3ffc3f4a38b92ae794fd68`. **Both remain committed,
immutable, and unedited** — AGENTS.md rule 4 forbids rewriting them, and
`DEC-20260809-a2f829` supersedes on the merits rather than by edit. This entry
does the only thing available: it **narrows what may be cited from them.**

**This entry authors no replacement mathematics.** It does not restate, repair,
correct or re-derive the cost formula in `KN-FIND-4e7a92` or the walk-length
relation in `KN-FIND-d1c853`. Where their content is not supported, this entry
says so and stops.

## 1. Neither entry is the entry that was scheduled

`DEC-20260802-48c72c.knowledge_promotion` **fixed the content of this
promotion slot in advance**, on 2026-08-02, before any BATCH-403f13 datum
existed. The scheduled durable claim was the **estimator lemma and the
intercept/slope pairing rule** —

> An intercept is only meaningful paired with the slope of the same fit of the
> same series over the same window; a slope-only calibration law reports ZERO
> overhead for an object carrying a large constant one

— with two named instances (the C-NULL counterexample, where the slope-only
law misses by up to `12.605090` bits; and the A-3 absorption, which converts a
2.4-bit unpaired excursion into a 1.007-bit correctly-paired one),
`proof_status: derivation`, the same `proof_refs` as `EV-PEC-857664`, and
**explicitly not any `c` value**.

What shipped instead was a cost-model formula in `KN-FIND-4e7a92` and a
walk-length relation in `KN-FIND-d1c853`. **The scheduled entry was therefore
never shipped**, and this was its third consecutive non-delivery. It ships now
as `KN-FIND-9ee5ed`, promoted by `DEC-20260809-a2f829`.

Consequence for readers: **neither `KN-FIND-4e7a92` nor `KN-FIND-d1c853`
discharges, partially discharges, or is a variant of, the
`DEC-20260802-48c72c` promotion obligation.** They are separate entries that
happened to occupy its slot.

## 2. The reused term: "pairing rule" names two different objects

`KN-FIND-d1c853` is titled a "Heuristic-1 pairing rule" and states
`N_pairs ~ exp(H_1 * n_walk)` — a relation between **walk length and expected
smooth-norm pair count**.

The **scheduled** pairing rule is an **estimator discipline**: an intercept
paired with the slope of the same fit of the same series over the same window
(`KN-FIND-9ee5ed`).

**These are unrelated objects sharing a phrase.** One is a probabilistic
relation about isogeny walks; the other is a rule for reading a log-log
regression. A corpus in which one phrase denotes two unrelated things will be
miscited, so the collision is named here explicitly and in `KN-FIND-9ee5ed`.
Any citation of "the pairing rule" in this programme must name which entry it
means.

## 3. What may still be cited from these two entries

Exactly one thing, and it is a real measurement:

> At `ell` in `{47, 101, 151, 211}` and primes `p` in `{2^20, 2^30, 2^40}`
> (i.e. `p <= 2^40`), the pre-registered falsifier **FC-4 did not fire**:
> pooled `alpha_primary = 1.1321`, `alpha_null = 1.0715`, gap `0.0606` against
> a `0.15` threshold. FC-2 also did not fire. The MECHANISM-INCONSISTENT
> designation on assumption L5 is retired **at that scope, and only there**.

That measurement is durable (`RUN-P13-NC2d-a`, snapshot commit
`b7b3240b4266b85af1e0810831a66aa6e3300535`, an ancestor of `origin/main`) and
independently reviewed twice (`TASK-20260804-cf1ae3`
`accept_with_qualifications`; `TASK-20260804-83d874` `pass_with_constraints`).
**Cite it from `EV-WESO-556063`, not from these two entries**, because that
record carries the scope, the boundaries and the reviewers' six standing
objections with it.

## 4. What may NOT be cited from these two entries

1. **`C_corrected = phi(ell) * C_Phi_ell(p) + C_walk`** as this programme's
   cost estimator. The formula does **not appear** in
   `RUN-P13-NC2d-a/raw-result.json`, in `RUN-P13-NC2b-a/raw-result.json`, in
   the validation report, or in the red-team report of the batch the entry
   cites as its basis — all of which describe an `alpha`-exponent p-scaling
   regression and an NC2b slope-recovery check. Its provenance is untraced.
   See also the open item in section 5.
2. **`N_pairs ~ exp(H_1 * n_walk)`** as validated, or as evidence of anything
   about Heuristic 1. `KN-FIND-d1c853` says so itself and is right to: NC-3
   and NC-6 never executed. `TASK-20260804-6519fa` recorded
   `failed_infrastructure` ("Executor subagent returned empty result"), the
   feasibility gate FG-1 never ran, no pilot statistic exists, and
   `P0_predicted` was never computed. **Under AGENTS.md rule 5 that is not
   evidence for or against Heuristic 1 in either direction.**
3. **Anything at cryptographic scale.** Every number behind these entries was
   measured at `p <= 2^40` with `ell <= 211`. AGENTS.md rule 7 applies.
4. **`alpha = 1.13` as propagated into any cost or margin.** The measured
   `alpha = 1.1321` is 13 per cent above the theoretical `1.0` and **has not
   been propagated into any `c`-table row or margin row** (red-team objection
   RT-OBJ-B). No `c` value moves on this evidence, and all eight mandatory
   attachments and twelve standing prohibitions of `DEC-20260802-48c72c`
   remain in force.
5. **Anything about `ell` above 211.** The primary-minus-null gap is `0.0894`
   at `ell = 151` and `0.0877` at `ell = 211` — about 59 per cent of the
   threshold, against about `0.03` at `ell <= 101` — and the pre-registered
   no-trend check constrains `alpha` against `log2(ell)`, **not the gap**
   (RT-OBJ-A). Whether the gap crosses `0.15` above `ell = 211` is unmeasured.
6. **`DEC-20260804-e19a65`'s framing.** Both entries name it as
   `source_decision`. That decision used a `decision` value outside the
   template vocabulary, narrated a hypothesis-status transition to states this
   programme has never had and which was never applied to
   `ledger/hypotheses/H-WESO-001.yaml`, and described the campaign as
   advancing to a "completed-with-open-items state", which is not a status
   this programme has. It is superseded by `DEC-20260809-a2f829`.
   **`H-WESO-001` is and remains `analyzed`.**

## 5. OPEN ITEM, not adjudicated here: the `phi(ell)` gloss

`KN-FIND-4e7a92` glosses its symbol as

> `phi(ell)` = `ell − 1` (number of distinct roots of `Phi_ell` counted with
> multiplicity in the supersingular case)

**This is recorded as a SUSPECTED defect requiring an independent reviewer, and
it is NOT adjudicated by the Coordinator or by this entry.** The grounds for
suspicion, stated so a reviewer can check them: the classical modular
polynomial `Phi_ell(j, Y)` has degree `ell + 1` in `Y`, and the supersingular
`ell`-isogeny graph is `(ell + 1)`-regular, so the natural root count at a
supersingular `j`-invariant is `ell + 1` rather than `ell − 1`; the symbol
`phi` together with the value `ell − 1` is standard notation for **Euler's
totient** at a prime, which is a different object from a root count; and
"distinct" and "counted with multiplicity" are two different counts attached to
one quantity. Corroborating but **not deciding**: the BATCH-403f13 red-team
report's own OBJ-4 reads `n_distinct_roots = ell+1 or ell+2` off
`raw-result.json` and states that for supersingular curves with `p = 3 mod 4`
all `ell`-isogenies are defined over `F_p` and entries `= ell + 1`. That is one
reviewer's reading of a different run's artifact and is cited as such.

**Nothing here asserts the gloss is wrong.** What is asserted is that it is
unresolved, that resolving it is a review act on a mathematical claim, and that
the reviewer must be someone who did not originate the entry
(`DEC-20260809-a2f829` open item OI-1, next action NA-2). If it is wrong, the
remedy is a superseding knowledge entry under a new id — never an edit to
`KN-FIND-4e7a92`.

**This open item is an additional and independent reason for the narrowing in
section 4, item 1**, which stands on provenance grounds whatever the answer
turns out to be.

## 6. A schema observation, recorded because it cannot be repaired

Both entries' frontmatter omits `confidence`, `internal_refs` and `proof_refs`,
which `tools/validate_ledger.py` (`check_knowledge_entries`) requires of an
`internal_finding`. This is noted as an observation about corpus hygiene, not
as a criticism of their content, and it is **not repaired**: repairing it would
mean editing immutable committed entries. It is listed here so a later curator
does not mistake the omission for something this reconciliation overlooked.

## 7. Provenance and standing

Created by `DEC-20260809-a2f829` under `TASK-20260809-4119f6`, the
reconciliation-and-repair ledger archive for BATCH-403f13 that
`coordination/goals/GOAL-P13-001/batches/BATCH-8e1671/SCOPE-DECISION.md`
requested. `KN-FIND-4e7a92` and `KN-FIND-d1c853` are **not** marked
`superseded_by` in their own files, because their own files may not be edited;
their narrowing lives here and in `DEC-20260809-a2f829.knowledge_resolution`.
Any successor citing either entry must cite this one alongside it.
