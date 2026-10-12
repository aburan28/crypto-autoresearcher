# What would it take: closure-based point-decomposition index calculus vs rho on ECC2K-130

Zero-experiment derivation (scripted arithmetic, standard library only, ~9 s). It
answers one question: under which (arity m, refuting degree D, elimination
exponent omega, presentation) cells does a bounded-degree closure relation
search beat Pollard rho on ECC2K-130 (n = 131, matched rho 2^60.809
iterations)? Every constant carries a file:line or paper citation in
`wwit_tables.md`; assumed extrapolations are marked ASSUMED with their
sensitivity shown.

## Reproduction asserts (all pass)
- KN-FIND-aa2efc floors 89.25 / 68.58 / 56.40 / 48.44 / 42.85 / 35.61 (<= 0.005 bit).
- EXP-BINSTD-a222b4 pinned-D3 budgets 11.01 / 33.08 / 37.39 / 42.52 / 49.86 (<= 0.005 bit).
- H-BINSTD-555991 large-prime budgets 8.71 / 22.34; the plain m=3 budget -15.55.
- EXP-ICPERF-783e9e monomial counts 29.02 / 52.78 / 79.71 / 103.13.
- The m=3 pilot's W_4 column counts, exactly (columns = C(N, <= 4)).
- vOW 6nW at n=163 (91.26) and Semaev's Table-3 crossing (302).

## Headline
- **Time only, with the full variable count (direct or chained presentation): no
  cell beats rho at any refuting degree D >= 4**, for m in 3..16, D in 3..6,
  omega in {2, 2.37, 3}, dense or sparse. The only sub-rho rows have D = 3, which
  refutes nothing (pilot: W_3 refuted 0/140 UNSAT instances).
- **The only time-only winners** need all of: Semaev's per-block cost heuristic
  (charging one 2n+l-variable block times (m-2)), omega = 2.0 (within ~0.1-0.2),
  and m >= 10: +2.2 (m=10), +3.9 (m=12), +5.9 (m=16) bits. At omega = 2.37 the
  best such cell is -4.4 bits; at omega = 3, -22. Remove any one conjunct and
  nothing beats rho.
- **Time x memory: no refuting cell beats 6nW = 2^70.43** (derived: the program
  records no n=131 vOW row). The best refuting cell is 26-40 bits above it; the
  D=4 closure matrix alone is 2^55-2^80 bits per attempt.
- **The direct S_{m+1} presentation is dead at every omega >= 1**: at m=4 it has
  2^52.8 monomials against a 2^27.1 bit-op budget.

## D_max(m): the degree the m=4/5 pilot would have to beat
"3 (nonref)" means only the non-refuting degree fits the budget.

| m | budget c*(m), rho steps / bit-ops | N (chained) | D_max at omega 2 / 2.37 / 3 | omega to tie at D=4 | D_max, block heuristic, omega 2 |
|---|---|---|---|---|---|
| 3 | -15.55 / 0.5 | 218 | none | 0.02 | none |
| 4 | 11.01 / 27.1 | 378 | none | 0.91 | none |
| 5 | 33.08 / 49.2 | 531 | 3 (nonref) / none / none | 1.56 | 3 (nonref) |
| 6 | 37.39 / 53.5 | 664 | 3 (nonref) / none / none | 1.63 | 3 (nonref) |
| 8 | 42.52 / 58.6 | 932 | 3 (nonref) / none / none | 1.68 | 4 |
| 10 | 45.53 / 61.6 | 1201 | 3 (nonref) / none / none | 1.70 | 4 |
| 12 | 47.49 / 63.6 | 1470 | 3 (nonref) / none / none | 1.70 | 4 |
| 16 | 49.86 / 66.0 | 2009 | 3 (nonref) / none / none | 1.68 | 4 |

At m=4 the degree-4 Macaulay matrix (2^29.7 columns) cannot even be read inside
the 2^27.1 bit-op budget. At m=5 the D=4, omega=2 gap is 14 bits.

## Sensitivities
1. omega: 0.1 of omega is 2.8-3.9 bits at D=4.
2. D: D=4 -> 5 costs 11.5 (block) to 15.8 (chained) bits at omega=2.
3. Presentation: block (2n+l variables) vs chained (ml+(m-2)n) is 14-24 bits at
   omega=2 and is the entire difference between four winners and none.

## Asymptotic reading
If D=4 stays bounded for all m, the family is Semaev's 2^(1.6986 sqrt(n ln n));
at n=131 the exponential part is only 2^42.9, so the finite-n verdict is set by
the polynomial cofactor cols^omega. Time-only crossings against 2^(n/2): Semaev's
own formula reproduces 302; fair finite-n readings give 231 / 177 / 147 at
omega 3 / 2.37 / 2 (185 / 131 / 100 with the 2^16.1 bit-op credit). Time x
memory against 6nW: 518 (dense) and 460 (sparse), reproducing the program's
520 / 460 (EV-SEMBIN-4125ec); no variant goes below 244. ECC2K-130 sits below
every time x memory crossing and below every time-only crossing except the
block-heuristic, omega=2, credited one.

## One-line answer
Beating rho on ECC2K-130 with a closure oracle requires, simultaneously, (i) a
refutation at D=4, (ii) an elimination at omega = 2.0, (iii) cost scaling with
one 2n-variable block rather than the chain, (iv) m >= 10, and (v) the time x
memory metric waived. The m=4/5 pilot cannot satisfy (i)+(ii) inside its
budget under any presentation. This is a derivation, not a measurement; its
regenerable script is `wwit_model.py`.
