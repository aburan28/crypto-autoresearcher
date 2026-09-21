---
id: KN-LIT-5687
type: literature
title: "Order-Preserving Symmetric Encryption"
authors:
  - "Alexandra Boldyreva"
  - "Nathan Chenette"
  - "Younho Lee"
  - "Adam O’Neill"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the cryptographic study of order-preserving symmetric encryption (OPE), a primitive suggested in the database community by Agrawal et al. (SIGMOD ’04) for allowing efficient range queries on encrypted data.

## Key claims (as reported)
- Interestingly, we first show that a straightforward relaxation of standard security notions for encryption such as indistinguishability against chosen-plaintext attack (IND-CPA) is unachievable by a practical OPE scheme.
- Instead, we propose a security notion in the spirit of pseudorandom functions (PRFs) and related primitives asking that an OPE scheme look “as-random-as-possible” subject to the orderpreserving constraint.
- We then design an efficient OPE scheme and prove its security under our notion based on pseudorandomness of an underlying blockcipher.
- Our construction is based on a natural relation we uncover between a random order-preserving function and the hypergeometric probability distribution.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790225 (1).pdf`
- `downloads/54790225 (2).pdf`
- `downloads/54790225 (3).pdf`
- `downloads/54790225.pdf`
