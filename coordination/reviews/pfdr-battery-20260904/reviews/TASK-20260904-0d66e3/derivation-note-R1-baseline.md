# R1 derivation note — the (S2)-(S3) derivation and the Koszul-only baseline

TASK-20260904-0d66e3 (red team), EXP-PFDR-20ee58. **Labelled DERIVATION, never
proved.** Every mechanical value quoted here was produced by
`r1_r4_checks.py` (output `r1-r4-checks.json`) and `r2_sensitivity.py`
(`r2-sensitivity.json`) in this directory, using `harness/macaulay_fp` at
snapshot commit `2d2083e5` (per-file sha256 re-verified against
`harness/macaulay_fp/VALIDATION.md` §1; all twelve match). The twin generators
are built by `twin_build.py`, written from the definition in the handoff's
`review_plan` and H-PFDR-9aadc0 (S1)–(S4); no producer script is imported. The
builder reproduces the recorded generator statistics exactly (98 and 21 terms;
degree histograms `{0:1,1:7,2:15,3:33,4:42}` and `{0:1,1:4,2:7,3:6,4:3}` at
s = 3, p = 4099, curve 4101), which is the independent check that it is the
same object.

## 1. (S1) degrees — CONFIRMED at every tested (s, p)

`deg E1 = deg E2 = 4` at every (s, p) in {3,4,5,6} × {4099, 16411, 65537}
(12/12 cells). The derivation's reason is correct: in
`x_k^2 = Σ_i 4^i a_{k,i} + 2 Σ_{i<j} 2^{i+j} a_{k,i} a_{k,j}` the cross term
survives because 2 and 2^{i+j} are units for p > 2. It is exactly this clause
that fails at p = 2, and the p = 2 object (proves-too-much object 3) shows the
failure: `deg E1 = deg E2 = 3` in the mixed ring and 2 in the pure Boolean
reading.

## 2. (S3 ingredient ii) top-degree structure — CONFIRMED

At every tested (s, p): `top(E1)` has exactly `C(s,2)^2` u-free digit-degree-4
monomials (9 / 36 / 100 / 225 at s = 3 / 4 / 5 / 6, matching the derivation's
count); every monomial of `top(E2)` has u-exponent exactly 2 and block-3 digits
only, and there are exactly `C(s,2)` of them (3 / 6 / 10 / 15); the two top
forms share no monomial, hence are linearly independent, hence
`deg(c1 E1 + c2 E2) = 4` for every `(c1, c2) != (0,0)`. F1 does not fire.

## 3. (S2 / S3 ingredient i) the idempotent law — CONFIRMED, with one correction

`f = a_0 + a_1` gives `f^2 - f = 2 a_0 a_1 != 0`, so no affine form in ≥ 2
variables is idempotent for p > 2. That is what the derivation claims and it is
right.

**Correction to the surrounding prose.** `stage0-derivation.md` §3 concludes
that "the idempotent ingredient of the binary D = 3 mechanism has no F_p
analogue". The digit ring `F_p[a]/(a^2 - a)[u]` still contains 2^{3s}
idempotents — every digit monomial `e` satisfies `e^2 = e`, and `(1 - e) e = 0`
— at *every* p. What fails is only that an **affine** form in ≥ 2 variables is
idempotent. The distinction is not academic: object D1 of `r2-sensitivity.json`
(two quartics sharing the idempotent factor `a_0`) shows deficits
`[2, 20, 95, 289]` at D = 5..8 over F_4099, i.e. a Boolean-style duplication
relation (`a_0 f = f`, so the rows `m f` and `(a_0 m) f` coincide) living in
characteristic 4099. The twin escapes it because its generators have a nonzero
constant term and hence no digit-variable factor — a fact about these two
quartics, not about the characteristic.

## 4. The Koszul-only baseline: what is rigorous and what is HEUR-001

Split the baseline `rank(Mac_D) = rows(D) - koszul(D)` into two claims.

