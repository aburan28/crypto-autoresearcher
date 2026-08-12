---
id: KN-LIT-6143
type: literature
title: "Rasta: A cipher with low ANDdepth and few ANDs per bit"
authors:
  - "Christoph Dobraunig"
  - "Maria Eichlseder"
  - "Lorenzo Grassi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr, mpc, side-channel, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recent developments in multi party computation (MPC) and fully homomorphic encryption (FHE) promoted the design and analysis of symmetric cryptographic schemes that minimize multiplications in one way or another. In this paper, we propose with Rasta a design strategy for symmetric encryption that has ANDdepth d and at the same time only needs d ANDs per encrypted bit.

## Key claims (as reported)
- Even for very low values of d between 2 and 6 we can give strong evidence that attacks may not exist.
- This contributes to a better understanding of the limits of what concrete symmetric-key constructions can theoretically achieve with respect to AND-related metrics, and is to the best of our knowledge the first attempt that minimizes both metrics simultaneously.
- Furthermore, we can give evidence that for choices of d between 4 and 6 the resulting implementation properties may well be competitive by testing our construction in the use-case of removing the large ciphertext-expansion when using the BGV scheme.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993255 (1).pdf`
- `downloads/10993255.pdf`
