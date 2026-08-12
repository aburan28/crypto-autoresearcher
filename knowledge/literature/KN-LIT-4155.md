---
id: KN-LIT-4155
type: literature
title: "Hardness of Computing Individual Bits for One-way Functions on Elliptic Curves"
authors:
  - "Alexandre Duc"
  - "Dimitar Jetchev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdlp, elliptic-curve, finite-field, pairing, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We prove that if one can predict any of the bits of the input to an elliptic curve based one-way function over a finite field, then we can invert the function. In particular, our result implies that if one can predict any of the bits of the input to a classical pairing-based one-way function with non-negligible advantage over a random guess then one can efficiently invert this function and thus, solve the Fixed Argument Pairing Inversion problem (FAPI-1/FAPI-2).

## Key claims (as reported)
- The latter has implications on the security of various pairing-based schemes such as the identitybased encryption scheme of Boneh–Franklin, Hess’ identity-based signature scheme, as well as Joux’s three-party one-round key agreement protocol.
- Moreover, if one can solve FAPI-1 and FAPI-2 in polynomial time then one can solve the Computational Diffie–Hellman problem (CDH) in polynomial time.
- Our result implies that all the bits of the functions defined above are hard-to-compute assuming these functions are one-way.
- The argument is based on a list-decoding technique via discrete Fourier transforms due to Akavia–Goldwasser–Safra as well as an idea due to Boneh–Shparlinski.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170827 (1).pdf`
- `downloads/74170827 (2).pdf`
- `downloads/74170827 (3).pdf`
- `downloads/74170827.pdf`
