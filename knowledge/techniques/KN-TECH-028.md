---
id: KN-TECH-028
type: technique
title: Endomorphism rings, the Deuring correspondence, KLPT and SQIsign
tags: [deuring, endomorphism-ring, quaternion, maximal-order, klpt, sqisign, signature, isogeny, adjacent]
confidence: reported
complexity: KLPT quaternion ell-isogeny path in heuristic poly time; endomorphism-ring <-> path-finding equivalent under GRH
applicability: constructing isogeny signatures and computing/using supersingular endomorphism rings
source_refs: [KN-LIT-072, KN-LIT-073, KN-LIT-074, KN-LIT-075]
added: 2026-07-23
superseded_by: null
---

## Method
The Deuring correspondence (KN-LIT-075) is a dictionary: supersingular curves over
F_{p^2} <-> maximal orders in the quaternion algebra B_{p,infinity}; isogenies <->
connecting ideals; endomorphism rings <-> the maximal orders themselves. This lets
one work on the ALGEBRAIC (quaternion) side and transport back:
- **KLPT** (KN-LIT-073): given a connecting ideal, find an equivalent ideal of
  ell-power norm in heuristic polynomial time -- the quaternion path-finding
  engine.
- **SQIsign** (KN-LIT-072): a compact Fiat-Shamir signature whose prover, knowing
  the secret endomorphism ring, uses KLPT to answer challenges by producing
  connecting isogenies; reveals NO torsion images.
- **Equivalence** (KN-LIT-074): endomorphism-ring computation and isogeny
  path-finding are equivalent under GRH, so this is the true hardness core.

## Relevance to this program
The algebraic heart of supersingular isogeny crypto, and the direct point of
contact with the program's endomorphism-structure work (CM, orientation,
RQ-ISO-001, ISO-AR). The "solve the algebraic side of a correspondence, transport
to the geometric side" pattern mirrors the program's own transfer/cover methods.
Adjacent to the ECDLP mission.

## Applicability limits
KLPT is HEURISTIC (prime-distribution assumptions); the endomorphism-ring
equivalence is GRH-conditional (KN-OPEN-013). SQIsign parameters and signing cost
have evolved across versions. The quaternion side being EASY (KLPT) is what makes
endomorphism-ring KNOWLEDGE a trapdoor -- and what makes computing an UNKNOWN
endomorphism ring the hard problem the security rests on.
