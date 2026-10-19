# Partial-checkpoint recovery supplement — 16 October 2026

This supplement preserves the original check-vertex report and its
`SHA256SUMS` snapshot. It addresses a narrow restart failure found after
PR #2272 was opened: if the producer stops after writing its fixed
`edge-NNNN.json.partial` file but before linking the finished checkpoint,
its next `--resume` invocation refuses to create that same temporary path.
This is a file-state problem, not a result about the curve or relation yield.
[internal: `transport_path.py`, `SHA256SUMS`, PR #2272]

`recover_partial.py` is run **only after the producer has stopped**. It first
calls the independent integer-arithmetic verifier on the completed chain.
It accepts at most one partial file, at the last completed edge or the next
edge. It hard-links the exact partial bytes under a new preserved name,
checks the linked bytes, and removes only the producer's fixed temporary
pathname. Existing completed checkpoints are never overwritten. Its JSON
output includes the partial SHA-256 and preserved path. A later producer
resume still checks the frozen graph and producer-script hashes. [internal:
`recover_partial.py`, `verify_chain.py`]

From the repository root, after stopping the producer, use:

```sh
python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/recover_partial.py --stratum P29 --checkpoint-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p29-twoedge-attempt1
```

Use `P37` and its corresponding checkpoint directory for that stratum. The
recorded P29/P37 check-vertex chains had no partial file and were not
altered by this supplement. [internal: `controls/`]

The recovery tests constructed an interrupted next-edge partial in a
temporary copy of the P29 chain. They checked that its bytes were preserved,
the fixed temporary name was freed, and the completed chain still passed
independent replay. A non-next-edge partial was rejected and retained. The
extended suite also reran both valid chains, the prior pointwise digest
comparison, and a self-consistent point/digest tamper rejection. Exact
command and raw output:

```sh
python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/test_verify_chain_recovery.py > research/isogeny_relation_yield_scan_20261016/path_transport/controls/verification-tests-attempt3.stdout 2> research/isogeny_relation_yield_scan_20261016/path_transport/controls/verification-tests-attempt3.stderr
```

Five tests passed in the retained `attempt3` output. A preliminary five-test
run from the same source, then temporarily named `test_verify_chain.py`, is
retained as `attempt2`; `test_verify_chain_recovery.py` archives those test
bytes while the originally committed `test_verify_chain.py` stays intact.
The original report and `SHA256SUMS` remain valid for its first-check-vertex
snapshot. `SHA256SUMS-recovery` binds this additive supplement. No actual
process crash at a partial-file write was observed; the recovery scenario was
constructed to test the failure mode. [internal: test source and retained
`controls/verification-tests-attempt{2,3}.*`]
