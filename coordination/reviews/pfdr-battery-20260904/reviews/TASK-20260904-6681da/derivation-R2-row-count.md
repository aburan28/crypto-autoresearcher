# Derivation note R2 — bounded last fall versus bounded solve: the row-count
# obstruction to HEUR-001's second clause

Task TASK-20260904-6681da (Red Team), joint R2. **Derivation, not proof.**
Deliberately independent of note R1: it takes the cost model at face value with
a generator of *arbitrary* degree `delta` and asks what a degree-`D` solve can
do.

## Setting

`B = F_p[a]/(a^2 - a)`, `n` variables, one non-field generator `S~` of degree
`delta`, ideal `I = S~ B` (the field equations are already used up by the
quotient). `N_sol` = number of points of `{0,1}^n` on which `S~` vanishes; at
the balance of an index-calculus cell the intended `N_sol` is `O(1)` (the
expected number of decompositions per target is `B^m/(m! N) = N^{-1/(m+1)} << 1`,
and a successful target contributes `O(m! 2^m)` digit solutions).

HEUR-001 (`H-PFDR-06fd60`) has two clauses: (i) `d_lf <= D_0` and (ii) *the
degree-`D_0` Macaulay matrix determines the solutions*. The table prices (ii)
as one rank computation of cost `Ncols(n, D_0)^omega`.

## Step 1. What the priced matrix contains

The degree-`D` Macaulay matrix of a one-generator system has rows `mu S~` for
squarefree monomials `mu` with `deg mu <= D - delta` (nominal multiplier
degree, the convention frozen in `EXP-PFDR-cbdefb`'s
`stage1-closure-convention.md` sub-choice 1). Hence

    rows(D) = Ncols(n, D - delta),     cols(D) = Ncols(n, D),
    rank <= rows(D),
    corank >= Ncols(n, D) - Ncols(n, D - delta) = sum_{D-delta < i <= D} binom(n, i).

## Step 2. The counting consequence for a FIXED D_0

"Determines the solutions" requires at least `corank <= N_sol` (otherwise the
degree-`<= D_0` quotient by the row space is bigger than the solution space and
no solution can be read off, and in the overwhelmingly common no-decomposition
case the row space cannot contain the constant 1). Since `binom(n, i) >= 1` for
`0 <= i <= n`, the deficiency `sum_{D-delta < i <= D} binom(n, i)` cannot fall
to `O(1)` until the window `(D - delta, D]` has left the cube, i.e. until
`D >= n + delta - O(1)`. Computed exactly (`rt_cost_recheck.py`,
`R2.min_D_for_determination`):

| n | m | delta | min D with deficiency <= 1 | <= m! | <= 2^m m! | n + delta - 1 |
|---|---|---|---|---|---|---|
| 30 | 3 | 12 | 41 | 41 | 40 | 41 |
| 60 | 4 | 32 | 91 | 91 | 90 | 91 |
| 100 | 5 | 80 | 179 | 178 | 178 | 179 |
| 269 | 5 | 80 | 348 | 348 | 347 | 348 |

and at the headline cells themselves (`R2.cells`), with `D_0` as tabulated:

| cell | n | delta | cols at D_0 | rows at D_0 | corank lower bound |
|---|---|---|---|---|---|
| 256, m 5, D_0 4, omega 2 | 269 | 80 | 216 582 661 | 0 | `2^27.69` |
| 256, m 5, D_0 6, omega 2 | 289 | 80 | 7.85e11 | 0 | `2^39.51` |
| 256, m 5, D_0 8, omega 2 | 308 | 80 | 1.88e15 | 0 | `2^50.74` |
| 256, m 4, D_0 4, omega 2 | 255 | 32 | 174 825 281 | 0 | `2^27.38` |
| 256, m 3, D_0 4, omega 2 | 237 | 12 | 130 373 069 | 0 | `2^26.96` |

**Conclusion of Step 2.** For a plain one-shot Macaulay solve there is no fixed
`D_0`: the a-priori row count is below what determination needs until `D` is of
order `n + delta`, i.e. `D_0` must grow linearly in `s` — which is exactly the
growth of the semi-regular null slice the bounded slice was introduced to
escape. This is a statement about the object the table prices, not about every
conceivable solver.

## Step 3. The honest loophole, and why it does not rescue the table

Step 2 counts only rows whose *nominal* degree is `<= D`. Extra rows exist
whenever a product `mu S~` **falls** — reduces to degree below `deg mu + delta`.
That is precisely the Huang–Kosters–Yeo closure picture that HEUR-001's second
clause is imitating (`H-PFDR-06fd60` records the HKY solve relation as
`provenance: recalled`, `verified_by: null`; I did not open it either, and it
stays a pointer here).

But a fall at degree `D` needs a multiplier of degree `D - delta >= 1`, so the
first fall obeys `d_ff >= delta + 1` and any closure at degree `D_0 <= delta`
consists of `S~` alone (or of nothing). The closure loophole therefore cannot
produce rows below the generator's own degree, and:

- **measured, m = 2** (`EXP-PFDR-cbdefb` section C, 40 draws per cell, p in
  {4099, 16411, 65537}, closure convention `cbdefb-closure-v1`):
  `d_ff = d_lf = 5, 5, 6, 6` at `s = 2, 3, 4, 5`, i.e. `4 + floor(s/2)`, fitted
  slope `0.4000` with 95% interval `[0.382, 0.418]` (the analysis's own
  mechanical label for the joint outcome is *unresolved*; the slope interval
  excluding 0 is recorded there as a statistic, and reading it as a refutation
  of boundedness is the Validator's and the Coordinator's call, not mine);
- **derived, general m** (`IDEA-20260903-e1e38b` (D4), conditional on Wilson's
  inclusion-matrix rank theorem for the lower bound):
  `d_ff = m 2^{m-1} + floor((s - 2^{m-1})/2) + 1`.

Pricing the closure reading at the package's **own** balance point
(`rt_cost_recheck.py`, `R2.closure_cost`, omega = 2, log2 N = 256):

| m | n | s | `d_ff` | log2 `Ncols(n, d_ff)` | log2 cost `Ncols^omega` | full-guessing leaf `2^{n-s}` | whole cube `2^n` |
|---|---|---|---|---|---|---|---|
| 3 | 237 | 79 | 50 | 172.63 | **345.26** | 158 | 237 |
| 4 | 255 | 63 | 60 | 197.15 | **394.30** | 192 | 255 |
| 5 | 269 | 53 | 99 | 252.22 | **504.44** | 216 | 269 |

One rank at the first-fall degree already costs `2^{235}` times more than
enumerating the entire digit cube at m = 5, and the closure is a *sequence* of
such ranks. Under the only solve degree the data and the derivation support,
the algebraic oracle is worse than brute force, which is the null-slice verdict
(`N^1`) restated, not a route to `N^{2/(m+1)}`.

## What this note licenses

- Narrow, promotable boundary: **for a system consisting of the field equations
  and one generator of degree `delta` in `n` multilinear variables, a single
  Macaulay linear-algebra step at a degree `D_0` fixed independently of `n`
  cannot determine the solutions; the a-priori row count `Ncols(n, D_0 - delta)`
  is below `Ncols(n, D_0) - N_sol` until `D_0` is of order `n + delta`.**
  Everything in that sentence is counting; nothing is curve-specific.
- It does **not** show a fixed-degree solve is impossible for every solver
  (Step 3's loophole is real; what it cannot do is act below `delta`), and it
  does not close the digit-presentation lane. `IDEA-20260808-da1428`'s escape
  (E3) — solvers whose cost is not `Ncols^omega` — is untouched.
