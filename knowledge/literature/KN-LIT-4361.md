---
id: KN-LIT-4361
type: literature
title: "Implicit White-Box Implementations: White-Boxing ARX Ciphers"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since the first white-box implementation of AES published twenty years ago, no significant progress has been made in the design of secure implementations against an attacker with full control of the device. Designing white-box implementations of existing block ciphers is a challenging problem, as all proposals have been broken.

## Key claims (as reported)
- Only two whitebox design strategies have been published this far: the CEJO framework, which can only be applied to ciphers with small S-boxes, and selfequivalence encodings, which were only applied to AES.
- In this work we propose implicit implementations, a new design of whitebox implementations based on implicit functions, and we show that current generic attacks that break CEJO or self-equivalence implementations are not successful against implicit implementations.
- The generation and the security of implicit implementations are related to the self-equivalences of the non-linear layer of the cipher, and we propose a new method to obtain self-equivalences based on the CCZ-equivalence.
- We implemented this method and many other functionalities in a new open-source tool BoolCrypt, which we used to obtain for the first time affine, linear, and even quadratic self-equivalences of the permuted modular addition.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070018 (1).pdf`
- `downloads/135070018.pdf`
