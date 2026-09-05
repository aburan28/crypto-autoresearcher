# Derivation note R3 — marginal-cost sign, null-slice reproduction, the
# interior band, and the four k* anomalies

Task TASK-20260904-6681da (Red Team), joint R3. **Derivation, not proof.**
All numbers from `rt_cost_recheck.py` (`R3`) unless marked otherwise.

## 1. The marginal-cost sign flip (H-PFDR-06fd60 (B) and (C))

*Null slice.* `D(k) = ceil(((n-k) + delta)/2) > (n-k)/2`, so
`Ncols(n-k, D(k)) > 2^{n-k-1}` and
`C(k+1)/C(k) = 2 * (Ncols(n-k-1, D(k+1))/Ncols(n-k, D(k)))^omega -> 2 * 2^{-omega}`,
i.e. `log2` ratio `-> 1 - omega < 0` for every `omega > 1`. Recomputed with the
**corrected** `delta = m 2^{m-1}` (note R1 Step 5) the emitted ratios are
`-1.00` (omega 2) and `-1.807` (omega 2.807) at all six fixture cells, strictly
decreasing, argmin at the leaf under both leaf charges. The direction of (B) is
right and is not sensitive to the generator-degree error.

*Bounded slice.* For `D_0 << n' = n-k`,
`Ncols(n'-1, D_0)/Ncols(n', D_0) = 1 - D_0/n' + O(D_0^2/n'^2)`
(from `binom(n'-1,D_0)/binom(n',D_0) = (n'-D_0)/n'` term by term), so
`log2 C(k+1)/C(k) = 1 + omega log2(1 - D_0/n')`, positive exactly when
`n' > D_0/(1 - 2^{-1/omega})` = `3.414 D_0` (omega 2), `4.577 D_0`
(omega 2.807). Exact-versus-asymptotic, at the crossing:

| D_0 | omega | predicted crossing | exact log2 ratio at `n'` = pred-2 / pred / pred+2 |
|---|---|---|---|
| 4 | 2 | 13.66 | -0.084 (11) / +0.078 (13) / +0.200 (15) |
| 4 | 2.807 | 18.28 | -0.052 (16) / +0.066 (18) / +0.161 (20) |
| 6 | 2 | 20.49 | -0.036 (18) / +0.070 (20) / +0.157 (22) |
| 8 | 2.807 | 36.56 | -0.030 (34) / +0.030 (36) / +0.084 (38) |

The exact crossing sits 1–3 residual variables **below** the asymptotic
formula, matching the package's own reported "1 to 3 below". Claim (C)'s sign
derivation is correct **within the model**; the finite-`n` correction never
moves an argmin at the table's sizes (`n - k >= s >= 20` everywhere).

*What the quantity should have done.* The parameter that must destroy the flip
is the residual variable count: as `n - k` falls below `~3.41 D_0` the ratio
must go back below 1 and the argmin must return to the enumerative leaf. It
does, at exactly the predicted place (item 3 below). That is the right
behaviour for a real consequence of the assumption — and it is also why the
flip carries no information about the digit presentation specifically: the same
arithmetic flips for any object one feeds it (see the proves-too-much table).

## 2. The interior band and prediction P5

With the package's `delta = 2m`, `d_reg(k) = D_0` gives residual count
`n - k_c = 2 D_0 - 2m`, i.e. `k_c = n - 2(D_0 - m)`. P5 then charges
`2^{k_c} binom(2(D_0 - m), D_0)^omega`. That top binomial is **zero whenever
`D_0 < 2m`**, because the residual system has fewer variables than the degree:

| m | D_0 | residual `2(D_0-m)` | `binom(2(D_0-m), D_0)` | correct `Ncols(2(D_0-m), D_0)` | `= 2^{2(D_0-m)}`? |
|---|---|---|---|---|---|
| 3 | 4 | 2 | 0 | 4 | yes |
| 3 | 6 | 6 | 1 | 64 | yes |
| 3 | 8 | 10 | 45 | 1013 | no (`D_0 < 2(D_0-m)`) |
| 4 | 4 | 0 | 0 | 1 | yes |
| 4 | 6 | 4 | 0 | 16 | yes |
| 4 | 8 | 8 | 1 | 256 | yes |
| 5 | 4 | -2 | undefined | undefined | — |
| 5 | 6 | 2 | 0 | 4 | yes |
| 5 | 8 | 6 | 0 | 64 | yes |

