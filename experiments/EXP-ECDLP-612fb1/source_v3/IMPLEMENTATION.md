# source_v3 — STAGE 3A / 3B / 3C implementation notes

Contract: `experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml`
(`status: approved`, committed on the working branch at dispatch time).
Task: `TASK-20260907-aad514`, batch `BATCH-8f3e86`, goal `GOAL-ECDLP-bbc21f`.

This file discharges the amendment's `required_implementation_files` note for
`IMPLEMENTATION.md`: it names exactly which `source_v2` functions are reused,
what is new, and how this implementation makes the two choices Section 3
deliberately leaves open.

Observations only. Nothing here interprets a result.

---

## 1. What is reused from the FROZEN v2 instrument, unchanged

`experiments/EXP-ECDLP-612fb1/source_v2/instrument.py` is **imported**, never
copied, forked or edited. `g3_predicate.py` inserts `source_v2/` on `sys.path`
and does `import instrument as I`. Every run manifest hash-pins **both**
`source_v3/*.py` and `source_v2/*.py`, so a reviewer can confirm from the run
record alone that `source_v2/` was not modified.

Reused verbatim, with the Section 3 clause each one implements:

| `source_v2/instrument.py` symbol | used for | Section 3 clause |
| --- | --- | --- |
| `Params` (incl. `mix64_int`, `step`, `is_dp`, `dp_threshold`) | N, T, W, theta, cap; walk key K; DP key K_dp; all four seed streams | `parameters`, `reading_P1_frozen_instrument` |
| `T_OF_NBITS` | the frozen table sizes T = 64 (n=20), T = 256 (n=24) | `parameters`.T |
| `exact_basins` | the pointer-jumping exact-basin closure, cycle mass, capped mass | `basins` |
| `Basins.top_share` | TopShare(t) | `top_share` |
| `Basins.coverage` | StaticCov(T, r) and StaticCovNull(T, r) | `static_coverage` |
| `generate_pools` | the Bernstein–Lange pool at ratio r, every walk charged to P | `pool` |
| `numpy_select` | selection path 1 (numpy lexsort) — **canonical** | `selection`, control `NULL_B_G3` |
| `CountedSelector.select` | selection path 2 (counted streaming min-heap) | control `NULL_B_G3` |
| `table_hash` | table fingerprints in the run records | — |

Nothing else from `source_v2/` is used. `harness_run.py`, `run_ascan.py`,
`run_generic.py` and `analysis.py` are **not** imported: they are v2 drivers
for v2's own stages.

### What is new in `source_v3`

Only glue and the two things v2 has no driver for:

- the **assembly** of the Section 3 predicate out of the frozen pieces above
  (`g3_predicate.measure_cell`);
- the **NULL_A_G3 relabelling** applied to a *static* pool
  (`relabel_pool_evidence`). v2's own `null_a` mode relabels evidence during
  *online re-selection*, inside `run_arm`; this item runs no online arm, so
  the relabelling is applied directly to the pool's evidence multiset instead.
  The stream is v2's own `Params.seed_null_a` (300 + s), unchanged;
- the **BCa bootstrap** (`analyze_v3`), written locally because this host has
  no `scipy` — see §5;
- the run wrappers (§6).

No mathematical quantity is re-implemented. The margin, the coverages and the
basin sizes are computed only by frozen v2 code.

---

## 2. The selection invariant, and how the file is laid out to expose it

The amendment makes it an **invalidation rule** that reading true basin size
anywhere in the *selection* path is invalid — the confound
`EXP-ECDLP-6ac801`'s a = 1/8 disagreement traced to.

`g3_predicate.py` is therefore divided into four labelled regions, in the
order the work happens:

- **REGION A** — exact basins and the oracle ceiling (holds basin arrays);
- **REGION B** — the pool (evidence only);
- **REGION C** — selection (evidence only);
- **REGION D** — scoring and the predicate (basins meet an already-chosen set).

