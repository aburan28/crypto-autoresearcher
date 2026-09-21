---
id: KN-LIT-6813
type: literature
title: "Stream ciphers: A Practical Solution for Efficient Homomorphic-Ciphertext Compression?"
authors:
  - "maria.naya plasencia@inria.fr"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In typical applications of homomorphic encryption, the first step consists for Alice to encrypt some plaintext m under Bob’s public key pk and to send the ciphertext c = HEpk (m) to some third-party evaluator Charlie. This paper specifically considers that first step, i.e. the problem of transmitting c as efficiently as possible from Alice to Charlie.

## Key claims (as reported)
- As previously noted, a form of compression is achieved using hybrid encryption.
- Given a symmetric encryption scheme E, Alice picks a random key k and sends a much smaller ciphertext c0 = (HEpk (k), Ek (m)) that Charlie decompresses homomorphically into the original c using a decryption circuit CE−1 .
- In this paper, we revisit that paradigm in light of its concrete implementation constraints; in particular E is chosen to be an additive IV-based stream cipher.
- We investigate the performances offered in this context by Trivium, which belongs to the eSTREAM portfolio, and we also propose a variant with 128-bit security: Kreyvium.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830297 (1).pdf`
- `downloads/97830297.pdf`
