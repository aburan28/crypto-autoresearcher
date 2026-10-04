# EXP-MONO-bb6fa1 -- implementation notes

Run: `runs/RUN-MONO-bb6fa1-1/`. Executor session, handoff
`TASK-20260904-b669ac`, frozen contract `specification.yaml`
(`status: approved`, `frozen: true`, `execution_authorized: true`,
`approved_by: coordinator`).

These are implementation and observation notes. They contain no judgement
about whether `H-MONO-572e7e` or `IDEA-20260904-a1b81b` is supported or
refuted -- that is reserved for the Coordinator-dispatched independent
review cycle.

## 1. The key construction shortcut, and why it is not a protocol deviation

The task card's own wording describes, for each (e1,e2,e3), obtaining "the
Galois-stable root multiset (over F_101, F_{101^2}, or F_{101^3} as needed)"
and evaluating `S_4(t1,t2,t3,T0)` there.

Reading `EXP-MONO-815525/implementation/derive_s4.py` (as instructed) shows
this program already proved, symbolically, from scratch:

- `S_4` is fully symmetric under all 24 permutations of `x1..x4`
  (`s4_fully_symmetric_in_x1_x4: true`), hence in particular symmetric in
  `x1,x2,x3` alone;
- each `x4`-coefficient of `S_4` symmetrizes to `e1,e2,e3` with **zero
  remainder** (`s4_symmetric_descent_exact: true`), giving
  `Q_e(T) = sum_{k=0}^{4} c_k(e1,e2,e3,A,B) T^k` as an EXACT identity, not
  an approximation.

Consequently, for ANY Galois-stable root triple `(t1,t2,t3)` of `g(X) =
X^3 - e1 X^2 + e2 X - e3` (whatever field it lives in), `S_4(t1,t2,t3,T0)`
depends on `(t1,t2,t3)` ONLY through `(e1,e2,e3)`, and equals `Q_e(T0)`
evaluated as an ordinary univariate polynomial in `T0` with numeric
coefficients `c_k(e1,e2,e3,A,B)`. **No root extraction over any extension
of F_101 is ever needed to test V_R-membership.** This is a direct,
already-proven consequence of this program's own construction, not a new
assumption, and it is disclosed prominently (also in `manifest.yaml`
`protocol_deviations`) because the task card's own wording suggested the
extension-field route.

Root extraction over F_101 **only** (never an extension) is still used, as
specified, to classify the factorization TYPE of `g` (split / 1+2 /
irreducible / degenerate) for every triple that needs classifying.

### Independent cross-checks performed before the recorded run

