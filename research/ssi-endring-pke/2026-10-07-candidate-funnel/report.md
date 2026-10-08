---
title: "EndRing PKE candidate funnel"
subtitle: "GOAL-SSI-2fa82a / BATCH-65c2dd"
date: "2026-10-07"
geometry: margin=0.75in
fontsize: 10pt
colorlinks: true
---

# Result

This batch implemented an explicit **propose -> evaluate -> gap-feed ->
propose -> evaluate** research loop for public-key encryption motivated by
the supersingular endomorphism-ring problem. It generated three candidate
packets, froze both review inputs, ran independent obligation-based reviews,
and produced **zero finalists**.

No secure PKE, EndRing security reduction, novelty result, implementation
result, parameter set, or universal impossibility theorem was established.
All work was symbolic: zero scientific, implementation, formalizer, benchmark,
or parameter-selection runs were performed. The evidence supports scoped
candidate findings only. [Method] [Final]

![Candidate funnel. Proposed material is yellow, independent review is blue,
breaks are red, and the next action is green. The diagram is a navigation aid,
not evidence.](funnel-flow.svg){ width=100% }

# Method

The frozen methodology requires materially different recipient mechanisms,
complete PKE algorithms and encodings, immutable snapshots before review,
joint ownership rather than whole-claim voting, known-false controls, and one
structured gap-fed revision. A KEM-only result does not satisfy the PKE goal.
The batch stops after the second evaluation. [Method]

Every candidate was judged against six obligations:

| Gate | Question |
|---|---|
| O1 | Is the exact EndRing problem, distribution, auxiliary view, representation, and setup specified? |
| O2 | Are KeyGen, Enc, and Dec honest, typed, public/secret separated, and polynomial-time? |
| O3 | Does Dec recover the selected plaintext for quantified keys, messages, coins, and failures? |
| O4 | What secret-dependent recipient operation meets the public sender operation, and why is it not public? |
| O5 | Does a scheme attacker yield a solver for the exact EndRing challenge in the correct direction? |
| O6 | Is the complete adversarial view covered, including encodings, malformed inputs, repetition, and auxiliary data? |

The controls included public recovery, leaked-plaintext known-false,
wrong-key/malformed ciphertext, real-distribution embedding, actual-message
recovery, and regression against previously failed lift/evaluator mechanisms.
[Plan1] [Plan2]

# Round 1: two independent candidates

## Candidate A: CEST-PKE

**Proposed mechanism.** A complete evaluable witness for `End(E)` selects an
endomorphism `psi_E`. The public key contains `P` and
`A = psi_E(P)`. Encryption samples `r`, publishes `R = [r]P`, and masks
the message with a hash of `[r]A`. Decryption computes `psi_E(R)`. [A]

**Derived correctness.** For an accepted valid key,

```
psi_E(R) = psi_E([r]P) = [r]psi_E(P) = [r]A.
```

The blind validator independently rederived exact selected-message recovery.
However, O2 breaks because the curve sampler, complete-ring verifier,
canonical endomorphism selector, evaluator bounds, and retry bounds are not
available. [V]

**Security finding.** The red team found no public polynomial transfer
algorithm, so recipient functionality was not directly broken. But decryption
uses only one `psi_E` evaluator: replacing the complete ring witness with
that evaluator leaves every decryption transcript unchanged. The direct
security object is therefore a hashed same-scalar-transfer problem, not the
complete EndRing problem. [R]

The known EndRing implication has the wrong direction:

```
complete EndRing solver -> derive psi_E -> compute transfer -> decrypt.
```

No reduction embeds a bare curve-only EndRing challenge into the real public
key and converts an IND-CPA attacker into a complete evaluable rank-four basis.
O5 therefore breaks. The surviving statement is only a conditional transfer
shell, not an EndRing-secure PKE. [R] [C1]

## Candidate B: ER-McE

**Proposed mechanism.** A canonical encoding of a complete EndRing witness
seeds a deterministic Goppa-code trapdoor. The public operation is raw
McEliece encryption

```
c = m G_pub + e,      wt(e) = t,
```

and the recipient uses the secret Goppa decoder. [B]

