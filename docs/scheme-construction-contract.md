# Cryptographic scheme construction contract

Use this contract when proposing a new signature, public-key encryption
scheme (PKE), key-encapsulation mechanism (KEM), or authenticated key-exchange
protocol (AKE). It gives agents six explicit obligations and the security
games against which to discharge them. Endomorphism-ring hardness supplies
a possible assumption; the honest-party algorithms supply the functionality.

Start from [the YAML template](../templates/scheme-construction-contract.yaml).
Attach the completed artifact to the existing hypothesis, `proof_search_map`,
and task handoff. This is a prospective documentation contract, not a new
runtime admission check or an instruction to validate before every `run`.
Existing ledger authority, archival rules, independent scientific review, and
immutable records remain binding. A populated template is not a security proof.

## Choose the primitive and claim

| Primitive | Required interface | Functional goal | Baseline security claim |
| --- | --- | --- | --- |
| Signature | `KeyGen, Sign, Verify` | Honest signatures verify | EUF-CMA; add SUF-CMA when required |
| PKE | `KeyGen, Enc, Dec` | Recover the selected plaintext | IND-CPA for a passive candidate; IND-CCA2 for a general-purpose active-security claim |
| KEM | `KeyGen, Encaps, Decaps` | Sender and recipient obtain the same key | IND-CPA for a passive candidate; IND-CCA2 for an active-security claim |
| AKE | Session creation, message processing, acceptance, key output | Matching honest sessions agree and authenticate the specified peer | Session-key indistinguishability and authentication in a named model |

These are separate claim families. A signature authenticates public data; a KEM
establishes confidential key material. An AKE protocol additionally binds
identities, roles, and sessions. Its corruption and exposure rules must be
defined; a KEM theorem alone does not establish an AKE theorem. [S1] [S5]

### Security vocabulary

| Notion | Meaning and scope |
| --- | --- |
| EUF-CMA | Existential unforgeability under adaptive chosen-message attack: produce a valid signature for a message never submitted to the signing oracle. |
| SUF-CMA | Strong unforgeability under adaptive chosen-message attack: produce a valid message/signature pair never returned by the signing oracle, including a different signature for an already signed message. |
| IND-CPA | Indistinguishability under chosen-plaintext attack. For PKE, hide which equal-length selected message was encrypted. For a KEM, distinguish the actual encapsulated key from an independent uniform key. No decryption/decapsulation oracle is provided. |
| IND-CCA1 | The corresponding indistinguishability game with a decryption/decapsulation oracle available only before the challenge. |
| IND-CCA2 | The oracle remains available after the challenge, with the challenge ciphertext excluded. In this contract, `IND-CCA` means `IND-CCA2`. |
| OW-CPA / OW-CCA | One-wayness: recover the entire challenge plaintext or encapsulated key, under the specified distribution and oracle access. This can leave partial information exposed. |
| NM-CPA / NM-CCA | Non-malleability under specified oracle access: prevent an adversary from constructing ciphertexts whose plaintexts satisfy a prohibited relation to the challenge plaintext. Cite the exact game. |
| Key-recovery resistance | Prevent recovery of the secret key or an equivalent representation. This alone does not establish unforgeability or confidentiality. |
| Proof of knowledge (PoK) | A specified extractor obtains a witness from a sufficiently successful prover, with explicit knowledge error and runtime. |
| HVZK / ZK | Honest-verifier zero knowledge / zero knowledge: specify which verifier class and simulator are covered. HVZK is not a claim against every malicious verifier. |
| Forward secrecy / KCI resistance | AKE properties under specified secret-exposure schedules. Key-compromise impersonation (KCI) asks whether compromising one party permits impersonating another party to it. |
| PPT / QPT; ROM / QROM | Classical / quantum polynomial-time adversaries; classical / quantum random-oracle models. These specify the model, not a security outcome. |

The signature notions follow [S2] and [S3]; the encryption oracle distinctions
and non-malleability vocabulary follow [S4]; KEM terminology follows [S1].
For a fixed primitive and matching model, IND-CCA2 implies IND-CCA1 implies
IND-CPA, and SUF-CMA implies EUF-CMA. There is no single ordering that turns a
signature theorem into a KEM or AKE theorem.

### Record the actual security games

Let `lambda` be the security parameter. Define `negl(lambda)` to mean a function
smaller than every inverse polynomial for sufficiently large `lambda`.
Declare all advantage conventions, query bounds, and input-length limits.

**Signatures.** Generate `(pk, sk) <- KeyGen(1^lambda)` and give `pk` to the
adversary. Answer adaptively chosen signing queries, recording their messages
in `M` and returned pairs in `T`. For a final `(m*, sigma*)`:

- EUF-CMA win: `Verify(pk, m*, sigma*) = 1` and `m* not in M`.
- SUF-CMA win: `Verify(pk, m*, sigma*) = 1` and `(m*, sigma*) not in T`.

The advantage is the win probability. Specify whether queries are classical,
even when the adversary has quantum computation. Superposition signing access
requires a separately defined quantum-query forgery game; do not silently
reuse the classical lists `M` and `T`.

