---
id: KN-TECH-d45927
type: technique
title: Per-launch-kind presence detectors held under independent review; post-return detectors lean on the raise path, co-located detectors shrink the consistent-loss residual, and detector tables must be written in the records' own coordinates
tags: [protocol-amendment, acceptance-reading, recording-layer, recorder-gap, lost-record, presence, launch-kind, call-site-closure, consistent-loss, fail-closed, deterministic-reading, red-team, known-answer-control, nearby-object-control, governance, methodology]
confidence: reported
complexity: >-
  not a cost model - a design rule for a verdict layer that must FAIL a
  package when a launch of the frozen code was not recorded. The operative
  quantities are, per launch KIND, (a) whether its lost-record detector is
  written before the launch or into the launching function's returned result,
  (b) whether the detector shares a record with the evidence of a launch that
  always leaves files, and (c) whether every path, closure and consumer rule
  that reads the detector is stated in the coordinates the records carry
applicability: >-
  every recording or verdict layer around frozen code that detects lost
  per-launch records by evidence written independently of the launch
  recorder, in particular after a per-kind detector table has been designed
  (KN-TECH-fe7faf) and before it is implemented
source_refs: [DEC-20260924-daf670, DEC-20260924-babd04, CORR-20260924-19154c, AMD-EXP-GFPN-05ff43-20260924-launchkind, AMD-EXP-GFPN-05ff43-20260924-attcount, TASK-20260924-d897a6, TASK-20260924-68cf6b, TASK-20260924-a571c7, TASK-20260924-d91a96, KN-TECH-fe7faf, KN-TECH-175a62, KN-TECH-79d6b9, DEC-20260924-e52eec, EXP-GFPN-05ff43]
proof_status: empirical_only
proof_refs:
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.yaml
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-d897a6/review-report.md
  - ledger/decisions/DEC-20260924-daf670.yaml
  - ledger/corrections/CORR-20260924-19154c.yaml
added: '2026-09-25'
superseded_by: null
---

## What this note is, and is not

A note about **protocol method**, amending `KN-TECH-fe7faf` by a new entry.
`KN-TECH-fe7faf` is not edited and is not superseded: its rule stands. That
note described its per-kind remedy as "a draft under review ..., not a
validated technique" and said it "will need amending if that fails". This
entry records that the remedy **held** under the review it was waiting for,
and three refinements that review surfaced.

It is drawn from one experiment of one campaign (`EXP-GFPN-05ff43`,
`GOAL-GFPN-380702`) and one independent zero-run review
(`TASK-20260924-d897a6`, archived by `TASK-20260924-68cf6b`, decided in
`DEC-20260924-daf670`, which approved the draft with conditions). It is
**not** a finding about any GFPN object, about D, about `H-GFPN-9a29be` or
`HEUR-GFPN-DFLAT`, or about the security of any curve, and nothing in it is a
mathematical result. The layer the rule describes has **not yet been
implemented**; no package of the approved protocol has run.

## 1. What held

