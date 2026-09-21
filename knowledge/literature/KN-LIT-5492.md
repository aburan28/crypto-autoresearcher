---
id: KN-LIT-5492
type: literature
title: "On the Impossibility of Algebraic NIZK"
authors:
  - "In Pairing-Free Groups"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Non-Interactive Zero-Knowledge proofs (NIZK) allow a prover to convince a verifier that a statement is true by sending only one message and without conveying any other information. In the CRS model, many instantiations have been proposed from group-theoretic assumptions.

## Key claims (as reported)
- On the one hand, some of these constructions use the group structure in a black-box way but rely on pairings, an example being the celebrated Groth-Sahai proof system.
- On the other hand, a recent line of research realized NIZKs from sub-exponential DDH in pairing-free groups using Correlation Intractable Hash functions, but at the price of making non black-box usage of the group.
- As of today no construction is known to simultaneously reduce its security to pairing-free group problems and to use the underlying group in a black-box way.
- This is indeed not a coincidence: in this paper, we prove that for a large class of NIZK either a pairing-free group is used non black-box by relying on element representation, or security reduces to external hardness assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850348 (1).pdf`
- `downloads/140850348.pdf`
