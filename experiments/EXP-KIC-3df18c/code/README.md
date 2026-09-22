# EXP-KIC-3df18c finite N19 affine-pool search

This implementation covers only the approved public-synthetic coordinate
geometry of the frozen 37-orbit Koblitz pool. It expands all signed Frobenius
orbits, discovers every affine two-plane from cross-orbit XOR collisions,
retains all plane keys and compatible four-orbit bases, constructs coordinate
support for 9,139 triple and 703 pair orbit multisets, and scores all 66,045
four-orbit bases. It does not use base-point scalar logs, SAT, imported
targets, rho, or IC timing.

The additive baseline amendment
`research/admissible_affine_factor_base_20260921/baseline_amendment.json`
binds the historical at-most-three histogram and unique maximum 6,257.
The chosen prior base `[6,9,22,28]` must reproduce exact-three 6,224 and
at-most-three 6,257. The global exact-three maximum is measured without a
frozen value. The selected plane is ranked by exact-three coverage, then
at-most-three, then sorted orbit IDs and its smallest canonical plane key.

Build only (permitted before process admission):

```sh
python3 experiments/EXP-KIC-3df18c/code/runner.py --phase build
```

This is the additive **v2** pre-launch build. The original committed
`source_closure.json`, `build/search_final`, environment and readiness files
remain byte-for-byte preserved. `source_custody_supersession.json` binds the
v2 source closure, binary, compiler receipt and the original commit. All
admitted process phases read the v2 closure and `build_v2/search_final`.

The following three commands are **templates**. Root supplies each exact
committed admission path and commit, and is the sole launch owner. Do not run
them before its explicit phase assignment:

```sh
python3 experiments/EXP-KIC-3df18c/code/runner.py --phase controls --admission <committed-native-admission-path> --admission-commit <commit>
python3 experiments/EXP-KIC-3df18c/code/runner.py --phase science --admission <committed-science-admission-path> --admission-commit <commit>
python3 experiments/EXP-KIC-3df18c/code/runner.py --phase checker --admission <committed-checker-admission-path> --admission-commit <commit>
```

The native and science processes are the same frozen C++ binary with
`--controls` and `--science`, respectively. The independent checker is a
separate Python implementation with long-division field arithmetic,
extended-Euclidean inversion, a separately written group law and direct
unordered coordinate pair-sum MITM. It verifies the full catalogue,
66,045 cache-derived scores, historical at-most histogram, selected/prior/null
target verdicts, and four forged artifacts. The checker does not import the
producer's kernels.

Each process runs once in a fresh session and directory. The supervisor
records Popen-to-wait4-reap wall, CPU/RSS, sampled footprint and a watchdog;
parent hashing and file promotion are separate. Failed and censored outputs
remain in the raw phase directory and archive, with no automatic retry.
