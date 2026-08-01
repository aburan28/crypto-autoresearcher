---
id: KN-LIT-4356
type: literature
title: "Implementing Cryptographic Pairings on Smartcards"
authors:
  - "Michael Scott"
  - "Neil Costigan"
  - "Wesam Abdulwahab"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdlp, elliptic-curve, pairing, quantum, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pairings on elliptic curves are fast coming of age as cryptographic primitives for deployment in new security applications, particularly in the context of implementations of Identity-Based Encryption (IBE). In this paper we describe the implementation of various pairings on a contemporary 32-bit smart-card, the Philips HiPerSmartTM , an instantiation of the MIPS-32 based SmartMIPSTM architecture.

## Key claims (as reported)
- Three types of pairing are considered, first the standard Tate pairing on a nonsupersingular curve E(Fp ), second the Ate pairing, also on a nonsupersingular curve E(Fp ), and finally the ηT pairing on a supersingular curve E(F2m ).
- We demonstrate that pairings can be calculated as efficiently as classic cryptographic primitives on this architecture, with a calculation time of as little as 0.15 seconds.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11 (1).pdf`
- `downloads/11 (2).pdf`
- `downloads/11 (3).pdf`
- `downloads/11.pdf`
