# GOAL-MCE-001 BATCH-002 — opening

**Goal:** GOAL-MCE-001 · **Question:** RQ-MCE-e65b3c · **Opened:** 2026-08-03
**Prior batch:** BATCH-001, closed by `DEC-20260803-a5b9b1` (disposition
`refine`), evidence `EV-MCE-332f99`.

BATCH-002 does two things: **repair what BATCH-001's reviews found broken**,
and **take the one substantive step BATCH-001 skipped for a reason that turned
out not to exist**. It designs no experiment, forms no hypothesis, runs no
solver, and asserts nothing about Classic McEliece's security in either
direction. Nothing in it is admissible toward an AGENTS.md rule 13 quorum.

---

## 1. This batch exists because BATCH-001's Coordinator was wrong three times

Not because a producer failed. Both BATCH-001 producer packages were admitted
(`DEC-20260803-a5b9b1` D-1): 26 sources re-acquired, 25 hash matches, zero
fabrications, rate arithmetic independently recomputed 5/5, scope firewall
held in both. **Every defect this batch repairs is the Coordinator's.**

| Defect | Where it lives | Status |
|---|---|---|
| Rate framing falsified by the batch's own text | `BATCH-001-OPENING` §4, `RQ-MCE-e65b3c.constraints`, `KN-LIT-4c8135` | D-2, D-4 — **repaired here** |
| `already bind to` vs `ISD-FC-2026 IS NOT ADOPTED` | `goal.yaml` | D-3 — **already corrected** in the BATCH-001 ledger archive |
| `key-recovery` on distinguisher-only entries, 4 of 4 | `KN-LIT-13a01d`, `71d1a0`, `7ee1a9`, `e37d4c` | D-5 — **repaired here** |
| Esser–Bellini SEC Table 1 read and not transcribed | deferred to the non-existent binding | D-3 cost — **taken here** |
| Divergent transcription standards inside one batch | validator Q2 | D-10 — **settled here, before more transcription** |
| Five specification `KN-LIT` entries proposed, not filed | deliberately deferred | **filed here** |

## 2. The correction is ONE defect in three places, and must land atomically

The red team's argument is the reason `TASK-20260803-a53f73` is a single task
rather than three: BATCH-001-OPENING §4, `RQ-MCE-e65b3c.constraints` and
`KN-LIT-4c8135` all state the same wrong thing, and **fixing them separately
lets a later batch inherit whichever is fixed last.**

The wrong thing, precisely. §4 asserted *"the rate threshold is the whole
question"* and built the batch's measurement plan on it. The batch's own
retrieved text says otherwise — `arXiv:2304.14757`, verbatim:

> *"Interestingly our attack does not work at all when the alternant code has
> the additional structure of being a Goppa code"*

with Table 1 carrying *"(does not apply in the particular case of Goppa
codes)"*. The decisive restriction is the **code family**. Classic McEliece
uses binary Goppa codes.

`KN-LIT-4c8135` mentions Goppa once, in the opposite direction, and calls its
rate-scoping *"the whole content of its practical reading"* — an entry that
teaches itself as this program's exemplar of scope honesty while having the
boundary wrong. It is corrected by **superseding**, never by editing
(`knowledge/README.md`); the old entry keeps its ID and gains `superseded_by`.

The same framing is **wrong-typed** for `KN-LIT-71d1a0`, which the correction
must also fix: its Theorem 3 is stated in the **dual** rate and says *"here we
allow any R"*; the 0.277 / 0.141 figures are null-model conditions on a
shortened code, not applicability bounds on the distinguisher.

## 3. The tagging defect is worse than a tagging defect

`RQ-MCE-e65b3c` carries the constraint *"Distinguisher is not break"* and names
`KN-LIT-13a01d` as its anchor. That entry's own body reads *"It does not
recover keys; it distinguishes"* — **and it is tagged `key-recovery`.**

Prevalence across the 137 entries filed 2026-08-03, measured by the red team,
not sampled: **36** tagged `key-recovery`, **4** tagged `distinguisher`, **4**
tagged both, **0** tagged distinguisher-only. So the constraint is defeated at
the grep level by exactly the entries meant to enforce it, and a future agent
grepping `key-recovery` to find breaks gets four distinguishers back.

That is why this is repaired now rather than noted: the corpus is the
program's retrieval substrate, and a substrate that answers this query wrongly
will keep answering it wrongly.