The draft `AMD-EXP-GFPN-05ff43-20260924-launchkind` gave each of the six
production call sites of one frozen launcher a lost-record detector written
independently of the launch recorder (a spec file or script written before
the launch; a presence bit of the returned result; the driver's own record of
its child; the resolve layer's per-attempt records and counters), an
unknown-kind catch-all and a stage-time closure check. The review found
(review-report.yaml 314-535, 537-593, 829-835):

- every single lost launch record, at each of the six kinds, on every child
  path constructed (refusal before fork, failure before the stdout open, a
  set-limit failure, a cap mismatch, exec, and an escaped child), is a named
  gap or a recorder gap and FAILs;
- no detector is derived from the launch records;
- the call-site set has a floor: twelve calls of the launcher in the scanned
  trees, six in production, none reachable any other way;
- no ordinary outcome is refused (85 reconstructed rows on four archived
  packages, 0 of 683 files unattributed);
- the **nearby-object control** worked as intended: weakening the one
  equality written for the callgrind kind to "at most" made the previous
  round's counterexample PASS again (253-259), so the repair's effect is
  attributable to that clause.

Of the eight drafts of this lineage since `readbackcover`, it is the first
whose pre-declared readings all held; the seven before it each failed one.

## 2. Refinements

**(a) A detector written into the returned result depends on the raise path.**
Evidence written *before* the launch (the spec file, the gp script) exists on
every path the launch occurs on. Evidence written *after* it - a key of the
returned result, or the driver's record of its child - is absent whenever the
launching function raises after launching. That is sound here only because a
raise ends the package in FAIL and leaves the launch record unmatched, which
is itself a count gap (the draft's RGL-11; review 403-410). **For every
post-return detector, state the raise-after-launch path explicitly and show
that it FAILs by some other rule.** Where it would not, the detector is
incomplete.

**(b) Co-locating a detector with an unavoidable sibling's evidence empties
the consistent-loss residual.** The declared residual of such layers is a
loss that removes a launch record *and* every detector bound to it together.
Per kind, that residual is non-empty where the only detector is a single file
or record (the solver launches; the child job and gp kinds if their pre-launch
file is also removed) and **empty** where the detector sits in the same record
as the evidence of a launch that must precede it and always leaves files: the
callgrind presence bit lives in the solver attempt record, callgrind runs only
after an ok solver launch, and so no consistent loss escapes (review 972-981;
`CORR-20260924-19154c` item 1). **When choosing where a detector lives, prefer
a record that also binds a launch that always leaves files.**

**(c) Write the detector table in the records' own coordinates, name the
recorder's own call in the closure, and extend every closed consumer list.**
Seven of the review's eight fail-closed findings were reading ambiguities of
the draft's own words, each a stage-time stop until a reading was recorded
(review 866-955):

- the detector forms were written relative to the package while the records
  carry absolute paths (a literal reading makes every launch unknown-kind);
- the closure item "no new function calls the launcher" caught the launch
  recorder itself, which another clause requires to call the original;
- a closed list of permitted consumers of a record field was not extended
  when later clauses added consumers;
- a development path-value rule listed values for substitution and then
  stopped on the form in which those same values carry the path;
- a stand-in level stated by direct call either excluded the needed stand-in
  or admitted one at the recorder's slot;
- a derived-value definition could classify a key-presence read as a read of
  the record stored under the key.

None was a break, and each was resolved by a recorded reading that removes no
check (`DEC-20260924-daf670` LKA-4..LKA-10). The cost was avoidable. **Before
review, state every path in the coordinates of the record that carries it;
name the recorder as the one permitted caller in any closure item, and check
that closure by listing every load of the launcher, not only calls through
its public names; and when adding a consumer of a field that an earlier
clause closed, extend that clause's list in the same text.**

A fourth, smaller point: a recorder defect that writes a detector wrongly
together with a lost record (review RP-5) is caught at stage time if the
**unaltered** discriminating object is also run through the positive control.
Run it there, not only its altered copies.

## 3. What remains untested

- **The delivered code.** Every statement above is about rule text and a
  static reading of frozen code. The r4 stage (`TASK-20260924-d91a96`) runs
  the development checks on the implementation; if they show a single lost
  record that does not FAIL, or a seventh launch site, this note needs
  amending again (and the approving decision reconsiders the one-record-per-
  launch alternative, option IE).
- **The declared residual** (a consistent loss of a record and every detector
  of a no-file launch) is declared, not closed. A frozen per-call record the
  health check already writes could bind the S-2 solver launches further; it
  was recorded, not adopted (`DEC-20260924-daf670`
  disposition.deprioritized).

## 4. Confidence and limits of the evidence

`reported`, not `established`.

- **One campaign, one experiment, one lineage, one reviewer per round.** The
  reviewer's context was independent of the author in context, authorship and
  inputs, not in model (68cf6b receipt, session arrangement). Its context was
  compacted once (its D-4) and every verdict-cited line was re-read; two no-op
  inline programs ran against its card's rule (D-2, D-5); four
  pre-compaction command entries survive only in abbreviated form (D-8). The
  deciding act accepted each with a limit.
- **Every counterexample considered is a constructed sequence** under a
  stated premise, several relying on recalled operating-system behaviour (an
  open that fails without creating the file).
- **The count checks are static and reconstructed** from four archived
  packages of the previous protocol layer.
- **Nothing here is evidence about any mathematical object.**
