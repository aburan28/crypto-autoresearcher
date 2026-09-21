# Coordinator reconciliation — TASK-20260807-dcfaee

Reconciles the dispatch_queue.json / ledger state mismatch reported against
`TASK-20260805-a1c3f9`, and dispositions the four findings in
`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/tasks/TASK-20260805-a1c3f9/independent_addendum_20260807.md`
(read in full before writing this memo). This memo is bookkeeping and
disposition only. It creates no hypothesis, runs no experiment, files no
KN-LIT entry, and makes no security assessment of ML-DSA/MLWE/MSIS/
SelfTargetMSIS, consistent with GOAL-MLDSA-001 BATCH-001's own scope.

## 1. Dispatch-queue state fix (done)

`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/dispatch_queue.json`
listed `TASK-20260805-a1c3f9` at `"state": "queued"`. That was stale: the
task's own `receipt.yaml` records `status: complete`, both required
independent reviews are committed
(`reviews/TASK-20260805-5b8a06/validation_report.yaml`,
verdict `accept_with_qualifications`; `reviews/TASK-20260805-9f2d71/`,
verdict `pass_with_constraints`), and a Coordinator decision already cites
the resulting evidence: `ledger/decisions/DEC-20260805-0d59ff.yaml`
(`evidence_refs: [EV-MLDSA-faf2ec]`), which records
`knowledge_promotion.promoted` for all five KN-LIT entries this task
proposed. I changed only the `"state"` field of the `TASK-20260805-a1c3f9`
entry from `"queued"` to `"completed"`, matching the pattern used by other
completed producer-task entries in this repo's dispatch queues (e.g.
`coordination/goals/GOAL-HQC-001/batches/BATCH-001/dispatch_queue.json`,
`TASK-20260802-6344ed`/`TASK-20260802-0100a5`: `"state": "completed"` with no
other field added at that level). No other field of that entry, and no other
task entry in the file, was touched.

**Left unfixed, deliberately, and why.** The four downstream chain entries in
the same queue (`TASK-20260805-d47e12` snapshot, `TASK-20260805-5b8a06`
validator, `TASK-20260805-9f2d71` red-team, `TASK-20260805-c60b84` ledger
archive) are *also* stale at `"state": "queued"` with `"commit_sha": null` in
their `archive` blocks, even though their artifacts exist and are cited by a
committed decision. I did not correct these in this task for two reasons:
(1) the explicit scope of this reconciliation names only
`TASK-20260805-a1c3f9`'s state field; (2) correcting the four archive-bearing
entries responsibly requires filling real `commit_sha`/`parent_sha`/
`path_sha256` values, which requires `git log`/`git show` access this task's
tool surface does not have (Read/Grep/Glob/Write/Edit only, no shell). Filing
placeholder or reconstructed hashes would itself be a fabrication under
AGENTS.md rule 9. **Recommendation:** a dedicated bookkeeping task with git
access should reconcile all four remaining entries against the actual commit
history the same way this task reconciled the first one.

I also note, but do not fix here, that the mismatch runs one level higher:
`ledger/goals/GOAL-MLDSA-001.yaml` `next_action` still reads "BATCH-001 is
queued and dispatch-ready ... Run TASK-20260805-a1c3f9", even though the
ledger shows the goal has since progressed through at least two further
batches on 2026-08-05 (`BATCH-66b482`, ideation — `DEC-20260805-ae4a96`;
`BATCH-214d98`, design/execution attempt blocked on PDF access —
`DEC-20260805-4843d6`, `DEC-20260805-64abe7`). Reconciling the goal head
correctly requires auditing all of BATCH-001, BATCH-66b482, and BATCH-214d98
and their decisions together, which is outside this task's declared write
scope (`coordination/.../tasks/TASK-20260807-dcfaee/` and the two files named
in the parent handoff) and outside what this addendum's findings warrant me
to touch. This is the same failure mode already documented for
GOAL-ECDLP-001 in `ledger/handoffs/TASK-20260807-48b8f2.yaml`
(goal-head fields left stale behind several completed batches). **This is
flagged for a dedicated goal-head reconciliation task, following that
precedent, before GOAL-MLDSA-001's next batch is opened.**

## 2. Disposition of the addendum's four findings

### (b) New candidate: Kosuge & Xagawa, "The Security of ML-DSA against Fault-Injection Attacks" (ASIACRYPT 2025 / ePrint 2025/904)

**Disposition: content is promotion-ready; filing needs the standard
independent-review step, not further source verification.**

The addendum fetched the primary ePrint page directly (HTTP 200), obtained
the verbatim abstract, and checked it against both the ten-entry declared
census and a corpus-wide grep — genuinely absent from the corpus. Its textual
match to RQ-MLDSA-001's own motivation phrase ("a formal proof covering only
a specific class of faults at internal function boundaries") is closer than
the already-filed KN-LIT-8ce0b5 (Gupta, NTT-twiddle-specific), and the
addendum correctly classifies it as IMPLEMENTATION/FAULT under AGENTS.md rule
7 (it says nothing about MLWE/MSIS/SelfTargetMSIS as mathematics). It is not
a duplicate of KN-LIT-8ce0b5 — different fault classes, both filable.

