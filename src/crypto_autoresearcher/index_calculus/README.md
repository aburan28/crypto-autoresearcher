# Index calculus for the ECDLP over prime fields

`crypto_autoresearcher.index_calculus` is a self-contained implementation of
the Semaev point-decomposition route to index calculus on prime-order
elliptic curves `E(F_p)`, with Pollard rho on the same curves as the baseline.
It solves toy instances end to end, verifies every logarithm by scalar
multiplication, and counts the cost of every stage.

Nothing here threatens a deployed curve. The point is to measure, honestly,
how the classical prime-field index calculus scales.

## Layout

| module | what it does |
|---|---|
| `curve.py` | curves `y^2 = x^3 + ax + b` over `F_p`; deterministic prime-order curves with a certified order (BSGS in the Hasse interval), optionally restricted by a filter on `p` |
| `semaev.py` | the summation polynomial `S_3` and its roots |
| `factor_base.py` | factor bases: `small_x` (smallest x-coordinates), `subgroup` (x in a coset `g·mu_d` of `F_p^*`), `random` (control); their membership polynomials; the prime filter that makes the subgroup base fair |
| `decompose.py` | decomposition of a point into `m` signed factor-base points: exhaustive (fix `m-2`, solve the last two with `S_3`), or meet-in-the-middle against a table of tails (fix `m-h-1`, solve one with `S_3`, look the rest up); both find the same relations |
| `tails.py` | the table of tails: every signed sum of `h` factor-base points the search can reach, keyed by x-coordinate and built once per factor base |
| `_accel.py` | optional numpy scan that locates the useful `S_3` roots (in the base or in a table of tails); relations and every counter are identical to the pure-Python path |
| `msolve.py` | algebraic decomposition: the Semaev system solved by the msolve Gröbner-basis engine |
| `linalg.py` | incremental sparse elimination mod `N`, stopping at the first relation that fixes the target log |
| `rho.py` | Pollard rho with distinguished points and a Teske 20-adding walk |
| `solver.py` | the end-to-end solver and its cost columns |
| `stats.py` | exponent fits with a stratified bootstrap confidence interval |

## Running it

```sh
pip install -e ".[index-calculus]"      # numpy for the fast path (optional)
apt install msolve                       # only for the msolve engine (optional)

# one instance, index calculus and rho, JSON out
python -m crypto_autoresearcher.index_calculus solve --bits 20 --m 3 --fb small_x --rho

# the same instance with meet-in-the-middle decomposition (same relations, fewer S_3 solves)
python -m crypto_autoresearcher.index_calculus solve --bits 20 --m 3 --fb small_x --engine mitm

# index calculus vs rho over field sizes, 4 processes, rows appended to a JSONL file
python -m crypto_autoresearcher.index_calculus sweep --bits 12 14 16 18 20 \
    --m 2 3 --fb small_x random subgroup --curves 5 --rho-curves 10 \
    --workers 4 --out sweep.jsonl

# both decomposition engines on every base; exhaustive search capped at 24 bits
python -m crypto_autoresearcher.index_calculus sweep --bits 12 16 20 24 28 --m 3 \
    --engine enumerate mitm --m-max-bits enumerate:3=24 --workers 4 --out mitm.jsonl

# per-target cost: msolve vs exhaustive enumeration on a ladder of |F|
python -m crypto_autoresearcher.index_calculus engines --bits 16 --m 2 3 \
    --targets 12 --workers 3 --out engines.jsonl

# refit and tabulate saved rows
python -m crypto_autoresearcher.index_calculus analyze sweep.jsonl engines.jsonl
```

Everything is deterministic in the seeds, so operation counts reproduce
exactly on any machine. Wall times do not reproduce.

## How cost is counted

Costs are counts in separate columns, and columns are never summed.

- **Index calculus.** The primary unit is one `S_3` root solve, i.e. one
  candidate factor-base element tried against a target (one modular square
  root). The other columns are membership tests, group operations, and
  modular multiply-adds in the linear algebra. Group operations are split
  into target generation (`aP + bQ`) and decomposition.
- **Meet-in-the-middle tables.** The `mitm` engine builds its table of
  tails once per run, and the build is inside the run's `s3_solves` (and
  reported on its own as `table_s3_solves`). Adding one factor-base point
  `F` to a stored tail with sum `S` gives `F + S` and `F − S` from one
  shared inversion. That is the pair of x-coordinates one `S_3` solve
  yields, so it is charged as one `S_3` solve, although it needs no square
  root. `table_entries` is the table's size.
