---
id: KN-LIT-6836
type: literature
title: "Strongly Secure Authenticated Key Exchange from Factoring, Codes, and Lattices"
authors:
  - "Atsushi Fujioka"
  - "Koutarou Suzuki"
  - "Keita Xagawa"
  - "Kazuki Yoneyama"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, lattice, pairing, protocol, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An unresolved problem in research on authenticated key exchange (AKE) is to construct a secure protocol against advanced attacks such as key compromise impersonation and maximal exposure attacks without relying on random oracles. HMQV, a state of the art AKE protocol, achieves both efficiency and the strong security model proposed by Krawczyk (we call it the CK+ model), which includes resistance to advanced attacks.

## Key claims (as reported)
- However, the security proof is given under the random oracle model.
- We propose a generic construction of AKE from a key encapsulation mechanism (KEM).
- The construction is based on a chosen-ciphertext secure KEM, and the resultant AKE protocol is CK+ secure in the standard model.
- The protocol gives the first CK+ secure AKE protocols based on the hardness of integer factorization problem, code-based problems, or learning problems with errors.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930468 (1).pdf`
- `downloads/72930468 (2).pdf`
- `downloads/72930468 (3).pdf`
- `downloads/72930468.pdf`
