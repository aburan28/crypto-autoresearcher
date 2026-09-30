# EXP-CERTBIN-ddfe75 impl/ (N-CONV)

Written by the executor of TASK-20260924-7c1fb2. The pinned engine
`crypto_autoresearcher.gf2` (src/, commit 934bee5, `_kernels.c` sha256
c8f79d59...a745) is IMPORTED (src/ inserted on `sys.path`; no editable
install) and never copied or edited. No file of EXP-CERTBIN-4e92d7/impl/ or
EXP-CERTBIN-e94b27/impl/ is copied. See impl-provenance.json.

| module | responsibility |
| --- | --- |
| `common.py` | E layout (mu_order(2, 18) columns), E_hex / E_sha256 conventions, input paths and bound hashes, seeds, deterministic gzip JSONL I/O; guarded development-only overrides (refused under experiments/) |
| `gf2n.py` | own F_{2^17} = F_2[t]/(t^17 + t^3 + 1) arithmetic, trace, irreducibility check |
| `construct.py` | own S_3 descent E_S3(x_R), Qpart / Lpart / constant, union support U and S_L, N-CONV17 forms Q_k, direct S_3 evaluation (self-test), c_k = Tr(t^k / x_R^2) (C-ELL) |
| `satcount.py` | exhaustive satisfiability over all 2^18 assignments (bit-sliced truth tables), solution lists |
| `draws.py` | the four fresh-arm draw rules and the keep rule (one PCG64 generator per arm) |
| `rcb.py` | RC-B: left kernel of the quadratic-column submatrix, ell, labels, the substitution v_{j*} := ell + v_{j*} and relabelling |
| `closures.py` | per-system M_3 / M_4 / W_4 / R'_3 / R'_4 / W'_4 calls into the engine, derived P / fallen / linear_forms, rc_b record, wdag extraction wrapper |
| `wdag.py` | wdag-v1 extractor: subclass of the engine's `closure.Closure` that re-runs the documented W_D iteration with `kernels.column_pass` / `products` / `backtrace`, keeps the op logs up to the first refuting iteration, and builds the DAG |
| `negctl.py` | C-VERIFIER negative-control certificates (types a-d per kind) with its own evaluator |
| `stats.py` | exact Clopper-Pearson (mpmath, 60 digits) and exact binomial tails (fractions) for the power table |
| `make_trial_plan.py` | writes trial-plan-v1.json from the specification before phase 0 |
| `engine_provenance.py` | C-ENGINE: tree rule, package hashes, full RC-1 replay, pytest, build_info |
| `selftest.py` | C-SELF and C-FIX |
| `driver.py` | phases 0-5 (and 7 on --resume), checkpoints, phase log, instrument checks computed on the engine side |
| `analysis.py` | phase 7: instrument checks, metrics MN1-MN3 and secondaries, decision rules NC-DR-1..9, raw-result / cell-summary |
| `report.py` | phase 7 writers: environment.json, manifest.yaml, run-report.md |

Commands are the specification's `execution.command`, `determinism_command`
and `verify_command` (see the run's command.txt).
