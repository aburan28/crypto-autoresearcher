# Named solver baselines and complete composition

This source implements the registered baseline module for the larger classical solver cohort. It does not run a scientific cohort during development or claim a speedup.

`vendor-source.json` binds the unchanged source bytes from `aburan28/cryptanalysis` at commit `379faa0f1e38facd9c8fdfc527f0b89518cf2e70`. The vendored `rho.c` and `precomp.c` are the actual upstream algorithms, not renamed BSGS. The license is retained at `vendor/LICENSE`.

All elliptic-curve operations go through the same `dec::Ops` backend used by the candidate. A custom generic-group vtable supplies addition, doubling, negation, full-point equality/hash, encoding and canonicalization. Batched calls execute those same affine additions individually; no uncharged optimized Montgomery/Jacobian backend is used. The two generic API glue functions perform shared-backend scalar multiplication and membership checks. This changes the arithmetic adapter, not the vendored walk algorithms.

## Build and interface

```sh
python3 baselines/build.py --output /tmp/validation-baselines
/tmp/validation-baselines --self-test
/tmp/validation-baselines --run FIXTURES.tsv PUBLIC_TARGETS.tsv FRESH_OUTPUT.jsonl
```

The build helper compiles the four unchanged C source files sequentially with GCC in GNU11 mode at `-O2 -Wall -Wextra -Werror`, then links the C++20 project adapter with `-O2 -Wall -Wextra -Wpedantic -Werror -Wconversion -Wshadow`, pthreads and libm. Upstream public headers are included through `-isystem vendor/include` because their documented GNU C `__int128` typedefs are third-party extensions; all project warnings remain active. Vendor source and headers are byte-identical to the upstream manifest. `--sanitize` adds ASan/UBSan instrumentation while retaining `-O2`; development checks use `ASAN_OPTIONS=detect_leaks=0` because host leak detection is unavailable. The candidate header is included from `../candidate/decoder.hpp` as ordinary project code.

The input TSV formats are identical to the candidate. They contain only public curve, base, order and target information. Existing outputs are never overwritten. No labelled subgroup orbit is passed to the candidate. BSGS deliberately constructs and charges its public baby-step dictionary as a named baseline.

## Methods

Every target has five rows, in a deterministic publicly randomized order:

* `rho_upstream_auto`: upstream r-adding distinguished-point rho, with negation and its look-ahead/windowed fruitless-cycle handling. One arithmetic worker; upstream public-order formulas choose adding-table size, lanes and distinguished-point bits. The C library starts one worker pthread while its main thread waits.
* `rho_upstream_auto_aa`: an independent invocation with fresh state, identical inputs and the exact same rho seed. This is an A/A process-CPU reference, not an extra independent target sample.
* `hybrid_xmod7_exact_b8_then_rho`: train the frozen x-mod-7 model once per fixture with diagnostics disabled; run four public views and exact-prefix beam eight; verify all eight candidates; on a miss invoke the identical rho implementation and seed in newly constructed walk state. It records candidate-only recovery and fallback recovery separately. The candidate does not inherit rho tables or scalar labels.
* `bernstein_lange_precomp`: upstream Bernstein–Lange distinguished-point chain precomputation, reused across the fixture's declared targets. Coverage is one and other walk/table parameters use the source-bound upstream public-size defaults. Setup is separately charged, including fixed-base and endpoint construction.
* `bsgs_complete`: a complete deterministic baby-step giant-step reference. A sorted full-point baby table of size ceil(sqrt(r)) is charged once per fixture; every returned candidate is publicly verified.

Rho and BL online use an upstream work backstop of `256*ceil(sqrt(r))+8192` reported group operations. BL setup uses `64*r+8192`. These are operational bounds; reaching a limit is censoring, not mathematical negative evidence. Source-internal reported operations are not identical to all actual arithmetic, so the complete shared-backend operation vector is also retained. There is no hidden BSGS rescue of a rho or BL failure. BSGS is a separate method.

The rho seed is a nonzero deterministic function of fixture seed and target ordinal, independent of the hidden scalar. Standalone, A/A and hybrid fallback use exactly the same seed. The method order uses a separate fixed public domain. The hybrid trains from a fresh per-fixture `Ops` and copies only its charged, target-independent Tonelli nonresidue cache into fresh target arithmetic state. Rho-alone and A/A use fresh independent arithmetic state.

## Outputs and cost scope

Rows use `scope=larger_solver_validation`, `track=solver-baselines` and `row_kind` in `fixture_validation`, `hybrid_setup`, `baseline_setup`, `baseline_target`.

There are four setup/validation rows per fixture, and five rows per target. For the frozen 48-curve/768-target cohort this is 4,032 rows. Setup methods are `shared_public_validation`, `hybrid_xmod7_exact_b8_then_rho`, `bernstein_lange_precomp` and `bsgs_complete`.

Target rows include `fixture`, `target_id`, `method`, `candidates`, `candidate_verification_hits`, `verified_scalar`, `status`, actual `CLOCK_PROCESS_CPUTIME_ID` CPU seconds, wall seconds and operation vectors. The hybrid also retains its complete `prefix_candidates`, prefix verification flags, fallback flag and stage costs. All produced candidates, including misses, are intended for the separate independent Jacobian checker.

`status` is `solved`, `failed`, `censored` or `invalid`; the original upstream status code is preserved. An incorrect returned scalar throws immediately and invalidates the implementation. Rho work/memory stops and BL exhausted attempts are retained explicitly. Setup failures propagate to BL target rows.

The CPU intervals cover setup/solver calls, including upstream worker CPU, scalar coefficient arithmetic, hashing, lookup, sorting and allocation. They exclude JSON serialization, module orchestration and final object teardown. Wall intervals are descriptive under concurrent execution. The EC field and group vectors measure actual shared-backend work; they are not a conversion of CPU time into one primitive. Upstream internal RNG draws and scalar-ring arithmetic are not counted in decoder RNG/Fp counters, and this limitation is explicitly marked. Upstream internal verification arithmetic is charged in field/group/scalar counters; `candidate_verifications` counts the wrapper's final checks. Upstream `ca_stats` are separate, nonadditive diagnostic counters.

Persistent table/kernel payload estimates are reported with their scope. They are not whole-process peak RSS. Training is charged once; the primary hybrid omits heldout and contraction diagnostics because they do not influence candidate selection. The full secondary candidate panel retains those diagnostics separately. Cold and amortized comparisons must add the appropriate setup and declare the number of targets sharing it.

## Fixed development checks

The self-test uses only three fixed known development curves: `(p,a,b)=(17,2,2)`, `(383,261,146)` and `(65537,1,7)`. It checks the negation quotient, actual upstream rho recoveries and A/A primitive paths, actual BL table construction/returned witnesses, and all 181 canonical scalars of the second curve through complete BSGS. These are implementation checks, not confirmation-cohort measurements.

The `cryptanalysis-reference/`, `build/` and temporary development artifacts are not source publication paths. Publish only the explicit source/header/license manifest and selected development receipts.
