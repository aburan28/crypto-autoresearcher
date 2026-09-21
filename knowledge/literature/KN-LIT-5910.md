---
id: KN-LIT-5910
type: literature
title: "Private Circuits with Quasilinear Randomness"
authors:
  - "Vipul Goyal"
  - "Yuval Ishai"
  - "Yifan Song"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A t-private circuit for a function f is a randomized Boolean circuit C that maps a randomized encoding of an input x to an encoding of the output f (x), such that probing t wires anywhere in C reveals nothing about x. Private circuits can be used to protect embedded devices against side-channel attacks.

## Key claims (as reported)
- Motivated by the high cost of generating fresh randomness in such devices, several works have studied the question of minimizing the randomness complexity of private circuits.
- The best known upper bound, due to Coron et al.
- (Eurocrypt 2020), is O(t2 · log ts) random bits, where s is the circuit size of f .
- We improve this to O(t · log ts), including the randomness used by the input encoder, and extend this bound to the stateful variant of private circuits.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760186 (1).pdf`
- `downloads/132760186.pdf`
