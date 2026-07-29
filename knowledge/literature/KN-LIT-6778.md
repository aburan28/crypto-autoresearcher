---
id: KN-LIT-6778
type: literature
title: "SPRING: Fast Pseudorandom Functions from Rounded Ring Products"
authors:
  - "Abhishek Banerjee"
  - "Hai Brenner"
  - "Gaëtan Leurent"
  - "Chris Peikert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, lattice, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently, Banerjee, Peikert and Rosen (EUROCRYPT 2012) proposed new theoretical pseudorandom function candidates based on “rounded products” in certain polynomial rings, which have rigorously provable security based on worst-case lattice problems. The functions also enjoy algebraic properties that make them highly parallelizable and attractive for modern applications, such as evaluation under homomorphic encryption schemes.

## Key claims (as reported)
- However, the parameters required by BPR’s security proofs are too large for practical use, and many other practical aspects of the design were left unexplored in that work.
- In this work we give two concrete and practically efficient instantiations of the BPR design, which we call SPRING, for “subset-product with rounding over a ring.” One instantiation uses a generator matrix of a binary BCH error-correcting code to “determinstically extract” nearly random bits from a (biased) rounded subset-product.
- The second instantiation eliminates bias by working over suitable moduli and decomposing the computation into “Chinese remainder” components.
- We analyze the concrete security of these instantiations, and provide initial software implementations whose throughputs are within small factors (as small as 4.5) of those of AES.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400183 (1).pdf`
- `downloads/85400183 (2).pdf`
- `downloads/85400183 (3).pdf`
- `downloads/85400183.pdf`
