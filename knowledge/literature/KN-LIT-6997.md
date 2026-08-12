---
id: KN-LIT-6997
type: literature
title: "The Impact of Decryption Failures on the"
authors:
  - "John Proos"
  - "Joseph H. Silverman"
  - "Ari Singer"
  - "William Whyte"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
NTRUEncrypt is unusual among public-key cryptosystems in that, with standard parameters, validly generated ciphertexts can fail to decrypt. This affects the provable security properties of a cryptosystem, as it limits the ability to build a simulator in the random oracle model without knowledge of the private key.

## Key claims (as reported)
- We demonstrate attacks which use decryption failures to recover the private key.
- Such attacks work for all standard parameter sets, and one of them applies to any padding.
- The appropriate countermeasure is to change the parameter sets and possibly the decryption process so that decryption failures are vanishingly unlikely, and to adopt a padding scheme that prevents an attacker from directly controlling any part of the input to the encryption primitive.
- We outline one such candidate padding scheme.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/27290225 (1).pdf`
- `downloads/27290225 (2).pdf`
- `downloads/27290225.pdf`
