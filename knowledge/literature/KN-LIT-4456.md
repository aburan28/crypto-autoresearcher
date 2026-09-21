---
id: KN-LIT-4456
type: literature
title: "Improving NFS for the discrete logarithm problem in non-prime finite fields"
authors:
  - "Aurore Guillevic"
  - "François Morain"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, extension-field, factoring, finite-field, number-theory, pairing, pollard-rho, prime-field]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The aim of this work is to investigate the hardness of the discrete logarithm problem in fields GF(pn ) where n is a small integer greater than 1. Though less studied than the small characteristic case or the prime field case, the difficulty of this problem is at the heart of security evaluations for torus-based and pairing-based cryptography.

## Key claims (as reported)
- The best known method for solving this problem is the Number Field Sieve (NFS).
- A key ingredient in this algorithm is the ability to find good polynomials that define the extension fields used in NFS.
- We design two new methods for this task, modifying the asymptotic complexity and paving the way for record-breaking computations.
- We exemplify these results with the computation of discrete logarithms over a field GF(p2 ) whose cardinality is 180 digits (595 bits) long.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560122 (1).pdf`
- `downloads/90560122.pdf`
