---
id: KN-LIT-7147
type: literature
title: "Tighter, faster, simpler side-channel security evaluations beyond computing power"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Christine van Vredendaal"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hyperelliptic, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A Eurocrypt 2013 paper “Security evaluations beyond computing power: How to analyze side-channel attacks you cannot mount?” by Veyrat-Charvillon, Gérard, and Standaert proposed a “Rank Estimation Algorithm” (REA) to estimate the difficulty of finding a secret key given side-channel information from independent subkeys, such as the 16 key bytes in AES-128 or the 32 key bytes in AES-256. The lower and upper bounds produced by the algorithm are far apart for most key ranks.

## Key claims (as reported)
- The algorithm can produce tighter bounds but then becomes exponentially slower; it also becomes exponentially slower as the number of subkeys increases.
- This paper introduces two better algorithms for the same problem.
- The first, the “Extended Rank Estimation Algorithm” (EREA), is an extension of REA using statistical sampling as a second step to increase the speed of tightening the bounds on the rank.
- The second, the “Polynomial Rank Outlining Algorithm” (PRO), is a new approach to computing the rank.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/pro-20150308.pdf`
