---
id: KN-LIT-3690
type: literature
title: "Enhanced Lattice-Based Signatures on Reconfigurable Hardware"
authors:
  - "Thomas Pöppelmann"
  - "Léo Ducas"
  - "Tim Güneysu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, ecdsa, hash, implementation, lattice, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The recent Bimodal Lattice Signature Scheme (Bliss) showed that lattice-based constructions have evolved to practical alternatives to RSA or ECC. Besides reasonably small signatures with 5600 bits for a 128-bit level of security, Bliss enables extremely fast signing and signature verification in software.

## Key claims (as reported)
- However, due to the complex sampling of Gaussian noise with high precision, it is not clear whether this scheme can be mapped efficiently to embedded devices.
- Even though the authors of Bliss also proposed a new sampling algorithm using Bernoulli variables this approach is more complex than previous methods using large precomputed tables.
- The clear disadvantage of using large tables for high performance is that they cannot be used on constrained computing environments, such as FPGAs, with limited memory.
- In this work we thus present techniques for an efficient Cumulative Distribution Table (CDT) based Gaussian sampler on reconfigurable hardware involving Peikert’s convolution lemma and the Kullback-Leibler divergence.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310171 (1).pdf`
- `downloads/87310171 (2).pdf`
- `downloads/87310171 (3).pdf`
- `downloads/87310171.pdf`
