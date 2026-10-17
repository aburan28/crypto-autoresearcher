# Pilot #3: does the degree-4 closure refutation survive a BLOCK-LOCAL monomial restriction?

**Exploratory, hypothesis-generating pilot. Not program evidence.** No contract, no
run record, no ledger write, no status change. Toy sizes (n = 7..11, m = 3..5)
only; it says nothing about ECC2K-130 or any cryptographic size. Run 2026-10-17
on the same 4-CPU / 15 GB host as pilots #1 and #2, sharing it with two other
pilots (wall times are upper bounds), one worker process at a time, 3 GB address
space cap per job (`RLIMIT_AS`), 20 min per job (10 min for the extension cells).

Successor of pilot #1 (`../m3-closure-pilot/`, m = 3) and pilot #2
(`../m45-closure-pilot/`, m = 4, 5). It runs on byte-identical copies of their
labelled instance files (`instances/*.json`; SHA-256 of the sources in
`PROVENANCE.sha256`): labels (SAT = number of Boolean solutions > 0, UNSAT = 0)
come from the two independent exhaustive enumerators of those pilots and were
not recomputed here.

## Question

Pilots #1/#2: the degree-4 mutant closure W_4 refutes every UNSAT chained-S_3
descent at m = 3, 4 while plain Macaulay M_4 refutes none; a support-matched
null is refuted and a dense null is not, so the refutation follows the sparse
block structure. The cost is the dense elimination over all C(N, <= 4)
monomials, which hits the memory wall near 1e5 columns. Question: if the
closure is restricted to monomials that are local to the chain's variable
blocks, is the degree-4 refutation preserved, and how many columns does that
save?

## Object

Chained S_3 with t = m (`pilot3.build_chain`, a verbatim copy of pilot #2's
`pilot2_lib.build_chain`, checked equal to pilot #1's `build_chain3` at m = 3
on instance n9-poly-S3-0000 before anything ran): S_3(u_0, x_0, x_1) = 0,
S_3(u_{i-1}, u_i, x_{i+1}) = 0 for i = 1..m-3, S_3(u_{m-3}, x_{m-1}, z) = 0,
u_i in F_(2^n), x_i in V = {deg < k}, N = (m-2) n + m k Boolean variables.

**Variable blocks** (m - 1 of them, one per S_3 equation block):
B_0 = (u_0, x_0, x_1); B_i = (u_{i-1}, u_i, x_{i+1}) for i = 1..m-3;
B_{m-2} = (u_{m-3}, x_{m-1}); z is a constant. u_i lies in the two adjacent
blocks i and i+1. **Locality** of a monomial = the minimal number of consecutive
blocks whose union contains all of its variables = max(1, B - A + 1) with
A = min over its variables of the highest block containing the variable and
B = max of the lowest block (`myclosure_local.c: locality`). Every generator
(each descended Boolean equation of one S_3 block) has locality 1; this is
asserted per instance by `pilot3.py`.

Column counts at D = 4 (exact, `pilot3.locality` over all C(N, <= 4) monomials):

| cell | k | N | blocks | all monomials (full W_4) | L <= 1 | L <= 2 |
|---|---|---|---|---|---|---|
| m=3 n=9 | 3 | 18 | 2 | 4,048 | 2,479 | = full |
| m=3 n=11 | 4 | 23 | 2 | 10,903 | 6,415 | = full |
| m=4 n=7 | 2 | 22 | 3 | 9,109 | 3,137 | 7,727 |
| m=4 n=9 | 3 | 30 | 3 | 31,931 | 9,770 | 26,258 |
| m=4 n=11 (extension) | 3 | 34 | 3 | 52,956 | 18,837 | 45,339 |
| m=5 n=9 k=3 (extension) | 3 | 42 | 4 | 124,314 | 17,061 | 65,649 |

## Method

`myclosure_local.c` is pilot #1/#2's independent bit-packed GF(2) eliminator
`myclosure.c` (no M4RI; sha256 `ce2b374f…`) with one change: the column set is
the subset of degree <= D monomials with locality <= Lmax (hash-indexed), and a
product x_j * g is **dropped as a whole** whenever any of its monomials falls
outside the column set. Nothing is ever truncated term-wise, so every row of
every variant is a genuine element of the ideal, and the restricted closure
is a subspace of the full W_D: a refutation by L <= 1 or L <= 2 implies a
refutation by W_4, and a false refutation of a SAT instance would be a bug.
With Lmax >= number of blocks and no multiplier rule the code is exactly the
old `my_closure` (`full` below): rank, verdict and column count agree with
pilot #1's recorded `myW_4` rows on every instance checked (n9-poly 0000,
0001, 0003, 0005, 0010: ranks 3839/3838/3836/4045/4045).

