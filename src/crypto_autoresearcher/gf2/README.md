# `crypto_autoresearcher.gf2`: fast GF(2) Macaulay engine

This package is a drop-in fast path for the bit-packed GF(2) elimination used by
the CERTBIN experiments (EXP-CERTBIN-4e92d7, -e94b27, -3f06d1 and the regime-A
half of -a58c63). It returns **exactly** what the archived numpy engines
return:
- the same op log (pivot rows, pivot columns and ascending X sets);
- the same final matrix, Z list and trace hashes;
- the same closure records and certificates.

It gets there with less work and without Python in the inner loops.

The archived `impl/` directories are immutable run records and are untouched.
New experiments import this package instead of copying the engine again.

## Layout

| module | contents |
| --- | --- |
| `kernels` | `column_pass` (algorithms `auto`, `sb`, `blocked`, `direct`), `row_pass`, `ops_json_bytes` / `trace_hashes`, `replay_planes`, `replay_direct`, `backtrace`, `products`, `map_threads`, `inner_threads`, `OpLog` |
| `closure` | `Closure` (M_D, W_D, certificates), `eliminate` (the trace instrument), `eval_cert`, `cert_to_json` |
| `reference` | numpy definitions copied from the archived engines; the native kernels must equal these |
| `rankprofile` | `macaulay_profile` (M_D record by rank profile, F5/Frobenius row filter, lead-descending row order), `f5_keep`, `lead_desc_order` |
| `_kernels.c` | the native kernels (C99 plus GCC builtins); compiled on first use and loaded with ctypes |

## Install

`pip install -e ".[gf2]"` adds numpy, the package's only Python dependency.
Without numpy the tests skip, as the `fast` extra's tests do without
python-flint.

## Backend

On first use `_kernels.c` is compiled with the system C compiler into
`~/.cache/crypto_autoresearcher/gf2/`, with OpenMP (`-fopenmp`) when the
compiler supports it and without it otherwise (same results, one thread).
`build_info["openmp"]` records which. `$CRYPTO_AR_GF2_CACHE` overrides that
location. The binary is cached under a key made from:
- the source sha256;
- the flags;
- the machine.

With no compiler, the package falls back to `reference` and gives the same
results, only slower. `CRYPTO_AR_GF2_BACKEND` selects the backend:

| value | effect |
| --- | --- |
| `reference` | force the numpy fallback |
| `native` | a failed native build is an error, not a silent fallback |

Speed knobs; none of them can change an output bit:

| variable | effect |
| --- | --- |
| `CRYPTO_AR_GF2_INNER_THREADS` | threads inside one elimination (default: all cores for matrices of at least 2^23 words, 1 below that and inside `map_threads` workers) |
| `CRYPTO_AR_GF2_THREADS` | `map_threads` pool size (default: all cores) |
| `CRYPTO_AR_GF2_SB_WORDS` | words per step of the `sb` column pass, 1..8 (default 2) |
| `CRYPTO_AR_GF2_TAIL_TABLE_WORDS` | Gray-table scratch per OpenMP thread, in uint64 words (default 2^17 = 1 MiB) |
| `CC` | C compiler for the native kernels (default: prefer `gcc` then `cc`/`clang`, so OpenMP is used when libgomp is present) |

`kernels._native.build_info` records which backend served a run and the
compiled binary's source hash. A run manifest should copy it.

## Why it is faster

1. **No column scans.** The archived column pass scans every unused row at
   every column. By the pass's own invariant, the unused rows with a 1 in
   column c are exactly those whose lowest set column is c. The native pass
   therefore buckets rows by lead and never scans.
2. **Word-blocked elimination (`algorithm="blocked"`, the default).** Inside
   one 64-column word block, every pivot choice and X set depends only on that
   word. The block is eliminated on a compact array of one word per row. The
   remaining words are then updated once per block, using 8-bit Gray-code
   tables of pivot-row sums (Four Russians). The step-by-step form stays
   available as `algorithm="direct"`. Tests check both against the reference.
3. **Packed Macaulay build.** Rows are written straight into the packed layout.
   The archived build filled a dense uint8 matrix and packed it: 212 MB at
   D = 5.
4. **Cache-shaped, threaded trailing update.** After each block, the
   remaining words of every active row get one XOR per 8-pivot table. The
   tables for a cache-sized chunk of columns (1 MiB) are built once, and each
   row chunk is read and written once with all its lookups, as in M4RI's
   multi-table form (the first version streamed each row once per table).
   Chunks own disjoint columns, so OpenMP threads take whole chunks with no
   locking. Table memory is allocated once per pass. The hot loops also have
   an AVX-512 clone next to the AVX2 one.
