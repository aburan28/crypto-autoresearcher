#set page(paper: "a4", margin: 16mm)
#set text(size: 10pt)
= Quotient lifting: historical seed capacity

All 13 frozen historical maps passed hash identity and triangularity checks. Two independent enumeration directions agreed on all 13 inputs. These are exact structural counts from degree-four certificates; no degree-five closure or new LFD bound is claimed.

#table(columns: 5, inset: 4pt, [Seed], [Seed coordinates], [New border], [Working coordinates], [Map GiB], [T33a], [4888], [0], [4888], [0.190], [R35a], [5287], [0], [5287], [0.274], [R35b], [5287], [0], [5287], [0.274], [U35a], [5287], [0], [5287], [0.274], [U35b], [5287], [0], [5287], [0.274], [Q35a], [5287], [0], [5287], [0.274], [Q35b], [5287], [0], [5287], [0.274], [T33b], [4888], [0], [4888], [0.190], [C19a], [9253], [1488], [10741], [0.951], [P45a], [12742], [940], [13682], [2.472], [C19b], [6817], [715], [7532], [0.668], [R37a], [10066], [1554], [11620], [0.793], [R37b], [10066], [1554], [11620], [0.793])

#image("coordinates.svg", width: 100%)

The map column is a calculated bit payload, not measured RSS. It excludes seed storage, export coexistence, indices, multiplication tables, allocator overhead, the checker and other workspaces. No speed or frontier-admission claim follows.

The small-instance reference implementation passed 144 full-space closure comparisons and four native-producer/original-checker integration fixtures. Four corrupted constant images were rejected. These are software controls, not the frontier experiment.

Next: implement a native producer with checked allocations, cross-check it against the reference and dense engine, then freeze a new degree-five run. A lower bound of six requires independent certificate acceptance and a checked codimension strictly larger than the exact solution count. Killing the constant in an over-approximating quotient is inconclusive for the true closure.

Evidence: `raw/*.json`, `export.json`, `profile-plan.json`; frozen protocol `../../profile-protocol-v2.json`. Shared-host timing is invalid. Version 1 had no executions; version 2 corrected the source commit before profiling.
