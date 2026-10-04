# TASK-20260913-1d3db7 / RUN-SEMBIN-8be036

Executor report for EXP-SEMBIN-911efe. Observations only. No evidence
record, no hypothesis status change, and no statement about any curve's
security or about first fall degree.

Frozen contract: `experiments/EXP-SEMBIN-911efe/specification.yaml`, approved
by DEC-20260913-c224bb, committed in `a88b4dfd0`.

## What was done

1. Copied `binary_field.py`, `fastfield.py`, `yield_core.py`, `yield_run.py`,
   `yield_stats.py`, `yield_null.py` from EXP-SEMBIN-354a75 into
   `experiments/EXP-SEMBIN-911efe/code/` (sha256 in `artifact-digests.json`).
2. Reconstruction control on all 180 configurations of
   `RUN-SEMBIN-1b9afe/per-R-counts.json`, E side, `usable_point_multiset`,
   pooled as in the validator table (10 000 draws per box).
3. Algebraic selftest: enumerate `E(F_{2^n})` for n=7,8,9 and a in {0,1},
   b=1; double every point; compare to `{P : Tr(x_P)=Tr(a)} ∪ {O}`.
4. Per source cell: `Tr(alpha^j)` for j<k under `modulus_for(n)`; random
   bases regenerated from `derived_seed` after the B draw, same as
   `yield_run.run_config`.
5. Split every configuration and both sides by `pi(R)=Tr(x_R)+Tr(a)` with
   a=0 on E and `twist_a` on T. Per class: counts, nonzero, mean, var/mean,
   f_dispersion, for single, chained and usable.
6. N1 as an exact integer with the offending list.
7. Controls: random-V split (null object); known-false (lowest bit of R_x;
   Tr under a second irreducible); matched-null availability; factor-base
   parity census including x=0.
8. P4: n=21 k=11 and n=23 k=12, low_degree_polynomial, B in {1, random},
   seeds 20260913201 and 20260913202, 2000 targets, exhaustive `|V|^t`.
9. P5: inspected RUN-SEMBIN-cbd770 `image-sizes.json` / `raw-result.json`.

## What stopped / what was unreached

- Reconstruction: passed (printed table).
- Algebraic selftest: passed (six cases).
- Known-false empty class: none. Run not invalidated on that rule.
- P4: both cells reached; `|V|^t` = 2^22 and 2^24; not sampled.
- N1 = 16. The contract says diagnose and form no claim. Diagnosis is
  recorded; remaining protocol measurements were still written.

## N1

**N1 = 16** (exact).

All 16 are `(configuration, target)` pairs on

- n=12, m=6, t=6, k=2
- `low_degree_polynomial`, `B_eq_1` only
- **twist side** (a = 512, Tr(a)=1)
- `pi=1`, `m·Tr(a)=0`, `Tr(x_R)=0`
- nonzero in `single_x_multiset` (class totals: chained pi=1 also nonzero;
  `usable_point_multiset` class total on T, pi=1 is 0 on those configs)

N1 on the three even-n t=2 low-degree cells: **0**.

Checked: E a=0; T a = first trace-1 delta; traces under `modulus_for(n)`;
R_x from the archive; n=12 window `Tr(1)=Tr(alpha)=0`. List:
`parity-split.json` `offending_pairs`.

## Reconstruction (printed table)

All 12 validator boxes matched at printed precision (E, usable). Low-degree
f_dispersion 0.7903–0.8222; random-V 0.9949–1.0072. Recomputed var/mean
(ddof 0): low-degree 1.438–1.545, random-V 0.985–1.012. The 1.46–1.52 /
0.99–1.00 lines in the validator report are a prose envelope around those
boxes, not a second table.

## Selftests

| n | a | Tr(a) | #affine | #2E | equal |
|---|---|-------|---------|-----|-------|
| 7 | 0 | 0 | 115 | 58 | true |
| 7 | 1 | 1 | 141 | 71 | true |
| 8 | 0 | 0 | 287 | 144 | true |
| 8 | 1 | 0 | 287 | 144 | true |
| 9 | 0 | 0 | 507 | 254 | true |
| 9 | 1 | 1 | 517 | 259 | true |

Even-n source cells: `Tr(alpha^j)=0` for all j<k (low-degree window confined).
Random bases were regenerated; membership in ker(Tr) is recorded per
config in `partial/subspace-checks.json` (not expected in general).

## Three t=2 low-degree cells (E, usable, pooled 5 seeds)

Class pi = Tr(x_R)+Tr(0). Predicted empty class is pi=1 (`m=2` even).

