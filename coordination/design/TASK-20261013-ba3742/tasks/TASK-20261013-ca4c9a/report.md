# EigenX/CEST-PKE six-obligation and reduction audit

Task: `TASK-20261013-ca4c9a`
Batch: `BATCH-44a1ce`
Goal: `GOAL-SSI-2fa82a`
Role: independent idea-generator / research-deep producer
Execution: **zero scientific, implementation, formalizer, benchmark, and parameter-selection runs**

## Outcome

The requested producer packet is complete, but **EigenX is not a complete
cryptographic construction**. EigenX is the existing CEST-PKE candidate, not a
new scheme. The accepted-key message-recovery identity and a classical-ROM
reduction to the separately named `CEST-XFER-KI` game can be stated precisely.
The EndRing claim cannot: the correctly directed chain reaches, at most, a
same-scalar transfer point on the ciphertext line. No supplied arrow turns
that capability into a global endomorphism evaluator, an adaptive bounded-
OneEnd oracle, or a complete rank-four basis of `End(E)`.

The strongest new producer derivation is narrower and useful. In the declared
prime-order basis, a candidate transfer point is publicly and **uniquely**
recognizable with two pairing equations. Consequently, a classical-ROM IND
attacker can be converted, by random-oracle query inspection, into a solver for
computational scalar transfer without a `q_H` guessing loss. This sharpens the
boundary; it does not connect scalar transfer to EndRing.

No security, novelty, practicality, performance, post-quantum, or deployment
claim is made. Every new derivation awaits the frozen independent J4/J5 review.

## Request-to-evidence accounting

| Requested item | Status in this packet | Exact evidence or gap |
| --- | --- | --- |
| Bind EigenX to the canonical candidate | Complete | EigenX is CEST-PKE; no new identity or version was created. |
| Fill O1--O6 using allowed statuses | Complete as an audit | `eigenx-scheme-contract.yaml`; O1/O2/O5 are `open`, O3/O4/O6 are `proposed_discharge`; none is reviewed. |
| Type every reduction arrow | Complete for the frozen chain | `reduction-boundary.yaml` RB-00--RB-11 gives inputs, distributions, simulator, extractor, loss, runtime, earliest gap, and value. |
| Keep `CEST-XFER-KI` separate from EndRing | Complete | RB-03/RB-04 end at scalar transfer; RB-01/RB-02/RB-05/RB-06/RB-08 remain open. |
| Label the reverse route | Complete | RB-10 is `complete EndRing -> decrypt`, an attack route with no security-reduction value. |
| Exercise scalar, quotient, pairing, malformed/repeated/CCA/model controls | Complete symbolically | Controls are recorded in both YAML artifacts and below. No experiment was run. |
| Complete EigenX as a secure EndRing PKE | **Blocked / not established** | Missing efficient setup and selector, challenge embedding, complete-ring extraction, adaptive coverage, independent review, parameters, and active/quantum security. |

## Frozen construction

For an accepted key, the public key contains a prime-order basis `(P,A)` of
`E[q]`, where

```text
A = psi_E(P),        e_q(P,A) != 1.
```

Encryption samples `r` uniformly from `Z_q^*`, sets

```text
R = [r]P,
S_snd = [r]A,
v = m XOR H_pad("CEST-PKE/v1" || pk_ser || Encode(R) || Encode(S_snd)),
```

and returns `(pk_ser,R,v)`. Decryption accepts only `R` in `<P>`, recomputes
`psi_E` from the declared full-ring witness, and uses

```text
S_rec = psi_E(R).
```

For an accepted key and every allowed message and nonce,

```text
psi_E([r]P) = [r]psi_E(P) = [r]A.
```

Thus sender and recipient use identical canonical random-oracle input and
recover the selected plaintext. This is a conditional, per-accepted-key
algebraic statement. It supplies no termination bound for `KeyGen` and no
security theorem.

## O1--O6 disposition

