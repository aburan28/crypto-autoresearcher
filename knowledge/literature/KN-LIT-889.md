---
id: KN-LIT-889
type: literature
title: "Meet-in-the-Middle Attacks Revisited:"
authors:
  - "Preimage Attacks⋆"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/427"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/427"
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At EUROCRYPT 2021, Bao et al. proposed an automatic method for systematically exploring the configuration space of meetin-the-middle (MITM) preimage attacks. We further extend it into a constraint-based framework for finding exploitable MITM characteristics in the context of key-recovery and collision attacks by taking the subtle peculiarities of both scenarios into account.

## Key claims (as reported)
- Moreover, to perform attacks based on MITM characteristics with nonlinear constrained neutral words, which have not been seen before, we present a procedure for deriving the solution spaces of neutral words without solving the corresponding nonlinear equations or increasing the overall time complexities of the attack.
- We apply our method to concrete symmetric-key primitives, including SKINNY, ForkSkinny, Romulus-H, Saturnin, Grøstl, WHIRLPOOL, and hashing modes with AES-256.
- As a result, we identify the first 23-round key-recovery attack on SKINNY-n-3n and the first 24-round key-recovery attack on ForkSkinny-n-3n in the single-key model.
- Moreover, improved (pseudo) preimage or collision attacks on round-reduced WHIRLPOOL, Grøstl, and hashing modes with AES-256 are obtained.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826150 (1).pdf`
- `downloads/12826150.pdf`