I am not filing it in this task: per the program's own PROPOSE/file
separation (the same one `TASK-20260805-a1c3f9` used, and per the task
instruction that only the Coordinator may promote knowledge entries and that
this task must not write into `knowledge/`), a new entry needs its own
producer→snapshot→independent-validator→independent-red-team→Coordinator-
ledger-archive chain before it becomes official, exactly as the original five
entries did. A second-pass session's own unreviewed fetch, however solid,
is not yet independently reviewed evidence. **Recommended follow-on:** a
dedicated idea-generator task (small — one already-sourced candidate) writing
`proposed_kn_lit_entries.md` for this paper (content can be drawn directly
from addendum §6b, already at the correct `citation_verified: web` /
`confidence: reported` honesty level), then the same validator + red-team +
ledger-archive chain. Task IDs are **not minted in this memo**; per
AGENTS.md rule 14 and the `TASK-20260807-48b8f2` precedent, whoever dispatches
this follow-on must mint them with `tools/allocate_id.py --next task --date
<YYYYMMDD>` and `--check` them before use.

### (c) New candidate: Jendral, Mattsson & Dubrova, FDTC 2024 pp. 34-43

**Disposition: needs verification — not yet actionable for filing.**

Bibliographic identity (authors, exact title, venue, pages) is confirmed via
dblp, a primary bibliographic index, so a bare bibliographic stub could in
principle be filed at `citation_verified: web` the way KN-LIT-4dadec and
KN-LIT-180ad5 were filed with partial provenance. I am not recommending that
here, for two compounding reasons:

1. Its specific content claims (s1 recovery, ~53%, Cortex-M4) reach this
   program only through convergent secondary WebSearch summaries, never a
   primary fetch, after eight independently logged and failed primary-source
   routes (IEEE Xplore, ResearchGate, KTH DiVA ×2, diva-portal.org,
   computer.org CSDL, Semantic Scholar). Filing those figures now, even
   flagged `confidence: unverified`, risks exactly the kind of
   secondary-reporting-presented-as-a-KN-LIT-claim the original task's own
   "relay, never launder" constraint exists to prevent. A bibliography-only
   stub with no content claims would be honest, but is of limited retrieval
   value and the addendum did not propose that narrower form.
2. This candidate is entangled with finding (e) below: multiple independent
   WebSearch results attribute RQ-MLDSA-001's *original* motivation figures
   ("s1", "Cortex-M4", "roughly 53%") to *this* three-author paper, not to
   the already-filed KN-LIT-4f3b80 (ePrint 2024/238, solo-authored, 58.2%).
   Filing this candidate now, before that identity question is resolved,
   risks creating a second entry that duplicates or conflicts with whatever
   correction KN-LIT-4f3b80 eventually needs. Sequencing matters here.

**Recommended follow-on:** fold into the same dedicated filing task as (b)
only after either (i) a primary abstract/full-text fetch succeeds for this
paper through a route not yet tried, or (ii) finding (e) is resolved by a
`/curate-knowledge` pass, whichever comes first. Until then this stays a
named, tracked gap — not silently dropped, not filed prematurely.

### (d)/(e) Citation-identity concern on the already-filed `KN-LIT-4f3b80`

**Disposition: flagged correction-needed, routed to a dedicated
`/curate-knowledge` pass. Not fixed, not adjudicated, in this task.**

`knowledge/literature/KN-LIT-4f3b80.md` records the title "A Single-Trace
Side-Channel Attack on ML-DSA: Practical Full-Key Recovery from a Single
Faulty Signature" at `identifiers.url: https://eprint.iacr.org/2024/238`. The
addendum independently re-fetched that exact URL in its own session and
reports (HTTP 200) that the page served there is titled "A Single Trace Fault
Injection Attack on Hedged CRYSTALS-Dilithium" (Jendral, sole author, FDTC
2024) — a different title. I did not re-fetch the URL myself in this task (my
tool surface here is Read/Grep/Glob/Write/Edit only, no network access), so I
am relaying the addendum's finding at its own hedging level: a specific,
checkable, logged HTTP 200 fetch from an independent second-pass session,
not yet independently validated or red-teamed itself. That is enough to
treat as a real, checkable discrepancy worth flagging under AGENTS.md rule 5
(never relay an unverified citation as verified), not enough for me to
adjudicate or fix here.

What the addendum's own analysis narrows the concern to: the recorded DOI
(`10.1109/FDTC64268.2024.00013`) and probability (0.582) in KN-LIT-4f3b80 DO
match what is served at that URL, so the underlying paper identity (ePrint
2024/238, the solo-authored Jendral paper) is very likely still correct —
only the *title field* appears mis-transcribed, plausibly drawn from the
closely related three-author paper in finding (c) instead of the paper the
URL and DOI actually point to.

