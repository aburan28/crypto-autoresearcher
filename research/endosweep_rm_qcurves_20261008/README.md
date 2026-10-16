# Real multiplication on fast Kummers, and Q-curves beyond FourQ

Two speculative (tier-2) follow-ups from the endomorphism shortlist, each
settled with a cheap test:

* **Item 7 (candidate "C2"):** do genus-2 Jacobians with real multiplication
  by `Z[(1+√5)/2]` ever meet the conditions a fast Kummer surface needs?
* **Item 8:** is any Smith-style Q-curve over `F_{p²}` competitive with
  FourQ under this harness's cost model?

This is scalar-multiplication engineering (constant factors). It is not an
ECDLP result and not a security claim. Every figure below is labelled
**measured** (exact counts, or checked on points) or **modelled** (from the
`costmodel.py` table).

Two commands regenerate every output here, followed by the checksum line:

```sh
python -m harness.endosweep.rmkummer --out-dir research/endosweep_rm_qcurves_20261008   # ~9-12 min under nice, 4 busy cores
python -m harness.endosweep.qcurves  --out-dir research/endosweep_rm_qcurves_20261008   # ~70 s; SEA point counts need cypari2
(cd research/endosweep_rm_qcurves_20261008 && sha256sum rm_kummer.json qcurves.json > SHA256SUMS)
```

The defaults are `--pmin 1000 --pmax 1600 --seed 20261008` for `rmkummer`
and `--dmax 3000 --seed 1` for `qcurves`. The counts are deterministic. The
`elapsed_s` fields and the random points used in the on-point checks are
not.

---

## Item 7: RM family against the fast-Kummer conditions

### Question

The family is `C_t : y² = D₅(x) + t`, where `D₅(x) = x⁵ − 5x³ + 5x` is the
Dickson polynomial. Its Jacobian carries an endomorphism `φ` with
`φ² + φ − 1 = 0`. Then `φ` and `φ − 1` are units and commute with `[−1]`, so
they descend to the Kummer surface. That would give the triple
`(P, φP, (φ−1)P)` a two-dimensional differential chain needs.

The named obstruction: a fast (Gaudry / squared-theta) Kummer needs all of
`J[2]` rational and `#J = 16·prime`, and the family might never give both.

**Kill rule:** zero hits in the family while a control shows hits.

### Literature: what the notes actually say

* **KN-LIT-3191** (Gaudry–Kohel–Smith, *Counting points on genus 2 curves
  with real multiplication*): an "accelerated Schoof-type point-counting
  algorithm for curves of genus 2 equipped with an efficiently computable
  real multiplication endomorphism", with which "we compute a 256-bit
  prime-order Jacobian".
* **KN-LIT-207** (Kohel–Smith 2006, *Efficiently computable endomorphisms
  for hyperelliptic curves*): "we describe three infinite families of curves
  which admit an efficiently computable endomorphism, and give algorithms
  for their efficient application".
* **KN-LIT-390** (Smith 2013, *Easy scalar decompositions*): short lattice
  bases "for the GLV, GLS, GLV+GLS, and Q-curve constructions on elliptic
  curves, and for genus 2 real multiplication constructions".

None of these notes names `x⁵ − 5x³ + 5x + t`, or says over which field its
RM is defined. That the family is due to Tautz–Top–Verberkmoes is from the
brief and is **(unverified)**. Everything this README says about the family
was derived and checked here, not taken from the literature.

For the Kummer side:

* **KN-LIT-3797** (Bos–Costello–Hisil–Lauter, *Fast cryptography in genus
  2*): "fast formulas on the Kummer surface and efficient 4-dimensional GLV
  decompositions", and a Kummer implementation that "breaks the 120 thousand
  cycle barrier".
* **KN-LIT-4614** (Bernstein–Chuengsatiansup–Lange–Schwabe, *Kummer strikes
  back*): reports Diffie–Hellman speed records from Kummer surfaces.

The exact conditions a squared-theta Kummer imposes beyond rational `J[2]`
(rationality of the squared theta constants) are not in any note and are
**(unverified)**. They are not tested here.

### What is checked

