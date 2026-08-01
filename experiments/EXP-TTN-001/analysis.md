# EXP-TTN-001 analysis — TTN contraction of the recursive Semaev tensor with rank truncation (candidate C2)

**Canonical run:** `RUN-TTN-001-b` (valid). `RUN-TTN-001-a` retained (valid_with_defect: derived-summary
timing field truncated by a serialization bug; all cell-level measurements intact and verified
identical to -b; see manifests). 27 cells: `p ∈ {101, 431, 1009}` × `m ∈ {3,4,5}` × seeds
`{20260717, 20260718, 20260719}`. No deviations; no censored cells; stopping rules untouched
(single sage invocation, 101 s wall < 600 s cap). stderr empty.

Protocol: exact F_p Semaev tensors `S_m` (S_3 closed form; S_4, S_5 symbolic formal-degree
resultants along the balanced recursion tree), side `n = 2^{m-2}+1`. Bond = balanced split
`{x1..x_⌊m/2⌋} | rest` (+ m=5 child `{x1,x2,x3}|{x4,x5}`, single-var context). Truncation =
deterministic prefix-CUR over F_p. Counting = contraction of the tensor with the factor-base
Vandermonde (EC x-coords; |FB| = 24/14/9 for m = 3/4/5). Recall measured against the exact zero set.

## 1. Bond ranks (the C2 complexity invariant)

| m | degree d = 2^(m−2) | bond shape | measured χ_full (all 27 cells) | full rank would be | random control (all cells) |
|---|---|---|---|---|---|
| 3 | 2 | 3 × 9 | **3** | 3 (full) | 3/3 ✓ |
| 4 | 4 | 25 × 25 | **6** | 25 | 25/25 ✓ |
| 5 | 8 | 81 × 729 | **15** | 81 | 81/81 ✓ |
| 5 (child) | 8 | 729 × 81 | **15** | 81 | — |

χ_full is identical for every prime, every seed, every curve (27/27 cells): **no field-size
dependence (β = 0.000000 at each m)**. The generic-full-rank obstruction named in the candidate
("bond ranks are generically full") does **not** hold on the tested range: Semaev bonds are
strongly low-rank (6 < 25, 15 < 81). Negative control confirms the apparatus: random tensors of
identical shape are full rank in every cell.

**Observation (exact combinatorial fit):** the measured ranks match the Sylvester-expansion
multiset count `χ(m) = C(2^{m−3}+2, 2)` — 3, 6, 15 at m = 3, 4, 5 (each root-resultant term is a
product of `2^{m−3}` of the 3 coefficients of S_3 in the eliminated variable). If that law persists,
χ(6) = C(10,2) = 45 and the asymptotic slope of log χ vs log d tends to **2** — i.e., into the
disproof region ≥ 1.9. m ≥ 6 is **outside the tested scope**; recorded as a falsifiable
extrapolation (rule 8), not as evidence.

## 2. Recall at capped χ (the actual gate metric)

Pooled-across-seeds recall on the growth bond (χ_full = last point, recall = 1.0 exactly,
0 false positives — prefix-CUR is an exact factorization at full rank, control P3):

| χ/χ_full | m=3 (χ_full=3) | m=4 (χ_full=6) | m=5 (χ_full=15) |
|---|---|---|---|
| best recall at any χ < χ_full | 0.034 (p=101) | 0.266 (p=1009, χ=1) | 0.106 (p=101, χ=1) |
| recall at χ = χ_full − 1 | 0.0058 | **0.0000** (all p) | 0.0000–0.0158 |
| recall at χ = χ_full | 1.0 | 1.0 | 1.0 |

Max recall at any χ < χ_full across all cells and both m=5 bonds: m=3: 0.111, m=4: 0.282,
m=5: 0.197. **χ_needed(recall ≥ 0.99) = χ_full in every one of the 27 cells** (pooled and per-cell).
Over F_p there is no norm and no decaying spectrum: every pivot direction of the exact
factorization is essential to the zero set; truncating even one direction destroys ≥ 72% of
recall (typically ≥ 89%). Truncated tensors also emit false positives (e.g. m=5, χ=1: 4288),
which the candidate's exact-verification witness would filter — recall, not precision, is the loss.

