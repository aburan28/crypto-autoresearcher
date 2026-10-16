# Native chain sets: Bandersnatch, Tom-384 and CP6-782 G1

**Purpose.** `research/endosweep_curves_20261006` modelled GLV-2 with a cheap
isogeny-chain endomorphism on every curve with a small CM discriminant. Only
GOST CryptoPro-B has been measured natively (aburan28/crypto#1423: 1.408×
counted, 1.417× median wall time against the best width-w NAF). Finding 5
there names the next three native measurements: Tom-384 (modelled 1.525),
Bandersnatch (1.522, on its short Weierstrass model) and CP6-782 G1 (1.494).
This directory holds their frozen inputs. Each curve gets a chain set in the
same `endosweep-chainsweep/1` format as
[`../endosweep_chainsweep_20261006/chains.constants.json`](../endosweep_chainsweep_20261006/chains.constants.json),
plus the scalar-multiplication count model priced with that curve's own
arithmetic. The native harness that measures them is in the crypto
repository (branch `endo-native-bench-20261016`), not here.

**No timing is produced in this directory.** The chain operation counts are
exact for the evaluators they mirror. The scalar-multiplication counts are
model expectations over 400 seeded random scalars, not measurements. This is
scalar-multiplication engineering (constant factors). It is not an attack and
not a security claim.

## Curves

| file prefix | curve (database entry) | p bits | n bits | cofactor h | D_K | h(D_K) | doubling priced as | generator |
|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `bandersnatch` | Bandersnatch, **short Weierstrass model** (`arkworks/ed_on_bls12_381_bandersnatch`) | 255 | 253 | 4 | −8 | 1 | general `a`: dbl-2007-bl 1M + 8S + 1M for `a` | arkworks' SW generator |
| `tom384` | Tom-384 (`other/Tom-384`, std-curves) | 384 | 384 | 1 | −619 | 5 | general `a`: 1M + 8S + 1M | none in the database; `point_of_order(E, n, 1, seed=2)` |
| `cp6_782` | CP6-782 `G1` (`arkworks/cp6_782`) | 782 | 377 | ≈ 2^405.1 (h·n ≈ p) | −339 | 6 | small `a = 5`: dbl-2007-bl 1M + 8S (the product by 5 is additions, not counted) | arkworks' generator |

* **Bandersnatch is measured on its short Weierstrass model** (the model the
  sweep priced). These are arkworks' SW constants. They are identical to the
  conversion of std-curves `bls/Bandersnatch` from its twisted-Edwards form
  (checked: same `a`, `b`, `n`, `h`). The deployed twisted-Edwards arithmetic
  of Bandersnatch is **not** what is modelled or measured.
* **CP6-782 `G1`** has `n` much smaller than `p`, so `n < 4√p` and the
  cofactor `h` is large. The generator and every test point are in the
  order-`n` subgroup: test points are lifted and multiplied by `h`, and the
  tests check `n·P = O` for every one. A native harness must clear the
  cofactor in the same way.
* Every curve file carries a `curve` block with its source, its trace `t`
  and conductor `f` (`t² − 4p = D_K·f²`, `p + 1 − t = h·n`), `ω`'s trace
  and norm, the generator `G`, and the arithmetic (`dbl`, `add`, `madd`,
  `inv` in (M, S)) that the model uses. The arithmetic is
  `curvesweep.arithmetic`; the Fermat inversion costs `popcount(p−2)` M plus
  `bitlen(p−2)` S.

## Results

| curve | catalogue (elements / orderings, all built and verified) | cheapest chain | optimised / generic M_eq | exported orderings (≤ 2× cheapest) | file size |
|:--|:--|:--|--:|--:|--:|
| Bandersnatch | 2 / 2 | `ω = √−2` as one 2-step (`0+1w/2`); also `1 + ω` as one 3-step, 6 M_eq too | **6** / 10 | 2 | 9 KB |
| Tom-384 | 11 / 34 | `4 + ω` as `7·5·5` (`4+1w/7.5.5`) | **80** / 128 | 22 (11 elements) | 280 KB |
| CP6-782 G1 | 18 / 106 | `4 + ω` as `7·3·5` (`4+1w/7.3.5`), norm 105 | **65** / 113 | 57 (18 elements) | 1.16 MB |

