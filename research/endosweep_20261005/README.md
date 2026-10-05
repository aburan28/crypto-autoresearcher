# Endomorphism-ring sweep for scalar-multiplication speed-ups

Exploratory tooling and a first sweep, 5 October 2026. Repository
`aburan28/crypto-autoresearcher`. **Status: a sweeper with certificates and a
modelled ranking. No ledger record is created or changed, no hypothesis moves,
and nothing below is a measured timing.**

**Question (user, 2026-10-05).** Beyond the obvious constructions (Frobenius
expansions, GLV, GLS), are there algorithmically discoverable endomorphism-based
scalar-multiplication speed-ups — "complex, high-order" endomorphisms that
nobody has written down — and can a sweeper find them?

**Answer in one paragraph.** The sweeper (`harness/endosweep/`) enumerates every
way an endomorphism ring can shorten a variable-base scalar multiplication on
31 target groups, reduces each candidate's relation lattice exactly, and costs it
under one explicit operation-count table. On every target the best modelled
configuration is one already in the literature (GLV, Galbraith–Scott G2,
Longa–Sica 4-GLV). The reason is structural and the sweep makes it quantitative:
the coefficient size of any decomposition is bounded below by
`(log2 n)/r − log2 H − log2 d`, where `r` is the rank of the endomorphism ring
(2 for every elliptic curve), `H` the largest coordinate ("height") of a
generator and `d` the number of generators. New dimensions therefore come only
from height, height is paid for in isogeny degree, and a chain of `ℓ`-isogenies
buys height at `2·cost(ℓ-step)/log2 ℓ` field multiplications per bit — 7.1 M
(ℓ=3) to 9.7 M (ℓ=7) under SIDH-literature step counts, against 6.0–7.4 M for
the doubling that bit removes. Frobenius is the one free height source, which
is exactly why GLS, 4-GLV, FourQ, G2 and τ-adic Koblitz work. Every
"high-order" configuration the sweep generated (isogeny-cycle pumps up to
dimension 8, Frobenius-power boxes up to dimension 8) loses to the best known
one by 8 % to 95 %, and the sweep says on which constant each loss turns.
Twelve of the fourteen deployed prime-field curves carry a certificate that no
non-scalar endomorphism of degree below 500 000 exists, so for them there is
nothing to sweep at all.

## 1. What was built

| file | role |
|---|---|
| `harness/endosweep/quadorder.py` | exact arithmetic in imaginary quadratic orders; discriminant certificate without factoring; elements of a given norm; class order of a prime ideal by form composition; Cornacchia for the generator of its first principal power |
| `harness/endosweep/lattice.py` | exact LLL over rationals, relation lattice, Babai decomposition with a provable coefficient bound |
| `harness/endosweep/costmodel.py` | one table of constants (EFD curve-operation counts, SIDH x-only isogeny-step counts, marked assumptions), interleaved width-w NAF multi-scalar cost |
| `harness/endosweep/targets.py` | 14 deployed curves verified from their constants alone; structural G2 entries; synthetic GLS and CM families |
| `harness/endosweep/sweep.py` | catalogue → configurations → exact reduction → cost → ranking → report |
| `harness/endosweep/toyverify.py` | builds the actual maps on toy curves and checks every prediction on points |
| `tests/test_endosweep.py` | 17 tests (algebra against brute force, lattice bounds, registry typo rejection, sweep regressions, toy maps) |
| `sweep/sweep.md`, `sweep/sweep.json` | the full sweep output (31 targets, every configuration) |
| `TABLES.md` | the four headline tables, generated from the JSON by `make_tables.py` |
| `toyverify_26bit.json` | the explicit-map verification record |

The theory the sweep is built on, and the enumeration it performs, are written
out in `harness/endosweep/README.md`.

## 2. Certificates (Table 1 of `TABLES.md`)

