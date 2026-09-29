# Derivation note R1 — the degree of the digit-substituted generator and the
# Macaulay degree floor it imposes on every bounded-slice cell

Task TASK-20260904-6681da (Red Team), joint R1 of the review plan.
**This is a DERIVATION, not a proof and not a measurement of any curve.** Every
line is meant to be checkable independently. Scope: d = 2 digit presentation,
m in {2,3,4,5}, the parameter grid of EXP-PFDR-c04716.

## Step 1. The object

`IDEA-20260830-84cdb7` claim (A) and `H-PFDR-06fd60` (A) define the decomposition
system in `n = m s` digit variables `a_{k,i}` over `F_p`:

- affine field generators `a_{k,i}(a_{k,i} - 1)`, so the working ring is the
  multilinear quotient `B = F_p[a]/(a^2 - a)` and the columns of a degree-`D`
  Macaulay matrix are the squarefree monomials of degree `<= D`,
  `Ncols(n, D) = sum_{i <= D} binom(n, i)`;
- one non-field generator, the digit-substituted summation polynomial
  `S~ = S_{m+1}(ell_1, ..., ell_m, x_R)` reduced in `B`, where
  `ell_k = sum_{i < s} 2^i a_{k,i}`.

Write `delta = deg S~` (reduced total degree in `B`).

`84cdb7` (A) asserts, verbatim, "one generator of total degree 2m (degree 2 in
each x_k, and each x_k is LINEAR in its digits)"; `H-PFDR-06fd60` (A) inherits
it through `d_reg(k) = ceil(((n - k) + 2m)/2)`, and the contract's
`CTRL-CONFOUNDERS-NAMED` repeats it.

## Step 2. `S_{m+1}` does not have degree 2 in each variable for m >= 3

The parenthesis "degree 2 in each x_k" is the property of `S_3` alone. The
classical degree law, recorded in this program's own corpus, is
`deg_{x_i} S_n = 2^{n-2}` (`knowledge/techniques/KN-TECH-002.md` header field
`complexity`; `knowledge/literature/KN-LIT-001.md` "Key claims"). For
`S_{m+1}(x_1..x_m, x_R)` that is `deg_{x_k} = 2^{m-1}`: 2, 4, 8, 16 at
m = 2, 3, 4, 5.

Two independent checks in this program:

- `EXP-PFDR-5726af`, run `RUN-PFDR-5726af-htop` (symbolic, sympy 1.14.0):
  `S_4(x_1,x_2,x_3,x_R)` has total degree **12** in `(x_1,x_2,x_3)`,
  per-variable degrees `[4,4,4]`, and exactly one degree-12 monomial,
  `x_1^4 x_2^4 x_3^4`, with integer coefficient 1.
- This task, `rt_degree_probe.py` (black-box evaluation over
  `F_p`, `p = 2^61 - 1`, plus exact Lagrange interpolation along a random line;
  seed 20260904, `a`, `b`, `x_R` printed in `rt_degree_probe.out`):

  | m | generator | total degree in the m unknowns | per-variable degrees |
  |---|---|---|---|
  | 2 | `S_3(x_1,x_2,x_R)` | 4 | [2, 2] |
  | 3 | `S_4(x_1..x_3,x_R)` | 12 | [4, 4, 4] |
  | 4 | `S_5(x_1..x_4,x_R)` | 32 | [8, 8, 8, 8] |
  | 5 | `S_6(x_1..x_5,x_R)` | 80 | [16, 16, 16, 16, 16] |

  The m = 2 and m = 3 rows are the instrument's controls: they reproduce the
  hand value 4 and `5726af`'s symbolic 12 by a completely different route
  (numeric Sylvester determinants + interpolation, no CAS).

Interpolation along a random line gives a **lower** bound on the total degree
(equality unless the direction is a zero of the top form). The matching
**upper** bounds come from the Sylvester construction itself, by inspection:
with `S_5 = Res_T(S_4(x_1,x_2,x_3,T), S_3(x_4,x_R,T))`, `deg_T S_4 = 4`,
`deg_T S_3 = 2`, the determinant is a sum of products of 2 coefficients of
`S_4` and 4 coefficients of `S_3`, so
`deg_{(x_1..x_4)} <= 2 * 12 + 4 * 2 = 32` and `deg_{x_1} <= 2 * 4 = 8`;
with `S_6 = Res_T(S_4(x_1,x_2,x_3,T), S_4(x_4,x_5,x_R,T))`,
`deg <= 4 * 12 + 4 * 8 = 80` and `deg_{x_1} <= 4 * 4 = 16`. Lower and upper
bound agree, so the measured values are exact for the resultant-route
polynomial (which is the object this program constructs; `5726af` built `S_4`
that way and `harness/semaev.py` follows the same recursion).

