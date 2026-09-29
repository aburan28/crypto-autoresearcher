# The ANF write-down barrier is an encoding artifact above n = 163

Analysis note, 2026-09-29. Written by the top-level session on direct user
instruction. **It is not a ledger evidence record, moves no hypothesis status
and approves nothing.** Its ledger consequence is the additive correction
`CORR-20260929-12a50e` against `EV-ICPERF-784b25`. Independent review of this
note is owed before any finding is promoted from it.

## Question

`EV-ICPERF-784b25` (strength moderate) reports that on the standardised binary
curves up to n = 283 the Weil-descended decomposition system is too large to
write down inside the per-decomposition Pollard rho budget. Its headline
reads: "No solver, however good, removes a term that is paid before the solver
is called." The blog draft `papers/blog-binary-ic-DRAFT.md` repeats this as
Finding 1.

That charge prices one encoding: `S_{m+1}(x_1..x_m, x_R)` expanded in the
`m*l` Boolean unknowns of the `x_i`. It has Boolean degree `m*min(m-1, l)`, so
12 at m = 4. The record's scope note says the charge "does not bind a method
that never materialises it". Two standard methods do materialise a system, just
a different one:

- **Symmetrized** (Faugère–Perret–Petit–Renault 2012, KN-LIT-023): rewrite
  `S_{m+1}` in the elementary symmetric functions `e_1..e_m`, with `e_k`
  as auxiliary unknowns, plus linking equations `e_k = sigma_k(x)`.
- **Chained** (Semaev 2015, the SEMBIN lane): `S_3(x_1, x_2, u_1)`,
  `S_3(u_1, x_3, u_2)`, ..., `S_3(u_{m-2}, x_m, x_R)` with full-field
  auxiliary unknowns `u_i`.

Does the barrier survive either?

## Answer

Only at n = 131 and n = 163, and there by 0.6 to 16 bits rather than 37 to 41.
At n = 233, 239 and 283 both auxiliary encodings fit under the budget with 8 to
37 bits to spare. The sign change moves from (283, 409] to (163, 233].

Per-decomposition ANF size minus the charged budget, in bits, at the best arity
per encoding. Budget, l, R and rho are taken unchanged from
`experiments/EXP-ICPERF-783e9e/impl`, Frobenius arm on, as in the original.

| n | curve | expanded (original) | symmetrized, block | chained, block |
|---|---|---:|---:|---:|
| 113 | SECG-adjacent | +24.1 | −1.2 | −9.7 |
| 127 | Mersenne degree | +24.5 | −2.4 | −11.0 |
| 131 | ECC2K-130 | +40.8 | **+14.3** | **+7.3** |
| 163 | K-163 / B-163 | +37.4 | **+8.0** | **+0.6** |
| 233 | K-233 / B-233 | +6.3 | −27.6 | −37.2 |
| 239 | sect239 | +26.4 | −8.0 | −16.2 |
| 283 | K-283 / B-283 | +18.8 | −17.7 | −26.2 |
| 409 | K-409 / B-409 | −4.9 | −45.9 | −55.0 |
| 571 | K-571 / B-571 | −38.5 | −83.6 | −93.2 |

Every best arity is m = 4 except the expanded n = 127 row, which is m = 3.
The rows at 571 cover m ≤ 4 only; the original's m = 5 figure at 571 is −49.7.
`anf_table.json` holds every (n, m, Frobenius-arm) cell with variable counts,
degrees and both bounds; `anf_summary.json` holds this table.

Three things to read off it:

- **n = 113 and 127 flip only with the Frobenius orbit quotient.** Without it
  they stay above budget by 8.1 to 17.6 bits under both auxiliary encodings.
- **n = 233 flips with or without the quotient.** B-233 without it reads
  −5.9 bits symmetrized and −14.0 chained.
- **ECC2K-130 is the only degree still clearly blocked**, by 7.3 bits under
  the chained encoding. K-163 sits within one bit of its budget under the
  chained block bound, which is an upper bound, so it is inside the resolution
  of this note.

## What was measured

1. **The symmetrized binary summation polynomials** for m = 2, 3, 4
   (`semaev_sym.sage.py`, output `support_m2_3_4.json`). S_3 is written down;
   S_4 and S_5 come from the resultant recursion. Each is rewritten in
   `e_1..e_m` by the fundamental-theorem reduction.

   | m | x-monomials | e-monomials | expanded Boolean degree | symmetrized Boolean degree |
   |---|---:|---:|---:|---:|
   | 2 | 5 | 4 | 2 | 1 |
   | 3 | 23 | 11 | 6 | 2 |
   | 4 | 441 | 68 | 12 | 4 |

   Squaring is F_2-linear, so a monomial `prod e_k^{a_k}` descends to Boolean
   degree `sum_k wt2(a_k)`. The expanded degrees reproduce the original
   record's law `m*min(m-1, l)` exactly, which checks the pipeline.

