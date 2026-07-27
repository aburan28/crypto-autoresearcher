---
id: KN-LIT-1766
type: literature
title: "Oblivious Single Access Machines are Concretely Efficient Sage Pia UConn"
authors:
  - "Amey Shukla"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/451"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/451"
tags: [lattice, mov-fr, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious algorithms allow a space-constrained client program to securely outsource storage to an untrusted server. Any program can be compiled to an oblivious form via Oblivious RAM (ORAM), but this is asymptotically and concretely expensive.

## Key claims (as reported)
- Recent work (Appan et al., CCS’24) proposed a weakening of ORAM called Oblivious Single Access Machine (OSAM), which offers asymptotically-improved oblivious compilation for many programs, including those that manipulate graph data structures.
- While of theoretical interest, OSAM graph algorithms were worse than generic ORAM, even for large graphs (tested on graphs of size up to 225 ).
- This work improves the concrete costs of OSAM-based oblivious algorithms.
- In short, the original work on OSAM proposed algorithms for manipulating objects with pointers to other objects, but their management of pointers involves non-trivial and concretely-expensive algorithms.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-451.pdf`