1. **The splitting condition, proven and then checked.**
   * `J[2]` is the group of even subsets of the six Weierstrass points
     modulo complement. Frobenius fixes `∞`, so `J[2] ⊂ J(F_p)` exactly when
     `f` splits into five distinct linear factors over `F_p`.
   * Substitute `x = z + 1/z`. Then `D₅(x) = z⁵ + z⁻⁵`, so the roots of `f`
     come from the fifth roots of `w`, where `w² + tw + 1 = 0`.
   * This gives a closed form, `rmkummer.split_criterion`:
     * `p ≡ 1 (mod 5)`: `f` splits iff `t² − 4` is a nonzero square and `w`
       is a fifth power in `F_p^*`.
     * `p ≡ 4 (mod 5)`: `f` splits iff `t² − 4` is a non-square and `w` is
       a fifth power in the norm-one torus of `F_{p²}`.
     * `p ≡ ±2 (mod 5)`: never. Here `z ↦ z⁵` is a bijection on both tori,
       so `D₅` permutes `F_p` and `f` has exactly one rational root for
       every `t`.
   * The criterion is compared with direct root counting on every member.
2. **`#J` and `#J_twist` of every member, exactly.**
   * `#C(F_p)` and `#C(F_{p²})` are computed for all `t` of a prime at
     once. The values `g(x)` for `x ∈ F_{p²}` are binned by
     `(Re, nr·Im²)`, which turns the character sum into an FFT
     cross-correlation in `t`. The result is rounded, and the code raises
     an error if any value is more than `10⁻³` from an integer.
   * Then `#J = (N1² + N2)/2 − p`.
   * Cross-checks: the brute-force `genus2.jacobian_order` (in the tests),
     and PARI's `hyperellcharpoly` on 12 random members (12 of 12 agree).
3. **RM on every member.** The characteristic polynomial factors over
   `Q(√5)` as `(T² − aT + p)(T² − a′T + p)` iff `s1² − 4s2 + 8p = 5v²`.
4. **`φ` written on points and verified.**
   * The map is `P = (x, y) ↦ (x₁, y) + (x₂, y)`, where
     `x₁ + x₂ = φ₁x`, `x₁x₂ = x² − 3 − φ₁` and `φ₁ = ζ₅ + ζ₅⁻¹`. In Mumford
     form this is `u = X² − φ₁xX + (x² − 3 − φ₁)`, `v = y`, defined over
     `F_p(√5)`.
   * It is `π_* σ π^*` for the cyclic cover `z ↦ z + 1/z`. Because that
     cover's quotient by `σ` has genus 0, the map satisfies `T² + T − 1 = 0`.
     The derivation is in the module docstring.
   * Checked on points:
     * `T(P)` lies on `J` (40 points);
     * `T(T(P)) + T(P) − P = 0` on every sampled point whose image splits;
     * all 16 two-torsion classes are rational;
     * `T` acts on `J[l]`, `l = #J/16`, as a root of `X² + X − 1 (mod l)`;
     * the decomposition `k = k₁ + k₂λ` reconstructs `kD`.
5. **Controls (no RM):**
   * **A** is the translation family `g + t`, with `g` a random monic
     quintic of the same shape: one `g` per prime and the same pipeline.
   * **B** is random fully split quintics `∏(x − rᵢ)`: about a third as
     many per prime as the RM family has split members, counted directly.

### Results (all measured, 1000 < p < 1600)

The full table, with Wilson intervals and examples, is in
[`rm_kummer.md`](rm_kummer.md).

| | RM family `D₅ + t` | control A `g + t` | control B random split `f` |
|:--|--:|--:|--:|
| primes `p ≡ ±1 (mod 5)` | 44 | 44 | 44 |
| nonsingular members, all with exact `#J` | 56 630 | 56 686 | 1 891 |
| `f` splits (all of `J[2]` rational) | 5 628 (9.94 %) | 456 (0.80 %) | 1 891 |
| … and `#J/16` prime | **859 (15.3 %)** | 21 (4.6 %) | 80 (4.2 %) |
| … and `#J_twist/16` prime | 863 | 37 | 103 |
| … both (twist-secure) | **247 (4.4 %)** | 7 (1.5 %) | 20 (1.1 %) |
| char. poly. factors over `Q(√5)` | 56 630 of 56 630 | 507 of 56 686 | 67 of 1 891 |
| 2-adic valuation of `#J`, split members | only even: 4 (72 %), 6, 8, … | 4 (35 %), 5, 6, … | 4 (35 %), 5, 6, … |

