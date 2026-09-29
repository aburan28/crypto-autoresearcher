# Design notes — GOAL-ENDO-001 resource-and-implementation-planning gate, second attempt

Work unit: `coordination/goals/GOAL-ENDO-001/batches/BATCH-25e27c/resource-implementation-planning-gate-2/`
Author role: coordinator. Requested policy `coordinator-orchestration-code`, effort `high`.
Recorded 2026-08-19. Zero experiment runs. Nothing here is committed by this session.

This file is the reasoning behind the other four, including — and this is the half
that matters most for the two independent reviews this gate will face — **what was
deliberately not done and why**.

---

## 1. What the mandate actually was, and what it was not

The goal head's reconciled `next_action` directs a **second** bounded, nonautomatic
resource-and-implementation-planning gate at **unchanged scope**, and adds four
constraints C-A through C-D.

The temptation was to treat a dual REVISE as a verdict against the gate's *design* and
to rebuild it. That reading is wrong and the records say so plainly. The red team's
`verdict_scope` limits REVISE to the wording and framing of three sections, two controls,
one stopping-rule gap and one archive-custody defect, and states in terms that it **does
not apply to the factual layer**. Its `baseline_comparison` concludes: *"The package meets
its mandate."* The validator's own gloss on the forced `failed` token says it does not
mean the planning gate is void, that any bound value is wrong, that any obligation was
dropped, that a gate was cleared, or that anything scientific failed.

So the design is untouched. Six required contents under the next_action's own words. Eight
estimates E1–E8. Five proposals PB-1–PB-5. Five controls CT-1–CT-5. The stopping-rule set,
extended rather than restructured. Six evidence preconditions, extended to eight. Same
scope, ten objections answered.

**What I did not do:** I did not add a section, drop a section, rename a required content,
introduce a new deliverable class, or restructure the estimate/budget split. A second gate
that answered the objections by changing the subject would be a different document wearing
the mandate's name.

---

## 2. C-A, and what the reviews actually said

C-A is the constraint the previous session could not discharge and said so. This worktree
carries both review artifacts, `EV-JINV-d080c6` and `DEC-20260818-c52d54`, so I read all
four end to end before writing a byte — plus the preservation manifest, the batch-opening
decision `DEC-20260815-f7e2d4`, and the first gate itself, because a gate that "fixes"
a document it has not read is guessing.

The single most important thing the reviews said is not a defect. It is this: **the factual
layer survived two adversarial attacks with zero mismatches.** Between them the reviewers
recomputed 17 SHA-256 values, 11 sizes, 12 commits, 33 arithmetic and cost values, three
suite manifest hashes from an independently reconstructed canonical encoding, one recursive
type manifest hash, a 441350-node census in all six categories, 26 committed formula fields,
an eight-component byte sum and two budget totals — and found nothing wrong. All eighteen
obligations verified, none dropped, none reworded, none silently resolved. Both looked for
smuggled authorization by two *different* methods and both found none. `resource_incomplete`
stayed fail-closed with zero gates cleared, verified three ways plus a five-route attack.

The second most important thing is that **the most consequential finding ran against the
producer, not the contract.** MF-2 asserted an absence that the tree contradicts. That is
why C-C exists and why R-10 is now a standing campaign requirement.

Everything else — the fifteen budget figures, the four-gates-are-one-gate framing, the
dropped E14 C1 clause, the missing PB-3 stopping rule, the two broken controls, the
precondition ordering, the null receipt — is real, is answered one at a time in
`objection-disposition.yaml`, and none of it is scientific.

**What I did not do:** I did not treat C-A as satisfied by reading the decision alone. The
decision is an adjudication and it is excellent, but the head forbids treating any summary
as a substitute for the reviews, and the reviews contain things the decision does not —
HC-1's unspecified reduction factor, HC-2's paper-model circularity, OBS-4's conservative
bias, the validator's E8 units note. Several of those are fixed in this gate and would have
been missed from the decision alone.

