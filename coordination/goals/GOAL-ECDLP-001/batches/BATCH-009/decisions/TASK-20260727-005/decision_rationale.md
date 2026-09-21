# Decision rationale — TASK-20260727-005

**Determination:** `H-GGM-001` returns from `supported` to **`specified`**.

Companion to `status_determination.yaml` (DET-20260727-005), which carries the installable
record blocks. This document gives the reasoning in prose, including the strongest argument
*against* the determination and why it did not prevail.

Two statements govern everything below and are not qualified anywhere in it:

- **Nothing here is evidence for or against ECDLP hardness.** KN-OPEN-001, prime-field ECDLP
  and index calculus are untouched. No solve, no relation, no certificate, no cost comparison.
- **AGENTS.md rule 12 is not discharged by anything in this batch.** Both producers requested a
  higher policy, both resolved `claude-opus-5` with `fallback_used: true` and
  `equivalence_to_requested_policy_claimed: false`, and REV-20260727-002 says of itself: *"It
  discharges rule 12 for nothing."* Since both are the same resolved model, rule 13's
  three-independently-resolved-models standard is not met by the pair either. This determination
  is itself subject to later review on a conforming backend.

---

## 1. What the review actually found, and why it is different from what the escalation found

ESC-20260727-001 ruled main's EXP-GGM-001 archive process-invalid and recommended `specified`.
Its author explicitly asked for the ruling to be tested rather than accepted, and recorded that
it had **not read** `experiments/EXP-GGM-001/simulability_test.py`.

TASK-20260727-002 read it, and read it *first* — before the ruling, before RT-20260726-001,
before REV-20260726-005. That ordering is the only structural reason to prefer its agreement over
an echo, and it is what produced the finding the ruling could not have had:

> `classify_oracle` is a lookup table keyed on the subject's name, not a decision procedure.

Everything follows from that one sentence:

- The eight verdicts are **inputs** to the program, not outputs of it. There is no parser, no
  simulator constructor, no overhead checker and no witness generator, although
  `specification.yaml implementation_requirements` names all four.
- The control gate compares `ORACLES[name]["expected_verdict"]` (source literals, lines 27–92)
  against `classify_oracle`'s return (source literals, lines 121–178). Two constants in one file.
  `controls_correct == 4` on **every possible execution**, so the frozen falsification criterion
  — *"a single control misclassification falsifies the test's soundness"* — cannot fire.
- And the figure never reached an artifact: `controls_correct` is printed at line 312 and never
  passed to `write_run`, which writes `stdout.log` and `stderr.log` as empty strings at lines
  271–274. All 18 log files are 0 bytes. The 4/4 exists only as prose in `analysis.md`,
  `EV-GGM-001` and `DEC-20260726-007`.
- The nine "runs" are one computation. `verdicts` is built once at lines 295–299, *outside* the
  loop at 325–337, and the same object is serialized nine times by one process in 1.005 seconds.
  All nine `raw-result.json` are byte-identical (`388c95d8…`).

The escalation thought an execution had occurred that was invalid. The review establishes that
**the specified test was never executed at all.** That is a stronger fact and a different one,
and it is the ground this determination rests on.

The review also **corrected the escalation in main's favour**, which matters for the integrity of
this record. ESC horn 2 claimed that a uniform structured GGM forces the `encoding` control to
flip to SIMULABLE. The reviewer showed that step "conflates publicity of the curve EQUATION with
readability of a labelled point's COORDINATES", built a properly formalised SGGM, and found the
gate genuinely reads 4/4 under it. The ruling reached the right destination by a partly wrong
route. Agreeing with a ruling's destination while correcting its route is the difference between
resting on review and resting on authority.

---

## 2. Why `specified`, and what the status is asserting

The handoff asked two questions directly. Answering them directly:

**Does a hypothesis whose sole test is a lookup table have any evidential support at all?**
No. None. Not weak support, not anecdotal support — *no measurement occurred*. A program that
reads out its own inputs measures nothing, and a gate whose two operands are literals in the same
file carries zero information. The evidential content of the nine runs with respect to H-GGM-001
is empty **in both directions**.

**What status honestly represents "untested" as distinct from "refuted"?**
`specified`. The chain is

```
proposed → specified → approved → running → analyzed → replicated
        → supported | weakened | rejected | inconclusive | superseded
```

