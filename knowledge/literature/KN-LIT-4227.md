---
id: KN-LIT-4227
type: literature
title: "Holographic SNARGs for P and Batch-NP from (Polynomially Hard) Learning with Errors"
authors:
  - "Susumu Kiyoshima"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A succinct non-interactive argument (SNARG) is called holographic if the verifier runs in time sub-linear in the input length when given oracle access to an encoding of the input. We present holographic SNARGs for P and Batch-NP under the learning with errors (LWE) assumption.

## Key claims (as reported)
- Our holographic SNARG for P has a verifier that runs in time poly(λ, log T, log n) for T -time computations and n-bit inputs (λ is the security parameter), while our holographic SNARG for Batch-NP has a verifier that runs in time poly(λ, T, log k) for k instances of T -time computations.
- Before this work, constructions with the same asymptotic efficiency were known in the designated-verifier setting or under the sub-exponential hardness of the LWE assumption.
- We obtain our holographic SNARGs (in the public-verification setting under the polynomial hardness of the LWE assumption) by constructing holographic SNARGs for certain hash computations and then applying known/trivial transformations.
- As an application, we use our holographic SNARGs to weaken the assumption needed for a recent public-coin 3-round zero-knowledge (ZK) argument [Kiyoshima, CRYPTO 2022].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369070 (1).pdf`
- `downloads/14369070.pdf`