- **Rho.** The primary unit is one group addition of the walk (`walk_ops`).
  The fixed scalar multiplications for the step table and the walk starts
  are reported separately as `setup_ops`. At toy sizes that setup term rivals
  the walk, and mixing the two flattens a fitted slope toward 0.3.
- **Exponents.** An exponent is the least-squares slope of `log2(cost)`
  against `log2(N)`. The 95% interval comes from a bootstrap that resamples
  instances within each size.
- **Factor-base size.** `|F|` defaults to `((m! N)/2)^(1/m) / 2`, which gives
  about one decomposition per two attempts.
- **Fair subgroup comparison.** When the subgroup base is in a sweep, `p` is
  drawn so that `p - 1` has a divisor `d` within 15% of `2|F|` for every arity
  in the sweep. Every base in a cell then uses the subgroup base's actual
  size.

## Results (2026-09-24; section 3 2026-09-26)

These are toy sizes: the sweep uses primes of 12 to 32 bits, and the msolve
comparison uses one 16-bit prime. The runs were on a 4-core Intel Xeon
(2.1 GHz) cloud container, with Python 3.11.15, numpy 2.4.6 and msolve
0.6.5 (the Ubuntu 24.04 package).

The raw rows are in `results/`, and one command regenerates every number
below:

```sh
python -m crypto_autoresearcher.index_calculus analyze \
    results/sweep-20260924.jsonl.gz results/engines-20260924.jsonl.gz
```

### 1. Index calculus against Pollard rho, 12–32 bits

```sh
python -m crypto_autoresearcher.index_calculus sweep \
    --bits 12 14 16 18 20 22 24 26 28 30 32 --m 2 3 \
    --fb small_x random subgroup --curves 5 --rho-curves 10 --workers 4
```

- **Runs.** 440 instances: 5 curves per size for each of the six
  index-calculus configurations, and 10 curves per size for rho. Every
  recovered logarithm was checked against `kP = Q`, and none failed.
- **Setup.** `p` was drawn so that `p - 1` hosts the subgroup base at both
  arities. The three bases in a cell have identical `|F|`.

| method | cost unit | exponent in N [95% CI] |
|---|---|---|
| rho | walk group additions | **0.50** [0.48, 0.52] |
| rho | walk + fixed setup | 0.32 [0.30, 0.34] |
| IC, m = 2, small_x | S₃ root solves | **0.99** [0.97, 1.00] |
| IC, m = 2, random | S₃ root solves | 0.98 [0.97, 1.00] |
| IC, m = 2, subgroup | S₃ root solves | 0.97 [0.95, 0.99] |
| IC, m = 3, small_x | S₃ root solves | **1.01** [0.99, 1.02] |
| IC, m = 3, random | S₃ root solves | 1.00 [0.99, 1.01] |
| IC, m = 3, subgroup | S₃ root solves | 1.00 [0.98, 1.01] |

Median cost per instance. Rho is counted in walk additions; index calculus
in S₃ solves.

| bits | \|F\| (m=2) | \|F\| (m=3) | rho walk | IC m=2 small_x | m=2 random | m=2 subgroup | IC m=3 small_x | m=3 random | m=3 subgroup |
|---|---|---|---|---|---|---|---|---|---|
| 12 | 25 | 11 | 54 | 970 | 1,033 | 586 | 811 | 1,451 | 3,161 |
| 14 | 60 | 17 | 118 | 2,639 | 2,442 | 3,793 | 9,316 | 9,533 | 6,901 |
| 16 | 109 | 26 | 318 | 8,961 | 14,348 | 11,789 | 35,393 | 28,124 | 27,463 |
| 18 | 203 | 44 | 391 | 43,365 | 46,691 | 51,984 | 1.22e5 | 1.42e5 | 1.13e5 |
| 20 | 410 | 63 | 1,036 | 1.81e5 | 1.31e5 | 1.39e5 | 4.24e5 | 4.27e5 | 4.82e5 |
| 22 | 914 | 107 | 1,913 | 8.39e5 | 5.82e5 | 7.66e5 | 2.32e6 | 2.38e6 | 2.65e6 |
| 24 | 1,750 | 160 | 5,034 | 3.03e6 | 3.20e6 | 2.31e6 | 9.18e6 | 9.48e6 | 9.90e6 |
| 26 | 2,990 | 250 | 4,956 | 8.69e6 | 1.09e7 | 1.09e7 | 3.31e7 | 2.73e7 | 3.34e7 |
| 28 | 6,485 | 408 | 18,398 | 4.15e7 | 4.36e7 | 4.28e7 | 1.31e8 | 1.48e8 | 1.48e8 |
| 30 | 12,275 | 699 | 37,854 | 1.56e8 | 1.65e8 | 1.56e8 | 4.62e8 | 4.37e8 | 4.23e8 |
| 32 | 27,660 | 1,108 | 75,694 | 8.07e8 | 8.60e8 | 8.08e8 | 2.38e9 | 2.31e9 | 2.36e9 |

