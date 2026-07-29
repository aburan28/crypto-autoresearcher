---
id: KN-LIT-6040
type: literature
title: "Publicly Verifiable Deletion from Minimal Assumptions"
authors:
  - "Fuyuki Kitagawa"
  - "Ryo Nishimaki"
  - "Takashi Yamakawa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, lattice, pairing, pqc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a general compiler to add the publicly verifiable deletion property for various cryptographic primitives including public key encryption, attribute-based encryption, and quantum fully homomorphic encryption. Our compiler only uses one-way functions, or more generally hard quantum planted problems for NP, which are implied by one-way functions.

## Key claims (as reported)
- It relies on minimal assumptions and enables us to add the publicly verifiable deletion property with no additional assumption for the above primitives.
- Previously, such a compiler needs additional assumptions such as injective trapdoor one-way functions or pseudorandom group actions [Bartusek-Khurana-Poremba, CRYPTO 2023].
- Technically, we upgrade an existing compiler for privately verifiable deletion [BartusekKhurana, CRYPTO 2023] to achieve publicly verifiable deletion by using digital signatures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369079 (1).pdf`
- `downloads/14369079.pdf`
