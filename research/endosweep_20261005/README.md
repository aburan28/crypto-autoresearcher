# Endomorphism-ring sweep for scalar-multiplication speed-ups

Exploratory tooling and sweeps, 5 October 2026. Repository
`aburan28/crypto-autoresearcher`. **Status: a sweeper with certificates, a
modelled ranking, an explicit builder that constructs and verifies the
endomorphisms it predicts, a pass over the whole standardized-curve corpus,
FourQ verified with its real maps, the genus-2 route modelled, and the
CryptoPro-B chain measured natively (1.25× median / 1.34× min, §9). No
ledger record is created or changed and no hypothesis moves; every number
here is an operation count under the stated model except the timings quoted
in §9 from the `crypto` repository's benchmark record.**

**Question (user, 2026-10-05).** Beyond the obvious constructions (Frobenius
expansions, GLV, GLS), are there algorithmically discoverable endomorphism-based
scalar-multiplication speed-ups — "complex, high-order" endomorphisms that
nobody has written down — and can a sweeper find them? Follow-up: a speed-up
was found by hand on the Russian GOST CryptoPro-B curve (CM discriminant −619,
minimum endomorphism degree 155); how is finding things like that automated?
Second follow-up: do every item on the follow-up list, end to end.

**Answer in one paragraph.** The sweeper (`harness/endosweep/`, 2 500 lines,
25 tests) enumerates every way an endomorphism ring can shorten a
variable-base scalar multiplication, reduces each candidate's relation lattice
exactly, costs it under one explicit operation-count table, labels what it
reproduces from the literature, and then constructs the winning endomorphism
on the real curve and verifies it on points. Run over the **248-curve
std-curves corpus** it verifies all 171 prime-field curves from their constants
(zero failures), certifies 113 of them free of any endomorphism of degree below
500 000, finds 58 with a small CM discriminant, agrees with the database's
independently computed CM data in all 117 cases where it exists, and **builds
and verifies on points the cheapest chain endomorphism of every one of the
58** — among them the user's CryptoPro-B result (`4+ω`, degree `5²·7`, 1.45×
modelled), its 384-bit sibling Tom-384 (same field, 1.50×), Tom-256 (class
number 12, a `5·11³` chain, 1.42×), Tom-521 (class number 24, a `7·11³` chain,
1.52×), the five MNT families (class numbers 1–3, chains of 5, 7, 11), and the
GOST 2001 test set (class number 8, `3·7·11`). FourQ is verified with the
authors' actual endomorphism formulas (CM discriminant −40 derived from the
trace; `ψ² = 32`, `φ² = −80` on the subgroup; 61-bit four-dimensional
coefficients; 1.84× modelled). The genus-2 route is modelled with counted
Cantor arithmetic and proved at toy scale: the ζ₅ power basis gives 2.46× and
the ζ₅ × Frobenius box over `F_{p²}` reproduces the 8-dimensional
Bos–Costello–Hisil–Lauter decomposition at 3.03×, while the sweep correctly
refuses the same box on the ζ₈ family because `i ∈ Z[ζ₈]`. Nothing the sweep
generated beats the literature's constructions on the targets where those
apply; what it adds is the certificate on the clean curves and the
construction on the class-number-above-one curves, where the cheapest
endomorphism is a chain through the class group and is not the obvious one.

## 1. What was built

