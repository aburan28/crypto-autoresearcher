# EXP-PFDR-fd901a -- Stage 0: the (2, 2, 3) matrix family at D = 4, the minor-degree bound, content primes

Zero-compute stage of the contract (specification `stages[0]`). Everything
below is a derivation about ONE integer matrix family; it claims nothing about
H-PFDR-09e1b0. The integer tables quoted in section 3 were produced by
`stage0_content_check()` in `run_experiment.py` and are stored verbatim in
`runs/RUN-PFDR-fd901a-fixture-p4099/raw-result.json` (`raw.stage0_content_check`),
so every number here is reproducible from a run record.

## 1. The system at (m, d, s) = (2, 2, 3)

Digit variables a_0, a_1, a_2 (unknown 1) and a_3, a_4, a_5 (unknown 2), with
ell_1 = a_0 + 2 a_1 + 4 a_2 and ell_2 = a_3 + 2 a_4 + 4 a_5 (window [0, 8)).
The membership generators a_i (a_i - 1) are absorbed into the ring quotient
B = Z[a]/(a_i^2 - a_i), whose Hilbert series is (1 + z)^6; the reduced Macaulay
column space at D <= 6 is therefore the 2^6 = 64 squarefree monomials, and the
only explicit generator is

    S~(A, B, x_R) = S_3(ell_1, ell_2, x_R) reduced in B,

with S_3(x_1, x_2, x_3) = (x_1 - x_2)^2 x_3^2 - 2((x_1 + x_2)(x_1 x_2 + A) + 2B) x_3
+ (x_1 x_2 - A)^2 - 4B(x_1 + x_2) (`harness/semaev.py::s3_expr`). The null
series of the contract is (1 + z)^6 (1 - z^4): coefficients 1, 6, 15, 20, 14,
0, -14, so the semi-regular null has d_reg = 5 (first non-positive coefficient,
84cdb7 / DREG convention) and D_null = floor((6 + 4)/2) + 1 = 6 (H-PFDR-4148b8
convention). Both are recorded in every manifest's `parameters`.

## 2. The matrix family M_D(A, B, x_R) over Z[A, B, x_R]

Per-layer convention (macaulay.py): the rows of M_D are m * S~ for the
squarefree multipliers m of degree D - 4, so

| D | rows r(D) | columns (deg <= D) | top columns (deg = D) |
|---|---|---|---|
| 3 | 0 | 42 | 20 |
| 4 | 1 | 57 | 15 |
| 5 | 6 | 63 | 6 |
| 6 | 15 | 64 | 1 |

At D = 4 the matrix is the single row S~ itself. Its 49 nonzero entries (out of
57 columns; the 8 missing columns are the monomials with three variables from
one block or four with an odd split, which cannot occur in a product of two
degree-2 block forms) are polynomials in (A, B, x_R) of total degree <= 2:

| column | entry over Z[A, B, x_R] | degree in (A, B, x_R) | integer content |
|---|---|---|---|
| 1 | A^2 - 4 B x_R | 2 | 1 |
| a_0 | x_R^2 - 2 A x_R - 4 B | 2 | 1 |
| a_3 | x_R^2 - 2 A x_R - 4 B | 2 | 1 |
| a_1, a_4 | 4 (x_R^2 - 2 A x_R - 4 B) / 4 ... i.e. -4 A x_R - 8 B + 4 x_R^2 | 2 | 4 |
| a_2, a_5 | -8 A x_R - 16 B + 16 x_R^2 | 2 | 8 |
| a_0 a_1, a_3 a_4 | 4 x_R^2 | 2 | 4 |
| a_0 a_2, a_3 a_5 | 8 x_R^2 | 2 | 8 |
| a_1 a_2, a_4 a_5 | 16 x_R^2 | 2 | 16 |
| a_0 a_3 | -2 A - 2 x_R^2 - 4 x_R + 1 | 2 | 1 |
| a_0 a_4, a_1 a_3 | -4 A - 4 x_R^2 - 12 x_R + 4 | 2 | 4 |
| a_0 a_5, a_2 a_3 | -8 A - 8 x_R^2 - 40 x_R + 16 | 2 | 8 |
| a_1 a_4 | -8 A - 8 x_R^2 - 32 x_R + 16 | 2 | 8 |
| a_1 a_5, a_2 a_4 | -16 A - 16 x_R^2 - 96 x_R + 64 | 2 | 16 |
| a_2 a_5 | -32 A - 32 x_R^2 - 256 x_R + 256 | 2 | 32 |
| a_0 a_1 a_3, a_0 a_3 a_4 | 4 - 8 x_R | 1 | 4 |
| a_0 a_1 a_4, a_1 a_3 a_4 | 16 - 16 x_R | 1 | 16 |
| a_0 a_1 a_5, a_2 a_3 a_4 | 64 - 32 x_R | 1 | 32 |
| a_0 a_2 a_3, a_0 a_3 a_5 | 8 - 16 x_R | 1 | 8 |
| a_0 a_2 a_4, a_1 a_3 a_5 | 32 - 32 x_R | 1 | 32 |
| a_0 a_2 a_5, a_2 a_3 a_5 | 128 - 64 x_R | 1 | 64 |
| a_0 a_4 a_5, a_1 a_2 a_3 | 16 - 32 x_R | 1 | 16 |
| a_1 a_2 a_4, a_1 a_4 a_5 | 64 - 64 x_R | 1 | 64 |
| a_1 a_2 a_5, a_2 a_4 a_5 | 256 - 128 x_R | 1 | 128 |
| a_0 a_1 a_3 a_4 | 16 | 0 | 16 |
| a_0 a_1 a_3 a_5, a_0 a_2 a_3 a_4 | 32 | 0 | 32 |
| a_0 a_1 a_4 a_5, a_0 a_2 a_3 a_5, a_1 a_2 a_3 a_4 | 64 | 0 | 64 |
| a_0 a_2 a_4 a_5, a_1 a_2 a_3 a_5 | 128 | 0 | 128 |
| a_1 a_2 a_4 a_5 | 256 | 0 | 256 |

