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
