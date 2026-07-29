---
id: KN-LIT-4503
type: literature
title: "Information-Combining Differential Fault Attacks on DEFAULT"
authors:
  - "Marcel Nageler"
  - "Christoph Dobraunig"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Differential fault analysis (DFA) is a very powerful attack vector for implementations of symmetric cryptography. Most countermeasures are applied at the implementation level.

## Key claims (as reported)
- At ASIACRYPT 2021, Baksi et al. proposed a design strategy that aims to provide inherent cipher level resistance against DFA by using S-boxes with linear structures.
- They argue that in their instantiation, the block cipher DEFAULT, a DFA adversary can learn at most 64 of the 128 key bits, so the remaining brute-force complexity of 264 is impractical.
- In this paper, we show that a DFA adversary can combine information across rounds to recover the full key, invalidating their security claim.
- In particular, we observe that such ciphers exhibit large classes of equivalent keys that can be represented efficiently in normalized form using linear equations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760130 (1).pdf`
- `downloads/132760130.pdf`
