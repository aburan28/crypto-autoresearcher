# EndRing PKE candidate funnel

Date: 2026-10-07

Goal: `GOAL-SSI-2fa82a`

Question: `RQ-SSI-1946c9`

Batch: `BATCH-65c2dd`

## Status and claim boundary

This document freezes a research method. It does not supply a secure scheme,
prove EndRing hardness, or establish novelty. Every construction produced by
this batch is a **candidate** until all six obligations in
`docs/scheme-construction-contract.md` have independent reviewed discharges.
The existing scoped C-star, recipient-lift, transporter, evaluator, and
admission failures remain regression tests; they are not a universal
impossibility result.

The primitive is classified before evaluation. A mechanism with
`KeyGen/Enc/Dec` and actual selected-message recovery is evaluated as PKE. A
mechanism that only agrees on a random key is a KEM candidate and does not meet
this goal's PKE completion criterion without a separately specified, reviewed
composition. A KEX or AKE transcript is out of scope.

## Alternating loop

Each cycle is frozen before its producers run:

1. **Generate independently.** Two idea-generator sessions receive the same
   problem boundary and prior negative controls, but may not read one another's
   output. They must choose materially different functionality mechanisms and
   populate separate six-obligation contracts.
2. **Normalize.** Each producer gives exact domains, encodings, algorithms,
   security game, EndRing challenge distribution, public view, private
   operation, correctness statement, and a correctly directed reduction map.
   Missing algorithms are named obligations, never implicit oracles.
3. **Snapshot.** The Coordinator archives both packets before review. Reviewers
   inspect the same immutable bytes.
4. **Evaluate uniformly.** A validator owns syntax/correctness joints O1--O3;
   a red team owns functionality, reduction direction, and attack-surface
   joints O4--O6. Reviewers are mutually blind and report `holds`, `breaks`, or
   `inconclusive` on owned joints, not a whole-claim vote.
5. **Compose.** The Coordinator applies deterministic gates:
   - any ill-typed public encryption or failure to recover the actual message
     kills the PKE reading;
   - a public operation identical to the alleged recipient-only operation
     kills the confidentiality mechanism;
   - a reduction running `EndRing -> break scheme` without the reverse solver
     is an attack route, not a security proof;
   - an uncovered auxiliary assumption is separated and named;
   - surviving conditional candidates remain candidates, never constructions.
6. **Feed gaps forward.** The composer emits a machine-readable gap packet,
   containing only failed joints, counterexamples, missing interfaces, and
   preserved subclaims. A fresh idea generator uses that packet to revise or
   replace one mechanism. It may not erase the original candidate or relax a
   security game after seeing a failure.
7. **Re-evaluate.** The revised candidate is snapshotted and attacked under the
   same six obligations. Another cycle is admitted only if it targets a named
   decision-changing gap; an empty queue is not filled with cosmetic variants.

## Candidate diversity rule

The first two producers must differ in the operation that provides recipient
advantage, not merely in serialization, parameters, or hash/KDF choice. Each
packet states its nearest prior construction among Séta, SiGamal/C-SiGamal,
LIT-SiGamal, and key-updatable supersingular PKE. Novelty remains `unverified`
unless primary sources are read and the delta is checkable.

## Six-obligation scorecard

| Gate | Required question | Immediate failure signature |
| --- | --- | --- |
| O1 | What exact EndRing instance, distribution, auxiliary data, output representation, and setup are assumed? | “EndRing” is only a motivation label, or the real public-key distribution cannot be embedded. |
| O2 | Are `KeyGen`, `Enc`, and `Dec` typed, public/secret inputs separated, and polynomial-time subroutines explicit? | `Enc` calls the secret ring, or a `SecretLift`/`EndpointLift`/`Complete_2` oracle is merely named. |
| O3 | Does decryption recover the selected message under quantified key/message/coin distributions? | It returns only an orbit, endpoint, invariant, or constant; exceptional keys are unbounded. |
| O4 | Which public sender operation and secret-dependent recipient operation meet, and why is the latter not public? | The same public data computes both, or correctness uses an unproved lift. |
| O5 | Can a scheme attacker be converted into a solver for the exact EndRing challenge with explicit loss and oracle simulation? | Only the forward attack `EndRing solver => scheme break` is shown, or an intermediate assumption is relabeled EndRing. |
| O6 | Does the model cover every curve, torsion image, hint, encoding, ciphertext, validation response, repetition, and oracle query? | Auxiliary data falls outside the assumption, alternate encodings bypass challenge exclusion, or malformed inputs leak. |

## Frozen controls

- **Public-data control:** run the claimed recipient-only computation using the
  identical public data and charge every enumeration. Public success destroys
  the asserted asymmetry.
- **Known-false control:** apply the security argument to a construction where
  the ciphertext directly includes the plaintext/key. The argument must fail
  at a named step.
- **Wrong-key and malformed-ciphertext controls:** decryption must reject or
  return the specified failure symbol without creating a stronger oracle than
  the declared game.
- **Distribution control:** compare the real public-key distribution with the
  EndRing challenge distribution and exhibit the exact compiler or the gap.
- **Actual-message control:** distinguish recovery of `m` from recovery of an
  endpoint, kernel, equivalence class, or hash that is message-independent.
- **Prior-failure regression:** no candidate may treat `BaseGen`, `Eval2`,
  target-frame reconstruction, normalized quotient lifting, or a digit-loop
  tie rule as available without an explicit algorithm and scope.

## Cycle outputs

Every cycle retains both successful and failed candidates, their complete
contracts, independent reports, gap packet, editable diagram source, SVG, and
PDF report. Evidence language separates `proposed`, `derived`, `reviewed`, and
`measured`; this batch contains no measured scientific run.

## Stopping and continuation

The cycle stops after the second evaluation in `BATCH-65c2dd`. A later cycle
requires a new Coordinator decision and batch. A candidate may be promoted for
implementation design only if O1--O4 have no breaking joint and O5--O6 have a
precise, separately named security target with no hidden assumption. Security
support requires much more: reviewed reductions, implementations, experiments
where relevant, concrete parameters, and the repository's normal evidence
gates.
