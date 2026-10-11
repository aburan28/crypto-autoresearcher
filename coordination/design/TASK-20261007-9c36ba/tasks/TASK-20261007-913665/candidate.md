# Candidate A: canonical-endomorphism scalar-transfer PKE

Task: `TASK-20261007-913665`  
Goal: `GOAL-SSI-2fa82a`  
Question: `RQ-SSI-1946c9`  
Proposal: `IDEA-20261007-560bcb`  
Hypothesis: `H-SSI-fbe68d`

Status: **candidate only**. The construction below is not claimed secure,
novel, practical, or deployable. It has no experimental evidence. Its exact
correctness identity is proposed, while its EndRing security reduction is
open.

## 1. Mechanism and boundary

The candidate is called **CEST-PKE** (canonical-endomorphism scalar-transfer
PKE). It deliberately does not use the previous C-star, public label
transport, target-frame reconstruction, `Eval2`, `BaseGen`, normalized
quotient lift, endpoint lift, or digit-decoder routes.

The public sender and the recipient meet through ordinary scalar linearity.
Key generation derives a deterministic non-scalar endomorphism `psi_E` from a
complete evaluable witness for `End(E)` and publishes one point
`A = psi_E(P)`. To encrypt, a sender samples `r`, publishes `R = [r]P`, and
derives the pad from `[r]A`. To decrypt, the recipient derives `psi_E` from the
complete ring witness and computes `psi_E(R)`. The equality

```text
psi_E([r]P) = [r]psi_E(P) = [r]A
```

gives actual-message correctness.

This creates an honest, sharply visible security gap. The immediate
confidentiality target is a same-scalar transfer problem on `(P,A,R)`, not
plain EndRing. A solver for the relevant auxiliary-data EndRing instance can
break the scheme, but that implication is the wrong direction for a security
reduction. No conversion of a successful IND-CPA adversary into an EndRing
solver is supplied.

## 2. Exact objects and encodings

For security parameter `lambda`, fix:

- a prime `p`, a supersingular elliptic curve `E/F_(p^2)`, an odd prime
  `q != p`, and an extension degree `d = poly(lambda)` over which `E[q]` is
  rational;
- a message length `mu(lambda)` and message space `{0,1}^mu`;
- a public degree bound `B(lambda) = poly(lambda)`;
- canonical encodings of the field, curve model, points, integers, tuples, and
  the point at infinity;
- the public Weil pairing `e_q` for subgroup and basis checks;
- a domain-separated random oracle
  `H_pad : {0,1}* -> {0,1}^mu` with classical query access only.

A **complete evaluable endomorphism-ring witness** `W` is a rank-four
`Z`-basis for exactly `End(E)`, multiplication/trace/reduced-norm tables, and
algorithms that convert every represented element into an evaluator on points
over declared extensions. Equality of witnesses means that they span the same
full ring and induce the same endomorphisms on `E`; basis changes alone do not
change the witness relation.

`CanonicalBoundedEnd(E,W,B)` is the following required interface.

1. Enumerate all noncentral primitive elements of `End(E)` with degree at most
   `B` from the norm lattice represented by `W`.
2. Convert each to a normalized rational-map encoding on the fixed public
   model of `E`, remove duplicates as maps, and choose the lexicographically
   first encoding.
3. Return that evaluable map `psi_E`, or `fail` if the set is empty.

The definition is representation-independent if normalized rational-map
conversion is correct. Polynomial enumeration, normalization, and the
non-negligible availability of a suitable element are open obligations; the
name is not an oracle entitlement.

`TrapCurveGen(1^lambda)` must output `(E,W,q,d)` such that `W` is complete and
evaluable, `CanonicalBoundedEnd` succeeds, and its result acts non-scalarly on
`E[q]`. A proposed realization is to generate from a known-ring base curve,
walk secretly to `E`, and transport the full ring, but no such sampler is
established here. Its output distribution is part of the assumption and may
be highly structured.

Public-key serialization is the exact canonical byte string

```text
pk_ser = Encode(version, lambda, p, d, E, q, B, P, A, H_pad_domain)
```