Variants (`pilot3.py run <cell> <variants>`):

- `full`: W_4, no restriction (the control; `stop_at_one` as in the earlier `myW`).
- `L1`, `L2`: columns restricted to locality <= 1, <= 2.
- `adj<r>` ("multiply only by variables of the same or adjacent block"): all
  columns, but a basis row g is multiplied only by variables whose block
  interval meets g's own block window widened by r on each side (r = 0 same
  block, r = 1 adjacent). `L1adj0`, `L2adj1` combine both rules.

Per instance and variant the worker records columns, rows (generators +
products inserted), rank, contains_one, products dropped, pivots by degree and
by locality, wall s and peak RSS of the worker process, and on SAT instances
the number of basis rows that fail to vanish at up to 16 known solutions
(always 0) and codim = columns - rank. Clopper-Pearson 95% intervals are exact
(`aggregate.py`, stdlib).

Instance selection (the first non-duplicate targets in file order, as the
earlier pilots selected): m=3 n=9: 60 UNSAT + 8 SAT (all); m=3 n=11: first
20 UNSAT + first 10 SAT (pilot #1's `myW_4` subset was the first 20 UNSAT +
first 5 SAT); m=4 n=7: 25 UNSAT + 4 SAT (all); m=4 n=9: 10 UNSAT + 4 SAT
(pilot #2's W_4 subset). Extension cells (not in the request, local variants
only): m=4 n=11 first 10 UNSAT + 2 SAT at L1, 5 UNSAT at L2; m=5 n=9 k=3
first 10 UNSAT + 3 SAT at L1, 5 UNSAT at L2.

## Result (`aggregate.md`, regenerated by `python3 aggregate.py`; raw rows in `results/*.jsonl`)

Summary (per cell; `aggregate.md` has rows, dropped products, pivots and the adjacency variants).
Columns = size of the elimination; reduction relative to the full W_4 of the same cell.
UNSAT refuted and SAT false refutations carry exact Clopper-Pearson 95% intervals.
"median wall" is the worker process (UNSAT runs stop when 1 enters; SAT runs go to the fixpoint).