I am explicitly **not** voiding, superseding, or editing KN-LIT-4f3b80 in
this task — the task instructions require routing this to a dedicated
`/curate-knowledge` pass rather than a same-task fix, and the addendum itself
declined to propose superseding `DEC-20260805-0d59ff` gate_2 on the same
evidence, for the same reason: the three-author paper's primary text remains
unread, so which paper the "~53%" figure actually belongs to is not yet
certain enough to relitigate a committed ruling. I note the entanglement for
the future correction task to weigh, but do not adjudicate gate_2 here.
**No coordinator_decision is warranted for this alone** (see §4) — a title-
field correction is bookkeeping once independently confirmed, not yet a
research-state judgment call, and gate_2's own correctness is a separate,
not-yet-resolved question this memo does not settle.

**Recommended follow-on:** a `/curate-knowledge` correction pass that (i)
independently re-fetches `https://eprint.iacr.org/2024/238` itself, (ii)
if confirmed, records a `correction` (per `templates/research-records.md`,
append-only — KN-LIT-4f3b80 is not edited or deleted) with the corrected
title and a note explaining the source of the original mis-transcription,
and (iii) separately assesses whether the entanglement with finding (c)
warrants revisiting `DEC-20260805-0d59ff` gate_2 — that assessment is a
Coordinator research-state judgment in its own right and does not belong in
this bookkeeping task.

### 6a. Upgrade: `KN-LIT-4dadec` `citation_verified: partial → read`

**Disposition: promotion-ready; process-pending like (b).**

The addendum obtained the full 65-page FIPS 204 standard text (via the
`Read` tool's native PDF parsing on the fetch tool's own cached bytes — a
route distinct from the fetch tool's summarizer, which failed both in the
original 2026-08-05 session and in this session's own first attempt) and
transcribed §3.2 (Computational Assumptions) and §3.4/§3.6.1 fn.3 (hedged vs.
deterministic, and FIPS 204's own cited fault-attack baseline) verbatim with
exact section references. This is exactly the SEEDING.md-sanctioned upgrade
path ("fetch the actual source; note the upgrade in the entry body") applied
correctly. I note in passing, for the same `/curate-knowledge` pass, that the
entry's existing `citation_verified: partial` is not one of SEEDING.md's
three canonical values (`web`/`read`/`false`) — a pre-existing minor schema
drift in the original filing, not something this task introduces or needs to
resolve to act on the upgrade.

I am not editing `knowledge/literature/KN-LIT-4dadec.md` in this task, for
the same PROPOSE/file separation reason as (b): only the Coordinator files,
and filing here is a ledger-archive act requiring the same independent-review
discipline the original entry went through. **Recommended follow-on:** fold
into the same dedicated filing task as (b), amending its `write_scope`/
`artifact_paths` to add `knowledge/literature/KN-LIT-4dadec.md` and
`knowledge/INDEX.md`, per the `GOAL-HQC-001` BATCH-001 precedent already
cited in this goal's own task cards.

## 3. Summary disposition table

| Finding | Disposition | Blocking factor |
|---|---|---|
| (a) queue state mismatch | Fixed in this task | none |
| (b) Kosuge & Xagawa (new) | Content ready; needs independent validator+red-team review before filing | process, not source verification |
| (c) Jendral/Mattsson/Dubrova FDTC2024 (new) | Needs verification | primary-source access (8 routes exhausted, more possible) AND resolution of (e) |
| (d)/(e) KN-LIT-4f3b80 title mismatch | Flagged correction-needed | routed to dedicated `/curate-knowledge` pass, not fixed here |
| KN-LIT-4dadec upgrade (partial→read) | Content ready; needs same filing process as (b) | process only |

## 4. Why no `coordinator_decision` was authored

None of the five items above required a research-state judgment beyond
bookkeeping: item (a) is a queue-field correction; (b) and the KN-LIT-4dadec
upgrade are content-ready proposals awaiting the standard review pipeline,
not yet a Coordinator ruling; (c) is source-blocked and explicitly deferred;
and (d)/(e) is a flagged concern explicitly routed to a dedicated correction
pass rather than adjudicated here, per the task's own instruction. No
hypothesis status, evidence strength, or KN-LIT record changed as a result of
this task. Per the task instructions ("do not manufacture one"), I did not
author a `coordinator_decision`.

## 5. What this task did NOT do

- Did not write into `knowledge/` or touch `knowledge/INDEX.md`.
- Did not edit `KN-LIT-4f3b80.md` or any other already-filed KN-LIT entry.
- Did not change `RQ-MLDSA-001` or `GOAL-MLDSA-001` status, `active_hypothesis_ids`, or `next_action`.
- Did not mint any new `KN-LIT-*` or `TASK-*` identifier; all follow-on work
  named above is described by objective only, for a future dispatcher to mint
  IDs via `tools/allocate_id.py` and `--check` them before use.
- Did not re-fetch any external source itself (no network tool available in
  this task); all claims about the addendum's own fetches are relayed at the
  addendum's own hedging level, per AGENTS.md rule 5.