**PKE.** Give `pk` to the adversary, obtain admissible equal-length
`(m0, m1)`, sample a uniform bit `b`, and return `c* <- Enc(pk, mb)`.
The adversary outputs `b'`. This document uses advantage
`abs(Pr[b' = b] - 1/2)`. CPA/CCA1/CCA2 differ in the oracle access above.
State every other restriction on the message space and challenge selection.

**KEM.** Generate `(pk, sk) <- KeyGen(1^lambda)` and
`(c*, K0) <- Encaps(pk)`. Independently sample `K1` uniformly from the
declared key space, and a uniform bit `b`. Give `(pk, c*, Kb)` to the adversary.
The advantage is `abs(Pr[b' = b] - 1/2)` with the stated oracle access.
Decapsulation queries use the real `sk` in both worlds. KEM key recovery and
this real-or-random challenge are different goals.

**AKE.** Choose a published model and its version, or define the complete game.
State session matching, peer identity, acceptance, `Send`, `Reveal`,
`Corrupt`, any ephemeral-state reveal, and the `Test` freshness predicate.
Record which unilateral or mutual authentication property is claimed.
Forward secrecy must survive precisely the exposures the claim permits.
An AKE experiment without a freshness definition is incomplete. [S5]

For CCA games, define ciphertext serialization and equality. Do not quietly
exclude every ciphertext with the same mathematical endpoint as `c*`:
that can remove legitimate adversarial queries and weaken the claimed game.
If alternate encodings are accepted, analyze them explicitly.

## The six obligations

### O1 — Specify the exact hard problem

Write the instance sampler, adversary input, required output, success predicate,
and bit-complexity model. Identify the secret and its efficient representation.
State whether setup is trusted, transparent, or trapdoored, what must be erased,
and which distribution the theorem covers. Any statistical or computational
replacement of the real key distribution needs its own argument.

For EndRing, distinguish a complete evaluable endomorphism-ring basis, an
abstract quaternion order, one non-scalar endomorphism, a connecting isogeny,
and an evaluable Hom module. State how representations are converted and the
cost. Each cited equivalence must apply to the exact distribution, auxiliary
data, and output representation used here.

**Discharge artifact:** a formal problem statement, sampler, representation
specification, named assumptions, and citations with provenance.

### O2 — Write every honest-party algorithm

Give input/output domains, randomness, encodings, validation, failure behavior,
and pseudocode for every required interface. Include setup and key generation.
Account for field operations, sampling retries, memory, preprocessing, and bit
length. Distinguish worst-case polynomial time from expected polynomial time
and state the success/tail bounds used for the latter.

A mathematical existence statement is not an executable subroutine. Name
missing lifts, inversions, translations, and samplers as open obligations.
An exponential enumeration may establish a finite definition while leaving
the efficient-algorithm obligation open.

**Discharge artifact:** complete algorithms and runtime/memory arguments,
with implementation and measurements separately labeled when available.

### O3 — Prove correctness under the actual distributions

State whether the guarantee averages over key generation or holds per valid
key, and whether it covers every allowed message or a defined distribution.
Include coins, rejection sampling, exceptional inputs, and decryption failures.
For the declared domains and probability spaces, prove:

```text
Signature: Pr[Verify(pk, m, Sign(sk, m)) = 1] >= 1 - epsilon_sig(lambda)
PKE:       Pr[Dec(sk, Enc(pk, m)) = m]       >= 1 - epsilon_pke(lambda)
KEM:       Pr[Decaps(sk, c) = K]            >= 1 - epsilon_kem(lambda)
           where (c, K) <- Encaps(pk)
AKE:       matching honest accepting sessions output equal keys,
           except with the declared agreement-error bound
```

For negligible-error correctness, justify each `epsilon` bound. For
perfect correctness, prove the relevant error is zero. PKE recovery must return
the actual selected message. An invariant constant across messages or a
decoder returning only an orbit does not discharge that obligation.

**Discharge artifact:** a quantified correctness theorem and failure bound;
round-trip tests are supporting implementation checks, not that theorem.

### O4 — Identify the mechanism that supplies the functionality

For signatures, show how the secret enables message-bound verifiable outputs
while the required forgery game remains hard. If using identification followed
by Fiat–Shamir, specify the relation, completeness, soundness/extraction,
simulation property, challenge space, transcript binding, and the transform
theorem's exact hypotheses. This is one construction route, not a universal
requirement on all signatures.

For a KEM or PKE, identify the public sender operation and the recipient's
efficient secret-dependent recovery operation. Prove that they meet at the
same key or selected message. List every extra recipient secret.

In an EndRing proposal, write the precise `SecretLift`, `Complete_2`, or
`EndpointLift` interface if one is needed: inputs, output representation,
uniqueness or acceptable equivalence, runtime, failure bound, and how its
output recovers the key/message. Treat these names as obligations, never
available oracles. Compare the identical public-data operation to justify any
claimed secret advantage. A publicly computable endpoint hash or a constant
invariant does not supply a confidential shared key.