What the sweep shows:

- **Index calculus is linear in N; rho is √N.**
  - Exhaustive-decomposition index calculus costs about `N^1.0` at m = 2
    and at m = 3. Rho costs `N^0.50`.
  - At 32 bits the gap is about 10⁴ (8.1·10⁸ S₃ solves against 7.6·10⁴
    walk steps), and it grows like √N.
  - The two units differ: an S₃ solve is one modular square root, a rho
    step one point addition. Each is about one modular exponentiation or
    inversion, which moves constants, not exponents.
- **The factor base's structure changes nothing measurable at matched
  `|F|`.**
  - The confidence intervals overlap.
  - At 32 bits the three bases are within 7% of each other.
  - The relation supply is the same for all three: relations needed are
    0.50·|F| at m = 2 and 0.92·|F| at m = 3, and attempts per relation are
    2.5–2.7.
  - So the high-degree subgroup base behaves like a random set of the same
    size, as the conservation of mean yield (`KN-FIND-007`) predicts.
  - This extends the earlier toy-scale negative for prime-field index
    calculus (`ledger/FINDING-PF-IC-001.md`) to that class.
- **m = 3 has the same exponent as m = 2 and costs 2.7–3.0× more at 32
  bits** with exhaustive decomposition. Its smaller base (N^(1/3) instead
  of N^(1/2)) is offset by `|F|²` S₃ solves per attempt instead of `|F|`.
  Section 3 removes that offset and moves m = 3 to N^0.67.
- **Rho's setup cost explains the old 0.30 slope.** The fixed setup (the
  step table and walk starts) costs 730–2,060 group operations and exceeds
  the walk itself below about 22 bits. The walk alone scales as 0.50; walk
  plus setup gives the 0.3 slope measured before this change.

### 2. Algebraic decomposition (msolve) against exhaustive enumeration

```sh
python -m crypto_autoresearcher.index_calculus engines --bits 16 --m 2 3 \
    --targets 12 --workers 3 --timeout 900 --max-seconds 60
python -m crypto_autoresearcher.index_calculus engines --bits 16 --m 3 \
    --fb subgroup random --max-size 48 --targets 12 --workers 3 --timeout 900 --max-seconds 60
```

The first run was stopped partway through its m = 3 small-x cell at
`|F| = 64`. The second finished the m = 3 ladders on the same curve,
`p = 62401`.

- **Targets.** 687 in all, 345 of them planted as sums of `m` base points.
  417 have at least one decomposition, 590 decompositions in total.
- **Agreement.** msolve finished 685 targets and found exactly the same set
  of decompositions as enumeration on all 685. Every msolve solution lifted
  back to factor-base points.
- **Censored.** The other 2 targets hit the 900 s timeout. They are
  treated as censored, not as "no decomposition".

Per-target exponents below come from cells whose median msolve time is at
least 0.05 s and where at least half the targets finished. msolve's ~4 ms
process start-up is subtracted.

| arity, base | enumeration: S₃ solves vs \|F\| | msolve time vs \|F\| | msolve time vs deg f |
|---|---|---|---|
| m = 2, small_x | 1.00 | **3.80** [3.73, 3.88] | 3.80 [3.73, 3.88] |
| m = 2, random | 1.00 | 3.73 [3.67, 3.79] | 3.73 [3.67, 3.79] |
| m = 2, subgroup | 1.00 | **2.48** [2.44, 2.51] | **2.29** [2.26, 2.32] |
| m = 3, small_x | 1.90 | **4.41** [4.36, 4.45] | 4.41 [4.36, 4.45] |
| m = 3, random | 1.90 | 4.39 [4.35, 4.42] | 4.39 [4.35, 4.42] |
| m = 3, subgroup | 1.89 | 3.54 [3.52, 3.56] | **4.44** [4.42, 4.47] |

