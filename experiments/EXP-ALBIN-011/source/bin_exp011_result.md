# BIN-EXP-011 Result — the DIAGONAL cost capstone (honest replacement for BIN-NR-003)

**Date:** 2026-06-01. Script: `bin_exp011_diagonal_capstone.sage`. Log: `bin_exp011_diagonal_capstone.log`.

## SURVIVOR: NO (no practical break) · but the DIAGONAL is asymptotically PQ-favorable under the standard cost model

## What this is
BIN-NR-003 measured the IC/rho cost gap at FIXED m=3 (gap grows ~n/6) — but BIN-OBS-009 showed that misrepresents the Petit–Quisquater diagonal. This experiment measures the TOTAL IC cost along the ACTUAL diagonal **m = round(n^{1/3})**, combining: measured |FB| (subspace enumeration), relation-generation exponent, sparse-LA exponent (2 log₂|FB| + log₂ m), and the per-relation **solve** exponent ω·log₂(Σ_{i≤D} C(N,i)) with D = D_solv = m(m−1)+c (the BIN-OBS-007 measured law; c swept in {0,1,2} to bracket the fall constant). Big-integer arithmetic with bit-length log₂ (a float-overflow bug in the first run — `inf` past n=4096 — was caught and fixed before banking).

## Measured |FB| confirms the diagonal scaling
At m=round(n^{1/3}), measured log₂|FB| tracks n^{2/3}: n=27→8.12 (n^{2/3}=9.0), n=40→11.98 (11.70), n=64→15.0 (16.0). Confirms |FB| ≈ 2^{n^{2/3}} on the diagonal (the basis of BIN-OBS-009).

## Raw result — IC total vs rho along the diagonal (c=1; insensitive to c)

| n | m | LA 2^ | relgen 2^ | D_solv | solve 2^ | IC 2^ | rho 2^ | IC−rho |
|---|---|---|---|---|---|---|---|---|
| 64 | 4 | 32 | 24 | 13 | 104 | 128 | 32 | +96 |
| 256 | 6 | 89 | 51 | 31 | 316 | 366 | 128 | +238 |
| 1024 | 10 | 207 | 128 | 91 | 1038 | 1166 | 512 | +654 |
| 4096 | 16 | 516 | 300 | 241 | 3122 | 3422 | 2048 | +1374 |
| 16384 | 25 | 1315 | 748 | 601 | 8794 | 9542 | 8192 | +1350 |
| **65536** | **40** | 3281 | 1813 | 1561 | 25204 | **27017** | **32768** | **−5751** |
| 262144 | 64 | 8198 | 4392 | 4033 | 71229 | 75621 | 131072 | −55451 |
| 1048576 | 102 | 20567 | 10834 | 10303 | 197885 | 208719 | 524288 | −315569 |

**Crossover: IC drops below rho first at n* ≈ 65536 = 2^16**, and this is INSENSITIVE to the fall constant c (n*=65536 for c=0,1,2 — the m(m−1) term dominates, +c negligible).

## Finding — and the honest correction it completes

**Under the standard heuristic cost model, the Petit–Quisquater diagonal asymptotically beats rho, crossing over near n ≈ 2^16.** This CONFIRMS the BIN-OBS-009 reframe with corrected arithmetic: neither the LA axis (sub-rho on the diagonal) nor the degree axis (PQ-favorable) obstructs it; the binding term is the per-relation solve, and even that becomes sub-rho once n is large enough that ω·D_solv·log(N) < n/2, i.e. ω·m(m−1)·log n < n/2 with m≈n^{1/3} → ω·n^{2/3}·log n < n/2, which holds for large n.

**This REPLACES the campaign's misleading "binary IC loses" headline with the accurate one:** binary Semaev IC loses to rho at fixed small m and at all reachable n, but the asymptotic diagonal beats rho under the standard model — exactly the (heuristic, unproven) Petit–Quisquater claim, which our negatives never refuted.

## Critical caveats (this is NOT a break, and the model is unproven)

1. **HEURISTIC cost model, not a measured solve.** The solve exponent assumes (a) D_solv = m(m−1)+O(1) holds on the whole diagonal — this is PO-BIN-001(b), GENUINELY OPEN, supported by only 2 clean points (m=3,4); and (b) F4 cost = ω·log₂(dense degree-≤D column count) — standard but an over-estimate (real F4 is sparser) and an under-estimate if D_solv exceeds m(m−1). Either could move n* by orders of magnitude. Petit–Quisquater's own constants give n* ">> 2000 or never"; our model gives 2^16. The EXACT n* is model-bound; the QUALITATIVE asymptotic crossover is the robust part.
2. **n*≈2^16 means ~65000-bit binary fields** — astronomically beyond any deployed curve (NIST binary n ≤ 571). **NOT a practical attack on anything.** Deployed binary ECDLP is unaffected.
3. **Generic-curve, prime-n target.** Special-curve speedups (Frobenius/Koblitz) are dead for the exponent (BIN-OBS-009) and don't change this.
4. **Relation-matrix rank / target-descent** not modeled (assumed full-rank, O(1) extra) — standard but unverified at scale.

## Claim label

`HEURISTIC` (MODEL-BOUND, asymptotic) → **BIN-OBS-010**: under the standard index-calculus cost model with the measured D_solv≈m(m−1)+O(1) law, the binary Semaev IC pipeline along the diagonal m=round(n^{1/3}) crosses below Pollard rho at n* ≈ 2^16 (model-dependent; PQ constants give much larger or no crossover), with measured |FB|≈2^{n^{2/3}} confirming the scaling. This is the analytic shadow of the (open, heuristic) Petit–Quisquater subexponential claim; it is NOT a practical break (n* is ~65000-bit) and rests on the unproven PO-BIN-001(b) solve-degree law. It completes the BIN-OBS-009 correction: the campaign's fixed-m negatives do NOT refute the diagonal, and the standard model says the diagonal wins asymptotically.

## What remains OPEN
- PO-BIN-001(b): does D_solv truly stay ≈m(m−1) on the diagonal as m→∞? (2 clean points; m=5 confounded.) This is the one assumption the crossover rests on.
- The F4-cost model constant (dense vs sparse Macaulay) — pins n* but not the qualitative result.
- Whether the relation matrix stays full-rank with O(1)-cost target descent on the diagonal.
