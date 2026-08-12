---
id: KN-LIT-3212
type: literature
title: "Cryptanalysis of"
authors:
  - "Jian Guo"
  - "San Ling"
  - "Huaxiong Wang"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, factoring, fhe, hash, implementation, lattice, pairing, protocol, provable-security, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that the LASH-x hash function is vulnerable to attacks that trade time for memory, including collision attacks as fast as 2(4x/11) and preimage attacks as fast as 2(4x/7) . Moreover, we briefly mention heuristic lattice based collision attacks that use small memory but require very long messages that are expected to find collisions much faster than 2x/2 .

## Key claims (as reported)
- All of these attacks exploit the designers’ choice of an all zero IV.
- We then consider whether LASH can be patched simply by changing the IV.
- In this case, we show that LASH is vulnerable to a 2(7x/8) preimage attack.
- We also show that LASH is trivially not a PRF when any subset of input bytes is used as a secret key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272277 (1).pdf`
- `downloads/11272277.pdf`
- `downloads/14438169 (1).pdf`
- `downloads/14438169.pdf`
- `downloads/50860204 (1).pdf`
- `downloads/50860204 (2).pdf`
- (+12 more duplicate copies)
