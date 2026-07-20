# EXP-SIG-002 — Implementation notes

## Provenance

- Instrument: `src/h013_f5_signatures.sage` is a **bit-identical copy** of the
  EXP-SIG-001 instrument (sha256
  `1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087`, verified
  against `experiments/EXP-SIG-001/src/h013_f5_signatures.sage` on
  2026-07-18). Sibling modules `semaev_tree.py`, `ic_first_fall_fast.py`,
  `macaulay_export.py` copied unchanged (sha256 recorded in run manifests).
- Driver: `SIG2_run.sage` (new) reuses the instrument's public functions
  (`build_boolean_semaev`, `boolean_null`, `analyze_syzygy_space`,
  `classify_cell`, `stable_seed`, `jsonsafe`) with EXP-SIG-002-specific modes.

## Method summary (inherited from the instrument, unchanged)

- Tagged Macaulay matrix at degree D over GF(2) (boolean monomials as
  frozensets; row enumeration identical to `macaulay_export.macaulay_rows`).
- Streaming GF(2) echelon with transformation tracking → full row-kernel basis
  = all syzygies at degree ≤ D.
- Model family K_D = monomial multiples of pairwise Koszul syzygies + boolean
  principal (Frobenius/annihilator) family + unit vectors of vanishing
  multiples (GF(2) symmetric-difference semantics — the EXP-SIG-001 OR/XOR bug
  fix is present in the copied instrument).
- `extra(D) = dim ker(M_D) − rank(K_D)`; F5 rewritten-rule analysis: rank of
  D3-syzygy multiplier images mod K4; `residual_new_at_D4 = extra(D4) − rank`.
- Matched semi-regular null (T11 semantics) per cell.

## EXP-SIG-002 additions (driver only; instrument untouched)

1. **Degeneracy detection**: `is_degenerate(meta)` flags `R_x == "0"`
   (2-torsion decomposition target; verified against the EXP-SIG-001
   RUN-EXP-SIG-001-b record where n=12 seed 1 has `R_x: '0'`).
2. **Seed probing** (`--mode boolean`): for each n, seeds are probed in order
   (requested seeds, then 1..`--max-probed-seeds`) until
   `--required-nondegenerate` (default 3) non-degenerate cells are collected.
   Every probed cell is recorded, degenerate ones flagged and retained as
   observations but excluded from the growth series.
3. **Per-cell control flags**: `null_extra_zero`, `t2_d4_deficit_eq_8n_over_3`,
   `t2_d3_deficit_eq_1` recorded per cell; run-level aggregates under
   `controls`.
4. **Gate** (`--mode gate`): V1 null control (n=9,12; D=3,4), V2
   injected-syzygy detection (n=9), V3 T2-anchor sanity (n=15 seed 1 must
   reproduce D3 deficit 1, D4 deficit 40, residual 10 — certified in
   EXP-SIG-001), determinism rerun-check (n=15 seed 2 computed twice,
   compared modulo timing fields).
5. **D5 arm** (`--mode d5`): count-only `analyze_syzygy_space(..., D=5,
   extract=False)` on sem and (unless `--d5-null 0`) the matched null, cells
   launched in the CLI-given order under the soft cap.

## Resource measurement

Each run is wrapped in `/usr/bin/time -l timeout 600 sage ...`; peak RSS
(bytes), real/user/sys seconds are parsed from stderr into the run manifest.
Per-cell wall seconds are recorded in raw.json by the driver. Hard kill at
600 s (`timeout`); driver soft cap 480 s stops launching new cells beforehand,
so censoring happens at cell boundaries and flushed cells survive.

## Environment

SageMath 10.9, Python 3.14.3, macOS-15.6 arm64 (same host as EXP-SIG-001).
Exact versions are embedded in each raw.json `environment` block and each
manifest.