**(4a) The trivial-syzygy count is exact here — RIGOROUS.** With exactly two
generators of degree 4 there is exactly one Koszul pair; under the cumulative
convention `koszul_pair_count(D) = #{monomials of degree ≤ D - 8}`, which is 0
for D < 8 and 1 at D = 8. `koszul.py`'s docstring warns that the pairwise count
is exact "only below the first degree at which second syzygies (degree
d_i + d_j + d_k) appear" — with only two generators there is no third generator
and no such degree, so the count cannot over-count anywhere in D ≤ 8. This is
not a heuristic. (Contrast: on the binary fixture at p = 2 the same count *does*
over-count above D = 5, and my p = 2 twin object 3b returns
`deficit_pairwise = [0, 0, 0, -12, -102, -402, -987]`; negative values are the
over-count showing.) The Frobenius family contributes 0 here by §3, and
`koszul.frobenius_count` returns 0 for p > 2 and in mixed mode, consistently.

**(4b) That the rank attains that bound — HEURISTIC (HEUR-001).** The step
"hence the generic prediction is `rank = rows` for D < 8 and `rows - 1` at
D = 8" is Fröberg / Bardet–Faugère–Salvy semi-regularity applied to this ring
and support. It is not derivable from (S2)–(S3), and objects A1, A2, A3 and D1
of `r2-sensitivity.json` are counterexamples in the same ring at the same
degrees which satisfy (S2) and (S3) verbatim. H-PFDR-9aadc0 does carry this
step as HEUR-001 with a `falsification_condition`, which is the honest
treatment; `stage0-derivation.md` §4 and H-PFDR-9aadc0 (S2) — the latter under
the tag "DERIVED" — present the same step as a consequence of (S2). **The two
should be reconciled: (S2)'s "Hence … predicted generic rank …" is HEUR-001,
not a derivation.** Nothing in the run set depends on the mislabel, because the
quantity was measured rather than assumed.

## 5. The three candidate "second trivial relations" the attack plan named

- **(i) relations induced by the reduction `a^2 -> a`.** A product `m·E_i` can
  drop below degree D; such rows are kept and counted (VALIDATION.md §4 item 1)
  and would appear as rank loss. Measured: none — at D = 5, 6, 7 the rank equals
  the row count exactly (22, 114, 374) on all twelve deciding-cell instances.
- **(ii) the free variable's powers.** The row blocks `u^e E_i` occupy disjoint
  column sets by u-exponent (the generators are not u-free, so this is not a
  clean block decomposition for the twin; it *is* one for the calibration's
  mixed-mode object, see the R3 note), and no dependency among them was found.
- **(iii) zero-product rows.** Under the cumulative convention a row `m·E_i = 0`
  is a genuine syzygy `(m, 0)` that is DROPPED and separately counted. It could
  therefore hide a relation. Measured: `zero_product_rows = 0` on every one of
  the 246 twin draws (R0) and on all twelve instances I rebuilt, so nothing is
  hidden here. The convention's blind spot is real but empty for this object;
  it is not empty in general (my p = 2 mixed object drops up to 405 such rows).

## 6. What the deficit-0 reading actually asserts — VERIFIED DIRECTLY

On all twelve deciding-cell instances (6 curves × 2 targets, s = 3, p = 4099) I
rebuilt the generators and found rows 886, columns 2304, rank 885, so the left
kernel of the D = 8 Macaulay matrix has dimension exactly **1**; and the Koszul
vector (coefficients = the monomials of E2 on the E1 rows, minus the monomials
of E1 on the E2 rows — all of degree ≤ 4, hence all legal multipliers) is a
genuine dependency. A 1-dimensional kernel containing the Koszul line **is** the
Koszul line. So `deficit(8) = 0` is not a coincidence of two counts: the twin's
only degree-≤4 syzygy is the Koszul one. Equivalent statement of the finding:
*the syzygy module of (E1, E2) has no minimal generator of multiplier degree
≤ 4 other than the Koszul relation.*

## 7. Scope of the baseline claim

Everything above is at m = 3, d = 2, s ∈ {3,4,5,6}, p ∈ {4099, 16411, 65537},
D ≤ 8, cumulative multipliers. Nothing is claimed at D > 8, where the multiplier
degree exceeds 4 and neither (4a) nor the measurement applies.