The prime classes `p ≡ ±2 (mod 5)` in the range:

* 39 primes and 50 861 members, of which 0 split.
* `D₅` is a permutation of `F_p` on all 39.
* 0 of 4 188 members tested have a characteristic polynomial that factors
  over `Q(√5)`, so the RM is not defined over `F_p` there.

The closed-form criterion and the root count disagree on 0 members.

### Findings

1. **The named obstruction does not hold. Item 7 is not killed.**
   * Within the measured range, a tenth of the family has all of `J[2]`
     rational.
   * Of those, 15.3 % have `#J = 16·prime`, and 4.4 % also have a
     `16·prime` twist.
   * That is about 3.5 times the rate of generic curves with full rational
     2-torsion (4.2–4.6 %, controls A and B).
2. **The excess has a clear cause.**
   * `#J = N_{Q(√5)/Q}(1 + p − a)`, and 2 is inert in `Z[φ]`, so the 2-part
     of `J(F_p)` is a module over `Z₂[φ]` and has even 2-adic valuation.
   * The measured valuations are all even, and the minimum, 4, occurs in
     72 % of split members against 35 % in the controls.
   * Splitting is also 12 times more frequent than for a generic quintic:
     1/10 from the closed form (half the `t` put `w` in the right torus,
     and a fifth of those make it a fifth power), against `1/120` for an
     `S₅` quintic.
3. **The prime classes `p ≡ ±2 (mod 5)` are excluded, and they include
   `2^127 − 1`.**
   * There `D₅` permutes `F_p`, so no member has rational `J[2]`, and the
     RM is not even defined over `F_p` (`φ₁ ∈ F_p(√5)`).
   * `2^127 − 1 ≡ 2 (mod 5)`, so the family cannot use the prime of the
     record Kummer implementations. It needs `p ≡ ±1 (mod 5)`.
4. **`φ` is explicit and verified.** On `p = 1009, t = 11` (`p ≡ 4 mod 5`,
   `#J = 16·61 751`) and `p = 1021, t = 40` (`p ≡ 1 mod 5`,
   `#J = 16·67 061`), every check in item 4 above holds. The decomposition has
   coefficients of `log₂(l)/2` bits.
5. **Payoff ceiling (modelled).**
   * A 1-D ladder takes `b` steps of xDBL + xADD. The 2-D chain takes `b/2`
     steps of xDBL + 2 xADD (the Bernstein binary-chain shape, assumed).
   * With `ρ = cost(xADD)/cost(xDBL)`, the speed-up is `2(1+ρ)/(1+2ρ)`:
     **1.333 at ρ = 1**, 1.5 at ρ = 0.5 and 1.25 at ρ = 1.5.
   * The model ignores the one-off cost of `φ` on the Kummer and the
     differences.
   * The chain needs `(φ−1)P` as its difference point, and that point
     descends to the Kummer.
6. **Changing the model cannot get around the split condition.**
   * `J[2]` is a Galois module of the Jacobian, independent of the curve
     model, and a quadratic twist leaves it unchanged (`[−1]` is trivial on
     `J[2]`).
   * The fast Kummer's level-2 theta structure uses the translations by
     `J[2]`, so "rational 2-torsion on another model, or on the Kummer only"
     is the same condition.
   * A general (Cassels–Flynn) Kummer needs no rational 2-torsion, but it
     is not the fast one; its cost was not measured here.

### Still open for item 7, in order

* Whether hits have rational squared theta constants (the extra Gaudry
  condition, **unverified**).
* Formulas for `φ` in squared-theta coordinates. `φ` is an automorphism of
  `J` that does not preserve the principal polarization, so on the
  `2Θ`-embedded Kummer it is given by higher-degree forms, not a linear map.
* A 127-bit prime `p ≡ ±1 (mod 5)` with fast arithmetic, and a member
  found by `split_criterion` plus point counting (Gaudry–Kohel–Smith,
  KN-LIT-3191).