No function in REGION B or REGION C takes an `instrument.Basins`, a basin-size
array, or any array of length N as a parameter, holds one in a closure, or
constructs one. The single object crossing into REGION C is `PoolEvidence`,
whose fields are exactly `dps`, `S`, `h` and three cost counters — all of
length r·T. `_assert_evidence_only` checks that length invariant at run time
(`len(dps) == r*T`, and `S`, `h` the same length), so a basin-length array
smuggled into the weight computation fails loudly rather than silently
producing an oracle selection.

Exact basin sizes enter only in REGION D, through `Basins.coverage(table)`,
where `table` has already been chosen. Exact sizes therefore **score** a
selection and never **make** one.

---

## 3. The two choices Section 3 deliberately leaves open

Section 3 `what_a_reviewer_needs_and_this_section_does_not_give` names two
things it does not fix and requires any re-derivation to disclose its own
choices. This implementation makes them as follows.

**(i) The PRNG that draws the uniform pool starts, and its batching.**
`numpy.random.default_rng(s)` (PCG64), seeded by the walk-key seed *s*, drawing
`rng.integers(0, N, size=4*T, dtype=np.int64)` in batches of `4*T` until the
pool first holds exactly `r*T` distinct DPs. This is `instrument.generate_pools`
unchanged — v2's frozen choice, not a new one.

`build_pool` calls `generate_pools(P, [r])` with a **single-element** ratio
list, one call per (a, r), exactly as the frozen v2 STAGE 0 a-scan
(`source_v2/run_ascan.py`) calls it. The generation sequence is deterministic
in *s*, so the snapshot at `r*T` distinct DPs is the same whether the pools for
several r are generated in one call or separately; calling it the same way as
the a-scan keeps STAGE 3A a replication of that scan's own pool draw rather
than merely a draw from the same law.

**(ii) The tie-break key stream.** A **fresh**
`numpy.random.default_rng(400 + s)` per selection, drawing one `int64` in
[0, 2^63) per pool entry in pool order, sorted **ascending** among equal
weights. `400 + s` is v2's frozen `Params.seed_tiebreak`. Drawing a fresh
generator per selection (rather than advancing one shared stream) is again
`run_ascan.py`'s own pattern.

The NULL_A_G3 relabelled selection reuses the **same** key array, attached to
the same pool positions; only the `(S_d, h_d)` pairs move.

**Which selection path is canonical.** `numpy_select` (the lexsort path), because
that is the path the frozen v2 a-scan used, so STAGE 3A is compared against the
same code path that produced the committed numbers. `CountedSelector` is run on
the same weights and keys as the NULL_B_G3 second path, and the two selected DP
sets are required to be identical as sets; a difference invalidates the cell.

---

## 4. Controls are computed beside the signal, on the same pool draw

`measure_cell(P, basins, r)` computes, for one (N, a, r, seed):

1. the pool at ratio r → `PoolEvidence`;
2. tie-break keys for that pool;
3. `w(d) = S_d + 4·W·h_d` → both selection paths → NULL_B_G3 identity;
4. the NULL_A_G3 relabelling of **that same** `PoolEvidence` → the same weight
   formula, the same keys → `StaticCovNull`;
5. scoring of both selected sets against the same `Basins`;
6. the EXACT_COVERAGE_NON_EXCEEDANCE check
   (`StaticCov ≤ TopShare(T)` and `StaticCovNull ≤ TopShare(T)`).

There is no second pass and no second pool draw: NULL_A_G3 is by construction
on the identical pool, as the amendment's `construction` clause requires.

DECAY_G3 varies only r, over the frozen grid {2, 4, 8}, at fixed (N, a, T_sel, s).

Both stages compute the full control set. Section 5's controls are stated per
(N, a, r, s) without an N restriction, so they are measured at N = 2^20 as well
as at N = 2^24, through the same code path.

---

## 5. The bootstrap

`analyze_v3.bca_mean` — BCa (bias-corrected and accelerated), 95%, **10000**
resamples, resampling generator seeded **20260907**. Both are explicit fields in
`g3_verdict_table.json`. `scipy` is not installed on this host, so the two
normal-distribution functions are local: `norm_cdf` via `math.erfc`, and
`norm_ppf` via Acklam's rational approximation refined by one Halley step
against `erfc` (full double precision).

