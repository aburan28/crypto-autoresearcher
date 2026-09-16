# Quasi-subfield-polynomial index calculus at the ECC2K-130 field: a pre-compute audit

**Status: analysis note, not evidence.** Every number here is this program's
arithmetic, produced by `qsp_ecc2k130.py` from formulas read in two frozen
sources; nothing was run against a curve. It is a section-8 audit in the sense
of `docs/inventor-protocol.md` (exact baseline embedding and method ceiling at
one parameter) written for `RQ-QSP-f9bbdb`. Regenerate with

```sh
python3 analysis/qsp-ecc2k130/qsp_ecc2k130.py --json results.json --md table.md
```

Sources: `KN-LIT-0a321c` (Huang, Kosters, Petit, Yeo, Yun, J. Math. Cryptol.
2020; `inputs/HUANG-2020-JMC-QSP/`) and `KN-LIT-4fe9d2` (Euler, Petit, arXiv
1909.11326v2; `inputs/EULER-PETIT-2019-QSP/`). Target: ECC2K-130,
`y^2 + xy = x^3 + 1` over `F_{2^131}` (`KN-LIT-096`, `KN-LIT-661e97`); the
baselines are `sqrt(2^131) = 2^65.5` (generic) and the recorded
`2^60.9` iterations for rho with the Frobenius and negation classes.

## Conventions

- `p = q = 2`, `n = 131`, `kappa = 4.876` (the Rojas exponent of Lemma 3.1).
- A cell is `(n', d, m)`: factor-base parameter `n'` (`|V| ~ 2^{n'}`), `d = deg
  lambda`, `m` points per relation. `beta = n log2(d) / n'^2`.
- Cost is `log2` of arithmetic operations over `F_{2^131}` as Theorem 3.2
  counts them, **with the `m!`, `m^{5.188}` and `3^{kappa m^2}` factors kept**:
  at `n = 131` they are not constants a reader can drop (`3^{kappa m^2}` is
  `2^{70}` at `m = 3`). The `O~` cofactor is dropped.
- Attempts per relation search: `2^{n'} / min(1, 2^{n'm - n} / m!)`.
- "Resultant-model floor": attempts times `M(E) = 2^{m(m-1)} d^{m(m-1)}`, the
  degree of the univariate polynomial Rojas' method must root-find per attempt
  (Appendix A.1), or the linear-algebra term, whichever is larger. It is a lower
  bound **for the paper's own solver model**, not an achievable cost.
- "Frobenius orbits": if `L in F_2[X]` then `V` is Frobenius-stable and, on a
  Koblitz curve, the factor base splits into orbits of size 131 under an
  endomorphism, so relations needed and linear-algebra dimension both drop by
  131. This is the same constant-factor lever that gives rho its `sqrt(262)`
  (already inside the 60.9 figure).

## Field facts (computed)

| fact | value |
|---|---|
| `ord_131(2)` | 130, so `X^131 - 1 = (X + 1) Phi_131` with `Phi_131` irreducible over `F_2` (verified by Ben-Or gcds) |
| `2^131 - 1` | `263 * 10350794431055162386718619237468234569`, cofactor prime (sympy 1.14) |
| `n + 1 = 132` | `= 4 * 3 * 11`; `131 = -1 mod n'` for `n' in {2, 3, 4, 6, 11, 12, 22, 33, 44, 66}` |

## What the theorems already decide at n = 131

1. **`F_2`-coefficient linearized QSPs** (Prop. 2 of `KN-LIT-4fe9d2`): only
   `X^2 + X` (`n' = 1`, the subfield `F_2`) and Type 1bis `L_{Phi_131}`
   (`n' = 130`, `beta = 0.99994`). Nothing else exists.
2. **Any linearized QSP** (Theorem 1): `beta >= 3/4`, so under Prop. 8's
   asymptotics the exponent is `>= 0.93`, i.e. `>= 2^122`. Lemma 2 gives the
   exact reach: at `l = 1` (`deg lambda = 2`) `n' <= 11`, at `l = 2` `n' <= 16`,
   ... at `l = 11` `n' <= 41` -- every one with `beta > 1`.
