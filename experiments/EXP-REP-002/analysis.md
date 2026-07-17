# EXP-REP-002 analysis — m=3 model-native PDP solving degree

**Run:** `RUN-REP-002-a` (valid). `p=2^16`, `m=3` chained, `d ∈ {4,6,8}`, 3 seeds.

## Result (all arms dim=0, planted 3-summand decomposition = root)

| d | W_semaev_m3 (baseline) | ED_native_m3 (8 vars) |
|---|---|---|
| 4 | d_reg **2**, vdim 6 | d_reg **2**, vdim 6 |
| 6 | d_reg **2**, vdim 6 | d_reg **2**, vdim 6 |
| 8 | d_reg **2**, vdim 6 | d_reg **2**, vdim 6 |

Identical across seeds. `vdim = 6 = 3!` = the ordered decompositions of `R = F0+F1+F2`;
the planted decomposition is a verified root of every arm — genuine, complete solves.
Edwards native wall-time grows (0.09→31 s across d) while Weierstrass Semaev stays fast:
the 8-variable native Edwards system is **constant-factor costlier** at the **same** `d_reg`.

## Verdict (against the frozen criteria)

**Falsification criterion MET at m=3.** Edwards-native and the Weierstrass-Semaev baseline
have equal solving degree (`d_reg=2`) at every tested `d`, with identical solution counts.
Combined with EXP-REP-001 (m=2, same tie), the model-native PDP **solving degree is invariant
across the curve model at both m=2 and m=3**, and the twisted-Edwards native formulation is
if anything a constant-factor *disadvantage* (more variables) at fixed `d_reg`. No
sub-birthday exponent signal.

## Boundaries

Toy (`p=2^16`, `d≤8`, `m≤3`); Edwards-admitting curves only; `d_reg` metric. Negative closes
only this scope (AGENTS rule 6). Does not test symmetrized/FHJRV Edwards (IC-5: constant-factor).