---

## 3. The one genuinely new finding, and why I am nervous about it

Reading `v4-cost-worksheet.json` first-hand rather than through the reviews' quotations
produced something neither review found. I record it as **AR-1**.

R-4 calls it the batch's most useful output that **one lever controls all four gates**, with
"a single scalar target of roughly a 1.2e4-fold reduction". The dependency claim is exactly
right and I confirmed it at source: `total_logical_io_bytes_upper` is literally
`3*retained_artifact_bytes_upper`; `largest_required_logical_artifact_bytes_upper` is
literally `all_replacement_pairs_upper*256`; the shard count is a ceiling of the retained
total over a constant.

But the retained total is a **sum of eight components**, and the dominant term is one of
them. Subtracting it leaves 219,032,804,608 bytes — still about **51×** the retained cap,
408 shards against a cap of 24, and about 2.39× the logical-I/O cap. **The dominant term
cannot be reduced enough, by any factor including infinity, to pass the retained-byte
gate.** The single lever is necessary and *not sufficient*, and a design author who read
"one scalar target of 1.2e4" as a sufficient target would build to it and still fail all
four gates.

This refines R-4 rather than overruling it — R-4's own wording is a necessity claim
("before ANY of E4–E7 can pass"), which is correct — and it cuts conservatively, which R-4
requires of anything cited from it. It makes the obstruction worse.

**Why I am nervous about it:** it is hand arithmetic by a session with no calculator. So I
did three things against my own interest. I wrote every step out in full (ARITH-6 through
ARITH-13) so a reviewer can recompute each in one command. I widened SR-5 so a reviewer's
disagreement fires a stopping rule *against this document*. And I flagged the one sub-figure
that is conditional — the residual largest-single-artifact figure assumes a particular
component is one logical artifact, which the worksheet does not state and I did not
establish (UR-18) — while noting the other three residual figures do not depend on it.

**What I did not do:** I did not present the algebraic route as RC-1. RC-1 perturbs and
recomputes; I read formulas and subtracted. RC-1 has now been carried forward twice without
being run by anybody, and it is EV-PRE-8 and UR-19 rather than quietly marked done.

---

## 4. The budgets: three classes, not one

R-2 is the ruling with the sharpest binding effect: **no later decision may cite any of the
fifteen magnitudes as a derived budget.** It also names the three permitted remedies — give
each a committed antecedent, mark it UNDERIVED, or remove it.

I used all three, which required inventing an explicit third provenance class.

- **Six** figures (PB-3/4/5 wall and memory) get `PRECEDENT_CITED_NOT_DERIVED`, pointing at
  `DEC-20260815-f7e2d4`'s `declared_task_budgets` for equivalently-shaped tasks. I carried
  that source's *own* warning — `ceilings_are_not_estimates`, "not predictions of duration
  and not measurements" — into the same field, because keeping the supporting half of a
  citation and dropping the impeaching half is precisely RT-O4.
- **Nine** figures go UNDERIVED with reasons. All five disk figures are underived because
  the declared-budgets block **carries no disk figure for any task at all**. PB-1's and
  PB-2's wall and memory are underived because, as R-2 says, they have no visible antecedent.
- **The envelope total is removed**, not restated, along with the `relation_to_frozen_caps`
  sentence R-2's secondary item found either false or inapplicable.

A precedent is weaker than a derivation and stronger than a bare assertion. Collapsing it
into "derived" would be exactly the substitution R-2 forbids; collapsing it into "underived"
would understate what the record contains, which this campaign treats as a failure symmetric
with overclaiming. So it is its own labelled class with a warning attached.

**What I did not do:** I did not invent a derivation for any of the fifteen. There is no
committed rate, no measured duration and no benchmark from which a planning-task duration
could follow — that is E1 and E2's entire problem — so any derivation offered here would be
the plausible number the validator praised the first gate for refusing elsewhere.

