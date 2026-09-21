---
id: KN-LIT-3507
type: literature
title: "ECM USING EDWARDS CURVES"
authors:
  - "DANIEL J. BERNSTEIN"
  - "PETER BIRKNER"
  - "TANJA LANGE"
  - "CHRISTIANE PETERS"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, factoring, jacobian, pairing, pollard-rho, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces EECM-MPFQ, a fast implementation of the elliptic-curve method of factoring integers. EECM-MPFQ uses fewer modular multiplications than the well-known GMP-ECM software, takes less time than GMP-ECM, and finds more primes than GMP-ECM.

## Key claims (as reported)
- The main improvements above the modular-arithmetic level are as follows: (1) use Edwards curves instead of Montgomery curves; (2) use extended Edwards coordinates; (3) use signed-sliding-window addition-subtraction chains; (4) batch primes to increase the window size; (5) choose curves with small parameters and base points; (6) choose curves with large torsion.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/eecm-20111008 (1).pdf`
- `downloads/eecm-20111008.pdf`
