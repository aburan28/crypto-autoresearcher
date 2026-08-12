---
id: KN-LIT-4841
type: literature
title: "Making Sigma-protocols Non-interactive without Random Oracles"
authors:
  - "Pyrros Chaidos"
  - "Jens Groth"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, mov-fr, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Damgård, Fazio and Nicolosi (TCC 2006) gave a transformation of Sigma-protocols, 3-move honest verifier zero-knowledge proofs, into efficient non-interactive zero-knowledge arguments for a designated verifier. Their transformation uses additively homomorphic encryption to encrypt the verifier’s challenge, which the prover uses to compute an encrypted answer.

## Key claims (as reported)
- The transformation does not rely on the random oracle model but proving soundness requires a complexity leveraging assumption.
- We propose an alternative instantiation of their transformation and show that it achieves culpable soundness without complexity leveraging.
- This improves upon an earlier result by Ventre and Visconti (Africacrypt 2009), who used a different construction which achieved weak culpable soundness.
- We demonstrate how our construction can be used to prove validity of encrypted votes in a referendum.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90200192 (1).pdf`
- `downloads/90200192 (2).pdf`
- `downloads/90200192 (3).pdf`
- `downloads/90200192 (4).pdf`
- `downloads/90200192.pdf`
