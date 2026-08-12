---
id: KN-LIT-5278
type: literature
title: "Oblivious RAM with Worst-Case Logarithmic Overhead"
authors:
  - "Gilad Asharov"
  - "Ilan Komargodski"
  - "Wei-Kai Lin"
  - "Elaine Shi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first Oblivious RAM (ORAM) construction that for N memory blocks supports accesses with worst-case O(log N ) overhead for any block size Ω(log N ) while requiring a client memory of only a constant number of memory blocks. We rely on the existence of one-way functions and guarantee computational security.

## Key claims (as reported)
- Our result closes a long line of research on fundamental feasibility results for ORAM constructions as logarithmic overhead is necessary.
- The previous best logarithmic overhead construction only guarantees it in an amortized sense, i.e., logarithmic overhead is achieved only for long enough access sequences, where some of the individual accesses incur Θ(N ) overhead.
- The previously best ORAM in terms of worst-case overhead achieves O(log2 N/ log log N ) overhead.
- Technically, we design a novel de-amortization framework for modern ORAM constructions that use the “shuffled inputs” assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826170 (1).pdf`
- `downloads/12826170.pdf`