5. **Super-blocks (`sb`).** Two words (128 columns) are eliminated per step,
   with exact multi-word row state and up to 128-bit pivot coefficients, so
   the far tail is updated once per 128 columns. The op log cannot change:
   every unused row holding a bit of the current column has its lead inside
   the step, where its words are exact (argument in the kernel source).
6. **Zero-copy op log.** The X list, hundreds of MB at nv = 24, is viewed
   in place from the C buffer and freed with the numpy view. Copying it
   cost more than half the elimination at that size.
7. **No Python in the inner loops.** Op-log JSON, trace hashes, replays, the
   certificate back-trace and the W_D products are all native. Native calls
   release the GIL, so `kernels.map_threads` runs independent instances in
   parallel.
8. **Reusable scratch + a working OpenMP build.** Blocked / super-blocked
   passes keep buffers and the Gray-table pool in a grow-only thread-local
   arena (no malloc/mmap per call). The build prefers `gcc` so `-fopenmp`
   succeeds when `cc` is clang without `omp.h`. Same-key compiles take a
   file lock. Certificate checks use native `gf2_xor_rows_prefix` when the
   combination is long enough.

## Measured (this container, 4 cores, no GPU)

Measured on real RC-1 instances. Outputs were identical in every case.
The tables below were recorded before the threaded and super-block
changes; see "Larger matrices" for the current engine.

| workload | archived | this package | speedup |
| --- | --- | --- | --- |
| `eliminate`, D = 4 (per target, 1 thread) | 242 ms | 13 ms | 19x |
| `eliminate`, D = 4 (4 threads, per target) | 242 ms | 4.6 ms | 53x |
| column pass, D = 5 (16796 x 12616) | ~3 s | 0.18 s | ~17x |
| **whole RC-1 closure workload** (1062 records, 268 certificates), 1 thread | 1878 s | 110 s | **17x** |
| same, 4 threads (`map_threads`) | 1878 s | 34 s | **56x** |

The archived figure is the sum of the recorded `wall_seconds` for M_5, W_4 and
W_5; M_3 and M_4 had none recorded. Per closure on 1 thread the speedups are
M_5 17.9x, W_4 22.4x and W_5 16.2x.

### Larger matrices (2026-09-30)

Random quadratic systems with neq = nv - 1, the CERTBIN shape. Measured on 4
cores (Xeon with AVX-512, no GPU); "before" is the engine as first merged.
The op log, final matrix and ops_strict equal the column-at-a-time `direct`
pass in every case, at every thread count.

| matrix (R x C) | rank only: before -> now | with op log: before -> now |
| --- | --- | --- |
| nv = 20, D = 5 (25669 x 21700) | 1.6 s -> 0.73 s | 2.9 s -> 1.0 s |
| nv = 24, D = 5 (53475 x 55455) | 22.6 s -> 4.9 s | 29.4 s -> 5.4 s |
| nv = 20, D = 6 (117724 x 60460) | 92 s -> 22.5 s | 124 s -> 36.9 s |

Single-threaded, `blocked` alone is about 2x the first version at these sizes
(nv = 24, D = 5: 11.4 s). What remains is bandwidth: every row word needs one
table read per 8 pivots, from L2 (about 32 GB/s per core here). The dense cost
is the standard cubic one. Beyond this, gains would need a fast-multiplication
(Strassen-type) trailing update, or a solver that skips rows known to reduce
to zero (F5 criterion). Neither keeps the column pass's op log, so either
would be a new instrument, not a speed-up of this one.

Reproduce with `python3 tools/gf2_replay_rc1.py [--threads N]`. The tool
re-runs every archived closure record and certificate of RUN-CERTBIN-c417e0,
checks each field and certificate against the archive, and exits nonzero on
any mismatch.

### Threads

Native calls on large matrices release the GIL. Calls under
`kernels.GIL_RELEASE_WORDS` keep it (`ctypes.PyDLL`), and the Macaulay build is
a single scatter-XOR. Without these two measures, many short GIL releases under
a thread pool cause a convoy that made small closures 10x *slower* with 4
threads.

## Rank-profile solver (`rankprofile`)

`macaulay_profile(eqs, nv, D)` returns the M_D record `{rank, one,
dims_by_deg}`, which equals `Closure.macaulay_closure`'s, together with a
certificate when 1 is in M_D. It is faster because it needs only the column
rank profile (the pivot-column set in the fixed column order), and every
elimination of every spanning set of the row space gives the same profile:

1. **F5/Frobenius row filter.** A row mu*f_k is dropped when mu is a degree-e
   leading monomial of span{nu*f_j : j <= k, deg nu <= e - 2}. Using
   f_k^2 = f_k in B, such a row is a sum of rows with smaller keys; the module
   docstring has the proof. The lead sets come from small lower-degree
   matrices processed equation by equation (`kernels.row_leads`). The filter
   removes every zero-reducing row at D <= 5 on CERTBIN-shaped systems, and
   38.8k of the 57.3k at nv = 20, D = 6.
