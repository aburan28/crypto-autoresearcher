# EXP-MONO-815525 -- implementation notes

Run: `runs/RUN-MONO-815525-1/`. Executor session, handoff `TASK-20260904-73d110`,
frozen contract `specification.yaml` (`status: approved`, `frozen: true`,
`execution_authorized: true`, `approved_by: coordinator`).

These are implementation and observation notes. They contain no judgement about
whether `H-MONO-5b6617` or `IDEA-20260904-ad63fe` is supported or refuted.

## 1. Which construction route was used, and why

The task card offered route (a) symbolic symmetrization and route (b) numeric
substitution of the roots of `g` into an ordered-base `S_4`, and recommended
(b). **Both were implemented, and a third route was added, and all three are
run against each other on every checked instance.** The symbolic derivation
turned out to be cheap (10.5 s total), so there was no reason to choose.

### Route 1 -- symbolic elimination (`implementation/derive_s4.py`, sympy)

`S_3` is derived from the group law exactly as in this session's already
verified `m=3` work, and re-derived here rather than copied:

* encode `x(P1+P2) = x3` with the denominator of `lambda` cleared:
  `(y2-y1)^2 = (x1+x2+x3)(x2-x1)^2`;
* `Res_{y1}` against `y1^2 - f(x1)`, then `Res_{y2}` against `y2^2 - f(x2)`.

The elimination result factors **exactly** as `(x1-x2)^4 * S_3^2` -- verified
symbolically (`s3_elimination_matches_squared_form: true`). The `(x1-x2)^4` is
the extraneous factor from clearing `lambda`'s denominator; the square is
because each `Res_{y_i}` sees both signs of `y_i`. The genuine `S_3` is

```
S_3 = A^2 - 2A(x1x2+x1x3+x2x3) - 4B(x1+x2+x3)
      + x1^2x2^2 - 2x1^2x2x3 + x1^2x3^2 - 2x1x2^2x3 - 2x1x2x3^2 + x2^2x3^2
```

symmetric, degree 2 in each variable.

`S_4` is then obtained by eliminating the **intermediate point**. `P1+P2+P3+P4=O`
holds iff there is a point `R` with `P1+P2 = -R` and `P3+P4 = R`, i.e. iff
`S_3(x1,x2,U)` and `S_3(x3,x4,U)` share the root `U = x(R)`. Eliminating `U` is
one Sylvester resultant of two `U`-quadratics:

```
S_4(x1,x2,x3,x4) = Res_U( S_3(x1,x2,U), S_3(x3,x4,U) )
```

This is the same "introduce the intermediate point, then clear it" step the task
card describes, done as a resultant rather than by hand. Verified symbolically:

* degree in `x1,x2,x3,x4` = `[4,4,4,4]` -- matches this program's established
  `deg_T S_4 = 2^{4-2} = 4`;
* **no extraneous factor**: the resultant is irreducible over `Q[A,B]`
  (unlike the `S_3` elimination, which carried `(x1-x2)^4` and a square);
* fully symmetric under all 24 permutations of `x1..x4`;
* 540 terms. Full expansion in `implementation/S4_expanded.txt`.

### Descent to the symmetric base

Each `x4`-coefficient of `S_4` is symmetric in `x1,x2,x3` and was symmetrized
exactly (zero remainder) into `e1,e2,e3`, giving
`Q_e(T) = sum_{k=0..4} c_k(e1,e2,e3,A,B) T^k`. The five `c_k` are in
`implementation/Qe_coeff_c{0..4}.txt`. The leading one is worth recording here
because it drives the one anomaly in the census:

```
c_4 = ( -A^2 + 2A e2 + 4B e1 + 4 e1 e3 - e2^2 )^2
```

### Route 2 -- numeric substitution in `F_{p^3}` (the task card's route (b))

`F_{p^3} = F_p[X]/(g)` is built directly from the base cubic itself
(`g` is irreducible in Stage 1 by selection), so `x1 = X`, `x2 = x1^p`,
`x3 = x1^{p^2}`, with no root-finding and no square roots. The 540-term
ordered-base `S_4` table is then evaluated at those three `F_{p^3}` elements
with `x4 = T` kept symbolic, giving five `F_{p^3}` coefficients.

### Route 3 -- runtime resultant, independent of the derived `S_4`

`Q_e(T) = Res_U( S_3(x1,x2,U), S_3(x3,T,U) )` computed at runtime as a 4x4
Sylvester determinant over `F_{p^3}[T]`, reading only the `S_3` table. This path
never touches the derived `S_4` at all, so it is a genuinely independent check
on the whole `S_4` derivation and its symmetric descent.

### No CAS at runtime

`run_census.py` imports only the standard library. sympy is used only offline by
`derive_s4.py` to emit the monomial tables. Polynomial factorization over `F_p`
is Yun squarefree decomposition + distinct-degree factorization via
`gcd(T^{p^i} - T, .)` with repeated-squaring modular exponentiation, as the
specification requires. Equal-degree splitting is not needed: a
distinct-degree-`d` block of degree `D` contributes `D/d` factors, which is all
the degree pattern needs.

## 2. Curves

Five ordinary curves at four primes in `[101,2000]` (specification minimum: two
curves at two primes). Ordinariness (`t mod p != 0`) and `j not in {0,1728}`
are computed and asserted at runtime, not assumed:

| id | p | A | B | j | #E | t |
|----|---|---|---|---|----|---|
| C1 | 101  | 2  | 3  | 74   | 96   | 6   |
| C2 | 1009 | 5  | 7  | 459  | 966  | 44  |
| C3 | 211  | 3  | 11 | 111  | 223  | -11 |
| C4 | 1999 | 7  | 13 | 1870 | 2064 | -64 |
| C5 | 101  | 37 | 29 | 45   | 96   | 6   |

C5 exists only so the exhaustive `p=101` sweep could be replicated on a second
curve.

## 3. Stage 0 -- construction verification (all checks PASS)

| check | result |
|---|---|
| `S_3` vanishes at `(x(P), x(Q), x(P±Q))` for every pair from 6 real points, all 5 curves | PASS |
| (a1) symbolic `deg_T S_4 = 4` | PASS |
| (a2) specialised degree law `deg_T Q_e = 4 - #(sign classes summing to O)`, 269 split-`g` probes | PASS, 0 mismatches |
| (b) monic `Q_e` equals `prod (T - x(±P1±P2±P3))` over the finite sign classes, 269 split-`g` probes, 5 curves | PASS |
| (c) `Q_e` invariant under all 6 orderings of the root triple, and lands in `F_p[T]` | PASS |
| all three construction routes agree coefficient-by-coefficient | PASS |

Split-`g` probes are built the honest way round: take three real points on `E`
with distinct `x`, set `e_i` to their elementary symmetric functions, so `g`
splits by construction; then compute the four sign-class sums
(`eps_1 = +1` fixed) by ordinary point addition, exactly as
`EXP-MONO-917e3a/implementation/witness_search.py` does.

### Disclosed operationalisation of check (a)

The specification says only "it must be degree 4 in `T`". That is unambiguous
for the polynomial `S_4` and **not** unambiguous for its specialisation `Q_e` at
a particular `(e1,e2,e3)`, because `c_4` above is a nonzero polynomial that can
vanish at a point. Check (a) was therefore split into (a1) and (a2) above.
`deg_T Q_e < 4` happens exactly when `c_4(e) = 0`; on all 269 split-`g` probes
the degree drop equalled, exactly, the number of sign classes whose sum is the
point at infinity -- 0 mismatches, with 4 of the 269 probes actually exhibiting
a drop. So a degree drop is a root of the homogenised quartic at `T = infinity`,
not a defect.

**Timeline, for audit**: this split was made and the code corrected during a
smoke test whose Stage 0 aborted before Stage 1 ever executed. No Stage-1
factorization pattern had been observed at that point. Nothing about the
g-irreducibility selection rule was changed at any time.

## 4. Stage 1 -- census design

Base-point selection is `g(X) = X^3 - e1 X^2 + e2 X - e3` irreducible over
`F_p`, tested by `gcd(T^p - T, g) = 1`. This is a selection on the **base
point**, never on the curve, and every rejection is counted.

* **Sampled arm**: seeded `random.Random(20260904002)`, 300 qualifying base
  points per curve on all five curves = 1500 instances. Rejection counts are in
  `raw-result.json` under `stage_1.sampling` (e.g. C1: 300 kept from 840 draws,
  540 rejected).
* **Exhaustive arm**: all `101^3 = 1,030,301` triples `(e1,e2,e3)` in
  lexicographic order, for C1 and C5. Both **completed** -- the 200 s cap was
  not reached (45.9 s and 45.8 s). Each found exactly
  `343400 = (101^3 - 101)/3` irreducible `g`, which is the correct count.

For every sampled instance the ordered-base `F_{p^3}` route and the symmetric
route were both computed and compared, and `F_p`-rationality of the `F_{p^3}`
result was checked: `lands_in_Fp` and `ordered_and_symmetric_paths_agree` are
`true` for all 1500. The exhaustive arm uses the symmetric route only, for
speed; its agreement with the other two routes rests on the 1500 sampled
instances plus the 50 Stage-0 three-way probes.

Nothing was discarded, re-drawn, or summarised away. Every sampled instance is
in `raw-result.json` (`stage_1.instances`), and every literal deviation in the
exhaustive arm is stored individually
(`stage_1.exhaustive_sweep[*].deviations_all`, 3378 records per curve, untruncated).

## 5. Two reported readings of M1, and why both

`M1` is pre-registered as "does `Q_e(T)` factor as exactly (linear)(irreducible
cubic)?". For 0.98% of g-irreducible base points, `c_4(e) = 0`, `Q_e` has degree
3, and factors as a single irreducible cubic with no linear factor. Under the
literal affine reading that is a deviation. Under the projective reading -- the
missing root sits at `T = infinity`, which is an `F_p`-rational point of the
fibre, so the fibre is 1 rational point + 3 conjugates -- it is not.

Both are reported, separately and unmixed, everywhere:
`matches_prediction_1_3_literal` / `pattern` and `matches_1_3_projective` /
`projective_pattern`. Which reading the pre-registered prediction intended is a
Reviewer and Coordinator judgement. The Executor does not adjudicate it and does
not claim the prediction is met or missed.

## 6. Budget

Wall 103.3 s of 600 s; CPU 92.5 s (census) + 10.2 s (derivation) of 600 s; peak
RSS 31,260,672 B of 134,217,728 B; `raw-result.json` 4,713,330 B of 10,485,760 B;
one worker; no network. No stopping rule or invalidation rule was triggered.

## 7. Reproduction

```sh
cd experiments/EXP-MONO-815525
python3 implementation/derive_s4.py            # requires sympy; ~10 s
python3 implementation/run_census.py OUT.json  # stdlib only; ~93 s
```

Fully deterministic given the single seed 20260904002 and the fixed curve list
and search order, both hard-coded at the top of `run_census.py`.