| file | role |
|---|---|
| `harness/endosweep/quadorder.py` | exact arithmetic in imaginary quadratic orders; discriminant certificate without factoring; elements of a given norm; class order of a prime ideal by form composition; Cornacchia for the generator of its first principal power |
| `harness/endosweep/lattice.py` | exact LLL over rationals, relation lattice, Babai decomposition with a provable coefficient bound |
| `harness/endosweep/costmodel.py` | one table of constants (EFD curve-operation counts, the same over `F_{p²}`, SIDH-literature x-only isogeny-step counts, two genus-2 Jacobian models — one measured, one marked as an assumption), interleaved width-w NAF multi-scalar cost |
| `harness/endosweep/targets.py` | 18 deployed curves verified from their constants alone; structural G2 entries; synthetic GLS and CM families; FourQ and synthetic genus-2 targets |
| `harness/endosweep/sweep.py` | catalogue (inventory to 8× the minimum non-scalar degree, composite degrees priced as chains) → configurations (GLV pairs, pump boxes, Frobenius boxes, ζ₅/ζ₈ power bases, ζ-powers × Frobenius boxes) → exact reduction → cost → ranking → report |
| `harness/endosweep/explicit.py` | builds a predicted chain endomorphism on the real curve: division polynomials (python-flint or pure Python), kernel polynomials by factoring (`ℓ ≤ 7`), by the Frobenius-eigenvalue gcd (larger `ℓ`) or as rational 2-torsion roots (`ℓ = 2`), Kohel-form Vélu, dual-aware closed-walk search, AMM roots for the isomorphism back, eigenvalue acceptance on a point of prime order, end-to-end GLV-2 check |
| `harness/endosweep/corpus.py` | the std-curves corpus: verification, certificate, cross-check against the database's `cm_disc`/`conductor`, inventory, ranking and explicit construction for every small-discriminant curve |
| `harness/endosweep/fourq.py` | FourQ: `F_{p²}` arithmetic, the twisted Edwards curve, the maps `τ, τ̂, δ, δ⁻¹, φ_W, ψ_W` from the authors' Magma script, parameter and generator verification, relations and eigenvalues found by search, 4-dim decomposition on points |
| `harness/endosweep/genus2.py` | genus-2 Jacobians: counted affine Cantor arithmetic, ζ₅/ζ₈ on Mumford divisors, zeta-function group order at toy size, toy proof of the rank-4 decomposition, measured counts into the cost table, synthetic 128-bit targets |
| `harness/endosweep/toyverify.py` | the same objects with explicit kernel points on toy curves; `cm_curve_from_class_polynomial` for any-size CM curves from a Hilbert class polynomial |
| `tests/test_endosweep.py` | 25 tests (~14 s): algebra against brute force, lattice bounds, registry typo rejection, sweep regressions, toy maps, flint/pure-Python parity, the CryptoPro-B `5²·7` and `5·31` chains, 2-isogeny chains on a 256-bit class-number-3 curve, FourQ, genus 2, corpus ingestion |
| `sweep/sweep.md`, `sweep/sweep.json`, `TABLES.md` | the full sweep (42 targets, every configuration) and its five headline tables, generated from the JSON by `make_tables.py` |
| `corpus/corpus.md`, `corpus/corpus.json` | the 248-curve corpus pass |
| `cryptopro_b_chain_5_5_7.json`, `cryptopro_b_chain_5_5_7.constants.json`, `cryptopro_b_chain_5_31.constants.json` | the two CryptoPro-B chains with kernel polynomials, rational-map polynomials, isomorphism, eigenvalue, GLV basis and test vectors (frozen input of the native experiment); `emit_rust_constants.py` renders them as a Rust module |
| `toyverify_26bit.json` | the toy explicit-map verification record |

The theory the sweep is built on, the enumeration it performs, and the
reason √élu was not implemented are in `harness/endosweep/README.md`.

## 2. Certificates on the registry targets (Table 1 of `TABLES.md`)

* **Thirteen deployed prime-field curves** (P-256, P-384, P-521,
  brainpoolP256r1, SM2, GOST CryptoPro-A, GOST CryptoPro-C, Curve25519, Ed448,
  Curve1174, Curve41417, E-521, M-511) have `|D_K| > 2 000 000`, certified by
  one exact perfect-square test per fundamental discriminant below the bound,
  with no factoring of `t² − 4q`: no endomorphism of degree below 500 000, so
  no cheap one, so the generic decomposition only.
* **secp256k1, BN254 G1, BLS12-381 G1** have `D_K = −3`; ζ₃ wins at 1.50×.
* **GOST CryptoPro-B** (`D_K = −619`, `h = 5`) and the **GOST 2001 test set**
  (`D_K = −915`, `h = 8`): §3.
* All 18 deployed parameter sets re-verified from their constants.

## 3. CryptoPro-B, found and built automatically

The user's hand-found result, reproduced by the pipeline with nothing
curve-specific typed in beyond the RFC 4357 constants; it also closes the
repository's earlier audit notes (`research/cm_isogeny_ecdlp_ideas_200.md`,
items 20 and 40: "explicit maps and the maximal-order claim unfinished").

