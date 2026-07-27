---
id: KN-LIT-3823
type: literature
title: "Faster Amortized FHEW Bootstrapping Using Ring Automorphisms Gabrielle De Micheli1[0000−0002−2617−6878] , Duhyeong Kim2[0000−0002−4766−3456]"
authors:
  - "Daniele Micciancio"
  - "Adam Suhl"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Amortized bootstrapping offers a way to simultaneously refresh many ciphertexts of a fully homomorphic encryption scheme, at a total cost comparable to that of refreshing a single ciphertext. An amortization method for FHEW-style cryptosystems was first proposed by (Micciancio and Sorrell, ICALP 2018), who showed that the amortized cost of bootstrapping n FHEW-style ciphertexts can be reduced from Õ(n) basic cryptographic operations to just Õ(n ), for any constant  > 0.

## Key claims (as reported)
- However, despite the promising asymptotic saving, the algorithm was rather impractical due to a large constant (exponential in 1/) hidden in the asymptotic notation.
- In this work, we propose an alternative amortized bootstrapping method with much smaller overhead, still achieving O(n ) asymptotic amortized cost, but with a hidden constant that is only linear in 1/, and with reduced noise growth.
- This is achieved following the general strategy of (Micciancio and Sorrell), but replacing their use of the Nussbaumer transform, with a much more practical Number Theoretic Transform, with multiplication by twiddle factors implemented using ring automorphisms.
- A key technical ingredient to do this is a new “scheme switching” technique proposed in this paper which may be of independent interest.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602061 (1).pdf`
- `downloads/14602061.pdf`