## 4. The substantive lane: the baseline BATCH-001 declined to take

`TASK-20260803-f3aece` read Esser–Bellini SEC Table 1 — three memory models ×
five parameter sets, p.10 — and **deliberately did not transcribe it**,
deferring to a costing-convention binding that `DEC-20260802-344883` D-6 says
does not exist.

Transcribing a published table is not adopting a convention. It is the
**baseline half of BATCH-001-OPENING §1's own justification**, and it was
available at zero retrieval cost. `TASK-20260803-cb44ab` takes it.

This is the first genuinely substantive content in the campaign: with the
rates already transcribed (0.729167 – 0.796875, `EV-MCE-332f99` O-1) and a
published memory-charged cost table beside them, the goal's second completion
criterion becomes reachable — under a **stated** convention that is explicitly
**not** ISD-FC-2026 until that convention is adopted.

**What this task may not do:** it may not adopt ISD-FC-2026, derive a competing
convention, or compute a cost of its own. It transcribes a third party's
published table and records which convention that table uses, in that party's
own words.

## 5. Settle the transcription convention before transcribing more

Validator finding Q2: `TASK-20260803-f3aece` silently glyph-normalised quoted
material presented as *verbatim* while declaring **zero** `[EXTRACTION-DAMAGED]`
markers, where `TASK-20260803-292b99` left raw `(cid:NN)` tokens visible and
marked them. Two standards inside one batch. No number was affected.

`DEC-20260803-a5b9b1` D-10 requires this settled **before** the next
transcription batch, not after — which is now, because §4 is a transcription
task. It is folded into `TASK-20260803-a53f73` rather than given its own task:
it is a one-paragraph convention, and giving it a task would make three
producers where two suffice.

## 6. What BATCH-002 deliberately does not do

- **Does not re-attempt `iacr:2026/1232`'s PDF.** The 403 is path-scoped and
  reproduced twice; `/archive/versions/` is HTML and also 403. Circumventing
  bot protection is forbidden, and AGENTS.md rule 5 makes a blocked route a
  recorded outcome rather than evidence. The paper stays unread and every
  record says so.
- **Does not compute a distance** between the 2026 attack regime and Classic
  McEliece. There is still no transcribed left-hand side.
- **Does not design an experiment or form a hypothesis.**
  `active_hypothesis_ids` stays empty.
- **Does not touch `knowledge/` from a producer.** Producers propose; only the
  ledger archive files. That rule is why BATCH-001's defective entries were
  caught before five more joined them.

## 7. Batch shape

Two producers, disjoint write scopes, neither depending on the other.

| Task | Role | Duty |
|---|---|---|
| `TASK-20260803-a53f73` | executor | Draft the whole correction package as PROPOSED files: superseding `KN-LIT-4c8135`, the four tag-defective entries, the `RQ` constraint text, a `BATCH-001-OPENING` superseding note, the five specification entries, and the transcription convention |
| `TASK-20260803-cb44ab` | executor | Transcribe Esser–Bellini SEC Table 1 and the convention it uses, verbatim |
| `TASK-20260803-77eeb2` | coordinator | Snapshot archive |
| `TASK-20260803-8cf2b6` | validator | Re-acquire; check every superseding entry against the source it corrects |
| `TASK-20260803-9ab856` | red-team | Attack the corrections themselves |
| `TASK-20260803-3aa684` | coordinator | Ledger archive — `EV-MCE-0fbb1a`, `DEC-20260803-18d8f3`; **files** the entries |

**The red team's standing instruction is unchanged and now has a fourth
precedent to work with.** Three consecutive campaigns had a Coordinator claim
about a prior record found wrong by its own red team, and BATCH-001 proved that
naming the precedent does not prevent it. A correction batch is the *highest*
risk place for a fourth: a corrected claim feels checked, and it is
specifically directed to verify that each superseding entry is right rather
than merely different.

## 8. Repository state at open

`origin/main` merged cleanly at this open — no conflict, unlike BATCH-001's
merge. `tools/validate_ledger.py` reports **20** errors, down from 110 before
the merge; `tools/check_merge_hygiene.py` now **PASSES**, where it previously
reported 5 unparseable records. Both improvements came from `main`, not from
this branch. **Zero errors name an MCE record.**