* **Twelve deployed prime-field curves** (P-256, P-384, P-521, brainpoolP256r1,
  SM2, Curve25519, Ed448, Curve1174, Curve41417, E-521, M-511 and — trivially —
  every curve without small CM) have `|D_K| > 2 000 000`, certified by one exact
  perfect-square test per fundamental discriminant below the bound, with no
  factoring of `t² − 4q`. Since every non-scalar endomorphism of an order of
  discriminant `D_K` has degree at least `|D_K|/4`, none of these curves has an
  endomorphism of degree below 500 000, hence no cheap one at all; a Vélu
  evaluation would cost more than the whole scalar multiplication. Their only
  decomposition is the generic one, and only an extension-field view
  (a different group) could change that.
* **secp256k1, BN254 G1, BLS12-381 G1** have `D_K = −3`, the whole inventory
  of primitive endomorphisms of degree ≤ 64 is listed, and all of them produce
  the same 128-bit two-dimensional lattice as ζ₃ (rank 2 cannot do better), so
  ζ₃ wins on cost: 1.50× over width-w NAF under the model.
* Every one of the 14 deployed parameter sets was re-verified from its constants
  (prime `n`, Hasse interval, a point of order divisible by `n` killed by `h·n`),
  so a typo would have excluded the curve rather than coloured a conclusion.

## 3. Free pumps reproduce the literature and saturate at dimension 4 (Table 3)

On BLS12-381 G2 and BN254 G2 the Galbraith–Scott basis `{1, ψ, ψ², ψ³}` gives
64-bit coefficients (ideal 63.5) and 1.89×; the box `{1, ζ₃} × {1, ψ}` is the same
lattice with one fewer ψ to apply, 1.96×. Adding more Frobenius powers
(dimensions 5–8) does not reduce a single coefficient bit — the reduced basis
acquires vectors of ∞-norm 1, i.e. the extra generator is a small integer
combination of the others — while the additions grow, so dimension 8 is back
at 1.20×. `{1, ψ}` alone on BLS12-381 G2 is nearly useless (191-bit coefficient,
1.04×) because `λ_ψ = x` is a 64-bit seed; the sweep sees this as a 64-bit short
vector. The synthetic GLS group over `F_{p²}`, `p ≈ 2^127`, reproduces
Longa–Sica 4-GLV at 2.26×. All of this is known; it is reported because it is
the calibration that makes the negative results below credible.

## 4. Paid pumps: parity by construction, loss in practice (Table 2)

An **isogeny-cycle pump** is the generator of the first principal power of a
split prime `ℓ` (a closed walk of `k = ord[𝔩]` steps on the `ℓ`-isogeny graph),
raised to a power `j` so that its height is about `n^{1/4}`; with a free
generator `u` (ζ₃, or the cheapest small-degree endomorphism when there is no
unit) the box `{1, u, α, uα}` gives a genuine four-dimensional decomposition —
verified explicitly on toy curves, see §5 — with 63–64-bit coefficients on a
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

So the best possible pump, a 3-isogeny chain on a curve where 3 splits, is at
parity with the doublings it removes: on the synthetic `D = −8` curve the pump
costs 462 M (79 steps + overhead) and removes 62 doublings worth 459 M. The
configuration still **loses by 8.6 %** (1825 M vs 1680 M) because going from
two to four scalars costs 13 more additions (the optimiser also drops the window
from 4 to 3) and two more endomorphism images. On the j = 0 curves the only
split primes are 7, 13, 19, …, so the pump is 9.7 M per bit against a 6.0 M
doubling and loses by 23 %. Across all 17 targets that have a pump the loss
ranges from 8.0 % (`D = −11`, 3-cycles) to 95 % (`D = −163`, 41-cycles). For
the 3-isogeny pump to break even on a generic-a curve, one step would have to
cost about 3.7 M instead of 5.6 M; no formula in the literature the author knows
is close, and on a = 0 curves the bar is lower still.

**Literature status.** The sweep labels these boxes "no literature match found".
The author did not find a paper using powers of a principal ideal generator as a
GLV generator; the nearest are Guillevic–Masson–Thomé (single endomorphisms of
degree in the hundreds via Vélu on small-|D| curves) and Smith's Q-curve
reductions (Frobenius composed with one small isogeny). This is a statement
about the author's reading, not a priority claim, and the result is negative in
any case.

