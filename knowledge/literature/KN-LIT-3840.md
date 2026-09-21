---
id: KN-LIT-3840
type: literature
title: "Faster Fully Homomorphic Encryption: Bootstrapping in less than 0.1 Seconds"
authors:
  - "Ilaria Chillotti"
  - "Nicolas Gama"
  - "Mariya Georgieva"
  - "Malika Izabachène"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we revisit fully homomorphic encryption (FHE) based on GSW and its ring variants. We notice that the internal product of GSW can be replaced by a simpler external product between a GSW and an LWE ciphertext.

## Key claims (as reported)
- We show that the bootstrapping scheme FHEW of Ducas and Micciancio [11] can be expressed only in terms of this external product.
- As a result, we obtain a speed up from less than 1 second to less than 0.1 seconds.
- We also reduce the 1GB bootstrapping key size to 24MB, preserving the same security levels, and we improve the noise propagation overhead by replacing exact decomposition algorithms with approximate ones.
- Moreover, our external product allows to explain the unique asymmetry in the noise propagation of GSW samples and makes it possible to evaluate deterministic automata homomorphically as in [13] in an efficient way with a noise overhead only linear in the length of the tested word.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031271 (1).pdf`
- `downloads/10031271.pdf`
