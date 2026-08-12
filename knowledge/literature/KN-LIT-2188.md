---
id: KN-LIT-2188
type: literature
title: "A Practical Attack on KeeLoq"
authors:
  - "Sebastiaan Indesteege"
  - "Nathan Keller"
  - "⋆ ⋆ ⋆"
  - "Orr Dunkelman"
  - "Eli Biham"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
KeeLoq is a lightweight block cipher with a 32-bit block size and a 64-bit key. Despite its short key size, it is widely used in remote keyless entry systems and other wireless authentication applications.

## Key claims (as reported)
- For example, authentication protocols based on KeeLoq are supposedly used by various car manufacturers in anti-theft mechanisms.
- This paper presents a practical key recovery attack against KeeLoq that requires 216 known plaintexts and has a time complexity of 244.5 KeeLoq encryptions.
- It is based on the slide attack and a novel approach to meet-in-the-middle attacks.
- The fully implemented attack requires 65 minutes to obtain the required data and 7.8 days of calculations on 64 CPU cores.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49650001 (1).pdf`
- `downloads/49650001 (2).pdf`
- `downloads/49650001 (3).pdf`
- `downloads/49650001.pdf`