Enumeration's m = 3 count is exactly `|F|(|F| + 1)` per target; its slope
is below 2 only because small `|F|` are in the fit. The subgroup base's
membership degree is `d`, which is `2|F|` give or take; the dense bases have
degree `|F|`.

| cell | \|F\| | deg f | enumeration S₃ / target | msolve s / target (median) | msolve finished | agree |
|---|---|---|---|---|---|---|
| m = 2 small_x | 104 | 104 | 104 | 0.120 | 12/12 | 12/12 |
| m = 2 small_x | 258 | 258 | 258 | 3.55 | 12/12 | 12/12 |
| m = 2 random | 258 | 258 | 258 | 3.72 | 12/12 | 12/12 |
| m = 2 subgroup | 104 | 192 | 104 | 0.089 | 12/12 | 12/12 |
| m = 2 subgroup | 258 | 520 | 258 | 0.882 | 12/12 | 12/12 |
| m = 3 small_x | 25 | 25 | 650 | 6.97 | 12/12 | 12/12 |
| m = 3 small_x | 39 | 39 | 1,560 | 52.9 | 12/12 | 12/12 |
| m = 3 small_x | 64 | 64 | 4,160 | ≥ 770 (lower bound) | 1/3 | 1/1 |
| m = 3 random | 39 | 39 | 1,560 | 50.9 | 12/12 | 12/12 |
| m = 3 subgroup | 25 | 48 | 650 | 134 | 12/12 | 12/12 |

What the comparison shows:

- **The algebraic route loses to plain enumeration at every size
  measured.**
  - msolve's per-target cost grows much faster: `|F|^3.7–3.8` against
    `|F|^1` at m = 2, and `|F|^4.4` against `|F|^2` at m = 3.
  - The comparison with rho, which is far cheaper still, doesn't even come
    into it.
  - Wall times are C (msolve) against Python/numpy (enumeration), so
    compare exponents, not times.
- **The sparse subgroup equation `x^d = g^d` helps msolve at m = 2.**
  - Cost grows like `deg^2.3` there, against `deg^3.8` for the dense
    `∏(x − x_j)`.
  - At `|F| = 258` the subgroup base is 4× faster than a dense base of the
    same size, despite having twice the degree.
- **At m = 3 sparsity stops helping.**
  - Every base costs about `deg^4.4`.
  - The subgroup base, of degree ≈ 2|F|, is therefore about 2^4.4 ≈ 20×
    slower than a dense base of the same `|F|` (measured: 134 s against
    7 s at `|F| = 25`).
- **Modeled, not measured: the total exponent is well above rho's
  `N^0.5`.**
  - Combine the sweep's attempt counts (about 2.7 attempts per relation
    and 0.5–0.9·|F| relations at the default `|F|`) with a per-target cost
    of `|F|^γ`. The total is about `N^((1+γ)/m)`.
  - Enumeration gives `N^1.0`, which matches the sweep.
  - msolve gives `N^2.4` (m = 2, dense), `N^1.7` (m = 2, subgroup) and
    `N^1.8` (m = 3, any base).
  - This extrapolates per-target exponents fitted at `|F| ≤ 258` (m = 2)
    and `|F| ≤ 39` (m = 3) on one 16-bit field.

### 3. Meet-in-the-middle decomposition (2026-09-26)

Exhaustive search spends `|F|^(m−1)` S₃ solves on every target. The `mitm`
engine first builds a table of every signed sum of `h` base points that the
search can reach, keyed by x-coordinate (`tails.py`). It builds the table
once per factor base. Each target then needs `m − h − 1` fixed points and one
S₃ solve, and the table lookup does the rest. That is `|F|^(m−h)` S₃ solves
per target.

- **Arity.** The default `h = ⌈m/2⌉` balances the table against the
  search: pairs at m = 3 and m = 4, triples at m = 5. At m = 2, `h = 1` and
  the engine is the exhaustive search.
- **Same relations.** Both engines find the same relation for every target.
  A run therefore makes the same relations, attempts, matrix and logarithm
  under either engine, and only the cost differs. The tests check this
  against brute force on every kind of target, including points of `±F` and
  sums of fewer than `m` points. Every run below checks it again.

