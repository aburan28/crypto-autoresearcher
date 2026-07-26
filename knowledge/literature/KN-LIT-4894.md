---
id: KN-LIT-4894
type: literature
title: "Memory-Hard Functions from Cryptographic Primitives"
authors:
  - "Binyi Chen"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing, provable-security, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Memory-hard functions (MHFs) are moderately-hard functions which enforce evaluation costs both in terms of time and memory (often, in form of a trade-off). They are used e.g. for password protection, password-based key-derivation, and within cryptocurrencies, and have received a considerable amount of theoretical scrutiny over the last few years.

## Key claims (as reported)
- However, analyses see MHFs as modes of operation of some underlying hash function H, modeled as a monolithic random oracle.
- This is however a very strong assumption, as such hash functions are built from much simpler primitives, following somewhat ad-hoc design paradigms.
- This paper initiates the study of how to securely instantiate H within MHF designs using common cryptographic primitives like block ciphers, compression functions, and permutations.
- Security here will be in a model in which the adversary has parallel access to an idealized version of the underlying primitive.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940326 (1).pdf`
- `downloads/116940326.pdf`
