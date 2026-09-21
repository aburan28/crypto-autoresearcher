# EXP-PFDR-20ee58 -- Stage 0: the (S2)-(S3) derivation, written out and checked by hand

Zero compute. This is the hard gate of the contract: the two identities that
IDEA-20260903-cf63ad / H-PFDR-9aadc0 derive, written out step by step so an
independent reader can check each line. A mechanical confirmation of the same
statements (in the digit ring at s = 3, p in {4099, 65537}) is recorded in the
calibration run's `raw.result.stage0_mechanical_checks`; it is a supplement,
not a substitute, for this note.

## 0. Setting

`E: y^2 = x^3 + A x + B` over `F_p`, `p > 3`, `A B != 0` (generic j). The third
summation polynomial, exactly as `harness/semaev.py::s3_expr` writes it:

```
S_3(x_1, x_2, x_3) = (x_1 - x_2)^2 x_3^2
                     - 2 ((x_1 + x_2)(x_1 x_2 + A) + 2B) x_3
                     + (x_1 x_2 - A)^2 - 4B (x_1 + x_2).
```

The twin: `E1 = S_3(x_1, x_2, u)`, `E2 = S_3(u, x_3, x_R)`, `u` a free
variable, `x_R` a constant, and each leaf `x_k = sum_{i<s} 2^i a_{k,i}` with
`a_{k,i}(a_{k,i} - 1) = 0`. All computation is in the multilinear quotient
`F_p[a]/(a^2 - a)[u]`, graded by total degree (digit count plus u-exponent).

## 1. (S1) Degrees: E1 and E2 have total degree 4

Group `S_3` by degree in `(x_1, x_2, x_3)`:

| part | monomials | degree |
|---|---|---|
| `(x_1 - x_2)^2 x_3^2` | `x_1^2 x_3^2, x_1 x_2 x_3^2, x_2^2 x_3^2` | 4 |
| `-2 (x_1 + x_2) x_1 x_2 x_3` | `x_1^2 x_2 x_3, x_1 x_2^2 x_3` | 4 |
| `x_1^2 x_2^2` | | 4 |
| `-2A (x_1 + x_2) x_3 - 4B x_3 - 2A x_1 x_2 - 4B (x_1 + x_2)` | | <= 3 |
| `A^2` | | 0 |

So `S_3` has total degree 4 in its three arguments. Under the digit
substitution `x_k -> sum_i 2^i a_{k,i}` a square becomes
`x_k^2 = sum_i 4^i a_{k,i} + 2 sum_{i<j} 2^{i+j} a_{k,i} a_{k,j}` in the
quotient (the diagonal `a^2` collapses to `a`), which has digit-degree 2
exactly when `s >= 2` (the cross term `2 * 2^{i+j} a_{k,i} a_{k,j}` is nonzero
because `2` and `2^{i+j}` are units for `p > 2`). A product of two such
squares has digit-degree 4. Hence `deg E1 = deg E2 = 4` for `s >= 2`. The
membership relations `a(a - 1) = 0` are the ring quotient and contribute no
generator (S2, second half). So the twin is exactly two quartics in `3s + 1`
variables, and the first cross-generator cell is `D = 4 + 4 = 8`.

## 2. (S3, ingredient ii) The degree-4 parts have disjoint supports

**E1's degree-4 part.** With `x_3 = u`:

```
top(E1) = (x_1 - x_2)^2 u^2 - 2 x_1 x_2 (x_1 + x_2) u + x_1^2 x_2^2 .
```

The last term `x_1^2 x_2^2` is free of `u`. In the digit ring it becomes

```
x_1^2 x_2^2 = ( sum_i 4^i a_{1,i} + 2 sum_{i<i'} 2^{i+i'} a_{1,i} a_{1,i'} )
            * ( sum_k 4^k a_{2,k} + 2 sum_{k<k'} 2^{k+k'} a_{2,k} a_{2,k'} ),
```

whose degree-4 monomials `a_{1,i} a_{1,i'} a_{2,k} a_{2,k'}` (`i < i'`,
`k < k'`) carry the coefficient `4 * 2^{i+i'+k+k'}`, a unit. So `top(E1)`
contains `u`-free monomials of digit-degree 4 (there are `C(s,2)^2` of them:
9 at `s = 3`, as the mechanical check records).

