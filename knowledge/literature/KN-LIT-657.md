---
id: KN-LIT-657
type: literature
title: "A new ECDLP-based PoW model"
authors:
  - "Alessio Meneghetti"
  - "Massimiliano Sala"
  - "Daniele Taufer"
year: 2019
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1911.11287"
  url: "https://arxiv.org/abs/1911.11287"
tags: [dlp, ecdlp, elliptic-curve, finite-field, index-calculus, pairing, pollard-rho, prime-field, quantum, semaev]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We lay the foundations for a blockchain scheme, whose consensus is reached via a proof of work algorithm based on the solution of consecutive discrete logarithm problems over the point group of elliptic curves. In the considered architecture, the curves are pseudorandomly determined by block creators, chosen to be cryptographically secure and changed every epoch.

## Key claims (as reported)
- Given the current state of the chain and a prescribed set of transactions, the curve selection is fully rigid, therefore trust is needed neither in miners nor in the scheme proposers.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1911.11287v2.pdf`
