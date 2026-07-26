---
id: KN-LIT-6034
type: literature
title: "Public-Key Locally-Decodable Codes"
authors:
  - "Brett Hemenway"
  - "Rafail Ostrovsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we introduce the notion of a Public-Key Encryption Scheme that is also a Locally-Decodable Error-Correcting Code (PKLDC). In particular, we allow any polynomial-time adversary to read the entire ciphertext, and corrupt a constant fraction of the bits of the entire ciphertext.

## Key claims (as reported)
- Nevertheless, the decoding algorithm can recover any bit of the plaintext with all but negligible probability by reading only a sublinear number of bits of the (corrupted) ciphertext.
- We give a general construction of a PKLDC from any SemanticallySecure Public Key Encryption (SS-PKE) and any Private Information Retrieval (PIR) protocol.
- Since Homomorphic encryption implies PIR, we also show a reduction from any Homomorphic encryption protocol to PKLDC.
- Applying our construction to the best known PIR protocol (that of Gentry and Ramzan), we obtain a PKLDC, which for messages of size n and security parameter k achieves ciphertexts of size O(n), public key of size O(n + k), and locality of size O(k2 ).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51570127 (1).pdf`
- `downloads/51570127 (2).pdf`
- `downloads/51570127 (3).pdf`
- `downloads/51570127.pdf`
