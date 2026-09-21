---
id: KN-LIT-3127
type: literature
title: "Constrained Pseudorandom Functions for Unconstrained Inputs"
authors:
  - "Apoorvaa Deshpande"
  - "Venkata Koppula"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A constrained pseudo random function (PRF) behaves like a standard PRF, but with the added feature that the (master) secret key holder, having secret key K, can produce a constrained key, K{f }, that allows for the evaluation of the PRF on all inputs satisfied by the constraint f . Most existing constrained PRF constructions can handle only bounded length inputs.

## Key claims (as reported)
- In a recent work, Abusalah et al.
- [1] constructed a constrained PRF scheme where constraints can be represented as Turing machines with unbounded inputs.
- Their proof of security, however, requires risky “knowledge type” assumptions such as differing inputs obfuscation for circuits and SNARKs.
- In this work, we construct a constrained PRF scheme for Turing machines with unbounded inputs under weaker assumptions, namely, the existence of indistinguishability obfuscation for circuits (and injective pseudorandom generators).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650300 (1).pdf`
- `downloads/96650300.pdf`