**E2's degree-4 part.** With `(x_1, x_2, x_3) = (u, x_3, x_R)` and `x_R` a
constant, every term carrying `x_R` has degree at most 3 in `(u, x_3)`
(`(u - x_3)^2 x_R^2` has degree 2; `-2((u + x_3)(u x_3 + A) + 2B) x_R` has
degree 3), and the `x_R`-free part is `(u x_3 - A)^2 - 4B(u + x_3)`, whose
degree-4 part is `u^2 x_3^2`. Hence

```
top(E2) = u^2 x_3^2 = u^2 ( sum_k 4^k a_{3,k} + 2 sum_{k<k'} 2^{k+k'} a_{3,k} a_{3,k'} )
```

restricted to total degree 4, i.e. `u^2 a_{3,k} a_{3,k'}` (`k < k'`): every
monomial of `top(E2)` has `u`-exponent exactly 2 and digits from block 3 only.

**Consequence.** `top(E1)` has a monomial with `u`-exponent 0 that `top(E2)`
does not contain, and `top(E2)` has monomials `top(E1)` does not contain (they
involve block-3 digits, which do not occur in E1). The two degree-4 forms are
therefore linearly independent, and for every `(c_1, c_2) != (0, 0)`

```
deg (c_1 E1 + c_2 E2) = 4 .
```

No subset-sum of the generators degenerates in degree. (Compare
DREG_DEFICIT_CLOSED_FORM.md: over GF(2) the D = 3 syzygy came from a
subset-sum of descended quadrics whose quadratic parts cancel; that route
does not exist here.)

## 3. (S2, S3 ingredient i) The Boolean idempotent identity fails

In a Boolean ring every `f` satisfies `f^2 = f`, so for an affine `P` the
relation `P (1 + P) = P + P^2 = 0` holds and gives the Frobenius syzygies
`f_i^2 = f_i` that KN-FIND-006's generic baseline counts (`n_q` of them at
`D = 4`). In `F_p[a]/(a^2 - a)` take `f = a_1 + a_2`:

```
f^2 = a_1^2 + 2 a_1 a_2 + a_2^2 = a_1 + a_2 + 2 a_1 a_2 = f + 2 a_1 a_2 .
```

Since `2` is a unit for `p > 2`, `f^2 - f = 2 a_1 a_2 != 0`. More generally
for affine `P = c_0 + sum_i c_i a_i` one has
`P^2 - P = (c_0^2 - c_0) + sum_i (2 c_0 c_i + c_i^2 - c_i) a_i + 2 sum_{i<j} c_i c_j a_i a_j`,
and the last sum is nonzero as soon as two coefficients `c_i, c_j` are
nonzero. So `P^2 = P` fails for every affine `P` with at least two variables:
the idempotent ingredient of the binary D = 3 mechanism has no `F_p` analogue,
and the Frobenius family `f_i^2 = f_i` contributes nothing to the twin's
generic baseline. (The meter encodes exactly this: `koszul.frobenius_count`
is zero for `p > 2` and in mixed mode, and the series factor is the naive
`(1 - z^d)`; see `harness/macaulay_fp/VALIDATION.md` section 4 item 3.)

## 4. Koszul-only baseline (S2, conclusion)

The Koszul relation `E2 * E1 - E1 * E2 = 0` is exact in every commutative
ring. With two generators of degree 4 it first appears at `D = 8`, with
multiplier `1` only, so under the cumulative-multiplier convention
`koszul(D) = 0` for `D < 8` and `koszul(8) = 1`. Hence the generic prediction
is `rank(Mac_D) = rows(D)` for `D < 8` and `rows(8) - 1` at `D = 8`, and the
contract's `deficit(D) = rows(D) - rank(Mac_D) - koszul(D)` is 0 under M1.

## 5. F1 check

F1 fires if Stage 0 finds a degenerate subset-sum (section 2 shows none) or
an idempotent affine `P` with at least two variables (section 3 shows none).
Neither is found: F1 does not fire. The mechanical check in the calibration run
(`stage0_mechanical_checks`) records, at `s = 3` and `p in {4099, 65537}`:
`deg E1 = deg E2 = 4`; `top(E1)` has `u`-free monomials (9 of digit shape
(2, 2)); every monomial of `top(E2)` has `u^2` and block-3 digits only; the top
forms share no monomial; and `f^2 - f = 2 a_0 a_1` for `f = a_0 + a_1`.
