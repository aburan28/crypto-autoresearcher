---
id: KN-LIT-4429
type: literature
title: "Improved Progressive BKZ Algorithms and their Precise Cost Estimation by Sharp Simulator"
authors:
  - "Yoshinori Aono"
  - "Yuntao Wang"
  - "Takuya Hayashi"
  - "Tsuyoshi Takagi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we investigate a variant of the BKZ algorithm, called progressive BKZ, which performs BKZ reductions by starting with a small blocksize and gradually switching to larger blocks as the process continues. We discuss techniques to accelerate the speed of the progressive BKZ algorithm by optimizing the following parameters: blocksize, searching radius and probability for pruning of the local enumeration algorithm, and the constant in the geometric series assumption (GSA).

## Key claims (as reported)
- We then propose a simulator for predicting the length of the Gram-Schmidt basis obtained from the BKZ reduction.
- We also present a model for estimating the computational cost of the proposed progressive BKZ by considering the efficient implementation of the local enumeration algorithm and the LLL algorithm.
- Finally, we compare the cost of the proposed progressive BKZ with that of other algorithms using instances from the Darmstadt SVP Challenge.
- The proposed algorithm is approximately 50 times faster than BKZ 2.0 (proposed by Chen-Nguyen) for solving the SVP Challenge up to 160 dimensions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650325 (1).pdf`
- `downloads/96650325.pdf`