Expected totals of the native arms (the model, not a measurement; `M_eq = M + S`
per `k·P`, 400 seeded scalars, decomposition not included):

| curve | best baseline (width-w NAF) | best GLV-2 (cheapest chain) | modelled ratio | curves.json ratio (200 scalars) |
|:--|:--|:--|--:|--:|
| Bandersnatch | jacobian/w5: 3 285.3 | optimised/jacobian/w5: 2 157.6 | **1.523** | 1.522 |
| Tom-384 | jacobian/w6: 4 930.5 | optimised/jacobian/w5: 3 234.6 | **1.524** | 1.525 |
| CP6-782 G1 | jacobian/w6: 4 463.9 | optimised/jacobian/w5: 2 987.6 | **1.494** | 1.494 |

Every arm in the grid (baseline w 3..7 with affine and Jacobian tables; every
exported chain × {generic, optimised} × {affine, jacobian} × w 3..7) is in
`<curve>.model.json`. The per-curve reports are `<curve>.catalogue.md`.

Findings:

1. **Tom-384's chain set matches CryptoPro-B's element for element.** Both
   curves have `D_K = −619`. The cheapest-to-2× sets have the same 11
   elements, the same 22 orderings and the same counts (80 M_eq for
   `4 + ω` as `7·5·5`). The curves differ only in the field size and in
   `a`: Tom-384's `a` is general, so it pays 2M + 8S per doubling against
   CryptoPro-B's 3M + 5S.
2. **Bandersnatch's endomorphism is a single step.** Both `√−2` (a 2-isogeny,
   Velu) and `1 + √−2` (a 3-isogeny) cost 6 M_eq, ⅓ of a doubling. The
   model's GLV totals for the two differ by only 0.4 M_eq. That gap comes
   from the lattice bases, not the chain.
3. **CP6-782's cheapest chain is cheaper than Tom-384's (65 against 80), but
   the modelled ratio is lower (1.494 against 1.524).** CP6-782's subgroup
   is only 377 bits, and its doubling is cheaper (`a = 5`, 1M + 8S). So the
   fixed cost of the chain and the tables is a larger share of a shorter
   scalar multiplication.

## Format (`endosweep-chainsweep/1`) and what is new in it

The format is exactly that of the CryptoPro-B file. Each chain is a list of
steps. Each step gives its domain and codomain `(a, b)` and the monic Kohel-form
polynomials `ψ`, `N`, `M`, low degree first, with `x′ = N/ψ²` and
`y′ = y·M/ψ³`. After the steps, `(x, y) ↦ (u²x, u³y)` with `isomorphism_u`
maps back to `E`. Each chain also records the eigenvalue `λ`, the reduced
GLV basis, the model's chain counts and two test vectors
(`P`, `φ(P) = λP`, `k`, `k₁`, `k₂`, `kP`). Three things are added for
these curves; none of them appears in the CryptoPro-B file:

* a top-level `curve` block (described above);
* **2-steps** (Bandersnatch). For a 2-step, `ψ = x − x₀` has degree 1 and `N`
  and `M` have degree 3. A 2-step also carries `velu2: {x0, v}` with
  `v = 3x₀² + a`. The counted evaluator is Velu in Jacobian coordinates:
  `d = X − x₀Z²`, `X′ = (Xd + vZ⁴)d`, `Y′ = Y(d² − vZ⁴)d`, `Z′ = Zd`. That
  costs 7M + 3S, or 4M + 1S on an affine input. This is the same formula
  `curvesweep` counts, and it is the homogenisation of the exported `N`, `ψ`
  and `M`, so a generic Kohel evaluator gives the same point;
* for `D ≡ 0 (mod 4)` (Bandersnatch), `ω = √(D/4) = √−2`. The note on
  `omega_root` says so.

## Completeness

The catalogue is `curvesweep.complete_catalogue` (`--catalogue cost`), not
CryptoPro-B's norm-bounded one:

