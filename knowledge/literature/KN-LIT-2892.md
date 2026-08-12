---
id: KN-LIT-2892
type: literature
title: "Chosen-Ciphertext Security of Multiple Encryption"
authors:
  - "Yevgeniy Dodis"
  - "Jonathan Katz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Encryption of data using multiple, independent encryption schemes (“multiple encryption”) has been suggested in a variety of contexts, and can be used, for example, to protect against partial key exposure or cryptanalysis, or to enforce threshold access to data. Most prior work on this subject has focused on the security of multiple encryption against chosen-plaintext attacks, and has shown constructions secure in this sense based on the chosen-plaintext security of the component schemes.

## Key claims (as reported)
- Subsequent work has sometimes assumed that these solutions are also secure against chosen-ciphertext attacks when component schemes with stronger security properties are used.
- Unfortunately, this intuition is false for all existing multiple encryption schemes.
- Here, in addition to formalizing the problem of chosen-ciphertext security for multiple encryption, we give simple, efficient, and generic constructions of multiple encryption schemes secure against chosen-ciphertext attacks (based on any component schemes secure against such attacks) in the standard model.
- We also give a more efficient construction from any (hierarchical) identity-based encryption scheme secure against selectiveidentity chosen plaintext attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/3378_189 (1).pdf`
- `downloads/3378_189 (2).pdf`
- `downloads/3378_189 (3).pdf`
- `downloads/3378_189.pdf`