Every status to the *right* of `running` asserts that a test was carried out and interpreted.
`specified` is the last status on the chain that asserts only that a test exists on paper. That
is exactly, and only, what is true: the hypothesis has a specified test, the test was never
approved, and the one execution that occurred did not implement it.

`specified` also resolves a live contradiction between two committed records: `H-GGM-001` read
`supported` while `ledger/goals/GOAL-ECDLP-001.yaml` BATCH-006 `claim_boundary` said it stays
`specified`. It restores no more than DEC-20260726-008 had already recorded.

### The alternatives, and why each fails

| Status | Why not |
|---|---|
| `supported` | Terminal verdict is DOES_NOT_SURVIVE. The gate cannot fail and appears in no run artifact; the jet closure fails under both formalised models, including the steelman that *does* save the gate; `strong` was never available for one unreplicated execution over eight frozen strings. |
| `weakened` | Evidence-driven adverse transition with no observation behind it. Rule 5 forbids reading an implementation failure as evidence against a mathematical hypothesis. The one candidate ground — falsification condition 4 firing textually for elliptic-net and incidence — fails because condition 4 is *misstated*: growth in C degrades the bound to `q ≥ Ω(√p/C)`, which at `C = O(log N)` is `p^{1/2−o(1)}`, exponent intact. A misstated falsifier cannot fire. |
| `rejected` | Forbidden three ways: no counterexample certificate; the only oracle-level derivation is the reviewer's own and is unreviewed; `reject_scoped` on a single unreplicated empirical-only run set is forbidden outright — and this set is not even that. |
| `inconclusive` | The closest competitor. It asserts that a test *ran* and its data did not discriminate. Recording it would silently ratify the proposition that EXP-GGM-001 tested H-GGM-001 and returned ambiguous data. It did not. |
| `superseded` | Requires a successor hypothesis record. None exists; DEC-20260726-008 named the obligation and it is carried to TASK-20260727-009. |
| `approved` | Not sought. v1 stays `review_required` / `approved_by: null`; OBJ-02 still blocks. |

**Where `inconclusive` *is* the right word**: on whether the four augmented oracles are in fact
GGM-simulable. That question the evidence cannot discriminate, and the decision says so plainly
in its limitations and in EV-GGM-002's `unresolved_confounds`. It is a question about the
*oracles*, not about H-GGM-001's status, and encoding it as a hypothesis status it does not
describe would be a category error.

---

## 3. The strongest argument against this determination, and why it did not prevail

The strongest case for a *higher* landing than `specified` is the one the reviewer himself built
and named as "the best argument available to main" (`adversarial_notes` §I.6), combined with the
one substantive result that survived:

> Even granting that `classify_oracle` is a lookup table, the *table entries* are what matter. If
> a domain expert hand-derived eight verdicts and encoded them, the code is a transcription
> device, and the question becomes whether the eight entries are right — a mathematical question,
> not a software one. And at least one entry *is* right: the endomorphism oracle is genuinely
> simulable, and exponent 1/2 genuinely is preserved. On that reading H-GGM-001 has some support,
> and `specified` under-records what the archive produced.

This is a serious argument. It did not prevail, for four independent reasons, any one of which is
sufficient:

1. **The reviewer broke it on its own terms, by doing the work it demands.** He checked all eight
   entries by hand under two models. Two of the eight — jet and elliptic-net — are wrong under
   both. Correct control entries and wrong augmented entries coexist in a lookup table at zero
   cost, because the branches share no machinery. So "the entries are what matter" cuts against
   the archive once you actually check the entries.

2. **A transcription device is not the thing H-GGM-001 claims.** The hypothesis statement is that
   *a machine-checkable simulability test, given an oracle's input-output specification, correctly
   decides* simulability. Eight correct hand-derived entries would support the eight *claims*, not
   the *test*. The hypothesis under test is about the existence and soundness of the decision
   procedure, and no decision procedure was written.

3. **The surviving entry is right for a reason the artifact never gives, and it is not new.** The
   `[λ]`-multiplication simulator — φ acts on the prime-order subgroup as multiplication by a
   publicly computable λ, answerable using only the group oracle — appears nowhere in the module.
   Main's argument applies `φ(x,y) = (ζx, y)` to coordinates the model forbids and charges `C = 0`
   for the very operation being simulated. The honest count is `Θ(log N)`, at which the exponent
   is still 1/2 — and that fact is a restatement of Wiener–Zuccherato, GLV and
   Duursma–Gaudry–Morain, already the content of KN-TECH-005.

