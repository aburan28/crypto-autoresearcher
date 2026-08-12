---
id: KN-LIT-2800
type: literature
title: "Breaking the Circuit Size Barrier for Secure Computation under Quasi-Polynomial LPN"
authors:
  - "Geoffroy Couteau"
  - "Pierre Meyer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we introduce a new (circuit-dependent) homomorphic secret sharing (HSS) scheme for all log / log log-local circuits, with communication proportional only to the width of the circuit, and polynomial computation, assuming the super-polynomial hardness of learning parity with noise (LPN). At the heart of our new construction is a pseudorandom correlation generator (PCG), which allows two partie to locally stretch, from short seeds, pseudorandom instances of an arbitrary log / log log-local additive correlation.

## Key claims (as reported)
- Our main application, and the main motivation behind this work, is a generic two-party secure computation protocol for every layered (boolean or arithmetic) circuit of size s with total communication O(s/ log log s) and polynomial computation, assuming the super-polynomial hardness of the standard learning parity with noise assumption (a circuit is layered if its nodes can be partitioned in layers, such that any wire connects adjacent layers).
- This expands the set of assumptions under which the ‘circuit size barrier’ can be broken, for a large class of circuits.
- The strength of the underlying assumption is tied to the sublinearity factor: k(s) we achieve communication O(s/k(s)) under the s2 -hardness of LPN, for any k(s) ≤ log log s/4.
- Previously, the set of assumptions known to imply a PCG for correlations of degree ω(1) or generic secure computation protocols with sublinear communication was restricted to LWE, DDH, and a circularly secure variant of DCR.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960326 (1).pdf`
- `downloads/126960326.pdf`
