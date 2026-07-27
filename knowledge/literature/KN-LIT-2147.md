---
id: KN-LIT-2147
type: literature
title: "A New Framework For More Efficient Round-Optimal Lattice-Based (Partially) Blind Signature via Trapdoor Sampling"
authors:
  - "Rafael del Pino"
  - "Shuichi Katsumata"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mov-fr, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Blind signatures, proposed by Chaum (CRYPTO’82), are interactive protocols between a signer and a user, where a user can obtain a signature without revealing the message to be signed. Recently, Hauck et al.

## Key claims (as reported)
- (EUROCRYPT’20) observed that all efficient lattice-based blind signatures following the blueprint of the original blind signature by Rükert (ASIACRYPT’10) have a flawed security proof.
- This puts us in a situation where all known lattice-based blind signatures have at least two of the following drawbacks: heuristic security; 1 MB or more signature size; only supporting bounded polynomially many signatures, or being based on non-standard assumptions.
- In this work, we construct the first round-optimal (i.e., two-round) lattice-based blind signature with a signature size roughly 100 KB that supports unbounded polynomially many signatures and is provably secure under standard assumptions.
- Even if we allow non-standard assumptions and more rounds, ours provide the shortest signature size while simultaneously supporting unbounded polynomially many signatures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070332 (1).pdf`
- `downloads/135070332.pdf`