The ceiling stays ≤ 1.33× over the fast-Kummer ladder at `ρ = 1`.

---

## Item 8: Q-curves over `F_{p²}` against FourQ

### Question

Does any Smith-style Q-curve with a degree-`d` endomorphism beat FourQ
(`D = −40`, maps of degree 2 and 5, 4-D GLV+GLS) under the harness cost
model?

### Literature: what the notes actually say

* **KN-LIT-3779** (Smith, *Families of fast elliptic curves from
  Q-curves*):
  * "reducing quadratic Q-curves … modulo inert primes";
  * "for every prime p > 3, two one-parameter families of elliptic curves
    over F_{p²} equipped with endomorphisms that are faster than doubling";
  * "GLS … appears as a degenerate case";
  * examples "for the particularly efficient primes p = 2^127 − 1 and
    p = 2^255 − 19".
* **KN-LIT-3937** (Guillevic–Ionica, *Four-dimensional GLV via the Weil
  restriction*): "a four-dimensional GLV method on Freeman and Satoh's
  Jacobians and on two new families of elliptic curves defined over
  F_{p²}".
* **KN-LIT-3831** (Costello–Hisil–Smith): "two-dimensional differential
  addition chains driven by efficient endomorphism decompositions, built on
  curves selected from a family of Q-curve reductions over F_{p²} with
  p = 2^127 − 1".

Smith's explicit degree-2 family is, as recalled (**unverified**),
`y² = x³ − 6(5 − 3s√Δ)x + 8(7 − 9s√Δ)`. With `s = 4/9` and `Δ = 5` this is
exactly FourQ's model `W` in `fourq.py` (`A = −(30 − 8√5)`,
`B = 56 − 32√5`); the arithmetic was checked. The constructions below do not
rely on that formula.

### What is checked

1. **Explicit maps at `p = 2^127 − 1`, verified on points.**
   * Curves with a `d`-isogeny to their Frobenius conjugate come from the
     `X_0(d)` Hauptmodul:
     * `d = 2`: `j = (t+16)³/t` with `t·t^p = 4096`;
     * `d = 3`: `j = (t+27)(t+3)³/t` with `t·t^p = 729`.
   * The Atkin–Lehner involution `t ↦ c/t` maps `j(τ)` to `j(dτ)`, so this
     choice makes `j(dτ) = j^p`.
   * The map is built as `ψ = Frobenius ∘ isomorphism ∘ Vélu`. The kernel is
     a root of the 2- or 3-division polynomial in `F_{p²}`
     (Cantor–Zassenhaus). The codomain must have `j = j(E)^p`, and the
     isomorphism must be defined over `F_{p²}`.
   * Checked on points:
     * `ψ(P)` lies on `E`;
     * `ψ(P+Q) = ψ(P) + ψ(Q)`;
     * `ψ(ψ(P)) = [±d]P`;
     * `[#E]P = O`, with `#E` from PARI's SEA;
     * `ψ` acts as a square root of `±d` on a subgroup of large prime
       order `l`;
     * the decomposition `k = k₁ + k₂λ` reconstructs `kG`.
   * The same builder is run on FourQ's `W`.
2. **The CM sweep at `p = 2^127 − 1`, exact.**
   * Scope: every fundamental `D` with `|D| ≤ 3000`, `p` split in `Q(√D)`,
     and the prime `𝔭` above `p` of class order exactly 2 (so `j ∈
     F_{p²} \ F_p`).
   * `π_{p²}` generates `𝔭²` (found by Cornacchia), and `#E = N(1 − π)` for
     `π = ±γ`.
   * Each ideal `𝔞` in the class of `𝔭` gives a Q-curve map `E → E^(p)` of
     degree `N(𝔞)`. Its `ψ_𝔞` is the generator of `𝔞𝔭`, with eigenvalue
     `β(λ_ω)`, where `λ_ω` is fixed by `π ≡ 1` on the subgroup.
   * 2-D configurations are `{1, ψ_𝔞}`. 4-D configurations are
     `{1, ψ_𝔞, ψ_𝔟, ψ_𝔞ψ_𝔟}` for two independent ideals, on the exact LLL
     lattice.
   * `D = −40` must reproduce FourQ.
