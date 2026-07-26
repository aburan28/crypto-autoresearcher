---
id: KN-LIT-7563
type: literature
title: Resource Estimation of the Distributed Quantum Algorithm for the Elliptic Curve Logarithm Problem
authors: [Khajeian MohamadAli]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1244'
identifiers:
  eprint: iacr:2026/1244
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1244
tags: [ecdlp, quantum, shor, resource-estimation, distributed-quantum-computing, logical-qubits, modular-inversion, extended-euclidean, cost-model, p256, quantum-cryptanalysis]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Adapts two distributed quantum algorithms to the elliptic-curve setting and gives a
resource estimate for each architecture, targeting the ECDLP on a cryptographically
sized 256-bit curve. The motivating observation is that a monolithic Shor machine for
ECDLP is bottlenecked by the logical-qubit cost of modular arithmetic — specifically
modular inversion — and that Distributed Quantum Computing (DQC), linking several
smaller QPUs, changes the per-node requirement.

## Key claims (as reported)
- Using the compact register-sharing Extended Euclidean Algorithm formulation of Luo
  et al. for modular inversion, the two distributed variants have distinct per-node
  footprints on a 256-bit curve.
- The zero-quantum-communication variant (Xu et al.) requires **1080-1140 logical
  qubits per node**, depending on the search-window configuration.
- The sequential quantum-communication variant (Li et al.) can be realized with as few
  as **828-1068 logical qubits per node**, depending on the number of participating
  nodes.
- The comparative analysis maps trade-offs between quantum communication overhead,
  classical coordination, and single-node hardware constraints.
- These are *logical* qubit counts for a fault-tolerant setting; the paper frames the
  result as establishing a design space, not as a near-term break.

## Relevance to this program
Directly updates `KN-TECH-037` (quantum ECDLP resource estimation, Shor circuits for
elliptic curves), which the corpus records in the monolithic-machine framing. The new
axis is that the headline "logical qubits to break P-256" number is not
architecture-invariant: splitting the computation across cooperating QPUs trades
qubit-count per node against communication, so a single scalar qubit figure is an
incomplete statement of quantum ECDLP cost in the same way the program already
insists a classical exponent is incomplete without its memory and communication
charges (`KN-TECH-035`, full-cost accounting).

This is a **quantum-model** result and does **not** bear on the classical
`sqrt(p)` question the program's active hypotheses target. It forecloses nothing on
the index-calculus side: a proposal claiming novelty for "distributed quantum ECDLP
resource estimation" is `known` as of this entry, but the classical relation-harvesting
line is untouched.

Methodologically the paper is an instance of the pattern `KN-TECH-052` describes —
fitting a cost model to an architecture rather than measuring a solve — and should be
read with the same caution the program applies to its own extrapolations.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`). ePrint history:
received 2026-06-11, last of 6 revisions 2026-07-22. No DOI or journal publication
recorded on the ePrint page.

NOT verified here: the correctness of the qubit counts, the fidelity of the adaptation
of the Xu et al. and Li et al. algorithms to the elliptic-curve setting, the Luo et al.
Extended-Euclidean inversion circuit it builds on, the gate/depth costs (the abstract
quotes only qubit width), the error-correction assumptions behind "logical", and the
communication-round costs. The referenced prior works (Luo et al., Xu et al., Li et
al.) are not themselves in this corpus and were not checked.
