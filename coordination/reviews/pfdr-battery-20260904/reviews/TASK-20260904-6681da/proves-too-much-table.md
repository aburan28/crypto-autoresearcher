# The proves-too-much control for EXP-PFDR-c04716

Task TASK-20260904-6681da (Red Team). Assigned by `review_plan.proves_too_much`.
The argument under test is run **unchanged** — the bounded slice
`D(k) = min(D_0, d_reg(k))`, cost `C(k) = 2^k Ncols(n-k, D(k))^omega` (or the
direct presentation's own dense column count), the balance
`B = (m! 2^m C N)^{1/(m+1)}`, `T = 2 B^2` — against objects for which its
conclusion is KNOWN FALSE. Numbers: `rt_cost_recheck.py`, key
`proves_too_much`. Declared failure signature per object is quoted from the
plan.

## Object 1 — the direct presentation (membership degree `B`)

*Why the conclusion is known false*: `IDEA-20260808-afe4ce`'s floor
`d_lf >= B` for a set-theoretically described factor base, and
`IDEA-20260808-da1428`'s full-guessing optimum with the `k=m-2` / `k=m-1` ratio
`Theta(B^{2 omega - 1})` — which the package's own fixture F2 reproduces.
*Declared signature*: the bounded-slice arithmetic must NOT be applicable, and
**any sub-rho cell emitted for it exposes the table as assumption-only
arithmetic.**

Run at log2 N = 256, `D(k) = D_0`, residual dense column count
`binom(D_0 + (m-k), m-k)`, argmin `k = 0`:

| m | D_0 | omega | log2 C(0) | log2 T | rho | T - rho | `B` at balance | `D_0 < B`? |
|---|---|---|---|---|---|---|---|---|
| 3 | 4 | 2 | 10.26 | 136.92 | 127.83 | +9.10 | `2^67.96` | yes |
| 3 | 8 | 2.807 | 20.68 | 142.13 | 127.83 | +14.31 | `2^70.57` | yes |
| 4 | 4 | 2 | 12.26 | **111.74** | 127.83 | **-16.09** | `2^55.37` | yes |
| 4 | 6 | 2 | 15.43 | **113.01** | 127.83 | **-14.82** | `2^56.00` | yes |
| 4 | 8 | 2.807 | 25.13 | **116.88** | 127.83 | **-10.94** | `2^57.94` | yes |
| 5 | 4 | 2 | 13.96 | **94.95** | 127.83 | **-32.87** | `2^46.98` | yes |
| 5 | 6 | 2.807 | 24.85 | **98.59** | 127.83 | **-29.24** | `2^48.79` | yes |
| 5 | 8 | 2.807 | 29.00 | **99.97** | 127.83 | **-27.86** | `2^49.48` | yes |

**SIGNATURE PRESENT.** 12 of the 18 cells (every m in {4,5} cell, both omega,
every `D_0`) come out sub-rho, the best at `2^94.95` — *better* than any cell of
the digit-presentation table — for an object whose last fall degree is bounded
below by `B = 2^47 .. 2^70`, i.e. `2^44` times the assumed `D_0`. Where the
survival happens: nowhere in particular, and that is the finding — **no step of
the argument ever compares `D_0` with the generator degrees of the system it is
pricing**. `D_0` enters only through `Ncols(., D_0)`; the object enters only
through `n`, `m` and the column-count convention. The table is therefore a
function of the assumption, not of the presentation.

## Object 2 — the digit presentation at m = 2

*Why the conclusion is known false*: the assembly exponent `2/(m+1) = 2/3`
exceeds `1/2`, so no `m = 2` cell can beat rho at any `N`.
*Declared signature*: every `m = 2` cell above rho, or the arithmetic is wrong.

| log2 N | D_0 | omega | log2 T | rho | T - rho | rows at `D_0` |
|---|---|---|---|---|---|---|
| 64 | 4 | 2 | 72.30 | 31.83 | +40.48 | 1 |
| 256 | 4 | 2 | 208.60 | 127.83 | +80.78 | 1 |
| 256 | 6 | 2 | 223.29 | 127.83 | +95.46 | 24 754 |
| 256 | 8 | 2.807 | 265.26 | 127.83 | +137.44 | 200 895 971 |

(all 18 `m = 2` cells in `rt_cost_recheck.py`; minimum margin +40.48).

**SIGNATURE ABSENT — the object passes.** Every `m = 2` cell is above rho, by
`2^40` to `2^137`. Note that `m = 2` is also the **only** part of the whole
grid where the priced Macaulay matrix is nonempty (`delta = 4`, so `D_0 in
{6,8}` gives real rows), and there the route loses to rho by at least `2^95` at
256 bits.

## Object 3 — the m in {3,4,5} cells with `D_0` below the generator degree

*Why the conclusion is known false*: a Macaulay matrix at degree
`D_0 < delta = m 2^{m-1}` has **no rows** (note R1), so "costs
`Ncols(n, D_0)^omega` and solves" cannot hold.
*Declared signature*: the reviewer must exhibit `rows = Ncols(n, D_0 - delta) = 0`
and show the cost model cannot tell an empty matrix from a solving one; an
argument that still prices those cells has proved too much.

| cell | delta | rows at `D_0` | log2 T emitted | rho |
|---|---|---|---|---|
| 256, m 5, D_0 4, omega 2 | 80 | **0** | 108.76 | 127.83 |
| 256, m 5, D_0 6, omega 2 | 80 | **0** | 116.64 | 127.83 |
| 256, m 5, D_0 8, omega 2 | 80 | **0** | 124.13 | 127.83 |
| 256, m 4, D_0 4, omega 2 | 32 | **0** | 128.74 | 127.83 |
| 256, m 3, D_0 4, omega 2 | 12 | **0** | 158.75 | 127.83 |

and the same at all 54 cells (`rt_cost_recheck.py`, `R1.cells`).

**SIGNATURE PRESENT.** The model prices every one of them, including the four
cells it reports as beating rho. The reason it cannot tell the difference is
structural: `Ncols(n - k, D(k))^omega` is a **column** count raised to a matrix
exponent; the row count `Ncols(n - k, D(k) - delta)` never appears in the model
at all, so `delta` is not an input to any cell.

## Object 4 — `D_0 = 2`

*Why the conclusion is known false*: `2 < delta` for every `m >= 2`
(`delta = 4` even at m = 2), so the degree-2 Macaulay matrix has no rows;
`thresholds.yaml` nevertheless reports `T < rho` at `(m 4, D_0 2)` at 256 bits.

| cell | log2 T | rho | sub-rho? | delta | rows at `D_0 = 2` |
|---|---|---|---|---|---|
| 256, m 4, D_0 2, omega 2 | 118.64 | 127.83 | yes | 32 | **0** |
| 256, m 4, D_0 2, omega 2.807 | 123.54 | 127.83 | yes | 32 | **0** |
| 256, m 5, D_0 2, omega 2 | 100.25 | 127.83 | yes | 80 | **0** |
| 256, m 5, D_0 2, omega 2.807 | 104.36 | 127.83 | yes | 80 | **0** |

(the omega-2 value 118.64 reproduces `thresholds.yaml`'s own 118.6.)

**SIGNATURE PRESENT.** The argument goes through and emits four sub-rho cells
for a degree at which the system has no equations whatsoever. These cells are
load-bearing: they are the "largest even `D_0` with `T < rho`" entries that
produce the frozen bracket "`(m 4, omega 2)`: between 2 and 4".

## Summary

| object | conclusion known false because | signature | verdict |
|---|---|---|---|
| 1 direct presentation | afe4ce floor `d_lf >= B`; da1428 boundary optimum | sub-rho cells emitted (12/18, best `2^94.95`) | **argument proves too much** |
| 2 m = 2 | assembly exponent 2/3 > 1/2 | none: all cells above rho by `>= 2^40` | passes |
| 3 m >= 3, `D_0 < delta` | empty Macaulay matrix | finite cost emitted for `rows = 0` at all 54 cells | **argument proves too much** |
| 4 `D_0 = 2` | empty Macaulay matrix | 4 sub-rho cells emitted; bracket depends on them | **argument proves too much** |

The control locates the defect without needing note R1: the bounded-slice
arithmetic has no channel through which a generator degree can reach a cell, so
it prices an assumption rather than an object. Note R1 then identifies which
assumption and by how much.
