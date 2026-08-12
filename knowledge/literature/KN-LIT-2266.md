---
id: KN-LIT-2266
type: literature
title: "A Transform for NIZK Almost as Efficient and General as the Fiat-Shamir Transform Without Programmable Random Oracles"
authors:
  - "Michele Ciampi"
  - "Giuseppe Persiano"
  - "Luisa Siniscalchi"
  - "Ivan Visconti"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Fiat-Shamir (FS) transform is a popular technique for obtaining practical zero-knowledge argument systems. The FS transform uses a hash function to generate, without any further overhead, noninteractive zero-knowledge (NIZK) argument systems from public-coin honest-verifier zero-knowledge (public-coin HVZK) proof systems.

## Key claims (as reported)
- In the proof of zero knowledge, the hash function is modeled as a programmable random oracle (PRO).
- In TCC 2015, Lindell embarked on the challenging task of obtaining a similar transform with improved heuristic security.
- Lindell showed that, for several interesting and practical languages, there exists an efficient transform in the non-programmable random oracle (NPRO) model that also uses a common reference string (CRS).
- A major contribution of Lindell’s transform is that zero knowledge is proved without random oracles and this is an important step towards achieving efficient NIZK arguments in the CRS model without random oracles.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95620687 (1).pdf`
- `downloads/95620687.pdf`