with `P,A` nonzero exact-order-`q` points and `e_q(P,A) != 1`. Ciphertexts are
bytewise-canonical tuples `(pk_ser,R,v)`. Alternate point or field encodings
are rejected rather than identified after parsing.

## 3. Algorithms

### `KeyGen(1^lambda)`

1. Run `TrapCurveGen(1^lambda)` to obtain `(E,W,q,d)`. On failure, retry; the
   sampler must later supply an expected-polynomial retry bound.
2. Compute `psi_E <- CanonicalBoundedEnd(E,W,B)`. Retry if it fails.
3. Sample `P` uniformly from exact-order-`q` points. Set `A = psi_E(P)`.
   Retry the point if `A = O`, `[q]A != O`, or `e_q(P,A) = 1`.
4. Form and validate `pk_ser` as above.
5. Return `pk = pk_ser` and `sk = (pk_ser,W)`.

Key generation uses private generation coins. Neither those coins nor a
connecting isogeny are part of the secret-key interface. No erasure claim is
made.

### `Enc(pk,m)`

1. Parse `pk` canonically. Check the curve and field encodings; primality and
   declared-size bounds; `P,A != O`; `[q]P = [q]A = O`; and
   `e_q(P,A) != 1`. Return `fail` on any error.
2. Require `m in {0,1}^mu`.
3. Sample `r` uniformly from `Z_q^*`.
4. Compute `R = [r]P` and the public sender secret `S_snd = [r]A`.
5. Compute
   `k = H_pad("CEST-PKE/v1" || pk_ser || Encode(R) || Encode(S_snd))`.
6. Set `v = m XOR k` and return the canonical ciphertext
   `c = (pk_ser,R,v)`.

Encryption uses only public inputs, group arithmetic, the public pairing for
key validation, and the public random oracle. It never calls `W`,
`CanonicalBoundedEnd`, or an isogeny-label evaluator.

### `Dec(sk,c)`

1. Parse `sk = (pk_ser,W)` and `c = (pk_ser_c,R,v)` canonically. Reject with
   `fail` unless `pk_ser_c` equals `pk_ser` byte for byte and `|v| = mu`.
2. Revalidate `pk_ser`. Validate `R != O`, `[q]R = O`, and
   `e_q(P,R) = 1`. The last check places `R` in the line generated by `P`
   because `q` is prime and `P` has exact order `q`.
3. Compute `psi_E <- CanonicalBoundedEnd(E,W,B)`. Reject if it fails or if
   `psi_E(P) != A`.
4. Compute the recipient value `S_rec = psi_E(R)`.
5. Compute
   `k = H_pad("CEST-PKE/v1" || pk_ser || Encode(R) || Encode(S_rec))` and
   return `m = v XOR k`.

For a well-formed but adversarial `R` in `<P>`, decryption returns a bit string;
this IND-CPA candidate provides no ciphertext integrity. Noncanonical,
off-curve, wrong-order, outside-line, infinity, wrong-key, and wrong-length
inputs return the single public failure symbol. Constant-time behavior is not
claimed.

## 4. Actual-message correctness

For every accepted key `(pk,sk)`, every `m in {0,1}^mu`, and every
`r in Z_q^*`, `R=[r]P` passes the declared checks. Endomorphisms are group
homomorphisms, hence

```text
S_rec = psi_E(R)
      = psi_E([r]P)
      = [r]psi_E(P)
      = [r]A
      = S_snd.
```

Both sides therefore query `H_pad` on the identical canonical byte string, so
`Dec(sk,Enc(pk,m;r)) = m`. Conditional on accepted key generation and correct
implementations of the declared interfaces, encryption/decryption correctness
is perfect. The candidate does not yet bound key-generation retry probability
or prove that `CanonicalBoundedEnd` is polynomial on the sampled family.

The recovered value is the selected plaintext `m`, not an endpoint, orbit,
kernel, invariant, or message-independent tag.

## 5. Exact problems and assumption direction

### `AuxEndRing_CEST`

