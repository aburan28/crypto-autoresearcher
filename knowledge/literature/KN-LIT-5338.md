---
id: KN-LIT-5338
type: literature
title: "On dual lattice attacks against small-secret LWE"
authors:
  - "Martin R. Albrecht"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, pqc, protocol, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present novel variants of the dual-lattice attack against LWE in the presence of an unusually short secret. These variants are informed by recent progress in BKW-style algorithms for solving LWE.

## Key claims (as reported)
- Applying them to parameter sets suggested by the homomorphic encryption libraries HElib and SEAL yields revised security estimates.
- Our techniques scale the exponent of the dual-lattice attack by a factor of (2 L)/(2 L+1) when log q = Θ(L log n), when the secret has constant hamming weight h and where L is the maximum depth of supported circuits.
- They also allow to half the dimension of the lattice under consideration at a multiplicative cost of 2h operations.
- Moreover, our techniques yield revised concrete security estimates.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210169 (1).pdf`
- `downloads/10210169.pdf`