1. a norm-bounded seed catalogue gives a first cheapest cost `c₀`;
2. every realizable multiset of step degrees whose cheapest ordering costs
   at most `2c₀` is enumerated, together with every primitive element of
   each product norm. Realizable means split primes with any multiplicity,
   ramified primes at most once, and no inert primes.

So the catalogue contains every element whose cheapest chain is within 2× of
the cheapest. Every ordering of every such element is built, and every
ordering within the limit is exported. In each file,
`bounds.cost_complete` records this, and `bounds.outside_lower_bound` keeps
the norm- and step-bounded bound for the largest norm and step in the
catalogue, for context only.

## Verification

* The harness builds every ordering on the curve and verifies it on points:
  the walk closes, the map acts as the predicted scalar on a point of order
  `n`, and a GLV-2 reconstruction succeeds. All orderings passed: **2 of 2,
  34 of 34 and 106 of 106**. Every ordering of one element acts as the same
  scalar up to sign.
* `tests/test_endosweep_native_chains.py` (14 tests) re-checks every exported
  constant from the JSON alone, without using the harness's isogeny objects.
  It checks:
  * the curve-level identities;
  * `G` and every `P`: on the curve and of order `n`;
  * the chain evaluated from its `ψ`, `N`, `M` and `u`, which must equal
    `φ(P)` and `λ·P`;
  * `λ` as a root of the characteristic polynomial;
  * the norm, the step product, and that the walk is closed;
  * the GLV basis, its determinant ±n, and that it is LLL-reduced as
    `lattice.reduce` reduces it;
  * `k ≡ k₁ + k₂λ`, and `kP = k₁P + k₂φ(P)` by full scalar multiplications;
  * the model's `dbl` against `curvesweep.arithmetic`;
  * `SHA256SUMS`;
  * file sizes, each under 4 MB.

  It also checks that the generalised `chainsweep` is unchanged for
  CryptoPro-B. The curve-generic model with CryptoPro-B's own arithmetic
  equals the original model exactly. Re-exporting the frozen `4+1w/7.5.5`
  record reproduces it unchanged. 2-step counts agree with `curvesweep`, and
  2-step maps agree with Velu.
* Primality of `p` and `n` is checked when the harness loads a curve
  (`targets.verify`, sympy `isprime`, a probabilistic test). It is **not** a
  Lean claim (see below).

## Regeneration

The std-curves checkout is J08nY/std-curves at commit
`77fe6e3585ca2c2225b59d7df24b7c775437276f` (the commit
`endosweep_curves_20261006/curves.json` records). The arkworks constants are
the in-repo `research/endosweep_curves_20261006/arkworks/curves.json`
(arkworks-rs/curves `e2d16a27`). Run from the repository root:

```sh
STD=/path/to/std-curves   # at 77fe6e35...
for c in "bandersnatch. arkworks/ed_on_bls12_381_bandersnatch" "tom384. other/Tom-384" "cp6_782. arkworks/cp6_782"; do
  set -- $c
  python3 -m harness.endosweep.chainsweep --target "$2" --std-curves "$STD" \
      --extra research/endosweep_curves_20261006 --catalogue cost --prefix "$1" \
      --out-dir research/endosweep_native_chains_20261016
done
python3 research/endosweep_native_chains_20261016/lean/gen_native_chains_lean.py .
python3 -m pytest -q tests/test_endosweep_native_chains.py
```

