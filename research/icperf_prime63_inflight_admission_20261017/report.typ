#set page(paper: "us-letter", margin: 0.60in)
#set text(font: "New Computer Modern", size: 9pt)
#set par(leading: 0.55em)
#set heading(numbering: none)

= Prime63 in-flight admission engineering record

TASK-20261017-7fbab5  •  GOAL-ICPERF-e6b6a4  •  2026-10-17

This report records engineering observations only. It asserts no scientific
experiment status, solver performance, relation yield, or end-to-end gain.

== Scope

The successor preserves 27 frozen requests: six planted public controls and
21 natural systems across coset, random, and small-x arms at m=2 through 8.
The unchanged guards are 300 seconds per cell, 8 GiB RSS, 8 GiB scratch,
64 models, and four hours per panel. The two prior launcher source hashes
matched their archives.

The ordinary selector must say *ready* before dispatch. The standard
supervisor creates the run directory and `launch.json` before the driver
starts, changing the one-trial selector state to `needs_reconciliation`.
The new admission path accepts that state only when the write-once launch
record binds the exact plan SHA256, trial/run IDs, commands and a canonical
absolute or repository-relative plan path,
live owner/epoch claim, and fresh repository authorization. Parent and child
each recheck these facts before additional task output or Sage work.

#figure(image("diagram.svg", width: 94%), caption: [Observed fixture order and refusal boundary. Synthetic approval and claim do not establish admission for a future scientific trial.])

== Recorded engineering controls

Ten final tests passed. The one-trial fixture used the real standard
supervisor, a disposable local Git repository, and real Python driver and
checker subprocesses. It observed `ready` before dispatch and exact bound
`needs_reconciliation` in both subprocesses. One fixture trial validated,
the second attempt was refused, and zero Sage processes started.

Seven altered launch records were refused. A repository-relative plan token
resolved to the exact frozen plan; a changed token was refused. Changed
source, wrong owner/epoch,
missing or expired claim, selector refusal, and prior receipt were also
refused without additional task output. A small-prime exact checker accepted
one polynomial/full-point root and rejected five altered objects. A raw
archive check rejected changed bytes and passed replay with disk cell files
removed. A bounded positive remained censored; a forged `ok` response without
the planted witness was rejected. The 27-request schedule matched the
archived launcher bytewise.
The mock panel driver emitted a schema-valid manifest.

The first goal-lane publish attempt hit a sandbox Git index-lock denial;
the same write-once claim was subsequently committed and pushed at
`450209b3d2`. A repository `ResourceWarning` appears in final stderr;
all ten tests passed. Exact commands, hashes, environment and raw logs
are in this task directory.

== Remaining gate

The Coordinator still needs an exact preapproval packet with
`approvable: true`, an archived one-trial scientific plan that declares
all fixed raw archive and receipt custody paths, and a genuine
ready-selector/live-claim positive run. The checker can replay its raw cells
from tar plus receipt without disk scratch files.
No full-width system was solved in this engineering task. Degree of
regularity, natural relation yield, useful rank, target work, matched rho,
and end-to-end runtime remain unmeasured.
