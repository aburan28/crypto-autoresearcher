---
id: KN-LIT-7507
type: literature
title: "When Homomorphism Becomes a Liability"
authors:
  - "Zvika Brakerski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that an encryption scheme cannot have a simple decryption function and be homomorphic at the same time, even with added noise. Specifically, if a scheme can homomorphically evaluate the majority function, then its decryption cannot be weakly-learnable (in particular, linear), even if the probability of decryption error is high.

## Key claims (as reported)
- (In contrast, without homomorphism, such schemes do exist and are presumed secure, e.g. based on LPN.) An immediate corollary is that known schemes that are based on the hardness of decoding in the presence of low hamming-weight noise cannot be fully homomorphic.
- This applies to known schemes such as LPN-based symmetric or public key encryption.
- Using these techniques, we show that the recent candidate fully homomorphic encryption, suggested by Bogdanov and Lee (ePrint ’11, henceforth BL), is insecure.
- In fact, we show two attacks on the BL scheme: One that uses homomorphism, and another that directly attacks a component of the scheme.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77850142 (1).pdf`
- `downloads/77850142 (2).pdf`
- `downloads/77850142 (3).pdf`
- `downloads/77850142.pdf`
