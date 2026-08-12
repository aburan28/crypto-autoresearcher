---
id: KN-LIT-3455
type: literature
title: "Distributed Public-Key Cryptography from Weak Secrets"
authors:
  - "Michel Abdalla"
  - "Xavier Boyen"
  - "Céline Chevalier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [protocol, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the notion of distributed password-based publickey cryptography, where a virtual high-entropy private key is implicitly defined as a concatenation of low-entropy passwords held in separate locations. The users can jointly perform private-key operations by exchanging messages over an arbitrary channel, based on their respective passwords, without ever sharing their passwords or reconstituting the key.

## Key claims (as reported)
- Focusing on the case of ElGamal encryption as an example, we start by formally defining ideal functionalities for distributed public-key generation and virtual private-key computation in the UC model.
- We then construct efficient protocols that securely realize them in either the RO model (for efficiency) or the CRS model (for elegance).
- We conclude by showing that our distributed protocols generalize to a broad class of “discrete-log”-based public-key cryptosystems, which notably includes identity-based encryption.
- This opens the door to a powerful extension of IBE with a virtual PKG made of a group of people, each one memorizing a small portion of the master key.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54430146 (1).pdf`
- `downloads/54430146 (2).pdf`
- `downloads/54430146 (3).pdf`
- `downloads/54430146.pdf`
