---
id: KN-LIT-6597
type: literature
title: "Short Variable Length Domain Extenders With Beyond Birthday Bound Security"
authors:
  - "Yu Long Chen"
  - "Bart Mennink"
  - "Mridul Nandi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Length doublers are cryptographic functions that transform an n-bit cryptographic primitive into an efficient and secure cipher that length-preservingly encrypts strings of length in [n, 2n − 1]. All currently known constructions are only proven secure up to the birthday bound, and for all but one construction this bound is known to be tight.

## Key claims (as reported)
- We consider the remaining candidate, LDT by Chen et al.
- (ToSC 2017(3)), and prove that it achieves beyond the birthday bound security for the domain [n, 3n/2).
- We generalize the construction to multiple rounds and demonstrate that by adding one more encryption layer to LDT, beyond the birthday bound security can be achieved for all strings of length in [n, 2n − 1]: security up to around 22n/3 for the encryption of strings close to n and security up to around 2n for strings of length close to 2n.
- The security analysis of both schemes is performed in a modular manner through the introduction and analysis of a new concept called “harmonic permutation primitives.”

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272253 (1).pdf`
- `downloads/11272253.pdf`
