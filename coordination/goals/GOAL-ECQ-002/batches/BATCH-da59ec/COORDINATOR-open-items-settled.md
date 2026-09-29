# Coordinator: settling two open items raised by TASK-20260823-452f5f before review

Author: orchestrating session (Coordinator). Written BEFORE the blind reviewers were dispatched.

## O-MULTIMETRIC-EXPOSURE — settled by disclosure, not by concealment

`COORDINATOR-multimetric-check.md` carries the line "Not evidence; the reviewers have not seen it."
THAT LINE IS FALSE and the archive was right to catch it. The file is committed inside the batch
directory, which is in BOTH reviewers' declared `read_scope`, and it is reachable at the snapshot
sha. It cannot be unpublished.

The line is corrected here rather than by editing that file, so the mistake stays visible.

Settled as follows: BOTH REVIEWERS ARE TOLD TO READ IT AND TO ATTACK IT. A Coordinator analysis
sitting silently in a reviewer's read path is ambient bias — it anchors without ever being
examined. Named as an explicit target, it becomes a claim under test. The red team's joint J3 is
precisely about whether the Coordinator's target choice is sound, so its author's later reasoning
about that same choice is squarely in scope.

What the reviewers are told about it: it is Coordinator analysis, produced AFTER the producer
returned, unreviewed, and NOT evidence. Its method-class hypothesis — that high rank and small
size are served by different method classes, and that this campaign's A2 premise may be wrong at
the root — is UNESTABLISHED, rests on two families and an unreplicated program attribution, and is
offered to be knocked down.

## O-RUN-011-012-EQUAL — verified by the Coordinator, and it is sharper than reported

The archive observed, from hashes alone, that `raw-result.json` of RUN-ECQNAG-f88f54-011 and -012
share a sha256. Verified directly:

    -010 raw-result        b9ec01490827be44   19164 bytes
    -011 raw-result        563299c864b23d34   22681 bytes
    -012 raw-result        563299c864b23d34   22681 bytes
    nagao_height_budget    563299c864b23d34   22681 bytes

So -011, -012 and the deliverable are BYTE-IDENTICAL, all three.

THE HEADLINE NUMBER IS THE CORRECTED ONE. Both `nagao_height_budget.json` and
`cell_reachability.json` contain 1137 (seven occurrences each) and contain no occurrence of 1258.
The conclusion "0 of 1137 distinct measured fibres below any target" therefore rests on the
corrected union, not the double-counted one. Nothing in the result changes.

THE AUDIT TRAIL IS THE PROBLEM, NOT THE NUMBER. The producer declared -011 invalid SPECIFICALLY
because it "hard-coded fibre count 1258 double counted the 121-parameter overlap between the two
boxes; true union is 1137". Yet -011's own raw-result.json contains 1137 and is byte-identical to
its superseder. Only two readings are available:

  (a) The 1258 defect never reached raw-result.json, and -011's record was always correct — in
      which case the stated supersession reason does not describe what distinguishes the two runs,
      and the real difference (if any) is undocumented.
  (b) -011's record was written or overwritten after -012 ran — in which case an INVALID run's
      record displays a corrected output it did not produce, and AGENTS.md rule 2 (run records are
      immutable; corrections supersede, never overwrite) is engaged.

I DO NOT ADJUDICATE BETWEEN THESE. (b) would be a real immutability finding and is not mine to
declare from hashes; the validator has the artifacts, the scripts and the run wrapper, and can
determine which reading is true. Routed to TASK-20260823-72505a as a named check rather than left
as a generic open item.

Recorded so that neither reading can later be adopted silently: if (a), the supersession reason in
the execution report is inaccurate and should be corrected; if (b), the run record is not
trustworthy as a record of that run, and the batch owes a correction record.
