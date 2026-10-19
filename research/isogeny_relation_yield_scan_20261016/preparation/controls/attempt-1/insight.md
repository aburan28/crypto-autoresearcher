# Input-preparation implementation control

**Question.** Does the new graph adapter deterministically produce valid
signed factor bases and the same accepted target coefficients across
isogenous vertices and arm rules, and can a separate arithmetic implementation
replay the prepared group equations?

**Workload.** P29 and P37 archived full walks; path indices 0 and 1;
`low_x`, `mid_x`, `random_x`, selected `power_x`, `u2_native`, and
`u2_transport`; eight fixed fixture targets per case. The roots were the
literal 32-byte sequences `B` and `T`, saved as hex in this directory.
They are implementation fixtures, not scientific target roots. Three
prepared fixtures are saved: P29 index 0 `low_x`, P29 index 1 `random_x`,
and P37 index 1 `u2_transport`.

**Revision and environment.** Base commit
`3f78e0521bce670ecb66b07718ca4dc9dbd61afd`; candidate source was the
uncommitted files in this preparation directory, bound by the subsequent
archive commit and file hashes. macOS arm64, Python 3.12.8. No hardware
speed comparison or profiler was run.

**Commands and raw outputs.** The commands were
`python3 research/isogeny_relation_yield_scan_20261016/preparation/test_prepare_graph_input.py`
and Python import of `verify_prepared_graph.verify` on the three saved
`prepared.txt`/`manifest.json` pairs with the two fixed root files. Both
exited 0; raw standard output and error are `test.stdout`, `test.stderr`,
`verify.stdout`, and `verify.stderr`. The fixture-generation command called
`prepare(..., target_count=8)` for the three listed cases and retained its
prepared bytes and metadata in their named subdirectories.
The separate `mutation-alpha/` control changes target 0's `alpha` by one,
updates the prepared-input digest, and retains the modified input, manifest,
and rejection result.

**Observations.** All 22 small arm/vertex cases passed the deterministic,
coefficient, group-law, and coordinate controls. The separate prepared-input
checker passed all three saved fixtures, replaying 512, 512, and 3,200 base
points respectively and eight targets in each. Its optional root replay
reproduced each prepared byte stream. Empty stderr files record no diagnostic
output. The fixture inputs are the raw artifacts; no relation collector was
invoked.
The mutated input was rejected with `target group equation failed`, showing
that the point-equation check runs beyond the input hash check.

**Interpretation and limits.** The adapter reaches the existing collector
input format for the specified native and coordinate bases. The verifier
uses separate point arithmetic for target equations but shares the
preparer for optional root replay. These controls say nothing about
full-size throughput, relation completeness, rank, ECDLP solving, or an
end-to-end improvement. The degree-7 transported-base control is still to
be implemented, and the protocol is not yet runnable or approved.