2. **Lead-descending row order.** Unreduced, still-sparse rows become pivots
   before filled-in ones, so fill-in drops.
3. The native column pass on what remains.

Its certificate is a valid list of (mu, k) Macaulay rows summing to 1,
checked by `eval_cert` before it is returned. It is generally not the
certificate the declared column pass extracts, and there is no op log or
trace hash. **It is a separate instrument:** an experiment whose protocol pins
the exact engine's certificates or hashes must keep using `Closure`.

Measured, warm, 4 cores (random systems, neq = nv - 1; records identical):

| matrix | exact `Closure.macaulay_closure` | `rankprofile` | rows kept / rank |
| --- | --- | --- | --- |
| nv = 20, D = 5 | 1.36 s | 0.78 s | 21679 / 21679 |
| nv = 24, D = 5 | 7.30 s | 3.43 s | 46575 / 46575 |
| nv = 20, D = 6 | 35.4 s | 8.28 s | 78964 / 60453 |

`python3 tools/gf2_replay_rc1.py --solver rankprofile` replays all 784
archived RC-1 M_D records with 0 mismatches. Its 186 refutation certificates
are checked by evaluation instead of compared, because they differ from the
archived ones.

## Not covered yet

- **Regime B** (`EXP-CERTBIN-a58c63` `regimeB.py`). Its elimination is dense
  over F_{2^n}, not GF(2), and needs its own kernel.

## Rank-only instrument (`rank_only`)

A **separate** solver for questions that need the pivot-column set (is 1 in
M_D, rank, dimensions by degree) and not the dense op log. Declared as
instrument `gf2.rank_only`:

- `rank_only.rank_profile(M, C)` — sparse GE with the same pivot rule as the
  dense column pass (so `pivcols` match), densifying past
  `CRYPTO_AR_GF2_RANK_DENSE_NNZ` or falling back to
  `column_pass(keep_ops=False)` on large matrices;
- `rank_only.macaulay_rank(eqs, nv, D, neq)` — M_D rank-profile record plus a
  checkable combination certificate (`verify_certificate`);
- certificates are **not** the dense op log and must not be mixed with
  CERTBIN op-log certificates.

```sh
python3 tools/gf2_bench_rank.py            # small shapes
python3 tools/gf2_bench_rank.py --large    # CERTBIN-shaped
pytest tests/test_gf2_rank_only.py
```

A native sparse kernel (and a true mid-stream sparse→dense handoff) is the
next speed step; the Python sparse path is the correctness scaffold.

## GPU trailing update (`gf2.gpu`)

`gpu/tail_update.cu` is a CuPy/NVRTC port of `_kernels.c::tail_chunk`. It is
bit-identical to the CPU update on every tested input when a CUDA device is
present (`tests/test_gf2_gpu_tail.py`). This environment has no GPU; use
RunPod (or any CUDA host) to time it:

```sh
export RUNPOD_API_KEY=...          # https://www.runpod.io/console/user/settings
python3 tools/gf2_runpod.py probe
python3 tools/gf2_runpod.py bench --gpu-type "NVIDIA GeForce RTX 4090"
python3 tools/gf2_bench_rank.py --gpu --large --out bench.json
```

Optional extra: `pip install -e ".[gf2-gpu]"` (pulls `cupy-cuda12x`).

## Tests

- `tests/test_gf2_kernels.py`:
  - native equals reference on random and low-rank matrices, for every
    algorithm at 1 and 4 threads;
  - on matrices large enough for the threaded, table and multi-word paths,
    `sb` and `blocked` at every super-block width and thread count equal
    `direct`;
  - the reference equals the archived 4e92d7 code;
  - the closure reproduces archived RC-1 records and certificates;
  - the forced reference backend gives the same results.
- `tests/test_gf2_rank_only.py`: sparse/dense/auto rank-only vs dense pivcols;
  combination certificates verify.
- `tests/test_gf2_gpu_tail.py`: CPU tables==direct; GPU==CPU when a device is
  present (skipped otherwise).
- `tests/test_gf2_rankprofile.py`:
  - native `row_leads` and `row_lead_weight` equal their references;
  - `macaulay_profile` equals the exact engine on random and edge-case systems,
    and planted-solution systems are never refuted;
  - every dropped row lies in the span of the kept rows;
  - archived RC-1 M_D records are reproduced;
  - the reference backend runs the same code.
- `tools/gf2_replay_rc1.py [--solver rankprofile]`: the full RC-1 sweep.