1. `specialize_at_T0` (this run's merged-polynomial evaluator) was checked
   against `EXP-MONO-815525`'s own independent `qe_from_sym` function
   (evaluate `Q_e(T)` there, then evaluate the resulting degree-4
   polynomial at `T0`) on 500 random `(e1,e2,e3)` triples at
   `(p,A,B,T0)=(101,2,3,5)`: 0 mismatches.
2. `find_VR_points` (the nested-Horner exhaustive zero-set enumerator) was
   checked against a brute-force direct evaluation of the same merged
   polynomial for `e1 in [0,10)` and all `(e2,e3) in F_101^2`: the fast
   enumerator's hits restricted to `e1<10` matched the brute-force hit set
   exactly (1002 of 1002).
3. `classify_cubic` was checked against three hand-verified cases: a split
   cubic with roots `{0,1,2}`, a hand-found irreducible cubic, and a
   double-root-plus-simple-root degenerate cubic; all three classified
   correctly.

These checks are recorded here as implementation diligence; they are not
themselves part of the recorded run (they used a different, arbitrary test
curve `(A,B)=(2,3)`, not the run's own selected curve), and are not
retained as run artifacts.

## 2. Curve and point selection

**Rule (declared before any result was seen):** ascending scan `A = 0..100`
outer, `B = 0..100` inner (both starting at 0); take the first `(A,B)` with
(a) nonsingular discriminant `4A^3+27B^2 != 0 mod 101`, (b) `j not in
{0, 1728 mod 101}`, and (c) ordinary (`trace mod 101 != 0`, computed by
direct point-counting, not assumed).

**Result:** `E: y^2 = x^3 + x + 1` over `F_101`. `j = 34`, `#E(F_101) = 105`,
`trace = -3`. 103 `(A,B)` pairs were examined before this hit (the scan
starts at `A=0,B=0`, which is `y^2=x^3`, singular, and works forward).

**Generator:** ascending `x = 0,1,2,...`; for each `x` with a curve point,
compute the point's TRUE order by factoring `n = #E(F_101) = 105 =
3 * 5 * 7` and reducing the exponent at each prime (never assumed equal to
`n`). First point of full order `105`: `G = (6, 18)`.

**Point R:** `R = kG`, `k` smallest `>= 2` such that `R`'s own TRUE order
(computed the same way) exceeds 2 (i.e. `R` is provably not in `E[2]`).
`k=2`: `R = (8, 4)`, true order `105` (`> 2`, confirmed not in `E[2]`).
`T0 = x(R) = 8`.

## 3. Stage R8 (m=3 baseline, run first as a free/cheap gate)

Reused `EXP-MONO-815525/implementation/s3_monomials.json` read-only.
Checked the identity `disc_{x2} S_3(x1,x2,T0) = 16 f(x1) f(T0)` (with
`f(x)=x^3+Ax+B`) at 30 sample `(x1,T0)` pairs spanning `F_101` (stride 17
in `x1`, stride 23 in `T0`). **All 30 matched exactly.** R8: **PASS**.

## 4. Stage 1 (mandatory nearby-object controls)

Two DIRECT enumerations (never filtered from V_R), exactly as specified:

- **Synthetic A_3 object**: all `(e1,e2,e3) in F_101^3` with `disc(g)` a
  nonzero square. 510050 such triples (all non-degenerate, since disc=0
  is excluded by construction). Observed triple (split, 1+2, irreducible)
  = `(0.32673, 0.00000, 0.67327)`.
- **Unconstrained object**: all `1030301` triples in `F_101^3`, no
  condition. 10201 are degenerate (repeated root); of the 1020100
  non-degenerate, observed triple = `(0.16337, 0.50000, 0.33663)`.

**Literal gate as specified** ("confirm the reported triple is
`(1/3,0,2/3)` / `(1/6,1/2,1/3)` ... within 3 standard errors, ~0.005 at
p=101"): computing the standard error as `sqrt(0.25/n)` from the ACTUAL
exhaustive-census sample size (`n=510050` and `n=1020100` respectively,
giving `se ~ 7e-4` and `~5e-4`), **both controls FAIL** this literal
numeric band -- the observed deviations (0.0033-0.0066) exceed `3*se`
(0.0015-0.0021).

**Disclosed in full, not used to override the gate**: both control
objects are EXHAUSTIVE censuses of the entire population of monic cubics
over `F_101`, not statistical samples of a curve. Their exact
factorization-type counts are classical, closed-form combinatorial facts
(valid for any `p` with `char != 2,3`):

```
#split              = C(p,3)              = p(p-1)(p-2)/6
#one_plus_two       = p * #irred_quadratics = p^2(p-1)/2
#irreducible_cubic  = (p^3 - p)/3
#degenerate         = p^2
```

giving EXACT finite-`p` densities `((p-2)/(3p), 0, 2(p+1)/(3p))` on the
disc-square stratum and `((p-2)/(6p), 1/2, (p+1)/(3p))` on the
unconstrained population -- both `O(1/p)` away from the `p -> infinity`
idealized Chebotarev triples `(1/3,0,2/3)` and `(1/6,1/2,1/3)` used as the
literal comparison target, **by construction of finite-field
combinatorics, not by any deficiency of the classifier**. This run's
observed counts match these closed-form formulas **bit-exactly**
(verified in code, `matches_exact_finite_p_formula: true` for both
objects), and the two objects are sharply, correctly distinguished from
one another (0.3267 vs 0.1634 split density; 0.0 vs 0.5000 one-plus-two
density) -- the opposite of "the classifier cannot see the effect", which
is what S1 is actually trying to rule out.

This tension -- a literal numeric tolerance apparently calibrated for a
much smaller sample (Stage 0's own `~p^2 ~ 10^4`-point V_R census) applied
here to a `~10^5`-`10^6`-point EXHAUSTIVE population census, whose
deviation from the idealized target is a real `O(1/p)` combinatorial fact
that no larger `n` will shrink -- is a plausible specification-tolerance
ambiguity. **This run does not resolve it unilaterally.** It applies the
literal wording exactly as written, records BOTH the literal result and
the full exact-formula context, and follows the frozen stopping rule: **S1
fails, so Stage 0's own R1/R2/R3 are reported below but NOT interpreted in
either direction.**

## 5. Stage 0 (reported, not interpreted, because S1 failed)

Exhaustive enumeration of all `1030301` `(e1,e2,e3) in F_101^3` via the
`Q_e(T0)` merged-polynomial zero test (Section 1): `|V_R(F_101)| = 10202`
(Lang-Weil expectation `p^2 = 10201`, envelope `+/- 3045.1` -- within
envelope). Of these, `203` are degenerate (repeated root of `g`) and `0`
are the `anomaly_disc_q_zero` flag (none triggered, as expected for a
correct discriminant formula). Of the `9999` non-degenerate points:

- `R1` (disc-square rate) = `0.49525`
- `R2` (1+2 density) = `0.50475`
- `R3` (split density) = `0.16832`
- irreducible density = `0.32693`

**These numbers are recorded exactly, per the specification's own
`success_criterion`, but are NOT interpreted against outcome I / II /
neither, because S1 (Stage 1's mandatory gate) did not pass under the
specification's literal wording.** See `execution_report.yaml` and
`manifest.yaml` `protocol_deviations`/`anomalies` for the full disclosure.

## 6. No CAS at runtime

Only the Python standard library is imported by
`run_galois_cubic_census.py`. `sympy` is never imported at runtime; the
`s3_monomials.json` / `s4_symmetric_coeffs.json` tables it reads were
produced offline by `EXP-MONO-815525`'s own `derive_s4.py` and are reused
read-only, unmodified.

## 7. Budget

Total wall/CPU: 6.4s (budget 900s each). Peak RSS: ~20.1 MiB (budget 128
MiB). Disk: 24 KB (budget 10 MB). All well within budget; no internal
limit was extended.