| cell | variant | columns (vs full) | UNSAT refuted [CP95] | SAT false refut. [CP95] | median wall UNSAT / SAT | median peak RSS |
|---|---|---|---|---|---|---|
| m=3 n=9 (60 U, 8 S) | full | 4,048 | 60/60 [0.94, 1.00] | 0/8 [0.00, 0.37] | 0.0 s / 0.2 s | 13 MB |
| | L1 | 2,479 (-39%) | 60/60 [0.94, 1.00] | 0/8 [0.00, 0.37] | 0.0 s / 0.1 s | 12 MB |
| | adj0 / adj1 | 4,048 | 60/60, 60/60 | 0/8, 0/8 | 0.0 / 0.4 s, 0.0 / 0.3 s | 12 MB |
| m=3 n=11 (20 U, 10 S) | full | 10,903 | 20/20 [0.83, 1.00] | 0/10 [0.00, 0.31] | 1.2 s / 6.2 s | 25 MB |
| | L1 | 6,415 (-41%) | 20/20 [0.83, 1.00] | 0/10 [0.00, 0.31] | 0.4 s / 0.9 s | 16 MB |
| | adj1 | 10,903 | 20/20 [0.83, 1.00] | 0/10 [0.00, 0.31] | 1.2 s / 6.0 s | 25 MB |
| m=4 n=7 (25 U, 4 S) | full | 9,109 | 25/25 [0.86, 1.00] | 0/4 [0.00, 0.60] | 0.1 s / 1.6 s | 20 MB |
| | L1 | 3,137 (-66%) | 25/25 [0.86, 1.00] | 0/4 [0.00, 0.60] | 0.0 s / 0.1 s | 13 MB |
| | L2 | 7,727 (-15%) | 25/25 [0.86, 1.00] | 0/4 [0.00, 0.60] | 0.1 s / 1.0 s | 17 MB |
| | adj0 / adj1 | 9,109 | 25/25, 25/25 | 0/4, 0/4 | 0.2 / 5.5 s, 0.1 / 2.0 s | 17-19 MB |
| | L1adj0 | 3,137 (-66%) | **4/25 [0.05, 0.36]** | 0/4 [0.00, 0.60] | 0.0 s / 0.1 s | 13 MB |
| m=4 n=9 (10 U, 4 S) | full | 31,931 | 10/10 [0.69, 1.00] | 0/4 [0.00, 0.60] | 9.3 s / 114 s | 122 MB |
| | L1 | 9,770 (-69%) | **9/10 [0.55, 1.00]** | 0/4 [0.00, 0.60] | 1.6 s / 2.0 s | 23 MB |
| | L2 | 26,258 (-18%) | 10/10 [0.69, 1.00] | 0/4 [0.00, 0.60] | 7.1 s / 54 s | 79 MB |
| | adj1 | 31,931 | 10/10 [0.69, 1.00] | 0/4 [0.00, 0.60] | 8.6 s / 166 s | 113 MB |
| | L2adj1 | 26,258 (-18%) | 10/10 [0.69, 1.00] | 0/4 [0.00, 0.60] | 6.8 s / 54 s | 77 MB |
| m=4 n=11, ext. (10 U, 2 S) | L1 | 18,837 (-64% vs 52,956) | 10/10 [0.69, 1.00] | 0/2 [0.00, 0.84] | 9.4 s / 10.4 s | 56 MB |
| | L2 (5 U) | 45,339 (-14%) | 5/5 [0.48, 1.00] | — | 38 s / — | 210 MB |
| m=5 n=9 k=3, ext. (10 U, 3 S) | L1 | 17,061 (-86% vs 124,314) | **0/10 [0.00, 0.31]** | 0/3 [0.00, 0.71] | 4.7 s / 5.0 s | 44 MB |
| | L2 (5 U) | 65,649 (-47%) | 5/5 [0.48, 1.00] | — | 170 s / — | 483 MB |

Pooled (all cells): full 115/115 UNSAT, 0/26 SAT; L1 124/135 UNSAT [0.86, 0.96], 0/31 SAT [0.00, 0.11];
L2 45/45 UNSAT [0.92, 1.00], 0/8 SAT; adj1 115/115, 0/26; L1adj0 4/25; L2adj1 10/10, 0/4.
Soundness: 111 completed SAT runs, 0 with 1 in the basis, 0 of 809 witness evaluations
non-vanishing, no eliminator error codes, no time-outs, no memory kills.

Minimal locality that refutes, per UNSAT instance: L = 1 on 124 instances (all of m=3 n=9,
m=3 n=11, m=4 n=7, m=4 n=11 and 9 of 10 at m=4 n=9); L = 2 on m4-n9-S3-0004 (the one L1 miss)
and on all 5 m=5 n=9 k=3 instances tried at L2 (L1 refuted none of 10 there; the five L2
instances are 0000, 0001, 0004, 0006, 0007, all L1 misses). No instance needed L = 3.

SAT codim: equals the number of Boolean solutions on every `full`, `L2`, `adj1` and `L2adj1`
SAT run (26/26, 8/8, 26/26, 4/4). Under `L1` it differs on 11 of 31 SAT runs (and under `adj0` on 1 of 12), in both
directions (e.g. m4-n9-S3-0000: codim 38 vs 4 solutions; m4-n9-S3-0006: 33 vs 46;
m5-n9k3-S3-0005: 3,118 vs 149). That is expected for a strictly smaller closure on a
smaller monomial space (codim bounds the rank of the solution-evaluation functionals on
the local monomials, which need not separate the solutions) and is not a soundness signal;
the witness evaluations are the soundness check.

## Reading (derived; not a decision)

1. **The degree-4 refutation is block-local at m = 3 and 4, with one exception.**
   Restricting the closure to locality-1 monomials (-39% to -69% columns) keeps
   the W_4 verdict on 124 of 125 UNSAT instances across m=3 n=9/11 and m=4
   n=7/9/11, with zero false refutations on 31 SAT instances. The one miss
   (m4-n9-S3-0004) is refuted at L <= 2. At m = 4 the L <= 2 saving is small
   (-14% to -18%): with u_{i-1} and u_i both in block i, most degree-4
   monomials of three blocks already have locality <= 2.
