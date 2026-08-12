---
id: KN-LIT-2597
type: literature
title: "Asymptotics for the standard block size in primal lattice attacks:"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, factoring, lattice, number-theory, pairing, pqc, quantum, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many proposals of lattice-based cryptosystems estimate security levels by following a recipe introduced in the New Hope proposal. This recipe, given a lattice dimension n, modulus q, and standard deviation s, outputs a “primal block size” β and a security level growing linearly with β.

## Key claims (as reported)
- This β is minimal such that some κ satisfies ((n + κ)s2 + 1)1/2 < (d/β)1/2 δ 2β−d−1 q κ/d , where d = n + κ + 1 and δ = (β(πβ)1/β /(2π exp 1))1/2(β−1) .
- This paper identifies how β grows with n, with enough precision to show the impact of adjusting q and s by constant factors.
- Specifically, this paper shows that if lg q grows as Q0 lg n+Q1 +o(1) and lg s grows as S0 lg n+S1 +o(1), where 0 ≤ S0 ≤ 1/2 < Q0 −S0 , then β/n grows as z0 + (z1 + o(1))/lg n, where z0 = 2Q0 /(Q0 − S0 + 1/2)2 and z1 has a formula given in the paper.
- The paper provides a traditional-format proof and a proof verified by the HOL Light proof assistant.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/latticeasymp-20240413.pdf`
- `downloads/latticeasymp-20240427.pdf`
- `downloads/latticeasymp-20240727.pdf`
