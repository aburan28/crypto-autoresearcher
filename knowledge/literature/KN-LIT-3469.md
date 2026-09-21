---
id: KN-LIT-3469
type: literature
title: "Double-base scalar multiplication revisited"
authors:
  - "Daniel J. Bernstein"
  - "Chitchanok Chuengsatiansup"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, endomorphism, factoring, hyperelliptic, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper reduces the number of field multiplications required for scalar multiplication on conservative elliptic curves. For an average 256-bit integer n, this paper’s multiply-by-n algorithm takes just 7.47M per bit on twisted Edwards curves −x2 + y 2 = 1 + dx2 y 2 with small d.

## Key claims (as reported)
- The previous record, 7.62M per bit, was unbeaten for seven years.
- Unlike previous record-setting algorithms, this paper’s multiply-by-n algorithm uses double-base chains.
- The new speeds rely on advances in tripling speeds and on advances in constructing double-base chains.
- This paper’s new tripling formula for twisted Edwards curves takes just 11.4M, and its new algorithm for constructing an optimal double-base chain for n takes just (log n)2.5+o(1) bit operations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/dagger-20170113.pdf`
