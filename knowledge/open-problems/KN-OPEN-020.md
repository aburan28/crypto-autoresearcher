---
id: KN-OPEN-020
type: open_problem
title: Does quasi-cyclic structure weaken syndrome decoding beyond the DOOM square-root discount?
tags: [code-based, quasi-cyclic, doom, bike, hqc, syndrome-decoding, structural-attack, parameter-selection, open]
confidence: reported
status: open
source_refs: [KN-TECH-061, KN-TECH-060, KN-TECH-059, KN-LIT-7574, KN-LIT-2085, KN-LIT-3735, KN-LIT-7575, KN-LIT-6923]
added: 2026-07-27
superseded_by: null
---

## Statement
Quasi-cyclic (QC) code-based schemes shrink keys by three orders of magnitude by
imposing a cyclic block structure on the parity-check matrix. Current parameter
selection accounts for exactly one consequence: the Decoding One Out of Many
(DOOM) discount, since rotations of a ciphertext supply free extra targets,
worth roughly a square-root factor in the block size (KN-TECH-061).

**Is that the whole cost of quasi-cyclicity?** Or does the QC structure admit a
structural attack -- in the KN-TECH-059 sense, against key security rather than
decoding hardness -- that no current parameter set prices?

## Current state (as reported)
- **The DOOM discount is standard and priced.** QC parameter sets in BIKE and HQC
  include it (KN-LIT-7574).
- **QC structure has already been fatal elsewhere.** Quasi-cyclic and quasi-dyadic
  *compact-key Goppa* variants were broken algebraically (KN-LIT-2395). Those
  breaks exploited the algebraic code family rather than quasi-cyclicity as such,
  but they establish that adding cyclic structure to a code-based key has
  historically cost more than its designers priced.
- **QC-MDPC's known exposure is elsewhere.** The live attack surface for BIKE and
  HQC is decoding failures (KN-TECH-060), not key structure. The absence of a
  structural attack on QC-MDPC is an absence of published results, not a proof.
- **Weak keys exist.** KN-LIT-3735 reports weak-key classes for BIKE. Weak keys
  are a partial structural result: some keys *are* distinguishable and
  exploitable. Whether the class extends is not settled here.
- **NIST treated the QC family's analysis as less mature** than HQC's in round 4
  (KN-LIT-7575), which is an external judgement in the same direction, though it
  was made about decoding-failure analysis specifically.

## Why it matters here
This is the sharpest live instance of the general screen recorded in
KN-TECH-059: efficiency bought with algebraic structure is borrowed against the
structural-attack surface. QC-MDPC bought a 1000x key-size reduction. The field
has priced a square-root discount for it. That asymmetry -- three orders of
magnitude of structure, half an order of magnitude of charged cost -- is exactly
the shape that should attract scrutiny, and it is not resolved by the fact that
no one has broken it yet.

For this program specifically: if the Idea Generator proposes structured
instances of any hard problem to gain efficiency, this is the worked example of
what the corresponding audit has to look like, and of how hard it is to conclude
anything from "no published attack."

## What would close it
- **A distinguisher.** Any efficiently computable invariant separating a QC-MDPC
  public key from a random quasi-cyclic parity-check matrix, at deployed
  parameters, would reopen QC parameter selection entirely.
- **A reduction.** A proof that decoding a random QC code is as hard as decoding
  a random linear code, up to the DOOM factor, would close the question the other
  way. Partial results of this kind may exist in the literature; this corpus has
  not surveyed for them, and doing so is the cheap first step.
- **An extension of the weak-key analysis.** Determining whether the KN-LIT-3735
  weak-key classes are a bounded curiosity or the visible part of a general
  structural handle is a well-scoped literature-plus-computation task.

None of the three has been attempted here. The first step is a survey, not an
experiment.
