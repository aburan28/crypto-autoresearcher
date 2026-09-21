---
id: KN-LIT-3242
type: literature
title: "Cryptanalysis of JAMBU"
authors:
  - "Thomas Peyrin"
  - "Siang Meng Sim∗"
  - "Lei Wang"
  - "Guoyan Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article, we analyse the security of the authenticated encryption mode JAMBU, a submission to the CAESAR competition that remains currently unbroken. We show that the security claims of this candidate regarding its nonce-misuse resistance can be broken.

## Key claims (as reported)
- More precisely, we explain a technique to guess in advance a ciphertext block corresponding to a plaintext that has never been queried before (nor its prefix), thus breaking the confidentiality of the scheme when the attacker can make encryption queries with the same nonce.
- Our attack is very practical as it requires only about 232 encryption queries and computations (instead of the 2128 claimed by the designers).
- Our cryptanalysis has been fully implemented in order to verify our findings.
- Moreover, due to the small tag length of JAMBU, we show how this attack can be extended in the nonce-respecting scenario to break confidentiality in the adaptive chosen-ciphertext model (IND-CCA2) with 296 computations, with message prefixes not previously queried.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400140 (4).pdf`
- `downloads/85400140 (5).pdf`
