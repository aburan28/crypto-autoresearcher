---
id: KN-TECH-175a62
type: technique
title: Positive attribution of launch outputs held against real package listings, but a positive source shared by several launches attributes a lost launch's files to its sibling; bind the multiplicity of a shared source to an independently written count
tags: [protocol-amendment, acceptance-reading, recording-layer, recorder-gap, positive-evidence, attribution, listing-check, lost-record, multiplicity, independent-count, fail-closed, red-team, known-answer-control, governance, methodology]
confidence: reported
complexity: >-
  not a cost model - a design rule for a verdict layer that FAILs a package on
  any output file it cannot attribute to a recorded launch. The operative
  quantities are (a) which files of real archived packages a candidate
  attribution rule leaves unattributed, and (b) for each positive source the
  rule reads (an output path, an argv element, a spec file), how many launch
  records carry it; a source carried by more than one record is positive per
  file but not per launch
applicability: >-
  every recording or verdict layer around frozen code that must show that
  each file in a package was written by a recorded launch, in particular one
  whose frozen code re-runs a command with identical arguments and output
  paths (retries, re-solves, re-invocations); and, by extension, any
  "attributed to some record" test used to detect a lost record
source_refs: [DEC-20260924-1d7614, DEC-20260924-61b22c, DEC-20260924-844896, CORR-20260924-5c3086, CORR-20260924-3c831f, AMD-EXP-GFPN-05ff43-20260924-gapattr, AMD-EXP-GFPN-05ff43-20260924-childend, AMD-EXP-GFPN-05ff43-20260924-attcount, TASK-20260924-94cc33, TASK-20260924-93f3ca, TASK-20260924-1ecb7d, TASK-20260924-7e8a5d, TASK-20260924-27ea14, TASK-20260924-be2daf, KN-TECH-79d6b9, EXP-GFPN-05ff43]
proof_status: empirical_only
proof_refs:
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.md
  - ledger/decisions/DEC-20260924-1d7614.yaml
  - ledger/decisions/DEC-20260924-61b22c.yaml
added: '2026-09-24'
superseded_by: null
---

## What this note is, and is not

A note about **protocol method**, amending `KN-TECH-79d6b9` by a new entry.
`KN-TECH-79d6b9` is not edited and is not superseded: nothing in it is
withdrawn. This entry adds what the next round of the same lineage showed
about one of its rules, positive evidence, when that rule was applied to
**file attribution** and tested against **real archived package listings**.

It is drawn from one experiment of one campaign (`EXP-GFPN-05ff43`,
`GOAL-GFPN-380702`) and one independent zero-run review
(`TASK-20260924-94cc33`, archived by `TASK-20260924-93f3ca`, decided in
`DEC-20260924-1d7614`). It is **not** a finding about any GFPN object, about D,
about `H-GFPN-9a29be` or `HEUR-GFPN-DFLAT`, or about the security of any curve,
and nothing in it is a mathematical result. No package of the repaired
protocol has run.

## 1. The question the firm revisit asked

`DEC-20260924-61b22c` required this entry "once the review of gapattr has
tested positive attribution against the r3 gate listings". The previous draft
of the lineage (`childend`) had a gap rule that attributed a file only through
a launch record's output paths or argv; applied to the frozen code's ordinary
outputs it refused planned bases by design (the build and raw-grid children
write files named inside a spec file; the approved re-solve rule renames
attempt files). Its successor (`gapattr`, RH-1) replaced it with six positive
clauses, each reading one record: an output path; an exact argv path; the
value of a `--callgrind-out-file=` element; a directory only one argv names;
the `out` value of the spec file a child job's argv names; the renamed-files
list of a re-solve event.

## 2. Did positive attribution hold against the r3 gate listings? Yes.

The review applied the rule as worded to the full listings of the five output
directories of the four archived r3 gate packages, with launch sets
**reconstructed** from the files by the frozen naming (a reading of r3
artifacts under r4 rule text, never a result about any package):

| package | files | unattributed under the old rule (`childend` RG-4 (b)) | unattributed under RH-1 |
|---|---|---|---|
| RUN-GFPN-f6a21a | 284 | 16 meta + 4 npz | 0 |
| RUN-GFPN-902222 | 284 | 16 meta + 4 npz | 0 |
| RUN-GFPN-f5412a | 32 | 1 meta + 1 npz | 0 |
| RUN-GFPN-bfe956 | 83 | 11 meta + 7 npz | 0 |

(review-report.yaml 234-245 and 455-461.) It also attributed every file of
thirteen constructed normal outcomes the gate never produced (re-solves, a
failing and a timed-out callgrind child, cached and uncached builds, refusal
paths, the health and gp children; 462-475). The joint the Coordinator's prior
thought most likely to break (about one in three) held.

