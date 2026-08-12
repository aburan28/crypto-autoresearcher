---
id: KN-LIT-2169
type: literature
title: "A Note on Perfect Correctness by Derandomization?"
authors:
  - "Nir Bitansky"
  - "Vinod Vaikuntanathan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, mov-fr, mpc, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show a general compiler that transforms a large class of erroneous cryptographic schemes (such as public-key encryption, indistinguishability obfuscation, and secure multiparty computation schemes) into perfectly correct ones. The transformation works for schemes that are correct on all inputs with probability noticeably larger than half, and are secure under parallel repetition.

## Key claims (as reported)
- We assume the existence of one-way functions and of functions with deterministic (uniform) time complexity 2O(n) and non-deterministic circuit complexity 2Ω(n) .
- Our transformation complements previous results that showed how publickey encryption and indistinguishability obfuscation that err on a noticeable fraction of inputs can be turned into ones that for all inputs are often correct.
- The technique relies on the idea of “reverse randomization” [Naor, Crypto 1989] and on Nisan-Wigderson style derandomization, previously used in cryptography to remove interaction from witness-indistinguishable proofs and commitment schemes [Barak, Ong and Vadhan, Crypto 2003].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210240 (1).pdf`
- `downloads/10210240.pdf`
