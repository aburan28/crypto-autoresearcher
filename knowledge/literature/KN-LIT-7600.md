---
id: KN-LIT-7600
type: literature
title: "A Resource Estimation Model for the Hardware-Software Co-Design of Distributed Quantum Architectures"
authors:
  - "Raymond P. H. Wu"
  - "Chathurika Ranaweera"
  - "Sutharshan Rajasegarar"
  - "Ria Rushin Joseph"
  - "Jinho Choi"
  - "Seng W. Loke"
year: 2026
venue: 'arXiv preprint arXiv:2607.22998 [quant-ph, cs.DC]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.22998'
  url: https://arxiv.org/abs/2607.22998
tags: [distributed-quantum-computing, resource-estimation, communication-qubits, entanglement-distribution, decoherence, cost-model, circuit-partitioning, hidden-cost]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
A resource-estimation model for **distributed quantum computing** that prices the
trade-off ignored by most partitioning work: physical qubits inside a QPU must be split
between *computational* qubits and *communication* qubits used to generate and distribute
entanglement, and entanglement must be either fetched on demand (latency) or pre-fetched
(decoherence).

## Key claims (as reported)
- Distributed quantum compilation "routinely ignores" channel capacity, and hardware
  architects lack a method to determine it before circuit partitioning.
- Allocating more communication qubits raises concurrent non-local operation capacity but
  reduces computational qubits — a hard trade-off inside a finite QPU.
- Scheduling entanglement on demand introduces severe latency; pre-fetching exposes stored
  pairs to decoherence.
- The proposed model borrows the **economic order quantity** model from perishable
  inventory theory to optimize latency against the time cost of decoherence.
- Dual application: optimal allocation of dedicated communication qubits for static
  heterogeneous architectures, and the optimal number to reserve dynamically in
  homogeneous ones.

## Relevance to this program
Recorded strictly as a **cost-model** entry, and it earns that place by pairing with a
specific existing entry rather than on quantum keywords.

[[KN-LIT-7563]] (iacr:2026/1244) is the distributed-quantum ECDLP resource estimate
ingested in the 2026-07-26 gather — the only directly-ECDLP item in that window, and an
update to `KN-TECH-037`. That paper estimates the cost of running the elliptic-curve
discrete-logarithm algorithm across multiple QPUs. This paper argues that a class of costs
in exactly that setting is **routinely omitted**: the computational qubits sacrificed to
communication, and the latency-versus-decoherence penalty on entanglement supply.

The bearing is therefore narrow and specific: **any distributed-quantum ECDLP figure that
does not account for the communication-qubit split is an underestimate of the hardware
required.** Whether the estimate in [[KN-LIT-7563]] does account for it has **not been
checked here** — that check is the concrete follow-up this entry exists to prompt, and
until it is done nothing about `KN-TECH-037` changes. `KN-TECH-037` is unchanged and
unsuperseded by this entry.

This is `KN-TECH-035` full-cost discipline appearing in the quantum-hardware literature
under its own name: the paper's whole point is that a headline resource count that omits
a structurally necessary overhead is not a cost.

**Does not bear on the classical ECDLP.**

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-28 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-25, primary category quant-ph, cross-listed cs.DC. Preprint — not peer-reviewed,
no DOI or venue as of this entry.

NOT verified here: the economic-order-quantity model and its applicability to entanglement
supply; the claim that distributed quantum compilation routinely ignores channel capacity;
any of the quantitative allocation results. **Whether the ECDLP resource estimate of
[[KN-LIT-7563]] omits the communication-qubit cost described here has not been checked,
and no revision to that entry or to `KN-TECH-037` is asserted.**
