# Completed classical ECDLP finite diagnostic pilot

25 October 2026. **Observations only.** Experiment `EXP-ECDLP-fe3337`, run `RUN-ECDLP-d7f049`, hypothesis `H-ECDLP-98a95a`, goal `GOAL-ECDLP-087fc3`. All ten declared tracks produced outputs from five C++ programs, with up to three concurrent measurement processes. The genuine repository supervisor records `output_validated`, `measurement_complete: true`, and zero remaining trials. This qualifies output integrity; scientific review remains unverified.

The batch produced **241 rows**: 205 completed measurement rows, 24 completed control rows and 12 inapplicable residue-map rows. There were no failed, timed-out or truncated measurement modules. Five strict builds and all five development self-tests completed before the measurement pool. Supervisor wall time was **22.363381 seconds**, including builds, self-tests and the measurement driver. It is not a solver benchmark.

## Inputs and provenance

The eight public synthetic fixtures are an additive pilot at subgroup sizes 5, 6 and 8 bits. Six main fixtures are ordinary, non-anomalous and non-special-j; two j=0 fixtures are separate endomorphism controls. Exact field primes, coefficients, points, group orders, rejection history and certificates are in the [input manifest](../../../../harness/classical_ecdlp_pilot/protocol/fixtures.tsv) and its sibling preparation records. Input manifest SHA-256: `607f41f2ba6be5433a2095b82ccf94f6a991191f1fb53ab92fb271989cdcc18b`.

| Fixture | p | (a,b) | P | r | #E |
| --- | ---: | --- | --- | ---: | ---: |
| main-r5-0 | 61 | (1,4) | (41,55) | 19 | 57 |
| main-r5-1 | 37 | (29,3) | (30,30) | 17 | 34 |
| main-r6-0 | 127 | (13,45) | (26,68) | 41 | 123 |
| main-r6-1 | 127 | (95,36) | (38,15) | 47 | 141 |
| main-r8-0 | 457 | (73,39) | (193,306) | 211 | 422 |
| main-r8-1 | 383 | (299,157) | (199,117) | 199 | 398 |
| j0-r6-0 | 127 | (0,20) | (63,2) | 37 | 148 |
| j0-r6-1 | 127 | (0,62) | (65,42) | 43 | 129 |

The code and fixture snapshot was published before measurement. Exact-byte prospective admission returned `approvable: true` with no blockers. The approved selector returned `ready` with decision holds respected, and the genuine executor claim was committed and published before launch. Launch authority/source commit: `b7ce88e21bf2a96adaecb0cacd32c7a4ce7cb65b`. Raw-data archive commit: `6689f7036932ba0a4e9a9a6b6511af285a7987a0`.

All **110 sealed run files** are preserved. The 241 JSONL records occupy 22 of 64 declared part slots; unused slots are intentionally empty. The part manifest reconstructs 1,157,410 original bytes exactly. An isolated raw-plus-snapshot commit was checked by the unchanged repository `GitRepositoryVerifier` against all 111 paths, including its snapshot receipt. No sealed run file was edited during reporting.

The source [trial plan](../../trial-plan.json), [launch receipt](../../runs/RUN-ECDLP-d7f049/launch.json), [execution receipt](../../runs/RUN-ECDLP-d7f049/execution-receipt.json), [raw summary](../../runs/RUN-ECDLP-d7f049/raw-result.json), [parts manifest](../../runs/RUN-ECDLP-d7f049/parts-manifest.json) and [derived arithmetic summary](observations-summary.json) make the observations replayable. Compiler: g++ 14.2.0; runtime: Linux/Python 3.12.14; declared envelope: 12 GiB and driver plus three module workers. Module programs use no nested threads. Prior ASan/UBSan development checks disabled unavailable leak detection explicitly; the admitted measurements used optimized ordinary builds.

## Scope of completion

This campaign completed the implemented finite diagnostics and their control panels. It does not replace the larger 8/10/12-bit discovery panel or the blinded 192-target solver study in the parent plan. An EC-specific cancellation constructor, target-local decoder, global planar reduction and algorithmic advantage remain unsupplied where identified below. No quantum computation, simulated quantum attack, factor base, relation collection or index calculus was used.