**What this cost me:** my own task budget is now UNDERIVED (UR-14). The first gate could
state 5400/4/1 because a batch-opening decision had declared them. I read no such decision
for this work unit. Writing a plausible figure would manufacture a budget nobody set, so I
recorded a defect against myself instead. A disclosed null is a defect; an invented figure is
a fabrication.

---

## 5. R-10, and the decision not to search

R-10 is now standing: any assertion that something is **absent** from a committed artifact
must record the exact pattern, the exact paths and the exact count, with a varied method.

I have no shell. I cannot run the exact search R-10 requires. So rather than record a
weakly-searched absence, **this gate makes no absence claim about any committed artifact at
all.** That is a structural compliance route, not a procedural one, and it is stated as
such.

The two places where an absence would have been natural:

1. *Does a batch-opening decision exist for this work unit?* Recorded as **UNDETERMINED**,
   with the exact glob (`ledger/decisions/DEC-20260819-*.yaml`), its root, its count (1), the
   identity of the single match, and an explicit statement that a filename glob is narrower
   than any absence conclusion and that a decision under another date token would not appear
   in it.
2. *Does any stopping rule bind PB-3?* Attributed to RT-O5, which enumerated the nine rules
   and produced a counterexample. My own contribution is a **complete read of a closed
   nine-item list** at `planning-gate.yaml` lines 595–652 — an enumeration, not a pattern
   search — and I said which it was rather than blurring them.

**What I did not do:** I did not re-verify the MF-2 fact. Head constraint C-C tells me
441350 is present as "441,350" at line 624. I did not run that search and I say so. I rely
on the validator (both search forms, both counts), the adjudicating session (reran with a
different tool, confirmed the containing task object) and C-C (separator-tolerant pattern).
Re-asserting a fact I did not check, on the strength of three people who did, is fine —
*claiming* to have checked it would not be.

Nor did I run any search, fold-blind or folding-aware, for obligation text in the head. Six
of the eighteen are split across a line break, and a raw byte search for obligation 14's
complete text returns zero because a newline falls in its middle. With no shell I could only
have run the fold-blind form, which is the trap. So I ran neither and assert nothing in
either direction; the presence of all eighteen is carried as the reviews' finding.

---

## 6. The eighteen: bound, not copied

`preservation-binding.yaml` contains **zero** `obligation_verbatim` strings. Each obligation
is an exact pointer to
`preservation-manifest.yaml obligations[n=<n>].obligation_verbatim`.

The head itself refused to re-transcribe them on 2026-08-19 for exactly this reason, and
incorporated them by exact reference instead. Copying eighteen frozen strings correctly is
not a skill a session with no parser and no hashing tool can demonstrate; **not copying them
is.** The cost is that a reader cannot see the text in that file, and I accepted it: every
entry carries the exact path and field, plus a `subject_descriptor` that is explicitly
labelled as my own non-normative gloss with no binding force, so a reviewer can navigate
without the text being restated.

I extended the same discipline one step further than required: **obligation 6's three
manifest hashes are also not retyped.** Three 64-character hex strings hand-copied by a
session with no hashing tool is the same avoidable risk in a different costume. They are
bound where the committed manifest already binds them.

---

## 7. OBD-1: the temptation, and the refusal

Both reviews independently strengthened the case for reading B. The validator recomputed the
contested manifest hash and found it in nine committed places — three more than the producer
claimed, including the controlling decision *and* the neutral evidence record — and zero
times in the queue where the other two appear four and five times. The red team established
by direct computation which named object each 45-entry manifest hashes and concluded the
defect is material rather than cosmetic.

That is a real accumulation of support, and acting on it would still be the forbidden act,
**because the authority question is not how strong the case is but who may decide.** C-B
reserves it to a separately authorized goal-head reconciliation. R-3 records that the
adjudicating Coordinator did not have the authority either and said so rather than resolving
it quietly. This gate has less authority than that decision, not more.