```sh
python -m crypto_autoresearcher.index_calculus sweep \
    --bits 12 14 16 18 20 22 24 26 28 30 32 --m 2 3 \
    --fb small_x random subgroup --curves 5 --rho-curves 10 \
    --engine enumerate mitm --m-max-bits 2=0 enumerate:3=24 --workers 4 \
    --out results/sweep-mitm-20260926.jsonl
python -m crypto_autoresearcher.index_calculus sweep \
    --bits 12 14 16 18 20 22 24 26 28 30 32 --m 3 4 5 --fb small_x \
    --curves 5 --rho-curves 10 --engine enumerate mitm \
    --m-max-bits enumerate:3=20 enumerate:4=18 enumerate:5=16 --workers 4 \
    --out results/sweep-arity-20260926.jsonl
gzip -n results/sweep-mitm-20260926.jsonl results/sweep-arity-20260926.jsonl
python -m crypto_autoresearcher.index_calculus analyze results/sweep-mitm-20260926.jsonl.gz
python -m crypto_autoresearcher.index_calculus analyze results/sweep-arity-20260926.jsonl.gz
```

- **Runs.** The first sweep re-solves the 165 m = 3 instances of section 1
  (same curves, bases and targets) and runs rho on the same 110. It passes
  `--m 2 3` with m = 2 capped at 0 bits only because the prime filter
  depends on the arities, so this keeps §1's curves. The second sweep runs
  small_x at m = 3, 4 and 5 on unfiltered curves: 165 instances, plus 110
  rho. Every logarithm was checked against `kP = Q`, and none failed.
- **Same runs, checked.**
  - mitm matched §1's stored enumeration row on all 165 instances, exactly:
    attempts, relations, rank, target operations and linear-algebra
    operations.
  - The 105 enumeration rows (≤ 24 bits) and 110 rho rows re-run for this
    section reproduce every stored count.
  - In the second sweep, the 60 instances run under both engines agree.
- **Host.** A 4-core Intel Xeon (2.8 GHz) cloud container, with Python
  3.12.8 and numpy 2.5.3. Counts are deterministic; wall times are not.

m = 3, medians over the 15 instances of each size (5 curves × 3 bases).
Exhaustive S₃ counts are §1's stored rows. The mitm count includes the
table.

| bits | \|F\| | exhaustive S₃ | mitm S₃ | of which table | ratio | mitm S₃ / rho walk | linear algebra | table entries |
|---|---|---|---|---|---|---|---|---|
| 12 | 11 | 1,521 | 190 | 66 | 8× | 3.5 | 155 | 121 |
| 14 | 17 | 8,208 | 587 | 153 | 13× | 5.0 | 225 | 289 |
| 16 | 26 | 28,888 | 1,385 | 351 | 22× | 4.3 | 537 | 676 |
| 18 | 44 | 1.22e5 | 3,516 | 990 | 35× | 9.0 | 1,092 | 1,936 |
| 20 | 63 | 4.27e5 | 8,857 | 2,016 | 52× | 8.5 | 2,026 | 3,969 |
| 22 | 107 | 2.38e6 | 27,342 | 5,778 | 85× | 14.3 | 5,757 | 11,449 |
| 24 | 160 | 9.48e6 | 65,018 | 12,880 | 138× | 12.9 | 12,175 | 25,600 |
| 26 | 250 | 2.90e7 | 1.36e5 | 31,375 | 211× | 27.5 | 31,592 | 62,500 |
| 28 | 408 | 1.48e8 | 4.23e5 | 83,436 | 349× | 23.0 | 1.03e5 | 1.66e5 |
| 30 | 699 | 4.41e8 | 8.55e5 | 2.45e5 | 527× | 22.6 | 4.41e5 | 4.89e5 |
| 32 | 1,108 | 2.36e9 | 2.56e6 | 6.14e5 | 924× | 33.9 | 1.57e6 | 1.23e6 |

The ratio is the median of per-instance ratios. The rho column divides by
the median rho walk on the same curves, in different units as in §1. Linear
algebra is counted in modular multiply-adds and is the same under both
engines.

