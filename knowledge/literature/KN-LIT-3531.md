---
id: KN-LIT-3531
type: literature
title: "Efficient Binary Conversion for Paillier Encrypted Values"
authors:
  - "Berry Schoenmakers"
  - "Pim Tuyls"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the framework of secure n-party computation based on threshold homomorphic cryptosystems as put forth by Cramer, Damgård, and Nielsen at Eurocrypt 2001. When used with Paillier’s cryptosystem, this framework allows for efficient secure evaluation of any arithmetic circuit defined over ZN , where N is the RSA modulus of the underlying Paillier cryptosystem.

## Key claims (as reported)
- In this paper, we extend the scope of the framework by considering the problem of converting a given Paillier encryption of a value x ∈ ZN into Paillier encryptions of the bits of x.
- We present solutions for the general case in which x can be any integer in {0, 1, . . . , N − 1}, and for the restricted case in which x < N/(n2κ ) for a security parameter κ.
- In the latter case, we show how to extract the ` least significant bits of x (in encrypted form) in time proportional to `, typically saving a factor of log2 N/` compared to the general case.
- Thus, intermediate computations that rely in an essential way on the binary representations of their input values can be handled without enforcing that the entire computation is done bitwise.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40040529 (1).pdf`
- `downloads/40040529 (2).pdf`
- `downloads/40040529 (3).pdf`
- `downloads/40040529.pdf`