## 5. Explicit verification at toy scale (`toyverify_26bit.json`)

On a j = 0 curve over a 26-bit prime with rational 7-torsion, and on a curve with
CM by the class-number-3 order of `Q(√−23)` built from its Hilbert class
polynomial (which was itself checked by naive point counting at four primes):

| check | result |
|---|---|
| ζ₃: (x, y) ↦ (βx, y) acts as one of the two predicted roots | pass |
| degree-7 endomorphism `2 + ω` from Vélu + isomorphism back to E acts as `a + bλ_ω` | pass (element (2, 1)) |
| its j-th power acts as the predicted eigenvalue with the predicted height | pass |
| `{1, ζ, α^j, ζα^j}` reconstructs kP from explicit images for 8 random k, coefficients within the Babai bound | pass (max 5 bits, bound 6, ideal 4.5) |
| closed 3-walk of 2-isogenies on the `D = −23` curve is an endomorphism of degree 8 with the eigenvalue of `1 + ω` (up to unit/conjugate) | pass (2 closed walks found, element (2, −1)) |
| its cube acts as predicted (degree 512, height 22) | pass |

So the objects the sweeper costs are real maps with the predicted action, not
just eigenvalue bookkeeping.

## 6. What this says about the original question

* The only lever that creates new decomposition dimensions on an elliptic
  curve is **free height**, and the only free height is Frobenius over an
  extension field. Everything in that direction (GLS, Longa–Sica, FourQ, G2,
  Koblitz) is known and reproduced here; beyond the effective rank of the
  Frobenius-generated ring (4 for the cyclotomic relations in play) extra
  generators are redundant and cost additions.
* **Paid height is at parity with doublings** by a per-bit accounting that
  does not depend on the curve, so no isogeny-built endomorphism, however
  high its degree or order, beats GLV by more than the constant-factor margin
  of the isogeny-step formulas — and with the best published step counts that
  margin is negative by 8 % and more.
* **Higher rank** — genus-2 Jacobians with quartic CM (Buhler–Koblitz,
  Furukawa–Kawazoe–Takahashi curves; 8-dimensional over `F_{p²}` per
  Bos–Costello–Hisil–Lauter) — is the remaining route to "higher order"
  decompositions. It is outside this sweep (no Jacobian cost model here) and
  capped by index calculus at genus ≤ 3.

A clean negative with a named obstruction is the intended deliverable here;
the obstruction is the height bound in `harness/endosweep/README.md`.

## 7. Limits of this work

* Costs are operation counts under `costmodel.py`; squaring at 0.8 M, inversion
  at 100 M, an assumed 20 M per isogeny-chain image for y-recovery and model
  changes, and SIDH-literature x-only step counts. A different table moves the
  pump losses by a few percent either way; it cannot move the parity argument.
* The synthetic CM and GLS targets are structural (no curve equation); their
  lattices are exact, their security is not assessed.
* FourQ is not included: its two eigenvalue relations were not re-derived here
  and the registry refuses unverified constants.
* Genus 2 and higher is not swept.
* 32 random scalars per lattice for the empirical coefficient size; the Babai
  bound is provable and is reported alongside.

## 8. Reproduce

```sh
python -m pytest -q tests/test_endosweep.py
python -m harness.endosweep --out-dir research/endosweep_20261005/sweep       # ~3 min
python3 research/endosweep_20261005/make_tables.py > research/endosweep_20261005/TABLES.md
python -m harness.endosweep.toyverify --bits 26 --out research/endosweep_20261005/toyverify_26bit.json
```

## 9. Possible follow-ups (not started; would enter the ledger via /propose-ideas)

1. A genus-2 Jacobian cost model and the BK/FKT families, to put the rank-4
   route on the same footing as the elliptic results.
2. FourQ as a verified target (derive and check `ψ`, `φ` eigenvalue relations).
3. If anyone has a 3-isogeny step at ≲ 3.7 M in a usable coordinate system, a
   native measurement of the `D = −8` or `D = −11` pump box against GLV-2 is
   the one experiment in this space whose outcome the model cannot call.
