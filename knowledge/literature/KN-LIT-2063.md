---
id: KN-LIT-2063
type: literature
title: "A Generalized Birthday Problem"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, pairing, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
) David Wagner University of California at Berkeley Abstract. We study a k-dimensional generalization of the birthday problem: given k lists of n-bit values, find some way to choose one element from each list so that the resulting k values xor to zero.

## Key claims (as reported)
- For k = 2, this is just the extremely well-known birthday problem, which has a square-root time algorithm with many applications in cryptography.
- In this paper, we show new algorithms for the case k > 2: we show a cube-root time algorithm for the case of k = 4 lists, and we give an algorithm with subexponential running time when k is unrestricted.
- We also give several applications to cryptanalysis, describing new subexponential algorithms for constructing one-more forgeries for certain blind signature schemes, for breaking certain incremental hash functions, and for finding low-weight parity check equations for fast correlation attacks √ on stream ciphers.
- In these applications, our algorithm runs in O(22 n ) time for an n-bit modulus, demonstrating that moduli may need to be at least 1600 bits long for security against these new attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420288 (1).pdf`
- `downloads/24420288 (2).pdf`
- `downloads/24420288.pdf`
