---
id: KN-LIT-3506
type: literature
title: "ECM on Graphics Cards Daniel J. Bernstein1 , Tien-Ren Chen2 , Chen-Mou Cheng3"
authors:
  - "Tanja Lange"
  - "Bo-Yin Yang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, elliptic-curve, factoring, hyperelliptic, index-calculus, number-theory, pairing, pollard-rho, prime-field, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper reports record-setting performance for the ellipticcurve method of integer factorization: for example, 926.11 curves/second for ECM stage 1 with B1 = 8192 for 280-bit integers on a single PC. The state-of-the-art GMP-ECM software handles 124.71 curves/second for ECM stage 1 with B1 = 8192 for 280-bit integers using all four cores of a 2.4 GHz Core 2 Quad Q6600.

## Key claims (as reported)
- The extra speed takes advantage of extra hardware, specifically two NVIDIA GTX 295 graphics cards, using a new ECM implementation introduced in this paper.
- Our implementation uses Edwards curves, relies on new parallel addition formulas, and is carefully tuned for the highly parallel GPU architecture.
- On a single GTX 295 the implementation performs 41.88 million modular multiplications per second for a general 280-bit modulus.
- GMP-ECM, using all four cores of a Q6600, performs 13.03 million modular multiplications per second.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790481 (1).pdf`
- `downloads/54790481 (2).pdf`
- `downloads/54790481 (3).pdf`
- `downloads/54790481 (4).pdf`
- `downloads/54790481.pdf`
- `downloads/gpuecm-20090127.pdf`
