---
id: KN-LIT-5822
type: literature
title: "PPAD-Hardness and Delegation with Unambiguous Proofs"
authors:
  - "Yael Tauman Kalai"
  - "Omer Paneth"
  - "Lisa Yang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we show the hardness of finding a Nash equilibrium, a PPAD-complete problem, based on the quasi-polynomial hardness of the decisional assumption on groups with bilinear maps introduced by Kalai, Paneth and Yang [STOC 2019]. Towards this goal, we construct an unambiguous and updatable delegation scheme under this assumption for deterministic computations running in super-polynomial time and polynomial space.

## Key claims (as reported)
- This delegation scheme, which is of independent interest, is publicly verifiable and non-interactive in the common reference string (CRS) model.
- It is unambiguous meaning that it is hard to compute two different proofs for the same statement.
- It is updatable meaning that given a proof for the statement that a Turing machine M reaches configuration cf T in T steps, one can efficiently generate a proof for the statement that M reaches configuration cf T +1 in T + 1 steps.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171406 (1).pdf`
- `downloads/12171406.pdf`