| method | cost unit | exponent in N [95% CI] | model |
|---|---|---|---|
| rho | walk group additions | 0.50 [0.48, 0.52] | 1/2 |
| IC, m = 3, exhaustive (§1) | S₃ root solves | 1.01 [0.99, 1.02] (small_x) | 1 |
| IC, m = 3, mitm, small_x | S₃ solves, table included | **0.67** [0.66, 0.69] | 2/3 |
| IC, m = 3, mitm, random | S₃ solves, table included | 0.67 [0.66, 0.68] | 2/3 |
| IC, m = 3, mitm, subgroup | S₃ solves, table included | 0.67 [0.66, 0.68] | 2/3 |
| IC, m = 3, either engine | linear-algebra multiply-adds | 0.64–0.66 | |
| IC, m = 4, mitm, small_x (second sweep) | S₃ solves, table included | 0.75 [0.74, 0.77] | 3/4 |
| IC, m = 5, mitm, small_x (second sweep) | S₃ solves, table included | **0.60** [0.58, 0.61] | 3/5 |

In the second sweep rho measures 0.51 [0.48, 0.53] and m = 3 mitm
measures 0.66 [0.65, 0.68]. At 32 bits the medians are: rho 93,546 walk
additions; m = 3 mitm 2.08·10⁶ S₃ solves (|F| = 984); m = 4 mitm
1.71·10⁷ (|F| = 209); m = 5 mitm 1.38·10⁶ (|F| = 87, 4.5·10⁵ table
entries).

The model column is a derivation, not a fit:

- A run tries about `|F|` targets, since relations needed and attempts
  per relation are both proportional to `|F|` at the default size.
- It therefore costs about `|F|^h` for the table plus `|F| · |F|^(m−h)`
  for the search.
- With `|F| ≈ N^(1/m)` the total is `N^(max(h, m−h+1)/m)`.

What the sweeps show:

- **The exponent moved, not just the constant.**
  - At m = 3 the saving grows from 8× at 12 bits to 924× at 32 bits. The
    exponent drops from 1.0 to 0.67, the model's 2/3, on all three bases.
  - m = 4 and m = 5 land on their models too, 3/4 and 3/5.
  - Wall time at m = 3 and 32 bits fell from a median of 574 s (§1's
    host) to 5.1 s (this host). The hosts differ, so this is a
    practicality note only.
- **It still loses to rho, and the gap still grows.**
  - At m = 3, mitm costs 3.5× rho's walk at 12 bits and 34× at 32 bits.
  - The best arity measured, m = 5, costs 15× rho at 32 bits and grows
    like N^0.1 relative to it.
  - In the model, no choice of `m` or `h` crosses rho, because
    `max(h, m−h+1)/m` is always above 1/2. It tends to 1/2 as `m` grows
    (4/7 at m = 7) but never reaches it.
  - The engine uses S₃ only to add two points, so it is a generic
    algorithm. It stays above rho's exponent, as the model predicts.
- **Linear algebra now costs as much as decomposition.**
  - With exhaustive decomposition, elimination was 10% of the S₃ count
    at 12 bits and under 0.1% at 32 bits.
  - With mitm at m = 3 and 32 bits it is 1.57·10⁶ multiply-adds against
    2.56·10⁶ S₃ solves, and both grow like N^(2/3).
  - A multiply-add is cheaper than an S₃ solve (a square root). But a
    further decomposition gain is capped by the linear algebra unless the
    elimination improves too.
- **The table trades memory for time.**
  - The m = 3 table holds `|F|²` tails, 1.23·10⁶ at 32 bits. One 32-bit
    solve peaked at 430 MB resident (the whole Python process).
  - So memory grows like N^(2/3), where rho needs almost none.
  - m = 5 needs about a third of that table (4.5·10⁵ tails at 32 bits)
    and is also the cheapest arity in S₃ solves there.
- **msolve (§2) is further behind.** §2 compared msolve with exhaustive
  enumeration. At m = 3, mitm spends `|F|` S₃ solves per target plus a
  share of the table, so msolve's `|F|^4.4` per target loses to it by more.
  This is inferred from the exponents; it was not re-measured.

### Caveats

- **Toy scale.** Exponents fitted over 12–32 bits include lower-order
  terms. The operation counts are the primary metric. Wall-time slopes
  (0.67–0.79 for index calculus) are lower because the vectorised scan gets
  more efficient on longer arrays.
- **Linear algebra stops early.** It stops at the first relation that fixes
  `k`: about 0.5·|F| relations at m = 2 (the first cycle in the relation
  graph) and 0.92·|F| at m = 3. A full-rank solve needs about `|F|`, a
  constant factor more. With mitm decomposition that constant lands on a
  phase that is already as large as decomposition (section 3).
- **msolve bound.** The comparison runs below 2^16 because msolve 0.6.5 is
  wrong above that bound (see `msolve.py`). The per-target exponents concern
  `|F|`, not `p`.