The challenge sampler runs honest `KeyGen` internally and releases only
`pk_ser`. A solution is any complete evaluable witness `W'` for `End(E)` such
that `CanonicalBoundedEnd(E,W',B)(P) = A`; success requires that `W'` span the
full ring, not merely contain one useful endomorphism. The adversary receives
every byte in the public key, including `q,P,A` and the structured key
distribution. This is an auxiliary-data and distribution-specific EndRing
problem. Its relationship to bare or uniformly sampled EndRing is open.

### `CEST-XFER-KI` in the classical ROM

The challenger samples an honest public key, `r <- Z_q^*`, `R=[r]P`, and a
bit `b`. It sets

```text
K_0 = H_pad("CEST-PKE/v1" || pk_ser || Encode(R) || Encode([r]A)),
K_1 <- {0,1}^mu,
```

and gives `(pk_ser,R,K_b)` to a PPT distinguisher with classical oracle access
to `H_pad`. Its advantage is
`|Pr[D(pk,R,K_0)=1] - Pr[D(pk,R,K_1)=1]|`.

This is the direct intermediate assumption. Given a `CEST-XFER-KI` challenge,
an IND-CPA reduction can mask the adversary's chosen `m_beta` with the supplied
`K_b`. In the real world this is an honest encryption; in the random world the
masked component is independent of `beta`. Thus the intended classical-ROM
bound is

```text
Adv_IND-CPA_CEST(A) <= Adv_CEST-XFER-KI(D) + delta_parse,
```

where `delta_parse=0` for honest canonical challenges. This is only a proposed
reduction to the named intermediate game; it is not a reduction to EndRing.

An `AuxEndRing_CEST` solver computes `W`, derives `psi_E`, evaluates
`psi_E(R)=[r]A`, and therefore breaks `CEST-XFER-KI` and the PKE. This is

```text
EndRing solver  ->  break scheme,
```

which identifies an attack route but does not establish the needed

```text
scheme attacker  ->  EndRing solver.
```

The latter direction, including extraction of a complete ring rather than a
single transfer value, is open. Pairings make candidate transfer points
publicly checkable via `e_q(P,S)=e_q(R,A)`, so a DDH assumption is unsuitable;
the intermediate target is a verifiable/gap-style computational transfer
problem. It may be no harder than ordinary elliptic-curve CDH and may have no
equivalence to EndRing.

## 6. Complete adversarial view

The public view contains the parameter-generation algorithms, field and curve
model, extension degree, `q`, `B`, canonical encodings, `P`, `A`, the pairing,
the random-oracle domains, full public-key bytes, every ciphertext
`(pk_ser,R,v)`, all public validation outcomes, and any number of repeated
honest encryptions. IND-CPA supplies no decryption oracle. Encryption is public,
so the adversary may generate arbitrary honest-looking ciphertexts and query
`H_pad` adaptively. The claim is only for classical PPT adversaries in the
classical ROM; QPT adversaries, superposition queries, CCA security, malicious
public keys, side channels, fault attacks, and concrete parameters are outside
the claim.

Reusing `r` repeats `(R,k)` and reveals the XOR of two messages. For `Q`
encryptions under one key, the nonce-collision probability is at most
`Q(Q-1)/(2(q-1))`; any multi-ciphertext theorem must include this term. For a
fixed valid `(pk,R)`, different messages give different `v`. Alternate
encodings are rejected. Hash, point, and key-serialization collision risks
have no concrete parameter assessment here.

The public key may disclose structured-ring information through `A`, the
pairing relation, the curve family, automorphisms, or key-generation rejection
patterns. Those disclosures are inside `CEST-XFER-KI` and
`AuxEndRing_CEST`; they are not covered by bare EndRing merely because `E` is
supersingular.

## 7. Mandatory controls and falsifiers

- **Public-data control.** Give an algorithm only `(pk_ser,R)` and charge all
  work needed to output `[r]A`. Any polynomial algorithm with non-negligible
  success breaks the claimed recipient asymmetry and falsifies
  `CEST-XFER-KI`. The pairing may verify an answer but does not itself provide
  the point.
- **Complete-witness quotient control.** Replace `W` by only an evaluator for
  `psi_E`. Decryption remains identical. This shows that functionality factors
  through a strict candidate quotient unless a reverse reduction from that
  quotient to complete EndRing is proved. Full-ring sufficiency is not full-
  ring necessity.
