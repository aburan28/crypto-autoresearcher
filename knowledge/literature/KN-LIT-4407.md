---
id: KN-LIT-4407
type: literature
title: "Improved Generic Attacks Against Hash-based MACs and HAIFA?"
authors:
  - "Itai Dinur"
  - "Gaëtan Leurent"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The security of HMAC (and more general hash-based MACs) against state-recovery and universal forgery attacks was very recently shown to be suboptimal, following a series of surprising results by Leurent et al. and Peyrin et al.. These results have shown that such powerful attacks require much less than 2` computations, contradicting the common belief (where ` denotes the internal state size).

## Key claims (as reported)
- In this work, we revisit and extend these results, with a focus on properties of concrete hash functions such as a limited message length, and special iteration modes.
- We begin by devising the first state-recovery attack on HMAC with a HAIFA hash function (using a block counter in every compression function call), with complexity 24`/5 .
- Then, we describe improved tradeoffs between the message length and the complexity of a state-recovery attack on HMAC.
- Consequently, we obtain improved attacks on several HMAC constructions used in practice, in which the hash functions limit the maximal message length (e.g., SHA-1 and SHA-2).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160271 (1).pdf`
- `downloads/86160271 (2).pdf`
- `downloads/86160271 (3).pdf`
- `downloads/86160271 (4).pdf`
- `downloads/86160271 (5).pdf`
- `downloads/86160271.pdf`