1. **Certificate.** `t² − 4q = −619 · f²`, `f = 4646402506017662432554672533504826433`,
   class number 5, minimum non-scalar degree `(619+1)/4 = 155 = 5·31` (that is
   `N(ω)`, `ω = (1+√−619)/2`).
2. **Inventory, priced as chains.** No endomorphism of degree 5 or 7 exists
   (the prime ideals are not principal), but a primitive element of composite
   norm is a chain through the class group costing the sum of its steps:
   `4+ω` of norm `175 = 5²·7` costs `2·(8M+2S) + (12M+2S) + 20M ≈ 53 M`, ahead
   of `ω` itself (`5·31`, 91 M) and of any prime-norm element as one map.
3. **Modelled speed-up.** GLV-2 with `4+ω`: 1681 M against 2439 M generic,
   **1.45×**. The pump box on top loses by 16.6 % (Table 2), as everywhere.
4. **Explicit construction, 1.3 s.** The 5- and 7-division polynomials have
   exactly two rational cyclic subgroups each (the `𝔭` and `𝔭̄` directions);
   of the closed walks of shape 5·5·7, two return to `j(E)` through three
   distinct neighbours; composed with the isomorphism back to `E`, one acts on
   a point of prime order as the scalar predicted for `−5+ω` (the unit-
   conjugate of `4+ω`), and `kP = k₁P + k₂φ(P)` holds with 127-bit
   coefficients. **The degree-155 element `ω` itself** is built the same way as
   a 5-isogeny followed by a 31-isogeny (the order-31 kernels come from the
   Frobenius-eigenvalue method in 0.5 s; no rational 31-torsion point exists).
5. **Maximal order.** A chain realising `ω` exists, so `End(E)` is the maximal
   order of `Q(√−619)` — settled by construction.

Both chains are exported with their rational-map polynomials as frozen
constants for the native experiment (§9).

## 4. The whole standardized corpus (`corpus/corpus.md`)

| | |
|---|---|
| curves in the std-curves database | 248 |
| prime-field curves in Weierstrass/Montgomery/Edwards form, verified from their constants | 171 (0 failures) |
| skipped (binary, extension or tower fields) | 77 |
| certified `|D_K| > 2 000 000` (no endomorphism of degree below 500 000) | 113 |
| small CM discriminant | 58 |
| cross-check against the database's own `cm_disc`/`conductor` | 117 agree, 0 disagree, 54 without database data |
| cheapest chain **built and verified on points** | 58 of 58 |

The 58 split as: 44 curves with `D_K = −3` (BN, BLS, Pallas/Vesta/Tweedle,
the SECG/X9.63/WTLS Koblitz-style `k1` curves, the `FpXXXBN` family) where ζ₃
is the answer and the sweep merely confirms it; and **14 curves with class
number above one or a non-unit minimum**, where the cheapest endomorphism is
a chain the sweep had to find:

| curve | bits | `D_K` | `h` | min degree | cheapest chain | chain M | modelled speed-up |
|---|---|---|---|---|---|---|---|
| gost/CryptoPro-B | 256 | −619 | 5 | 155 | `5²·7` | 53 | 1.45× |
| gost/gost256 (2001 test set) | 256 | −915 | 8 | 229 | `3·7·11` | 61 | 1.46× |
| other/Tom-256 | 256 | −4155 | 12 | 1039 | `5·11³` | 89 | 1.42× |
| other/Tom-384 | 384 | −619 | 5 | 155 | `5²·7` | 53 | 1.50× |
| other/Tom-521 | 521 | −28243 | 24 | 7061 | `7·11³` | 98 | 1.52× |
| mnt/mnt1 | 170 | −19 | 1 | 5 | `5` | 30 | 1.43× |
| mnt/mnt2 (×2) | 159 | −91 | 2 | 23 | `5·7` | 43 | 1.41× |
| mnt/mnt3 (×3) | 160 | −139 | 3 | 35 | `5·11` | 43 | 1.41× |
| mnt/mnt4 | 240 | −163 | 1 | 41 | `41` | 102 | 1.40× |
| mnt/mnt5 (×3) | 240 | −211 | 3 | 53 | `5³` | 49 | 1.45× |

Every one of these chains was constructed and checked on points (the
Tom-521 chain `7·11³` has degree 9317; the `11`-steps use the
Frobenius-eigenvalue kernels). The MNT curves were CM-generated with small
discriminants by construction and the literature knows they admit GLV; the
Tom curves and the two GOST sets are the ones where the sweep's chain
pricing is the difference between "a degree-7061 endomorphism, useless" and
"a 98 M chain, 1.52×". These are modelled speed-ups under `costmodel.py`;
none is a timing.

