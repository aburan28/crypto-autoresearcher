#set page(paper: "a4", margin: 17mm)
#set text(font: "Libertinus Serif", size: 9pt)
#set par(justify: false, leading: 0.45em)
#set heading(numbering: none)
= P-192 degree 50,341: terminal replay profile
#text(size: 9pt)[EXP-ISOU-32a530 / RUN-ISOU-93b2b3 / GOAL-ISOU-f30a07]
#parbreak()
Descriptive run report only. This records a completed operational attempt and its censored mathematical verification; it makes no evidence-review decision or frontier promotion.
#image("flow.svg", width: 100%)
== Attempt and native result
One requested replay, one started, one timed out, zero completed verifications; no scientific rerun. Native public status CENSORED, reason TIMEOUT, score null. Native worker elapsed 3,600,033 ms; worker exit code unavailable after termination. Public judge exit 3; thin adapter exit 0 acknowledges observation delivery. Start 2026-10-16 09:12:21 UTC; terminal 10:12:21 UTC. Hypothesis ID is null: this is instrumentation of a sealed map.
#table(columns: (1.8fr, 1fr, 1.8fr, 1fr), inset: 5pt, stroke: 0.4pt + luma(80%),
[OS real, measured], [3,600.05 s], [OS user, measured], [1,716.81 s],
[OS system, measured], [62.75 s], [CPU user + system, derived], [1,779.56 s],
[Sampled worker peak RSS], [250,052,608 bytes], [Unavailable RSS samples], [0],
[Worker sampled RSS limit], [8,589,934,592 bytes], [Sampling / monitor grace], [25 / 100 ms])
CPU covers the public native judge and waited descendants; it excludes compilation, orchestration and historical attempts. Shared Apple M4 Pro, 14 logical CPUs, 48 GiB RAM, Darwin arm64/macOS 26.6; launch load averages 41.25 / 44.40 / 45.45. These observations do not establish an isolated-host performance ratio.
== Completed trace stages and missing terminal data
#table(columns: (2.4fr, 1fr, 1.4fr), inset: 4pt, stroke: 0.4pt + luma(80%),
[Stage], [Wall difference], [Recorded state],
[Setup: loading / field parsing], [5 / 1 ms], [end / end],
[Registry / source subgroup], [10 / 0 ms], [end / end],
[Coefficient parsing / kernel degree], [32 / 0 ms], [end / end],
[Squarefree-kernel GCD], [21,671 ms], [end],
[Selected division-polynomial torsion], [2,001,627 ms], [end],
[Subgroup inverse], [23 ms], [end],
[Subgroup modular composition], [unavailable], [begin only])
Differences are derived as each recorded end timestamp minus its matching begin timestamp. Resolution is milliseconds; 0 ms does not imply no work. Total, attempt, map and kernel-validation parent stages also lack ends. The trace contains 23 parseable records, zero parse errors and zero terminal trace records. Parent stages nest; do not sum overlapping values. No final point/map admission is available.
== Identity, custody and controls
The sealed P-192 map contains one of two constructor-reported Frobenius eigenlines (PARTIAL coverage). Source and claimed codomain are identified by ICV1 slugs ending 52e4af59 and 0af73cab respectively; their complete field/equation identities are in report.md and the sealed map. Constructor self-checks remain distinct from this unfinished independent replay. Inputs were reused without regeneration.
#parbreak()
#text(size: 7.4pt)[
Source commit: e82d80feaf82d3730576ccd9137911b336f9dab8; dirty=false.\
Executable SHA256: b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b\
Map SHA256: 82e3951488c793c5901ecf1dfeb3ab072b7cda16730899330df7caa9832a170c\
Raw archive SHA256: 55c1c18440109a8c1e87c266a67e6d366cbfd64c988a86b5e52ff528126be0ae
]
#parbreak()
Inputs, snapshots and executable retained expected hashes. The 3,594,206-byte raw archive preserves 21 original files, per-file hashes and the metadata-only collector. All 8 released artifacts and 21 raw hashes were rechecked. Preparation controls: 94 passed, 0 failed; 1 helper definition ignored but invoked by its parent. No controls rerun here. Served model/effort unexposed. One observation: spread unavailable; diagram used because fewer than two comparable trials completed. Full commands, identities, original status-field differences and build receipts: report.md.
