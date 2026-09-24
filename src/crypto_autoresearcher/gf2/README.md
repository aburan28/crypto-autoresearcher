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
| `kernels` | `column_pass`, `row_pass`, `ops_json_bytes` / `trace_hashes`, `replay_planes`, `replay_direct`, `backtrace`, `products`, `map_threads`, `OpLog` |
| `closure` | `Closure` (M_D, W_D, certificates), `eliminate` (the trace instrument), `eval_cert`, `cert_to_json` |
| `reference` | numpy definitions copied from the archived engines; the native kernels must equal these |
| `_kernels.c` | the native kernels (C99 plus GCC builtins); compiled on first use and loaded with ctypes |

## Backend

On first use `_kernels.c` is compiled with the system C compiler into
`~/.cache/crypto_autoresearcher/gf2/`. `$CRYPTO_AR_GF2_CACHE` overrides that
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
4. **No Python in the inner loops.** Op-log JSON, trace hashes, replays, the
   certificate back-trace and the W_D products are all native. Native calls
   release the GIL, so `kernels.map_threads` runs independent instances in
   parallel.

## Measured (this container, 4 cores, no GPU)

Measured on real RC-1 instances. Outputs were identical in every case.

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

## Not covered yet

- **Regime B** (`EXP-CERTBIN-a58c63` `regimeB.py`). Its elimination is dense
  over F_{2^n}, not GF(2), and needs its own kernel.
- **GPU.** There is no GPU in this environment. The word-blocked form maps
  naturally to a GPU (one block per matrix, a warp per word block) but is
  unimplemented.

## Tests

- `tests/test_gf2_kernels.py`:
  - native equals reference on random and low-rank matrices;
  - the reference equals the archived 4e92d7 code;
  - the closure reproduces archived RC-1 records and certificates;
  - the forced reference backend gives the same results.
- `tools/gf2_replay_rc1.py`: the full RC-1 sweep.