**Decisive break.** For distinct challenge messages `m_0,m_1`, compute

```
x_i = c - m_i G_pub.
```

The true residual has weight exactly `t`. If both residuals had weight
`t`, then the nonzero codeword
`(m_0-m_1)G_pub = x_0+x_1` would have weight at most `2t`, contradicting
the declared minimum distance at least `2t+1`. Exactly one residual has
weight `t`; the challenge bit is recovered with probability one, for
advantage `1/2` under the packet's convention. This is a static symbolic
counterexample and required no experiment. [R]

ER-McE is eliminated in its exact syntax. The result does not break general
McEliece, EndRing, or every EndRing-seeded composition. Independently, the
real public matrix cannot be generated from a bare EndRing challenge without
the hidden ring seed, and code decoding remains a separate assumption. [R]

# Composition and gap selection

The first composition copied each joint owner's verdict without voting.
CEST-PKE had a conditional message-transfer identity but broke O2 and O5.
ER-McE broke all five review joints and was eliminated by the public
exact-weight test. No candidate was a finalist. [C1]

One decision-changing gap was selected:

> Make complete EndRing information both sufficient and demonstrably
> necessary for recipient functionality on the exact real public-key
> distribution, and give the correctly directed IND-attacker-to-complete-ring
> reduction.

The gap packet forbade renaming transfer, CDH, torsion-action, or decoding
hardness as EndRing; assuming a missing lift/evaluator; weakening
selected-message IND-CPA; or treating KeyGen provenance as proof that the full
ring is necessary. [G]

# Round 2: gap-fed revision

## RWCT-PKE

The fresh producer saw only the gap packet and contracts. It attempted to
replace the single evaluator with polynomially many noncommutative words
`w_j(B)`, each syntactically involving all four elements of a planted
complete basis `B`. The public key contains
`A_j=w_j(B)(P_j)`; encryption uses `[r_j]A_j`; decryption evaluates
`w_j(B)([r_j]P_j)`. [W]

For a supplied valid planted tuple, the conditional identity

```
w_j(B)([r_j]P_j) = [r_j]w_j(B)(P_j) = [r_j]A_j
```

recovers the selected message. The producer nevertheless returned a scoped
obstruction packet: decryption factors through the finite restricted
evaluators, a bare `E` cannot generate the correlated public images, and an
arbitrary EndRing basis requires an unavailable alignment to the planted word
variables. [W]

## Fresh review

The second packet was frozen at commit `c020468c0e` and evaluated by a fresh
reviewer who did not read the first-round reports. All three revision joints
break; the selected gap is not repaired. [S2] [RR]

The reviewer found:

1. **Ill-typed decryption.** `KeyGen` returns `sk=B`, while `Dec(sk,ct)`
   reads `pp`, `pk`, word descriptors, points, and transcript domains that
   are neither in `sk` nor passed as inputs.
2. **Ambiguous honest zero coins.** Uniform `r_j` includes zero, so honest
   ciphertexts can contain the identity. Correctness requires subgroup
   membership to accept it, whereas an exact-order-`N_j` point test would
   reject.
3. **Syntactic dependence is not semantic dependence.** The allowed word
   `X_1+(X_2-X_2)+(X_3-X_3)+(X_4-X_4)` mentions every variable but collapses
   to `X_1`, replaying the single-evaluator route.
4. **The three reduction arrows remain absent.** Bare `E` does not sample
   the real key, an attacker bit does not yield a complete ring, and an
   arbitrary complete basis is not aligned with the planted variables.

The factorization through restricted evaluators is exact, but it does not
prove a family-level no-go result. No strict efficient quotient, collision
pair, meta-reduction, or reconstruction impossibility was supplied.
Accordingly, the producer's proposed scoped obstruction is **inconclusive**,
not an impossibility theorem. [RR]

# Final scorecard

| Candidate | O1 | O2 | O3 | O4 | O5 | O6 | Disposition |
|---|---|---|---|---|---|---|---|
| CEST-PKE | inconclusive | breaks | conditional identity verified | inconclusive | breaks | inconclusive | transfer shell only |
| ER-McE | breaks | breaks | incomplete conditional claim | breaks | breaks | breaks | eliminated by perfect IND-CPA distinguisher |
| RWCT-PKE | open | open | conditional identity only | open | open / missing reduction | open | selected gap not repaired |

