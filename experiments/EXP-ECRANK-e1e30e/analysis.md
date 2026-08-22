# EXP-ECRANK-e1e30e — analysis

Certified Mordell–Weil rank ≥ 31 for explicit elliptic curves over explicit
number fields, and how small the field degree gets.

## The distinction the result turns on

"An elliptic curve of rank > 30" is two different problems.

* **Over Q** the largest known rank for an explicit curve is **30**
  (Alpöge–Howell, 2026; previously Elkies–Klagsbrun 29 in 2024, Elkies 28 in
  2006). Rank ≥ 31 over Q is **open**. This experiment claims nothing there.
* **Over number fields of growing degree** rank is unbounded, so existence is
  not the question. The measurable questions are *how small a field*, *how
  explicit a witness*, and *how strong a certificate*.

Everything below is the second problem, stated in those terms.

## Results

| [K:Q] | rank ≥ | certificate | base curve |
|---|---|---|---|
| 2 | 31 | relative (external 30, exact +1) | Alpöge–Howell record curve |
| 8 | 20 | **control: short of 31** | `[0,-1,1,8,-50]` |
| 16 | 32 | exact + height regulator | `y² = x³ − 22275x − 232733250` |
| 32 | **32** | **exact, no numerics** | `[1,-1,1,0,0]`, conductor 53 |
| 32 | 52 | exact + height regulator | `y² = x³ − 891x − 1861866` |
| 64 | **64** | **exact, no numerics** | `[1,0,1,4,21]` |

Headline exact statement, with no floating point anywhere in its proof:

> **E : y² = x³ + 405x + 16038**, minimal model `[1,-1,1,0,0]`, conductor 53,
> has **rank E(K) ≥ 32** over **K = Q(√−2, √−3, √−5, √7, √13)**, `[K:Q] = 32`.

At degree 64, curve `[1,0,1,4,21]` reaches **rank ≥ 64** — all 64 twist classes
carry a point, the ceiling of the method at k = 6.

## Mechanism

For squarefree d, E^(d) injects into E(K) as a χ_d-eigenvector of
Gal(K/Q) ≅ (Z/2)^k. Distinct classes ⇒ distinct isotypic components ⇒
independence *by algebra*. The certificate is then four finite exact checks:
points on curve; non-torsion via Mazur (m·P ≠ O, m = 1..12); classes pairwise
distinct mod squares; V a subgroup containing 1. Full statement in
`source/twist_family.py` and KN-TECH-eb06ea.

The ceiling is structural — only 2^k characters — so rank ≥ 31 by this argument
alone forces [K:Q] ≥ 32. The degree-16 row buys its extra rank from several
points per class, whose independence is a Néron–Tate regulator: numerical, and
reported separately for that reason.

## Controls, and what they showed

* **Null object (degree 8).** Best over the whole 502-curve pool: 20, not 31.
  The pipeline does not succeed at every degree.
* **Independent verifier.** `verify_certificate.py` is pure-Python exact
  arithmetic and never calls PARI. It **rejected the first build** of the
  multiplicity certificates: XOR cancellation in coset transport had put 16
  points on isomorphic-but-different models. Fixed with an explicit transport
  factor `t`, then rebuilt and re-verified. The independence of verifier from
  search is load-bearing in fact, not just in design.
* **Timeouts are never evidence.** A twist whose descent hits the PARI alarm
  contributes 0 to every score and is counted `timed_out`, never as rank 0.
* **PARI is used to find, never to assert.** Every point it returns is
  re-checked on-curve and re-checked non-torsion downstream.

## The negative result, which constrains the ladder

Base rank over Q is the binding constraint, and this pipeline could not raise it:

* Mestre–Nagao prefilter over **364,756** squarefree twists of five
  small-conductor curves (|d| ≤ 300000, primes to 1500), then `ellrank` on the
  400 best per curve: **no twist of rank ≥ 5**.
* Enumeration of **49,692** small-coefficient curves: 497 distinct j-invariants
  of rank ≥ 3, exactly **2** of rank 4.

So the reported degree floor of 16 is **a property of the search, not a
theorem**. The degree-2 row is the proof of that: hand the construction a
rank-30 curve and degree 2 follows immediately. Reaching degree 8 needs base
curves of rank ≈ 8 over Q — a Mestre-style construction, not a twist search.

## Reproduction

```sh
cd experiments/EXP-ECRANK-e1e30e
python3 source/verify_all.py                                   # exact + regulator, all certificates
python3 source/verify_certificate.py certificates/cert_deg32_eigenspace.json   # stdlib only
python3 source/verify_quadratic_lift.py certificates/cert_deg2_rank31.json
python3 source/verify_record_curve.py runs/RUN-ECRANK-e1e30e-003/record_curve_input.json /tmp/out.json
```

`verify_certificate.py` and `verify_quadratic_lift.py` need **only the Python
standard library**. `regulator_check.py` and `verify_record_curve.py` need
`cypari`; the search additionally needs `numpy`.
