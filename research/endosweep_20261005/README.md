# Endomorphism-ring sweep for scalar-multiplication speed-ups

Exploratory tooling and a first sweep, 5 October 2026. Repository
`aburan28/crypto-autoresearcher`. **Status: a sweeper with certificates, a
modelled ranking, and one deployed-curve endomorphism constructed and verified
on points. No ledger record is created or changed, no hypothesis moves, and no
number below is a measured timing.**

**Question (user, 2026-10-05).** Beyond the obvious constructions (Frobenius
expansions, GLV, GLS), are there algorithmically discoverable endomorphism-based
scalar-multiplication speed-ups — "complex, high-order" endomorphisms that
nobody has written down — and can a sweeper find them? Follow-up: a speed-up was
found by hand on the Russian GOST CryptoPro-B curve (CM discriminant −619,
minimum endomorphism degree 155); how is finding things like that automated?

**Answer in one paragraph.** The sweeper (`harness/endosweep/`) enumerates every
way an endomorphism ring can shorten a variable-base scalar multiplication on
35 target groups, reduces each candidate's relation lattice exactly, costs it
under one explicit operation-count table, and — new in the second pass —
constructs the winning endomorphism on the real curve and verifies it on points.
Thirteen of the eighteen deployed curves carry a certificate that no non-scalar
endomorphism of degree below 500 000 exists. Three (secp256k1, BN254 G1,
BLS12-381 G1) have the textbook ζ₃ GLV. **Two have a small CM discriminant with
class number above one: GOST CryptoPro-B (D_K = −619, h = 5) and the GOST 2001
test curve (D_K = −915, h = 8).** On CryptoPro-B the sweep finds, unaided, that
the cheapest endomorphism is not the degree-155 element ω but 4+ω of degree
5²·7 = 175, evaluated as a chain of two 5-isogenies and one 7-isogeny through
the class group at about 53 M, worth a modelled 1.45× over width-w NAF; the
chain is then built explicitly (division polynomials, Kohel-form Vélu, closed
walk back to j(E)), acts on a point of prime order as the predicted scalar, and
reconstructs kP with 127-bit coefficients, all in 1.3 s. Everything else the
sweep generated — isogeny-cycle pumps up to dimension 8, Frobenius-power boxes
up to dimension 8 — reproduces the literature or loses to it, because the
coefficient size of any decomposition is bounded below by
`(log2 n)/rank − log2 height − log2 dimension`, height is paid for in isogeny
degree at parity with the doublings it removes, and Frobenius is the only free
height.

## 1. What was built

| file | role |
|---|---|
| `harness/endosweep/quadorder.py` | exact arithmetic in imaginary quadratic orders; discriminant certificate without factoring; elements of a given norm; class order of a prime ideal by form composition; Cornacchia for the generator of its first principal power |
| `harness/endosweep/lattice.py` | exact LLL over rationals, relation lattice, Babai decomposition with a provable coefficient bound |
| `harness/endosweep/costmodel.py` | one table of constants (EFD curve-operation counts, SIDH x-only isogeny-step counts, marked assumptions), interleaved width-w NAF multi-scalar cost |
| `harness/endosweep/targets.py` | 18 deployed curves verified from their constants alone; structural G2 entries; synthetic GLS and CM families |
| `harness/endosweep/sweep.py` | catalogue (inventory reaches 8× the minimum non-scalar degree, composite degrees priced as isogeny chains) → configurations → exact reduction → cost → ranking → report |
| `harness/endosweep/explicit.py` | **builds a predicted chain endomorphism on the real curve**: division polynomials, rational kernel polynomials by factoring over F_p, Vélu in Kohel's kernel-polynomial form (no kernel point needed), closed-walk search through the isogeny class, eigenvalue check on a point of prime order, end-to-end GLV-2 check |
| `harness/endosweep/toyverify.py` | the same objects built with explicit kernel points on toy curves |
| `tests/test_endosweep.py` | 19 tests (~2 s), including the CryptoPro-B chain |
| `sweep/sweep.md`, `sweep/sweep.json` | the full sweep output (35 targets, every configuration) |
| `TABLES.md` | the four headline tables, generated from the JSON by `make_tables.py` |
| `cryptopro_b_chain_5_5_7.json` | the CryptoPro-B endomorphism: intermediate curves, j-walk, eigenvalue, GLV check |
| `toyverify_26bit.json` | the toy explicit-map verification record |

