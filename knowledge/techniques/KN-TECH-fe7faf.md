---
id: KN-TECH-fe7faf
type: technique
title: Binding the multiplicity of shared output sources closed lost-record detection where it applied, but a lost launch that writes nothing has no source to count; bind presence per launch kind, with evidence written independently of the recorder, over the launcher's closed set of call sites
tags: [protocol-amendment, acceptance-reading, recording-layer, recorder-gap, lost-record, presence, multiplicity, independent-count, launch-kind, call-site-closure, definitional-fail-open, fail-closed, red-team, known-answer-control, nearby-object-control, governance, methodology]
confidence: reported
complexity: >-
  not a cost model - a design rule for a verdict layer that must FAIL a
  package when a launch of the frozen code was not recorded. The operative
  quantities are, per launch KIND, (a) whether some evidence of the launch is
  written independently of the launch recorder, (b) whether that evidence is
  written on every path the launch occurs on, including a child that fails
  before writing anything, and (c) whether the set of launch kinds is closed
  (a finite set of call sites of one launcher in hash-bound code)
applicability: >-
  every recording or verdict layer around frozen code that must detect a
  lost per-launch record, in particular one whose launches include children
  that can fail before writing any output file; and, by extension, any
  "every event was recorded" test that relies on the artifacts the events
  leave behind
source_refs: [DEC-20260924-babd04, DEC-20260924-1d7614, CORR-20260924-c248d6, CORR-20260924-5c3086, AMD-EXP-GFPN-05ff43-20260924-attcount, AMD-EXP-GFPN-05ff43-20260924-launchkind, AMD-EXP-GFPN-05ff43-20260924-gapattr, TASK-20260924-be2daf, TASK-20260924-682890, TASK-20260924-2a7c7f, TASK-20260924-d897a6, KN-TECH-175a62, KN-TECH-79d6b9, DEC-20260924-e52eec, EXP-GFPN-05ff43]
proof_status: empirical_only
proof_refs:
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.yaml
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-be2daf/review-report.md
  - ledger/decisions/DEC-20260924-babd04.yaml
  - ledger/decisions/DEC-20260924-1d7614.yaml
added: '2026-09-25'
superseded_by: null
---

## What this note is, and is not

A note about **protocol method**, amending `KN-TECH-175a62` by a new entry.
`KN-TECH-175a62` is not edited and is not superseded: what it records about
positive attribution against real listings, and about binding the
multiplicity of a shared source, still stands. This entry records that its
section 4 rule, **as stated**, was incomplete, and what the next round of the
same lineage showed about why.

It is drawn from one experiment of one campaign (`EXP-GFPN-05ff43`,
`GOAL-GFPN-380702`) and one independent zero-run review
(`TASK-20260924-be2daf`, archived by `TASK-20260924-682890`, decided in
`DEC-20260924-babd04`). It is **not** a finding about any GFPN object, about D,
about `H-GFPN-9a29be` or `HEUR-GFPN-DFLAT`, or about the security of any curve,
and nothing in it is a mathematical result. No package of the repaired
protocol has run.

## 1. What the previous note asked to be tested

`KN-TECH-175a62` section 4: "For each positive source an attribution rule
reads, count the launch records that carry it. If the count can exceed one on
an ordinary path, bind it to a count written independently ... Where the
count should be one, require uniqueness." Its section 6: "Whether binding
multiplicity to independent counts closes CX-1 without refusing a planned
basis is the question of the next review. This note will need amending if
that fails." The draft that implemented the rule (`attcount`, RI-1) counted
the solver launches of each tag against the resolve layer's per-attempt
records, pass-through records, re-solve events and site counters, and
required every other output path to be carried by at most one launch record.

## 2. Where it held

On its own ground the rule held (review-report.yaml 163-168, 198-210,
228-234, 267-298):

- every lost-record construction at a solver or health launch the review
  built, including the previous round's CX-1 family and eleven single
  removals among 2, 3 and 6 attempts, became a named count gap and FAIL,
  where the previous rule gave PASS;
