---
id: KN-LIT-7156
type: literature
title: "Tightly-Secure Key-Encapsulation Mechanism in the Quantum Random Oracle Model"
authors:
  - "Tsunekazu Saito"
  - "Keita Xagawa"
  - "Takashi Yamakawa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pqc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Key-encapsulation mechanisms secure against chosen ciphertext attacks (IND-CCA-secure KEMs) in the quantum random oracle model have been proposed by Boneh, Dagdelen, Fischlin, Lehmann, Schafner, and Zhandry (CRYPTO 2012), Targhi and Unruh (TCC 2016-B), and Hofheinz, Hövelmanns, and Kiltz (TCC 2017). However, all are non-tight and, in particular, security levels of the schemes obtained by these constructions are less than half of original security levels of their building blocks.

## Key claims (as reported)
- In this paper, we give a conversion that tightly converts a weakly secure publickey encryption scheme into an IND-CCA-secure KEM in the quantum random oracle model.
- More precisely, we define a new security notion for deterministic public key encryption (DPKE) called the disjoint simulatability, and we propose a way to convert a disjoint simulatable DPKE scheme into an IND-CCA-secure key-encapsulation mechanism scheme without incurring a significant security degradation.
- In addition, we give DPKE schemes whose disjoint simulatability is tightly reduced to post-quantum assumptions.
- As a result, we obtain INDCCA-secure KEMs tightly reduced to various post-quantum assumptions in the quantum random oracle model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822185 (1).pdf`
- `downloads/10822185.pdf`
