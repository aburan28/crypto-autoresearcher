# C1: Gaudry–Diem n=4 with a pi_16 orbit factor base on the c2pnb curves (cost model)

This is a zero-experiment derivation; every figure in it is computed arithmetic. `c1_tables.md` holds the conventions, each with a file:line citation, the provenance of every parameter, heuristics H0–H3 with a toy-ladder validation plan, and the full script output pasted verbatim.

## Setting
- **Curves:** the five ANSI X9.62 example curves c2pnb176v1, 208w1, 272w1, 304w1 and 368w1. Their coefficients lie in F_(2^16). Source: `analysis/binstd-curve-audit/audit-certificate.txt` (OpenSSL provenance; IMP-X962 is still open).
- **Field:** each curve lives over F_(2^(16k)) = F_(Q^4), with Q = 2^(4k) and k = 11, 13, 17, 19, 23.
- **Factor base:** points with x in F_Q. The base is reduced modulo negation and pi_16, which acts with order k on F_Q. That gives N = Q/(2k) orbits.
- **Relation collection:** double large prime (Gaudry–Thomé–Thériault–Diem). The small-prime base size s is optimised analytically.

## Reproduction checks
The script asserts each check to within 0.05 bit before it computes anything else.
- **Matched rho:** 78.10 / 93.98 / 125.78 / 141.71 / 173.57 bits (EV-BINSTD-f541ea). r is recomputed exactly through the Weil recursion.
- **vOW 6nW minima and record point:** taken from `experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c/arm-b-coherent-baseline.json`.
- **HOLD-D floors:** all 18 match within 0.036 bit.

## Headline (margin in bits; positive means C1 is cheaper)

**(i) Time only.** C1 beats rho on all five rows for every c_trial in [2^15.5, 2^32.5].

| row | 176v1 | 208w1 | 272w1 | 304w1 | 368w1 |
|---|---|---|---|---|---|
| margin at c_trial = 2^30 | +1.46 | +5.80 | +14.19 | +18.34 | +26.60 |

**(ii) The program's time×memory convention against vOW 6nW, at p = 0.** C1 loses on every row inside the band, by 35 to 56 bits at c_trial = 2^30.

**(iii) Mesh area-time.** C1 wins only at c_trial ≤ 2^27, on two rows:

| row | margin |
|---|---|
| 304w1 | +1.28 |
| 368w1 | +0.97 |

The break-even c_trial for every row under every metric is tabulated in `c1_tables.md`.

## The one open number
The verdict depends on three quantities, in order:
1. **c_trial**, the per-decomposition cost in rho steps. It has never been measured at toy size.
2. The per-worker FGLM memory, about D^2 elements with D = 4096.
3. The linear-algebra constant.

A toy ladder pins all three: E over F_(2^4), lifted to F_(2^(4k)) for k in {5, 7, 9, 11, 13}, about 2×10^4 decompositions in total. The plan is in `c1_tables.md`.

## Unverified inputs (kept as brief-supplied, and flagged as such)
- The c_trial band and the Granger 247 s figure. KN-LIT-41fe5c covers Granger's abstract only.
- D = 4096.
- The root-extraction floor.
- The mesh routing constant.

## Regenerate
`python3 c1_model.py --verify-repo <repo-root>` (about 11 s). The `--verify-repo` step re-reads four repository files to confirm the embedded constants.
