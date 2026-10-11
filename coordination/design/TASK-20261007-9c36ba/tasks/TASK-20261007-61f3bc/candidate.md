# Candidate B: ER-seeded McEliece PKE

Task: `TASK-20261007-61f3bc`  
Idea: `IDEA-20261007-6553d5`  
Hypothesis: `H-SSI-3dad1f`  
Primitive: public-key encryption (PKE), not a KEM or key exchange  
Status: explicit candidate; security, novelty, efficient key generation, and deployability are not established

## Candidate claim

`ER-McE` is a deliberately auditable composition. A complete evaluable basis
of `End(E)` is canonicalized and used as the sole secret seed for a binary
Goppa-code trapdoor. Encryption is the public McEliece operation and
decryption is bounded-distance decoding. Thus the recipient mechanism is code
decoding, not C-star evaluation, label transport, evaluator reconstruction, or
an assumed `SecretLift`/`EndpointLift` operation.

The construction has exact finite syntax and a conditional actual-message
correctness argument. It is **not** presently an EndRing-secure construction:
the known implication is only

```text
complete EndRing solver -> recover canonical ring seed -> recover code trapdoor -> decrypt.
```

The required security direction,

```text
IND-CPA attacker on ER-McE -> solve the stated EndRing challenge,
```

is open. Moreover the real public key contains a ring-seeded code matrix, so a
bare-curve EndRing challenge cannot currently be embedded without already
knowing the ring. The code-decoding assumption is separate and may remain hard
even when EndRing is easy, or fail while EndRing remains hard.

## Domains and encodings

- Security parameter: `lambda`.
- Curve: a supersingular curve `E/F_(p^2)` in a fixed canonical Weierstrass
  serialization, with `log p = Theta(lambda)`.
- EndRing witness: four evaluable rational maps `W=(omega_1,...,omega_4)`
  whose `Z`-span is exactly `End(E)`, including exact addition, composition,
  degree, trace, and equality data.
- Canonical ring string: `r = CanRing(E,W)`, defined by finite shortlex
  enumeration below. It is representation-independent for the same exact
  evaluable order, but no polynomial runtime is claimed.
- Code parameters: binary irreducible Goppa parameters `(q=2^s,n,k,t)` with
  a certified minimum distance at least `2t+1` and polynomially bounded
  `n(lambda)`.
- Messages: canonical `k`-bit strings, identified with `F_2^k`.
- Public code key: a full-rank `k x n` binary matrix `G_pub` in row-major
  encoding.
- Ciphertext: `(version,key_id,c)` where `c in F_2^n` and
  `key_id = H_tag(encode(pk))`.
- Failure symbol: `bottom`, distinct from every message.
- Equality: byte equality after strict canonical parsing; noncanonical field,
  curve, matrix, or ciphertext encodings are rejected.

`H_seed`, `H_tag`, and the XOF used by deterministic code generation are
domain-separated public functions. No random-oracle security theorem is
claimed by defining them.

## Exact algorithms

### `EnumerateEndRing(E)`

Enumerate finite strings in shortlex order. Parse each candidate as four
rational maps on `E`; discard parse failures. Check that every map is an
endomorphism, that the maps are `Z`-linearly independent, that their span is
closed under composition and contains `[1]`, and that the trace-pairing
discriminant is that of a maximal order in `B_(p,infinity)`. Return the first
tuple passing all checks. This is a finite definition: a complete basis exists
and has a finite encoding. Its runtime is unbounded by this packet and is not
used as an available polynomial oracle.

### `CanRing(E,W)`

Enumerate candidate four-map tuples in shortlex order. Using `W` as exact
coordinates, retain only tuples related to `W` by a matrix in `GL_4(Z)` and
whose maps are byte-canonical. Return the encoding of the first retained
tuple. The enumeration terminates because `W` supplies at least one basis.
This is an explicit algorithm, not a lift interface; polynomial runtime is
open.

### `KeyGen(1^lambda)`

1. Sample public supersingular parameters and a curve `E` from the declared
   walk-generated key distribution. Keep the sampled isogeny path only long
   enough to aid candidate enumeration, then run `EnumerateEndRing(E)` to get
   `W`; erase the path before output.
