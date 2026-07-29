---
id: KN-LIT-3254
type: literature
title: "Cryptanalysis of RSA Signatures with Fixed-Pattern Padding"
authors:
  - "Eric Brier"
  - "Christophe Clavier"
  - "Jean-Sébastien Coron"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, hash, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A fixed-pattern padding consists in concatenating to the message m a fixed pattern P . The RSA signature is then obtained by computing (P |m)d mod N where d is the private exponent and N the modulus.

## Key claims (as reported)
- In Eurocrypt ’97, Girault and Misarsky showed that the size of P must be at least half the size of N (in other words the parameter configurations |P | < |N |/2 are insecure) but the security of RSA fixedpattern padding remained unknown for |P | > |N |/2.
- In this paper we show that the size of P must be at least two-thirds of the size of N , i.e. we show that |P | < 2|N |/3 is insecure.
- Key-words: RSA signatures, fixed-pattern padding, affine redundancy.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/21390431 (1).pdf`
- `downloads/21390431 (2).pdf`
- `downloads/21390431.pdf`