**Corollary (H-TOP at m <= 5, now derived rather than assumed).** Total degree
`m 2^{m-1}` together with per-variable degree `<= 2^{m-1}` forces every
monomial of top degree to have exponent exactly `2^{m-1}` in every variable.
So the top form is the single monomial `c prod_k x_k^{2^{m-1}}`, `c != 0`.

## Step 3. The substitution and the reduction do not lower the degree

Let `F_Delta` be the top form of `S_{m+1}`, `Delta = m 2^{m-1}`. In the
top-form algebra `A = F_p[a]/(a^2) = A_1 (x) ... (x) A_m` (one block per
unknown), reduction `a^2 -> a` strictly lowers degree, so the degree-`Delta`
part of the reduced `S~` is exactly the image of `F_Delta(ell_1, ..., ell_m)`
in `A_Delta`.

`A` is multigraded by block degree. A monomial `c_e prod_k x_k^{e_k}` of
`F_Delta` maps to `c_e prod_k (ell_k^{e_k} in A_k)`, which lies in the block
multidegree `(e_1, ..., e_m)` component and equals
`c_e prod_k [ e_k! sum_{|I|=e_k} (prod_{i in I} 2^i) a_I ]`; it is nonzero
whenever `e_k <= s` and `p > e_k`. Monomials with different `e` land in
different multigraded components, **so no cancellation between them is
possible**. Hence

    deg S~ = delta(m, s) = m * min(2^{m-1}, s),        p > 2^{m-1},

which is `m 2^{m-1}` at every cell of the table (`s = 20..82`, `2^{m-1} <= 16`).
The bound `min(2^{m-1}, s)` is the per-block cap `ell_k^{e} = 0 in A_k` for
`e > s`; the "cap at 2 per block" asserted by `CTRL-CONFOUNDERS-NAMED (iv)` is
not a cap that exists.

Direct check of Step 3 at small `(m, s)` (`rt_degree_probe.py`, Moebius
inversion of the reduced generator over the Boolean cube): a degree-`delta`
coefficient of `S~` is nonzero at `(m,s) = (2,2), (2,3), (2,5), (3,4)`, and at
`(2,3)` and `(2,5)` **every** coefficient of degree `delta + 1` vanishes, so
`deg S~ = 4` exactly there. `EXP-PFDR-cbdefb` Stage 3 at `(m,s) = (3,2)`
independently sees a generator of degree `3 * min(4,2) = 6`.

So `delta = 2m` holds **only at m = 2** (`4 = 2m = m 2^{m-1}`), and the table's
grid is m in {3,4,5}, where `delta` is 12, 32, 80 against the assumed 6, 8, 10.

## Step 4. The Macaulay degree floor

At degree `D` the rows of the Macaulay matrix of the system are the products
`mu S~` with `mu` squarefree and `deg mu <= D - delta` (this is the same
"nominal multiplier degree" convention that `EXP-PFDR-cbdefb`'s frozen
`stage1-closure-convention.md` sub-choice 1 fixes, and the one XL/crossbred
at degree `D_0` uses). Their number is `Ncols(n, D - delta)`, which is **0**
when `D < delta` (empty sum).

