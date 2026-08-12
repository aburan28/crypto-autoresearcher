---
id: KN-LIT-2302
type: literature
title: "Accelerating LTV Based Homomorphic Encryption in Reconfigurable Hardware"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
After being introduced in 2009, the first fully homomorphic encryption (FHE) scheme has created significant excitement in academia and industry. Despite rapid advances in the last 6 years, FHE schemes are still not ready for deployment due to an efficiency bottleneck.

## Key claims (as reported)
- Here we introduce a custom hardware accelerator optimized for a class of reconfigurable logic to bring LTV based somewhat homomorphic encryption (SWHE) schemes one step closer to deployment in real-life applications.
- The accelerator we present is connected via a fast PCIe interface to a CPU platform to provide homomorphic evaluation services to any application that needs to support blinded computations.
- Specifically we introduce a number theoretical transform based multiplier architecture capable of efficiently handling very large polynomials.
- When synthesized for the Xilinx Virtex 7 family the presented architecture can compute the product of large polynomials in under 6.25 msec making it the fastest multiplier design of its kind currently available in the literature and is more than 102 times faster than a software implementation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930182 (1).pdf`
- `downloads/92930182.pdf`
