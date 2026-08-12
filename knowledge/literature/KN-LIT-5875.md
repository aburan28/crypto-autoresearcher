---
id: KN-LIT-5875
type: literature
title: "Predicate Encryption for Circuits from LWE"
authors:
  - "Sergey Gorbunov"
  - "Vinod Vaikuntanathan"
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In predicate encryption, a ciphertext is associated with descriptive attribute values x in addition to a plaintext μ, and a secret key is associated with a predicate f . Decryption returns plaintext μ if and only if f (x) = 1.

## Key claims (as reported)
- Moreover, security of predicate encryption guarantees that an adversary learns nothing about the attribute x or the plaintext μ from a ciphertext, given arbitrary many secret keys that are not authorized to decrypt the ciphertext individually.
- We construct a leveled predicate encryption scheme for all circuits, assuming the hardness of the subexponential learning with errors (LWE) problem.
- That is, for any polynomial function d = d(λ), we construct a predicate encryption scheme for the class of all circuits with depth bounded by d(λ), where λ is the security parameter.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160160 (1).pdf`
- `downloads/92160160 (2).pdf`
- `downloads/92160160.pdf`