The theory the sweep is built on, and the enumeration it performs, are written
out in `harness/endosweep/README.md`.

## 2. Certificates (Table 1 of `TABLES.md`)

* **Thirteen deployed prime-field curves** (P-256, P-384, P-521,
  brainpoolP256r1, SM2, GOST CryptoPro-A, GOST CryptoPro-C, Curve25519, Ed448,
  Curve1174, Curve41417, E-521, M-511) have `|D_K| > 2 000 000`, certified by
  one exact perfect-square test per fundamental discriminant below the bound,
  with no factoring of `t² − 4q`. Every non-scalar endomorphism of an order of
  discriminant `D_K` has degree at least `|D_K|/4`, so none of these curves has
  an endomorphism of degree below 500 000, hence no cheap one; their only
  decomposition is the generic one.
* **secp256k1, BN254 G1, BLS12-381 G1** have `D_K = −3`; every primitive
  endomorphism up to the inventory bound produces the same 128-bit
  two-dimensional lattice as ζ₃ (rank 2 cannot do better), so ζ₃ wins on cost:
  1.50× under the model.
* **GOST CryptoPro-B** has `t² − 4q = −619 · f²` with
  `f = 4646402506017662432554672533504826433`, class number 5; **the GOST 2001
  test curve** has `D_K = −915`, class number 8. Both are treated in §3.
* All 18 deployed parameter sets were re-verified from their constants (prime
  `n`, Hasse interval, a point of order divisible by `n` killed by `h·n`), so a
  typo would have excluded a curve rather than coloured a conclusion.

## 3. A real one: GOST CryptoPro-B, found and built automatically

This is the finding the user made by hand, reproduced by the pipeline with
nothing curve-specific typed in beyond the RFC 4357 constants. The repository's
earlier audit notes (`research/cm_isogeny_ecdlp_ideas_200.md`, items 20 and
40) recorded `D_K = −619, h = 5` with "explicit maps and the maximal-order claim
unfinished"; both are now finished constructively.

1. **Certificate.** `small_discriminant_scan` finds `−619` at once (one
   perfect-square test per fundamental discriminant; no factoring). Minimum
   non-scalar degree `(619+1)/4 = 155 = 5·31`, which is `N(ω)` for
   `ω = (1+√−619)/2`.
2. **Inventory, priced as chains.** Because `h(−619) = 5`, the prime ideals
   above 5, 7, 23, 31, … are not principal and no endomorphism of degree 5 or 7
   exists; but a primitive element of composite norm `∏ ℓ^e` generates
   `∏ 𝔭_ℓ^e`, i.e. a chain of `ℓ`-isogenies through neighbouring curves that
   ends back at `E`. Its cost is the sum of the step costs, so the ranking is
   not by degree: `4+ω` of norm `175 = 5²·7` costs `2·(8M+2S) + (12M+2S) + 20M
   ≈ 53 M`, ahead of `9+ω` (`5·7²`, 57 M) and far ahead of `ω` itself
   (`5·31`, 91 M) or the prime-norm element `1+ω` (157, 333 M as one Vélu map).
3. **Modelled speed-up.** GLV-2 with `4+ω`: 1681 M against 2439 M generic,
   **1.45×** (Table 1) — the same shape as the 1.50× of secp256k1 minus the
   chain cost. The isogeny-cycle pump box on top of it loses by 16.6 %
   (Table 2), as on every other target.