| Obligation | Status | Narrow finding | What prevents completion |
| --- | --- | --- | --- |
| O1 exact hard problem | `open` | `AuxEndRing_CEST`, `CEST-XFER-KI`, and their exact intended auxiliary data are named. | The real-key sampler is not executable/proved. Bare EndRing input `E` cannot be embedded into a real key containing `A=psi_E(P)` without `W` or an equivalent evaluator. The auxiliary problem's hardness is not established. |
| O2 honest algorithms | `open` | `KeyGen`, `Enc`, and `Dec` syntax and failure classes are explicit. | `TrapCurveGen`, exact full-ring certification, `CanonicalBoundedEnd`, normalized-map uniqueness/cost, accepted mass, retry tails, and total memory/time remain missing. |
| O3 quantified correctness | `proposed_discharge` | Actual-message recovery is perfect for every accepted key, message, and nonzero nonce, assuming correct O2 interfaces. | The theorem is conditional on accepted keys and incomplete algorithms; no independent rederivation exists yet. |
| O4 functionality mechanism | `proposed_discharge` | Public `[r]A` and private `psi_E([r]P)` meet exactly. | On accepted ciphertexts the mechanism factors through `EvalLine_(P,A):[x]P -> [x]A`; complete-ring necessity is not shown. |
| O5 correctly directed reduction | `open` | Classical IND-CPA reduces to `CEST-XFER-KI`; query inspection further reaches computational scalar transfer. | No arrow lifts scalar transfer to a global `psi_E`, adaptive OneEnd, or complete EndRing. The only complete-ring arrow runs in reverse. |
| O6 complete adversarial view | `proposed_discharge` | The classical IND-CPA view, byte parsing, pairings, repetitions, and rejection behavior are enumerated. | IND-CCA2 is explicitly broken; QPT/QROM, multi-user, malicious-key/setup, side-channel, concrete-parameter, and implementation claims are absent. |

`proposed_discharge` means an unreviewed candidate argument, not a completed
obligation. Since no independent review artifact exists, all O1--O6 remain in
the assessment's open-obligation list.

### Correction to the original O1 grading

The original producer contract marked O1 `proposed_discharge`. This audit
tightens it to `open`. The issue is not nomenclature: the supposed exact
instance sampler calls the incomplete honest `KeyGen`, and the advertised bare
EndRing challenge does not contain the secret-dependent `A` needed to simulate
the real public-key distribution. The exact change is to retain the two named
games as conditional definitions while leaving the hard-problem and
distribution bridge obligation open.

## Pairing audit: nonuniqueness, then uniqueness

Let `g=e_q(P,A)`. Because `q` is prime and `g != 1`, `g` has order `q` and
`P,A` form a basis of `E[q]`. Write a proposed transfer point as

```text
T = [x]P + [y]A.
```

The equation used in the original pairing control,

```text
e_q(P,T) = e_q(R,A),
```

becomes `g^y=g^r`, so it fixes `y=r` but leaves `x` arbitrary. It accepts the
entire coset

```text
[r]A + <P>,
```

and therefore has `q` solutions. On its own it does not uniquely verify the
hash input.

However, public data also permits the second equation

```text
e_q(A,T) = 1.
```

This is `g^(-x)=1`, hence `x=0`. Together with q-torsion membership, the two
equations uniquely accept `T=[r]A`. This yields a public unique-transfer
verifier; it does not compute the point.

Two consequences follow.

1. A classical-ROM reduction may inspect `H_pad` queries and recognize the
   unique correct scalar-transfer point without guessing one of `q_H` queries.
2. There is a public target-group discrete-log route: compute
   `h=e_q(R,A)=g^r`, recover `r` in `<g>`, and output `[r]A`. This is only an
   attack-route upper bound. No concrete algorithm, parameter cost, or measured
   security level was assessed.

## Correctly directed reduction boundary

The desired EndRing proof must start with an EndRing challenge and end with a
complete ring basis:

```text
EndRing challenge
    + successful EigenX IND attacker
        -> complete evaluable rank-four End(E) basis.
```

The frozen packet supports only this proposed prefix:

```text
IND attacker
    -> CEST-XFER-KI distinguisher
    -> scalar-transfer point S=[r]A.
```

For the first arrow, embed the real-or-random intermediate string `K` as
`m_beta XOR K`. In the real world this is the honest challenge; in the random
world it is independent of `beta`. Under the aligned advantage convention,

```text
Adv_IND-CPA(A) <= Adv_CEST-XFER-KI(D).
```

For query extraction, mask the challenge with an independent uniform string,
simulate the classical random oracle lazily, and apply the two-pairing verifier
to candidate points in the attacker's queries. If an attacker has IND advantage
`epsilon`, it must ask the correct query with probability at least `epsilon`;
otherwise its view is independent of `beta`. Therefore the proposed bound is

```text
Succ_CEST-XFER-COMP(B) >= Adv_IND-CPA(A),
```

apart from declared parsing failures. Runtime is `T_A` plus `O(q_H)` parsing,
subgroup, and pairing checks; storage is `O(q_H)`. This is a classical-ROM
argument only. It is not a QROM extractor.

The remaining chain is open:

```text
scalar-transfer point
    ?-> reusable evaluator on <P>
    ?-> global rational-map psi_E
    -> one OneEnd output on initial E
    ?-> bounded OneEnd answers on every adaptive internal curve
    -> complete EndRing basis (source-supported only under that oracle).
```

The first bare-EndRing gap occurs even earlier. Given only a challenge curve
`E`, a reducer cannot sample the exact public point
`A=CanonicalBoundedEnd(E,W,B)(P)` without the missing `W` or an equivalent
evaluator. Defining `AuxEndRing_CEST` to hand the reducer the entire public key
removes this embedding mismatch by definition, but does not provide extraction.

## Evaluator-quotient boundary

Every accepted ciphertext has `R in <P>`. On that domain decryption needs only

```text
EvalLine_(P,A)([x]P) = [x]A.
```

As a mathematical homomorphism this function is already determined by public
`P,A`. Its presumed hardness is computational: extracting or transporting the
unknown scalar `x`. Returning transfer values on this line supplies no action
on a second independent torsion direction and no global rational map. A
discrete-log solver implements the same line evaluator without computing a
complete endomorphism ring.

This gives a scoped black-box obstruction: a reduction that treats the
attacker only as a transfer oracle receives no ring-identifying behavior beyond
the public-key-determined line map. To pass this boundary it needs a new,
checkable lemma or interface that exploits additional distributional structure
and outputs a full evaluator or the adaptive OneEnd answers. This is not a
universal impossibility result; a non-black-box or materially different
construction could escape the boundary.

## Reverse route is an attack, not a proof

Given a complete evaluable ring basis, an algorithm can run
`CanonicalBoundedEnd`, evaluate `psi_E(R)`, query `H_pad`, and decrypt. Thus

```text
complete EndRing solver -> break EigenX.
```

This shows full-ring sufficiency for attack. It neither shows full-ring
necessity for decryption nor constructs

```text
EigenX attacker -> complete EndRing solver.
```

Using the reverse arrow as the security reduction is rejected by the frozen
proves-too-much control.

## Exercised controls

| Control | Symbolic result | Scope |
| --- | --- | --- |
| Literal scalar slice `psi=[s]` | Then `A=[s]P` and `e_q(P,A)=1`, so the frozen key validator rejects it. | It remains an abstract cyclic hashed-DH regression, not an in-distribution counterexample. |
| Evaluator quotient | Replacing `W` with an efficient `EvalLine_(P,A)` changes no accepted decryption output. | Complete-ring necessity is unproved; no universal nonextractability theorem follows. |
| Pairing, one equation | Accepts `[r]A+xP` for all `x`. | Nonunique verifier. |
| Pairing, two equations | Uniquely accepts `[r]A`. | Enables classical-ROM query extraction and a gap-style verifier. |
| Pairing target DLP | `e_q(R,A)=e_q(P,A)^r`; target DLP yields `r`, then `[r]A`. | Attack-route upper bound only; no cost was measured. |
| Wrong key / malformed bytes | The specified parser returns one failure symbol for embedded-key mismatch, alternate encodings, invalid lengths, and invalid points. | Constant-time and side-channel uniformity are not established. |
| Repeated nonce | Repeats `R` and the pad, revealing plaintext XOR. | Collision probability is at most `Q(Q-1)/(2(q-1))` for `Q` independent nonzero nonces. |
| IND-CCA2 | Query `(pk,R,v XOR Delta)` after seeing `(pk,R,v)`; decryption reveals `m_beta XOR Delta`. | One-query deterministic break of this frozen unauthenticated construction. |
| Classical/quantum model | The proposed proof forwards and inspects classical random-oracle queries. | No QPT, QROM, or post-quantum theorem. |
| Full-ring solver | Decrypts through `psi_E(R)`. | Reversed attack route; no security value. |