**What that shows.** The listing check reproduced, from the files alone, the
refusal the previous draft carried (16, 16, 1 and 11 unattributed meta files,
plus 4, 4, 1 and 7 npz files the census had not listed), and cleared the
successor on the same objects. **An attribution rule should be run against
real package listings before it is reviewed**, because that is where the
previous refusal would have been visible before the rule was written
(`DEC-20260924-61b22c` rationale; `CORR-20260924-3c831f` item 4).

## 3. What the listings could not show: multiplicity

The same review broke the no-fail-open joint with one family, CX-1
(657-757). At a tag the approved re-solve rule solves more than once, **every
attempt's launch record carries the same output paths and argv** (the frozen
solve builds them from the tag). The earlier attempts' files are renamed and
listed in the event; the last attempt's keep their names. Remove any one
attempt's launch record, and every file is still attributed: the final files
to a sibling record by output path and argv, the renamed files by the event
list to whichever record now sits k-th. No gap; PASS, while the read-back the
parent read for the lost attempt is in no launch record. Two removals of
three FAIL; under the old rule every case FAILs.

The break is in the **lost-record class**, not the foreign-process class, and
the review found no ordinary path and no documented interpreter behaviour
that loses a record without the recorder's own consistency check firing. It
was decided a counterexample anyway (`DEC-20260924-1d7614` R-CX-1) because the
lineage's own rules posit that case: they keep the gap test gating precisely
as "the second line of detection for a lost launch record", and the draft's
own development check expected the removal to FAIL and could not pass (FC-1).

**What that shows.** "Every file is named by some record's positive source" is
a statement **per file**. The property the gap test exists for is **per
launch**: a lost launch must leave something unattributed. The two coincide
only if each positive source is carried by one launch record. Where the frozen
code re-runs a command with identical arguments, the source is shared, and
positive attribution degenerates into the absence-based condition
`KN-TECH-79d6b9` section 4 warns about, one level down ("some other record
explains this file" standing in for "this launch was recorded"). A listing
check cannot see this, because a listing shows files, not how many launches
wrote them.

## 4. The rule this suggests

For each positive source an attribution rule reads, **count the launch records
that carry it**. If the count can exceed one on an ordinary path, bind it to a
count written **independently** in the recording process: by a different code
path that is incremented on each launch (here the resolve layer's per-attempt
records, its pass-through records, the event's attempts list,
`accepted_attempt`, the renamed-files keys and the per-site attempt
counters). A mismatch is a named gap. Where the count should be one, require
uniqueness. Attribute the unrenamed final files only to the last record.

The successor draft `AMD-EXP-GFPN-05ff43-20260924-attcount` (RI-1) does this.
It is the reviewer's own cheapest mutation, generalised. **It is a draft under
review (`TASK-20260924-be2daf`), not a validated technique.** Its declared limit
(RGL-9): the counts are written by the same process and the same single writer
as the launch records, so a loss that removes a record and every count of it
consistently, or a later alteration of the file, is not detected by the count.
It moves the premise from one lost record to a consistent loss across several
independently updated fields; it does not remove it.

## 5. Other points from the same review

- **Known-answer control with a weakened clause discriminated.** Weakening the
  spec-file clause to "every file under child/ is attributed" made a lost
  child-job record PASS (fail-open), while the worded clause FAILed it
  (190-259). The review's cheapest discriminating control for the new break is
  the draft's own development check, run under both rules; the successor
  makes that a required, discriminating development check.
- **A development check's expected answer must be derived under the full rule
  set** (repeating `KN-TECH-79d6b9` section 3): three of the draft's own
  development checks could not pass as worded (FC-1, FC-2), and "a scratch
  copy" at another root would have made every file a gap (FC-3).
- **`KN-TECH-79d6b9` section 4's remedy still had not failed.** Positive
  child-end evidence (`childend` RG-1) was not broken in this round. The
  foreign-process constructions (an escaped child exiting 97-99, exec'ing, a
  second live child) still have no supplying code in the repository or in the
  third-party Python text read; compiled extensions, one YAML library and
  interpreter shutdown remain unread (review 398-430).

## 6. Confidence and limits of the evidence

`reported`, not `established`.

- **One campaign, one experiment, one lineage, one reviewer per round.** The
  reviewer's context was independent of the author in context, authorship and
  inputs, not in model (93f3ca receipt, session arrangement). The reviewer's
  context was compacted once (its DV-1); it states that every cited line was
  re-read after the compaction or is in a scratch output reproduced verbatim.
- **The listing check is static and reconstructed.** Launch sets were
  reconstructed from file names; no r4 launch record exists. 683 files is the
  tested scale; the transfer to cells and addendum invocations assumes the
  same solver flags write the same files (review B-9).
- **CX-1 is a constructed sequence** under a lost-record premise with no
  ordinary path found. It is not an observed event.
- **The remedy is unreviewed.** Whether binding multiplicity to independent
  counts closes CX-1 without refusing a planned basis is the question of the
  next review. This note will need amending if that fails.
- **Nothing here is evidence about any mathematical object.**