**Disclosed implementation choice — the resampling unit.** The amendment asks
for a "stratified-by-seed BCa bootstrap 95% CI" on each pooled margin. Each
cell holds exactly one margin per seed, so resampling *within* a seed stratum is
degenerate: it returns that seed's single value every time and yields an
interval of zero width. The non-degenerate reading is that the **seed is the
independent replicate** and the resample is over the five seed-level values;
that is what is implemented. This affects only the CI. It cannot affect a
`margin`, a `pass_count` or a `verdict`, all of which are computed from the
per-seed margins directly and never from the bootstrap. The choice is recorded
here, in `g3_verdict_table.json` (`bootstrap_method`), and in the task's
execution report.

**Property of the estimator, stated rather than interpreted.** With n = 5 there
are at most 5^5 = 3125 distinct resamples, so each CI is a coarse discrete
object whose endpoints can only fall on attainable resample means. The field
`max_distinct_resamples` records this per row, and `z0_proportion_clamped`
records whether the bias-correction proportion hit 0 or 1 and had to be clamped
to 1/(2B).

The margin/margin_null ratio CI (`bca_ratio_of_means`) resamples the seed index
**paired**, so a resample never combines one seed's margin with another seed's
null.

---

## 6. Run wrappers, and why there is no sixth module

The amendment declares **exactly five** `source_v3` files. `source_v2/harness_run.py`
is frozen and its `child_command` knows only v2's own child kinds
(`ascan`, `generic`, `analysis`), so it cannot launch a v3 stage, and it may not
be edited. A separate v3 harness module would be an undeclared sixth file.

`run_stage3.py` and `analyze_v3.py` are therefore each **their own wrapper**:
invoked without `--child` they create the run directory (refusing to overwrite
an existing one), write `command.txt` and `environment.json`, re-execute
themselves with `--child` under `RLIMIT_AS` = 8 GB and a 3600 s `subprocess`
timeout with stdout/stderr captured to the run's log files, then apply the
amendment's invalidation rules and write `manifest.yaml`.

**Five files emitted, five declared. No sixth module was needed.**

Machine protection is copied verbatim from the amendment's Section 10:
`WALL_LIMIT = 3600` s and `MEM_LIMIT_BYTES = 8 GiB` per run, `workers = 1`.
A timeout, a non-zero child exit, or a peak RSS above the ceiling is recorded as
`failed_infrastructure` with failure class `resource_exhaustion` /
`infrastructure_error` and is explicitly **not** a result of any sign
(AGENTS.md core rule 5).

---

## 7. Determinism

`raw-result.json` carries **no timestamp, no wall-clock figure and no absolute
path**: it is a pure function of (stage, seed, code, numpy version). Two
executions at the same seed therefore produce byte-identical files, which makes
its sha256 itself a determinism check. `basin_histogram.json.gz` is written with
`mtime=0` so the gzip container is reproducible too.

Timings live in `summary.json` and `cost_table.json`, which are not compared
byte-wise.

Two determinism checks were run and are reported in the execution report:

- **in-process**, inside STAGE 3C (`build_determinism_check`): one cell per
  stage recomputed from scratch at the declared seed and compared to the stored
  value — recorded in the analysis run's own `raw-result.json`;
- **whole-run**, at the shell: `RUN-ECDLP-612fb1-v3-g3x24-s3`'s child
  re-executed into a scratch directory and its `raw-result.json` sha256
  compared to the committed one. The repeat's output directory is *not* inside
  the declared artifact set — it cannot be — so it is not retained in the
  repository; the two digests are recorded in `execution_report.yaml`.

---

## 8. Artifacts

`run_stage3.py` emits the nine declared files of a measurement run;
`analyze_v3.py` emits the thirteen declared files of the analysis run (no
`basin_histogram.json.gz` — STAGE 3C enumerates nothing). In every artifact the
G3 verdict block is written **before** every other block, mirroring v2's frozen
gate ordering. These artifacts contain no interpretive line at all.

In `cost_table.json`, MEASURED and MODELED quantities sit in separate top-level
blocks and never share a column: `W`, `theta` and `cap` are MODELED; every
count, coverage, margin, bit count and resource measurement is MEASURED.

Certificate kind is `none` on every run: this item solves no logarithm and
finds no relation, so there is nothing to certify.
