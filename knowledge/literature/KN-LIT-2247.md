---
id: KN-LIT-2247
type: literature
title: "A Subversion-Resistant SNARK"
authors:
  - "Behzad Abdolmaleki"
  - "Karim Baghery"
  - "Helger Lipmaa"
  - "Michał Zając"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
While zk-SNARKs are widely studied, the question of what happens when the CRS has been subverted has received little attention. In ASIACRYPT 2016, Bellare, Fuchsbauer and Scafuro showed the first negative and positive results in this direction, proving also that it is impossible to achieve subversion soundness and (even non-subversion) zero knowledge at the same time.

## Key claims (as reported)
- On the positive side, they constructed an involved sound and Sub-ZK argument system for NP.
- We make Groth’s zk-SNARK for Circuit-SAT from EUROCRYPT 2016 computationally knowledge-sound and perfectly composable Sub-ZK with minimal changes.
- We just require the CRS trapdoor to be extractable and the CRS to be publicly verifiable.
- To achieve the latter, we add some new elements to the CRS and construct an efficient CRS verification algorithm.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240308 (1).pdf`
- `downloads/106240308.pdf`
