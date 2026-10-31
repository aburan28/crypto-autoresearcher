#set page(paper: "a4", margin: (x: 15mm, y: 13mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9pt, fill: rgb("172b3a"))
#set par(justify: false, leading: 0.45em, spacing: 0.55em)
#set heading(numbering: none)
#show heading.where(level: 1): set text(size: 16pt)
#show heading.where(level: 2): set text(size: 10.8pt)
= Cold active-support implementation
#text(size: 8pt)[DEC-20261030-af5218 · 30 October 2026 · fixed software checks]

*The reviewed cold-loop change is implemented and independently exercised.* The additive refuter preserves original labels and ordered certificates; its private per-solve bridge keeps the existing SAT callbacks and shared module identities. All six review joints hold. Accept this component at the frozen fixture scope; select a separately frozen cost comparison next.

== Observation: fixed executions completed
The producer ran one suite: *14 cold fixtures, 24 native slots, 392 parent assertions and 466 native assertions*. The fresh reviewer independently authored and ran one suite: *14 cold fixtures, 24 native slots and 1,387 passing named assertions*, including 50 malformed-input checks. Neither actor recorded a failed suite or retry. These assertion units have different harness granularity; no sum, ratio or statistical sample count is inferred.

#image("diagram.svg", width: 100%)
#text(size: 7.4pt)[Four predeclared software controls from the independent receipt; one fixed observation per actor, no sampling uncertainty. Counts include the overflowing call. All-active and early-constant cases retain equal search counts while adding eager support setup. These are correctness assertions, not performance samples.]

== Comparison: source and integration checks
#table(columns: (28%,72%), inset: 3.5pt, stroke: 0.4pt + rgb("ccd6df"),
  [*Joint*], [*Conclusion: holds*],
  [Source fidelity], [Kernel body differs only at the active iterator; validated baseline equals raw core on all 14 cases.],
  [Support and setup], [All generators scanned, even late/above-cap inputs; original masks/order and exact setup events preserved.],
  [Certificate and cap], [Ordered certificates match on baseline success; exact caps and free inactive bits retained.],
  [Private integration], [Frozen callbacks, alternating private instances and shared identities preserved.],
  [Coverage and failures], [Checked projected sets, corruption rejection, genuine partial/empty clauses and censorship preserved.],
  [Actual execution], [One independent invocation, 24 declared native slots, all assertions passed.],
)
#text(size: 7.4pt)[Source: research/prime_sat_active_support_implementation_20261030/TASK-20261030-6b3c1b/{review.md, independent-results.json, attestation.yaml}. Plot values and JSON locations are retained in report-inputs.json.]

#pagebreak()
= Scope, costs and the next comparison

== Inference: tested software fidelity
Each synthetic F5 family ran both refuters with model_only, partial_prefix and partial_prefix_aa. All 24 projected sets were complete and matched positive [3], negative [0,1,2], empty [] and auxiliary-fiber [0]. The suite checked real partial conflicts, empty clauses, fixed-assignment backtracking, zero-PC-budget leaf fallback, corrupt proofs/prefixes/models and missing coverage. A supplied closed-cover censored transcript remained censored. A checked witness covers its projected model; it does not make every assignment in that auxiliary fiber a root.

Python 3.12.8, python-sat 1.9.dev17 and Cadical195 were hash-bound. Native limits were degree 2, rows 256, PC calls 512, conflict/decision budgets 20,000 per call and 9 outer calls. Watchdogs were 5 seconds per native slot and 180 seconds per suite, with 2 GiB process address space. Timestamps serve custody, not timing evidence. The curve run_cell API was not exercised.

== Limitation: exact component boundary
Prime p and the frozen arithmetic semantics remain premises; input checks do not prove primality. Baseline success implies the tested exact certificate/cap behavior, while UNKNOWN does not prove non-refutability or require equal outcomes. This finite validation is not a universal implementation or formal proof. Eager support setup remains present on all-active and early-stop inputs, and its events cannot be silently added to or substituted for field work.

The reviewer could read target code and old helpers but was blinded to new producer tests/results/README/snapshot. The unchanged native independence gate passed. Requested gpt-6.1-sol/xhigh/fork-none is not authenticated serving model/provider/effective effort; capacity floors also remain unverified under the prospective amendment. There was no postdispatch exchange before sealing. No paper reread or novelty assessment was performed.

== Next action: retain the complete cost boundary
Design and freeze a paired residual/whole-search comparison for *quartic, membership, quadratic and quadratic_aa*, retaining A/A, controls, complementary-point reference, complete projected sets and signed witnesses. Use an additive exporter that keeps every per-call validation/support sidecar; the old exporter would omit this setup.

Charge both actual encoding constructions: the initial build and the checker's independent rebuild. Keep witness reconstruction/checking, private module loading, diagnostic copies/checkpoints, serialization, memory and failures. Preserve units and censoring. A timing claim needs its own frozen clock and isolation/control evidence. Warm reuse and callback bookkeeping remain separate factors. This recommendation does not design, approve or launch that experiment.

Earlier grouped raw-degree acceptance is unchanged: under its own even-s hypotheses, d_reg = 1+3s/2 in *2s variables* versus s+1 in *3s variables*, with a qualified mutant-closure upper bound (DEC-20261029-0857a9). No frontier, lead disposition or H/EXP/EV/KN/goal state changes here. Shared signed charts remain the separate continuation; no corpus promotion follows from this fixed component check.

== Evidence and custody
Producer source: 3d4d18598a7d; exact 15-path snapshot: 881f4ae2a91f. Independent source: 31ce804453; completed release: bc34a35380. Coordinator parsed both receipts, rehashed four review outputs and all 17 before/after bindings, and reran no test/checker. Producer JSON is preserved by a verified S3 gzip pointer; reviewer JSON remains inline. Actual hashes, native gate and canonical sources checked unchanged are in report-inputs.json. Root rendering/all-page inspection, exact ten-path archive and publication remain pending at composition.