`rt_cost_recheck.py` reproduces the package's balance (e.g. `(256, m 5, D_0 4,
omega 2)`: `s = 53.8813`, `n = 269`, `log2 T = 108.7625` — identical to the
archived cell) and then reports, per cell:

| log2 N | m | D_0 | delta | D_0 - delta | rows at D_0 | columns at D_0 | log2 T emitted |
|---|---|---|---|---|---|---|---|
| 256 | 3 | 4,6,8 | 12 | -8,-6,-4 | **0** | 1.3e8 .. | 158.75 / 170.18 / 181.00 |
| 256 | 4 | 4,6,8 | 32 | -28,-26,-24 | **0** | 1.7e8 .. | 128.74 / 138.07 / 146.93 |
| 256 | 5 | 4,6,8 | 80 | -76,-74,-72 | **0** | 2.2e8 .. | 108.76 / 116.64 / 124.13 |

and the same at 128 and 64 bits: **all 54 table cells, and the `D_0 = 2` rows
of `thresholds.yaml`, charge `Ncols(n, D_0)^omega` for a matrix with no rows.**
A matrix with no rows imposes no condition; its "solution set" is the whole
digit cube. Only `m = 2` with `D_0 >= delta = 4` has any row at all, and m = 2
is not in the grid.

The same conclusion in heuristic terms, independent of the cost model: a degree
fall at `D` needs a multiplier `g` of degree `D - delta >= 1` with
`g_top S~_top = 0`, so the first fall degree is `d_ff >= delta + 1`, and
`d_lf >= d_ff`. Any `D_0` satisfying **HEUR-001** must therefore be at least
`delta + 1` = 13, 33, 81 at m = 3, 4, 5. The measured pairs of
`EXP-PFDR-cbdefb` agree exactly at the boundary cells (`m=2, s=2,3`:
`d_ff = 5 = delta + 1`; `m=3, s=2`: `d_ff = 7 = delta + 1`). `D_0 in {2,4,6,8}`
is not merely unvalidated at m >= 3; it is excluded by the generator's own
degree.

## Step 5. Does the null slice (fixture F1) survive?

Recomputing the null curve with the corrected degree,
`D(k) = ceil(((n - k) + delta)/2)` (`rt_cost_recheck.py`,
`R1.corrected_null_fixtures`): at `(m,s) = (3,6), (4,8), (5,8)` and both omega,
`C(k)` is still **strictly decreasing** with argmin at the enumerative leaf
under both leaf charges; the log2 ratios sit at `-1.00` (omega 2) and `-1.807`
(omega 2.807), i.e. the asymptote `1 - omega`. **F1's verdict is unaffected by
the degree error**: the semi-regular slice still reproduces
`IDEA-20260808-da1428`'s full-guessing optimum and `N^1`.

## Step 6. Pricing the corrected floor

Two floors, each solved to a self-consistent balance with the package's own
solver (`rt_cost_recheck.py`, `R1.corrected_floor_cells`), at log2 N = 256
(rho = 127.83):

| m | omega | floor A: `D_0 = delta` (1 row) | floor B: `D_0 = d_ff` (e1e38b (D4)) |
|---|---|---|---|
| 3 | 2 | `D_0=12`, n=301, **log2 T = 201.50** | `D_0=1491`, n=8885, log2 T = 5924.6 |
| 3 | 2.807 | `D_0=12`, n=348, **log2 T = 233.20** | no fixed point (balance diverges) |
| 4 | 2 | `D_0=32`, n=477, **log2 T = 239.35** | `D_0=341`, n=2503, log2 T = 1252.7 |
| 4 | 2.807 | `D_0=32`, n=610, **log2 T = 305.92** | no fixed point |
| 5 | 2 | `D_0=80`, n=855, **log2 T = 342.97** | `D_0=334`, n=2617, log2 T = 1047.97 |
| 5 | 2.807 | `D_0=80`, n=1206, **log2 T = 483.56** | no fixed point |

Floor A is already `2^73` to `2^356` above rho, and it prices a matrix with a
single row, which cannot determine anything (joint R2). Floor B — the smallest
degree at which the ideal acquires anything new at all — is above rho by
`2^920` to `2^5797` where a balance exists, and where `d_ff` grows linearly in
`s` at omega = 2.807 the index-calculus balance has **no fixed point at all**.

## What this note does and does not license

- It does **not** show that no digit-presentation route can beat rho. It shows
  that the specific cells of `cost-table.yaml` and `thresholds.yaml` at
  m in {3,4,5} price a Macaulay matrix that has no rows, and that the
  smallest `D_0` consistent with the generator's own degree is far above the
  grid.
- It does not touch fixtures F1, F2, F3 or the small-N tell, which stand.
- It is a derivation about degrees, not a measurement of any curve, and it
  changes no record's status.