2. **Known-answer checks** (`verify_semaev.sage.py`,
   `verification_m2_3_4.json`). On E: y² + xy = x³ + x² + (z⁵ + 1) over
   GF(2^17), for m = 2, 3, 4: every polynomial has degree 2^(m−1) in each
   variable; it vanishes on 20 of 20 true sums `x(P_1 + ... + P_m)`; it is
   nonzero at 20 of 20 random wrong targets; and the e-form rebuilds the
   original exactly.

3. **Measured Weil descent** (`descend.sage.py`, `calibrate.py`,
   `calibration.json`). Eleven toy cells, n from 11 to 41, polynomial-basis
   factor base, random a6 and target. The measured symmetrized degree equals
   the prediction on 11 of 11 cells. The block bound equals the measured
   monomial count exactly at m = 3 and is within 0.7 to 2.4 percent of it at
   m = 4. The table therefore prices the symmetrized arm at a near-exact count,
   not a loose bound.

   | cell (n, m, l) | expanded monomials | symmetrized monomials (main + linking) |
   |---|---:|---:|
   | (21, 3, 7) | 22,121 | 1,141 |
   | (20, 4, 5) | 404,296 | 53,375 |

## How each column is charged

- **Budget** is `charged_budget` from the original implementation: rho minus
  sparse linear algebra, divided by the attempt count, at the (l, R) the
  original chose for that (n, m). Only the ANF term changes.
- **Symmetrized.** For a polynomial-basis V = span{1, t, ..., t^(l−1)}, `e_k`
  lies in span{1, ..., t^(k(l−1))}, so it has `d_k = min(n, k(l−1)+1)` bits.
  For a Frobenius-stable V, span(V^k) is not computed here and every `e_k`
  with k ≥ 2 is charged the whole field, `d_k = n`, which can only overstate
  the size. The linking equations are charged at the dense bound on `m*l`
  unknowns at degree m. The system stays zero-dimensional in the same `m*l`
  unknowns as the original.
- **Chained.** m − 2 auxiliary unknowns of n bits each. Every S_3 monomial is
  a product of at most one linear form per block, so each link has at most
  `(1+d_a)(1+d_b)(1+d_c)` monomials. That is a rigorous upper bound; it was
  not calibrated by measurement here.

## What this does not say

- **It is not an attack and not evidence that any curve is weaker.** Writing
  the system down is necessary, not sufficient. At n = 233, m = 4 the
  symmetrized system has 994 Boolean unknowns at degree 4 and must be solved
  within 2^59.2 operations: an exponent of 0.06 in the variable count. The
  only measured solver exponent in the lane is 0.56, at m = 2 on at most 30
  unknowns. The obstruction at 233 to 283 is therefore the solver, which is
  the disputed first-fall-degree question, not the write-down cost.
- **It does not find an encoding-independent barrier at n = 131.** Adding
  auxiliary variables shrinks any polynomial system towards the size of the
  arithmetic circuit that computes it. The chained encoding is the smallest
  examined. A further quadratisation might close the remaining 7.3 bits at
  ECC2K-130; that was not computed.
- **The m = 5 symmetrized polynomial was not finished** when this note was
  written, so m = 5 cells are absent from the auxiliary columns. The original
  record's best arity is m = 4 at every degree up to 409, so this does not
  change the table's verdicts except possibly at 571, which is already negative.
- The rho baseline divides by sqrt(2n) at every degree, as the original does.
  That is correct for Koblitz curves and conservative against index calculus
  on the B-curves.

## Reproduce

```sh
cd analysis/symmetrized-anf-20260929
sage -python semaev_sym.sage.py 2 3 4            # support_m2_3_4.json
sage -python verify_semaev.sage.py 2 3 4         # verification_m2_3_4.json
sage -python descend.sage.py '[[21,3,7],[20,4,5]]' descent_both.json
SKIP_UNSYM=1 sage -python descend.sage.py '[[31,3,10],[41,3,13],[29,4,7],[37,4,9]]' descent_sym_large.json
sage -python calibrate.py                        # calibration.json
sage -python table.py                            # anf_table.json, anf_summary.json
```

Here `sage` is `/opt/conda-sage/bin/sage`. Host: 4-core cloud container. The
largest single step, the n = 37, m = 4 descent, took 53 seconds.