4. **Explicit construction** (`explicit.py`, 1.3 s). The 5-division
   polynomial factors over `F_p` with degrees `1,1,2,4,4` and the 7-division
   polynomial with degrees `3,3,6,6,6`: exactly two rational cyclic subgroups
   of each order, the `𝔭` and `𝔭̄` directions (the two linear factors together
   form one order-5 kernel whose x-coordinates are rational although the points
   are not). Vélu in Kohel's form needs only those kernel polynomials. Of the
   closed walks of shape 5·5·7 with no immediate backtracking, two return to
   `j(E)` through three distinct neighbouring j-invariants; composed with the
   isomorphism back to `E`, one of them acts on a point of prime order `n` as
   the scalar predicted for `−5+ω` (the unit-conjugate of `4+ω`, as it must be
   up to the choice of root), and `kP = k₁P + k₂φ(P)` holds for random `k` with
   both coefficients at most 127 bits (Babai bound 128).
5. **Maximal order.** A chain realising `ω` exists, so `ω ∈ End(E)` and
   `End(E)` is the maximal order of `Q(√−619)`: the earlier "maximal-order
   claim" is settled by construction, not by Kohel's algorithm on the 121-bit
   conductor.

The GOST 2001 test parameter set (`D_K = −915`, `h = 8`) goes the same way on
paper (`1+ω`, degree `3·7·11`, 1.46×); it is a test vector, not a deployed
curve, and its chain was not built.

