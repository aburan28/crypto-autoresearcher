---
id: KN-LIT-5058
type: literature
title: "Narrow-Bicliques: Cryptanalysis of Full IDEA"
authors:
  - "Dmitry Khovratovich"
  - "Gaëtan Leurent"
  - "Christian Rechberger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We apply and extend the recently introduced biclique framework to IDEA and for the first time describe an approach to noticeably speed-up key-recovery for the full 8.5 round IDEA. We also show that the biclique approach to block cipher cryptanalysis not only obtains results on more rounds, but also improves time and data complexities over existing attacks.

## Key claims (as reported)
- We consider the first 7.5 rounds of IDEA and demonstrate a variant of the approach that works with practical data complexity.
- The conceptual contribution is the narrow-bicliques technique: the recently introduced independent-biclique approach extended with ways to allow for a significantly reduced data complexity with everything else being equal.
- For this we use available degrees of freedom as known from hash cryptanalysis to narrow the relevant differential trails.
- Our cryptanalysis is of high computational complexity, and does not threaten the practical use of IDEA in any way, yet the techniques are practically verified to a large extent.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370386 (1).pdf`
- `downloads/72370386 (2).pdf`
- `downloads/72370386 (3).pdf`
- `downloads/72370386.pdf`