- **Known-false leaked-plaintext control.** Modify the ciphertext to include
  `S_snd`, `k`, or `m`. The random-world step in the intermediate reduction is
  no longer message-independent, so the proof must fail there. Any argument
  that still declares the modified scheme confidential is invalid.
- **Wrong-key control.** A ciphertext embeds exact `pk_ser`; decryption under a
  different honest key returns `fail` before secret evaluation.
- **Malformed-ciphertext control.** Noncanonical, off-curve, infinity,
  wrong-order, outside-`<P>`, or wrong-length inputs return one failure symbol.
  Valid in-line modifications return an unauthenticated plaintext, as expected
  for this IND-CPA-only candidate.
- **Distribution control.** Compare the marginal curve distribution and full
  auxiliary public-key distribution of `TrapCurveGen` with the advertised
  EndRing challenge. Until a compiler with explicit distance and witness
  pullback exists, the assumption remains `AuxEndRing_CEST` on the real key
  distribution.
- **Pairing control.** Do not invoke DDH on `(P,A,R,S)`: the public equation
  `e_q(P,S)=e_q(R,A)` recognizes correct transfer values.

Direct falsifiers are: failure of the algebraic equality on any accepted key;
two equivalent complete ring witnesses producing different `psi_E`; absence
of a polynomially evaluable bounded canonical endomorphism on non-negligible
key mass; polynomial public scalar transfer; or an IND-CPA-to-EndRing proof
whose simulator cannot embed the real auxiliary-data key distribution.

## 8. O1--O6 status

| Obligation | Status | Reason |
| --- | --- | --- |
| O1 exact hard problem | `proposed_discharge` | `AuxEndRing_CEST` and `CEST-XFER-KI` are explicit, but the connection to bare EndRing and the structured sampler are open. |
| O2 honest algorithms | `open` | Algorithms and failure behavior are typed; `TrapCurveGen`, canonical normalized-map conversion, acceptance probability, and polynomial bounds are not established. |
| O3 quantified correctness | `proposed_discharge` | Perfect actual-message correctness is derived for every accepted key and all messages/coins, conditional on O2 interfaces. |
| O4 functionality | `proposed_discharge` | Sender scalar multiplication and recipient endomorphism evaluation meet exactly. The strict `psi_E` quotient means complete-ring necessity is open. |
| O5 reduction direction | `open` | A reduction to `CEST-XFER-KI` is sketched, but only the wrong-direction EndRing attack route is known. |
| O6 complete view | `proposed_discharge` | The classical-ROM IND-CPA view and parsing behavior are listed; CCA, quantum, side-channel, malicious-key, and concrete analysis are excluded. |

No obligation has independent review, so none is `reviewed_discharge`.

## 9. Prior-art and novelty discipline

No primary paper was read in this task. Novelty is therefore **unverified**.
The closest internal pointer is the SÉTA discussion carried by
`IDEA-20261004-edbd24`: both use a secret endomorphism action, but CEST-PKE's
sender rendezvous is ordinary cross-base scalar multiplication and its
immediate assumption is `CEST-XFER-KI`, not TCSSI. The SiGamal/C-SiGamal and
LIT-SiGamal pointers in `IDEA-20261004-e4c461` use public structured actions or
transport data; CEST-PKE publishes no action label and performs no public
isogeny composition. The key-updatable-PKE pointer is adjacent only at the
public-operation boundary. These comparisons are inherited internal pointers,
not a primary-source non-duplication finding.

The expected failure mode is informative rather than universal: a reviewer
may find that the candidate is simply hashed cross-base DH with an EndRing-
derived key, so its security does not rest on complete EndRing. That would be
a scoped obstruction for this candidate, not an impossibility result for
EndRing-based PKE.

## 10. Next action

Blindly rederive the correctness identity from `scheme-contract.yaml`, then
red-team the complete packet on three joints: (1) whether the canonical
endomorphism really depends on a complete witness, (2) whether public pairing
and generic CDH algorithms collapse the recipient advantage, and (3) whether
any correctly directed reduction can recover a complete EndRing solution from
a transfer/IND adversary without adding an unstated assumption.
