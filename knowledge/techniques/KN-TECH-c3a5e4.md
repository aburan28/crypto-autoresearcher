---
id: KN-TECH-c3a5e4
type: technique
title: >-
  Multi-generator trapdoor pattern -- any protocol fixing several curve points (Pedersen commitments, key images, hash-to-curve constants, proof-system generators) is trapdoored by whoever knows one discrete-log relation among them
tags: [trapdoor, pedersen, trapdoor-commitment, multi-generator, nothing-up-my-sleeve, hash-to-curve, bulletproofs, ring-signature, dual-ec, protocol-level, ecdlp]
confidence: established
complexity: >-
  holder of d with H = dG opens a Pedersen commitment C = mG + rH to any m' by setting r' = r + (m - m')/d (one field inversion); breaks binding of every commitment made with (G, H); an outsider must solve one ECDLP instance to acquire the same power
applicability: >-
  every discrete-log protocol that publishes two or more fixed points and whose binding, soundness or unforgeability proof assumes their relation is unknown; the generalization of Dual EC (KN-TECH-a7e9a8) from state recovery to equivocation and forgery
source_refs: [KN-TECH-a7e9a8, KN-TECH-257dbc, KN-TECH-6ead00]
added: 2026-09-30
superseded_by: null
---

## Mechanism

Pedersen commitment `C = mG + rH` is binding exactly when `log_G H` is
unknown to the committer: with `H = dG`, `C = (m + rd)G` and any `(m', r')`
with `m' + r'd = m + rd` opens it. The same relation breaks:

- **Bulletproof / inner-product generator vectors** `(G_i, H_i)`: a known
  relation lets a prover forge range proofs.
- **Ring-signature key images** and linkable tags derived from a second
  fixed point: a known relation lets a signer produce unlinkable double
  spends or an authority link honest ones.
- **Hash-to-curve constants and "nothing-up-my-sleeve" points**: if the
  point published as `H = hash_to_curve("string")` was in fact chosen as
  `dG`, the string is a decoy (compare the seed argument in
  KN-TECH-031027).
- **Structured reference strings** with independent generators that are in
  fact related.

This is precisely why such points are "trapdoor commitments" in the
literature: the trapdoor is a *feature* when held by a simulator in a
security proof and a *backdoor* when held by a standardizer.

## Why it is the general form of Dual EC

Dual EC (KN-TECH-a7e9a8) is the case where the two points are the DRBG's
`P` and `Q` and the consequence is state recovery. Every other consequence
(equivocation, forgery, linking) follows from the same single secret
`d = log_G H`, so the taxonomy (KN-TECH-6ead00) files the whole family under
one hiding mechanism: a secret scalar whose public image is a pair of points.

## Detectability

None from the points themselves, by definition of the DLP. The public defence
is procedural: derive every auxiliary generator by a specified hash-to-curve
from a fixed public string with no free parameters, or by a verifiable
multi-party ceremony, and publish the derivation so anyone can recompute it.

## Applicability limits

Attacks the protocol, not the curve; any single-generator protocol is
unaffected. Nothing here bears on ECDLP hardness or on GOAL-ECTD-001 except
as a reason such a solver would have immediate consequences: a DLP oracle on
a standard curve would recover every fixed relation ever deployed on it.
