# P9 pair-table reuse — executor implementation

This directory implements the frozen public-synthetic experiment
`EXP-KIC-d9c828` / `RUN-KIC-ba86d9`.  The normative contract is
[`research/pair_reuse_20260922/protocol.json`](../../../research/pair_reuse_20260922/protocol.json),
whose SHA-256 is `3de8d70ae219cd2aad2c6ccf67156fdc3d1c6591729efad9e9822224a4d844de`.

`native.cpp` contains both finite fields, exact binary-curve group arithmetic,
the supplied N19 signed-Frobenius base reconstruction, and the deterministic
N23 coordinate recipe. The control exports the aggregate Q-only panel record
and sixteen hash-manifested 512-Q regime/panel files. A cold worker takes only
the N19 base recipe, its one 512-Q file, an arm and `M`; it rebuilds its base
and table every time and reads the complete 512-Q file before selecting the
nested prefix. It
does not parse scalar labels, oracle metadata, expected answers, a retained
base, or a retained table.  The two measured arms are `expanded` and
`canonical_normal_x`.  The latter builds a fresh least normal basis, using
`ceil(n/4)` conversion chunks (five for N19 and six for N23, with the final
N23 chunk restricted to its three used bits).

`checker.py` is reserved for the one independent, pre-benchmark Python replay.
It must use its own polynomial long-division, Euclidean inverse and group
implementation; importing producer arithmetic or launching the native worker
is forbidden.  It checks the frozen inputs, regenerated bases and panels,
table set equality, every exported canonical row, all 4096 queries per regime,
all stored witnesses and the required known-false verifier controls.

`python3 runner.py --phase build` is the only Stage-A action. It compiles the native binary,
creates `source_closure.json`, `build_receipt.json`, `environment.json`, and
the 384-job `case_manifest.json`, and records
`IMPLEMENTATION_BUILD_READY_NO_CONTROL_ADMISSION`.
It cannot launch a control, checker, or job.  Root owns all phase admissions
and direct-native execution.  Its P8-derived supervisor must keep the primary
interval from `Popen` to kqueue `NOTE_EXIT` and the single `wait4` reap; it
must use a fresh cwd, HOME and TMPDIR for each job, run one compute process,
and retain all failed prefixes with no retry.

The planned processes are one native control, one independent checker and
384 cold workers:

| Dimension | Values |
| --- | --- |
| Regimes | `n19_k4`, `n23_k16` |
| Query counts | `1`, `32`, `512` nested prefixes |
| Panels | eight deterministic Q-only lists, 512 points each |
| Arms | expanded; canonical normal-x |
| Technical repeats | four fresh jobs per panel/arm/cell |

After root publishes each separate committed admission, the exact phase CLI is:

```sh
python3 runner.py --phase control --admission /absolute/admission.json --admission-commit FULL40HEX
python3 runner.py --phase checker --admission /absolute/admission.json --admission-commit FULL40HEX
python3 runner.py --phase benchmark --admission /absolute/admission.json --admission-commit FULL40HEX
```

The primary statistic is only N23/K16 at M=512: per-panel medians of four
fresh jobs yield eight paired `canonical_normal_x / expanded` ratios.  The
pre-registered gate requires every control, the checker, and all 384 valid job
receipts, a median at most 0.90, and a 10,000-resample type-7 upper endpoint
below one, using `Random("PAIR-REUSE-v1-bootstrap")`.  `analyze.py` refuses a
successful-only estimate whenever any required receipt is missing, invalid, or
censored.  Its scope is finite point decomposition and cold-job cost only; it
does not measure an index-calculus, rho, or asymptotic effect.
