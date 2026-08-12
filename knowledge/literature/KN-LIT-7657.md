---
id: KN-LIT-7657
type: literature
title: "Resource Estimation of the Distributed Quantum Algorithm for the Elliptic Curve Logarithm Problem"
authors:
  - "MohamadAli Khajeian"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1244"
identifiers:
  eprint: "iacr:2026/1244"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1244"
tags: [ecdlp, quantum, shor, resource-estimate, distributed-quantum-computing, toffoli-count, logical-qubits, fault-tolerant, elliptic-curve, cost-model, security-estimate, extended-euclidean]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

> **Ingested as a dedup repair.** `GATHER-20260729` recorded this paper as already in
> the corpus under KN-LIT-7563 and skipped it. **It was not.** KN-LIT-7563 is
> Wesolowski's supersingular isogeny `p^{1/3+o(1)}` result; the mis-citation also
> appears in KN-LIT-7600's body. This is the only entry in this sweep that is directly
> about the ECDLP, and it was skipped on a false positive. See
> `ledger/corrections/CORR-20260801-003.yaml`.

## Contribution
The first rigorous **resource estimation for distributed quantum ECDLP solvers**.

Monolithic Shor implementations against ECC are bottlenecked by the logical-qubit
demand of **modular inversion**. This paper adapts two distributed-quantum-computing
frameworks — a **zero-quantum-communication** paradigm and a **sequential
teleportation-based** protocol — to the elliptic-curve setting, incorporating a
compact register-sharing **Extended Euclidean Algorithm** formulation, and quantifies
the design trade-offs for a **cryptographically secure 256-bit curve** on
fault-tolerant architectures.

## Key claims (as reported)
- **Zero-quantum-communication variant:** 1094–1154 logical qubits **per node**.
- **Teleportation-based variant:** as few as 856–1098 logical qubits **per node**.
- With arithmetic window size `ω = 16` over `k = 22` nodes, the **single-node** Toffoli
  count falls to `2^{26.84}`, an approximately **14× reduction** against a `2^{30.63}`
  monolithic baseline.
- The stated contribution is a mapping of architectural boundaries between inter-QPU
  communication, classical coordination, and single-chip hardware floors.

**Read the qualifiers carefully.** Every headline figure is **per node** or
**single-node**. A 14× reduction in *single-node* Toffoli count across `k = 22` nodes is
a statement about how work is distributed, **not** a 14× reduction in total quantum
work, and the abstract does not state a total. Inter-node communication cost is named
as an axis of the trade-off, not quantified in the abstract.

## Relevance to this program
**This is one of the few entries in the corpus that is directly about the ECDLP at
cryptographic scale**, and it is a `cost-model`/`security-estimate` entry of the kind
`KN-TECH-035`'s full-cost rules exist to discipline.

- **256-bit is the real parameter.** Under `docs/target-result-profile.md` the program
  prizes results validated at cryptographic scale rather than toy scale. This is such a
  result — for the *quantum* attack cost, not the classical one.
- **Modular inversion as the identified bottleneck** matches the program's existing
  quantum-ECDLP resource literature, and the register-sharing EEA formulation is the
  specific lever pulled. Worth comparing against the point-addition-circuit line
  ([[KN-LIT-1797]], `iacr:2026/1128`).
- **The distribution axis is the new content.** Splitting a Shor-ECDLP circuit across
  cooperating QPUs trades logical qubits per node against inter-node communication and
  classical coordination. Whether that trade is favourable end-to-end is exactly the
  kind of question `KN-TECH-035` insists be answered with *all* cost axes charged —
  and the abstract does not answer it.

**Changes no assessment of ECC security in this program's ledger.** A per-node qubit
count is not a break, a distributed architecture is not a demonstrated machine, and no
end-to-end cost is stated.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1244,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, sole author MohamadAli Khajeian, report number, year 2026,
category ATTACKS.

NOT verified here: the qubit counts; the `2^{26.84}` Toffoli figure or the `2^{30.63}`
monolithic baseline it is compared against; the `ω = 16`, `k = 22` optimization; the
adaptation of either DQC framework; the EEA formulation; and — most importantly — the
**total** (as opposed to per-node) resource cost, the inter-node communication cost,
and the error-correction overhead, **none of which the abstract states**. No
quantum-security estimate for any curve is revised here.
