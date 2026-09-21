---
id: KN-LIT-1996
type: literature
title: "A 2n/2 -Time Algorithm for n-SVP and √"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pairing, protocol, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show a 2n/2+o(n) -time algorithm that, given as input a basis of a lattice L ⊂ Rn , finds a (non-zero) vector in whose length is √ at most e O( n) · min{λ1 (L), det(L)1/n }, where λ1 (L) is the length of a shortest non-zero lattice vector and det(L) is the lattice determinant. √ Minkowski showed that λ1 (L) ≤ n det(L)1/n and that there exist lat√ tices with λ1 (L) ≥ Ω( n)·det(L)1/n , so that our algorithm finds vectors that are as short as possible relative to the determinant (up to a polylogarithmic factor). The main technical contribution behind this result is new analysis of (a simpler variant of) a 2n/2+o(n) -time algorithm from [ADRS15], which was only previously known to solve less useful problems.

## Key claims (as reported)
- To achieve this, we rely crucially on the “reverse Minkowski theorem” (conjectured by Dadush [DR16] and proven by [RS17]), which can be thought of as a √ partial converse to the fact that λ1 (L) ≤ n det(L)1/n .
- Previously, the fastest known algorithm for finding such a vector was the 2.802n+o(n) -time algorithm due to [LWXZ11], which actually found a non-zero lattice vector with length O(1) · λ1 (L).
- Though we do not show how to find lattice vectors with this length in time 2n/2+o(n) , we do show that our algorithm suffices for the most important application of such algorithms: basis reduction.
- In particular, we show a modified version of Gama and Nguyen’s slide-reduction algorithm [GN08], which can be combined with the algorithm above to improve the time-length tradeoff for shortest-vector algorithms in nearly all regimes—including the regimes relevant to cryptography.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960066 (1).pdf`
- `downloads/126960066.pdf`
