---
id: KN-LIT-2662
type: literature
title: "Batch Fully Homomorphic Encryption over the Integers?"
authors:
  - "Jung Hee Cheon"
  - "Jean-Sébastien Coron"
  - "Jinsu Kim"
  - "Moon Sung Lee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We extend the fully homomorphic encryption scheme over the integers of van Dijk et al. (DGHV) into a batch fully homomorphic encryption scheme, i.e. to a scheme that supports encrypting and homomorphically processing a vector of plaintexts as a single ciphertext.

## Key claims (as reported)
- We present two variants in which the semantic security is based on different assumptions.
- The first variant is based on a new decisional problem, the Decisional Approximate-GCD problem, whereas the second variant is based on the more classical computational Error-Free Approximate-GCD problem but requires additional public key elements.
- We also show how to perform arbitrary permutations on the underlying plaintext vector given the ciphertext and the public key.
- Our scheme offers competitive performance even with the bootstrapping procedure: we describe an implementation of the homomorphic evaluation of AES, with an amortized cost of about 12 minutes per AES ciphertext on a standard desktop computer; this is comparable to the timings presented by Gentry et al. at Crypto 2012 for their implementation of a Ring-LWE based fully homomorphic encryption scheme.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810313 (1).pdf`
- `downloads/78810313 (2).pdf`
- `downloads/78810313 (3).pdf`
- `downloads/78810313.pdf`