2. Compute `r = CanRing(E,W)`.
3. Sample a uniform public salt `s <- {0,1}^{2 lambda}` and set
   `sigma = H_seed("ER-McE/v1" || encode(E) || s || r)`.
4. Run deterministic `GoppaGen(sigma)` by XOF/rejection sampling until it
   obtains a support `L`, square-free irreducible Goppa polynomial `g` of
   degree `t`, secret generator `G_sec`, invertible scrambler `S`, and
   permutation `P`. Certify `rank(G_sec)=k` and designed distance `>=2t+1`.
5. Set `G_pub = S G_sec P` and
   `pk=(version,E,s,parameters,G_pub)`. Set
   `sk=(version,E,s,parameters,G_pub,W,r,L,g,G_sec,S,P)`. The public-key
   copy in `sk` lets `Dec` verify the key tag without an undeclared input.

Step 1 is an exact terminating enumeration but lacks a polynomial runtime
proof. Steps 3--5 are expected polynomial time subject to a proved tail bound
for the declared deterministic rejection sampler; that tail bound is also
open here.

### `Enc(pk,m;rho)`

1. Strictly parse `pk` and `m`; reject unless `m in F_2^k` and `G_pub` has
   rank `k`.
2. Use uniform coins `rho` to sample `e` uniformly among length-`n` binary
   vectors of Hamming weight exactly `t`.
3. Compute `c = m G_pub + e` over `F_2`.
4. Return `(version,H_tag(encode(pk)),c)`.

### `Dec(sk,ct)`

1. Strictly parse `ct`; reject with `bottom` on a wrong version, length,
   noncanonical encoding, or key tag.
2. Compute `c_0 = c P^{-1}`.
3. Run the explicit Patterson bounded-distance decoder for the secret binary
   Goppa code. If it does not return a unique pair `(u,e_0)` with
   `c_0=u G_sec+e_0` and `wt(e_0)=t`, return `bottom`.
4. Compute `m=u S^{-1}`.
5. Recompute `e=c-m G_pub`; return `bottom` unless `wt(e)=t` and the original
   ciphertext serialization is canonical. Otherwise return the selected
   message `m`.

No step calls `SecretLift`, `Complete_2`, `EndpointLift`, `BaseGen`, `Eval2`,
target-frame reconstruction, quotient lifting, or a digit-loop tie rule.

## Conditional actual-message correctness

For every accepted key produced by `KeyGen`, every `m in F_2^k`, and every
weight-`t` encryption error, undoing `P` gives

```text
c P^{-1} = (m S) G_sec + e P^{-1}.
```

Permutation preserves Hamming weight. If the certified secret code has
minimum distance at least `2t+1` and the declared Patterson decoder is correct
on every error of weight at most `t`, unique decoding returns `u=mS`; hence
`Dec` returns `u S^{-1}=m`. The conditional failure probability is therefore
zero. This proves neither that `KeyGen` is efficient nor that the certificates
and decoder implementation exist in this repository. Those remain O2/O3
discharge work.

## Hard problems and assumption direction

1. `Walk-ER`: sample `E` from the exact `KeyGen` curve marginal; given only
   `E`, output any complete evaluable basis of `End(E)` accepted by the checks
   above. This is the intended bare problem.
2. `Aux-ER-McE`: give the adversary the complete real public key
   `(E,s,parameters,G_pub)` and require the same EndRing output. This may be
   easier than `Walk-ER`; no equivalence is asserted.
3. `Seeded-Goppa-IND`: distinguish McEliece encryptions for the public matrices
   produced by the ring-seeded generator. This is a separate intermediate
   assumption and is not called EndRing.

An `Aux-ER-McE` solver yields the canonical ring string, regenerates the code
trapdoor, and decrypts. That is an attack implication. No construction here
turns an IND-CPA adversary into a solver for either EndRing problem.

## Complete adversarial view

