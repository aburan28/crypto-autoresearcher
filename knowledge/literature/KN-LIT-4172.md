---
id: KN-LIT-4172
type: literature
title: "Hashing Garbled Circuits for Free"
authors:
  - "Xiong Fan"
  - "Chaya Ganesh"
  - "Vladimir Kolesnikov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr, mpc, pairing, provable-security, survey, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce Free Hash, a new approach to generating Garbled Circuit (GC) hash at no extra cost during GC generation. This is in contrast with state-of-the-art approaches, which hash GCs at computational cost of up to 6× of GC generation.

## Key claims (as reported)
- GC hashing is at the core of the cut-and-choose technique of GC-based secure function evaluation (SFE).
- Our main idea is to intertwine hash generation/verification with GC generation and evaluation.
- While we allow an adversary to generate a c whose hash collides with an honestly generated GC, such a GC c GC GC w.h.p. will fail evaluation and cheating will be discovered.
- Our GC hash is simply a (slightly modified) XOR of all the gate table rows of GC.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210288 (1).pdf`
- `downloads/10210288.pdf`
