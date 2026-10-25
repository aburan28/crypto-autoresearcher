#set page(paper: "a4", margin: 19mm)
#set text(font: "Helvetica", size: 10pt)
#set par(leading: 0.55em)
= ECPP cohort implementation status
2026-10-24 · Engineering snapshot through proposal v3

*Named orders executed: 0. No scientific experiment approved.*

== Recorded attempts
#table(columns: (0.6fr, 1.25fr, 2.9fr), inset: 5pt,
 [Draft], [Unittest output], [Reported defect],
 [v1], [4 tests; 1 failure], [Recursive-N and D regex patterns miss the printed lines.],
 [v2], [5 tests; 1 failure, 1 error], [Captured default catalog path; duplicate archived provenance collected recursively.],
 [v3], [5 tests; 2 errors], [Dictionary treated as a list; nonexistent D=1 catalog entry required.],
)
All three source proposals were materialized verbatim. Syntax compilation completed. These are revisions of one unfinished implementation, not independent curve measurements. Exact source and test logs are retained and hash-bound in source-bindings.json. The capturing shell ended with cat; the table reports preserved unittest output, not separately captured process exits.

#figure(image("status.svg", width: 100%, height: 91mm, fit: "contain"), caption: [Admission state. Dashed edge is prospective.])

The administrative goal, question, lane and zero-run implementation claim are published. This removes the earlier missing-lane gap. No scientific specification or trial plan exists for the reserved experiment identifier.

#pagebreak()
== The specific implementation obstruction
The v3 source still lacks copied binding-manifest bytes, private image-cache redirection, complete checker-side frozen-input and prior-corpus validation, and a realistic full driver-to-checker mocked fixture. Passing helper tests alone would not meet the canonical task gate. This draft is not implementation-ready.

The next engineering check must simulate the actual supervisor startup files and replace the entire legacy-library boundary with a fake. It must pass both admitted and censored fake outputs through the independent checker, then mutate identities, bindings, statuses, traces, certificates and raw artifacts. No original execute_case, vm or legacy executable may run during this task.

== Runtime calibration is separate
The original exact OpenAI/Terra Executor session is verified at medium effort. A stronger-effort request passed the public per-task resolver, but the native probe refused before launching with reasoning_effort_policy_mismatch. That helper resolves its default effort before comparison. The conditional amendment is ineffective in this snapshot; no higher-effort task execution is asserted. The original verified route remains available.

== Scientific boundary
These tests give no legacy-program outcome on a cohort order. They identify no common curve property or historical rejection criterion. Original caller code, candidate visitation and rejection logs remain unknown. Complete implementation, archival, actual preapproval, committed approval and the ready-state check still precede a separate run invocation.

The canonical admission graph is updated for the scoped lane and failed mock suites. No mathematical frontier, isogeny, endomorphism or weakness graph changes. The existing problem record and index carry the implementation gap and checkable exit criteria. Earlier report PDFs remain historical snapshots.

== Evidence and provenance
Internal retrieved artifacts: BATCH-08d006 / executor-implementation-v1 through v3 response.json and tests.log; implementation-attempts-custody-v1.json; executor-high-probe-v1.json. Source-bindings.json gives exact repository paths and SHA-256 values. Canonical task: TASK-20261024-4f1bf4; archival task: TASK-20261024-b17301. The unfinished source has not been archived as a completed task.