The IND-CPA adversary receives the field and curve parameters, `E`, public
salt, code dimensions, `G_pub`, hash/XOF specifications, key tag, all challenge
ciphertext fields, and every encryption it computes itself. It selects two
equal-length `k`-bit messages and receives an encryption of one. There is no
decryption oracle. Public parsing outcomes, rank checks, and serialization are
part of the view. Timing, power, faults, cache behavior, malicious setup,
multi-user correlation, CCA queries, quantum random-oracle queries, and
implementation leakage are excluded and therefore unsupported.

Repeated encryption exposes independent exact-weight errors under the same
linear code. Alternate encodings are rejected. Malformed ciphertexts return
only `bottom`; this does not establish CCA security. A wrong secret key either
rejects or may accidentally accept a word in its own decoding ball; no
wrong-key robustness bound is proved.

## O1--O6 scorecard

| Obligation | Status | Reason |
| --- | --- | --- |
| O1 exact hard problem | open | `Walk-ER`, `Aux-ER-McE`, and their output relation are stated, but hardness, real-distribution equivalence, and the effect of the ring-seeded code matrix are unproved. |
| O2 honest algorithms | open | Every step has a finite algorithm, but EndRing enumeration/canonicalization and seeded-code rejection tails lack polynomial bounds. |
| O3 correctness | proposed discharge | Actual-message recovery follows conditionally from the certified distance and total bounded-distance decoder; no implementation or independent review exists. |
| O4 functionality | proposed discharge | The private operation is explicit Goppa decoding from a trapdoor deterministically derived from `End(E)`; it is materially different from prior evaluator/lift routes. Recipient advantage over public decoding is an assumption, not a theorem. |
| O5 security reduction | open | Only `EndRing solver -> break PKE` is available. The required reverse reduction and bare-challenge embedding are missing. |
| O6 adversarial view | open | The CPA view and parsing behavior are enumerated, but auxiliary leakage, repeated-use attacks, wrong-key acceptance, side channels, and concrete parameters are unanalyzed. |

## Controls and falsifiers

- **Public-data control:** run generic information-set decoding and structural
  Goppa-key recovery using exactly `(E,s,parameters,G_pub)`. Any polynomial
  public decoder removes the asserted recipient advantage.
- **Seed recovery control:** search whether `G_pub` exposes `sigma`, `r`, or a
  canonical EndRing basis more cheaply than `Aux-ER-McE`.
- **Known-false control:** append `m` to the ciphertext. Any purported proof
  that still converts the trivial plaintext reader into an EndRing solver has
  a broken extraction step.
- **Distribution control:** an EndRing challenge containing only `E` does not
  let a reducer compute the correctly distributed `G_pub`; this is a current
  explicit failure, not an omitted detail.
- **Actual-message control:** test the algebraic identity above symbolically;
  returning a codeword, syndrome, seed, or ring invariant is not enough.
- **Wrong-key/malformed control:** require strict parse, unique decode, exact
  weight recheck, and `bottom` on failure; measure accidental wrong-key accepts
  before making any robustness claim.
- **Canonicalization collision:** two accepted bases of the same exact ring
  producing different `r` falsify deterministic trapdoor regeneration.
- **Assumption separation:** an attack on the seeded Goppa family that leaves
  EndRing unsolved refutes an EndRing-only reading without saying anything
  about EndRing hardness.

## Prior-art and novelty boundary

The nearest repository records name SÉTA, SiGamal/C-SiGamal, LIT-SiGamal, and
key-updatable supersingular PKE. This candidate does not use their public
isogeny evaluators; it composes a ring-derived seed with a code trapdoor. No
primary source was read in this task, so `novelty_status: unverified`. A generic
secret-seeding composition may already be known or may be judged vacuous as an
EndRing construction.

`dominated_by: n/a (no security or performance result claimed)`  
`sota_delta: exact finite PKE syntax plus an exposed wrong-direction reduction; zero claimed asymptotic, concrete, or deployment improvement`

## Next discriminating action

Before implementation, attempt a black-box challenge-embedding proof. Given a
bare `Walk-ER` curve `E*` without its ring, construct a public matrix distributed
as `G_pub` and use an IND-CPA adversary to output a complete EndRing basis. If
the matrix cannot be generated without the witness, record the exact
distribution obstruction. If the adversary only supplies a code decoder, keep
`Seeded-Goppa-IND` separate and do not promote the candidate as EndRing-based.