3. **Costs (modelled).**
   * `costmodel.multiscalar_cost`, in `F_p` multiplications of a 127-bit
     `p`. Twisted Edwards `a = −1` over `F_{p²}` is used for every row; it
     needs `4 | #E`, which is reported. Jacobian generic-`a` Weierstrass
     over `F_{p²}` is the second model.
   * A degree-`d` map costs `c(d) = 3·(Σ isogeny_step_cost(ℓ) + 20) + 6` M:
     the harness's x-only step counts plus its 20-M overhead, in `F_{p²}`,
     plus 2 `M₂` for the isomorphism. The Frobenius is free.
   * This gives `c(2) = 78`, `c(3) = 82.8`, `c(5) = 94.8`, `c(7) = 106.8`,
     `c(11) = 130.8` and `c(13) = 142.8`.

### Results

The full tables are in [`qcurves.md`](qcurves.md).

**FourQ under the harness model** (`n` = 246 bits):

| configuration | coeff bits | total M, Edwards | total M, Weierstrass |
|:--|--:|--:|--:|
| FourQ 4-D, maps at the model cost `c(2)`, `c(5)` | 62 | **3028.4** | 3579.8 |
| FourQ 4-D, maps at `fourq.py`'s measured affine counts (169 M, 211 M) | 62 | 3326.6 | 3878.0 |
| FourQ `ψ` alone (2-D) | 123 | 3950.2 | 4333.8 |
| no endomorphism (1-D) | 246 | 6073.0 | |
| GLV+GLS, `j = 0` (`ζ₃`, `ψ_GLS`), synthetic `n` (Longa–Sica shape, `d = 1`) | 61 | 2524.8 | 2911.2 |

**`ψ` alone (2-D) for every degree:**

* `d = 1` (GLS): 3658 M.
* `d = 2, 3, 5, 7, 11, 13`, either sign of `ψ²`: 3830–3940 M, with
  122–124-bit coefficients.

**CM sweep at `p = 2^127 − 1`:**

* 909 fundamental `D`; `p` splits for 459; the class of `𝔭` has order 2
  for 67.
* 6 twists have `#E = h·prime` with `h ≤ 4096`:

| D | cofactor | 4 \| #E | cheapest 4-D degrees | coeff bits | total M, Edwards | total M, Weierstrass |
|--:|--:|:--|:--|--:|--:|--:|
| −40 (**FourQ**, `#E = 392·N`) | 392 | yes | 2, 5 | 62 | **3028.4** | 3579.8 |
| −212 | 334 = 2·167 | **no** | 2, 27 = 3³ | 62 | 3050.0 | 3601.4 |
| −840 | 3348 | yes | 7, 30 | 61 | 3078.0 | 3618.2 |
| −795, −1588, −1752 | 457, 758, 972 | no, no, yes | only one class norm ≤ 61 | — | no cheap 4-D | — |

**Cross-check against `fourq.py` (measured).** On `D = −40`, FourQ's
verified maps act on the subgroup as `ψ = −4·ψ_𝔞` with `N(𝔞) = 2`, and
`φ = −4·ψ_𝔞` with `N(𝔞) = 5`. The factor 4 comes from the degree-4
conjugation through `τ` and `τ̂`. So the CM eigenvalue derivation reproduces
FourQ exactly.

**Explicit maps (measured on points, `p = 2^127 − 1`):**

| curve | `ψ²` | `#E` = cofactor · `l` | `ψ` affine ops (projective-equivalent) | all checks |
|:--|--:|:--|:--|:--|
| FourQ's `W`, degree 2 | +2 | 392 · (246-bit `N`) | 5 `M₂` + 1 `S₂` + 1 `I₂` (26 M) | pass |
| `X_0(2)` member, degree 2 | −2 | 824 583 204 · (225-bit prime) | 5 `M₂` + 1 `S₂` + 1 `I₂` (26 M) | pass |
| `X_0(3)` member, degree 3 | +3 | 75 323 · (238-bit prime) | 8 `M₂` + 1 `S₂` + 1 `I₂` (35 M) | pass |

The curve constants are in `qcurves.json`.

### Findings