4. **Adopting it would repeat the defect being corrected.** The `[λ]` result is REV-20260727-002's
   own hand derivation. It is derivation-level, expressly "offered for independent checking, not a
   theorem", and it has received no review. Promoting a hypothesis on the strength of an
   unreviewed hand derivation is the mirror image of archiving a closure claim without review. It
   is attributed, carried as an open item, and assigned to TASK-20260727-010 — and it is the basis
   of nothing in this determination.

The second-strongest argument against — that `weakened` better records a situation where a
declared falsification condition fired — is answered in the table above and in the decision's
rationale: condition 4's consequent is mathematically wrong in the direction that manufactures
false openness, so the protocol cannot adjudicate elliptic-net and incidence in *either*
direction. That is indeterminacy, not falsification, and firing a misstated falsifier would import
the review's own correction as though it were a result.

---

## 4. The refutation artifact

This determination is **not** an adverse evidence transition — not `weaken`, not `reject_scoped`,
not a move to `rejected` — so the refutation-artifact gate of `docs/claims-and-verification.md`
is not triggered by it. It *is* adverse to a committed claim (main's DEC-20260726-007 and
EV-GGM-001), so the artifact is named anyway, in the document's own order:

1. **Counterexample certificate — not available.** The Weierstrass-twist invariance test
   (`(x,y) ↦ (u²x, u³y)`, compare ε-coefficients across a group isomorphism) is pre-registered
   twice and has *never been run*. It needs a new experiment specification and is not authorized
   by anything in the ledger, including this determination.
2. **Derivation note — available, and this is what is relied on.**
   `.../reviews/TASK-20260727-002/review_report.yaml` and `adversarial_notes.md`. Its
   load-bearing steps require no mathematics at all: read `simulability_test.py` lines 27–92,
   106–178, 271–274, 295–299, 303–312 and 325–337, and observe that the gate's operands are
   literals in the same file and that the verdict dict is built once outside the loop. Labelled
   `derivation`, never "proved".
3. **Empirical-only — not available.** There is no empirical content: the seeds and bit sizes
   never touch a verdict.

The artifact must be committed and bound *before* the decision that relies on it. It is present
in a clean worktree at 6d6632fc but **no snapshot receipt exists** at the declared
TASK-20260727-004 path. TASK-20260727-006 must establish and record that binding, or stop and
record a binding failure. That is an evidence-integrity requirement, not a formality.

---

## 5. What the evidence record may and may not say

`EV-GGM-002` supersedes `EV-GGM-001` — supersedes, never overwrites; EV-GGM-001 keeps its bytes
and its id. It carries:

- all nine `RUN-GGM-*` ids (EV-GGM-001 asserted nine runs with `run_ids: []` — ESC ground A5);
- `direction: neutral` — the run set neither supports nor contradicts;
- `strength: inconclusive` — not caution, fact: nothing was observed about the hypothesis;
- `claim_tier: toy` — mechanical from 8/12/16 bits, at the recorded ceiling;
- `proof_status: not_applicable` — strictly *below* the recorded `empirical_only` default
  ceiling, so no ceiling supersession is claimed. The reviewer authorised exactly this: *"If the
  Coordinator prefers, `not_applicable` is defensible. What is NOT defensible is `derivation`."*

**The byte-identity is recorded as a scope limit, not a footnote.** The governing boundary reads:
the nine directories are one computation serialized nine times, so the record may not be cited
for replication, seed robustness, agreement across runs, verdict stability, or N-independence of
`overhead_C`; the constancy of `overhead_C` across 8/12/16 bits is a *necessary consequence* of
writing one integer nine times, and the overhead-growth check had zero degrees of freedom. Any
later record citing "9 runs" from this experiment must carry that sentence with it.

Every closure phrase from EV-GGM-001 — "closure at exponent 1/2", "scale-independent", "valid at
all scales", "this closes all jet-based ECDLP candidates" — is absent from EV-GGM-002 and
unsupported by it.

---

## 6. Two things this is, and one thing it is not

- **A process ruling.** No approval, no rule-12 review. Process facts, and *not* negative evidence
  about any oracle.
- **A substantive finding about the artifact.** The module implements no decision procedure and
  the gate cannot fail — derived from the committed source, and it would stand unchanged had the
  experiment been approved and reviewed perfectly.
