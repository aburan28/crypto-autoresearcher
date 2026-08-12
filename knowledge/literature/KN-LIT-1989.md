---
id: KN-LIT-1989
type: literature
title: "3kf9: Enhancing 3GPP-MAC beyond the Birthday Bound"
authors:
  - "Liting Zhang"
  - "Wenling Wu"
  - "Han Sui"
  - "Peng Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Among various cryptographic schemes, CBC-based MACs belong to the few ones most widely used in practice. Such MACs iterate a blockcipher EK in the so called Cipher-Block-Chaining way, i.e.

## Key claims (as reported)
- Ci = EK (Mi ⊕ Ci−1 ) , offering high efficiency in practical applications.
- In the paper, we propose a new deterministic variant of CBC-based MACs that is provably secure beyond the birthday bound.
- The new MAC 3kf9 is obtained by combining f 9 (3GPP-MAC) and EMAC sharing the same internal structure, and so it is almost as efficient as the original CBC 3 3 q MAC.
- 3kf9 offers O( l22n + 2lqn ) PRF-security when its underlying n-bit blockcipher is pseudorandom with three independent keys.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580291 (1).pdf`
- `downloads/76580291 (2).pdf`
- `downloads/76580291 (3).pdf`
- `downloads/76580291.pdf`
