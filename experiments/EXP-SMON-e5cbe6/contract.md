# EXP-SMON-e5cbe6 — falsification battery for the Semaev summation cover

- **Hypothesis:** `H-SMON-db677d`
- **Question:** `RQ-MONO-001` (the `m >= 4` half of `KN-OPEN-009`)
- **Scale tier:** `toy`. Largest prime exercised: 1009 (10 bits). Nothing here
  may be asserted at medium or crypto tier.
- **Authored and executed by:** the top-level session, 2026-08-07.

## Provenance and pre-registration — stated exactly

This contract was written in the same session as the code and the run. It is
**not** an independently pre-registered protocol and must not be read as one.
The honest ordering was:

1. The predictions C1–C5 were derived on paper, then implemented in
   `code/verify.py`, then run. The predicate `pattern_matches_prediction` was
   fixed in code before any specialization was sampled.
2. C8 (Frobenius class distribution) and C9 (discriminant square class) were
   added **after** seeing the C2–C5 results of a first pass, and before their own
   first execution. They were not tuned to data: each is an exact prediction with
   no free parameter.
3. The exhaustive per-class closed-form check in C6 was added last, again as an
   exact identity with no free parameter, and run once.

Because every prediction is an exact statement about a deterministic
computation, there is no analytic degree of freedom to exploit; but the record
says what happened rather than implying a pre-registration that did not occur.

**No independent validator or red-team review of this experiment was obtained.**
See `AGENTS.md` rule 12; this experiment does not meet it.

## Object under test

`E/F_p` a non-singular elliptic curve, `p > 3`, `f(x) = x^3 + Ax + B`.
`S_m` the m-th Semaev summation polynomial, built from the closed form for
`S_3` and the resultant recursion
`S_m(X_1..X_m) = Res_X(S_{m-1}(X_1..X_{m-2},X), S_3(X_{m-1},X_m,X))`
(the recursion of Semaev 2004, as stated in Kosters–Yeo, arXiv:1503.08001 §2).

For numeric `a_1..a_{m-1}` in `F_p`, `S_m(a_1,...,a_{m-1},T)` is recovered as a
coefficient list in `T` by evaluating the Sylvester determinant at `2^{m-2}+1`
values of `T` and interpolating. Formal degrees are held fixed in the Sylvester
matrix so that specialization commutes with the determinant; this is what makes
the interpolation valid at the `T` where a leading coefficient vanishes.

## Predictions (frozen; each can fail)

Write `n = m-1`, `P_i = (a_i, sqrt(f(a_i)))` over `F_{p^2}`,
`chi(x) = ` quadratic character of `f(x)`. Call a specialization **good** when
`S_m(a,T)` has degree exactly `2^{m-2}`, is squarefree, and the `2^{m-2}` signed
sums are finite and pairwise distinct.

- **C1.** `disc_T S_3(x1,x2,T) = 16 f(x1) f(x2)` as an identity in
  `Z[x1,x2,A,B]` — exact integer arithmetic, not a modular check.
- **C2.** At good specializations `deg_T S_m = 2^{m-2}` for `m = 3,4,5`.
- **C3.** At good specializations the root set of `S_m(a,T)` over `F_{p^2}` is
  exactly `{ x(eps_1 P_1 + ... + eps_n P_n) }`, `2^{m-2}` distinct values.
- **C4.** At good specializations the factorization of `S_m(a,T)` over `F_p` is
  `1^{2^{m-2}}` if `chi(f(a_1)) = ... = chi(f(a_n))`, and `2^{2^{m-3}}`
  otherwise. **No irreducible factor of degree >= 3 ever occurs, and no mixed
  factorization type ever occurs.**
- **C5.** If every `a_i` is the x-coordinate of an `F_p`-rational point (the
  factor-base locus) and the point is good, `S_m(a,T)` splits completely over
  `F_p`, at every `m`.
- **C6.** Exhaustively over `F_p^{n}`, for every Frobenius class `eps`,
  `S^k N^{n-k} + N^k S^{n-k} = #{good in class} + #{degenerate in class}`
  with residual exactly 0, where `S = #{x: chi=+1}`, `N = #{x: chi=-1}`.
- **C7 (null controls).** The C4 dichotomy must **fail** on two matched
  degree-4 families that are not summation polynomials: a uniform random
  degree-4 polynomial (NULL-A), and the `S_4` resultant construction with the
  inner summation polynomial replaced by a random quadratic (NULL-B). If either
  null obeys C4 at a rate near 100%, C4 is vacuous and the experiment fails.
- **C8.** All `2^{m-2}` Frobenius classes are realized, and each class yields
  exactly one factorization type.
- **C9.** `disc_T S_m` is a square in `F_p` at every good specialization for
  `m >= 4`, and is a non-square for exactly those `m = 3` specializations with
  `chi(f(a_1)) != chi(f(a_2))`.

## Falsification criteria

Any one of the following falsifies `H-SMON-db677d` at this scale:

- a good specialization whose factorization type is not the one C4 predicts;
- any irreducible factor of degree `>= 3` at a good specialization;
- any mixed factorization type at a good specialization;
- a good factor-base-locus specialization that does not split completely;
- a nonzero residual in the C6 per-class identity;
- a good specialization at `m >= 4` with non-square `disc_T S_m`;
- a null control obeying the C4 dichotomy at a rate indistinguishable from 100%.

## Curve battery

20 curves over `p in {101, 103, 211, 307, 401, 1009}`:

| class | count | why it is in the battery |
|---|---|---|
| generic `j` | 12 | the base case, two per prime |
| `j = 0`, `p = 1 mod 3` | 1 | extra automorphisms rational |
| `j = 0`, `p = 2 mod 3` | 1 | extra automorphisms irrational |
| `j = 1728`, `p = 1 mod 4` | 1 | extra automorphisms rational |
| `j = 1728`, `p = 3 mod 4` | 1 | supersingular |
| full rational 2-torsion | 4 | `Z = 3`: maximal ramification over `F_p` |

## Budget and replication

Single deterministic run, seed `20260807`, one process, < 5 minutes wall clock.
Sampling: 400 uniform specializations per curve at `m = 3, 4` and 100 at `m = 5`,
plus the same at the factor-base locus, plus exhaustive enumeration at
`(m,p) = (3,53), (3,101), (3,211), (4,37), (4,53)`.

## Required artifacts

- `code/semaev_cover.py`, `code/verify.py` (no third-party dependencies)
- `runs/RUN-SMON-e5cbe6-001/{manifest.yaml, raw-result.json, stdout.log, stderr.log}`

## What this experiment cannot establish

- It cannot prove the monodromy theorem. Frobenius data over finite fields
  constrain the monodromy group from below (which conjugacy classes occur) and
  give strong evidence against a larger group (no cycle type of order > 2 was
  ever seen), but the theorem is established by the derivation in
  `papers/semaev-conservation-specialization/paper.tex`, not by this battery.
- It says nothing about ECDLP hardness in either direction, and no run here
  solves any discrete logarithm.
- Largest prime is 1009. Any statement at cryptographic scale is out of tier.
