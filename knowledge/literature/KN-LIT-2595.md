---
id: KN-LIT-2595
type: literature
title: "Asymptotically Tight Bounds for Composing ORAM with PIR"
authors:
  - "Ittai Abraham"
  - "Christopher W. Fletcher"
  - "Kartik Nayak"
  - "Benny Pinkas"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice, mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious RAM (ORAM) is a cryptographic primitive that allows a trusted client to outsource storage to an untrusted server while hiding the client’s memory access patterns to the server. The last three decades of research on ORAMs √ have reduced the bandwidth blowup of ORAM schemes from O( N ) to O(1).

## Key claims (as reported)
- However, all schemes that achieve a bandwidth blowup smaller than O(log N ) use expensive computations such as homomorphic encryptions.
- In this paper, we achieve a sub-logarithmic bandwidth blowup of O(logd N ) (where d is a free parameter) without using expensive computation.
- We do so by using a d-ary tree and a two server private information retrieval (PIR) protocol based on inexpensive XOR operations at the servers.
- We also show a Ω(logcD N ) lower bound on bandwidth blowup in the modified model involving PIR operations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101740086 (1).pdf`
- `downloads/101740086 (2).pdf`
- `downloads/101740086 (3).pdf`
- `downloads/101740086 (4).pdf`
- `downloads/101740086.pdf`
