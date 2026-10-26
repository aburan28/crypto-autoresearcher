# Independent finite-stream integrity review

Independent validation of finite observation integrity only. This report makes no scientific hypothesis, attack, speedup, security, complete-S or prescribed-execution-proof verdict.

A fresh phase-one derivation was generated at 2026-10-26T06:30:40.398622Z, after its last read at 06:30:40.386171Z. The Coordinator seal at 06:31:39.053124Z and deliberate release at 06:33:33.695485Z were recorded as distinct authority boundary events; all protected reads followed release.

| B | m | attempts | accepted | U | rank | aug rank | nullity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | 8 | 229376 | 0 | 7 | 0 | 0 | 7 |
| 13 | 16 | 2293760 | 97 | 15 | 13 | 13 | 2 |
| 16 | 8 | 229376 | 0 | 7 | 0 | 0 | 7 |
| 16 | 16 | 2293760 | 67 | 15 | 9 | 9 | 6 |

The reviewer replayed every one of 4,587,520 m16 descriptors with independently written EC, polynomial, source-lift, interpolation, residual and canonical-identity code. All 128 status streams and branch commitments matched, including all rejected descriptors.

All 164 accepted E1 equations, principal polynomial/divisor witnesses, E2 sums and transported encodings passed. The fixed first4/last4/8 SHA-ranked sample is identified in math-verification.json; checking all rows is the explicitly wider scope. Every projected matrix, affine/augmented rank, pivot span, right kernel, rank progress and source checkpoint passed.

Both m8 reference cells were validation-replayed for 458,752 descriptors. All old8 descriptors and canonical keys embed under explicit fixture UID transport. There were zero historical accepted witnesses, so their empirical witness embedding is vacuous; a separate p101 positive witness tested the nonvacuous prefix path and the opposite-source alias path.

All 19 known-false copies were rejected. They cover source a+1 and seeded-uniform alternatives, native lift, U/anchor/pivot/kernel/affine/augmented rank, dropped/duplicated/changed statuses, missing/duplicated/reordered source blocks, prefix, transported encoding and alias key. Four separate logical-content pointer mutations were rejected during custody verification.

The 73 current native source/input bindings and all native receipt artifact hashes were rechecked. Three compressed remote-object representations were read from an existing public local cache; the remaining compressed raw representation was read from the repository. Stored SHA/size, gzip decoding and logical SHA/size matched, and 20 export file entries matched.

The reviewer made no fresh remote GET. Producer GET attestations and the parent-supplied publication custody are separate from this local byte audit. Historical source/input maps are retained as receipt-bound metadata; excluded historical private fixtures/helpers were not read or re-executed.

Counts and ranks describe exactly these two conditioned toy cases. There is no sampling uncertainty for this finite census, while implementation and custody limits remain. Native primitive-operation vectors reconcile with their stage subtotals, but were not independently instrumented. Pow internals, Python bookkeeping, general byte movement and a complete weighted S remain excluded. Clocks are diagnostic and are not a performance comparison.

The native export honestly leaves producer runtime, model, session and role null. No missing provenance was copied from planned metadata. No canonical scientific graph is changed: this exclusive-scope review adds its own evidence-linked chart, and the native graph artifacts were content-hash checked.

Evidence: [math-verification.json](math-verification.json), [control-verification.json](control-verification.json), [reference-verification.json](reference-verification.json), [custody-verification.json](custody-verification.json).

Runs: RUN-ECDLP-967315 and RUN-ECDLP-ea49a6. Task: TASK-20261025-2fe077. Claim tier: toy.

The Coordinator owns archival publication and any official research-state decision. Formal phase/independence and companion validation are performed by root against the final quiescent artifacts.
