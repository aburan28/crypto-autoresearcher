#set page(paper: "a4", margin: 16mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.45em)
#text(17pt, weight: "bold", [CPU receipt software correction: scoped acceptance])

TASK-20261026-73e6ca · DEC-20261026-49e865 · 26 October 2026

*Accept the bounded software correction; overall decision: revise.* Correct CPU units, honest counter coverage and failure retention are independently verified at published owner source 86ddd19f67e08160c22a0d8ba9a32a92321d18ad. No performance, complete process-tree, guard, mathematical, experiment-readiness or IC-improvement claim follows. Root must archive/publish this decision before downstream admission.

#image("diagram.svg", width: 100%)

== Observation and independent replay
Four producer outputs match programme snapshot b50185b81b7c145f04aae40eb0ef9770b427dc3d byte-for-byte. The Reviewer verified all 107 owner blobs, exact changed-path set, byte counts and the expectation seal, with no mismatches. Producer and fresh independent native builds each pass the same 17 fixed software fixtures under warnings as errors. Expectations were not changed to force a pass.

#table(columns: (43%, 28%, 29%), inset: 4pt, stroke: 0.4pt,
  [Input (sec,usec)], [Integer us], [Decimal seconds],
  [(0,1)], [1], [0.000001],
  [(0,10)], [10], [0.000010],
  [(0,999999)], [999999], [0.999999],
  [(1,0)], [1000000], [1.000000],
  [(1,1)], [1000001], [1.000001],
)

These deterministic formatter observations are software checks, not scientific timing samples. Negative, invalid-range and overflow inputs are rejected or explicitly unavailable. The prior unpadded seconds encoding is corrected; old receipts are preserved unchanged.

== Comparison of the assigned joint
TASK-20261026-64f987 owns cpu-units-coverage-and-failure-retention and reports holds. CPU-v2 separately records RUSAGE_SELF worker usage and RUSAGE_CHILDREN waited-child usage. Individual wait4 receipts remain diagnostic and are not added again. Child CPU is credited on reap; descendants are covered only when usage propagates through intervening waits. Full phase/process-tree CPU stays unknown.

Fake backend/helper checks preserve exit 17, SIGTERM, missing-exec 127 and malformed-output receipts before failure. Phase success/exception paths retain scoped counters/checkpoints. Additional independent software probes retain ECHILD/unavailable, counter regression and a nonstandard exception checkpoint. No breaking artifact was found. Actual cgroup supervisor execution was not tested.

#pagebreak()
#text(15pt, weight: "bold", [Independence, retained limits and next action])

== Current software round passes; old mathematical gaps remain
Recomputed check_review_independence.py exits 0: “1 report(s), every joint owned and attested, blindness respected, controls declared.” There is one fresh independent current-round review, no sibling review, no blind derivation assignment and no procedure deviation. The pass is only for this CPU-software round. Earlier DEC-20261026-cf272f retains its two schema/phase-list checker issues and unresolved mathematical/applicability scope. No old review or checker was rewritten or relaxed.

The initial producer strict build failure and five raw fake-helper vertex whitespace advisories remain preserved. Sealed expectations and raw outputs were not normalized after observation. This is source/receipt correctness, not a measured attack-cost advantage.

== Current source, runtime and scientific limits
Retained whole-library Cargo attempt 7 at base 27fca exits 101 for unchanged upstream unclosed delimiter src/cryptanalysis/binary_semaev_chain_sat.rs:1648. Log SHA256 c5c5cf1a7ee6b111b654532f5e94d28a09453219696205221acd2cdaf935be14. No clean current whole-suite pass is claimed; the older 4862/0/121 result belongs to b02. Hosted Actions account/payment availability still prevents check execution. No bypass is authorized.

Outer cgroupfs remains read-only. Managed Docker private delegation and Debian native loader/startup smoke provide a candidate local runtime, not qualified stopped-child placement, escaped-tree cleanup, real 1800 s watchdog, serial admission or exact 8 GiB OOM enforcement. Parent 16 GiB and /proc values alone do not establish required effective headroom. Guard qualification is separately prospective and conditional.

All 24 scientific cells remain not started. Reduction, extraction, theorem applicability, authoritative scientific admission, complete cost, current IC baseline comparison and independent replay remain unresolved. Future scientific execution still needs exact lane/queue and open-lane-count reconciliation, guard-qualified host/protocol, approval and publication. Standing research authorization is already satisfied.

== Exactly one next action
*Executor:* after this CPU decision/archive is published and actual fresh T-3 owner reservation and goal claim are admitted, perform bounded nonresearch guard qualification TASK-20261026-6374dd under prospective DEC-20261026-2a1490. Preserve the unchanged supervisor, actual 1800 s timer, fixed 5 classes, all failures/unknowns and the measured OOM headroom condition. No scientific execution follows automatically.

The full original goal remains joint-system reach-cost measurement, then verified improvement over the named current prime-field IC baseline with verified answers, full charged costs, matched rho and independent replay. Knowledge promotion: none; no new scientific finding or canonical scientific graph changes. The accompanying diagram is software coverage/gates, not scientific results.

== Evidence and provenance
P: TASK-20261026-dc4016 four archived outputs. R: TASK-20261026-64f987 report, canonical attestation and checks.json; Linux getrusage/wait4 semantics checked directly by Reviewer. C: independence-check.json retains actual checker command/result and exact input hashes. Published expectation hash 1fb61b6c45e4ef9bd0383519d255c0ea7084ca260038a0e0e5963622fcf5d4fe; owner expectation 18f166bff8b94e53d52d3ec8209e135512fa90c65193a15315f4901ae4728df2.

Native Coordinator: coordinator-orchestration-code, explicit openai-gpt61, gpt-6.1-sol/high; published claim coordinator-native-cpu-45aec1 epoch 1. No new API catalogue probe, serving attestation, fallback, degradation, worker or scientific call by this composition. Full linked source report: report.md. Root owns ledger receipt/archive/publication.
