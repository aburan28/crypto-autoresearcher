---
id: KN-LIT-2274
type: literature
title: "A Unified Framework for Trapdoor-Permutation-Based Sequential Aggregate Signatures"
authors:
  - "Craig Gentry"
  - "Adam O’Neill"
  - "Leonid Reyzin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls, hash, mov-fr, pairing, provable-security, quantum, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a framework for trapdoor-permutation-based sequential aggregate signatures (SAS) that unifies and simplifies prior work and leads to new results. The framework is based on ideal ciphers over large domains, which have recently been shown to be realizable in the random oracle model.

## Key claims (as reported)
- The basic idea is to replace the random oracle in the full-domain-hash signature scheme with an ideal cipher.
- Each signer in sequence applies the ideal cipher, keyed by the message, to the output of the previous signer, and then inverts the trapdoor permutation on the result.
- We obtain different variants of the scheme by varying additional keying material in the ideal cipher and making different assumptions on the trapdoor permutation.
- In particular, we obtain the first scheme with lazy verification and signature size independent of the number of signers that does not rely on bilinear pairings.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770206 (1).pdf`
- `downloads/10770206 (2).pdf`
- `downloads/10770206 (3).pdf`
- `downloads/10770206 (4).pdf`
- `downloads/10770206.pdf`
