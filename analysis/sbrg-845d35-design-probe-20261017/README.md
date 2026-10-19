# IDEA-20261017-845d35 design probe (design-experiment, 2026-10-17): returned, not approved

**This is a design-return probe, not program evidence.** It ran no contract, wrote no run record and changed no
status. It records why `/design-experiment IDEA-20261017-845d35` stopped before drafting a contract.

## What was measured
Instrument: plain Macaulay matrix M_D over the Boolean quotient, structural rows S (blocks without the target)
and target rows T(z) (closing S_3 block), z = target bits; T is affine in z (3-point check passes). Refuted target:
the constant 1 lies in the row space of [S; T(z)]; certificate (mu, lambda). Labels from exhaustive enumeration
(quadratic solves, half-trace; field and solver cross-checked against brute force). Vendored builders:
`experiments/EXP-SEMBIN-d9767f/implementation/vendor/boolsys.py` (chained S_3, same descent).

| cell (shape, n, k, SAT fraction) | D | rows_T | refuted / UNSAT | SAT refuted (soundness) |
|---|---|---|---|---|
| chain3, n=9, k=4, 0.752 | 3 | 198 | 0 / 127 | 0 |
| chain3, n=9, k=4 | 4 | 2088 | 0 / 127 | 0 |
| bal4, n=9, k=3, 0.383 | 3 | 279 | 0 / 316 | 0 |
| bal4, n=9, k=3 | 4 | 4194 | 0 / 316 | 0 |
| chain3, n=7, k=3, 0.469 | 4 | 959 | 0 / 68 | 0 |
| chain3, n=7, k=3 | 5 | 4879 | 0 / 68 | 0 |
| chain3, n=7, k=3 | 6 | 17619 | **68 / 68** | 0 |

Pair test at the smallest refuting cell (chain3, n=7, D=6): 8 of 8 random refuted pairs **share** one certificate;
left-kernel dimension of N(z) about 9,000 of 17,619 rows, of the concatenated pair system about 2,700. The sharing
holds by dimension counting (affine solution spaces of dimension about 9,000 meet generically), not because of
structure shared between the two targets.

## Consequences for the idea as written
1. **Its cells are empty.** n in {9, 11}, D in {3, 4}: plain Macaulay refutes no UNSAT target, so `pi_share` has no
   denominator. This matches `analysis/ecdlp2m-iteration-20261009/m3-closure-pilot` (plain M_4 and M_5: 0/60; M_6:
   60/60 at n=9; only the mutant closure W_4 refutes at degree 4).
2. **Its prediction is falsified where it can be tested.** E-point (`pi_share = 0`) fails at the only refuting
   degree (8/8 share). The proposal's own H1 bound, 2^-(c-s) with s the left-kernel dimension, is vacuous when s is
   about half the rows. The random-pencil null therefore matters more than the real system, and the idea's
   `d_star` is dominated by trivial (Koszul/field) syzygies.
3. **Cost.** n=9 at D=6 has about 68,000 target rows and 83,000 columns per instance: beyond the pure-Python
   eliminator used here; n=7 at D=6 costs about 2 s per target and about 6 s per pair.
4. **The cheap refutation is not a single linear combination at D=4.** W_4 certificates are multi-step
   (products of derived polynomials), so they live in a higher-degree Macaulay space.

## What a redesign would have to settle first
- Define the shared object modulo trivial syzygies (quotient by the kernel common to all targets), or measure
  sharing inside the W_4 closure trace instead of the plain Macaulay row space.
- Pre-register a null with the same left-kernel dimensions, so a rate is read against the dimension-forced rate and
  not against zero.
- Choose cells where the refuted set exists and the matrix fits: n=7 at D=6 (or an n=8/9 cell with a C eliminator).

## Reproduce
`python3 scan.py <n> <chain3|bal4> <k> <D>` (refutation rate, soundness) and
`python3 pairs.py <n> <shape> <k> <D> <pairs>` (pair test), run from this directory; dependencies are the vendored
builders under `experiments/EXP-SEMBIN-d9767f/implementation/vendor/`.
