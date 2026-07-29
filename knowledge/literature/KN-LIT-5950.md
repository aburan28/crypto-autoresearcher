---
id: KN-LIT-5950
type: literature
title: "Proofs of Work From Worst-Case Assumptions"
authors:
  - "Marshall Ball"
  - "Alon Rosen"
  - "Manuel Sabin"
  - "Prashant Nalini Vasudevan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, mov-fr, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give Proofs of Work (PoWs) whose hardness is based on well-studied worst-case assumptions from fine-grained complexity theory. This extends the work of (Ball et al., STOC ’17), that presents PoWs that are based on the Orthogonal Vectors, 3SUM, and All-Pairs Shortest Path problems.

## Key claims (as reported)
- These, however, were presented as a ‘proof of concept’ of provably secure PoWs and did not fully meet the requirements of a conventional PoW: namely, it was not shown that multiple proofs could not be generated faster than generating each individually.
- We use the considerable algebraic structure of these PoWs to prove that this nonamortizability of multiple proofs does in fact hold and further show that the PoWs’ structure can be exploited in ways previous heuristic PoWs could not.
- This creates full PoWs that are provably hard from worst-case assumptions (previously, PoWs were either only based on heuristic assumptions or on much stronger cryptographic assumptions (Bitansky et al., ITCS ’16)) while still retaining significant structure to enable extra properties of our PoWs.
- Namely, we show that the PoWs of (Ball et al, STOC ’17) can be modified to have much faster verification time, can be proved in zero knowledge, and more.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993336 (1).pdf`
- `downloads/10993336.pdf`