- no count the rule reads was derived from the launch records themselves
  (the circular case the Coordinator's prior thought likeliest);
- it refused no ordinary outcome: 85 reconstructed (site, tag) rows over the
  four archived gate packages, no mismatch; thirteen constructed normal
  outcomes; every PASS row of the earlier census.

## 3. Where it failed, and why

The review broke the no-fail-open joint with one object, **CX-A**
(397-442). A callgrind child is launched once per solved tag. If the child
fails to open its own stdout file (the frozen child opens it before any
exec, and exits on any exception), it leaves **no file at all**. Lose that
launch's record, and nothing notices: no file is unattributed, the counts
cover only solver launches, and uniqueness is trivially met. The package
PASSes while, by the lineage's definitions, a created child with no record
has no recorded cap read-back (definition (ii), with an absent record read as
"not class (A) or (C)"). The gp launch is in the same position once its
pre-launch script is listed as a non-launch write (CX-A-gp).

**What that shows.** The section 4 rule is stated **per positive source**. A
launch that writes nothing has no positive source, so there is nothing to
count and nothing to be unique. Uniqueness bounds **duplication** (a second
record for one path FAILs); it does not bound **loss**. The property the gap
test exists for is: *every launch that happened is recorded*. That is a lower
bound per launch, and it needs, for every launch kind, evidence of the launch
that

1. is written **independently of the launch recorder** (by the frozen code or
   by a different layer), and
2. is written **whatever the child does** - before the launch, or into the
   frozen function's returned result - and never depends on files the child
   writes, because a child can fail before writing any.

Files the child writes are good evidence of *which* record a file belongs to
(section 2 of `KN-TECH-175a62`); they are not evidence that a launch
happened.

## 4. The rule this suggests

Enumerate the **launch kinds** by the call sites of the launcher, not by the
execution paths of the code. Here the production launches are the calls of
one frozen function at six sites in hash-bound code (child job, solver at two
sites, callgrind, comparator, gp). For each kind name a **lost-record
detector** meeting 1 and 2 above:

| kind | detector (written independently, whatever the child does) |
|---|---|
| child job | the spec file the parent writes before the launch and names in argv |
| solver (both sites) | the resolve layer's per-attempt records, pass-through records, events and counters |
| callgrind | a presence bit of the returned solve result's callgrind key, copied by the resolve layer |
| comparator | the frozen driver's own record of the comparator child in its result file |
| gp | the script the parent writes before the launch and names in argv (so it must not be listed as a non-launch write) |

Then add a **catch-all** (a launch record of none of the known kinds FAILs)
and a **closure check** at stage time (the call sites are exactly the listed
ones; anything else STOPs). This is still an enumeration, but unlike the
path enumerations `KN-TECH-79d6b9` warns about it has a **floor**: a finite
set of call sites of one function in code whose hash is bound.

The successor draft `AMD-EXP-GFPN-05ff43-20260924-launchkind` (RJ-1..RJ-4)
does this. **It is a draft under review (`TASK-20260924-d897a6`), not a
validated technique.** Its declared limit (RGL-10): a loss that removes a
launch record together with every detector of it consistently is not seen by
the detectors; it still FAILs whenever the launch left a file, so the
undetected class is the consistent loss of a launch that left no file.

One constraint shaped the choice of detector: an earlier approved condition
makes the callgrind-site records "recorded and reported only", so a verdict
may not gate on them. The presence bit is taken from the returned result
instead. **Check the approved conditions before choosing a detector**, or the
repair stops its own stage.

## 5. Other points from the same review

- **A definition that classifies by record is fail-open on a lost record of a
  child that provably did nothing.** CX-A's child could not have executed its
  argv (no stdout file means it never reached the line before exec). The
  definitions ask whether a *record* shows the child could not have executed;
  with no record, they cannot. The deciding act refused to narrow the
  definition after the break and repaired the rule instead, so that the
  verdict never depends on inferring execution from a missing file.
- **The nearby-object control located the break exactly.** The same no-file,
  lost-record construction on a solver launch (LN-7a) FAILed under the counts;
  on a callgrind launch (CX-A) it PASSed. The separator was the absence of an
  independent count for launches whose stdout is not the solver log - a
  precise statement of the missing rule.
- **The prior aimed at depth; the break came from breadth.** The Coordinator
  expected the counts to fail by being circular or by being lost in the same
  atomic write. Neither happened; a launch kind outside the counts did. When
  a rule is written to close one route, attack the other kinds of the same
  object before its internals.
- **Development expectations under the full rule set, again.** The draft's
  discriminating control expected PASS on objects altered in place, which a
  carried whole-file hash check FAILs by construction; its stand-in level was
  unstated (FC-1, FC-6). Stating such expectations at the gap level, and
  placing stand-ins beneath the wrappers, repairs both (repeating
  `KN-TECH-79d6b9` section 3 and `KN-TECH-175a62` section 5).

## 6. Confidence and limits of the evidence

`reported`, not `established`.

- **One campaign, one experiment, one lineage, one reviewer per round.** The
  reviewer's context was independent of the author in context, authorship and
  inputs, not in model (682890 receipt, session arrangement). Its context was
  compacted once (its DV-1) and every verdict-cited line was re-read after;
  some pre-compaction inline commands survive only in summary form (its DV-8).
- **CX-A is a constructed sequence** under a lost-record premise with no
  ordinary path found, plus a recalled operating-system behaviour (an open
  that fails without creating the file). It is not an observed event, and its
  child could not have run outside its cap.
- **The count checks are static and reconstructed** from four archived
  packages of the previous protocol layer.
- **The per-kind remedy is unreviewed.** Whether every detector is written on
  every path its launch occurs on, and refuses no planned basis, is the
  question of the next review. This note will need amending if that fails.
- **Nothing here is evidence about any mathematical object.**
