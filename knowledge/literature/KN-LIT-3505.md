---
id: KN-LIT-3505
type: literature
title: "ECM at Work"
authors:
  - "Joppe W. Bos"
  - "Thorsten Kleinjung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, factoring, implementation, number-theory, pairing, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The performance of the elliptic curve method (ECM) for integer factorization plays an important role in the security assessment of RSA-based protocols as a cofactorization tool inside the number field sieve. The efficient arithmetic for Edwards curves found an application by speeding up ECM.

## Key claims (as reported)
- We propose techniques based on generating and combining addition-subtracting chains to optimize Edwards ECM in terms of both performance and memory requirements.
- This makes our approach very suitable for memory-constrained devices such as graphics processing units (GPU).
- For commonly used ECM parameters we are able to lower the required memory up to a factor 55 compared to the state-of-the-art Edwards ECM approach.
- Our ECM implementation on a GTX 580 GPU sets a new throughput record, outperforming the best GPU, CPU and FPGA results reported in literature.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580464 (1).pdf`
- `downloads/76580464 (2).pdf`
- `downloads/76580464 (3).pdf`
- `downloads/76580464.pdf`
