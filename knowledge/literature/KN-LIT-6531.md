---
id: KN-LIT-6531
type: literature
title: "Security with Functional Re-Encryption from CPA"
authors:
  - "Yevgeniy Dodis⋆"
  - "Shai Halevi⋆⋆"
  - "Daniel Wichs⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The notion of functional re-encryption security (funcCPA) for public-key encryption schemes was recently introduced by Akavia et al. (TCC’22), in the context of homomorphic encryption.

## Key claims (as reported)
- This notion lies in between CPA security and CCA security: we give the attacker a functional re-encryption oracle instead of the decryption oracle of CCA security.
- This oracle takes a ciphertext ct and a function f , and returns fresh encryption of the output of f applied to the decryption of ct; in symbols, ct′ = Enc(f (Dec(ct))).
- More generally, we even allow for a multi-input version, where the oracle takes an arbitrary number of ciphetexts ct1 , . . . ctl and outputs ct′ = Enc(f (Dec(ct1 ), . . . , Dec(ctl ))).
- In this work we observe that funcCPA security may have applications beyond homomorphic encryption, and set out to study its properties.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369127 (1).pdf`
- `downloads/14369127.pdf`