3. **Multiplicative QSPs** (App. C.2): `r | 2^131 - 1` gives `|V| = 264`
   (`beta = 12.9` at `n' = 9`) or `|V| = p + 1` (`n' = 123`, `beta = 1.02`).
   None.
4. **Published families**: Types 1 and 2 need `n = 1 + q' + ... + q'^{k+1}` or
   `n = q^{d+1} - 1`; the multiplicative families need `n` even or `p` of
   Solinas shape. Only Type 1bis contains `n = 131`.
5. **What is not excluded**: a non-linearized `lambda` (a term of degree not a
   power of 2, so `d >= 3`). Lemma 4.1 at `n' in {33, 44, 66}` requires only
   `l >= 1/3, 1/2, 1/2` respectively, because `131 mod n' = n' - 1`.

## The cost surface

Cheapest cells, `d` at the smallest degree Lemma 4.1 admits (cost is monotone
in `d`), `m` from `ceil(131/n')` upward; `d = 2` rows are linearized-only and
excluded by item 2, so the "not excluded" rows use `d = 3`:

| selection | n' | d | m | orbits | beta | log2 attempts | log2 relation phase | log2 lin. alg. | log2 total (Thm 3.2) | log2 floor |
|---|---|---|---|---|---|---|---|---|---|---|
| min total, not excluded | 66 | 3 | 2 | 1 | 0.048 | 66.0 | 133.0 | 133.0 | **133.0** | 133.0 |
| min floor, not excluded | 33 | 3 | 4 | 1 | 0.191 | 36.6 | 294.3 | 68.0 | 294.3 | **68.0** |
| min total, Frobenius orbits | 66 | 3 | 2 | 131 | 0.048 | 59.0 | 126.0 | 118.9 | **126.0** | 118.9 |
| min floor, Frobenius orbits | 33 | 3 | 4 | 131 | 0.191 | 29.6 | 287.2 | 53.9 | 287.2 | **60.6** |

Reading: under the paper's own solver the line costs at least `2^126` on
ECC2K-130 even granting a QSP that is not known to exist, because at
`n = 131` either the linear algebra (`2^{2n'}`) or the resultant factor
(`3^{kappa m^2}` with `m >= 3`) is enormous. Under the most optimistic floor
the paper's model allows, and with the Koblitz orbit reduction, the single
cell `(n' = 33, d = 3, m = 4)` reaches `2^60.6`, a tie with rho's `2^60.9`. That
cell requires (a) a non-linearized `X^{2^33} + lambda(X)`, `lambda in F_2[X]`,
with about `2^33` roots in `F_{2^131}` -- no such polynomial is known and the
Section 4.2 heuristic of `KN-LIT-0a321c` predicts none -- and (b) a solver
that decomposes at `M(E) = 2^31` operations per attempt, which no solver is
known to do.

Prop. 8's asymptotic table (`m >> 1`) evaluated at `n = 131` for reference:
`beta = 1: 2^124`, `0.75: 2^122`, `0.2: 2^97`, `0.1025: 2^65.5`, `0.0958: 2^60.9`.
Those exponents are never reached by any integer `m` at `n = 131`; see the
per-cell rows in `table.md`.

## What this note claims and does not claim

- Claims: the numbers above, under the stated conventions, for the algorithm
  of `KN-LIT-0a321c` Section 3.1 with the cost model of its Theorem 3.2 and
  the constraints of Lemma 4.1 and `KN-LIT-4fe9d2` Theorem 1.
- Does not claim: anything about other index-calculus lines on ECC2K-130
  (SEMBIN, ICPERF, FROB lanes), anything about `lambda` with coefficients
  outside `F_2` at `d >= 3`, or anything about the rational-`lambda` and
  isogeny-`L` generalisations the paper names as open.
- The sharpest remaining item is finite: the root count over `F_{2^131}` of
  each `X^{2^33} + lambda(X)`, `lambda in F_2[X]`, `3 <= deg lambda <= 7`,
  non-linearized (at most `2^8` candidates). A recorded discrepancy in
  `KN-LIT-4fe9d2` Section 4.4 (`kappa < 1.5` versus `kappa < 2/3`) does not
  affect any row above.
