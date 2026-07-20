# EXP-SIG-003 — implementation

Instrument: bit-identical copies of the EXP-SIG-002 (== EXP-SIG-001) pinned
sources under `src/` (sha256 verified at copy time and re-embedded in every
run's raw.json + manifest). The instrument is loaded, never modified. All
link-test logic lives in the driver `SIG3_run.sage` (same pattern as
EXP-SIG-002's `SIG2_run.sage`).

## What the driver computes per cell (n, seed, arm)

1. Build the boolean chained Semaev system via the pinned
   `build_boolean_semaev(n, 3, seed)` (deterministic via `stable_seed`).
   Null arm: `boolean_null(monosets, nb, Random(stable_seed("null", n, 3, seed)))`
   — the EXP-SIG-002 support-matched null, bit-identical across invocations.
2. Instance filter (input-side, control C5): standard iff `R_x != "0"` and
   `eq_degs_hist` has zero degree-1 equations. Recorded before outcomes.
3. D3 and D4 via `analyze_syzygy_space(..., extract=True)` (transformation-
   tracked echelon → valid kernel bases `kernel_3`, `kernel_4`, model-family
   pivots `kpiv_3/4`).
4. `residual_4` via the EXP-SIG-002 v3-multiples logic, verbatim semantics:
   x_j-images of `kernel_3` inside D4, rank mod K4, residual =
   extra_4 − that rank (control C1 anchors: 9 at n=12, 10 at n=15).
5. D5 via `analyze_syzygy_space(..., extract=False)` (count-only; the
   transformation-tracked kernel at D5 is not needed — the link test is a
   rank argument). Returns `rec_5` (rank, sr_pred, deficit, kernel_dim,
   rankK5, extra_5), `rows_5` (tagged rows), `kpiv_5` (K5 model pivots).
6. Link computation (all over GF(2), row-index bitmasks):
   - `tag2idx5` from `rows_5`.
   - v3 images at D5: for each `kernel_3` basis vector, for each multiplier
     ν ∈ {1} ∪ {x_j} ∪ {x_j x_k}: img = XOR over its tags (i, mu) of the unit
     vector at `tag2idx5[(i, mu|ν)]`. All such rows exist at D5 (degree
     bound); misses counted and recorded (expect 0).
   - v4 images at D5: same for each `kernel_4` basis vector with
     ν ∈ {1} ∪ {x_j}. Identity embeddings (ν = 1) are ALSO ranked separately
     (A4_id).
   - A3 = rank of v3 images reduced mod K5; A4 = rank of v4 images reduced
     mod K5; A4_beyond_A3 = incremental rank of v4 images over kpiv5 ∪ P3
     (merged pivot dict; P3 leads are disjoint from kpiv5 leads because the
     v3 images were reduced against kpiv5 first).
   - residual_5 = extra_5 − A4.

## Why these quantities answer the handoff

- Rank-nullity on the tagged Macaulay matrix: rank = nrows − dim ker. On the
  support-matched null, rank = sr_pred and extra = 0, so
  deficit_5 = extra_5 + (rankK5_sem − rankK5_null) — verified as a cross-run
  identity (secondary metric; EXP-SIG-002 measured rankK5_sem =
  rankK5_null − 1 on standard D5 cells, i.e. extra = deficit + 1).
- Every x_j-image of a K4 model vector is a K5 model vector (Koszul/principal
  multipliers compose; vanishing multiples map to vanishing multiples), so
  the K4 part of kernel_4 contributes nothing mod K5: A4 is exactly the rank
  of the multiplication closure of the D4 *extra* (non-model) space.
- The D3 closure is contained in the D4 closure (multiplication is
  transitive; checked numerically via A3 + A4_beyond_A3 == A4).
- Merge (i) ⟺ residual_5 == 0; independence (ii) ⟺ residual_5 > 0.
  Coverage A4/deficit_5 and amplification A4/extra_4 quantify the link.

## Determinism (C4)

`--mode link` is fully deterministic (seeded builders, no wall-clock
dependence). The n=12 seed 2 sem cell is run in two independent invocations
(RUN-a, RUN-e); `compare_determinism.py` deep-compares the cell payloads
modulo timing fields and writes its own receipt.

## Budget mechanics

Per-cell flush after every stage (D3, D4, D5, link) so a kill at a checkpoint
boundary leaves a valid partial receipt marked with the last completed stage.
Soft cap (default 540 s): the D5 echelon (longest stage, measured 5 s at
n=12 sem, 50 s at n=15 sem, 24 s / 183 s on the nulls in EXP-SIG-002) is not
started past the cap; the cell is then recorded as `censored_softcap`
(infrastructure, not evidence). Runs are wrapped in `/usr/bin/time -l` for
RSS/CPU. Scope-reduction order on censoring: seed-2026 cross-check first,
then the n=15 arm, then n=12.

## File layout

```
experiments/EXP-SIG-003/
  specification.yaml   implementation.md   analysis.md
  SIG3_run.sage        make_manifests.py   summarize.py  compare_determinism.py
  src/{h013_f5_signatures.sage, semaev_tree.py, ic_first_fall_fast.py, macaulay_export.py}
  runs/RUN-EXP-SIG-003-{a..g}/{manifest.yaml, command.txt, environment.json,
                               stdout.txt, stderr.txt, raw.json}
  summary.json
```
