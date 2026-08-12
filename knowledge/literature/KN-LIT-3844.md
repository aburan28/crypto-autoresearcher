---
id: KN-LIT-3844
type: literature
title: "Faster Homomorphic Linear Transformations in HElib?"
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
tags: [fhe, finite-field, implementation, lattice, mov-fr, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
HElib is a software library that implements homomorphic encryption (HE), with a focus on effective use of “packed” ciphertexts. An important operation is applying a known linear map to a vector of encrypted data.

## Key claims (as reported)
- In this paper, we describe several algorithmic improvements that significantly speed up this operation: in our experiments, our new algorithms are 30–75 times faster than those previously implemented in HElib for typical parameters.
- One application than can benefit from faster linear transformations is bootstrapping (in particular, “thin bootstrapping” as described in [Chen and Han, Eurocrypt 2018]).
- In some settings, our new algorithms for linear transformations result in a 6× speedup for the entire thin bootstrapping operation.
- Our techniques also reduce the size of the large public evaluation key, often using 33%-50% less space than the previous HElib implementation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993198 (1).pdf`
- `downloads/10993198.pdf`
- `downloads/matmul.pdf`
