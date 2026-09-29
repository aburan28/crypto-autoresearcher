# EXP-PFDR-4bfc6f -- Stage 0 (zero compute, hard gate)

Task: TASK-20260903-3a77d3 (retry of TASK-20260903-06b269, `failed_infrastructure`
at pre-flight; Sage confirmed present on this host, see `implementation.md`).
Hypothesis H-PFDR-e02f3b, contract `experiments/EXP-PFDR-4bfc6f/specification.yaml`
(`status: approved`, `approved_by: coordinator`). This file is zero-compute: hand
derivation, one Hilbert-series numeric check performed with plain-Python exact
rational arithmetic (`fractions.Fraction`, not Sage; no Groebner call), and one
symbolic induction check performed with `sympy` (again no Groebner call, no
Sage). Nothing here reads a new Sage cell.

## 1. Induction of claim (B): the membership top forms

Setup (verbatim from H-PFDR-e02f3b statement (B)): in the e-ring, the
factor-base membership constraint is `F(t) = prod_{v in FB}(t - v)`, degree
`k = |FB|`, reduced modulo the minimal polynomial `M(t) = t^3 - e_1 t^2 + e_2 t
- e_3` of the three e-ring generators. Write `t^j = A_j t^2 + B_j t + C_j (mod
M)`. From `t*M(t) = t^4 - e_1 t^3 + e_2 t^2 - e_3 t`, i.e. `t^3 = e_1 t^2 - e_2
t + e_3`, the reduction recurrence for `t^{j+1} = t * t^j (mod M)` is:

```
A_{j+1} = e_1 A_j + B_j
B_{j+1} = -e_2 A_j + C_j
C_{j+1} = e_3 A_j
```

with base case `(A_3, B_3, C_3) = (e_1, -e_2, e_3)` (immediate from `t^3 = e_1
t^2 - e_2 t + e_3`).

**Claim:** under the standard grading `deg e_i = 1` (i.e. `top_form` = the
degree-`d` homogeneous part where `d` is total degree treating each `e_i` as
weight 1 -- this is exactly what the archived `top_form(f, R)` computes, since
`R = PolynomialRing(Fp, ['e1','e2','e3'])` has no weighted term order), for
`j >= 3`:

```
top(A_j, B_j, C_j) = e_1^{j-3} * (e_1, -e_2, e_3),   deg = j - 2
```

**Verification (computational, zero Sage, `sympy` polynomial arithmetic over
`QQ`, exact):** ran the recurrence from `j = 3` to `j = 10` starting at
`(e_1, -e_2, e_3)`, took the total-degree-`d` homogeneous part of each of
`A_j, B_j, C_j` by `sympy.Poly(...).terms()` filtered on `sum(monom) == d`,
and compared against the closed form termwise. **Result: exact match at every
`j` in `{3,...,10}`, and `deg = j - 2` at every `j`** (script run inline, not
committed as a run directory since it is zero-compute derivation support, not
a planned experimental run; reproduced below verbatim):

```
j= 3 pred_ok= True deg= 1 expect_deg= 1
j= 4 pred_ok= True deg= 2 expect_deg= 2
j= 5 pred_ok= True deg= 3 expect_deg= 3
j= 6 pred_ok= True deg= 4 expect_deg= 4
j= 7 pred_ok= True deg= 5 expect_deg= 5
j= 8 pred_ok= True deg= 6 expect_deg= 6
j= 9 pred_ok= True deg= 7 expect_deg= 7
j=10 pred_ok= True deg= 8 expect_deg= 8
```

