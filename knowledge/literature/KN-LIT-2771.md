---
id: KN-LIT-2771
type: literature
title: "Bootstrapping for HElib"
authors:
  - "Shai Halevi"
  - "Victor Shoup"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [extension-field, fhe, lattice, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Gentry’s bootstrapping technique is still the only known method of obtaining fully homomorphic encryption where the system’s parameters do not depend on the complexity of the evaluated functions. Bootstrapping involves a recryption procedure where the scheme’s decryption algorithm is evaluated homomorphically.

## Key claims (as reported)
- So far, there have been precious few implementations of recryption, and fewer still that can handle “packed ciphertexts” that encrypt vectors of elements.
- In the current work, we report on an implementation of recryption of fully-packed ciphertexts using the HElib library for somewhathomomorphic encryption.
- This implementation required extending the recryption algorithms from the literature, as well as many aspects of the HElib library.
- Our implementation supports bootstrapping of packed ciphertexts over many extension fields/rings.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560206 (1).pdf`
- `downloads/90560206.pdf`
- `downloads/boot.pdf`