So: all three manifests stay bound, both readings stay recorded, neither is selected,
neither is ranked, and the strengthening is written down so the authorized decision can
weigh it. The only thing I added is **EV-PRE-7** — a later decision relying on obligation 6's
binding must first see whether OBD-1 has been adjudicated. Visibility is not resolution.

**What I did not do:** I did not write "reading B is better supported but I decline to
choose." That sentence is a resolution with a disclaimer attached, and a producer may never
make it silently.

---

## 8. A tension I should name rather than paper over

`DEC-20260818-c52d54`'s single next action asks for **one separately authorized Coordinator
decision** doing two things: (A) adjudicate OBD-1 via a goal-head reconciliation, and (B)
open one bounded superseding revision work unit carrying an eight-item work list.

The goal head, reconciled the following day, directs a **second gate at unchanged scope**
and explicitly forbids resolving OBD-1 here.

These are not in conflict, but they are not identical either, and a reviewer will notice.
My reading: the head is later and is the instruction I am under. Item (A) is **not done
here** and is forbidden here. Item (B)'s work list is what the *content* of this gate
addresses — RC-1 excepted, because it needs a shell — but **this gate is not that decision.**
I have written a planning document. I have not opened a work unit, minted an identifier,
declared a budget, created a handoff, or dispatched anything, and I have no authority to.

That is why `planning-gate-2.yaml` opens with an `admission_status` block saying the
document is complete and the *work unit* is not. It would have been easy, and wrong, to let
the document's completeness imply that a batch existed for it.

---

## 9. Everything I deliberately did not do

Collected, because this is what the reviews will check first.

**Authority.** Did not resolve OBD-1. Did not resurrect MF-2. Did not clear, lift, relax,
re-dispose or widen `resource_incomplete`. Did not raise a cap. Did not take any of the five
prohibited credits. Did not change any status — goal, batch, experiment, hypothesis,
evidence, knowledge. Did not open a batch, write a queue, create a handoff, or dispatch.
Did not write a ledger record of any kind. Did not promote anything to `knowledge/`.

**Records.** Did not edit the first gate's package, either review artifact, any receipt, any
ledger record, any `v6`-or-earlier byte, or the goal head. Every correction is a superseding
note; the immutable records still carry what they were authored with. Did not touch the
primary checkout.

**Identifiers and hashes.** Minted nothing — every identifier position carries a literal
`<ALLOCATE-...>` placeholder. Wrote no hash-shaped string anywhere; where a hash was
required and unavailable I wrote `null` with the reason.

**Numbers.** Invented no figure, interpolated none, back-filled none. Did not report an
underived quantity as an interval or an order of magnitude. Did not cite any of the fifteen
PB magnitudes as a derived budget. Did not assert an envelope total over underived
components. Did not substitute `temporary_working_bytes` for a peak-memory estimate.

**Claims.** Did not close the lane and did not recommend closing it — EV-PRE-3 keeps both
routes open and recommends neither, because declining to search because a target looks
saturated is a failure symmetric with overclaiming. Did not claim RC-1 was performed. Did
not claim any check I did not run. Did not claim a parse, a hash, a size, a commit, a
census, or a dispatcher verification. Did not record an attestation — none was sought and
none obtained. Did not claim a quorum. Did not describe the two reviews as cross-model
corroboration. Did not present the committed binding target as a live model confirmation.
Did not select, configure, probe, contact or use Bedrock, and recorded the refusal in the
gate and in SR-7.

**Scope.** Did not write outside this work-unit directory. Did not commit.

---

## 10. What I think is most likely to be wrong here

Written for the two reviewers, because guessing at my own weak points is cheaper for them
than finding them cold.

1. **AR-1 and ARITH-6 through ARITH-13.** New, hand-computed, unchecked by anyone. If one
   integer is wrong, this gate's most consequential new statement moves. Recompute these
   first. SR-5 is bound to them deliberately.
