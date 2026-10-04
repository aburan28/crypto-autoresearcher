# EXP-CERTBIN-060020 impl/ (the n = 19 cell)

Written by the executor under TASK-20260924-a50c5b from the frozen
specification (version 1). The GF(2) engine `crypto_autoresearcher.gf2`
(pinned 934bee5) is IMPORTED with `src/` on `sys.path` (`common.py` inserts it).
No engine file and no archived impl/ file is copied, and the package is not
edited. See `impl-provenance.json`.

| module | responsibility |
| --- | --- |
| `common.py` | literal parameters, seeds, the E layout (E_hex, E_sha256), deterministic gzip JSONL, hashing, timers |
| `gf2n.py` | F_{2^n} arithmetic (schoolbook and exp/log tables), trace, half-trace, irreducibility test |
| `curve.py` | E: Y^2 + XY = X^3 + A X^2 + B (affine), lifting, exact point count |
| `descent.py` | S_3 descent by generic sparse polynomial arithmetic over F_{2^n}; affine decomposition; union support; left kernel; the rc_b substitution |
| `oracles.py` | oracle A (quadratic root finding over V) and oracle B (exhaustive 2^20 evaluation, split into halves) |
| `arms.py` | the arm streams S3-PRIMARY, N-CONV19, N-ELL19, N-F219, N-AFF19, F-RANDX19 with keep rules and draw logs |
| `rcb.py` | rc_b: kernel, ell, labels, substitution, R'_3 and R'_4, C-ELL, the T5 prediction |
| `closures.py` | engine wrappers; `WdagClosure` (a subclass of `closure.Closure` whose `_extract` hook builds the grouped wdag-v1); the ell-route wdag-v1; the ann-v1 extractor (own RREF) |
| `literal.py` | the executor's own literal W_D in numpy (C-LIT, C-SELF (viii)/(ix)); imports nothing from the package |
| `stats.py` | exact binomial tails, Clopper-Pearson, one-sided Fisher, the power table |
| `make_trial_plan.py` | writes `trial-plan-v1.json` from the specification alone |
| `engine_provenance.py` | C-ENGINE (tree rule, hashes, the RC-1 replay, the kernel tests, build_info) |
| `selftest.py` | C-SRC, C-SEED, C-SELF (i)-(x), C-FIX, C-CURVE, C-ELL0 |
| `backend_worker.py` | separate-process worker for C-SELF (ix) (reference backend) |
| `driver.py` | phases 0-4, C-LIT, `--phase determinism` (C-DET), `--phase backend` (C-BACKEND), phase 7 on `--resume` |
| `analysis.py` | phase 7: instrument checks, MR19-1..3, N19-DR-1..10, raw-result, cell-summary, manifest, run report |
| `record_env.py` | environment.json |
| `launch.sh` | launcher: command.txt, logs, `ulimit -v` 3 GiB, 172,800 s run watchdog |

Launch order (specification execution): `launch.sh main RUN_ID`, then
`launch.sh determinism RUN_ID`, `launch.sh backend RUN_ID`,
`launch.sh verify RUN_ID`, `launch.sh aggregate RUN_ID`.