| n | B | pi=0 n | pi=0 nonzero | pi=0 mean | pi=0 var/mean | pi=0 f_disp | pi=1 n | pi=1 nonzero | pooled var/mean | 1+pooled mean |
|---|---|--------|--------------|-----------|---------------|-------------|--------|--------------|------------------|---------------|
| 20 | B=1 | 4996 | 2984 | 0.90252 | 0.9868 | 1.0047 | 5004 | 0 | 1.4384 | 1.4509 |
| 20 | random | 4993 | 3162 | 1.00200 | 0.9762 | 1.0007 | 5007 | 0 | 1.4779 | 1.5003 |
| 22 | B=1 | 5013 | 3136 | 1.00838 | 1.0417 | 0.9849 | 4987 | 0 | 1.5445 | 1.5055 |
| 22 | random | 5115 | 3284 | 1.00938 | 0.9668 | 1.0102 | 4885 | 0 | 1.4599 | 1.5163 |
| 24 | B=1 | 4984 | 3132 | 0.98054 | 1.0201 | 1.0056 | 5016 | 0 | 1.5119 | 1.4887 |
| 24 | random | 4989 | 3108 | 0.99298 | 1.0268 | 0.9896 | 5011 | 0 | 1.5244 | 1.4954 |

Per-configuration and twist-side rows: `parity-split.json`.

## Controls

- **Null object (random_k_dimensional):** both pi classes have nonzero usable
  counts on E at the t=2 cells; per-class means are of the same order (example
  n=20 B=1 seed 20260913201 E usable: pi0 mean 0.565, 439 nonzero; pi1 mean
  0.521, 398 nonzero). No empty class.
- **Known-false:** lowest bit of R_x and Tr under a second irreducible of the
  same degree. Neither split produced an empty class. Example n=20 B=1 seed
  20260913201 E usable: bit-0 mean 0.452 / bit-1 mean 0.450; alt-mod
  1048609 vs primary 1048585, both classes nonempty, f_dispersion remaining
  below 1 in both alt classes.
- **Matched null per-R:** **unavailable**. Source `per-R-counts.json` has curve
  targets only; `raw-result.json` matched_null is aggregates. Not substituted.
- **Factor-base census:** per configuration in `parity-split.json`, including
  x=0. Example n=12 B=1: E 5 points all pi=0 (x=0 included, pi=0); T 3 points
  all pi=1 (x=0 not listed on T, shared 2-torsion lives on E).

## Odd-n P4

Reached exhaustively. E-side usable f_dispersion (2000 targets):

| label | f_dispersion | mean | var/mean |
|---|--------------|------|----------|
| n21 B=1 s201 | 0.99036 | 0.9400 | 1.0196 |
| n21 B=1 s202 | 0.98811 | 0.9345 | 1.0222 |
| n21 random_B s201 | 1.01545 | 0.9545 | 0.9486 |
| n21 random_B s202 | 1.00549 | 1.0230 | 0.9731 |
| n23 B=1 s201 | 0.98500 | 1.0390 | 1.0409 |
| n23 B=1 s202 | 1.00406 | 1.0200 | 0.9937 |
| n23 random_B s201 | 0.99154 | 1.0020 | 1.0389 |
| n23 random_B s202 | 1.00162 | 0.9915 | 0.9878 |

Both parity classes on E are hit (pi0 and pi1 nonzero). T-side usable counts
are 0 on these configs (same pattern as t=2 twist usable in the source run).
Per-R columns: `odd-n-per-R-counts.json`.

## P1–P6 (scored or untestable; not conclusions)

- **P1:** N1 measured = 16 (predicted 0). Localised as above. No claim.
- **P2:** comparison statistics only, three t=2 cells, E usable: pi=1
  nonzero = 0; pi=0 var/mean 0.967–1.042; pooled var/mean 1.438–1.545 vs
  1+mean 1.451–1.516. No “whole deficit” statement.
- **P3:** random V, both classes hit on E; recorded.
- **P4:** f_dispersion on E 0.985–1.015 at the eight odd-n configs.
- **P5:** untestable from the archive (image sizes / fibre histograms, not
  membership).
- **P6:** not a new measurement (re-reading).

## Manifest status

`completed_valid`. Wall 234.1 s. Peak RSS 0.310 GB. Certificate `kind: none`.
Inference: requested `executor-implementation`, resolved
`cursor-grok-4.6-medium`, `model_verified: false`, `fallback_used: true`
with the DEC-20260913-c224bb reason.

## Files written

Under `experiments/EXP-SEMBIN-911efe/runs/RUN-SEMBIN-8be036/`:
manifest.yaml, raw-result.json, parity-split.json, task-report.md,
command.txt, stdout.log, stderr.log, environment.json,
artifact-digests.json, odd-n-per-R-counts.json, and `partial/` incremental
flushes.

Under `experiments/EXP-SEMBIN-911efe/code/`: copied sources plus
`parity_split_run.py`, `run_wrapper.py`.
