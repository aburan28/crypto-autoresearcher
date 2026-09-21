# Balanced-Primary Root-Choice Collapse

Date: 2026-07-24

## Candidate

Exploit the balanced-primary complementary-product criterion to remove the
local square-root enumeration factor from ramified self-pairing isogeny
recovery, conditional on a decoder that consumes sign-free Kummer generator
rows directly.

## Status

`HYPOTHESIS / RESTRICTED THEOREM CANDIDATE / CRYPTOGRAPHIC-IMPLICATIONS-IF-DECODER / NOT-A-BREAK`

## Setup

Let

```text
phi : E0 -> E1
```

be an unknown oriented isogeny of known degree `d`.  Suppose ramified
self-pairings provide, for pairwise-coprime odd primary orders
`n_1,...,n_r`, rows

```text
x(phi(P_i)) = x([alpha_i] Q_i),    alpha_i^2 = v_i mod n_i.
```

Each local row has two square-root choices.  A root-enumerating recovery path
therefore sees `2^r` signed tuples, or `2^(r-1)` tuples after quotienting by
global sign.

Define

```text
beta(n_1,...,n_r) = min_S (prod_{i in S} n_i + prod_{i notin S} n_i).
```

## Restricted Theorem

If `beta(n_1,...,n_r) > 4d`, then all degree-`d` homomorphisms matching the
sign-free Kummer rows differ by at most global sign.

Equivalently, the `2^(r-1)` local square-root classes cannot encode
`2^(r-1)` different degree-`d` Kummer maps in this regime.

## Proof Sketch

Let `psi` be another degree-`d` homomorphism matching the sign-free rows.  For
each `i`, the equality of target Kummer coordinates gives a sign
`epsilon_i in {+1,-1}` such that

```text
phi(P_i) = epsilon_i psi(P_i).
```

The indices with `epsilon_i=+1` contribute a subgroup of order `N_S` to
`ker(phi-psi)`, and the complementary indices contribute a subgroup of order
`N_{S^c}` to `ker(phi+psi)`.  If neither homomorphism vanishes, then

```text
N_S + N_{S^c} <= deg(phi-psi) + deg(phi+psi) = 4d,
```

contradicting `beta>4d`.  Hence `psi=phi` or `psi=-phi`.

## Cryptographic Implication

This interacts with self-pairing recovery analyses that include a factor `T`
for the number of square roots of `1 mod m`, where `m` has many distinct
ramified primary factors.  In the balanced-primary regime, those local root
classes are not distinct map identities.  Therefore:

- a direct Kummer-row decoder can avoid root-tuple enumeration;
- root-enumerating Kani/theta paths may be doing redundant branch work;
- discriminants with many ramified factors should be audited by `beta`, not
  only by the number of local square roots.

Primary-source context:

- Castryck et al. introduce cyclic self-pairings and weak class-group-action
  instances: <https://eprint.iacr.org/2023/549>.
- Macula and Stange extend the framework with sesquilinear pairings:
  <https://eprint.iacr.org/2024/880>.
- Galbraith, Gilchrist, and Robert apply self-pairings to ascending volcanoes
  and give the `T`-dependent recovery analysis:
  <https://eprint.iacr.org/2025/1243>.
- The 2026 isogeny-problems survey frames isogeny recovery and related path
  problems as active open terrain: <https://eprint.iacr.org/2026/1431>.

## Boundary

This is not yet a general isogeny-complexity improvement, SCALLOP break, or
ECDLP consequence.  The missing piece is an efficient, compact, and
same-instance competitive Kummer-row decoder.  The existing Schoof-Velu
target-scaling decoder is toy-scale and explicit-map oriented.

## First Falsification Screen

Run a parameter screen over degree values and small odd primary orders, under
a product cap `prod(n_i) <= 64 d^2`.  Record tuples satisfying:

- `beta>4d`;
- additive Kummer capacity `sum((n_i-1)/2)<2d`;
- root classes `2^(r-1)` as large as possible.

This tests whether the root-collapse regime is numerically nonempty without
using artificially enormous torsion products.

## Screen Result

`OBSERVATION / COMBINATORIAL-SCREEN / MODEL-BOUND / NOT-A-BREAK`.

The producer/verifier pair

```text
experiments/ecdlp_isogeny/iso_balanced_primary_root_collapse_screen.py
experiments/ecdlp_isogeny/iso_balanced_primary_root_collapse_screen_verify.py
```

passed with producer payload

```text
df640449eeb445c6017c23c3554fae6966da8e1225f66b985c155321f7a80bc0
```

and verifier payload

```text
2554d062293655b9e0d5fc39716dbbf849517a4ffe10dd5d67094a60c0b34ef6
```

The verifier reported success with zero errors.

Under the registered cap `prod(n_i) <= 64 d^2`, the canonical small-prime
prefix witnesses give:

| degree `d` | orders | root classes after global sign | beta | `4d` | additive capacity | `2d` |
|---:|---|---:|---:|---:|---:|---:|
| 13 | `3,5,7,11` | 8 | 68 | 52 | 11 | 26 |
| 17 | `3,5,7,11,13` | 16 | 248 | 68 | 17 | 34 |
| 127 | `3,5,7,11,13,17` | 32 | 1016 | 508 | 25 | 254 |
| 509 | `3,5,7,11,13,17,19` | 64 | 4406 | 2036 | 34 | 1018 |
| 2039 | `3,5,7,11,13,17,19,23` | 128 | 21124 | 8156 | 45 | 4078 |
| 8191 | `3,5,7,11,13,17,19,23,29` | 256 | 113752 | 32764 | 59 | 16382 |

Interpretation: even with product only a constant multiple of `d^2`, the
root-enumeration factor can grow across the screened degrees while
balanced-primary uniqueness and additive deficit both hold.  This is enough to
justify a recovery-backend comparison.  It does not establish that a direct
Kummer decoder is faster than root-enumerating Kani/theta.

## Next Concrete Action

Build a same-instance benchmark on a nonunique-source ordinary fixture that
compares:

1. direct Kummer-row target-scaling recovery;
2. explicit root-tuple enumeration feeding the same decoder;
3. additive curve-identity recovery;
4. the closest available Kani/theta or BMSS-style normalized backend.

Every torsion-field, pairing, pairing-root, memory, explicit-output, and
candidate-verification cost must be charged.
