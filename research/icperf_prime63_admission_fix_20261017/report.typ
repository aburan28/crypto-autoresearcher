#set page(width: 210mm, height: 297mm, margin: 17mm)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")
= Prime63 prospective admission repair

TASK-20261017-37ebda · GOAL-ICPERF-e6b6a4 · 2026-10-17

This report records engineering observations only. No full-width solver call
or experiment status transition occurred.

#figure(image("diagram.svg", width: 100%), caption: [Both entry points require repository admission before task output or Sage work. The future scientific claim-positive path is pending.])

== Implementation

The new launcher calls `load_plan`, `authorize`, and the public selector core
`newest_runnable` for the exact experiment. It requires a ready row binding
the same trial plan path and SHA256. The parent checks before task scratch or
run output. The child checks independently before request processing or Sage
work. Caller approval strings are not authority. The archived 18-file source
is unchanged; all 27 request cells match it.

`authorize` internally uses a temporary dispatcher render and subprocess as
part of admission. These are distinct from task scratch, output, or Sage
work, all of which occur only after the gate succeeds.

== Engineering controls

Latest tests: 9 passed. Ten refusal conditions were injected at each of two
entry points (20 total); none created task scratch, run output, or a worker
spawn. The real CLI rejected an unfrozen plan in both modes. A mocked positive
path forwarded the exact plan, owner, and epoch through 27 commands. Guards
remain 300 s per call, 8 GiB RSS and scratch, 64 models, and 4 h panel wall.

An earlier intermediate test failed because its invalid-plan fixture was
outside the checkout. The repository gate refused it; raw stderr preserves
the failure and corrected pass.

== Pending boundary

A real positive test requires a frozen approved EXP, ordinary selector ready
state, and published live executor claim. The exact future packet must pass
`experiment_preapproval.py --packet` before scientific approval. Solving
degree, relation yield, rank, linear algebra, target discrete log, matched
rho, and end-to-end speed delta are unmeasured.

Exact hashes, commands, environment, and all controls are in the companion
machine-readable files.