This is not a full induction proof by itself (it checks 8 instances, not "for
all j"), but the recurrence structure makes the inductive step transparent by
hand: if `top(A_j,B_j,C_j) = e_1^{j-3}(e_1,-e_2,e_3)`, i.e. `A_j`'s top term is
`e_1^{j-2}`, `B_j`'s is `-e_1^{j-3}e_2`, `C_j`'s is `e_1^{j-3}e_3` (all degree
`j-2`), then `A_{j+1} = e_1 A_j + B_j` has top-degree part `e_1 * e_1^{j-2} =
e_1^{j-1}` (degree `j-1`) since `B_j` is only degree `j-2 < j-1`, so it does
not contribute to the new top form; similarly `B_{j+1} = -e_2 A_j + C_j` has
top part `-e_2 e_1^{j-2}` (degree `j-1`, `C_j` at degree `j-2` again too low);
`C_{j+1} = e_3 A_j` has top part `e_3 e_1^{j-2}` (degree `j-1`). That is
exactly `e_1^{(j+1)-3}(e_1,-e_2,e_3)`. The instance check above confirms the
closed form and the "only the previous `A`'s top term survives" mechanism
agree for 8 consecutive steps; the by-hand argument in this paragraph is the
inductive step and closes the induction for all `j >= 3`.

## 2. The three syzygies

The three membership generators at `k = |FB|` are `A_k, B_k, C_k` (the
reduction of `F(t) = prod(t-v)` mod `M`, decomposed as `A_k t^2 + B_k t +
C_k`, i.e. the e-ring membership constraints are the three coefficients set to
their known values, so the *generators fed to the meter* are `A_k - a_k`,
`B_k - b_k`, `C_k - c_k` for the target's known coefficients `(a_k,b_k,c_k)`,
whose **top forms** are `top(A_k), top(B_k), top(C_k)` = `top(A_k,B_k,C_k)`
componentwise since subtracting the (lower-degree, `k` constant) target
values does not change the top form for `k >= 4`). By part 1, at `deg = k-2`:

```
top(A_k) = e_1^{k-3} e_1 = e_1^{k-2}          =: h_A
top(B_k) = -e_1^{k-3} e_2                     =: h_B
top(C_k) = e_1^{k-3} e_3                      =: h_C
```

All three are divisible by `e_1^{k-3}` and proportional (as vectors of
coefficients) to `(e_1, -e_2, e_3)`. This immediately gives three linear
syzygies among `(h_A, h_B, h_C)` at degree `(k-2) + 1 = k-1`:

```
S1:  e_2 * h_A + e_1 * h_B = e_2 e_1^{k-2} + e_1*(-e_1^{k-3}e_2) = e_2 e_1^{k-2} - e_2 e_1^{k-2} = 0
S2:  e_3 * h_A - e_1 * h_C = e_3 e_1^{k-2} - e_1*(e_1^{k-3}e_3)   = e_3 e_1^{k-2} - e_3 e_1^{k-2} = 0
S3:  e_3 * h_B + e_2 * h_C = e_3*(-e_1^{k-3}e_2) + e_2*(e_1^{k-3}e_3) = 0
```

Each is a degree-`(k-1)` element of the syzygy module on `(h_A,h_B,h_C)` with
coefficients `(e_2,e_1,0)`, `(e_3,0,-e_1)`, `(0,e_3,e_2)` respectively --
**none of the three coefficient vectors is a scalar multiple of the trivial
Koszul pair `(h_B,-h_A,0)` etc.** (Koszul syzygies among three degree-`(k-2)`
forms sit at degree `2(k-2)`, which for `k >= 4` is `>= k` and strictly above
`k-1` since `2(k-2) - (k-1) = k-3 >= 1`), so `S1,S2,S3` are non-Koszul at
degree `k-1`, independent (the three coefficient vectors `(e_2,e_1,0)`,
`(e_3,0,-e_1)`, `(0,e_3,e_2)` are linearly independent over the field for
generic `e_1,e_2,e_3`, e.g. their 3x3 coefficient-of-`e_1,e_2,e_3` matrix
`[[0,1,0],[0,0,-1],[0,0,0]]`-style check by direct row reduction: `S1` has an
`e_1*h_B` term absent from `S2,S3`; `S2` has an `e_1*h_C`-only difference from
`S3`... concretely the three syzygy vectors as elements of `R^3` are
`(e2,e1,0)`, `(e3,0,-e1)`, `(0,e3,e2)`, whose 3x3 matrix has determinant
`e2*(0*e2 - (-e1)*e3) - e1*(e3*e2 - (-e1)*0) + 0 = e2*e1*e3 - e1*e3*e2 = 0`
identically -- **so as *constant* combinations they are dependent (rank <=2
pointwise for fixed e1,e2,e3 as a 3x3 matrix), but as elements of the graded
module (with polynomial, not constant, coefficients) they remain three
distinct minimal generators of the syzygy module at degree k-1 in the sense
the archived meter measures: kernel dimension of the Macaulay map at
`D = k-1` minus the trivial-Koszul count. This document does NOT independently
reprove that the *module* kernel dimension is exactly 3 (as opposed to a
smaller number after allowing the linear dependence just found) -- that
numeric fact is measured, not derived, by the meter in Stage 1, and the
determinant-zero relation above is flagged here as an open point for the
Stage 1 measurement to confirm or correct, not silently assumed.**

**THEREFORE (the part that IS proved by hand):** `d_ff <= k - 1` (a
non-Koszul syzygy exists at `k-1`, exhibited explicitly above, so the kernel
is nontrivial there), for every `k >= 4`, every prime `p`, every curve, every
target, using only the membership generators -- no row of the S4 (Semaev)
polynomial is used in `S1,S2,S3`. Whether `d_ff` is *exactly* `k-1` (not
lower) and the *exact* kernel dimension at `k-1` is `3` are measured facts
(Stage 1/2), consistent with but not re-derived here beyond the archived
measurement already on file (see section 4).

## 3. D_reg table by hand

`D_reg` for a homogeneous system of degrees `degs = (d_1,...,d_m)` in `n`
variables is defined by the archived meter (`semireg_Dreg`, both
EXP-ALPF-009 and EXP-ALPF-010 copies, byte-identical logic) as the smallest
`D` with a non-positive coefficient in the Hilbert series
`prod_i(1 - t^{d_i}) / (1-t)^n`. For the e-ring degree profile at `|FB| = k`,
`degs = (k-2, k-2, k-2, 4)` (three membership generators of degree `k-2`, the
S4 top form fixed at degree 4 -- matches the archived "leading-form degs"
column, e.g. `[2,2,2,4]` at `k=4`), `n = 3`.

Computed with exact rational arithmetic (`fractions.Fraction`, plain Python,
no Sage, no Groebner basis -- pure formal power-series division by repeated
partial-sum recurrence for `1/(1-t)^n`):

| k=\|FB\| | degs | D_reg (Hilbert-series first non-positive coeff.) |
|---|---|---|
| 4 | (2,2,2,4) | **4** |
| 5 | (3,3,3,4) | **5** |
| 6 | (4,4,4,4) | **7** |
| 7 | (5,5,5,4) | **8** |
| 8 | (6,6,6,4) | **10** |

This matches the frozen prediction `D_reg = 4, 5, 7, 8, 10` at `k = 4..8`
(`stage0-predictions.yaml`, itself copied from `H-PFDR-e02f3b.predictions`
and `.test_boundary.budget` verbatim, per contract) and matches the two
archived e-ring cells directly measured by EXP-ALPF-011 (`D_reg=4` at `k=4`,
`D_reg=5` at `k=5`; section 6 of `round006_exp010_validated_resweep_result.md`).

Combined with part 2 (`d_ff <= k-1`, i.e. `d_ff <= D_reg - 1` at every row of
this table since `D_reg - (k-1)` is `1,1,2,2,3` at `k=4..8` -- all `>=1`),
the by-hand derivation predicts the archived meter should report `fires=True`
(`d_ff < D_reg`) at every `k` in `{4,...,8}` **on the membership block alone**,
independent of the S4/Semaev row. This is the M2 (membership-only) signature
named in `H-PFDR-e02f3b` part (C) and predicted by part (B).

## 4. Archive check of all 16 e-ring cells (zero compute -- reading archived numbers only)

`experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep_result.md`
section 6 lists, for representation (B) e-ring, 16 lines (4 curve-bit classes
x {structured, random} x `|FB| in {4,5}`, times 2 for the duplicated
13b/15b/17b/19b x structured/random enumeration -- the file's own listing has
16 e-ring lines, matched against the by-hand table above):

- `|FB|=4` e-ring lines (8 of them: structured x {13b,15b,17b,19b}, random x
  13b only listed once + repeats for the bit classes present in the file):
  leading-form degs `[2,2,2,4]`, **d_ff=3, D_reg=4** in every line -- matches
  `k-1 = 3` and the table's `D_reg=4` exactly.
- `|FB|=5` e-ring lines: leading-form degs `[3,3,3,4]`, **d_ff=4, D_reg=5** in
  every line -- matches `k-1 = 4` and the table's `D_reg=5` exactly.

Section 8 (the archive's own red-team correction, "Discriminator 2") gives
the *exact* leading forms for one measured cell (`p=4079, a=-3, k=4`):
`h1 = e1*e3`, `h2 = -e1*e2`, `h3 = e1^2`, all sharing the factor `e1` -- this
is **exactly** `(h_A, h_B, h_C) = (e_1^2, -e_1 e_2, e_1 e_3)` derived in part
1 at `k=4` (`e_1^{k-3} = e_1^1`), same three polynomials up to the labeling
order (`h3<->h_A, h2<->h_B, h1<->h_C`). **16/16 e-ring cells check by hand
against the by-hand table; 0 mismatches.** (The x-ring and power-sum 16+16
cells are not independently re-derived by hand here -- x-ring `D_reg` is
cited by the archive as matching EXP-009's `7/10/12` at `|FB|=3/4/5`
[archive section 4, "match: True" in all measured cells], and power-sum is
not covered by the closed-form induction of part 1, which is specific to the
e-ring's cubic-minimal-polynomial reduction; both remain to be checked by
running the meters in Stage 1, not by hand.)

## 5. EV-ALPF-001 versus the archive's own final section

`ledger/evidence/EV-ALPF-001.yaml` `observations` quotes, verbatim (line
matching `EXP-ALPF-011`):

> `EXP-ALPF-011: round006_exp010_validated_resweep — POSITIVE (SURVIVED) --
> at least one PRIME-FIELD m=3 representation genuinely early-falls (d_ff <
> D_reg) under the validated meter. This is the campaign's FIRST prime-field
> algebra-` [truncated]

This is the **Section 5 auto-verdict line** of the archived result file
(`round006_exp010_validated_resweep_result.md` line 139, section 5). The
*same file*, section 8 ("RED-TEAM CORRECTION"), which sits **after** section
5 in the same document EV-ALPF-001 cites, states:

> `### CORRECTED VERDICT: FAILED (BANKABLE NEGATIVE)` -- ... "No prime-field
> m=3 re-coordinatization exhibits a GENUINE, EXPLOITABLE early fall of the
> Semaev decomposition" ... "(B) e-ring: d_ff<D_reg is a COORDINATE-ARTIFACT
> shared-factor syzygy -- the three FB-membership leading forms all carry the
> factor e1 (POS-A mechanism), living entirely in the FB constraints, NOT in
> S4. Generic twin is regular. NOT a Semaev-difficulty drop."

**Written comparison:** EV-ALPF-001's quoted line reproduces the archive's
Section 5 headline verbatim (truncated mid-sentence at "algebra-", i.e. cut
off before "track POSITIVE" and before the file's own Section 8 override is
reached). The archive's own final substantive section overturns that exact
headline, for the exact mechanism (a shared-factor syzygy confined to the
FB-membership block, `e_1 | h_A, h_B, h_C`) that part 1-3 of this document
independently re-derives by hand from the recurrence, without reading Section
8 first (the derivation was written from the `H-PFDR-e02f3b` statement and
verified computationally in parts 1/3 before section 4/5 of this document
quoted the archive's own text). The two are consistent: the by-hand
mechanism (shared factor `e_1^{k-3}`) is the same mechanism the archive's
own red-team correction names, and both are **M2** (membership-only, per
`H-PFDR-e02f3b` part (C)) rather than **M1** (genuine, S4-involving).

The `EXP-ALPF-001` line quoted by EV-ALPF-001 (`d_ff(symmetric prime-field
Semaev) stays bounded (flat) across >=3 sizes for fixed m, strictly below
D_reg`) is not re-examined by hand in this section (it is the `m=2`
symmetric-arm, Q1/output-degree-proxy claim (A) of H-PFDR-e02f3b, addressed
by Stage 2's `CTRL-TARGET-ARM` / Q1 measurement, not by the e-ring induction
above).

## Gate result

Both zero-compute checks required before any rank are complete and pass:
the induction (part 1, computationally verified for `j=3..10`, by-hand
inductive step), the D_reg table (part 3, matches the frozen prediction and
the two archived e-ring `D_reg` values), and the archive check (part 4, 16/16
e-ring cells consistent with the by-hand `d_ff = k-1` rule; x-ring and
power-sum not independently re-derived by hand, only cited). **Stage 0 does
not by itself gate on x-ring/power-sum matching by hand** (the contract's
G1/CTRL-ARCHIVE-REPRODUCTION blocking check is a Stage 1 *measured*
reproduction on all 48 cells with both meters, not a hand check); Stage 0's
own hard gate (induction + D_reg table + 16 e-ring archive check + the
EV-ALPF-001-vs-archive comparison) is met. Proceeding to Stage 1.
