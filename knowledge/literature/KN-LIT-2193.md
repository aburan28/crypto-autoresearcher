---
id: KN-LIT-2193
type: literature
title: "A Practical Key Recovery Attack on Basic TCHo ?"
authors:
  - "Mathias Herrmann"
  - "Gregor Leander"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, ecdsa, finite-field, lattice, provable-security, quantum, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
TCHo is a public key encryption scheme based on a stream cipher component, which is particular suitable for low cost devices like RFIDs. In its basic version, TCHo offers no IND-CCA2 security, but the authors suggest to use a generic hybrid construction to achieve this security level.

## Key claims (as reported)
- The implementation of this method however, significantly increases the hardware complexity of TCHo and thus annihilates the advantage of being suitable for low cost devices.
- In this paper we show, that TCHo cannot be used without this construction.
- We present a chosen ciphertext attack on basic TCHo that recovers the secret key after approximately d3/2 decryptions, where d is the number of bits of the  d , where w secret key polynomial.
- The entropy of the secret key is log2 w is the weight of the secret key polynomial, and w is usually small compared to d.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54430415 (1).pdf`
- `downloads/54430415 (2).pdf`
- `downloads/54430415 (3).pdf`
- `downloads/54430415.pdf`
