---
id: KN-LIT-1506
type: literature
title: "WaterSQI and PRISMO: Quaternion Signatures for Supersingular Isogeny Group Actions"
authors:
  - "Tako Boris Fouotsa⋆"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1737"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1737"
tags: [class-group, elliptic-curve, endomorphism, isogeny, lattice, number-theory, pqc, protocol, quantum, sidh-csidh, signature, supersingular, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Isogeny group action based signatures are obtained from a sigma protocol with high soundness error, say 12 for its most basic variant. One needs to independently repeat the sigma protocol O(λ) times to reduce the soundness error to negligible (with λ being the security parameter).

## Key claims (as reported)
- These repetitions come with a considerable efficiency and size overhead.
- On the other hand, quaternion isogeny-based signatures such as SQIsign and PRISM are directly obtained from a sigma protocol with a negligible soundness error.
- The secret key in SQIsign and PRISM is a random supersingular isogeny, and both schemes are insecure when the secret isogeny arises from the supersingular isogeny group action setting.
- In this paper, we propose WaterSQI and PRISMO, variants of SQIsign and PRISM respectively, suited for secret isogenies that arise from the supersingular isogeny group action setting.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1737.pdf`
