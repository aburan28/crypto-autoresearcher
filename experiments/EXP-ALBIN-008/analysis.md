# Analysis — Autolab binary-field BIN-EXP-008: Solving degree vs n / subregularity

## Observation
**Date:** 2026-05-31. Scripts: `bin_exp008_solving_degree_vs_n.sage` (system generation, PolyBoRi probe) + `msolve` 0.9.5 (graded F4 degree measurement). Logs: `bin_exp008_solving_degree_vs_n.log`, `/tmp/ms_n*.v` (msolve verbose).

Source excerpt / raw summary:

```
# BIN-EXP-008 Result — graded solving degree D_solv vs n at fixed m (PO-BIN-001)

**Date:** 2026-05-31. Scripts: `bin_exp008_solving_degree_vs_n.sage` (system generation, PolyBoRi probe) + `msolve` 0.9.5 (graded F4 degree measurement). Logs: `bin_exp008_solving_degree_vs_n.log`, `/tmp/ms_n*.v` (msolve verbose).

## SURVIVOR: NO · CANDIDATE: NO · this is the decisive PO-BIN-001 measurement the literature flagged as "never run"

## What was measured
Per `research/proof_obligation_binary_solving_degree.md`, PO-BIN-001(a) asks: **at FIXED arity m, is the solving degree D_solv of the descended binary Semaev system bounded as n→∞?** Bounded → supports the Petit–Quisquater subexponential heuristic; rising with n → refutes it. The crux (Kosters–Yeo) is that the *first-fall* degree d_ff=2 for S₃ does NOT imply low D_solv — **D_solv is the cost-relevant quantity and had not been measured past n≈17**.

**Method.** For ordinary E/F_{2ⁿ}, m=3, factor base in an F₂-subspace V (dim ℓ≈n/3), build + **verify** S₄ (20/20 vanish on real 4-tuples), Weil-descend S₄(x₁,x₂,x₃,xR)=0 to F₂ (fast vectorized descent, validated byte-identical mod x²=x), adjoin field equations c²=c, and measure **the maximum F4 matrix degree reached by `msolve`** — the textbook solving degree D_solv (D1.5 in the obligation note). Target R = P₁+P₂+P₃ is known-decomposable so the system is consistent (real solution verified to satisfy it).

## Raw results (byte-verified from msolve verbose + PolyBoRi)

| n | m | nvars | descended eqs (deg) | **D_solv (max F4 degree)** | msolve status | PolyBoRi reduced-GB max deg | #solutions |
|---|---|---|---|---|---|---|---|
| 11 | 3 | 12 | 11 × deg-6 | **7** | FINISHED | 2 | 12 |
| 13 | 3 | 12 | 13 × deg-6 | **7** | FINISHED | 2 | 6 |
| 17 | 3 | 18 | 17 × deg-6 | **7** | wall (matrix size, not degree) | (PolyBoRi timeout >150s) | — |
| 19 | 3 | 18 | 19 × deg-6 | **7** | wall (matrix size) | (timeout) | — |
| 23 | 3 | 24 | 23 × deg-6 | **7** | wall (matrix size) | (timeout) | — |

## Finding — D_solv is CONSTANT (=7) across the measurable range at fixed m=3

**The graded solving degree D_solv = 7 at every n from 11 to 23**, m=3 fixed. The msolve F4 computation reaches degree 7 and then walls on matrix *size* (degree-6/7 Macaulay matrices grow from 17×9388 at n=17 to 250565×428797 at n=23) — **the degree does not grow with n; the matrix dimension does.** This separates two things the literature conflates:

1. **PolyBoRi reduced-GB max degree = 2** (the *output* basis degree, after full reduction — misleadingly low; the ideal is nearly linear once solved).
2. **msolve F4 solving degree = 7** (the degree the algorithm must *reach internally* — the cost-relevant D_solv that governs binomial(N, D_solv)^ω). These are genuinely different quantities; D_solv=7 is the correct one for PO-BIN-001.

## Interpretation (carefully scoped) → bears on PO-BIN-001(a)

**At fixed m=3, the measured D_solv is bounded (=7, flat) over n∈{11,…,23}.** This is evidence on the **bounded-degree (FPPR-favorable) side of PO-BIN-001(a)** in the measurable range — it does NOT show D_solv rising with n, which would have refuted (a). It is the first direct D_solv-vs-n measurement at fixed m for the binary Semaev system past the n≈13 Gröbner ceiling, reaching n=23 via msolve.

**Crucial caveats (do NOT overclaim):**
- n=17,19,23 did **not finish** — D_solv=7 there is the F4 degree reached before the *matrix-size* wall; it is a firm lower bound, and since the degree-6/7 matrices dominate with no degree-8 round appearing, D_solv=7 is the strongly-supported value, but not a completed solve.
- **Range is narrow (n=11–23) and m is fixed at the smallest non-trivial value (3).** PO-BIN-001(a) is about n→∞; five points over a 2× range of n cannot distinguish "bounded" from "grows like log n" or a constant that jumps at larger m. **(a) remains OPEN.**
- This says **nothing** about PO-BIN-001(b), the diagonal m≈n^{1/3} — there m grows, and D_solv at the smallest non-trivial m=3 gives no information about D_solv at m=6,8,….
- **Independent of the crossover.** Even with D_solv bounded at fixed m, BIN-NR-003 (|FB|²≈2^{2n/3} linear algebra) keeps IC above rho at fixed m=3. The two obstructions are independent (proof-obligation §5); this experiment addresses only the solving-degree one.

## Claim label

```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