2. **At m = 5 with |V| = 8 the refutation is NOT locality-1 but IS locality-2.**
   L1 refutes 0/10 UNSAT instances of m=5 n=9 k=3, L2 refutes 5/5. Because every
   L2 row is an element of W_4, this also settles, as a lower bound, the cell
   pilot #2 could not run (124,314 columns, "the one cell that decides whether
   the degree stays at 4 at m=5"): **W_4 refutes at m = 5, k = 3 on all five
   instances tried**, and pilot #2's W_3 refuted 0/30 there, so the minimal
   refuting closure degree is 4 at m = 3, 4 and 5 with |V| = 8. The L2 run cost
   170 s and 483 MB per instance against an infeasible full elimination.
3. **Restricting the multipliers is the wrong knob.** `adj1` (adjacent-block
   multipliers, all columns) changes no verdict and saves no columns; `adj0`
   likewise at m = 3, 4; but `L1adj0` (local columns and same-block multipliers)
   collapses to 4/25 at m=4 n=7. The refutation needs products that carry a
   block-local row across the shared u variables into the neighbouring block;
   it does not need non-local monomials as intermediate columns at m <= 4, and
   needs two-block monomials at m = 5.
4. **What it suggests for cost.** At fixed D = 4 the elimination size falls
   from C(N, <= 4) to roughly (number of blocks) x C(block-pair size, <= 4),
   i.e. linear in m at fixed block width (n + 2k variables per block pair),
   instead of ~(m n)^4 / 24. On these cells that is 2.5x (m=4) to 7x (m=5,
   L1; but L1 does not refute there) and 1.9x at the locality that does
   refute at m = 5. Whether locality 2 suffices at m >= 6, or the needed
   locality grows with m, is the next measurable question; this pilot cannot
   answer it (4 blocks at most). None of this changes the ECC2K-130 verdict
   of `../wwit-ecc2k130/`; it narrows the per-attempt constant, not the
   exponent.

## Limitations

- Same instances, curves (one per n, seed 0), polynomial basis V and labels as
  pilots #1/#2; nothing new was labelled, and no null controls were run here
  (the null question was settled by the earlier pilots and is orthogonal to the
  column restriction).
- The eliminator stops as soon as 1 enters the basis (`stop_at_one`), so rank,
  rows and wall time on UNSAT instances are those of a partial closure; only
  SAT instances run to the fixpoint. Compare UNSAT-to-UNSAT and SAT-to-SAT.
- The host was shared with two other pilots; wall times are upper bounds and
  the small-cell times (< 1 s) are dominated by process start-up.
- One eliminator, one ordering (degree, then colex; products processed in
  insertion order). The set of rows a bounded closure reaches to fixpoint does
  not depend on order, but which UNSAT instances a *partial* run (stop at 1)
  touches does affect timings, not verdicts.
- Sample sizes are small where it matters most: 10 UNSAT at m=4 n=9, and the
  extension cells have no full W_4 reference (m=5 n=9 k=3 was never run at
  D = 4 in pilot #2: 124,314 columns), so a local refutation there is a lower
  bound on W_4's power, not a comparison.
- m = 3 has only two blocks, so L <= 2 is the full closure there; the L <= 2
  cells are m = 4 (and m = 5 in the extension).
- Toy sizes. Nothing here is a cost model; the column reduction at fixed D is
  a constant factor per cell and the counts above grow with N at the same
  polynomial rate.

## Regenerate

```
gcc -O2 -Wall -fPIC -shared myclosure_local.c -o libmyclosure_local.so
./driver.sh      # the four requested cells, as run (about 60 min on this host)
./driver2.sh     # the extension cells, as run
python3 aggregate.py
```

Files: `pilot3.py` (driver: blocks, locality, instance selection, soundness
stop), `worker3.py` (one job per process), `myclosure_local.c`,
`aggregate.py`, `driver.sh`, `driver2.sh`, `instances/*.json` (copies),
`vendor/boolsys.py`, `vendor/gf2_chained_builder.py` (copies of pilot #2's
vendored builder, see `vendor/SOURCES.sha256`), `PROVENANCE.sha256`,
`results/*.jsonl`, `aggregate.md`.