## 5. FourQ with its real maps (`fourq.py`)

Parameters and the FourQlib generator verified; `D_K = −40` from the trace by
the exact scan (`t² − 4p² = −40·f²`); the transcribed `φ` and `ψ` are
homomorphisms of `E(F_{p²})` (on-curve, additive on random points); their
quadratic relations on the prime-order subgroup, found by search, are
`ψ² = 32` and `φ² = −80` — scaled forms of `√2` and `√−5` whose product
generates `Q(√−10)`, consistent with `D_K`; the realised eigenvalues give a
four-dimensional lattice with 61-bit coefficients (ideal 61.25) that
reconstructs `kP` from explicit images. Under the model, with the maps'
affine operation counts charged as projective-equivalent (an assumption,
stated in the table), FourQ's `{1, φ, ψ, φψ}` box is 1.84× over width-w NAF
on the same curve; the FourQ paper's optimised formulas are cheaper than the
charged counts, so the real ratio is higher.

## 6. Genus 2: the rank-4 route (`genus2.py`)

Toy proof (9-bit primes): on a Buhler–Koblitz Jacobian the zeta-function
order kills random divisors, ζ₅ acts on a divisor of prime order as a
primitive 5th root of unity, and the 4-dimensional decomposition
`{1, ζ, ζ², ζ³}` reconstructs `kD` within the Babai bound; the same for ζ₈ on
a Furukawa–Kawazoe–Takahashi Jacobian. Generic affine Cantor arithmetic
measures ADD = 125 M + 5 I and DBL = 112 M + 4 I. In the sweep (128-bit `p`,
`n ≈ 2^254`): the ζ₅ power basis gives **2.46×** under the assumed projective
model (and 2.54× under the counted affine one); over `F_{p²}` with a GLS-type
`ψ` (`ψ² = −1`) the box `{ζ₅^j ψ^i}` is 8-dimensional with 32-bit coefficients,
**3.03×**, the Bos–Costello–Hisil–Lauter setting; for ζ₈ the same box is
rejected because `i = ζ₈²` makes the generators dependent (the lattice shows
unit vectors), so 4 dimensions is that pairing's ceiling. Table 5 puts the
families side by side in 64-bit word multiplications under schoolbook scaling
(an assumption, stated there): genus-2 over 128-bit `p` at 0.45× of P-256
generic, FourQ at 0.34×, the 8-dimensional genus-2 `F_{p²}` box at 0.28×, the
CryptoPro-B chain at 0.69×, secp256k1 at 0.60×. The genus-2 rows rest on
assumed Jacobian counts and are indicative only.

## 7. Free pumps and paid pumps (Tables 2–3)

Unchanged from the first pass and now confirmed on 42 targets: Frobenius
powers saturate at dimension 4 on G2 and GLS (extra generators add unit
vectors and additions); isogeny-cycle pumps buy height at
`2·cost(step)/log2 ℓ` M per bit, parity with the doublings they remove, and
lose by 8–95 % once tables and additions are charged (CryptoPro-B: 16.6 %).

## 8. Explicit verification (`toyverify_26bit.json`, tests)

Toy scale: ζ₃, the degree-7 endomorphism `2+ω` and its powers on j = 0; the
closed 3-walk of 2-isogenies on the `D = −23` curve (from its Hilbert class
polynomial, checked by point counting); the 4-dimensional pump box. Real
scale: the CryptoPro-B `5²·7` and `5·31` chains; on a 255-bit curve with
`D = −23` the `2³` cycle, the `2·3` element `ω` and the `2²·3²` element
`5+ω`, each built and verified in under a second (degree-2 steps use the
rational 2-torsion kernel; the dual is excluded by the `±[2]` test, not by
j-invariant, which is what lets a two-step walk legitimately return to `E`).

## 9. Native timing experiment (separate repository): measured

