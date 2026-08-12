---
id: KN-LIT-6311
type: literature
title: "Rotational Rebound Attacks on Reduced Skein"
authors:
  - "Dmitry Khovratovich"
  - "Ivica Nikolić"
  - "Christian Rechberger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we combine a recent rotational cryptanalysis with the rebound attack, which results in the best cryptanalysis of Skein, a candidate for the SHA-3 competition. The rebound attack approach was so far only applied to AES-like constructions.

## Key claims (as reported)
- For the first time, we show that this approach can also be applied to very different constructions.
- In more detail, we develop a number of techniques that extend the reach of both the inbound and the outbound phase, leading to cryptanalytic results on an estimated 53/57 out of the 72 rounds of the Skein-256/512 compression function and the Threefish cipher.
- The new techniques include an analytical search for optimal input values in the rotational cryptanalysis, which allows to extend the outbound phase of the attack with a precomputation phase, an approach never used in any rebound-style attack before.
- Further we show how to combine multiple inside-out computations and neutral bits in the inbound phase of the rebound attack, and give well-defined rotational distinguishers as certificates of weaknesses for the compression functions and block ciphers.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477001 (1).pdf`
- `downloads/6477001 (2).pdf`
- `downloads/6477001 (3).pdf`
- `downloads/6477001.pdf`
