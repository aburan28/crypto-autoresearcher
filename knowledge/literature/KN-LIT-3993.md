---
id: KN-LIT-3993
type: literature
title: "Fully Homomorphic Message Authenticators"
authors:
  - "Rosario Gennaro Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We define and construct a new primitive called a fully homomorphic message authenticator. With such scheme, anybody can perform arbitrary computations over authenticated data and produce a short tag that authenticates the result of the computation (without knowing the secret key).

## Key claims (as reported)
- This tag can be verified using the secret key to ensure that the claimed result is indeed the correct output of the specified computation over previously authenticated data (without knowing the underlying data).
- For example, Alice can upload authenticated data to “the cloud”, which then performs some specified computations over this data and sends the output to Bob, along with a short tag that convinces Bob of correctness.
- Alice and Bob only share a secret key, and Bob never needs to know Alice’s underlying data.
- Our construction relies on fully homomorphic encryption to build fully homomorphic message authenticators.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82700301 (1).pdf`
- `downloads/82700301 (2).pdf`
- `downloads/82700301 (3).pdf`
- `downloads/82700301.pdf`
