# m4-sat-cost-pilot: the first m = 4 SAT (WDSat) point-decomposition cost cells

**Exploratory, hypothesis-generating pilot. Not program evidence.** No contract, no run
record, no ledger write, no status change. Toy sizes (n = 13..23, l = 3..7); nothing here
is a statement about ECC2K-130 or any cryptographic size. Everything below is derived from
`results/*.jsonl` by `fit.py`; `aggregate.md` holds the full per-cell table.

## Question
The per-attempt decomposition-cost harvest
(`../ctrial-harvest/README.md`, `fit_tables.md`) finds that at m = 3 WDSat spends
2^(3l)/3! conflicts per UNSAT attempt (slope 2.9985 bits per unit l), i.e. alpha ~ m in a
cost law 2^(alpha l), while relation collection can only beat rho if alpha < m/2 - 1
(0.5 at m = 3, 1 at m = 4). Its gap 1: no SAT solver has ever been run at m >= 4. This
pilot measures WDSat's UNSAT cost at m = 4 for the first time, with m = 3 run through the
same exporter as a control, and asks whether alpha at m = 4 is anywhere near 1.

## Object
Chained S_3 Boolean systems with t = m (pilot #2's Object A, `pilot2_lib.build_chain`,
code byte-identical to `../m45-closure-pilot/`): S_3(u_0, x_0, x_1) = 0,
S_3(u_{i-1}, u_i, x_{i+1}) = 0 (i = 1..m-3), S_3(u_{m-3}, x_{m-1}, z) = 0, u_i in F_(2^n),
x_i in V = {deg < k}, N = (m-2) n + m k Boolean variables, n (m-1) equations (cubic; the
last block quadratic). Curves y^2 + xy = x^3 + x^2 + b over F_(2^n) with #E = 2q, q prime
(`pilot_lib.pick_curve`, seed 0, one curve per n); targets z = x(2P) from
`pilot_lib.subgroup_targets` (seed 0). l = k (log2 |V|). k is varied at fixed n: the
relation l <= n/m of a real relation-collection phase is not needed for a per-attempt
cost law in l, and fixed-n fits (`fit.json`, keys `...|n17`, `...|n23`) separate the
l-dependence from the n-dependence.

**Labels.** Every instance is labelled SAT/UNSAT by pilot #2's two exhaustive
enumerators (`chain_solutions`, curve-level root solving; `boolean_count_chain`, C
enumeration of all 2^(mk) x-assignments with affine u-solves); `enum_agree` is true on
every instance of every cell (`label.py` output in the instance files). WDSat's own
answer agrees with the label on every completed run (`label_agrees_with_solver`), and
every SAT model WDSat returned on a chained instance was evaluated against the boolsys
system and satisfies it (`sat_model_verified`).

**Chained S_3 is a presentation choice.** The paper's m = 3 instances are *direct S_4*
systems in the 3l factor-base bits only (no field unknowns u). Direct S_5 (m = 4) was NOT
run: the repository has no S_5 or S_6 Boolean builder. Checked by
`rg "S_5|S5\b|s5sys|def s5|summation.*(order|degree)\s*5"` over `*.py, *.c, *.sage, *.m2`:
the only hits are the symmetric-group arms of EXP-GFPN-05ff43 and an unrelated run id; the
ctrial-harvest README records the same (gap 1, b94ec8), as does pilot #2's README.

## Solver
WDSat (Trimoska-Dequen), the vendored source `wdsat_987b7f5ef9` (sha256 of every file in
`wdsat_source_sha256.txt`), compiled per instance size class with exact static constants
(as `EXP-ICPERF-66fd51/code/bench.py:anf_sizing` does), `__XG_ENHANCED__` as shipped,
gcc 13.3.0 -O3. Two source patches, both in `wdsat_io.patch_source`:

1. counters: `nodes` (branch points opened) and `fails` (failed branch inferences) printed
   as a `c stats` line; the solver's own `conf` counter and all search code are untouched.
   On every row `nodes == conf` (WDSat's "conflicts" is a count of branch points, one per
   decision; there is no separate decision counter) and `fails == conf + 1` on UNSAT runs.
2. `symfull` (build variant, config `xg_symfull`): stock `-b` branches only on the first
   m*l variables and declares SAT when propagation finds no conflict there. That is complete
   for direct S_4 and for chained m = 3 (once the x's are fixed the u block is F_2-linear and
   XG decides it) but **not** for chained m >= 4 (the middle blocks contain u_{i-1} u_i
   products): on the m = 4 cells stock `-b` returns "SAT" with undefined bits on UNSAT
   instances (recorded as `status: unknown`, config `xg_b`, cell m4-n13-k3). `symfull`
   keeps the lexicographic pruning of the m x-blocks for h < m*l and then branches the u's
   plainly, so it is complete; its answers agree with the labels on every m = 4 row.