**Corrected interior-band cost.** The residual Macaulay matrix at `k_c` has
`Ncols(2(D_0 - m), D_0)` columns, which equals `2^{2(D_0-m)}` exactly when
`D_0 <= 2m` (the whole squarefree algebra) and `Ncols` otherwise. So

    C(k_c) = 2^{n - 2(D_0-m)} * Ncols(2(D_0-m), D_0)^omega
           = 2^{n - 2(D_0-m)} * 2^{2 omega (D_0-m)}   for D_0 <= 2m,

which is `2^{n - (2 - 2omega)(D_0 - m)}`, **exponential in `n`** with the same
`2^n` leading behaviour. P5 as frozen is a formula slip (it keeps only the top
binomial of a `Ncols`, and that binomial is degenerate at 7 of the 9 `(m, D_0)`
pairs); the qualitative conclusion it was written to support — the interior band
is exponential in `n` and reproduces the baseline verdict — **survives the
correction unchanged**. The package reported the degenerate values as `null`
and did not repair the frozen formula, which is the right handling.

With the corrected `delta = m 2^{m-1}` the band moves out of existence
altogether: `n - k_c = 2 D_0 - delta` is negative at 8 of the 9 `(m, D_0)`
pairs and at most 4 at the ninth `(m=3, D_0=8)`, while `s >= 20` at every table
cell, so `k_c > n - s` always — the same "outside the guessing range at all 54
cells" the package reports, for a second and stronger reason.

## 3. The four k* anomalies (A1)

At 64 bits the root-finding leaf `2^{n-s} 2^{m-1}` is cheaper than `C(0)` at
four cells. Recomputed independently (my balance, my curve):

| cell (64 bits) | s | n | log2 C(0) | log2 leaf | argmin k | log2 T tabulated (k = 0) | log2 T at the model's own optimum (enumerative balance) | rho |
|---|---|---|---|---|---|---|---|---|
| m 3, D_0 6, omega 2.807 | 39.69 | 119 | 89.18 | 81 | 79 = leaf | 80.38 | 72.58 | 31.83 |
| m 3, D_0 8, omega 2 | 36.74 | 110 | 77.38 | 75 | 73 = leaf | 74.48 | 72.58 | 31.83 |
| m 3, D_0 8, omega 2.807 | 46.48 | 139 | 116.34 | 95 | 93 = leaf | 93.96 | 72.58 | 31.83 |
| m 4, D_0 8, omega 2.807 | 38.46 | 154 | 119.71 | 119 | 116 = leaf | 77.92 | 76.58 | 31.83 |

(my `log2 C(0)` and leaf differ from the executor's by `<= 1` because of where
`s` is rounded before the leaf exponent `n - s`; the ordering is identical.)

**Which `T` the frozen model should have reported.** The frozen model defines
the oracle cost as the hybrid optimum `min_k C(k)`, and at these four cells that
optimum is the enumerative leaf, so the self-consistent total is the
full-guessing balance `T = 2 (m! 2^m B^{m-1} 2^{m-1} N)^{2/(m+1)}` — i.e.
`log2 T = 72.58` (m = 3) and `76.58` (m = 4), the `N^1` endpoint of fixture F1.
The table instead reports the `k = 0` value. This is a disclosed inconsistency
between the model's definition and the table's convention, it is
**conservative** at three of the four cells (the tabulated value is higher than
the model's own optimum), and no verdict moves: all four are `>= 2^{40}` above
rho under either convention. It is not an error in the sign derivation; it is
the null-slice verdict reappearing inside the bounded slice at small `n`,
exactly where item 1 says it must.
