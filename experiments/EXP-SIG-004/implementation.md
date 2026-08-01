# EXP-SIG-004 — Implementation

Experiment: EXP-SIG-004 (hypothesis H-SIG-001, handoff TASK-20260718-SIG-F4;
dispatched by DEC-20260718-019 next_actions).

## What is measured

The D4 residual non-rewritable syzygy count of the boolean chained Semaev
m = t = 3 systems, `residual = extra_4 - rank mod K4 of the D3-syzygy
monomial multiples`, re-measured under two reduction semantics side by side
on the SAME kernel bases and the SAME v3_mults family:

- **pinned** (continuity anchor): the instrument's early-break
  `reduce_against` (verbatim EXP-SIG-002 semantics; exact for membership,
  can overestimate quotient ranks — the EV-SIG-003 caveat).
- **canonical** (corrected): `full_reduce` copied verbatim from
  `experiments/EXP-SIG-003/SIG3_run.sage` — clears every pivot-lead bit
  top-down; linear; `rank(full_reduce(F)) == rank(F mod K4)` exactly.

Independently, control C8 computes the same quotient rank reduction-free as
`rank(v3_mults ∪ K4) - rank(K4)` (union echelon) on every cell; the
canonical value must equal it.

## Instrument

`src/` holds bit-identical copies of the pinned EXP-SIG-001 instrument,
copied from `experiments/EXP-SIG-003/src/` (read-only originals) and
hash-verified against `experiments/EXP-SIG-002/src/`:

- `h013_f5_signatures.sage` sha256 `1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087`
- `semaev_tree.py` sha256 `e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef`
- `ic_first_fall_fast.py` sha256 `f1c98bd8642df226760f43038d6687e73794d04b9c7a9073f244b8a0433fad61`
- `macaulay_export.py` sha256 `c00b8aad9ad47f8a3f09c39f6b65062a37562703bfd1c4f6159b1e54b1dbad97`

The driver re-verifies these hashes at startup (gate hard-fails on
mismatch). All re-measurement logic lives only in `SIG4_run.sage`.

## Driver

`SIG4_run.sage`, two modes:

- `--mode gate` (RUN-a, runs first): C1 support-matched null residual == 0
  under BOTH reductions at n = 9, 12 (explicitly computed from the null's
  own D3 kernel, not inferred); C2 injected-syzygy detection (verbatim
  EXP-SIG-002 gate); C3 T2-anchor continuity at n = 15 seed 1 (D3 def 1,
  D4 def 40, pinned residual == 10; canonical measured, must be >= pinned);
  C4a in-run determinism (n = 15 seed 3 sem computed twice, compared modulo
  timing fields). No measurement run launches unless gate = PASS.
- `--mode cells --cells n:seed:arm,...`: per cell, build instance
  (input-side filter fields recorded: R_x, eq_degs_hist, standard), matched
  null for the null arm, D3/D4 classification with kernel bases, the
  verbatim v3_mults family, both reductions, the C8 union cross-check,
  per-cell controls (C5/C6/C7/C8 + anchor reproduction), flush after every
  cell (checkpoint). Soft cap 540 s stops launching new cells; unlaunched
  cells recorded `not_run: soft budget cap`.

Stop rules implemented in-driver (halt at the cell boundary AFTER the
violating cell's payload is appended and flushed):

- C7: `residual_canonical < residual_pinned` on a standard sem cell →
  exit code 2, `halt` block in raw.json (mission stop-and-report rule).
- C8: union cross-check != canonical rank → exit code 3 (driver bug, not
  evidence).

## Run plan (8 of 10 budgeted runs)

| Run | Content |
|---|---|
| RUN-a | gate (C1, C2, C3, C4a) |
| RUN-b | n=9 seeds 1,2,3 × {sem,null} (6 cells) |
| RUN-c | n=12 seeds 1..7 × {sem,null} (14 cells; seeds 1,3 = filtered re-records) |
| RUN-d | n=15 seeds 1..6 × {sem,null} (12 cells; seed 2 = filtered re-record) |
| RUN-e | n=18 seeds 1,2,3 × {sem,null} (6 cells) |
| RUN-f | n=21 seeds 1,2,3 × {sem,null} (6 cells) |
| RUN-g | C4b cross-invocation determinism repeat: cell 18:1:sem |
| RUN-h | C4b compare receipt (compare_determinism.py RUN-e vs RUN-g, cell 18:1:sem) |

Seed sets are exactly EXP-SIG-002's (19 standard + 3 filtered instances),
so every anchored old count has a paired corrected count per (n, seed).
Runs launch in ascending-n order; the scope-reduction order on censoring is
n = 21 first, then n = 18 (mission rule). Every sage invocation is wrapped
in `/usr/bin/time -l` for RSS/CPU receipts; expected per-run wall is far
under the 600 s kill rule (EXP-SIG-002 measured the same 22-cell boolean
matrix in ≈ 105 s total; EXP-SIG-004 adds the null-arm extract and the
second reduction per cell).

## Determinism compare

`compare_determinism.py RUN-E-dir RUN-G-dir CELL OUT-dir` deep-compares the
named cell's payload modulo timing fields and writes its own receipt
raw.json (RUN-h).

## Deviations from the EXP-SIG-002 cell semantics

None in the measured quantities: the v3_mults construction, the K4 model
family, the instance builder, the null generator, and the filter are all
verbatim. The only additions are: (i) the canonical reduction computed
alongside the pinned one, (ii) the C8 union cross-check, (iii) the null arm
gets an explicit residual computation (EXP-SIG-002 inferred null residual 0
from extra = 0; here it is measured from the null's own D3 kernel), and
(iv) the D3 non-Koszul count is reported per cell from the same D3
classification (mission item 4; reduce-free: extra = kernel_dim - rankK).
