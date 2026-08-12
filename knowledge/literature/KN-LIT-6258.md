---
id: KN-LIT-6258
type: literature
title: "Revisiting Fairness in MPC: Polynomial Number of Parties and General Adversarial Structures"
authors:
  - "Dana Dachman-Soled"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate fairness in secure multiparty computation when the number of parties n = poly(λ) grows polynomially in the security parameter, λ. Prior to this work, efficient protocols achieving fairness with no honest majority and polynomial number of parties were known only for the AND and OR functionalities (Gordon and Katz, TCC’09).

## Key claims (as reported)
- We show the following: – We first consider symmetric Boolean functions F : {0, 1}n → {0, 1}, where the underlying function fn/2,n/2 : {0, . . . , n/2} × {0, . . . , n/2} → {0, 1} can be computed fairly and efficiently in the 2-party setting.
- We present an efficient protocol for any such F tolerating n/2 or fewer corruptions, for n = poly(λ) number of parties. – We present an efficient protocol for n-party majority tolerating n/2 + 1 or fewer corruptions, for n = poly(λ) number of parties.
- The construction extends to n/2 + c or fewer corruptions, for constant c. – We extend both of the above results to more general types of adversarial structures and present instantiations of non-threshold adversarial structures of these types.
- These instantiations are obtained via constructions of projective planes and combinatorial designs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550156 (1).pdf`
- `downloads/12550156.pdf`