**Discharge artifact:** a functionality lemma and the exact private operation,
or a named remaining obligation. For AKE, also supply identity/session binding.

### O5 — Give the security reduction in the correct direction

For each security claim, construct a solver for the named assumption using an
attacker on the complete scheme. For an EndRing-only claim the direction is:

```text
Input: EndRing challenge sampled from the stated hard distribution
Use:   a successful attacker on the stated scheme security game
Output: a valid solution to that EndRing challenge
```

Describe challenge embedding, public-key distribution, oracle simulation,
extraction, aborts, rewinding/programming, and runtime. Give an explicit bound,
for example `Adv_game(A) <= L * Succ_problem(B) + delta`, with polynomial
loss `L`, negligible error `delta`, and polynomial solver runtime if asserting
an asymptotic implication. Quantify every algorithm and assumption.

For multiple assumptions, write the actual bound and logical dependency.
If an intermediate assumption is needed, define its game and distribution
separately; record whether a reduction to EndRing exists or remains open.
Do not relabel it as EndRing hardness. Showing that an EndRing solver can break
the scheme exhibits an attack route, not this security reduction.

**Discharge artifact:** a theorem, worked reduction, quantitative loss, and
model statement. A classical rewinding proof does not automatically cover QPT
adversaries or the QROM.

### O6 — Evaluate the complete adversarial view

List everything disclosed: curves, torsion images, hints, bases, transcripts,
public parameters, ciphertexts, signatures, repeated queries, validation
responses, and observables such as timing where implementation security is
claimed. State the threat boundary and account for omitted channels explicitly.
The assumption and simulation must cover the actual public information.

Define rejection and parsing behavior. Evaluate message/key collisions,
alternate encodings, malformed inputs, repeated use, and oracle queries within
the chosen game. Include a public-data control for a claimed recipient-only
operation and a known-false control for a proposed proof implication.
State concrete parameter security separately from asymptotic hardness.

**Discharge artifact:** the complete threat model, adversarial tests with exact
scope, and analysis of their connection to the formal game. Experimental
success is not a security proof; timeout or implementation failure is not a
mathematical obstruction.

## Agent review and outcome

All six obligations are required. Primitive-specific subrequirements can be
inapplicable with a reason; a missing algorithm or proof is `open`.
Use `open | proposed_discharge | reviewed_discharge | contradicted` for each
obligation. A `reviewed_discharge` must cite the independently produced review
artifact; never manufacture an attestation.

- **Candidate:** an explicit proposal with named open obligations and a next
  action. Record whether its finite or efficient functionality is established.
- **Construction:** the required algorithms, correctness, and security
  arguments are supplied and reviewed under all named assumptions and models.
  State every condition and the remaining concrete-security limitations.
- **Scoped obstruction:** a counterexample or argument refutes an identified
  claim for a stated construction family and parameter domain. Name the
  affected obligation and the successor path. Do not generalize to all
  EndRing-based constructions.

These are artifact verdicts, not replacements for hypothesis/goal statuses.
The Coordinator alone makes official scientific state transitions through
the existing committed review and archive process. This document supplies no
new scheme, impossibility theorem, experiment result, or status transition.

## Sources and provenance

The definitions above are paraphrases; the six-obligation organization is this
repository's review rubric. Sources were opened on **2026-10-05** by the
**Codex PR-author session**. Their provenance is `retrieved`. Scope is stated
below so a metadata/abstract read is not represented as a full proof audit.

| Key | Primary source and inspected scope |
| --- | --- |
| S1 | [NIST SP 800-227, September 2025][S1], sections 2.2–2.3 and authentication discussion in section 4.2: KEM correctness, real-or-random security, oracle access, and protocol composition requirements. |
| S2 | [Goldwasser, Micali, Rivest, 1988][S2], sections 1–2: adaptive chosen-message attacks, signature syntax, and distinctions between key recovery and forgery. |
| S3 | [Bellare and Shoup, PKC 2007][S3], section 2, “Signatures”: ordinary versus strong chosen-message unforgeability. |
| S4 | [Bellare, Desai, Pointcheval, Rogaway, 1998][S4], sections 1.1–1.2 and 2.1–2.3: PKE indistinguishability, CCA1/CCA2 access, and non-malleability. |
| S5 | [Canetti and Krawczyk, 2001/040][S5], paper landing page and abstract: a named key-exchange analysis framework; this read does not discharge any candidate's session-security theorem. |
| S6 | [SQIsign specification, version 2.0, February 5, 2025][S6], sections 4.1 and 10.1: an identification/Fiat–Shamir route and explicit hinted-problem assumptions in the ROM. This source is not being cited as an EndRing-only KEM or a QROM theorem. |

[S1]: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-227.pdf
[S2]: https://people.csail.mit.edu/rivest/pubs/GMR88.pdf
[S3]: https://iacr.org/archive/pkc2007/44500201/44500201.pdf
[S4]: https://cseweb.ucsd.edu/~mihir/papers/relations.pdf
[S5]: https://eprint.iacr.org/2001/040
[S6]: https://sqisign.org/spec/sqisign-20250205.pdf
