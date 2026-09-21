---
id: KN-LIT-7329
type: literature
title: "Type-II Optimal Polynomial Bases"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, hyperelliptic, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the 1990s and early 2000s several papers investigated the relative merits of polynomial-basis and normal-basis computations for F2n . Even for particularly squaring-friendly applications, such as implementations of Koblitz curves, normal bases fell behind in performance unless a type-I normal basis existed for F2n .

## Key claims (as reported)
- In 2007 Shokrollahi proposed a new method of multiplying in a type-II normal basis.
- Shokrollahi’s method efficiently transforms the normal-basis multiplication into a single multiplication of two size-(n + 1) polynomials.
- This paper speeds up Shokrollahi’s method in several ways.
- It first presents a simpler algorithm that uses only size-n polynomials.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/opb-20100413.pdf`