(The row `a_1, a_4` reads: entry -4 A x_R - 8 B + 4 x_R^2.) The exact table,
with every entry as a string, is `raw.stage0_content_check.entry_table` in the
fixture run. The degree-4 part is 16 (a_0 + 2a_1 + 4a_2)^{[2]} (a_3 + 2a_4 + 4a_5)^{[2]}
where q^{[2]} denotes the squarefree square (a_i^2 -> a_i), i.e. the monomial
top form x_1^2 x_2^2 of S_3 pushed through the digit map; it is CONSTANT in
(A, B, x_R), so the top-degree block of every M_D is parameter-free.

The rows of M_5 and M_6 are m * S~ with m a digit variable (D = 5) or a product
of two (D = 6); multiplication by m only merges columns (bitwise OR), so every
entry of M_D is a Z-linear combination of entries of S~ and has degree <= 2 in
(A, B, x_R). Column and row counts do not depend on p; M_D over F_p is the
specialisation of this one family at (A, B, x_R) in F_p^3 (IDEA-20260903-26aa81
claim A).

## 3. Minor-degree bound and the Schwartz-Zippel constant

Let r_D be the generic rank of M_D over Q(A, B, x_R) and pick ONE nonzero
r_D x r_D minor P_D^*. Its degree in (A, B, x_R) is at most 2 r_D (entries have
degree <= 2), and a rank drop at a specialisation requires P_D^* to vanish
there, so for uniform (A, B, x_R) in F_p^3 and p not dividing the content of
P_D^*,

    Prob[rank(M_D mod p) < r_D]  <=  deg(P_D^*) / p  <=  2 r_D / p  <=  2 r(D) / p.

With the row counts of section 2 this is the frozen c_D (bounded, not computed):

| D | r(D) | 2 r(D) | bound at p = 4099 |
|---|---|---|---|
| 4 | 1 | 2 | 0.00049 |
| 5 | 6 | 12 | 0.0029 |
| 6 | 15 | 30 | 0.0073 |

Summed over D = 4, 5, 6 the union bound is 44 / 4099 = 0.0107 per draw, below
the contract's 0.1 threshold. The bound is for UNIFORM (A, B, x_R); the planted
design samples a subvariety (x_R = x(P_1 + P_2)), which is exactly HEUR-001's
heuristic content and is what Stage 3 measures rather than assumes. The
measured generic profile (section 4) has r_4 = 1, r_5 = 6, r_6 = 15, i.e. the
family is generically of full row rank at every D, so P_D^* is a maximal minor
of a full-row-rank matrix and the bound above is the sharpest this argument
gives.

## 4. Content primes

Integer content of the D = 4 row (gcd of all integer coefficients of all 49
entries): **1** (`raw.stage0_content_check.content_D4`), because the entries at
columns 1, a_0, a_3, a_0 a_3 have content 1. So no prime divides the whole row.
However, every entry of degree >= 3 in the digit variables has content divisible
by 4 (the smallest is 4 at a_0 a_1 a_3 and a_0 a_3 a_4), and every degree-4
entry has content divisible by 16. Hence at p = 2 the whole top form and the
whole degree-3 part vanish and the generator degenerates to a quadric: p = 2 is
a content prime for the TOP-DEGREE block (the object whose rank profile the
sweep reads), even though the row content is 1. The powers of 2 come from the
digit weights 2^i and are the only structural content; no odd prime divides any
entry's content in the table.

Empirical specialisation check (uniform (A, B, x_R), naive-elimination ranks of
the dense family, 24 samples per prime, reference = the profile at 2^64 - 59 on
8 uniform samples, (full_rank, top_rank) at D = 4, 5, 6):

| q | samples | equal to reference ((1,1),(6,2),(15,1)) | observed profiles |
|---|---|---|---|
| 2 | 24 | 0 | four distinct profiles, all with the generator of degree 2 (top form gone) |
| 3 | 24 | 23 | one sample ((1,1),(6,2),(13,1)): full rank at D = 6 dropped by 2 |
| 5 | 24 | 24 | reference only |
| 7 | 24 | 24 | reference only |
| 11 | 24 | 24 | reference only |
| 13 | 24 | 24 | reference only |
| 17 | 24 | 24 | reference only |
| 19 | 24 | 24 | reference only |
| 23 | 24 | 24 | reference only |

Read as: p = 2 is a content prime of the top block (every sample drops); p = 3
shows one rank-drop event in 24 uniform samples, consistent with the 2 r_6 / 3
bound being vacuous there; from p = 5 upward no drop was seen in 24 uniform
samples. The window condition 2^s = 8 <= p of the digit presentation excludes
p < 8 from the battery anyway; the toy prime 4099 is far above every content
prime found here.

## 5. What Stage 0 does NOT say

It bounds the uniform rank-drop probability and identifies the content primes
of one matrix family; it does not compute the generic rank (Stage 1 and 3 do,
by measurement at three primes), does not address the planted subvariety, and
carries no statement about the s-axis, yield, cost or any attack.