Security remark, because the question will be asked: a cheap endomorphism of
`E` acts on the prime-order subgroup as a scalar and adds no congruence an
attacker can use beyond the automorphism group, which is `±1` here (this is
H-ENDO-001's standing argument in the ENDO campaign). Nothing in this
directory changes that assessment.

## 4. Free pumps reproduce the literature and saturate at dimension 4 (Table 3)

On BLS12-381 G2 and BN254 G2 the Galbraith–Scott basis `{1, ψ, ψ², ψ³}` gives
64-bit coefficients (ideal 63.5) and 1.89×; the box `{1, ζ₃} × {1, ψ}` is the same
lattice with one fewer ψ to apply, 1.96×. Adding more Frobenius powers
(dimensions 5–8) does not reduce a single coefficient bit — the reduced basis
acquires vectors of ∞-norm 1, i.e. the extra generator is a small integer
combination of the others — while the additions grow, so dimension 8 is back
at 1.20×. `{1, ψ}` alone on BLS12-381 G2 is nearly useless (191-bit coefficient,
1.04×) because `λ_ψ = x` is a 64-bit seed. The synthetic GLS group over
`F_{p²}`, `p ≈ 2^127`, reproduces Longa–Sica 4-GLV at 2.26×. All of this is
known; it is the calibration that makes the negative results credible.

## 5. Paid pumps: parity by construction, loss in practice (Table 2)

An **isogeny-cycle pump** is the generator of the first principal power of a
split prime `ℓ` (a closed walk of `k = ord[𝔩]` steps on the `ℓ`-isogeny graph)
raised to a power so that its height is about `n^{1/4}`; with a free or cheap
generator `u` the box `{1, u, α, uα}` is a genuine four-dimensional
decomposition (verified on toy curves, §6) with 63–64-bit coefficients on a
256-bit group. The price per bit of height, from the step counts in
`costmodel.py`:

| step | count | M per bit of height |
|---|---|---|
| 2-isogeny | 4M | 8.0 |
| 3-isogeny | 4M + 2S | 7.1 |
| 4-isogeny | 6M + 2S | 7.6 |
| 5-isogeny | 8M + 2S | 8.3 |
| 7-isogeny | 12M + 2S | 9.7 |
| doubling (a = 0 / a = −3 / generic a) | — | 6.0 / 7.0 / 7.4 |

The best possible pump, a 3-isogeny chain where 3 splits, is at parity with the
doublings it removes: on the synthetic `D = −8` curve the pump costs 462 M and
removes 62 doublings worth 459 M, and the configuration still loses by 8.6 %
because four scalars need more additions and tables than two. Across all 20
targets that have a pump the loss runs from 8.0 % to 95 %; for a 3-isogeny pump
to break even on a generic-a curve a step would have to cost about 3.7 M
instead of 5.6 M. The sweep labels these boxes "no literature match found";
the author did not find the construction in print, and the result is negative
in any case.

## 6. Explicit verification at toy scale (`toyverify_26bit.json`)

On a j = 0 curve over a 26-bit prime with rational 7-torsion, and on a curve with
CM by the class-number-3 order of `Q(√−23)` from its Hilbert class polynomial
(checked by naive point counting at four primes): ζ₃ acts as a predicted root;
the degree-7 endomorphism `2+ω` from Vélu and an isomorphism acts as
`a + bλ_ω`; its powers act as predicted with the predicted height; the box
`{1, ζ, α^j, ζα^j}` reconstructs kP for 8 random k within the Babai bound; the
closed 3-walk of 2-isogenies on the `D = −23` curve is an endomorphism of degree
8 with the eigenvalue of `1+ω`, and its cube acts as predicted. The
kernel-polynomial Vélu of `explicit.py` agrees with the point-based Vélu on the
same toy curve (test).

## 7. What this says about the original question, and how the finding is automated

* The lever that creates new dimensions on an elliptic curve is **free
  height**, and the only free height is Frobenius over an extension field;
  everything in that direction is known and reproduced here.
* **Paid height is at parity with doublings** per bit, so no isogeny-built
  endomorphism of high degree or order beats GLV by more than the constant
  factor of the step formulas, which is currently negative.
* **What is automatable is the CryptoPro-B kind of result**, and it is now
  automated end to end: registry constants → discriminant certificate
  (`|D_K|` small or provably not) → inventory of primitive elements up to a
  multiple of the minimum degree, priced as chains through the class group →
  exact lattice and cost ranking → explicit construction by factoring
  division polynomials and walking the isogeny class → eigenvalue and
  decomposition verified on points. One command per curve
  (`python -m harness.endosweep.explicit --target NAME`), ~1 s at 256 bits for
  chains of small primes. The two curves the sweep flags among the eighteen
  standardized ones are exactly the two that were CM-generated with a small
  class-number field.
* **Higher rank** (genus-2 Jacobians with quartic CM) remains the only route
  to higher-dimensional decompositions with free generators; it is outside
  this sweep.

## 8. Limits of this work

* Costs are operation counts under `costmodel.py`; the 1.45× for CryptoPro-B is
  modelled, and the chain is evaluated here in affine Kohel form in Python,
  not as an optimised implementation. A projective evaluation of the 5-5-7
  chain in a real library is the measurement that would settle the number.
* `explicit.py` handles odd-prime steps; degree-2 steps in kernel-polynomial
  form and √élu-style evaluation of large prime steps are not implemented.
* The synthetic CM and GLS targets are structural (no curve equation); their
  security is not assessed. FourQ is not included (its eigenvalue relations
  were not re-derived). Genus 2 is not swept.
* 32 random scalars per lattice for the empirical coefficient size; the Babai
  bound is provable and reported alongside.

## 9. Reproduce

```sh
python -m pytest -q tests/test_endosweep.py
python -m harness.endosweep --out-dir research/endosweep_20261005/sweep         # ~5 min
python3 research/endosweep_20261005/make_tables.py > research/endosweep_20261005/TABLES.md
python -m harness.endosweep.explicit --target "GOST CryptoPro-B" --out research/endosweep_20261005/cryptopro_b_chain_5_5_7.json
python -m harness.endosweep.toyverify --bits 26 --out research/endosweep_20261005/toyverify_26bit.json
```

## 10. Possible follow-ups (not started; would enter the ledger via /propose-ideas)

1. Feed every standardized curve corpus the program knows into the registry
   (the `crypto` repository's curve registry scripts, the SafeCurves and
   std-curves lists) and run the certificate over all of them; the scan is
   0.2 s per curve.
2. A native (Rust) projective implementation of the CryptoPro-B 5-5-7 chain,
   timed against width-w NAF and against the degree-155 single map, as the
   first measured experiment of this line.
3. Degree-2 steps and √élu in `explicit.py`, so chains like `2²·3²` on
   class-number-3 curves and single large-prime steps are also buildable.
4. A genus-2 Jacobian cost model and the BK/FKT families, to put the rank-4
   route on the same footing as the elliptic results.
5. FourQ as a verified target.
