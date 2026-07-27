---
id: KN-LIT-3655
type: literature
title: "Efficient, Oblivious Data Structures for MPC"
authors:
  - "Marcel Keller"
  - "Peter Scholl"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present oblivious implementations of several data structures for secure multiparty computation (MPC) such as arrays, dictionaries, and priority queues. The resulting oblivious data structures have only polylogarithmic overhead compared with their classical counterparts.

## Key claims (as reported)
- To achieve this, we give secure multiparty protocols for the ORAM of Shi et al.
- (Asiacrypt ‘11) and the Path ORAM scheme of Stefanov et al.
- (CCS ‘13), and we compare the resulting implementations.
- We subsequently use our oblivious priority queue for secure computation of Dijkstra’s shortest path algorithm on general graphs, where the graph structure is secret.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730241 (1).pdf`
- `downloads/88730241 (2).pdf`
- `downloads/88730241 (3).pdf`
- `downloads/88730241 (4).pdf`
- `downloads/88730241.pdf`
