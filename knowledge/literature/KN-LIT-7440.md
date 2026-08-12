---
id: KN-LIT-7440
type: literature
title: "Valiant’s Universal Circuits Revisited: an"
authors:
  - "Overall Improvement"
  - "a Lower Bound"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, mpc, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A universal circuit (UC) is a general-purpose circuit that can simulate arbitrary circuits (up to a certain size n). At STOC 1976 Valiant presented a graph theoretic approach to the construction of UCs, where a UC is represented by an edge universal graph (EUG) and is recursively constructed using a dedicated graph object (referred to as supernode).

## Key claims (as reported)
- As a main end result, Valiant constructed a 4-way supernode of size 19 and an EUG of size 4.75n log n (omitting smaller terms), which remained the most size-efficient even to this day (after more than 4 decades).
- Motivated by the emerging applications of UCs in various privacy preserving computation scenarios, we revisit Valiant’s universal circuits, and propose a 4-way supernode of size 18, and an EUG of size 4.5n log n.
- As confirmed by our implementations, we reduce the size of universal circuits (and the number of AND gates) by more than 5% in general , and thus improve upon the efficiency of UC-based cryptographic applications accordingly.
- Our approach to the design of optimal supernodes is computer aided (rather than by hand as in previous works), which might be of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210182 (1).pdf`
- `downloads/119210182.pdf`
