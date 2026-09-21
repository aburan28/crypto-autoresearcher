# CORR-20260813-7e00d7 premerge custody disposition

The byte custody passed; the merge authorization did not.

Snapshot `112cab0155cf9164e0d296f5fe4cb03876c5906c` preserves both
branch and origin/main bodies of exactly seven canonical conflicts as fourteen
content-addressed opaque mirrors. Independent Validator
`TASK-20260813-2f7117` returned `PASS` for that exact custody boundary. Both
BATCH-080a9c histories remain reachable, and BATCH-1800b3's unqualified B080
parent references are permanently resolved to the branch bodies by ancestry.

Independent Red Team `TASK-20260813-97c505` returned `REVISE`. A two-parent
merge must resolve `ledger/goals/GOAL-ECDLP-001/goal.yaml`, yet neither existing
body is a truthful neutral integrated projection: the branch body has stale
pre-opening B180 pointers, while the origin/main body has stale preterminal
B080 pointers and hides the completed local B180 chain. Synthesizing a third
body during the merge would create an unreviewed authoritative projection.

The Red Team report also repeats one branch runtime-receipt SHA-256 incorrectly.
The report remains immutable; `CORR-20260813-7e00d7` records both the reported
and recomputed values. That transcription defect prevents treating the Red
Team table as an exact hash certificate, but it does not affect the independent
goal-pointer counterexample.

Accordingly `DEC-20260813-1169ad` blocks the merge. The only safe unqualified
B080 statement is `REVISE`, no EXP-SYC-b11b38 implementation or execution
authority, zero experiment runs, and no scientific status change. Finer reads
must name the source commit, original path, Git blob OID, and mirror SHA-256.

The next action is one additive zero-run repair: freeze a complete seven-path
merge-resolution manifest and exact neutral third-body goal projection against
the unchanged parents, snapshot them, and obtain fresh independent
`review-breakthrough` Validator and Red Team `PASS` verdicts at max effort.
There is no merge, experiment, ECDLP result, speedup, closure, or breakthrough
in this disposition.