2. **The `PRECEDENT_CITED_NOT_DERIVED` class.** I invented it to satisfy R-2's first remedy
   honestly. A reviewer may reasonably hold that a ceiling declared for a *different* task is
   not an antecedent at all and that all fifteen should be UNDERIVED. That is a defensible
   reading and I would not fight it hard; I chose the other because marking six figures
   underived when the record does contain a relevant committed figure understates the record.
3. **Restating thirteen caps where the first gate restated eleven.** No value differs and
   none is relaxed, and I said so explicitly — but any change to a cap list in this campaign
   is exactly what an adversarial reader should attack, and a silent expansion would look
   like a widening even though it is not.
4. **The self-audit in `underived-register.yaml`.** An author auditing its own numeric fields
   is the weakest form of that check. The first gate made the same claim about itself and was
   wrong about fifteen numbers, and it took two reviewers enumerating every field of five
   items to find them. **The same enumeration is owed here and only the author has done it.**
5. **YAML well-formedness.** ~~I have no parser...~~ **This fired. It was the right call to
   flag it and the flag was not enough.**

   The Coordinator ran `yaml.safe_load` and **two of the five deliverables failed** —
   `objection-disposition.yaml` and `underived-register.yaml` — both with the same defect,
   and it was not the colon-space class I had mitigated. It was a **sequence dash at the same
   indentation as the mapping keys around it**: I had written a prose key (`why_this_block_exists`,
   `context`) and then a list at the same level, which leaves the parser inside a block mapping
   with nowhere to put a `- `.

   The fix was structural, not cosmetic. In each case the prose key was always a *note about
   the list*, never a member of it — so the key moved **out** to become a sibling of the list
   rather than the list moving **in**. Nudging spaces until it parsed would have produced a
   different and false structure (a note filed as one of the findings it describes).

   **Sweeping found a third instance the report did not name:**
   `findings_in_the_first_packages_favour_that_this_gate_preserves` in
   `objection-disposition.yaml`, which `safe_load` could not have reached because it stops at
   the first failure. I found it by searching **by indent level** rather than by adjacency —
   every `^    - ` in both files, checking whether its container also held 4-space keys. After
   the three fixes, every 4-space dash sits under a valueless 2-space key, and every nested
   list at 6 and 8 spaces sits under its own key one level shallower.

   **The non-throwing class was checked and is clear.** Nine flow mappings exist, all in
   `planning-gate-2.yaml` (`{stage_id: ..., basis: '...'}`). Every `basis` value is
   single-quoted, so a comma inside it is safe by construction; every `stage_id` value is a
   plain snake_case identifier containing no comma. None can split into garbage keys. I did
   **not** convert them to block mappings: that would mean nine edits into a 153 KB file that
   currently parses, and I have no parser to re-verify the result — a worse trade than leaving
   a verifiably safe construct in place. The claim is falsifiable in one line: all nine must
   parse to exactly two keys.

   **What this episode actually shows.** My mitigation was real but aimed at the wrong class,
   and I ranked it fifth. A mitigation is not a check, which I had written — and then treated
   the written disclaimer as if it discharged the risk. It does not. The parse belonged to
   whoever had a parser, it found two failures, and the sweep it prompted found a third.

---

## 11. What this gate is worth

Modest, and worth saying plainly. It is a planning document that authorizes nothing, measures
nothing, and moves no status. Its `claim_tier` is toy, its `sota_delta` is zero on eleven
axes, and the one-N N = 19507 ceiling is intact. No completion criterion is met or advanced;
no pause condition is engaged.

What it does contribute: the ten standing objections are answered one at a time with named
changes; nine budget figures move from asserted to honestly underived; two broken controls
are repaired at no measurement cost; a stopping rule now exists that can refuse the central
deliverable; a precondition no longer forces a host measurement onto exits that do not need
one; and the cost obstruction is now stated in a form a design author can actually use —
including the part that says the obvious single lever will not be enough.

Every one of those cuts toward fail-closed. **Nothing in this gate is headroom**, and SR-11
exists to refuse any successor sentence that reads it as such.

Failing to break this plan would not be evidence that the plan is correct.