The batch generated three candidate packets, independently evaluated all
three, and found zero candidates with complete O1-O6 discharges. No
implementation or parameter run is warranted for these exact syntaxes.
[Final]

# What the loop learned

- A complete EndRing witness used during KeyGen proves sufficiency only. It
  does not make the complete ring necessary for decryption or extractable
  from an attacker.
- Every public-key field correlated with the hidden witness must be sampled
  from the exact EndRing challenge or justified by an explicit distribution
  compiler.
- The reduction output must be a complete evaluable rank-four basis, not one
  evaluator, a transfer point, torsion action, decoder, endpoint, or planted
  label.
- Syntactic use of four basis variables can cancel. Semantic dependence needs
  a non-factorization or reconstruction theorem.
- Elementary selected-message attacks belong before assumption-level
  analysis; this exposed ER-McE immediately. [Final]

# Exactly one next action

Before proposing another encryption wrapper, define and audit one
basis-independent trapdoor map

```
Trap_E : X_E -> Y_E
```

with all four properties:

1. public instance sampling and forward evaluation are polynomial from a bare
   `E` drawn from the exact EndRing challenge distribution;
2. any complete evaluable basis of `End(E)`, not one planted basis, enables
   polynomial inversion;
3. inversion either provably does not factor through a smaller witness, or a
   reconstruction theorem recovers the complete ring from that witness; and
4. a selected-message IND attacker yields a complete evaluable basis with
   explicit game hops, oracle simulation, loss, runtime, and abort bounds.

If any property is unavailable, the next record should preserve that exact
failed arrow before another PKE syntax is built. The goal remains active; this
batch closes as complete with no finalist. [Final]

# Evidence and reproducibility

- Initial producer bytes were frozen at commit `0f0a92e25e`; the revision
  bytes were frozen at `c020468c0e`. [S1] [S2]
- The initial independence check passed for two mutually blind reports; the
  revision independence check passed for the fresh report. [V] [R] [RR]
- The repository ledger validator returned the inherited baseline of 105
  diagnostics and 1,210 grandfathered legacy diagnostics, with no
  batch-local diagnostic after metadata correction.
- No primary paper was read in this batch. Prior-art comparisons used only
  abstract-level repository pointers, so novelty remains unverified. [R]
- No diagram or PDF is evidence; scientific statements above cite the
  underlying candidate, review, or composition artifact.

# Source index

- [Method] [Frozen methodology](methodology.md)
- [A] [CEST-PKE candidate](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/candidate.md)
- [B] [ER-McE candidate](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-61f3bc/candidate.md)
- [S1] [Initial snapshot receipt](../../../coordination/design/TASK-20261007-9c36ba/archives/TASK-20261007-0ec6c3/snapshot-receipt.json)
- [Plan1] [Initial review plan](../../../coordination/design/TASK-20261007-9c36ba/review-preparation/review-plan.yaml)
- [V] [Blind O1-O3 validation](../../../coordination/design/TASK-20261007-9c36ba/reviews/TASK-20261007-bc6c0f/validation-report.yaml)
- [R] [Initial O4-O6 red-team report](../../../coordination/design/TASK-20261007-9c36ba/reviews/TASK-20261007-385334/red-team-report.yaml)
- [C1] [Initial composition](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-79e571/composition.yaml)
- [G] [Structured gap packet](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-79e571/gap-packet.yaml)
- [W] [RWCT-PKE revision](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-8ab26c/revised-candidate.md)
- [S2] [Revision snapshot receipt](../../../coordination/design/TASK-20261007-9c36ba/archives/TASK-20261007-8116c4/snapshot-receipt.json)
- [Plan2] [Revision review plan](../../../coordination/design/TASK-20261007-9c36ba/review-preparation/revision-review-plan.yaml)
- [RR] [Fresh revision review](../../../coordination/design/TASK-20261007-9c36ba/reviews/TASK-20261007-b6c1ec/revision-review.yaml)
- [Final] [Final composition](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-c47fc6/final-composition.yaml)
