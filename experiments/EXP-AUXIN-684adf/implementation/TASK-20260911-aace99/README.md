# TASK-20260911-aace99 complete pipeline

This package is the approved implementation successor for the frozen supplied-residue arithmetic experiment. `fixtures.py` deterministically enumerates the exact 26,546 scientific identities in the frozen family/prime/panel/k/order traversal; `crt.py` folds only ordered `(residue, modulus)` inputs; `reference.py` independently scans the full finite domain. No module implements group operations, target import, key handling, or a first stage.

The only invocation authorized during this task is `python3 unit_checks.py`. It runs the 76 named nonpanel controls from `coordination/auxin-pipeline/TASK-20260911-aace99/implementation-controls.json`, with prime-13 test-policy injection confined to that harness. It does not enumerate frozen prime-101/241 cells.

For a future separately approved scientific task, only `tools/experiment_execution.py run` may launch the driver. The supervisor supplies `launch.json`, owns the actual task lock and calls the driver/checker argv shapes bound in the protocol. `admission.py` calls the canonical supervisor authorization; it accepts no boolean authorization flag, scans no descriptors, and never acquires a lock. The future plan must contain all 26,546 case inputs and the 22-file package. The checker builds `artifact-sha256.json` only after producer termination and checks full coverage. An empty `counterexamples.jsonl` is allowed only when it exists and is zero bytes.

This is implementation and custody work. Passing controls is neither a scientific trial nor a conclusion.
