---
id: KN-LIT-6707
type: literature
title: "Smaller decoding exponents: ball-collision decoding"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Christiane Peters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hyperelliptic, pairing, pqc, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Very few public-key cryptosystems are known that can encrypt and decrypt in time b2+o(1) with conjectured security level 2b against conventional computers and quantum computers. The oldest of these systems is the classic McEliece code-based cryptosystem.

## Key claims (as reported)
- The best attacks known against this system are generic decoding attacks that treat McEliece’s hidden binary Goppa codes as random linear codes.
- A standard conjecture is that the best possible w-error-decoding attacks against random linear codes of dimension k and length n take time 2(α(R,W )+o(1))n if k/n → R and w/n → W as n → ∞.
- Before this paper, the best upper bound known on the exponent α(R, W ) was the exponent of an attack introduced by Stern in 1989.
- This paper introduces “ball-collision decoding” and shows that it has a smaller exponent for each (R, W ): the speedup from Stern’s algorithm to ball-collision decoding is exponential in n.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/68410740 (1).pdf`
- `downloads/68410740 (2).pdf`
- `downloads/68410740 (3).pdf`
- `downloads/68410740.pdf`
- `downloads/ballcoll-20110307.pdf`