The 5·5·7 and 5·31 chains are implemented natively in Rust in the `crypto`
repository, pull request aburan28/crypto#1408 (branch
`cryptopro-b-glv-chain-20261005`, `research/cryptopro_b_glv_chain_20261005/`
there): Montgomery-form field for `p = 2^255 + 3225`, variable-time Jacobian
`a = −3` arithmetic shared by every arm, width-5 NAF baseline, the chain
evaluator as `x ↦ N(x)/ψ(x)²`, `y ↦ y·M(x)/ψ(x)³` in projective coordinates,
exact-rational Babai decomposition, interleaved 2-dimensional wNAF, 32 tests
against the exported vectors and the eigenvalue (and the full 3492-test
library suite), and a seeded, interleaved, CPU-pinned benchmark (256 pairs ×
20 rounds, alternating arm order, an A/A control arm). Its table, in
nanoseconds per scalar multiplication, median / minimum of 20 rounds, on an
Intel Xeon 2.10 GHz cloud VM:

| arm | median ns | min ns | ratio baseline/arm (median / min) | correct |
|---|---|---|---|---|
| width-5 NAF baseline | 111 158 | 107 220 | 1.000 / 1.000 | == textbook reference on all 256 pairs |
| GLV-2 via the `5·5·7` chain (`4+ω`, degree 175) | 88 759 | 80 199 | **1.252 / 1.337** | == baseline on all 256 pairs |
| GLV-2 via the `5·31` chain (`ω`, degree 155) | 91 799 | 84 544 | 1.211 / 1.268 | == baseline on all 256 pairs |
| A/A control (baseline timed again) | 118 769 | 108 890 | 0.936 / 0.985 | noise floor |

Stage diagnostics: decomposition ≈ 1.0 µs (about 1 % of the GLV total,
num-bigint), `φ(P)` ≈ 4.3 µs for the `5·5·7` chain and ≈ 9.5 µs for `5·31`.
The declared success condition (ratio above 1 on both medians and minima
with every correctness check passing) is met; the result is classed
**engineering** (same problem, constant factor) per that repository's rules.
It is **short of the modelled 1.45×**: the record reconciles the gap with a
formula-derived count for that implementation — the projective chain costs
about 128 M against the model's 53 M affine form, the Fermat inversion is
shared, and the GLV arm pays a second table and a larger batch — which puts
the implementation's own expected ratio near 1.30, where the measurement
sits. One host, one hardware class, variable-time code: a measurement of
this implementation, not a bound on what an optimised one would reach.

## 10. Limits

* Costs are operation counts under `costmodel.py`; the genus-2 projective
  counts and the FourQ endomorphism charges are assumptions marked as such.
* The corpus's binary-field, extension-field and tower-field curves (77) are
  outside the prime-field pipeline.
* 32 random scalars per lattice for the empirical coefficient size; the
  Babai bound is provable and reported alongside.
* Security is not assessed anywhere here; a cheap endomorphism acts on the
  prime-order subgroup as a scalar and adds nothing beyond the automorphism
  group to an attacker (H-ENDO-001's standing argument).

## 11. Reproduce

```sh
pip install python-flint                      # optional, used when present
python -m pytest -q tests/test_endosweep.py
python -m harness.endosweep --out-dir research/endosweep_20261005/sweep
python3 research/endosweep_20261005/make_tables.py > research/endosweep_20261005/TABLES.md
git clone --depth 1 https://github.com/J08nY/std-curves /tmp/std-curves
python -m harness.endosweep.corpus --std-curves /tmp/std-curves --out-dir research/endosweep_20261005/corpus --explicit-max-prime 47
python -m harness.endosweep.explicit --target "GOST CryptoPro-B" --out research/endosweep_20261005/cryptopro_b_chain_5_5_7.json
python3 research/endosweep_20261005/export_chain_constants.py --element 4,1 --out research/endosweep_20261005/cryptopro_b_chain_5_5_7.constants.json
python3 research/endosweep_20261005/export_chain_constants.py --element 0,1 --out research/endosweep_20261005/cryptopro_b_chain_5_31.constants.json
python3 research/endosweep_20261005/emit_rust_constants.py research/endosweep_20261005/cryptopro_b_chain_5_5_7.constants.json research/endosweep_20261005/cryptopro_b_chain_5_31.constants.json > cryptopro_b_chain_consts.rs
python -m harness.endosweep.fourq
python -m harness.endosweep.genus2 --bits 9
python -m harness.endosweep.toyverify --bits 26 --out research/endosweep_20261005/toyverify_26bit.json
```
