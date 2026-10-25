#set page(paper: "a4", margin: 22mm)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")

= Complete candidate graph discovery schedule

2026-10-22 · Conductor T-4766 · Candidate, unapproved

This schedule gives four separate controls their full discovery quota at each
fixed check vertex: `power_x`, graph-transported source `low_x`, `u2_native`,
and `u2_transport`. The last is the exact coordinate oracle for the same
vertex's native `low_x` base. Graph transport is separately compared with the
source `low_x` base, target by target.

#figure(image("arms.svg", width: 100%), caption: [Arm counts derived from the fixed graph paths and check strides.])

#table(
  columns: (auto, auto, auto, auto, auto, auto),
  inset: 5pt,
  [Stratum], [Vertices], [Check vertices], [Main arms], [Check arms], [Target probes],
  [P29], [2,049], [257], [6,147], [1,028], [58,777,600],
  [P37], [257], [65], [771], [260], [2,111,488],
  [Total], [2,306], [322], [6,918], [1,288], [60,889,088],
)

The write-once `discovery-arms.jsonl` has 8,206 unique rows. `manifest.json`
binds the archived walks, earlier independently verified main-arm inventory,
planner, schedule and checkpoint chains. The independent `verify.py` checked
all 8,206 rows, all 2,306 generator subgroup identities, and all 322 indexed
checkpoints; `verification.json` records a pass for schedule identity only.

No root, target, relation, rank, solve, runtime advantage, or Coordinator
approval is supplied here. The Coordinator must adopt or amend this mode,
freeze the execution contract and seeds, and issue admission before `run`
collects scientific targets. Fresh confirmation and complete same-point ECDLP
trials remain separate later stages. The additional 2,238,464 target probes
over the earlier three-control inventory are a workload count, not a runtime
estimate.
