---
id: KN-LIT-4630
type: literature
title: "Large-Precision Homomorphic Sign Evaluation using FHEW/TFHE Bootstrapping"
authors:
  - "Zeyu Liu"
  - "Daniele Micciancio"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A comparison of two encrypted numbers is an important operation needed in many machine learning applications, for example, decision tree or neural network inference/training. An efficient instantiation of this operation in the context of fully homomorphic encryption (FHE) can be challenging, especially when a relatively high precision is sought.

## Key claims (as reported)
- The conventional FHE way of evaluating the comparison operation, which is based on the sign function evaluation using FHEW/ TFHE bootstrapping (often referred in literature as programmable bootstrapping), can only support very small precision (practically limited to 4-5 bits or so).
- For higher precision, the runtime complexity scales linearly with the ciphertext (plaintext) modulus (i.e., exponentially with the modulus bit size).
- We propose sign function evaluation algorithms that scale logarithmically with the ciphertext (plaintext) modulus, enabling the support of large-precision comparison in practice.
- Our sign evaluation algorithms are based on an iterative use of homomorphic floor function algorithms, which are also derived in our work.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910162 (1).pdf`
- `downloads/137910162.pdf`