Run times on this VM (python-flint 0.9.0): about 2 s, 4.7 min and 12.5 min.
Each run writes `<prefix>chains.constants.json`, `<prefix>catalogue.json`,
`<prefix>model.json` and `<prefix>catalogue.md`, and updates its own three
lines of `SHA256SUMS` (the other curves' lines are kept). The defaults
(`--target "GOST CryptoPro-B"`, no `--prefix`, `--catalogue norm`) still
produce the CryptoPro-B files of `endosweep_chainsweep_20261006`.

## Files

| file | what |
|:--|:--|
| `<curve>.chains.constants.json` | the frozen chain set (format `endosweep-chainsweep/1` plus the `curve` block) |
| `<curve>.catalogue.json` | every ordering of the catalogue: element, order, verification, eigenvalue, both evaluators' counts, build time |
| `<curve>.model.json` | expected (M, S, I, M_eq) of every native arm with the curve's own arithmetic (400 seeded scalars, seed 7) |
| `<curve>.catalogue.md` | the per-curve report |
| `SHA256SUMS` | hashes of the nine JSON files |
| `lean/gen_native_chains_lean.py` | generator of the Lean certificate |

The chain sets were handed to the native harness as
`native_chains/<curve>.constants.json` (byte-identical copies; the SHA-256
values are those in `SHA256SUMS`).

## Lean verification

[`formal/CryptoResearch/Endosweep/NativeChains.lean`](../../formal/CryptoResearch/Endosweep/NativeChains.lean)
(namespace `CryptoResearch.Endosweep.NativeChains`) is generated from the
three chain files by `lean/gen_native_chains_lean.py`. The script re-checks
every proposition in Python and refuses to write on any mismatch. The
module uses core Lean only: no imports, closed propositions, `decide`. It
holds one theorem per curve:

* `bandersnatch_native_chain_certificate` (2 orderings);
* `tom384_native_chain_certificate` (22 orderings);
* `cp6_782_native_chain_certificate` (57 orderings).

Each theorem certifies, by kernel arithmetic:

* `p + 1 − t = h·n` and `t² − 4p = D_K·f²` for the recorded `t` and `f`;
* `λ_ω² − τλ_ω + m ≡ 0 (mod n)` for the recorded `omega_root`, where
  `ω² = τω − m` (`x² + 2` for Bandersnatch; `x² − x + 155` for Tom-384;
  `x² − x + 85` for CP6-782);
* `G` satisfies `y² = x³ + ax + b (mod p)`;
* for every exported ordering:
  * `N(a + bω)` equals the recorded norm and the product of the step
    degrees, for example `N(4 + ω) = 175 = 7·5·5` (Tom-384) and
    `N(4 + ω) = 105 = 7·3·5` (CP6-782);
  * the matched element is `±(a + bω)`;
  * the eigenvalue `e` satisfies `0 ≤ e < n` and `e ≡ a′ + b′λ_ω (mod n)`;
  * `e² − (2a′ + b′τ)e + N ≡ 0 (mod n)`: `e` is a root of the
    endomorphism's characteristic polynomial (trace `2a′ + b′τ`, norm `N`);
  * both reduced GLV basis vectors `(u, v)` satisfy `u + v·e ≡ 0 (mod n)`,
    and their determinant is `±n`. So, by
    `ChainEigen.glv_basis_spans_relation_lattice`, they are a basis of the
    relation lattice;
  * every test vector satisfies `k ≡ k₁ + k₂·e (mod n)`, and its `P`,
    `φ(P)` and `k·P` satisfy the curve equation mod `p`.

Checks run:

* `lean -o … CryptoResearch/Endosweep/NativeChains.lean`, run from `formal/`
  (Lean 4.35.0-rc1), compiles in about 3 s.
* `#print axioms` reports that all three theorems **do not depend on any
  axioms**. The file has no `sorry`, `admit`, `axiom`, `unsafe` or
  `native_decide`.
* Negative controls: changing one digit of Tom-384's `4+1w/7.5.5`
  eigenvalue, or of a CP6-782 test vector's `k·P`, makes the kernel reject
  the proof ("`decide` proved that the proposition … is false").

Hypotheses and non-claims:

* **Hypothesis, not proved in Lean:** `p` and `n` are prime. The harness
  checks this with sympy `isprime`, a probabilistic test.
* **Not Lean claims:**
  * that `t` is the curve's trace, so that `#E = h·n`;
  * that `G` and the test points have order `n`;
  * that each isogeny walk exists, is an endomorphism and acts as `e` on
    points (`φ(P) = e·P` and `kP = k₁P + k₂φ(P)` are checked on points by
    the harness and by the tests);
  * the completeness of the catalogue;
  * every operation count, and every timing.

Target specs:

* `formal/targets/endosweep-native-chains-bandersnatch.yaml` (`TASK-20261016-e027d4`);
* `endosweep-native-chains-tom384.yaml` (`TASK-20261016-038a57`);
* `endosweep-native-chains-cp6-782.yaml` (`TASK-20261016-ee0f02`).