Negative control N2: random-tensor recall at the Semaev matched χ is 0–0.017 (m=4, m=5) — no
spurious recall; the m=3 matched-χ = full dim case reproduces 1.0 trivially (exact reconstruction).

## 3. Promotion-gate arithmetic (numbers only; verdict belongs to the Coordinator)

Growth series across the three sizes (identical at p = 101, 431, 1009):
(d, χ_full) = (2,3), (4,6), (8,15); χ_needed = χ_full.

- **α_full** (least-squares slope, log₂χ vs log₂d, 3 points) = **1.160964** at each p.
- **α_needed** = **1.160964** (χ_needed = χ_full).
- **α_root2** (two-point root-bond-only slope m=4→m=5) = log₂(15/6) = **1.321928**.
- Gate condition α < 1: measured 1.160964 and 1.321928 — **not crossed** (both > 1).
- Disproof trigger α ≥ 1.9: **not triggered** in the tested window.
- Margin vs the dense 1.979 reference (MX-1478, cited from the candidate text, not re-measured
  here): 1.979 − 1.161 = 0.818 (3-point); 1.979 − 1.322 = 0.657 (root-only).

## 4. Dense (MX-1478-style) baseline, measured locally

| m | S_m terms (dense materialization) | t_dense symbolic (s, per cell) | t_contract+count (s) | t_direct verify (s) |
|---|---|---|---|---|
| 3 | 13 | ~0 | ~0.0002 | ~0.01 |
| 4 | 439 | 0.001–0.005 | ~0.0005 | ~0.3 |
| 5 | 54 377–54 777 (of 59 049 possible — near-dense) | 4.39–5.00 | ~0.003 | ~0.9 |

Term growth ×~124 from m=4 to m=5; dense resultant time ×~3500. Toy constant factors only; the
scaling statements rest on measured ranks/term counts, not timings.

## 5. Controls (all pass)

- **P1** S_3 baseline: 20/20 seeded point triples per curve satisfy S_3(x_P, x_Q, x_{−(P+Q)}) = 0.
- **P2** S_4 definition cross-check: symbolic S_4 ≡ per-point formal Sylvester resultant, 200/200 per m=4 cell.
- **P3** CUR exactness: reconstructed tensor == original at χ = rank, every Semaev bond and every random tensor.
- **P4** contraction == direct definition at **every** grid tuple (m=3 closed form; m=4 per-tuple 2×2 Sylvester; m=5 per-tuple 2×4 Sylvester via T_4): 0 mismatches in 27/27 cells — the internal "exact contraction reproduces exact solution counts" control. (No pre-existing ledger S3-harvester artifact exists in this repo to match against; the brute-force definition check is the faithful internal analog.)
- **N1** random tensors full rank: 27/27 cells. **N2** no spurious recall (values above).

## 6. Unexpected observations (rule 8)

1. Bond ranks are curve- and field-independent constants (3, 6, 15) and match the combinatorial
   multiset count C(2^{m−3}+2, 2) exactly — pointing to a provable generic-rank theorem.
2. Recall does not degrade gracefully: at χ = χ_full − 1 it is 0.00 for m=4 (all cells) and
   ≤ 0.016 for m=5. The F_p-norm absence (flagged in the candidate as an "honest sub-question")
   is quantified here: no direction is negligible.
3. S_5 tensors are near-dense as polynomials (~54.5k of 59k coefficients nonzero) yet have
   bond rank 15/81 — sparsity and tensor rank are decoupled.
4. RUN-TTN-001-a summary-serialization defect (sage `round` returns RealDoubleElement; naive
   JSON int()-fallback truncated it). Caught by executor self-audit; fixed; rerun as -b with
   measurements verified identical. No measurement impact.

## 7. Scope and limitations

Toy primes p ≤ 2^10; m ≤ 5; 3 seeds; ordinary short-Weierstrass prime-field curves only.
One truncation rule tested (deterministic prefix-CUR); other truncation/pivoting schemes,
border-rank relaxations, and norm-bearing liftings (e.g. to ℚ or padic norms) are untested.
Recall measured for FB-grid counting; enumeration-by-conditional-contraction not exercised.
Two/three-point exponent fits are window slopes, not asymptotics; the C(2^{m−3}+2, 2) law is an
exact fit on m ≤ 5 and an untested extrapolation beyond. Per rule 7: nothing here is a
crypto-scale statement.