- **Not a finding about the mathematics.** Whether jet, elliptic-net, incidence or endomorphism
  is GGM-simulable is *inconclusive* and undecided. A process defect never stands in as a
  mathematical finding here, and a badly instrumented execution is not evidence in either
  direction.

The second producer, RT-20260727-001, is recorded for the batch close only: DOES_NOT_SURVIVE and
REJECTED-duplicate on BAR-PATHDYN-CONDTAIL-D2, with RT-1476-SUBRES-A1 unchanged — *"THIS TASK DOES
NOT CLOSE THE GATE, AND IT DOES NOT OPEN IT."* Nothing in it bears on H-GGM-001.

---

## 7. What is refused, and what is assigned

**Refused:** any execution of EXP-GGM-001 version 1, in this campaign or any successor. The
reviewer's operative finding is that there is nothing to re-run — the module would reprint the
same eight literals. Its status stays `review_required` with `approved_by: null`, and this
determination does not set either field. Version 2 must **replace the classifier**, not restate
the definition around it.

**Assigned, not performed here:**

| Task | Item |
|---|---|
| TASK-20260727-006 | Install the three records; one-field H-GGM-001 edit; goal checkpoint; establish the D3 binding or stop. |
| TASK-20260727-007 | (already authorized) Clear the conflict markers and the KN-FIND-002 collision. Blocks the next item. |
| TASK-20260727-008 | Superseding/correcting KN-FIND for the GGM closure finding + regenerated `knowledge/INDEX.md` in one commit; demote BAR-PATHDYN-CONDTAIL-D2 in the Report 94 index. |
| TASK-20260727-009 | EXP-GGM-001 v2 (classifier replaced, one frozen model, verdicts re-derived before implementation, dynamic overhead over bits 8..32) + the superseding H-GGM-001 record. |
| TASK-20260727-010 | Conforming `review-breakthrough`/max review of this decision, of REV-20260727-002, and separately of its eight-subject hand derivation. |
| TASK-20260727-001 | (reserved) Nine-run provenance audit. Overlapped, not discharged. |

**Knowledge promotion:** none is warranted — `supersede` on `neutral`/`inconclusive` evidence does
not meet the gate, and the two candidate promotions were rejected on the merits (the `[λ]` result
is unreviewed and already KN-TECH-005; the control-gate lesson is about this harness, not about
ECDLP). But a *required* knowledge action does exist and is **deferred, not skipped**: main's
promotion of the GGM closure finding rests on evidence now superseded, and that entry needs a
superseding entry with a regenerated index. It cannot be done in BATCH-009 because
`knowledge/INDEX.md` and two KN-FIND entries carry unresolved Git conflict markers and
KN-FIND-002 is claimed by two different findings. Assigned to TASK-20260727-008, gated on
TASK-20260727-007, specified in CORR-20260727-003.

---

## 8. Two blocking bookkeeping deviations the archive must handle

1. **`DEC-20260727-003` is taken.** TASK-20260727-006's `archive.record_ids` names it, but it is
   the merge-corruption repair decision at HEAD. IDs are immutable and never reused, so this
   determination installs at **`DEC-20260727-004`**, and the archive's effective record_ids set is
   amended to `{EV-GGM-002, DEC-20260727-004, CORR-20260727-003, H-GGM-001, GOAL-ECDLP-001,
   BATCH-009}`. `DEC-20260727-003` is deliberately *omitted* from the commit message: this archive
   neither creates nor changes it, and naming it would make the verifier's message check pass for
   a false reason. The immutable handoff is not edited; the divergence goes in the receipt.
2. **`ledger/corrections/` is outside the declared write scope.** DEC-20260727-004 authorizes
   adding exactly one path, `ledger/corrections/CORR-20260727-003.yaml`, on the precedent of
   DEC-20260727-001 + CORR-20260727-001 and DEC-20260727-003 + CORR-20260727-002.

---

## 9. Authoring boundaries

This session has no shell and no clock. It ran no git command, computed no SHA-256, made no
commit and staged nothing, and **asserts that no commit happened**. Every hash it quotes was
computed by REV-20260727-002 from Git object content and is quoted, never recomputed. It edited no
ledger record, no experiment record and nothing under `knowledge/` or `experiments/`. It wrote
exactly two files, both under
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-009/decisions/TASK-20260727-005/`, and both are
working-tree-only until the Coordinator ledger archive commits them and the post-commit verifier
accepts that commit.