ANF export (`wdsat_io.export_anf`): the boolsys monomial masks are written in WDSat's
`x [T] [v | .d v1 .. vd]* 0` format with variables renumbered x-first (x_0 bits, x_1 bits,
..., then u_0 bits, ...), the paper's layout and the one `-b` assumes. WDSat's convention
is "XOR clause = TRUE" (checked against the vendored paper files
`inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/*.anf`, where every equation carries `T`),
so f = 0 is written with T toggled; an earlier draft had the constant inverted and was
caught by the SAT-model check (UNSAT reported on SAT-labelled instances), which is why
that check is kept on every run.

Configurations: `xg` = `-x` (Gaussian elimination, branching on all N variables in file
order); `xg_b` = `-x -b -m m -l k` (stock symmetry breaking); `xg_symfull` = same flags on
the symfull build; `b` = `-b -m 3 -l l` without `-x` (the paper's complete+symmetry
configuration, used only on the paper's own instances).

## Controls
1. **Solver build, paper instances, paper configuration.** The vendored published S_4
   instances `Xn15l5`, `Xn17l6`, `Xn19l6` (`inputs/TRIMOSKA-ECICB-2024`, m = 3) under
   config `b`: see `results/trimoska-control.jsonl` and the trimoska_S4 rows of
   `aggregate.md`. This is the object and configuration the harvest's 2^(3l)/3! law was
   fitted on.
2. **Same instances under `xg` and `xg_b`**, to show what Gaussian elimination changes.
3. **Chained m = 3 through this pilot's exporter** at (n, l) = (13,4), (17,5), (19,6),
   (23,5), (23,6), (23,7), under `xg` and `xg_b`.

## Method
`label.py m n k 14` builds and labels 14 targets per cell; `run_cells.py cell config`
exports, builds, runs (one solver process at a time, 600 s timeout per instance, global
deadline 95 min from launch, censoring never imputed) and appends one JSON line per
(instance, config) to `results/<cell>.jsonl`; `run_trimoska.py` does the same for the paper
instances; `fit.py` (stdlib, seed 20261017, 2000 bootstrap resamples) produces `fit.json`
and `aggregate.md`. UNSAT instances are fitted; SAT costs are reported separately and never
fitted. Host: 4 vCPU Intel Xeon 2.10 GHz, 15 GB shared with two other pilots and with this
pilot's own labelling process, so wall times are indicative only; conflict counts are
deterministic and unaffected.

## Result (state of `results/` at 15:57 UTC, 2026-10-17; the campaign continues in the background until its 17:15 UTC deadline — re-run `python3 fit.py` afterwards; `aggregate.md`/`fit.json` are regenerated from whatever `results/` holds)

Per-cell UNSAT medians (full table with means, walls and SAT rows in `aggregate.md`):

| family | m | n | l | config | N | UNSAT | median conf | 2^(ml)/m! | median/law | median/2^(ml) |
|---|---|---|---|---|---|---|---|---|---|---|
| trimoska_S4 (paper instances) | 3 | 15 | 5 | b (paper config) | 42 | 4 | 5587 | 5461 | 1.023 | 0.171 |
| trimoska_S4 | 3 | 17 | 6 | b | 51 | 4 | 43960 | 43691 | 1.006 | 0.168 |
| trimoska_S4 | 3 | 19 | 6 | b | 51 | 4 | 43976 | 43691 | 1.007 | 0.168 |
| chained_S3 | 3 | 13 | 4 | xg | 25 | 10 | 355 | 683 | 0.52 | 0.087 |
| chained_S3 | 3 | 17 | 5 | xg | 32 | 10 | 1753 | 5461 | 0.32 | 0.054 |
| chained_S3 | 3 | 19 | 6 | xg | 37 | 10 | 12278 | 43691 | 0.28 | 0.047 |
| chained_S3 | 3 | 13/17/19 | 4/5/6 | xg_b | | 10 each | 159 / 678 / 3615 | | 0.23 / 0.12 / 0.08 | |
| chained_S3 | 4 | 13 | 3 | xg | 38 | 10 | 1890 | 171 | 11.1 | 0.46 |
| chained_S3 | 4 | 17 | 3 | xg | 46 | 10 | 1887 | 171 | 11.1 | 0.46 |
| chained_S3 | 4 | 15 | 4 | xg | 46 | 10 | 38110 | 2731 | 14.0 | 0.58 |
| chained_S3 | 4 | 17 | 4 | xg | 50 | 5 (running) | 37048 | 2731 | 13.6 | 0.57 |
| chained_S3 | 4 | 13 | 3 | xg_symfull | 38 | 10 | 160 | 171 | 0.94 | 0.039 |
| chained_S3 | 4 | 17 | 3 | xg_symfull | 46 | 10 | 177 | 171 | 1.04 | 0.043 |
| chained_S3 | 4 | 15 | 4 | xg_symfull | 46 | 10 | 2384 | 2731 | 0.87 | 0.036 |

Fits log2(conf) = a + alpha l over completed UNSAT rows (bootstrap 95% CI):

| group | alpha | CI | budget needs |
|---|---|---|---|
| trimoska_S4, m=3, b (paper object + config) | 2.981 | [2.973, 2.997] | < 0.5 |
| chained_S3, m=3, xg | 2.551 | [2.505, 2.601] | < 0.5 |
| chained_S3, m=3, xg_b | 2.257 | [2.226, 2.289] | < 0.5 |
| **chained_S3, m=4, xg** | **4.328** | **[4.315, 4.340]** (fixed n=17: 4.310 [4.297, 4.325]) | **< 1** |
| **chained_S3, m=4, xg_symfull** | **3.824** | **[3.790, 3.859]** | **< 1** |

Still queued when this README was written (they append to `results/` and enter the fits on
re-running `fit.py`): m4-n17-k4 symfull, m4-n19-k5 symfull (l = 5), m4-n19-k5 xg (1 instance,
expected censored at 600 s), m3-n23-k5/k6/k7, m4-n23-k4, m4-n17-k5 symfull. m = 4 at l = 6 was
not attempted (xg needs ~2^24 branch points at ~1 ms each per instance, outside the 10-minute
limit); m4-n23-k5 could not be labelled (N = 66 > 63-bit enumerator masks).

## Reading (derived, not a decision)
- At m = 4 WDSat's UNSAT cost on chained S_3 grows at alpha = 4.3 bits per unit l with Gaussian
  elimination and 3.8 with symmetry breaking (medians sit at 0.9-1.0 x 2^(4l)/4!), against the
  alpha < 1 that the m = 4 budget requires. The first SAT measurement at m >= 4 therefore lands
  where the harvest's extrapolation put it: the solver enumerates the factor-base tuple up to
  symmetry; nothing in the m = 4 data hints at sub-exhaustive behaviour.
- The symmetry-breaking law 2^(ml)/m! transfers from m = 3 to m = 4 almost exactly
  (ratios 0.87-1.04 on the three completed symfull cells).
- The m = 3 control through this pilot's exporter is cheaper than the paper's law (alpha 2.3-2.6,
  not 3): with Gaussian elimination the chained presentation gives WDSat the u block and the last
  x block linearly once the first two x's are fixed. This is a presentation effect, visible also on
  the paper's own instances (xg/xg_b rows: 0.63-0.73 x law at the same l but slope 3.2), and it does
  not reach the m = 4 verdict (alpha 3.8-4.3 against 1).
- The build itself reproduces the harvest's object and law: paper instances, paper config, 1.006-1.023 x
  2^(3l)/3!, slope 2.981 against the harvest's 2.9985.

## Limitations
1. Chained S_3 is a presentation choice; direct S_5 was not run (no builder exists). Different
   presentations change the constant and, as the m = 3 control shows, even the slope under XG.
2. Two to three l values per m = 4 group so far (l = 3, 4; l = 5 only with symmetry breaking, and
   only once the queued runs land); fits over such short ranges are slopes, not laws. Censoring
   at l >= 5 (xg) biases nothing in the tables (nothing is imputed) but limits the range.
3. Wall times were taken on a shared 4-vCPU host while labelling and two other pilots ran;
   only conflict/node counts are reproducible figures. WDSat has no decision counter separate
   from `conf`; `nodes` and `fails` were added by patch and agree with it row by row.
4. Stock `-b` is incomplete on chained m >= 4 (false SAT with undefined bits); its m = 4 rows
   are recorded as `unknown` and excluded. The `symfull` patch is this pilot's, not the paper's.
5. One curve per n, seed 0, 10-14 targets per cell; SAT instances are rare at these parameters
   (2^(ml)/(m! 2^n) << 1) and their costs are reported only as lists.

## Regenerate
Labelling: `python3 label.py <m> <n> <k> 14 --pilot2 <dir>` where `<dir>` holds pilot #2's code
(`../m45-closure-pilot/`, byte-identical `pilot2_lib.py`, `pilot_lib.py`, `count_chain.c`,
`vendor/boolsys.py`; `vendor/gf2n.py` and `vendor/curve.py` are `experiments/EXP-CERTBIN-060020/impl/`
per `vendor/SOURCES.sha256`; build `libcountchain.so` with gcc -O2 -shared -fPIC). Solving:
`python3 run_cells.py <cell> xg|xg_b|xg_symfull [--unsat 10 --sat 3 --timeout 600]`,
`python3 run_trimoska.py --configs b,xg,xg_b`; both need the WDSat source at `wdsat_io.WDSAT_SRC`
(the vendored `wdsat_987b7f5ef9`, hashes in `wdsat_source_sha256.txt`) and gcc. Then
`python3 fit.py` (deterministic; two runs give identical `fit.json` and `aggregate.md`).
Campaign order as actually run: `campaign.sh`/`campaign2.sh`/`campaign3.sh` (copied here).
Provenance of every number: the `results/*.jsonl` row (instance id, flags, build hash,
anf_sha256, sizing, status, conf/nodes/fails, wall, cpu).