1. **`ψ` alone cannot compete.**
   * Every Smith family without CM has an endomorphism ring of rank 2, and
     `ψ` already uses it, so the decomposition is 2-D with ≈ 123-bit
     coefficients.
   * In the model that costs 3830–3940 M, 26–30 % more than FourQ's 4-D
     (3028 M). It loses even with a free map: GLS costs 3658 M, 21 % more.
   * Measured on points: both explicit families give `ψ² = ±d` and
     `log₂(l)/2`-bit coefficients.
2. **4-D needs CM, and at `p = 2^127 − 1` nothing found beats FourQ.**
   * Of 909 discriminants, 6 give a twist of small cofactor; FourQ is one of
     them.
   * Its own pair (2, 5) is the cheapest 4-D configuration on its curve.
     The others on it cost 3040–3076 M.
   * The nearest rival, `D = −212`, costs 3050 M, +0.7 % and inside the
     lattice-sampling noise: one coefficient bit is worth about 37 M. It has
     `4 ∤ #E`, so no `a = −1` Edwards model, and in Weierstrass form it
     costs 3601 M against FourQ's 3580.
   * `D = −840` costs +1.6 % with a 243-bit `n`. The other three have no
     second cheap map.
3. **What it would take (modelled).**
   * In this model FourQ's maps cost 251 M of 3028. Beyond the maps, the
     model rebuilds a table per generator when a map is dear, which costs
     another ~276 M.
   * The floor with essentially free maps, the GLV+GLS `j = 0` shape, is
     2525 M, 17 % below FourQ. That is the most any 4-D elliptic
     construction over `F_{p²}` of this size can gain in this model.
   * To get there a Q-curve would need maps costing a few M₂ each, and two
     independent cheap ideals in the class of `𝔭` at a fixed fast prime;
     only 6 of 909 discriminants even reach a small cofactor.
   * The direct Weierstrass-model `ψ` measured here costs 26 M (degree 2)
     and 35 M (degree 3) projective-equivalent. `fourq.py`'s transcription
     of FourQ's maps through the Edwards↔Weierstrass conversions costs 169
     and 211 M; the FourQ paper's own formulas are cheaper (figure
     **unverified**).
   * So the remaining room is engineering of map evaluation on one curve,
     not a new Q-curve family. More than 4 dimensions needs a different
     object, such as genus 2 over `F_{p²}` (KN-LIT-4203, 8-D GLV/GLS).
4. **Verdict for item 8:** no Smith-style Q-curve beats FourQ under the
   harness cost model. The 2-D families lose by 26–30 %. The CM 4-D
   candidates at `p = 2^127 − 1` with `|D| ≤ 3000` are FourQ itself or up to
   1.6 % worse, and the closest lacks an Edwards model.

## Scope

* Operation counts and exact arithmetic, not timings. The cost model's
  table strategy (one table per generator, rebuilt or mapped) is the
  harness's. FourQ's implementation uses its own table layout, so absolute
  figures are model figures; the comparisons share one model.
* Item 7 tests necessary conditions only: rational `J[2]` and `16·prime`.
  The squared-theta-constant condition and `φ` on Kummer coordinates are
  open.
* The CM sweep covers `|D| ≤ 3000`, cofactors up to 4096, and ideal norms up
  to 61 in the class of `𝔭`. A larger `|D|` makes the smallest class norms
  grow, so the maps get dearer.
* No ledger, knowledge or coordination record was created or changed.

## Files

| file | what |
|:--|:--|
| `rm_kummer.json` | item 7: survey counts for the RM family and both controls, Wilson intervals, 2-adic histograms, inert-prime scan, PARI spot checks, explicit-`φ` verifications, hit examples, the ceiling table |
| `rm_kummer.md` | item 7 report generated from the JSON |
| `qcurves.json` | item 8: FourQ rows, `ψ`-alone rows, GLV+GLS row, the CM sweep (funnel, every candidate, its 4-D pairs, the FourQ eigenvalue cross-check), and the explicit curves with their checks and operation counts |
| `qcurves.md` | item 8 report generated from the JSON |
| `SHA256SUMS` | hashes of the two JSON files |

Code: `harness/endosweep/rmkummer.py` and `harness/endosweep/qcurves.py`.
Tests: `tests/test_endosweep_rm_qcurves.py`.
