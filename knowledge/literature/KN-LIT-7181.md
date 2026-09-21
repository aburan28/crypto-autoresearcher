---
id: KN-LIT-7181
type: literature
title: "Topology-Hiding Computation on All Graphs"
authors:
  - "Adi Akavia"
  - "Rio LaVigne"
  - "Tal Moran"
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
A distributed computation in which nodes are connected by a partial communication graph is called topology-hiding if it does not reveal information about the graph beyond what is revealed by the output of the function. Previous results have shown that topology-hiding computation protocols exist for graphs of constant degree and logarithmic diameter in the number of nodes [MoranOrlov-Richelson, TCC’15; Hirt et al., Crypto’16] as well as for other graph families, such as cycles, trees, and low circumference graphs [Akavia-Moran, Eurocrypt’17], but the feasibility question for general graphs was open.

## Key claims (as reported)
- In this work we positively resolve the above open problem: we prove that topologyhiding MPC is feasible for all graphs under the Decisional Diffie-Hellman assumption.
- Our techniques employ random-walks to generate paths covering the graph, upon which we apply the Akavia-Moran topology-hiding broadcast for chain-graphs (paths).
- To prevent topology information revealed by the random-walk, we design multiple random-walks that, together, are locally identical to receiving at each round a message from each neighbors and sending back processed messages in a randomly permuted order.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401284 (1).pdf`
- `downloads/10401284.pdf`