## Honest-algorithm gaps

The candidate still lacks executable, costed versions of the following.

- `TrapCurveGen` with an exact output distribution, a complete transported or
  otherwise constructed ring, and a non-negligible accepted mass.
- A certificate and polynomial verifier that the proposed rank-four order is
  exactly `End(E)`, rather than a proper suborder.
- `CanonicalBoundedEnd` with representation-independent rational-map
  normalization, semantic duplicate removal, deterministic selection, and
  polynomial time/memory on the exact sampler support.
- A complete parameter-generation and exact-order-`q` point-sampling analysis,
  including all retries, output lengths, failure tails, and extension-field
  costs.

Consequently, the accepted-key correctness lemma does not upgrade the proposal
to an efficient PKE construction.

## Exact next construction-or-obstruction step

After the producer snapshot, the frozen J4/J5 reviewer should independently
rederive the pairing verifier, RB-03/RB-04, the evaluator quotient, and each
O1--O6 status. Advancement toward the requested EndRing claim requires one of
the following reviewed artifacts:

1. A direct reduction that receives the exact EndRing challenge, simulates the
   complete real EigenX view, and extracts a complete evaluable rank-four basis
   with explicit success, abort, loss, time, memory, and representation bounds;
   or
2. a polynomial `Lift_XFER_to_AdaptiveOneEnd` that starts from the exact
   attacker-derived scalar-transfer capability, uses no secret-correlated path,
   orientation, ideal, torsion label, tag, or ring advice, and answers every
   adaptive bounded-OneEnd query with a whole-transcript success/cost bound.

If neither interface survives independent review, the current named problem
remains open and the next construction must change the recipient mechanism so
that its challenge-simulatable transcript contains ring-identifying behavior.
Adding another encryption wrapper around the same line transfer does not
address O5.

## Sources and provenance

No external source was retrieved in this task. The following internal frozen
artifacts were read in full:

- [Original CEST candidate](../../../TASK-20261007-9c36ba/tasks/TASK-20261007-913665/candidate.md), all sections; provenance `internal`.
- [Original scheme contract](../../../TASK-20261007-9c36ba/tasks/TASK-20261007-913665/scheme-contract.yaml), complete artifact; provenance `internal`.
- [Original proof-search map](../../../TASK-20261007-9c36ba/tasks/TASK-20261007-913665/proof-search-map.yaml), complete artifact; provenance `internal`.
- [Original provenance record](../../../TASK-20261007-9c36ba/tasks/TASK-20261007-913665/provenance.yaml), complete artifact; provenance `internal`.
- `TASK-20261009-daf6ab/source-ledger.yaml`, the frozen Page--Wesolowski source statements and unsupported-transfer boundary; provenance `internal`, primary-source verification owned by `TASK-20261009-daf6ab`.
- The EigenX alias record, canonical problem record, batch opening, queue card,
  and frozen J1--J6 review plan; provenance `internal`.

The pairing, query-extraction, CCA2, and quotient arguments in this report are
producer derivations from the frozen scheme definition. They are not
independently reviewed findings. The complete machine-readable arrow accounting
is in `reduction-boundary.yaml`; the six-obligation artifact is in
`eigenx-scheme-contract.yaml`.
